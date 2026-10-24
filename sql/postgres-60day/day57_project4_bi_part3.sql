-- Day 57: Project 4 - Complex BI (Part 3)
-- BEGINNER WORKFLOW — sql-57: Project4 BI Part3
-- Guide: sql/postgres-60day/companion-guides/day57_project4_bi_part3.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-57/ copy, and prints the full
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
-- Trend analysis, anomaly detection, and forecast accuracy
BEGIN;
SET search_path TO training, public;

-- Daily revenue baseline
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), stats AS (
  -- Rolling 14-day window to compute z-score style anomaly score
  SELECT d,
         revenue,
         AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS avg14,
         STDDEV_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS sd14
  FROM daily
)
SELECT d,
       ROUND(revenue,2) AS revenue,
       ROUND(avg14,2)   AS rolling_avg14,
       ROUND(sd14,2)    AS rolling_sd14,
       CASE WHEN sd14 IS NULL OR sd14 = 0 THEN 0 ELSE ROUND((revenue - avg14)/sd14, 2) END AS z_score,
       CASE WHEN sd14 IS NOT NULL AND sd14 > 0 AND ABS((revenue-avg14)/sd14) >= 3 THEN 'anomaly' ELSE 'normal' END AS flag
FROM stats
ORDER BY d DESC
LIMIT 60;

-- MAD-based anomaly (more robust to outliers)
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), med AS (
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY revenue) AS median_rev FROM daily
), dev AS (
  SELECT d.revenue, d.d,
         ABS(d.revenue - m.median_rev) AS abs_dev,
         m.median_rev
  FROM daily d CROSS JOIN med m
), mad AS (
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY abs_dev) AS mad
  FROM dev
)
SELECT dev.d,
       ROUND(dev.revenue, 2) AS revenue,
       ROUND(dev.median_rev::numeric, 2) AS median_rev,
       CASE
         WHEN mad.mad = 0 THEN 0
         ELSE ROUND(
           (0.6745 * (dev.revenue - dev.median_rev) / mad.mad)::numeric,
           2
         )
       END AS modified_z,
       CASE
         WHEN mad.mad > 0
          AND ABS(0.6745 * (dev.revenue - dev.median_rev) / mad.mad) >= 3.5
         THEN 'anomaly'
         ELSE 'normal'
       END AS flag
FROM dev
CROSS JOIN mad
ORDER BY dev.d DESC
LIMIT 60;

-- Forecast accuracy: compare MA(7) forecast to actual; compute MAPE for last 30 days
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), f AS (
  SELECT d,
         revenue,
         AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS ma7
  FROM daily
)
SELECT d,
       ROUND(revenue,2) AS actual,
       ROUND(ma7,2) AS forecast,
       CASE WHEN revenue IS NULL OR revenue = 0 OR ma7 IS NULL THEN NULL
            ELSE ROUND(ABS(revenue - ma7)/revenue, 4) END AS ape
FROM f
ORDER BY d DESC
LIMIT 30;

