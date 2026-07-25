-- Day 53: Project 3 - Data Warehouse Design (Part 2)
-- Topics: Slowly Changing Dimensions (Type 2) for customers/products
BEGIN;
SET search_path TO dwh, training, public;

-- Example SCD Type 2 upsert for dim_customer
-- Assumption: source-of-truth is training.customers; we detect changes by comparing attributes
-- Steps per changed business key:
--   1) Close current row (set valid_to = today - 1, is_current = false)
--   2) Insert new row with updated attributes (valid_from = today, is_current = true)

-- Simulate a change in the OLTP source (demo only)
CREATE TEMP TABLE changed_customers AS
SELECT c.customer_id,
       c.full_name,
       c.country,
       CASE WHEN c.segment = 'platinum' THEN 'gold' ELSE 'platinum' END AS segment
FROM training.customers c
ORDER BY c.customer_id
LIMIT 10;

-- Detect current rows that differ from source attributes
WITH current_dim AS (
  SELECT dc.*
  FROM dim_customer dc
  WHERE dc.is_current
), diffs AS (
  SELECT s.customer_id,
         s.full_name,
         s.country,
         s.segment
  FROM changed_customers s
  JOIN current_dim dc ON dc.customer_id = s.customer_id
  WHERE coalesce(s.full_name,'') <> coalesce(dc.full_name,'')
     OR coalesce(s.country,'')   <> coalesce(dc.country,'')
     OR coalesce(s.segment,'')   <> coalesce(dc.segment,'')
), closed AS (
  UPDATE dim_customer dc
  SET valid_to = CURRENT_DATE - 1,
      is_current = FALSE
  FROM diffs d
  WHERE dc.customer_id = d.customer_id
    AND dc.is_current
  RETURNING dc.customer_id
)
INSERT INTO dim_customer(customer_id, full_name, country, segment, valid_from, valid_to, is_current)
SELECT d.customer_id, d.full_name, d.country, d.segment, CURRENT_DATE, NULL, TRUE
FROM diffs d;

-- Verify multiple versions per customer
SELECT customer_id,
       COUNT(*) AS versions,
       MIN(valid_from) AS first_seen,
       MAX(coalesce(valid_to, CURRENT_DATE)) AS last_seen
FROM dim_customer
GROUP BY customer_id
ORDER BY versions DESC, customer_id
LIMIT 10;

-- SCD Type 2 for dim_product (similar pattern)
CREATE TEMP TABLE changed_products AS
SELECT p.product_id,
       p.name,
       p.category,
       round(p.price * 1.05, 2) AS price,
       p.cost
FROM training.products p
ORDER BY p.product_id
LIMIT 10;

WITH current_p AS (
  SELECT * FROM dim_product WHERE is_current
), diffs AS (
  SELECT s.*
  FROM changed_products s
  JOIN current_p dp ON dp.product_id = s.product_id
  WHERE coalesce(s.name,'')     <> coalesce(dp.name,'')
     OR coalesce(s.category,'') <> coalesce(dp.category,'')
     OR coalesce(s.price,0)     <> coalesce(dp.price,0)
     OR coalesce(s.cost,0)      <> coalesce(dp.cost,0)
), close_p AS (
  UPDATE dim_product dp
  SET valid_to = CURRENT_DATE - 1,
      is_current = FALSE
  FROM diffs d
  WHERE dp.product_id = d.product_id
    AND dp.is_current
  RETURNING dp.product_id
)
INSERT INTO dim_product(product_id, name, category, price, cost, valid_from, valid_to, is_current)
SELECT d.product_id, d.name, d.category, d.price, d.cost, CURRENT_DATE, NULL, TRUE
FROM diffs d;

-- Fact table joins should point to is_current at load time; for historical facts you would key by date to choose appropriate SCD version.

-- Exercises
-- 1) Implement SCD2 change capture keyed by date_key (choose version where valid_from <= order_date <= coalesce(valid_to,'infinity')).
-- 2) Add audit columns (updated_by, updated_at) to dim tables.

ROLLBACK;
