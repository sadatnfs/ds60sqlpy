-- Day 30: Phase 2 Project - Multi-stage Analysis
-- BEGINNER WORKFLOW — sql-30: Phase2 Project
-- Guide: sql/postgres-60day/companion-guides/day30_phase2_project.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-30/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
  SELECT o.order_id,
         o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
           AS order_month_utc,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id,
           o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date
           AS cohort_month_utc
  FROM customers c
), cohort_sizes AS (
  -- The denominator includes customers who never place an order.
  SELECT cohort_month_utc,
         COUNT(*) AS original_customers
  FROM cohorts
  GROUP BY cohort_month_utc
), metrics AS (
  SELECT e.customer_id,
         c.cohort_month_utc,
         e.order_month_utc,
         SUM(e.order_value) AS revenue
  FROM orders_enriched e
  JOIN cohorts c ON c.customer_id = e.customer_id
  GROUP BY e.customer_id, c.cohort_month_utc, e.order_month_utc
), cohort_agg AS (
  SELECT cohort_month_utc,
         order_month_utc,
         (
           EXTRACT(YEAR FROM age(order_month_utc, cohort_month_utc)) * 12
           + EXTRACT(MONTH FROM age(order_month_utc, cohort_month_utc))
         )::int AS month_offset,
         SUM(revenue) AS cohort_revenue,
         COUNT(DISTINCT customer_id) AS active_customers
  FROM metrics
  GROUP BY cohort_month_utc, order_month_utc
)
-- This first pass contains observed activity months only. Exercise 4 creates
-- a dense offset spine so a missing month becomes an explicit zero.
SELECT agg.cohort_month_utc,
       agg.month_offset,
       sizes.original_customers,
       agg.active_customers,
       ROUND(
         agg.active_customers::numeric
         / NULLIF(sizes.original_customers, 0),
         4
       ) AS retention_rate,
       ROUND(agg.cohort_revenue, 2) AS revenue,
       ROUND(
         agg.cohort_revenue / NULLIF(agg.active_customers, 0),
         2
       ) AS revenue_per_active
FROM cohort_agg AS agg
JOIN cohort_sizes AS sizes
  ON sizes.cohort_month_utc = agg.cohort_month_utc
ORDER BY agg.cohort_month_utc DESC, agg.month_offset
LIMIT 200;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate original customer count for each UTC signup cohort month.
--    Hint: Build the denominator from customers, including customers who never order.
--    Inputs: For sql-30 Exercise 1, read from `customers`. Build the answer toward `cohort_month`, and `cohort_size`; keep `cohort_month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-30 Exercise 1, expected output: One row per cohort month. The final columns are `cohort_month`, and `cohort_size`. The final order is `cohort_month`.
--    Verify: For sql-30 Exercise 1, independently aggregate `customers` by `cohort_month`; require one output row for every distinct `cohort_month` tuple and compare `cohort_size` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `cohort_size` for the existing `cohort_month` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-30 Exercise 1, run `cohorts` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 2. [Query writing] Calculate active customers and net line revenue for each cohort/order month.
--    Hint: Aggregate line items to order grain before cohort joins, then count distinct active customers.
--    Inputs: For sql-30 Exercise 2, read from `orders`, `order_items`, and `customers`. Build the answer toward `cohort_month`, `order_month`, `active_customers`, and `net_revenue`; keep `cohort_month`, and `order_month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-30 Exercise 2, expected output: One row per observed cohort/order month. The final columns are `cohort_month`, `order_month`, `active_customers`, and `net_revenue`. The final order is `c.cohort_month, ov.order_month`.
--    Verify: For sql-30 Exercise 2, independently aggregate `orders`, `order_items`, and `customers` by `cohort_month`, and `order_month`; require one output row for every distinct `cohort_month`, and `order_month` tuple and compare `order_month`, `active_customers`, and `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `active_customers`, and `net_revenue` for the existing `cohort_month`, and `order_month` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-30 Exercise 2, run `order_values`, and `cohorts` one at a time. Record each CTE's row count and `cohort_month`, and `order_month` uniqueness before the next stage uses it.
-- 3. [Query writing] Calculate cohort month offset and retention using original cohort size.
--    Hint: Use year-plus-month age components and guard the denominator.
--    Inputs: For sql-30 Exercise 3, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`; keep `cohort_month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-30 Exercise 3, expected output: Observed cohort/offset rows with retention from 0 to 1. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`. The final order is `a.cohort_month, month_offset`.
--    Verify: For sql-30 Exercise 3, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate` values match those staged rows without unintended fanout or loss. Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.
--    Hint ladder, rung 1: For sql-30 Exercise 3, run `cohorts`, `cohort_sizes`, and `activity` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 4. [Prediction] Create a dense cohort/offset spine from offset 0 through 12 and show missing activity as zero.
--    Hint: Cross join cohort months with generate_series, then left join observed activity at the same offset grain.
--    Inputs: For sql-30 Exercise 4, read from `customers`, `orders`, and `generate_series`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`; keep `cohort_month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-30 Exercise 4, expected output: Thirteen rows per cohort. The final columns are `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`. The final order is `s.cohort_month, s.month_offset`.
--    Verify: For sql-30 Exercise 4, project `cohort_month` plus the raw source columns from `customers`, `orders`, and `generate_series` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, and `active_customers` values match those staged rows without unintended fanout or loss. Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.
--    Hint ladder, rung 1: For sql-30 Exercise 4, run `cohorts`, `cohort_sizes`, `activity`, and `spine` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 5. [Debugging] Calculate revenue per active customer and a trailing three-observation annualized teaching projection.
--    Hint: Compute stable cohort metrics before applying the window; disclose that observed rows may have month gaps.
--    Inputs: For sql-30 Exercise 5, read from `orders`, `order_items`, and `customers`. Build the answer toward `cohort_month`, `order_month`, `month_offset`, `active_customers`, `revenue`, `revenue_per_active`, and `illustrative_annualized_clv`; keep `cohort_month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-30 Exercise 5, expected output: One row per observed cohort/month with nullable guarded measures. The final columns are `cohort_month`, `order_month`, `month_offset`, `active_customers`, `revenue`, `revenue_per_active`, and `illustrative_annualized_clv`. The final order is `cohort_month, month_offset`.
--    Verify: For sql-30 Exercise 5, choose one complete partition from `orders`, `order_items`, and `customers`; hand-calculate its first, middle, and final window values for `order_month`, `active_customers`, `revenue`, and `revenue_per_active`, then verify output keys remain `cohort_month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-30 Exercise 5, run `order_values`, `cohorts`, `metrics`, and `per_active` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 6. [Extension] Audit cohort constraints and reconcile cohort revenue to net line revenue for offsets 0–12.
--    Hint: Calculate violations and compare totals at the same scoped population.
--    Inputs: For sql-30 Exercise 6, read from `orders`, `order_items`, and `customers`. Build the answer toward `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-30 Exercise 6, expected output: One row with zero retention violations and zero revenue difference. The final columns are `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference`.
--    Verify: For sql-30 Exercise 6, project `order_id` plus the raw source columns from `orders`, `order_items`, and `customers` at each join stage; record row count and distinct `order_id`, then assert the final `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-30 Exercise 6, run `order_values`, `cohorts`, `cohort_sizes`, `metrics`, and `scoped` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.

ROLLBACK;
