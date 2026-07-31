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
--    Inputs: For sql-40 Exercise 1, read from `orders`. Compute `order_day`, `revenue`, `avg15`, `sd15`, and `z_score` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-40 Exercise 1, expected output: one row per day with orders. A positive z-score is above the rolling mean; a negative score is below it. The final columns are `order_day`, `revenue`, `avg15`, `sd15`, and `z_score`. The final order is `order_day`.
--    Verify: For sql-40 Exercise 1, evaluate each of `order_day`, `revenue`, `sd15`, and `z_score` in a separate control `SELECT` over `orders`; require one final row and compare every value. Add one source row with a new `day`; verify the result gains exactly one row carrying that `day` value.
--    Hint ladder, rung 1: For sql-40 Exercise 1, run `daily`, and `rolling` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
-- 2. For each category, compute P50 and P90 of order totals.
--    Inputs: For sql-40 Exercise 2, read from `order_items`, and `products`. Compute `category`, `p50_order_value`, `p90_order_value`, and `category_orders` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-40 Exercise 2, expected output: one row per sold category. `PERCENTILE_CONT` can interpolate between observed values, so a percentile need not equal an actual order value. The final columns are `category`, `p50_order_value`, `p90_order_value`, and `category_orders`. The final order is `category`.
--    Verify: For sql-40 Exercise 2, evaluate each of `p50_order_value`, `p90_order_value`, and `category_orders` in a separate control `SELECT` over `order_items`, and `products`; require one final row and compare every value. Add one row to an existing group and one row for a new group; recompute `p50_order_value`, `p90_order_value`, and `category_orders` for the existing `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-40 Exercise 2, run `category_order_values` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 3. Prediction: compare percentile_disc(0.5) with percentile_cont(0.5) for
--    the values (10, 20, 100, 200). Predict both medians before running.
--    Inputs: For sql-40 Exercise 3, read from the inline `VALUES` fixture. Build the answer toward `discrete_median`, and `continuous_median`; keep `discrete_median` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-40 Exercise 3, expected output: one row per `discrete_median`. The final columns are `discrete_median`, and `continuous_median`.
--    Verify: For sql-40 Exercise 3, reselect the returned keys directly from the source; require unique `discrete_median` where the expected grain is one row per key and confirm the projected `discrete_median`, and `continuous_median` against the inline `VALUES` fixture. Add one source row with a new `discrete_median`; verify the result gains exactly one row carrying that `discrete_median` value.
--    Hint ladder, rung 1: For sql-40 Exercise 3, select `discrete_median` from the inline `VALUES` fixture before adding derived columns.
-- 4. Construction: calculate each category's revenue share within its month,
--    with a deterministic rank for equal revenue.
--    Inputs: For sql-40 Exercise 4, read from `orders`, `order_items`, and `products`. Build the answer toward `month`, `category`, `revenue`, `month_share`, and `category_rank`; keep `month`, and `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-40 Exercise 4, expected output: one row per `month`, and `category`. The final columns are `month`, `category`, `revenue`, `month_share`, and `category_rank`. The final order is `month DESC, category_rank`.
--    Verify: For sql-40 Exercise 4, choose one complete partition from `orders`, `order_items`, and `products`; hand-calculate its first, middle, and final window values for `revenue`, `month_share`, and `category_rank`, then verify output keys remain `month`, and `category`. Give two rows the same `month DESC` value and different `category_rank` values; verify `month DESC, category_rank` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-40 Exercise 4, run `category_month` one at a time. Record each CTE's row count and `month`, and `category` uniqueness before the next stage uses it.
-- 5. Debugging: repair a rolling average that includes the current row when the
--    intended forecast must use only prior observations.
--    Inputs: For sql-40 Exercise 5, read from `orders`. Build the answer toward `day`, `revenue`, and `prior_seven_forecast`; keep `day` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-40 Exercise 5, expected output: at most 20 rows keyed by `day`. The final columns are `day`, `revenue`, and `prior_seven_forecast`. The final order is `day DESC`.
--    Verify: For sql-40 Exercise 5, assert no more than 20 rows, no duplicate `day`, and no adjacent pair that violates `day DESC`. Rejoin the returned keys to `orders` to confirm `day`, `revenue`, and `prior_seven_forecast` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `day DESC`.
--    Hint ladder, rung 1: For sql-40 Exercise 5, run `daily` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
-- 6. Edge case: compute a z-score for a constant three-row series and preserve
--    NULL when standard deviation is zero.
--    Inputs: For sql-40 Exercise 6, read from `constant`. Build the answer toward `value`, and `z_score`; keep `value` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-40 Exercise 6, expected output: one row per `value`. The final columns are `value`, and `z_score`.
--    Verify: For sql-40 Exercise 6, reselect the returned keys directly from the source; require unique `value` where the expected grain is one row per key and confirm the projected `value`, and `z_score` against `constant`. Repeat with `NULL` in `value`, and `z_score` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-40 Exercise 6, run `moments` one at a time. Record each CTE's row count and `value` uniqueness before the next stage uses it.

ROLLBACK;
