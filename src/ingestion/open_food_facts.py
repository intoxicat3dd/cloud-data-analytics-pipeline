import json
from datetime import datetime, timezone
from pathlib import Path

import requests


API_URL = "https://world.openfoodfacts.org/api/v2/search"

HEADERS = {
    "User-Agent": "CloudDataAnalyticsPipeline/1.0 (GitHub portfolio project)"
}

PARAMS = {
    "categories_tags_en": "beverages",
    "page": 1,
    "page_size": 100,
    "fields": (
        "code,"
        "product_name,"
        "brands,"
        "categories_tags_en,"
        "countries_tags_en,"
        "nutriscore_grade,"
        "nutriscore_score,"
        "ecoscore_grade,"
        "nutriments"
    ),
}

OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "open_food_facts_raw.json"


def fetch_products():
    """Fetch product data from the Open Food Facts API."""

    response = requests.get(
        API_URL,
        params=PARAMS,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if "products" not in data:
        raise ValueError("API response does not contain a 'products' field.")

    return data


def save_raw_data(data):
    """Save the raw API response locally as JSON."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output = {
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "source": API_URL,
        "product_count": len(data["products"]),
        "products": data["products"],
    }

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    return OUTPUT_FILE


def main():
    print("Starting Open Food Facts ingestion...")

    data = fetch_products()

    print(f"Products retrieved: {len(data['products'])}")

    output_file = save_raw_data(data)

    print(f"Raw data saved to: {output_file}")
    print("Ingestion completed successfully.")


if __name__ == "__main__":
    main()
