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
--    Inputs: For sql-49 Exercise 1, aggregate `orders` by observed month, left-join to `month_spine`, compute full-window history counts, and reshape four forecasts over `common_scoring_rows`.
--    Expected result/shape: For sql-49 Exercise 1, expected output: exactly four rows keyed by `model`, with `scored_rows`, `zero_actual_rows`, and `mape`, ordered by `model`.
--    Verify: For sql-49 Exercise 1, require `ma6_history_rows = 6`, `ma12_history_rows = 12`, and a non-NULL twelve-month seasonal value before any model is scored. All four models must have identical eligible months and equal `scored_rows`; independently recompute each MAPE.
--    Hint ladder, rung 1: Inspect `month_spine`, `monthly_complete`, `forecast_rows`, and `common_scoring_rows`; reject partial warm-up frames before reshaping models.
-- 2. Produce a combined forecast blending 50% seasonal-naive and 50% MA(6).
--    Inputs: For sql-49 Exercise 2, read from `orders`. Build the answer toward `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-49 Exercise 2, expected output: one row per `month`. The final columns are `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast`. The final order is `month DESC`.
--    Verify: For sql-49 Exercise 2, run an anti-check that counts rows where NOT ((seasonal_naive IS NOT NULL)); require unique `month` where the expected grain is one row per key and confirm the projected `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast` against `orders`. Add one row for which `(seasonal_naive IS NOT NULL)` is true and one for which it is false; verify only the matching `month` value is returned.
--    Hint ladder, rung 1: For sql-49 Exercise 2, run `monthly`, and `forecasted` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 3. Prediction: explain why evaluating a moving average on the same rows used
--    to calculate it leaks the current actual and understates error.
--    Inputs: For sql-49 Exercise 3, read from `orders`. Build the answer toward `month`, `revenue`, `leaky_ma6`, and `honest_ma6`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-49 Exercise 3, expected output: one row per `month`. The final columns are `month`, `revenue`, `leaky_ma6`, and `honest_ma6`. The final order is `month`.
--    Verify: For sql-49 Exercise 3, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `revenue`, `leaky_ma6`, and `honest_ma6`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-49 Exercise 3, run `monthly` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 4. Construction: create a complete monthly spine before LAG(..., 12), then
--    distinguish a missing month from a true zero-revenue month.
--    Inputs: For sql-49 Exercise 4, read from `orders`. Build the answer toward `month`, `revenue`, `had_source_rows`, and `seasonal_forecast`; keep `month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-49 Exercise 4, expected output: one row per calendar month before the 12-row lag. The final columns are `month`, `revenue`, `had_source_rows`, and `seasonal_forecast`. The final order is `month`.
--    Verify: For sql-49 Exercise 4, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `revenue`, and `had_source_rows`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
--    Hint ladder, rung 1: For sql-49 Exercise 4, run `bounds`, `spine`, `actual`, and `complete` one at a time. Record each CTE's row count and `month` uniqueness before the next stage uses it.
-- 5. Debugging: repair MAPE when actual revenue is zero and report how many
--    observations were excluded from the percentage error.
--    Inputs: For sql-49 Exercise 5, read from `toy`. Build the answer toward `mape`, `scored_rows`, and `excluded_zero_actuals`; keep `mape` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-49 Exercise 5, expected output: one row per `mape`. The final columns are `mape`, `scored_rows`, and `excluded_zero_actuals`.
--    Verify: For sql-49 Exercise 5, reselect the returned keys directly from the source; require unique `mape` where the expected grain is one row per key and confirm the projected `mape`, `scored_rows`, and `excluded_zero_actuals` against `toy`. Add one source row with a new `mape`; verify the result gains exactly one row carrying that `mape` value.
--    Hint ladder, rung 1: For sql-49 Exercise 5, inspect the source keys that survive `WHERE`.
-- 6. Edge case: compare MAE and MAPE when one low-revenue month has a modest
--    absolute miss but a very large percentage miss.
--    Inputs: For sql-49 Exercise 6, read from `toy`. Build the answer toward `mae`, and `mape`; keep `mae` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-49 Exercise 6, expected output: one row per `mae`. The final columns are `mae`, and `mape`.
--    Verify: For sql-49 Exercise 6, reselect the returned keys directly from the source; require unique `mae` where the expected grain is one row per key and confirm the projected `mae`, and `mape` against `toy`. Add one source row with a new `mae`; verify the result gains exactly one row carrying that `mae` value.
--    Hint ladder, rung 1: For sql-49 Exercise 6, select `mae` from `toy` before adding derived columns.

ROLLBACK;
