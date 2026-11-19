-- Day 53: Project 3 - Data Warehouse Design (Part 2)
-- BEGINNER WORKFLOW - sql-53: Project 3 DWH Part 2 SCD
-- Guide: sql/postgres-60day/companion-guides/day53_project3_dwh_part2_scd.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-53.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: training.customers, dim_customer, dim_country, training.products, dim_product.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Topics: Slowly Changing Dimensions (Type 2) for customers/products
BEGIN;
SET search_path TO dwh, training, public;

-- Starting contract from Day 52 Exercise 1: every dim_customer version links
-- to dim_country through a NOT NULL country_sk. If your committed Day 52 already
-- did that, these idempotent statements change nothing; if you ran only the
-- Day 52 base load, they add the same link inside this rolled-back transaction.
-- IF NOT EXISTS adopts an existing table without checking its shape, so the
-- load below looks keys up in a way that fails loudly instead of guessing.
CREATE TABLE IF NOT EXISTS dim_country (
  country_sk int GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  country_code text NOT NULL UNIQUE
);

INSERT INTO dim_country (country_code)
SELECT DISTINCT
  c.country
FROM
  training.customers c
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      dim_country co
    WHERE
      co.country_code = c.country)
ORDER BY
  c.country;

ALTER TABLE dim_customer
  ADD COLUMN IF NOT EXISTS country_sk int REFERENCES dim_country (country_sk);

UPDATE
  dim_customer dc
SET
  country_sk = co.country_sk
FROM
  dim_country co
WHERE
  co.country_code = dc.country
  AND dc.country_sk IS NULL;

ALTER TABLE dim_customer
  ALTER COLUMN country_sk SET NOT NULL;

-- Example SCD Type 2 upsert for dim_customer
-- Assumption: source-of-truth is training.customers; we detect changes by comparing attributes
-- Steps per changed business key:
--   1) Close current row (set valid_to = today - 1, is_current = false)
--   2) Insert new row with updated attributes (valid_from = today, is_current = true)
-- Simulate a change in the OLTP source (demo only)
CREATE TEMP TABLE changed_customers AS
SELECT
  c.customer_id,
  c.full_name,
  c.country,
  CASE WHEN c.segment = 'platinum' THEN
    'gold'
  ELSE
    'platinum'
  END AS segment
FROM
  training.customers c
ORDER BY
  c.customer_id
LIMIT 10;

-- Detect current rows that differ from source attributes
WITH current_dim AS (
  SELECT
    dc.*
  FROM
    dim_customer dc
  WHERE
    dc.is_current
),
diffs AS (
  SELECT
    s.customer_id,
    s.full_name,
    s.country,
    s.segment
  FROM
    changed_customers s
    JOIN current_dim dc ON dc.customer_id = s.customer_id
  WHERE
    coalesce(s.full_name, '') <> coalesce(dc.full_name, '')
    OR coalesce(s.country, '') <> coalesce(dc.country, '')
    OR coalesce(s.segment, '') <> coalesce(dc.segment, '')
),
closed AS (
  UPDATE
    dim_customer dc
  SET
    valid_to = CURRENT_DATE -1,
    is_current = FALSE
  FROM
    diffs d
  WHERE
    dc.customer_id = d.customer_id
    AND dc.is_current
  RETURNING
    dc.customer_id)
  -- A new version carries every attribute, including the Day 52 country_sk.
  -- The scalar lookup returns NULL for a country missing from dim_country (the
  -- NOT NULL rule then rejects the whole statement, so no row is closed) and
  -- raises an error if dim_country repeats a code. An inner join would instead
  -- drop that customer's new version after its old row had been closed.
  INSERT INTO dim_customer (customer_id, full_name, country, segment, country_sk, valid_from, valid_to, is_current)
  SELECT
    d.customer_id,
    d.full_name,
    d.country,
    d.segment,
    (
      SELECT
        co.country_sk
      FROM
        dim_country co
      WHERE
        co.country_code = d.country), CURRENT_DATE, NULL, TRUE
  FROM
    diffs d;

-- Every version must point at the dim_country row for its own country.
SELECT
  COUNT(*) AS customer_versions,
  COUNT(*) FILTER (WHERE co.country_code IS DISTINCT FROM dc.country) AS mismatched_country_keys
