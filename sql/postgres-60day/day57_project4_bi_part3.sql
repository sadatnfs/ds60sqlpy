-- Day 57: Project 4 - Complex BI (Part 3)
-- BEGINNER WORKFLOW - sql-57: Project 4 BI Part 3
-- Guide: sql/postgres-60day/companion-guides/day57_project4_bi_part3.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-57.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT
    date_trunc('day', o.order_date)::date AS d,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
),
stats AS (
  -- Rolling 14-day window to compute z-score style anomaly score
  SELECT
    d,
    revenue,
    AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS avg14,
    STDDEV_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS sd14
  FROM
    daily
)
SELECT
  d,
  ROUND(revenue, 2) AS revenue,
  ROUND(avg14, 2) AS rolling_avg14,
  ROUND(sd14, 2) AS rolling_sd14,
  CASE WHEN sd14 IS NULL
    OR sd14 = 0 THEN
    0
  ELSE
    ROUND((revenue - avg14) / sd14, 2)
  END AS z_score,
  CASE WHEN sd14 IS NOT NULL
    AND sd14 > 0
    AND ABS((revenue - avg14) / sd14) >= 3 THEN
    'anomaly'
  ELSE
    'normal'
  END AS flag
FROM
  stats
ORDER BY
  d DESC
LIMIT 60;

-- MAD-based anomaly (more robust to outliers)
WITH daily AS (
  SELECT
    date_trunc('day', o.order_date)::date AS d,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
),
med AS (
  SELECT
    percentile_cont(0.5) WITHIN GROUP (ORDER BY revenue) AS median_rev
  FROM
    daily
),
dev AS (
  SELECT
    d.revenue,
    d.d,
    ABS(d.revenue - m.median_rev) AS abs_dev,
    m.median_rev
  FROM
    daily d
    CROSS JOIN med m
),
mad AS (
  SELECT
    percentile_cont(0.5) WITHIN GROUP (ORDER BY abs_dev) AS mad
  FROM
    dev
)
SELECT
  dev.d,
  ROUND(dev.revenue, 2) AS revenue,
  ROUND(dev.median_rev::numeric, 2) AS median_rev,
  CASE WHEN mad.mad = 0 THEN
    0
  ELSE
    ROUND((0.6745 * (dev.revenue - dev.median_rev) / mad.mad)::numeric, 2)
  END AS modified_z,
  CASE WHEN mad.mad > 0
    AND ABS(0.6745 * (dev.revenue - dev.median_rev) / mad.mad) >= 3.5 THEN
    'anomaly'
  ELSE
    'normal'
  END AS flag
FROM
  dev
  CROSS JOIN mad
ORDER BY
  dev.d DESC
LIMIT 60;

-- Forecast accuracy: compare MA(7) forecast to actual; compute MAPE for last 30 days
WITH daily AS (
  SELECT
    date_trunc('day', o.order_date)::date AS d,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
),
f AS (
  SELECT
    d,
    revenue,
    AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS ma7
  FROM
    daily
)
SELECT
  d,
  ROUND(revenue, 2) AS actual,
  ROUND(ma7, 2) AS forecast,
  CASE WHEN revenue IS NULL
    OR revenue = 0
    OR ma7 IS NULL THEN
    NULL
  ELSE
    ROUND(ABS(revenue - ma7) / revenue, 4)
  END AS ape
FROM
  f
ORDER BY
  d DESC
LIMIT 30;

