-- Day 52: Project 3 - Data Warehouse Design (Part 1)
-- BEGINNER WORKFLOW — sql-52: Project3 DWH Part1
-- Guide: sql/postgres-60day/companion-guides/day52_project3_dwh_part1.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-52/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: dim_date, dim_customer, dim_product, fact_sales, training.orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. This stateful lesson ends with COMMIT and preserves only the course-owned dwh schema.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Topics: Star schema design (facts/dimensions) and initial loads
BEGIN;
SET search_path TO training, public;

-- This three-day project is intentionally stateful. Re-running Day 52 resets
-- only the course-owned dwh schema, then commits it for Days 53 and 54.
DROP SCHEMA IF EXISTS dwh CASCADE;
CREATE SCHEMA dwh;
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

-- Populate dim_date for every source order plus a useful planning horizon.
-- Deriving the bounds from the source prevents old facts from missing a date key.
WITH bounds AS (
  SELECT LEAST(
           MIN(order_date)::date,
           (CURRENT_DATE - interval '2 years')::date
         ) AS start_date,
         GREATEST(
           MAX(order_date)::date,
           (CURRENT_DATE + interval '1 year')::date
         ) AS end_date
  FROM training.orders
), cal AS (
  SELECT generate_series(
           start_date,
           end_date,
           interval '1 day'
         )::date AS d
  FROM bounds
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
       c.created_at::date, NULL, TRUE
FROM training.customers c;

-- Initial load for product dimension
INSERT INTO dim_product(product_id, name, category, price, cost, valid_from, valid_to, is_current)
SELECT p.product_id, p.name, p.category, p.price, p.cost,
       p.created_at::date, NULL, TRUE
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
-- 1. Add dim_country and link customers to it.
--    Inputs: For sql-52 Exercise 1, read the target keys from `dim_country`, `training.customers`, `dim_customer`, and `dwh.dim_customer` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-52 Exercise 1, expected output: one row per country code in `dim_country`; every customer-dimension version has exactly one `country_sk`. The final columns are `country`. The final order is `country`.
--    Verify: For sql-52 Exercise 1, materialize the intended `country` target set first; require the command tag/`RETURNING` set to match it, then query `dim_country`, `training.customers`, `dim_customer`, and `dwh.dim_customer` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `country` values in both cases.
--    Hint ladder, rung 1: For sql-52 Exercise 1, materialize the intended `country` target set first; require the command tag/`RETURNING` set to match it, then query `dim_country`, `training.customers`, `dim_customer`, and `dwh.dim_customer` again and prove rollback or idempotent retry.
-- 2. Build a second fact table fact_payments linked to dim_date and dim_customer.
--    Inputs: For sql-52 Exercise 2, read from `training.payments`, `training.orders`, `dim_date`, and `dim_customer`. Compute `payment_id`, `order_id`, `date_key`, `customer_sk`, `amount`, and `method` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-52 Exercise 2, expected output: one row per source payment with: - `payment_id` as the idempotent fact key; - `order_id` as a degenerate operational reference; - the payment-. The final columns are `payment_id`, `order_id`, `date_key`, `customer_sk`, `amount`, and `method`. The final order is `p.payment_id`.
--    Verify: For sql-52 Exercise 2, evaluate each of `customer_sk`, and `amount` in a separate control `SELECT` over `training.payments`, `training.orders`, `dim_date`, and `dim_customer`; require one final row and compare every value. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `p.payment_id`.
--    Hint ladder, rung 1: For sql-52 Exercise 2, start with the first relation in `training.payments`, `training.orders`, `dim_date`, and `dim_customer`; after each join, record total rows and distinct `payment_id` so the exact fanout or loss is visible.
-- 3. Prediction: identify the grain of fact_sales and explain why order_id alone
--    cannot be its primary key.
--    Inputs: For sql-52 Exercise 3, read from `fact_sales`. Compute `fact_rows`, `orders`, and `distinct_order_items` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-52 Exercise 3, expected output: one row per order line. The final columns are `fact_rows`, `orders`, and `distinct_order_items`.
--    Verify: For sql-52 Exercise 3, evaluate each of `fact_rows`, `orders`, and `distinct_order_items` in a separate control `SELECT` over `fact_sales`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-52 Exercise 3, select `order_id` from `fact_sales` before adding derived columns.
-- 4. Construction: add unknown (-1) members to dimensions and route an
--    intentionally unmatched source key to them during a test load.
--    Inputs: For sql-52 Exercise 4, read from `dim_country`, `dim_customer`, and `dim_product`. Build the answer toward `routed_customer_sk`; keep `routed_customer_sk` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-52 Exercise 4, expected output: one row per `routed_customer_sk`. The final columns are `routed_customer_sk`.
--    Verify: For sql-52 Exercise 4, project `routed_customer_sk` plus the raw source columns from `dim_country`, `dim_customer`, and `dim_product` at each join stage; record row count and distinct `routed_customer_sk`, then assert the final `routed_customer_sk` values match those staged rows without unintended fanout or loss. Add one source row with a new `routed_customer_sk`; verify the result gains exactly one row carrying that `routed_customer_sk` value.
--    Hint ladder, rung 1: For sql-52 Exercise 4, start with the first relation in `dim_country`, `dim_customer`, and `dim_product`; after each join, record total rows and distinct `routed_customer_sk` so the exact fanout or loss is visible.
-- 5. Debugging: prove that fact_sales amount reconciles to source line-item
--    revenue and investigate any row-count or amount difference.
--    Inputs: For sql-52 Exercise 5, read from `fact_sales`, and `training.order_items`. Compute `fact_rows`, `source_rows`, `fact_amount`, and `source_amount` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-52 Exercise 5, expected output: exactly one aggregate summary row. The final columns are `fact_rows`, `source_rows`, `fact_amount`, and `source_amount`.
--    Verify: For sql-52 Exercise 5, evaluate each of `fact_rows`, `source_rows`, `fact_amount`, and `source_amount` in a separate control `SELECT` over `fact_sales`, and `training.order_items`; require one final row and compare every value. Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.
--    Hint ladder, rung 1: For sql-52 Exercise 5, select `order_item_id` from `fact_sales`, and `training.order_items` before adding derived columns.
-- 6. Edge case: document how a late-arriving payment date outside dim_date's
--    generated range should fail, extend, or map according to an explicit policy.
--    Inputs: For sql-52 Exercise 6, read from `training.payments`, and `dim_date`. Build the answer toward `payment_id`, and `date`; keep `payment_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-52 Exercise 6, expected output: one row per `payment_id`. The final columns are `payment_id`, and `date`. The final order is `p.payment_id`.
--    Verify: For sql-52 Exercise 6, project `payment_id` plus the raw source columns from `training.payments`, and `dim_date` at each join stage; record row count and distinct `payment_id`, then assert the final `payment_id`, and `date` values match those staged rows without unintended fanout or loss. Add one row for which `(d.date_key IS NULL)` is true and one for which it is false; verify only the matching `payment_id` value is returned.
--    Hint ladder, rung 1: For sql-52 Exercise 6, start with the first relation in `training.payments`, and `dim_date`; after each join, record total rows and distinct `payment_id` so the exact fanout or loss is visible.

COMMIT;
