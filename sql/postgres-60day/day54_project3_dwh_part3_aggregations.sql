-- Day 54: Project 3 - Data Warehouse Design (Part 3)
-- BEGINNER WORKFLOW - sql-54: Project 3 DWH Part 3 Aggregations
-- Guide: sql/postgres-60day/companion-guides/day54_project3_dwh_part3_aggregations.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-54.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  year INT NOT NULL,
  month INT NOT NULL,
  category TEXT NOT NULL,
  revenue NUMERIC(14, 2) NOT NULL,
  PRIMARY KEY (year, month, category)
);

CREATE TABLE agg_sales_customer_month (
  year INT NOT NULL,
  month INT NOT NULL,
  customer_sk INT NOT NULL,
  revenue NUMERIC(14, 2) NOT NULL,
  PRIMARY KEY (year, month, customer_sk)
);

-- Initial full builds (would normally be incremental)
INSERT INTO agg_sales_category_month (year, month, category, revenue)
SELECT
  dd.year,
  dd.month,
  dp.category,
  ROUND(SUM(fs.amount), 2) AS revenue
FROM
  fact_sales fs
  JOIN dim_date dd ON dd.date_key = fs.date_key
  JOIN dim_product dp ON dp.product_sk = fs.product_sk
GROUP BY
  dd.year,
  dd.month,
  dp.category;

INSERT INTO agg_sales_customer_month (year, month, customer_sk, revenue)
SELECT
  dd.year,
  dd.month,
  fs.customer_sk,
  ROUND(SUM(fs.amount), 2) AS revenue
FROM
  fact_sales fs
  JOIN dim_date dd ON dd.date_key = fs.date_key
GROUP BY
  dd.year,
  dd.month,
  fs.customer_sk;

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
  SELECT
    dd.year,
    dd.month,
    dp.category,
    ROUND(SUM(fs.amount), 2) AS rev
  FROM
    fact_sales fs
    JOIN dim_date dd ON dd.date_key = fs.date_key
    JOIN dim_product dp ON dp.product_sk = fs.product_sk
  GROUP BY
    dd.year,
    dd.month,
    dp.category
),
diff AS (
  SELECT
    b.year,
    b.month,
    b.category,
    b.rev AS base_rev,
    a.revenue AS agg_rev,
    ROUND(coalesce(a.revenue, 0) - coalesce(b.rev, 0), 2) AS delta
  FROM
    base b
    FULL OUTER JOIN agg_sales_category_month a ON a.year = b.year
    AND a.month = b.month
    AND a.category = b.category
)
SELECT
  *
FROM
  diff
WHERE
  delta <> 0
ORDER BY
  year DESC,
  month DESC,
  category;

-- 2. Check for orphan SKs in agg_sales_customer_month
SELECT
  a.customer_sk
FROM
  agg_sales_customer_month a
  LEFT JOIN dim_customer dc ON dc.customer_sk = a.customer_sk
WHERE
  dc.customer_sk IS NULL
LIMIT 10;

