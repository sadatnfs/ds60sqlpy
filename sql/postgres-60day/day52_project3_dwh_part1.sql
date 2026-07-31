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
--    Inputs: Use only the declared lesson objects (dim_date, dim_customer, dim_product, fact_sales, training.orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Build a second fact table fact_payments linked to dim_date and dim_customer.
--    Inputs: Use only the declared lesson objects (dim_date, dim_customer, dim_product, fact_sales, training.orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 3. Prediction: identify the grain of fact_sales and explain why order_id alone
--    cannot be its primary key.
--    Inputs: Use only the declared lesson objects (dim_date, dim_customer, dim_product, fact_sales, training.orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: add unknown (-1) members to dimensions and route an
--    intentionally unmatched source key to them during a test load.
--    Inputs: Use only the declared lesson objects (dim_date, dim_customer, dim_product, fact_sales, training.orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: prove that fact_sales amount reconciles to source line-item
--    revenue and investigate any row-count or amount difference.
--    Inputs: Use only the declared lesson objects (dim_date, dim_customer, dim_product, fact_sales, training.orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: document how a late-arriving payment date outside dim_date's
--    generated range should fail, extend, or map according to an explicit policy.
--    Inputs: Use only the declared lesson objects (dim_date, dim_customer, dim_product, fact_sales, training.orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

COMMIT;
