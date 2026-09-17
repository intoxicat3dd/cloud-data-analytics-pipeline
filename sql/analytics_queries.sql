-- Best-selling products by gross sales.
SELECT product_id, product_title, SUM(quantity) AS units_sold, ROUND(SUM(line_total), 2) AS gross_sales
FROM YOUR_DATABASE.cart_items
GROUP BY 1, 2
ORDER BY gross_sales DESC
LIMIT 10;

-- Product catalogue health by category.
SELECT category, COUNT(*) AS product_count, ROUND(AVG(price), 2) AS avg_price,
       ROUND(AVG(rating), 2) AS avg_rating, SUM(stock) AS total_stock
FROM YOUR_DATABASE.products
GROUP BY 1
ORDER BY product_count DESC;
