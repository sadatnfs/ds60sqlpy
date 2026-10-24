-- Day 53: Project 3 - Data Warehouse Design (Part 2)
-- BEGINNER WORKFLOW — sql-53: Project3 DWH Part2 SCD
-- Guide: sql/postgres-60day/companion-guides/day53_project3_dwh_part2_scd.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-53/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: training.customers, dim_customer, training.products, dim_product.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
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
-- 1. Implement SCD2 change capture keyed by date_key (choose version where valid_from <= order_date <= coalesce(valid_to,'infinity')).
--    Inputs: For sql-53 Exercise 1, read from `training.orders`, `training.order_items`, `dim_date`, `dim_customer`, and `dim_product`. Build the answer toward `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-53 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount`.
--    Verify: For sql-53 Exercise 1, project `order_id` plus the raw source columns from `training.orders`, `training.order_items`, `dim_date`, `dim_customer`, and `dim_product` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-53 Exercise 1, start with the first relation in `training.orders`, `training.order_items`, `dim_date`, `dim_customer`, and `dim_product`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 2. Add audit columns (updated_by, updated_at) to dim tables.
--    Inputs: For sql-53 Exercise 2, change only `dim_customer`, and `dim_product` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `information_schema.columns` rows.
--    Expected result/shape: For sql-53 Exercise 2, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `updated_by`, and `day53_solution`.
--    Verify: For sql-53 Exercise 2, inspect `information_schema.columns` for `dim_customer`, and `dim_product`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
--    Hint ladder, rung 1: For sql-53 Exercise 2, inspect `information_schema.columns` for `dim_customer`, and `dim_product`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
-- 3. Prediction: explain why closing a version at CURRENT_DATE - 1 can create an
--    invalid range when two changes for one key arrive on the same date.
--    Inputs: For sql-53 Exercise 3, read from `dim_customer`. Build the answer toward `customer_id`, `valid_from`, `valid_to`, and `invalid_range`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-53 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`, `valid_from`, `valid_to`, and `invalid_range`. The final order is `valid_from`.
--    Verify: For sql-53 Exercise 3, run an anti-check that counts rows where NOT ((customer_id = 1)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `valid_from`, `valid_to`, and `invalid_range` against `dim_customer`. Add one row for which `(customer_id = 1)` is true and one for which it is false; verify only the matching `customer_id` value is returned.
--    Hint ladder, rung 1: For sql-53 Exercise 3, inspect the source keys that survive `WHERE`; then check `valid_from` before applying the row cap.
-- 4. Construction: add a constraint or exclusion-style validation that detects
--    overlapping effective ranges for each natural customer key.
--    Inputs: For sql-53 Exercise 4, read from `dim_customer`. Build the answer toward `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-53 Exercise 4, expected output: one row per `customer_id`. The final columns are `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to`. The final order is `a.customer_id, version_a, version_b`.
--    Verify: For sql-53 Exercise 4, project `customer_id` plus the raw source columns from `dim_customer` at each join stage; record row count and distinct `customer_id`, then assert the final `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to` values match those staged rows without unintended fanout or loss. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-53 Exercise 4, start with the first relation in `dim_customer`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.
-- 5. Debugging: make the SCD2 load idempotent so rerunning an unchanged source
--    creates no new version.
--    Inputs: For sql-53 Exercise 5, compare the current `dim_customer` row to `desired_customer_state`, which is copied from the same `staged_customer_change` used by Exercise 2.
--    Expected result/shape: For sql-53 Exercise 5, expected output: exactly one aggregate row, `unchanged_rows_that_would_version = 0`.
--    Verify: For sql-53 Exercise 5, rerun the nullable-safe attribute comparison against `desired_customer_state`; the result must report zero differences. Then alter one staged attribute and require a result of exactly one difference before applying any close/insert statements.
--    Hint ladder, rung 1: Prove both desired and current relations are unique on `customer_id`, then compare with `IS DISTINCT FROM`.
-- 6. Edge case: define a same-day change policy using timestamptz boundaries or
--    source sequence numbers, and explain the tradeoff.
--    Inputs: For sql-53 Exercise 6, read from `training.customers`, `dim_customer`, and `changed_customers`. Compute `first_version`, and `ROLLBACK` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-53 Exercise 6, expected output: exactly one aggregate summary row. The final columns are `first_version`, and `ROLLBACK`.
--    Verify: For sql-53 Exercise 6, evaluate each of `first_version`, and `ROLLBACK` in a separate control `SELECT` over `training.customers`, `dim_customer`, and `changed_customers`; require one final row and compare every value. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-53 Exercise 6, select `customer_id` from `training.customers`, `dim_customer`, and `changed_customers` before adding derived columns.

ROLLBACK;
