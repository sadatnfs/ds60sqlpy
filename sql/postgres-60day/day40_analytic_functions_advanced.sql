-- Day 40: Analytic Functions - Advanced (statistics and distributions)
-- BEGINNER WORKFLOW — sql-40: Analytic Functions Advanced
-- Guide: sql/postgres-60day/companion-guides/day40_analytic_functions_advanced.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-40/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Statistical aggregates over windows
WITH daily AS (
  SELECT date_trunc('day', o.order_date) AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT d,
       revenue,
       ROUND(AVG(revenue)  OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW),2) AS ma15,
       ROUND(STDDEV_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW),2) AS sd15,
       ROUND(VAR_POP(revenue)      OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW),2) AS var15
FROM daily
ORDER BY d DESC
LIMIT 60;

-- Percentiles using PERCENTILE_CONT (continuous) within month
WITH monthly AS (
  SELECT date_trunc('month', o.order_date) AS m,
         o.total_amount AS amt
  FROM orders o
)
SELECT m,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amt) AS p50,
       PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY amt) AS p90,
       PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM monthly
GROUP BY m
ORDER BY m DESC
LIMIT 12;

-- Ratio to total (ratio_to_report equivalent)
WITH cat AS (
  SELECT p.category, SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM order_items oi JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category
)
SELECT category,
       ROUND(revenue,2) AS revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (),0), 4) AS share_of_total
FROM cat
ORDER BY revenue DESC;

-- Exercises
-- 1. Compute z-score for daily revenue: (rev - avg15)/sd15.
--    Inputs: Use only the declared lesson objects (orders, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. For each category, compute P50 and P90 of order totals.
--    Inputs: Use only the declared lesson objects (orders, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Prediction: compare percentile_disc(0.5) with percentile_cont(0.5) for
--    the values (10, 20, 100, 200). Predict both medians before running.
--    Inputs: Use only the declared lesson objects (orders, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: calculate each category's revenue share within its month,
--    with a deterministic rank for equal revenue.
--    Inputs: Use only the declared lesson objects (orders, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: repair a rolling average that includes the current row when the
--    intended forecast must use only prior observations.
--    Inputs: Use only the declared lesson objects (orders, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: compute a z-score for a constant three-row series and preserve
--    NULL when standard deviation is zero.
--    Inputs: Use only the declared lesson objects (orders, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
