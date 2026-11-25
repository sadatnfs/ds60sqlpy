-- Day 30: Phase 2 Project - Multi-stage Analysis
-- BEGINNER WORKFLOW - sql-30: Phase2 Project
-- Guide: sql/postgres-60day/companion-guides/day30_phase2_project.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-30.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Build a cohort-retention analysis through explicit grains, a stable denominator, a dense calendar, reconciled revenue, and clearly limited projections.
-- Assumptions: Cohort month is customer creation month in UTC. Active means at least one order in the order month. Net revenue is computed from line items.
-- Pitfall: Observed rows are not a complete calendar; active customers must not exceed original cohort size, and a moving average is not a production CLV model.
-- Predict row grain and NULL/order behavior before executing each example.
-- Example: Customer lifetime value with cohort analysis
WITH orders_enriched AS (
  SELECT
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS order_month_utc,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
),
cohorts AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date AS cohort_month_utc
  FROM
    customers c
),
cohort_sizes AS (
  -- The denominator includes customers who never place an order.
  SELECT
    cohort_month_utc,
    COUNT(*) AS original_customers
  FROM
    cohorts
  GROUP BY
    cohort_month_utc
),
metrics AS (
  SELECT
    e.customer_id,
    c.cohort_month_utc,
    e.order_month_utc,
    SUM(e.order_value) AS revenue
  FROM
    orders_enriched e
    JOIN cohorts c ON c.customer_id = e.customer_id
  GROUP BY
    e.customer_id,
    c.cohort_month_utc,
    e.order_month_utc
),
cohort_agg AS (
  SELECT
    cohort_month_utc,
    order_month_utc,
    (EXTRACT(YEAR FROM age(order_month_utc, cohort_month_utc)) * 12 + EXTRACT(MONTH FROM age(order_month_utc, cohort_month_utc)))::int AS month_offset,
    SUM(revenue) AS cohort_revenue,
    COUNT(DISTINCT customer_id) AS active_customers
  FROM
    metrics
  GROUP BY
    cohort_month_utc,
    order_month_utc)
  -- This first pass contains observed activity months only. Exercise 4 creates
  -- a dense offset spine so a missing month becomes an explicit zero.
  SELECT
    agg.cohort_month_utc,
    agg.month_offset,
    sizes.original_customers,
    agg.active_customers,
    ROUND(agg.active_customers::numeric / NULLIF (sizes.original_customers, 0), 4) AS retention_rate,
    ROUND(agg.cohort_revenue, 2) AS revenue,
    ROUND(agg.cohort_revenue / NULLIF (agg.active_customers, 0), 2) AS revenue_per_active
  FROM
    cohort_agg AS agg
    JOIN cohort_sizes AS sizes ON sizes.cohort_month_utc = agg.cohort_month_utc
  ORDER BY
    agg.cohort_month_utc DESC,
    agg.month_offset
  LIMIT 200;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate original customer count for each UTC signup cohort month.
