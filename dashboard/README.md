# Dashboard

Connect Power BI Desktop to the Athena `products` and `cart_items` tables.

Recommended visuals:

- Top 10 products by gross sales
- Gross sales and units sold by product
- Product count and average rating by category
- Stock level by category

Use `product_id` to relate `cart_items` to `products`. Keep the Athena query result location separate from data storage and remove it when the project is no longer needed.