-- Exercises
-- 1. Add an agg table agg_sales_product_month and validate it.
--    Inputs: For sql-54 Exercise 1, create `agg_sales_product_month` with `PRIMARY KEY (year, month, product_sk)` and load it by grouping the 13,085 `fact_sales` rows joined to `dim_date` on `date_key` by year, month, and `product_sk`, storing `ROUND(SUM(amount), 2)` as `revenue`, `SUM(quantity)` as `units`, and `COUNT(DISTINCT order_id)` as `orders`; then reconcile it against an independent per-month sum of `fact_sales`.
--    Expected result/shape: For sql-54 Exercise 1, expected output: the load inserts one row per year, month, and `product_sk` (6,741 rows on our load), and the reconciliation returns one row per month, 46 rows, with columns `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`, every `difference` 0.00. The final order is `a.year, a.month`. The solution file runs this full build inside `SAVEPOINT exercise_1` and rolls back to it, so Exercise 2 starts from an empty table.
--    Verify: For sql-54 Exercise 1, confirm that no (year, month, `product_sk`) appears twice, that February 2023 holds 6 product rows with 1,203.26 revenue and 17 units, and that November 2026 holds 234 product rows with 85,364.73 revenue. In the transaction, add 1.00 to the revenue of product 69 in February 2023: the reconciliation shows that month alone with `difference` 1.00. Then delete the February 2023 rows: the inner join drops to 45 months and reports no difference at all, which is the gap Exercise 5 closes.
--    Hint ladder, rung 1: For sql-54 Exercise 1, run `aggregate_total` and `fact_total` on their own first: each should return 46 rows, one per year and month, and both revenue columns should add up to the same 2,355,648.13 before you join them.
-- 2. Create a stored procedure to refresh a given y, m across all aggs.
--    Inputs: For sql-54 Exercise 2, write `refresh_sales_aggregates_solution(p_year, p_month)` so it deletes that month from `agg_sales_category_month`, `agg_sales_customer_month`, and `agg_sales_product_month` and reinserts it from `fact_sales` joined to `dim_date` (and to `dim_product` for the category); call it for the newest fact month, then reconcile the product aggregate against `fact_sales` for the months it holds.
--    Expected result/shape: For sql-54 Exercise 2, expected output: the procedure returns nothing; the call leaves 6 category rows, 73 customer rows, and 234 product rows, all for November 2026 on our load, and the reconciliation returns 1 row with columns `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference` (2026, 11, 85,364.73, 85,364.73, 0.00 on our load). The query has no `ORDER BY` because it returns one month.
--    Verify: For sql-54 Exercise 2, check that all three tables sum to 85,364.73 revenue, that the category `units` total 1,399, and that the customer `orders` total 151, the same as `COUNT(DISTINCT order_id)` for that month in `fact_sales`. Call the procedure again for 2026-11 and then for 2030-01, a month with no facts: the counts stay 6, 73, and 234. Call it for 2023-02: the counts become 12, 75, and 240, and the reconciliation returns 2 rows, both with `difference` 0.00.
--    Hint ladder, rung 1: For sql-54 Exercise 2, write and test the three `DELETE` plus `INSERT ... SELECT` pairs for one hard-coded month first, then replace the literals with `p_year` and `p_month`; after a call, `SELECT year, month, count(*)` on each table should show only that month.
-- 3. Prediction: explain why refreshing only the current month misses a
--    late-arriving fact for a previous month.
--    Inputs: For sql-54 Exercise 3, group the 13,085 `fact_sales` rows joined to `dim_date` by year and month, counting the fact rows and taking `MAX(date_actual)` as the latest loaded day of each month.
--    Expected result/shape: For sql-54 Exercise 3, expected output: 46 rows, one per year and month from February 2023 to November 2026, with columns `year`, `month`, `fact_rows`, and `latest_fact_date`, ordered by `dd.year DESC, dd.month DESC`. On our load October 2026 has 965 rows ending 2026-10-31, the partial November 2026 has 468 rows ending 2026-11-23, and February 2023 has 6 rows, all on 2023-02-13.
--    Verify: For sql-54 Exercise 3, confirm that `fact_rows` adds up to 13,085. In a transaction, insert a late fact for order 3739, product 69, `order_item_id` 999999, `date_key` 20230220, and amount 35.53: February 2023 rises to 7 rows with `latest_fact_date` 2023-02-20. If February 2023 was already refreshed, the Exercise 5 reconciliation now shows it with 1,203.26 against 1,238.79, a `difference` of -35.53, until the procedure is called for 2023-02 again; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-54 Exercise 3, count `fact_sales` first (13,085), then count the join to `dim_date` on `date_key`; it keeps all 13,085 rows because the foreign key guarantees a calendar row for every `date_key`, so the grouped counts must add back to that total.
-- 4. Construction: implement delete-and-insert refresh for one closed month in
--    a transaction and return inserted row counts.
--    Inputs: For sql-54 Exercise 4, after the Exercise 2 call has deleted and reinserted the newest month inside the open transaction, group `agg_sales_category_month` by year and month, counting the category rows and summing their revenue.
--    Expected result/shape: For sql-54 Exercise 4, expected output: one row per refreshed month, 1 row on our load (2026, 11, 6 category rows, 85,364.73 revenue), with columns `year`, `month`, `category_rows`, and `revenue`. The final order is `year DESC, month DESC`.
--    Verify: For sql-54 Exercise 4, list the six categories for the month (Apparel 14,026.26, Beauty 13,151.38, Books 15,823.05, Electronics 13,811.36, Home 12,125.38, and Sports 16,427.30 on our load) and confirm that they add up to the reported revenue. Call the procedure for 2023-02 as well: the query returns 2 rows, 2026-11 first and then 2023-02 with 6 rows and 1,203.26. After the file's `ROLLBACK`, `to_regclass('dwh.agg_sales_category_month')` returns `NULL`.
--    Hint ladder, rung 1: For sql-54 Exercise 4, count rows per year and month in `agg_sales_category_month` before calling the procedure (none here, since the table starts empty); after the call, the only new group should be the month you passed, with one row per category that has facts in it.
-- 5. Debugging: repair the FULL JOIN reconciliation so a row missing from either
--    the fact aggregate or stored aggregate is reported, not hidden by NULL math.
--    Inputs: For sql-54 Exercise 5, sum `agg_sales_category_month` revenue by year and month in `aggregate_total`, sum the `fact_sales` amounts joined to `dim_date` by year and month in `fact_total`, and `FULL JOIN` the two on year and month, keeping the rows where `a.revenue IS DISTINCT FROM f.revenue`.
--    Expected result/shape: For sql-54 Exercise 5, expected output: 45 rows on our load, one for every fact month the aggregate does not hold (all but the refreshed November 2026), with columns `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`, ordered by `year, month`. Each row has a `NULL` `aggregate_revenue` and a `difference` equal to minus its fact revenue, for example -1,203.26 for February 2023.
--    Verify: For sql-54 Exercise 5, call the procedure for 2023-02 and confirm that the result drops to 44 rows, now starting at March 2023. Then insert a category row for 2030-01 (Books, 10.00 revenue, 1 unit) that has no facts: it appears with a `NULL` `fact_revenue` and a `difference` of 10.00, for 45 rows. An inner join with `<>` would return neither kind of row; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-54 Exercise 5, run `aggregate_total` (1 row) and `fact_total` (46 rows) separately, then the `FULL JOIN` without the `WHERE`: it returns 46 rows, 45 of them with a `NULL` aggregate side.
-- 6. Edge case: rerun the same month refresh twice and prove both row count and
--    revenue are identical (idempotency).
--    Inputs: For sql-54 Exercise 6, copy `agg_sales_category_month` into the temporary table `aggregate_snapshot_before`, call the refresh again for the same newest month, and compare the snapshot with the live table using `EXCEPT` in both directions, labeling each side.
--    Expected result/shape: For sql-54 Exercise 6, expected output: 0 rows on the course data, because the second refresh deletes and rewrites the same 6 category rows with the same values. The final columns are `side`, `year`, `month`, `category`, `revenue`, and `units`, where `side` is `before_minus_after` or `after_minus_before`; the query has no `ORDER BY`.
--    Verify: For sql-54 Exercise 6, check that the snapshot and the live table both hold 6 rows with 85,364.73 revenue after the rerun. Then, in a transaction, insert a late November 2026 fact (order 3739, product 69, `order_item_id` 999999, `date_key` 20261120, amount 35.53) between the snapshot and the rerun: the query returns 2 Home rows, `before_minus_after` with 12,125.38 and 209 units and `after_minus_before` with 12,160.91 and 210 units, which proves that the comparison catches a real change; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-54 Exercise 6, run each `EXCEPT` on its own before adding the `UNION ALL`; both should return 0 rows, and `count(*)` and `sum(revenue)` should give 6 and 85,364.73 on both the snapshot and the live table.
ROLLBACK;