--    Hint: Build the denominator from customers, including customers who never order.
--    Inputs: For sql-30 Exercise 1, read the 500 rows of `customers`, assign each one a `cohort_month` with `date_trunc('month', created_at AT TIME ZONE 'UTC')::date` in the `cohorts` CTE, and count customers per month.
--    Expected result/shape: For sql-30 Exercise 1, expected output: one row per UTC signup month, 48 on this load (from 2022-11-01 through 2026-10-01), with `cohort_size` between 7 and 12 and a total of 500. The final columns are `cohort_month`, and `cohort_size`. The final order is `cohort_month`.
--    Verify: For sql-30 Exercise 1, confirm `SUM(cohort_size)` is 500, the `customers` row count, so no customer is dropped by the UTC conversion; then, inside `BEGIN ... ROLLBACK`, insert one customer with the default `created_at` (now) and confirm a new cohort for the current month appears with size 1 while every older cohort keeps its count.
--    Hint ladder, rung 1: For sql-30 Exercise 1, run `cohorts` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 2. [Query writing] Calculate active customers and net line revenue for each cohort/order month.
--    Hint: Aggregate line items to order grain before cohort joins, then count distinct active customers.
--    Inputs: For sql-30 Exercise 2, read `orders` and `order_items` to build one net value per order and UTC `order_month` in `order_values`, read `customers` for each signup `cohort_month` in `cohorts`, then join the two on `customer_id` and group by cohort and order month.
--    Expected result/shape: For sql-30 Exercise 2, expected output: one row per cohort and order month with activity, 1060 rows on this load across all 48 cohorts; the first is cohort 2022-11-01 in order month 2023-02-01 with 2 active customers and 1203.26 of revenue. The final columns are `cohort_month`, `order_month`, `active_customers`, and `net_revenue`. The final order is `c.cohort_month, ov.order_month`.
--    Verify: For sql-30 Exercise 2, confirm `SUM(active_customers)` is 3912, equal to `COUNT(DISTINCT (customer_id, order_month))` over `order_values`, and that `SUM(net_revenue)` is 2355647.39, a few cents above the unrounded 2355647.12 because each cell is rounded; also confirm 0 rows have `order_month < cohort_month`, so no order predates its customer's signup.
--    Hint ladder, rung 1: For sql-30 Exercise 2, run `order_values`, and `cohorts` one at a time. Record each CTE's row count and `cohort_month`, and `order_month` uniqueness before the next stage uses it.
-- 3. [Query writing] Calculate cohort month offset and retention using original cohort size.
--    Hint: Use year-plus-month age components and guard the denominator.
--    Inputs: For sql-30 Exercise 3, read `customers` for each signup `cohort_month` and its `cohort_size`, read `orders` for distinct active customers per cohort and UTC order month in `activity`, then compute `month_offset` with `age()` and divide active customers by the original cohort size.
--    Expected result/shape: For sql-30 Exercise 3, expected output: 1060 observed cohort and offset rows on this load, with `month_offset` from 0 to 45 and `retention_rate` between 0.0833 and 0.9091; only 12 cohorts have an offset 0 row, and the first cohort, 2022-11-01, starts at offset 3. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`. The final order is `a.cohort_month, month_offset`.
--    Verify: For sql-30 Exercise 3, confirm no row has `active_customers > cohort_size` and that the 2022-11-01 cohort shows sizes of 10 with 2, 1, and 2 active customers at offsets 3, 4, and 5; then, inside `BEGIN ... ROLLBACK`, insert a customer with no orders and confirm the row count stays 1060, because the inner join to `activity` hides cohorts with no orders.
--    Hint ladder, rung 1: For sql-30 Exercise 3, run `cohorts`, `cohort_sizes`, and `activity` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 4. [Prediction] Create a dense cohort/offset spine from offset 0 through 12 and show missing activity as zero.
--    Hint: Cross join cohort months with generate_series, then left join observed activity at the same offset grain.
--    Inputs: For sql-30 Exercise 4, read `customers` for cohort sizes and `orders` for active customers per cohort and `month_offset`, build a `spine` by crossing every cohort with `generate_series(0, 12)`, and `LEFT JOIN` the activity onto it with `COALESCE(..., 0)`.
--    Expected result/shape: For sql-30 Exercise 4, expected output: exactly 13 rows per cohort, 624 rows for the 48 cohorts on this load, of which 137 carry a zero-filled `active_customers`; cohort 2022-11-01 shows 0, 0, 0 at offsets 0 to 2 and then 2 at offset 3. The final columns are `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`. The final order is `s.cohort_month, s.month_offset`.
--    Verify: For sql-30 Exercise 4, confirm `COUNT(*) = 13 * COUNT(DISTINCT cohort_month)` and that the 487 nonzero rows match the offset 0 to 12 rows of Exercise 3; then, inside `BEGIN ... ROLLBACK`, insert a customer with no orders and confirm 637 rows, 150 of them zero, and 49 cohorts, because the spine keeps the new cohort that the inner join in Exercise 3 dropped.
--    Hint ladder, rung 1: For sql-30 Exercise 4, run `cohorts`, `cohort_sizes`, `activity`, and `spine` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 5. [Debugging] Calculate revenue per active customer and a trailing three-observation annualized teaching projection.
--    Hint: Compute stable cohort metrics before applying the window; disclose that observed rows may have month gaps.
--    Inputs: For sql-30 Exercise 5, read `orders` and `order_items` for net order values, read `customers` for cohorts, then aggregate active customers and revenue per cohort and order month in `metrics`, divide them in `per_active` with `NULLIF`, and average the last three `revenue_per_active` values per cohort with a `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` frame.
--    Expected result/shape: For sql-30 Exercise 5, expected output: 487 rows on this load, all with `month_offset` from 0 to 12 and no NULL `revenue_per_active`; the first cohort's rows show `revenue_per_active` 601.63, 656.19, 660.47, and 76.67, with `illustrative_annualized_clv` 7219.56, 7546.92, 7673.15, and 5573.32. The final columns are `cohort_month`, `order_month`, `month_offset`, `active_customers`, `revenue`, `revenue_per_active`, and `illustrative_annualized_clv`. The final order is `cohort_month, month_offset`.
--    Verify: For sql-30 Exercise 5, confirm the first cohort by hand: 601.63 times 12 is 7219.56 for its first row, the second row averages two values, and the fourth row, 5573.32, drops the first value because the frame holds only three rows; also confirm that the first row of the next cohort equals its own `revenue_per_active` times 12, which shows the frame resets at each `cohort_month`.
--    Hint ladder, rung 1: For sql-30 Exercise 5, run `order_values`, `cohorts`, `metrics`, and `per_active` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 6. [Extension] Audit cohort constraints and reconcile cohort revenue to net line revenue for offsets 0-12.
--    Hint: Calculate violations and compare totals at the same scoped population.
--    Inputs: For sql-30 Exercise 6, read `orders`, `order_items`, and `customers` to rebuild `order_values`, `cohorts`, `cohort_sizes`, and `metrics`, keep offsets 0 to 12 in `scoped`, then count rows where active customers exceed the cohort size and compare their revenue with a subquery that sums `order_values` directly for the same offsets.
--    Expected result/shape: For sql-30 Exercise 6, expected output: exactly one row: 0 violations, `cohort_revenue` 1410578.66, `independent_revenue` 1410578.66, and `revenue_difference` 0.00 on this load. The final columns are `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference`.
--    Verify: For sql-30 Exercise 6, confirm that the 1410578.66 is less than the full net revenue of 2355647.12 because orders after offset 12 are left out on purpose; then change `COUNT(DISTINCT ov.customer_id)` to `COUNT(*)` in `metrics` and confirm the audit reports 37 violations, because counting orders instead of customers lets activity exceed cohort size.
--    Hint ladder, rung 1: For sql-30 Exercise 6, run `order_values`, `cohorts`, `cohort_sizes`, `metrics`, and `scoped` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
ROLLBACK;
