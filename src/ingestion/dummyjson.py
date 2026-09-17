import json
import os
from datetime import datetime, timezone
from pathlib import Path

import boto3
import requests
from dotenv import load_dotenv


BASE_URL = "https://dummyjson.com"

load_dotenv()
AWS_PROFILE = os.getenv("AWS_PROFILE")
S3_BUCKET = os.getenv("S3_BUCKET")

HEADERS = {
    "User-Agent": "CloudDataAnalyticsPipeline/1.0"
}

OUTPUT_DIR = Path("data/raw")

PRODUCTS_FILE = OUTPUT_DIR / "products_raw.json"
CARTS_FILE = OUTPUT_DIR / "carts_raw.json"


def fetch_all_products():
    """Fetch all products from the DummyJSON API."""

    products = []
    skip = 0
    limit = 100

    while True:
        response = requests.get(
            f"{BASE_URL}/products",
            params={
                "limit": limit,
                "skip": skip,
            },
            headers=HEADERS,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()
        batch = data.get("products", [])

        products.extend(batch)

        if len(products) >= data.get("total", 0):
            break

        if not batch:
            break

        skip += limit

    return products


def fetch_carts():
    """Fetch cart data from the DummyJSON API."""

    response = requests.get(
        f"{BASE_URL}/carts",
        params={"limit": 100},
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("carts", [])


def save_json(data, output_file, source):
    """Save API data as raw JSON."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "record_count": len(data),
        "data": data,
    }

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)


def upload_to_s3(local_file, s3_key):
    """Upload a local file to the project S3 bucket."""

    if not S3_BUCKET:
        raise ValueError("Set S3_BUCKET in .env before uploading to S3.")

    session = boto3.Session(profile_name=AWS_PROFILE) if AWS_PROFILE else boto3.Session()
    s3 = session.client("s3")

    s3.upload_file(
        str(local_file),
        S3_BUCKET,
        s3_key,
    )

    print(f"Uploaded to s3://{S3_BUCKET}/{s3_key}")


def main(upload=False):
    """Extract DummyJSON data locally, optionally landing it in S3."""

    print("Starting DummyJSON ingestion...")

    products = fetch_all_products()
    print(f"Products retrieved: {len(products)}")

    carts = fetch_carts()
    print(f"Carts retrieved: {len(carts)}")

    save_json(
        products,
        PRODUCTS_FILE,
        f"{BASE_URL}/products",
    )

    save_json(
        carts,
        CARTS_FILE,
        f"{BASE_URL}/carts",
    )

    print(f"Products saved to: {PRODUCTS_FILE}")
    print(f"Carts saved to: {CARTS_FILE}")

    if upload:
        upload_to_s3(PRODUCTS_FILE, "raw/products/products_raw.json")
        upload_to_s3(CARTS_FILE, "raw/carts/carts_raw.json")

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
