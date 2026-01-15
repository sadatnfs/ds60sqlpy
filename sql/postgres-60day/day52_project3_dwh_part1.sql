-- Day 52: Project 3 - Data Warehouse Design (Part 1)
-- Topics: Star schema design (facts/dimensions) and initial loads
BEGIN;
SET search_path TO training, public;

-- Create a DWH schema (demo; will be rolled back)
CREATE SCHEMA IF NOT EXISTS dwh;
SET search_path TO dwh, training, public;

-- Dimension tables (surrogate keys)
CREATE TABLE dim_date (
  date_key       INT PRIMARY KEY,      -- yyyymmdd
  date_actual    DATE NOT NULL,
  year           INT NOT NULL,
  quarter        INT NOT NULL,
  month          INT NOT NULL,
  day            INT NOT NULL,
  day_name       TEXT NOT NULL,
  is_weekend     BOOLEAN NOT NULL
);

CREATE SEQUENCE dim_customer_sk_seq;
CREATE TABLE dim_customer (
  customer_sk    INT PRIMARY KEY DEFAULT nextval('dim_customer_sk_seq'),
  customer_id    INT NOT NULL,   -- business key
  full_name      TEXT,
  country        TEXT,
  segment        TEXT,
  valid_from     DATE NOT NULL,
  valid_to       DATE,
  is_current     BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE SEQUENCE dim_product_sk_seq;
CREATE TABLE dim_product (
  product_sk     INT PRIMARY KEY DEFAULT nextval('dim_product_sk_seq'),
  product_id     INT NOT NULL,  -- business key
  name           TEXT,
  category       TEXT,
  price          NUMERIC(10,2),
  cost           NUMERIC(10,2),
  valid_from     DATE NOT NULL,
  valid_to       DATE,
  is_current     BOOLEAN NOT NULL DEFAULT TRUE
);

-- Fact table
CREATE TABLE fact_sales (
  order_id       INT NOT NULL,
  order_item_id  INT NOT NULL,
  date_key       INT NOT NULL REFERENCES dim_date(date_key),
  customer_sk    INT NOT NULL REFERENCES dim_customer(customer_sk),
  product_sk     INT NOT NULL REFERENCES dim_product(product_sk),
  quantity       INT NOT NULL,
  unit_price     NUMERIC(10,2) NOT NULL,
  discount       NUMERIC(5,2) NOT NULL,
  amount         NUMERIC(12,2) NOT NULL
);

-- Populate dim_date for a 3-year range around today
WITH cal AS (
  SELECT generate_series(
           (CURRENT_DATE - interval '2 years')::date,
           (CURRENT_DATE + interval '1 year')::date,
           interval '1 day'
         )::date AS d
)
INSERT INTO dim_date(date_key, date_actual, year, quarter, month, day, day_name, is_weekend)
SELECT extract(year from d)::int * 10000 + extract(month from d)::int * 100 + extract(day from d)::int,
       d,
       extract(year from d)::int,
       extract(quarter from d)::int,
       extract(month from d)::int,
       extract(day from d)::int,
       to_char(d, 'Dy'),
       (extract(isodow from d)::int >= 6)
FROM cal;

-- Initial load for customer dimension (Type 2 structure; initial current rows)
INSERT INTO dim_customer(customer_id, full_name, country, segment, valid_from, valid_to, is_current)
SELECT c.customer_id, c.full_name, c.country, COALESCE(c.segment,'standard') AS segment,
       CURRENT_DATE, NULL, TRUE
FROM training.customers c;

-- Initial load for product dimension
INSERT INTO dim_product(product_id, name, category, price, cost, valid_from, valid_to, is_current)
SELECT p.product_id, p.name, p.category, p.price, p.cost,
       CURRENT_DATE, NULL, TRUE
FROM training.products p;

-- Load fact from existing orders/items (map to dims using current rows)
WITH oi AS (
  SELECT oi.order_item_id, oi.order_id, o.order_date::date AS od,
         o.customer_id, oi.product_id,
         oi.quantity, oi.unit_price, oi.discount,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS amount
  FROM training.order_items oi
  JOIN training.orders o ON o.order_id = oi.order_id
), keys AS (
  SELECT oi.*, 
         (extract(year from oi.od)::int * 10000 + extract(month from oi.od)::int * 100 + extract(day from oi.od)::int) AS date_key,
         dc.customer_sk,
         dp.product_sk
  FROM oi
  JOIN dim_customer dc ON dc.customer_id = oi.customer_id AND dc.is_current
  JOIN dim_product  dp ON dp.product_id  = oi.product_id  AND dp.is_current
)
INSERT INTO fact_sales(order_id, order_item_id, date_key, customer_sk, product_sk, quantity, unit_price, discount, amount)
SELECT order_id, order_item_id, date_key, customer_sk, product_sk, quantity, unit_price, discount, amount
FROM keys;

-- Sample star query
SELECT dd.year, dd.month, dp.category,
       ROUND(SUM(fs.amount),2) AS revenue
FROM fact_sales fs
JOIN dim_date dd     ON dd.date_key = fs.date_key
JOIN dim_product dp  ON dp.product_sk = fs.product_sk
GROUP BY dd.year, dd.month, dp.category
ORDER BY dd.year DESC, dd.month DESC, revenue DESC
LIMIT 50;

-- Exercises
-- 1) Add dim_country and link customers to it.
-- 2) Build a second fact table fact_payments linked to dim_date and dim_customer.

ROLLBACK;
