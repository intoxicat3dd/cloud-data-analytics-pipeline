"""Transform DummyJSON raw extracts into analytics-ready Parquet datasets."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def load_raw_extract(path: Path) -> list[dict]:
    """Load a raw extract written by the ingestion job."""

    with path.open(encoding="utf-8") as source:
        payload = json.load(source)

    records = payload.get("data")
    if not isinstance(records, list):
        raise ValueError(f"{path} does not contain a list in its 'data' field.")
    return records


def transform_products(products: list[dict]) -> pd.DataFrame:
    """Select stable product fields and standardise their data types."""

    frame = pd.DataFrame(products)
    required = {"id", "title", "category", "price", "stock", "rating"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Product records are missing columns: {sorted(missing)}")

    columns = [
        "id", "title", "brand", "category", "price", "discountPercentage",
        "rating", "stock", "availabilityStatus", "shippingInformation",
    ]
    frame = frame.reindex(columns=columns)
    frame = frame.rename(columns={"id": "product_id", "discountPercentage": "discount_percentage"})
    for column in ("price", "discount_percentage", "rating"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["stock"] = pd.to_numeric(frame["stock"], errors="coerce").astype("Int64")
    return frame.drop_duplicates(subset=["product_id"])


def transform_cart_items(carts: list[dict]) -> pd.DataFrame:
    """Flatten cart lines so each row represents one product in one cart."""

    rows = []
    for cart in carts:
        for item in cart.get("products", []):
            rows.append({
                "cart_id": cart.get("id"),
                "user_id": cart.get("userId"),
                "product_id": item.get("id"),
                "product_title": item.get("title"),
                "unit_price": item.get("price"),
                "quantity": item.get("quantity"),
                "line_total": item.get("total"),
                "discounted_line_total": item.get("discountedTotal"),
            })
    frame = pd.DataFrame(rows)
    for column in ("unit_price", "line_total", "discounted_line_total"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if not frame.empty:
        frame["quantity"] = pd.to_numeric(frame["quantity"], errors="coerce").astype("Int64")
    return frame


def write_partitioned_parquet(frame: pd.DataFrame, dataset: str, output_dir: Path = PROCESSED_DIR) -> Path:
    """Write a date-partitioned Parquet file that Athena can query efficiently."""

    ingestion_date = datetime.now(timezone.utc).date().isoformat()
    destination = output_dir / f"dataset={dataset}" / f"ingestion_date={ingestion_date}"
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "part-000.parquet"
    frame.to_parquet(target, index=False)
    return target


def main() -> None:
    """Create the products and cart-items analytical datasets locally."""

    products = transform_products(load_raw_extract(RAW_DIR / "products_raw.json"))
    cart_items = transform_cart_items(load_raw_extract(RAW_DIR / "carts_raw.json"))
    print(f"Wrote {len(products)} product records to {write_partitioned_parquet(products, 'products')}")
    print(f"Wrote {len(cart_items)} cart-item records to {write_partitioned_parquet(cart_items, 'cart_items')}")


if __name__ == "__main__":
    main()
