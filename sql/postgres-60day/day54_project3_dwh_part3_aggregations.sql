-- Day 54: Project 3 - Data Warehouse Design (Part 3)
-- BEGINNER WORKFLOW — sql-54: Project3 DWH Part3 Aggregations
-- Guide: sql/postgres-60day/companion-guides/day54_project3_dwh_part3_aggregations.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-54/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: agg_sales_category_month, agg_sales_customer_month, fact_sales, dim_date, dim_product.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Topics: Aggregation tables and DQ checks in DWH
BEGIN;
SET search_path TO dwh, training, public;

-- Aggregate tables (star-schema rollups)
CREATE TABLE agg_sales_category_month (
  year    INT NOT NULL,
  month   INT NOT NULL,
  category TEXT NOT NULL,
  revenue NUMERIC(14,2) NOT NULL,
  PRIMARY KEY (year, month, category)
);

CREATE TABLE agg_sales_customer_month (
  year     INT NOT NULL,
  month    INT NOT NULL,
  customer_sk INT NOT NULL,
  revenue  NUMERIC(14,2) NOT NULL,
  PRIMARY KEY (year, month, customer_sk)
);

-- Initial full builds (would normally be incremental)
INSERT INTO agg_sales_category_month(year, month, category, revenue)
SELECT dd.year,
       dd.month,
       dp.category,
       ROUND(SUM(fs.amount),2) AS revenue
FROM fact_sales fs
JOIN dim_date dd    ON dd.date_key = fs.date_key
JOIN dim_product dp ON dp.product_sk = fs.product_sk
GROUP BY dd.year, dd.month, dp.category;

INSERT INTO agg_sales_customer_month(year, month, customer_sk, revenue)
SELECT dd.year,
       dd.month,
       fs.customer_sk,
       ROUND(SUM(fs.amount),2) AS revenue
FROM fact_sales fs
JOIN dim_date dd ON dd.date_key = fs.date_key
GROUP BY dd.year, dd.month, fs.customer_sk;

-- Example incremental refresh for a given month (delete + insert)
-- WITH target AS (
--   SELECT 2026 AS y, 1 AS m
-- )
-- DELETE FROM agg_sales_category_month a
-- USING target t
-- WHERE a.year = t.y AND a.month = t.m;
-- INSERT INTO agg_sales_category_month(year, month, category, revenue)
-- SELECT t.y, t.m, dp.category, ROUND(SUM(fs.amount),2)
-- FROM fact_sales fs
-- JOIN dim_date dd ON dd.date_key = fs.date_key
-- JOIN dim_product dp ON dp.product_sk = fs.product_sk
-- JOIN target t ON dd.year = t.y AND dd.month = t.m
-- GROUP BY dp.category, t.y, t.m;

-- Data Quality checks: reconciling aggregates to facts
-- 1. Compare monthly category revenue between agg and base
WITH base AS (
  SELECT dd.year, dd.month, dp.category, ROUND(SUM(fs.amount),2) AS rev
  FROM fact_sales fs
  JOIN dim_date dd ON dd.date_key = fs.date_key
  JOIN dim_product dp ON dp.product_sk = fs.product_sk
  GROUP BY dd.year, dd.month, dp.category
), diff AS (
  SELECT b.year, b.month, b.category,
         b.rev AS base_rev,
         a.revenue AS agg_rev,
         ROUND(coalesce(a.revenue,0) - coalesce(b.rev,0),2) AS delta
  FROM base b
  FULL OUTER JOIN agg_sales_category_month a
    ON a.year = b.year AND a.month = b.month AND a.category = b.category
)
SELECT * FROM diff WHERE delta <> 0 ORDER BY year DESC, month DESC, category;

-- 2. Check for orphan SKs in agg_sales_customer_month
SELECT a.customer_sk
FROM agg_sales_customer_month a
LEFT JOIN dim_customer dc ON dc.customer_sk = a.customer_sk
WHERE dc.customer_sk IS NULL
LIMIT 10;