-- Exercises
-- 1. Replace MA(7) with seasonal naive (value from 7 days ago) and compare MAPE.
--    Inputs: For sql-57 Exercise 1, read `orders` into a one-row-per-day calendar spine, calculate `ma7_forecast` and `seasonal_naive` in `forecasts`, and aggregate the final `model` and `mape`; the output grain is model, not order.
--    Expected result/shape: For sql-57 Exercise 1, expected output: two model rows. Zero-revenue days are excluded from MAPE by `NULLIF`; disclose that choice. The final columns are `model` and `mape`. The final order is `model`.
--    Verify: For sql-57 Exercise 1, require exactly two rows with model values `MA(7)` and `seasonal naive (lag 7)` and require unique `model`. Count the `forecasts` rows with `day >= CURRENT_DATE - 180` and a non-NULL forecast for each model (the same 179 days from 2026-05-29 on a run dated 2026-11-25, none with revenue 0) and recompute each `mape` as the average of `ABS(revenue - forecast) / revenue` over them (0.4289 and 0.5329 on the checked load). Then replace `CURRENT_DATE` with `date '2027-06-01'`: no day qualifies, and both model rows still print with `mape` NULL.
--    Hint ladder, rung 1: For sql-57 Exercise 1, count `calendar` and `complete` (1,380 dates each, 299 of them with revenue 0 on the checked load) and `daily` (one row per order day), then filter `forecasts` to `day >= CURRENT_DATE - 180` and confirm both models keep the same days before you average them.
-- 2. Flag top-10 positive and negative anomalies in the last 6 months with both SD and MAD methods.
--    Inputs: For sql-57 Exercise 2, read the `orders` placed since `CURRENT_TIMESTAMP - interval '6 months'`, sum `total_amount` per order day in `daily`, take one mean, sample SD, median and MAD over those days, and score each day with `sd_z` and `modified_z`; `direction` records the day's side of the mean and `anomaly_rank` numbers the days within it.
--    Expected result/shape: For sql-57 Exercise 2, expected output: 20 rows, ten `positive` and ten `negative`, each side ranked 1 to 10 (a side with fewer than ten days would return fewer). The combined absolute score is a ranking heuristic; it is not a calibrated probability. The final columns are `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z`. The final order is `direction DESC, anomaly_rank`.
--    Verify: For sql-57 Exercise 2, confirm 20 rows and that `daily` holds 183 days (89 at or above the mean of 4,640.09 and 94 below on the checked load). Both scores are straight-line functions of revenue, so the `positive` list must equal the ten highest-revenue days and the `negative` list the ten lowest; check both with `ORDER BY revenue`. Then move the cutoff to `date_trunc('day', CURRENT_TIMESTAMP) - interval '6 months'`: the partial oldest day 2026-05-25 gets its full 3,758.33 instead of 1,446.62 and leaves the negative list.
--    Hint ladder, rung 1: For sql-57 Exercise 2, run `daily` first and confirm one row per order day (183 on the checked load); then run `moments`, `median`, and `mad`, which must each return exactly one row, before `scored` and `ranked` attach those values to every day.
-- 3. Prediction: remove the calendar spine and explain why LAG(revenue, 7) now
--    means seven observed rows rather than seven calendar days.
--    Inputs: For sql-57 Exercise 3, read `orders` twice: `observed_daily` sums revenue only for days that have orders, and `calendar_daily` left-joins those sums onto a `generate_series` spine from `bounds`, with 0 for empty days; apply `LAG(revenue, 7)` to each and join the two by `day`.
--    Expected result/shape: For sql-57 Exercise 3, expected output: 30 rows, one per calendar `day`, newest first. The final columns are `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7`. The final order is `c.day DESC`.
--    Verify: For sql-57 Exercise 3, confirm 30 rows from the last order day back (2026-11-23 to 2026-10-25 on the checked load) with `observed_row_lag7` equal to `calendar_day_lag7` on every row, because no recent day is empty. Remove `LIMIT 30` and count the rows where the lags are `IS DISTINCT FROM` each other: on the checked load 728 of the 1,380 dates, the last on 2025-12-13, made of 435 observed days whose seventh earlier row is not seven days back and 293 empty spine days whose `observed_row_lag7` is NULL.
--    Hint ladder, rung 1: For sql-57 Exercise 3, count `observed_daily` (1,081 rows on the checked load) and `calendar_daily` (1,380 rows, the extra 299 carrying revenue 0); that difference is the set of empty days the observed lag skips.
-- 4. Construction: calculate MAE, RMSE, MAPE, and the number of scored rows for
--    both models over one identical evaluation window.
--    Inputs: For sql-57 Exercise 4, derive `calendar_daily` (one row per date, 0 for days without orders) and `forecasts` from `orders`, keep the last 181 days on which both `ma7` and `seasonal_naive` exist, reshape the two forecasts with `LATERAL VALUES` into `common_scoring_rows` keyed by `day` and `model_name`, and build `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows` for each model.
--    Expected result/shape: For sql-57 Exercise 4, expected output: one row per `model_name`. That gives 2 rows, `MA(7)` and `seasonal naive`, each with 181 `scored_rows` and 0 `zero_actual_rows`; on the checked load MA(7) has MAE 1,340.94, RMSE 1,695.59, and MAPE 0.4284 against 1,715.92, 2,157.43, and 0.5349 for seasonal naive. The final columns are `model_name`, `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows`. The final order is `model_name`.
--    Verify: For sql-57 Exercise 4, group `common_scoring_rows` by `model_name` yourself: it holds 362 rows, 181 per model over the same dates, so `scored_rows` and `zero_actual_rows` must match between the models; recompute `mae` as `ROUND(AVG(ABS(error)), 2)`, `rmse` as `ROUND(SQRT(AVG(POWER(error, 2))), 2)`, and `mape` with `NULLIF(actual, 0)`, and compare every value. In a rolled-back transaction delete the orders of the day 30 days before the last order day (15 orders on 2026-10-24 on the checked load): both models keep 181 `scored_rows`, `zero_actual_rows` becomes 1, and `mape` now averages only the 180 nonzero days (0.4268 and 0.5400).
--    Hint ladder, rung 1: For sql-57 Exercise 4, count `calendar_daily` and `forecasts` (1,380 rows each, one per date) and then `common_scoring_rows` (362 rows: 181 days times two models) before grouping; `model_name` exists only after the `LATERAL VALUES` step.
-- 5. Debugging: repair a backtest whose moving-average frame includes CURRENT
--    ROW, and prove the corrected forecast uses no information from the target day.
--    Inputs: For sql-57 Exercise 5, read `orders`, sum `total_amount` per observed order day in `daily` (no calendar spine), and compute two seven-row averages over `ORDER BY day`: `leaky_window` ends at `CURRENT ROW` and `forecast_window` ends at `1 PRECEDING`.
--    Expected result/shape: For sql-57 Exercise 5, expected output: 20 rows, one per observed order `day`, newest first. The final columns are `day`, `revenue`, `leaky_window`, and `forecast_window`. The final order is `day DESC`.
--    Verify: For sql-57 Exercise 5, confirm 20 rows ending at the last order day (2026-11-23 back to 2026-11-04 on the checked load) and that every `leaky_window` equals the `forecast_window` printed one row above it; recompute the newest `forecast_window` as the plain average of the seven previous days' revenue (2,300.43 on the checked load). Then, in a rolled-back transaction, add 700 to the `total_amount` of the newest day's only order: its `leaky_window` rises by exactly 100, from 2,079.31 to 2,179.31, while its `forecast_window` stays 2,300.43.
--    Hint ladder, rung 1: For sql-57 Exercise 5, run `daily` alone and confirm one row per order day with no zero-revenue rows; then add the two `AVG` columns and compare their frames by hand on the newest three days.
-- 6. Edge case: create a constant-valued test series and preserve NULL SD/MAD
--    scores when dispersion is zero; do not silently label them normal.
--    Inputs: For sql-57 Exercise 6, read only the three-row `VALUES` fixture `constant` (revenue 100 on 2026-01-01, 2026-01-02 and 2026-01-03); `center` takes its median, mean and sample SD, `deviations` measures each day's distance from the median, and `dispersion` takes the MAD.
--    Expected result/shape: For sql-57 Exercise 6, expected output: three rows, one per fixture `day`, each with revenue 100 and both scores NULL. The final columns are `day`, `revenue`, `sd_z`, and `modified_mad_z`. The final order is `d.day`.
--    Verify: For sql-57 Exercise 6, confirm 3 rows with NULL `sd_z` and `modified_mad_z`, `center` showing SD 0 and `dispersion` showing MAD 0. Append `(date '2026-01-04', 101)`: `sd_z` becomes -0.5 for the three old days and 1.5 for the new one, while `modified_mad_z` stays NULL because three of the four deviations are 0. Make the values 100, 100, 101 and 101 and both scores are defined: `sd_z` is -0.8660 or 0.8660 and `modified_mad_z` -0.6745 or 0.6745.
--    Hint ladder, rung 1: For sql-57 Exercise 6, run `center` and `dispersion` on the fixture: each returns one row, with `sd_revenue` 0 and `mad` 0, and those zeros are what `NULLIF` turns into NULL denominators.
ROLLBACK;