FROM
  dim_customer dc
  LEFT JOIN dim_country co ON co.country_sk = dc.country_sk;

-- Verify multiple versions per customer
SELECT
  customer_id,
  COUNT(*) AS versions,
  MIN(valid_from) AS first_seen,
  MAX(coalesce(valid_to, CURRENT_DATE)) AS last_seen
FROM
  dim_customer
GROUP BY
  customer_id
ORDER BY
  versions DESC,
  customer_id
LIMIT 10;

-- SCD Type 2 for dim_product (similar pattern)
CREATE TEMP TABLE changed_products AS
SELECT
  p.product_id,
  p.name,
  p.category,
  round(p.price * 1.05, 2) AS price,
  p.cost
FROM
  training.products p
ORDER BY
  p.product_id
LIMIT 10;

WITH current_p AS (
  SELECT
    *
  FROM
    dim_product
  WHERE
    is_current
),
diffs AS (
  SELECT
    s.*
  FROM
    changed_products s
    JOIN current_p dp ON dp.product_id = s.product_id
  WHERE
    coalesce(s.name, '') <> coalesce(dp.name, '')
    OR coalesce(s.category, '') <> coalesce(dp.category, '')
    OR coalesce(s.price, 0) <> coalesce(dp.price, 0)
    OR coalesce(s.cost, 0) <> coalesce(dp.cost, 0)
),
close_p AS (
  UPDATE
    dim_product dp
  SET
    valid_to = CURRENT_DATE -1,
    is_current = FALSE
  FROM
    diffs d
  WHERE
    dp.product_id = d.product_id
    AND dp.is_current
  RETURNING
    dp.product_id)
INSERT INTO dim_product (product_id, name, category, price, cost, valid_from, valid_to, is_current)
SELECT
  d.product_id,
  d.name,
  d.category,
  d.price,
  d.cost,
  CURRENT_DATE,
  NULL,
  TRUE
FROM
  diffs d;

