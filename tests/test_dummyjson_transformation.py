from src.transformation.dummyjson import transform_cart_items, transform_products


def test_transform_products_selects_and_deduplicates_records():
    products = [
        {"id": 1, "title": "Tea", "brand": "Acme", "category": "beverages", "price": 3,
         "discountPercentage": 10, "rating": 4.5, "stock": 7, "availabilityStatus": "In Stock"},
        {"id": 1, "title": "Tea updated", "category": "beverages", "price": 3,
         "discountPercentage": 10, "rating": 4.5, "stock": 7},
    ]

    actual = transform_products(products)

    assert list(actual["product_id"]) == [1]
    assert actual.loc[0, "price"] == 3
    assert "discount_percentage" in actual.columns


def test_transform_cart_items_flattens_nested_products():
    carts = [{"id": 4, "userId": 8, "products": [
        {"id": 1, "title": "Tea", "price": 3, "quantity": 2, "total": 6, "discountedTotal": 5.5}
    ]}]

    actual = transform_cart_items(carts)

    assert len(actual) == 1
    assert actual.loc[0, "cart_id"] == 4
    assert actual.loc[0, "discounted_line_total"] == 5.5