-- Exercises
-- 1. Add an agg table agg_sales_product_month and validate it.
--    Inputs: For sql-54 Exercise 1, read from `dim_product`, `agg_sales_product_month`, `fact_sales`, and `dim_date`. Build the answer toward `year`, `month`, and `product_sk`; keep `year`, `month`, and `product_sk` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-54 Exercise 1, expected output: one row per `year`, `month`, and `product_sk`. The final columns are `year`, `month`, and `product_sk`. The final order is `a.year, a.month`.
--    Verify: For sql-54 Exercise 1, independently aggregate `dim_product`, `agg_sales_product_month`, `fact_sales`, and `dim_date` by `year`, `month`, and `product_sk`; require one output row for every distinct `year`, `month`, and `product_sk` tuple and compare `product_sk` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `year`, and `month` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-54 Exercise 1, run `aggregate_total`, and `fact_total` one at a time. Record each CTE's row count and `year`, `month`, and `product_sk` uniqueness before the next stage uses it.
-- 2. Create a stored procedure to refresh a given y, m across all aggs.
--    Inputs: For sql-54 Exercise 2, read from `agg_sales_category_month`, `agg_sales_customer_month`, `agg_sales_product_month`, `fact_sales`, and `dim_date`. Build the answer toward `year`, `month`, and `category`; keep `year`, `month`, and `product_sk` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-54 Exercise 2, expected output: one row per `year`, `month`, and `product_sk`. The final columns are `year`, `month`, and `category`. The final order is `dd.year DESC, dd.month DESC`.
--    Verify: For sql-54 Exercise 2, assert no more than 1 rows, no duplicate `year`, `month`, and `product_sk`, and no adjacent pair that violates `dd.year DESC, dd.month DESC`. Rejoin the returned keys to `agg_sales_category_month`, `agg_sales_customer_month`, `agg_sales_product_month`, `fact_sales`, and `dim_date` to confirm `year`, `month`, and `category` came from the same source rows. Run with 1 minus one and 1 plus one eligible rows; require the output cap of 1 while retaining `dd.year DESC, dd.month DESC`.
--    Hint ladder, rung 1: For sql-54 Exercise 2, run `aggregate_total`, and `fact_total` one at a time. Record each CTE's row count and `year`, `month`, and `product_sk` uniqueness before the next stage uses it.
-- 3. Prediction: explain why refreshing only the current month misses a
--    late-arriving fact for a previous month.
--    Inputs: For sql-54 Exercise 3, read from `fact_sales`, and `dim_date`. Build the answer toward `year`, `month`, `fact_rows`, and `latest_fact_date`; keep `year`, and `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-54 Exercise 3, expected output: one row per `year`, and `month`. The final columns are `year`, `month`, `fact_rows`, and `latest_fact_date`. The final order is `dd.year DESC, dd.month DESC`.
--    Verify: For sql-54 Exercise 3, independently aggregate `fact_sales`, and `dim_date` by `year`, and `month`; require one output row for every distinct `year`, and `month` tuple and compare `fact_rows` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `fact_rows` for the existing `year`, and `month` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-54 Exercise 3, start with the first relation in `fact_sales`, and `dim_date`; after each join, record total rows and distinct `year`, and `month` so the exact fanout or loss is visible.
-- 4. Construction: implement delete-and-insert refresh for one closed month in
--    a transaction and return inserted row counts.
--    Inputs: For sql-54 Exercise 4, read the target keys from `agg_sales_category_month` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-54 Exercise 4, expected output: the command tag and an independently counted set of affected `year`, and `month` values. The final columns are `year`, `month`, `category_rows`, and `revenue`. The final order is `year DESC, month DESC`.
--    Verify: For sql-54 Exercise 4, materialize the intended `year`, and `month` target set first; require the command tag/`RETURNING` set to match it, then query `agg_sales_category_month` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `year`, and `month` values in both cases.
--    Hint ladder, rung 1: For sql-54 Exercise 4, materialize the intended `year`, and `month` target set first; require the command tag/`RETURNING` set to match it, then query `agg_sales_category_month` again and prove rollback or idempotent retry.
-- 5. Debugging: repair the FULL JOIN reconciliation so a row missing from either
--    the fact aggregate or stored aggregate is reported, not hidden by NULL math.
--    Inputs: For sql-54 Exercise 5, read from `agg_sales_category_month`, `fact_sales`, `dim_date`, and `f.revenue`. Build the answer toward `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`; keep `year`, and `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-54 Exercise 5, expected output: one row per `year`, and `month`. The final columns are `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`. The final order is `year, month`.
--    Verify: For sql-54 Exercise 5, project `year`, and `month` plus the raw source columns from `agg_sales_category_month`, `fact_sales`, `dim_date`, and `f.revenue` at each join stage; record row count and distinct `year`, and `month`, then assert the final `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference` values match those staged rows without unintended fanout or loss. Repeat with `NULL` in `year`, and `month` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-54 Exercise 5, run `aggregate_total`, and `fact_total` one at a time. Record each CTE's row count and `year`, and `month` uniqueness before the next stage uses it.
-- 6. Edge case: rerun the same month refresh twice and prove both row count and
--    revenue are identical (idempotency).
--    Inputs: For sql-54 Exercise 6, read from `agg_sales_category_month`, `fact_sales`, `dim_date`, and `aggregate_snapshot_before`. Build the answer toward `except`; keep `except` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-54 Exercise 6, expected output: at most one row keyed by `except`. The final columns are `except`. The final order is `dd.year DESC, dd.month DESC`.
--    Verify: For sql-54 Exercise 6, assert no more than 1 rows, no duplicate `except`, and no adjacent pair that violates `dd.year DESC, dd.month DESC`. Rejoin the returned keys to `agg_sales_category_month`, `fact_sales`, `dim_date`, and `aggregate_snapshot_before` to confirm `except` came from the same source rows. Add duplicate source candidates for `except`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
--    Hint ladder, rung 1: For sql-54 Exercise 6, start with the first relation in `agg_sales_category_month`, `fact_sales`, `dim_date`, and `aggregate_snapshot_before`; after each join, record total rows and distinct `except` so the exact fanout or loss is visible.

ROLLBACK;
