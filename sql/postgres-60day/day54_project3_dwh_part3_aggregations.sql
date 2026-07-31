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
--    Inputs: Use only the declared lesson objects (agg_sales_category_month, agg_sales_customer_month, fact_sales, dim_date, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 2. Create a stored procedure to refresh a given y, m across all aggs.
--    Inputs: Use only the declared lesson objects (agg_sales_category_month, agg_sales_customer_month, fact_sales, dim_date, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 3. Prediction: explain why refreshing only the current month misses a
--    late-arriving fact for a previous month.
--    Inputs: Use only the declared lesson objects (agg_sales_category_month, agg_sales_customer_month, fact_sales, dim_date, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: implement delete-and-insert refresh for one closed month in
--    a transaction and return inserted row counts.
--    Inputs: Use only the declared lesson objects (agg_sales_category_month, agg_sales_customer_month, fact_sales, dim_date, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: repair the FULL JOIN reconciliation so a row missing from either
--    the fact aggregate or stored aggregate is reported, not hidden by NULL math.
--    Inputs: Use only the declared lesson objects (agg_sales_category_month, agg_sales_customer_month, fact_sales, dim_date, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: rerun the same month refresh twice and prove both row count and
--    revenue are identical (idempotency).
--    Inputs: Use only the declared lesson objects (agg_sales_category_month, agg_sales_customer_month, fact_sales, dim_date, dim_product) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
