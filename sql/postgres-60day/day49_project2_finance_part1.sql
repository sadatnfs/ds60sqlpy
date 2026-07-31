-- Day 49: Project 2 - Financial/Operational Analysis (Part 1)
-- BEGINNER WORKFLOW — sql-49: Project2 Finance Part1
-- Guide: sql/postgres-60day/companion-guides/day49_project2_finance_part1.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-49/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Revenue forecasting with time-series patterns
BEGIN;
SET search_path TO training, public;

-- Monthly revenue
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT * FROM monthly ORDER BY month DESC LIMIT 24;

-- YoY growth per month
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT m.month,
       m.revenue,
       LAG(m.revenue, 12) OVER (ORDER BY m.month) AS prev_year,
       ROUND((m.revenue - COALESCE(LAG(m.revenue,12) OVER (ORDER BY m.month),0))
             / NULLIF(LAG(m.revenue,12) OVER (ORDER BY m.month),0), 4) AS yoy_growth
FROM monthly m
ORDER BY m.month DESC
LIMIT 36;

-- Naive seasonal forecast: use last year's month as forecast
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), future AS (
  SELECT (date_trunc('month', CURRENT_DATE) + (n || ' month')::interval)::date AS month
  FROM generate_series(1, 3) AS g(n)
)
SELECT f.month,
       m_prev.revenue AS forecast_revenue
FROM future f
LEFT JOIN monthly m_prev ON m_prev.month = (f.month - interval '12 months')::date
ORDER BY f.month;

-- MA(3) forecast: average of last 3 months revenue
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), ma AS (
  SELECT month,
         revenue,
         ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),2) AS ma3
  FROM monthly
)
SELECT * FROM ma ORDER BY month DESC LIMIT 6;

-- Exercises
-- 1. Build MA(6) and MA(12) and compare MAPEs vs seasonal naive.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 2. Produce a combined forecast blending 50% seasonal-naive and 50% MA(6).
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Prediction: explain why evaluating a moving average on the same rows used
--    to calculate it leaks the current actual and understates error.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: create a complete monthly spine before LAG(..., 12), then
--    distinguish a missing month from a true zero-revenue month.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 5. Debugging: repair MAPE when actual revenue is zero and report how many
--    observations were excluded from the percentage error.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: compare MAE and MAPE when one low-revenue month has a modest
--    absolute miss but a very large percentage miss.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