-- Fact table joins should point to is_current at load time; for historical facts you would key by date to choose appropriate SCD version.
-- Exercises
-- 1. Implement SCD2 change capture keyed by date_key (choose version where valid_from <= order_date <= coalesce(valid_to,'infinity')).
--    Inputs: For sql-53 Exercise 1, map every `training.order_items` row to `dim_date`, to the `dim_customer` version whose `valid_from <= order_date::date <= COALESCE(valid_to, 'infinity')`, and to the matching `dim_product` version, after the Exercise 2 change gave customer 1 a second version.
--    Expected result/shape: For sql-53 Exercise 1, expected output: the temporary table `fact_sales_temporal_solution`, one row per `order_item_id`, with columns `order_id`, `order_item_id`, `date_key`, `customer_sk`, `product_sk`, `quantity`, `unit_price`, `discount`, and `amount`; the check row reports `mapped_fact_rows = 13085`, `source_item_rows = 13085`, and `customer_versions = 2`.
--    Verify: For sql-53 Exercise 1, confirm that `SELECT COUNT(DISTINCT order_item_id) FROM fact_sales_temporal_solution` also returns 13,085, so no item was duplicated by overlapping versions or lost in a validity gap; for customer 1, check that orders dated before the change map to the closed version's `customer_sk` and later orders to the current one.
--    Hint ladder, rung 1: For sql-53 Exercise 1, the date join picks one day; the customer and product joins must each pick exactly one version that is valid on that day.
-- 2. Add audit columns (updated_by, updated_at) to dim tables.
--    Inputs: For sql-53 Exercise 2, add `updated_by text NOT NULL DEFAULT CURRENT_USER` and `updated_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP` to `dim_customer` and `dim_product`, then apply one staged segment change for customer 1 as an SCD2 close-and-insert whose new version also carries `country_sk`.
--    Expected result/shape: For sql-53 Exercise 2, expected output: two `ALTER TABLE` command tags for the audit columns, then `SELECT 1`, `UPDATE 1`, and `INSERT 0 1` for the staged change; the closed and the new customer 1 rows both carry `updated_by = 'day53_solution'`.
--    Verify: For sql-53 Exercise 2, query `information_schema.columns` for `table_schema = 'dwh'` and both tables and confirm the two new columns with `is_nullable = 'NO'`; after a savepoint, `UPDATE dim_customer SET updated_by = NULL WHERE customer_id = 1` must fail with SQLSTATE `23502` (not-null violation), then roll back to the savepoint.
--    Hint ladder, rung 1: For sql-53 Exercise 2, a `NOT NULL` column added with a `DEFAULT` fills every existing row with that default, so the `ALTER TABLE` succeeds on a populated table.
-- 3. Prediction: explain why closing a version at CURRENT_DATE - 1 can create an
--    invalid range when two changes for one key arrive on the same date.
--    Inputs: For sql-53 Exercise 3, list customer 1's versions from `dim_customer` with `valid_from`, `valid_to`, and the flag `invalid_range = (valid_to IS NOT NULL AND valid_to < valid_from)`.
--    Expected result/shape: For sql-53 Exercise 3, expected output: two rows ordered by `valid_from`, both with `invalid_range = false`; the closed version ends on `CURRENT_DATE - 31`, the day before the current version begins on `CURRENT_DATE - 30`.
--    Verify: For sql-53 Exercise 3, after a savepoint, apply a second change for customer 1 with the same effective date: closing the current version at `effective_date - 1` gives it a `valid_to` earlier than its `valid_from`, so the flag becomes `true` for that row. That is why date-grain versions cannot order two changes on one date.
--    Hint ladder, rung 1: For sql-53 Exercise 3, write both versions on a calendar first; then ask what `effective_date - 1` means for a version that started on `effective_date`.
-- 4. Construction: add a constraint or exclusion-style validation that detects
--    overlapping effective ranges for each natural customer key.
--    Inputs: For sql-53 Exercise 4, self-join `dim_customer` on `customer_id` with `b.customer_sk > a.customer_sk`, keeping pairs whose inclusive ranges overlap: `a.valid_from <= COALESCE(b.valid_to, 'infinity')` and `b.valid_from <= COALESCE(a.valid_to, 'infinity')`.
--    Expected result/shape: For sql-53 Exercise 4, expected output: zero rows with columns `customer_id`, `version_a`, `version_b`, `a_from`, `a_to`, `b_from`, and `b_to`, ordered by `a.customer_id, version_a, version_b`, because every customer's versions are disjoint after the Exercise 2 change.
--    Verify: For sql-53 Exercise 4, after a savepoint, set the closed version's `valid_to` to the new version's `valid_from` and confirm that exactly one row appears for `customer_id = 1`; each overlapping pair is reported once because of `b.customer_sk > a.customer_sk`.
--    Hint ladder, rung 1: For sql-53 Exercise 4, two inclusive ranges overlap when neither ends before the other begins.
-- 5. Debugging: make the SCD2 load idempotent so rerunning an unchanged source
--    creates no new version.
--    Inputs: For sql-53 Exercise 5, compare the current `dim_customer` row to `desired_customer_state`, which is copied from the same `staged_customer_change` used by Exercise 2.
--    Expected result/shape: For sql-53 Exercise 5, expected output: exactly one aggregate row, `unchanged_rows_that_would_version = 0`.
--    Verify: For sql-53 Exercise 5, rerun the nullable-safe attribute comparison against `desired_customer_state`; the result must report zero differences. Then alter one staged attribute and require a result of exactly one difference before applying any close/insert statements.
--    Hint ladder, rung 1: Prove both desired and current relations are unique on `customer_id`, then compare with `IS DISTINCT FROM`.
-- 6. Edge case: define a same-day change policy using timestamptz boundaries or
--    source sequence numbers, and explain the tradeoff.
--    Inputs: For sql-53 Exercise 6, model two same-day versions with half-open `tstzrange` values, `[2026-01-15 09:00+00, 2026-01-15 12:00+00)` and `[2026-01-15 12:00+00, infinity)`, instead of inclusive date ranges.
--    Expected result/shape: For sql-53 Exercise 6, expected output: one row with columns `first_version` and `second_version` showing the two ranges; they meet at 12:00 without overlapping, because the `)` upper bound is exclusive.
--    Verify: For sql-53 Exercise 6, confirm that `first_version && second_version` returns `false`, `first_version -|- second_version` (adjacent) returns `true`, and that `'2026-01-15 12:00+00'::timestamptz <@ second_version` returns `true` while the same test against `first_version` returns `false`.
--    Hint ladder, rung 1: For sql-53 Exercise 6, a half-open range `[start, end)` lets the next version begin exactly where the previous one ends.
ROLLBACK;
