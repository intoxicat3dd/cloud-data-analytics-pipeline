-- Run after copying data/processed to s3://YOUR_BUCKET/processed/.
-- Replace YOUR_DATABASE and YOUR_BUCKET before executing.
CREATE DATABASE IF NOT EXISTS YOUR_DATABASE;

CREATE EXTERNAL TABLE IF NOT EXISTS YOUR_DATABASE.products (
  product_id BIGINT,
  title STRING,
  brand STRING,
  category STRING,
  price DOUBLE,
  discount_percentage DOUBLE,
  rating DOUBLE,
  stock INT,
  availability_status STRING,
  shipping_information STRING
)
PARTITIONED BY (ingestion_date DATE)
STORED AS PARQUET
LOCATION 's3://YOUR_BUCKET/processed/dataset=products/';

CREATE EXTERNAL TABLE IF NOT EXISTS YOUR_DATABASE.cart_items (
  cart_id BIGINT,
  user_id BIGINT,
  product_id BIGINT,
  product_title STRING,
  unit_price DOUBLE,
  quantity INT,
  line_total DOUBLE,
  discounted_line_total DOUBLE
)
PARTITIONED BY (ingestion_date DATE)
STORED AS PARQUET
LOCATION 's3://YOUR_BUCKET/processed/dataset=cart_items/';

MSCK REPAIR TABLE YOUR_DATABASE.products;
MSCK REPAIR TABLE YOUR_DATABASE.cart_items;
