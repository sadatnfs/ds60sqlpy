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
--    Inputs: Use only the declared lesson objects (training.customers, dim_customer, training.products, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Add audit columns (updated_by, updated_at) to dim tables.
--    Inputs: Use only the declared lesson objects (training.customers, dim_customer, training.products, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 3. Prediction: explain why closing a version at CURRENT_DATE - 1 can create an
--    invalid range when two changes for one key arrive on the same date.
--    Inputs: Use only the declared lesson objects (training.customers, dim_customer, training.products, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 4. Construction: add a constraint or exclusion-style validation that detects
--    overlapping effective ranges for each natural customer key.
--    Inputs: Use only the declared lesson objects (training.customers, dim_customer, training.products, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 5. Debugging: make the SCD2 load idempotent so rerunning an unchanged source
--    creates no new version.
--    Inputs: Use only the declared lesson objects (training.customers, dim_customer, training.products, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: define a same-day change policy using timestamptz boundaries or
--    source sequence numbers, and explain the tradeoff.
--    Inputs: Use only the declared lesson objects (training.customers, dim_customer, training.products, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
