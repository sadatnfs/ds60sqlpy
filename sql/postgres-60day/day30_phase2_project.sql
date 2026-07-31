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
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 2. [Query writing] Calculate active customers and net line revenue for each cohort/order month.
--    Hint: Aggregate line items to order grain before cohort joins, then count distinct active customers.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 3. [Query writing] Calculate cohort month offset and retention using original cohort size.
--    Hint: Use year-plus-month age components and guard the denominator.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 4. [Prediction] Create a dense cohort/offset spine from offset 0 through 12 and show missing activity as zero.
--    Hint: Cross join cohort months with generate_series, then left join observed activity at the same offset grain.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
-- 5. [Debugging] Calculate revenue per active customer and a trailing three-observation annualized teaching projection.
--    Hint: Compute stable cohort metrics before applying the window; disclose that observed rows may have month gaps.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
-- 6. [Extension] Audit cohort constraints and reconcile cohort revenue to net line revenue for offsets 0–12.
--    Hint: Calculate violations and compare totals at the same scoped population.
--    Inputs: Use only the declared lesson objects (orders, order_items, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.

ROLLBACK;