-- Exercises
-- 1. Replace MA(7) with seasonal naive (value from 7 days ago) and compare MAPE.
--    Inputs: For sql-57 Exercise 1, read `orders` into a one-row-per-day calendar spine, calculate `ma7_forecast` and `seasonal_naive` in `forecasts`, and aggregate the final `model` and `mape`; the output grain is model, not order.
--    Expected result/shape: For sql-57 Exercise 1, expected output: two model rows. Zero-revenue days are excluded from MAPE by `NULLIF`; disclose that choice. The final columns are `model`, and `mape`. The final order is `model`.
--    Verify: For sql-57 Exercise 1, require exactly two rows with model values `MA(7)` and `seasonal naive (lag 7)` and require unique `model`. From the same `forecasts` rows and 180-day evaluation window, independently recompute each model's absolute percentage-error numerator and eligible denominator, compare the resulting `mape`, and disclose that zero-revenue days and NULL forecasts are excluded.
--    Hint ladder, rung 1: For sql-57 Exercise 1, run `bounds`, `calendar`, `daily`, `complete`, and `forecasts` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 2. Flag top-10 positive and negative anomalies in the last 6 months with both SD and MAD methods.
--    Inputs: For sql-57 Exercise 2, read from `orders`. Build the answer toward `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z`; keep `day` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-57 Exercise 2, expected output: up to ten positive and ten negative rows. The combined absolute score is a ranking heuristic; it is not a calibrated probability. The final columns are `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z`. The final order is `direction DESC, anomaly_rank`.
--    Verify: For sql-57 Exercise 2, project `day` plus the raw source columns from `orders` at each join stage; record row count and distinct `day`, then assert the final `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z` values match those staged rows without unintended fanout or loss. Give two rows the same `direction DESC` value and different `anomaly_rank` values; verify `direction DESC, anomaly_rank` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-57 Exercise 2, run `daily`, `moments`, `median`, `deviations`, `mad`, `scored`, and `ranked` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
-- 3. Prediction: remove the calendar spine and explain why LAG(revenue, 7) now
--    means seven observed rows rather than seven calendar days.
--    Inputs: For sql-57 Exercise 3, read from `orders`. Build the answer toward `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7`; keep `day` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-57 Exercise 3, expected output: at most 30 rows keyed by `day`. The final columns are `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7`. The final order is `c.day DESC`.
--    Verify: For sql-57 Exercise 3, assert no more than 30 rows, no duplicate `day`, and no adjacent pair that violates `c.day DESC`. Rejoin the returned keys to `orders` to confirm `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7` came from the same source rows. Run with 30 minus one and 30 plus one eligible rows; require the output cap of 30 while retaining `c.day DESC`.
--    Hint ladder, rung 1: For sql-57 Exercise 3, run `bounds`, `observed_daily`, `observed_lag`, `calendar_daily`, and `calendar_lag` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
-- 4. Construction: calculate MAE, RMSE, MAPE, and the number of scored rows for
--    both models over one identical evaluation window.
--    Inputs: For sql-57 Exercise 4, derive `common_scoring_rows` from `orders`, reshape both forecasts to `model_name` rows, and build `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows`; keep `model_name` as the final grouping key.
--    Expected result/shape: For sql-57 Exercise 4, expected output: one row per `model_name`. The final columns are `model_name`, `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows`. The final order is `model_name`.
--    Verify: For sql-57 Exercise 4, independently aggregate `common_scoring_rows` by `model_name` and require exactly two unique `model_name` rows. Require both models to have the same `scored_rows` and `zero_actual_rows` because they share one evaluation population; recompute `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows` for each model and compare every value, preserving NULL `mape` when the eligible percentage-error denominator is zero.
--    Hint ladder, rung 1: For sql-57 Exercise 4, run `bounds`, `daily`, `calendar_daily`, `forecasts`, and `common_scoring_rows` one at a time. Record each CTE's row count and `model_name` uniqueness before the next stage uses it.
-- 5. Debugging: repair a backtest whose moving-average frame includes CURRENT
--    ROW, and prove the corrected forecast uses no information from the target day.
--    Inputs: For sql-57 Exercise 5, read from `orders`. Build the answer toward `day`, `revenue`, `leaky_window`, and `forecast_window`; keep `day` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-57 Exercise 5, expected output: at most 20 rows keyed by `day`. The final columns are `day`, `revenue`, `leaky_window`, and `forecast_window`. The final order is `day DESC`.
--    Verify: For sql-57 Exercise 5, assert no more than 20 rows, no duplicate `day`, and no adjacent pair that violates `day DESC`. Rejoin the returned keys to `orders` to confirm `day`, `revenue`, `leaky_window`, and `forecast_window` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `day DESC`.
--    Hint ladder, rung 1: For sql-57 Exercise 5, run `daily` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
-- 6. Edge case: create a constant-valued test series and preserve NULL SD/MAD
--    scores when dispersion is zero; do not silently label them normal.
--    Inputs: For sql-57 Exercise 6, read from `constant`. Build the answer toward `day`, `revenue`, `sd_z`, and `modified_mad_z`; keep `day` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-57 Exercise 6, expected output: one row per `day`. The final columns are `day`, `revenue`, `sd_z`, and `modified_mad_z`. The final order is `d.day`.
--    Verify: For sql-57 Exercise 6, project `day` plus the raw source columns from `constant` at each join stage; record row count and distinct `day`, then assert the final `day`, `revenue`, `sd_z`, and `modified_mad_z` values match those staged rows without unintended fanout or loss. Add one source row with a new `day`; verify the result gains exactly one row carrying that `day` value.
--    Hint ladder, rung 1: For sql-57 Exercise 6, run `center`, `deviations`, and `dispersion` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.

ROLLBACK;
