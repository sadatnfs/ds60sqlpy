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
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 requires a written prediction and the observed result for “Compare MA(7) with calendar-week seasonal naive using MAPE”. Show both compared result shapes at one row per requested calendar/cohort bucket and grouping key, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `day`, `revenue`, `ma7_forecast`, `seasonal_naive`, `model`, `mape`, `ma`.
--    Verify: For Exercise 1, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.
-- 2. Flag top-10 positive and negative anomalies in the last 6 months with both SD and MAD methods.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 returns a table-shaped answer to “Rank positive/negative anomalies with SD and MAD scores” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `absolute_deviation`, `mad`, `sd_z`, `modified_z`, `direction`, `anomaly_rank`, `sd`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 2, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.
-- 3. Prediction: remove the calendar spine and explain why LAG(revenue, 7) now
--    means seven observed rows rather than seven calendar days.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 requires a written prediction and the observed result for “Predict how removing the date spine changes LAG(..., 7)”. Show both compared result shapes at one row per requested calendar/cohort bucket and grouping key, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `max_day`, `day`, `revenue`, `observed_row_lag7`, `calendar`, `calendar_day_lag7`, `lag`.
--    Verify: For Exercise 3, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.
-- 4. Construction: calculate MAE, RMSE, MAPE, and the number of scored rows for
--    both models over one identical evaluation window.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Compare MAE, RMSE, MAPE, and scored-row counts on one window”. Show both compared result shapes at one summary row per grouping key explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `error`, `model`, `scored_rows`, `mae`, `rmse`, `mape`, `zero_actual_rows`.
--    Verify: For Exercise 4, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.
-- 5. Debugging: repair a backtest whose moving-average frame includes CURRENT
--    ROW, and prove the corrected forecast uses no information from the target day.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 returns a table-shaped answer to “Detect and remove current-row forecast leakage” at one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `day`, `revenue`, `leaky_window`, `forecast_window`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 5, prove uniqueness at one row per requested calendar/cohort bucket and grouping key; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.
-- 6. Edge case: create a constant-valued test series and preserve NULL SD/MAD
--    scores when dispersion is zero; do not silently label them normal.
--    Inputs: Use `orders` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 requires a written prediction and the observed result for “Preserve undefined scores for a constant series. Compare absent no-order days with explicit zero-revenue days”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `median_revenue`, `mean_revenue`, `sd_revenue`, `absolute_deviation`, `mad`, `sd_z`, `modified_mad_z`.
--    Verify: For Exercise 6, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.

ROLLBACK;
