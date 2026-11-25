-- Day 49: Project 2 - Financial/Operational Analysis (Part 1)
-- BEGINNER WORKFLOW - sql-49: Project 2 Finance Part 1
-- Guide: sql/postgres-60day/companion-guides/day49_project2_finance_part1.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-49.
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
-- Revenue forecasting with time-series patterns
BEGIN;
SET search_path TO training, public;

-- Monthly revenue
WITH monthly AS (
  SELECT
    date_trunc('month', o.order_date)::date AS month,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
)
SELECT
  *
FROM
  monthly
ORDER BY
  month DESC
LIMIT 24;

-- YoY growth per month
WITH monthly AS (
  SELECT
    date_trunc('month', o.order_date)::date AS month,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
)
SELECT
  m.month,
  m.revenue,
  LAG(m.revenue, 12) OVER (ORDER BY m.month) AS prev_year,
  ROUND((m.revenue - COALESCE(LAG(m.revenue, 12) OVER (ORDER BY m.month), 0)) / NULLIF (LAG(m.revenue, 12) OVER (ORDER BY m.month), 0), 4) AS yoy_growth
FROM
  monthly m
ORDER BY
  m.month DESC
LIMIT 36;

-- Naive seasonal forecast: use last year's month as forecast
WITH monthly AS (
  SELECT
    date_trunc('month', o.order_date)::date AS month,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
),
future AS (
  SELECT
    (date_trunc('month', CURRENT_DATE) + (n || ' month')::interval)::date AS month
  FROM
    generate_series(1, 3) AS g (n))
SELECT
  f.month,
  m_prev.revenue AS forecast_revenue
FROM
  future f
  LEFT JOIN monthly m_prev ON m_prev.month = (f.month - interval '12 months')::date
ORDER BY
  f.month;

-- MA(3) forecast: average of last 3 months revenue
WITH monthly AS (
  SELECT
    date_trunc('month', o.order_date)::date AS month,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
),
ma AS (
  SELECT
    month,
    revenue,
    ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS ma3
  FROM
    monthly
)
SELECT
  *
FROM
  ma
ORDER BY
  month DESC
LIMIT 6;

-- Exercises
-- 1. Build MA(6) and MA(12) and compare MAPEs vs seasonal naive.
--    Inputs: For sql-49 Exercise 1, aggregate `orders` by observed month, left-join to `month_spine`, compute full-window history counts, and reshape four forecasts over `common_scoring_rows`.
--    Expected result/shape: For sql-49 Exercise 1, expected output: exactly four rows keyed by `model`, with `scored_rows`, `zero_actual_rows`, and `mape`, ordered by `model`.
--    Verify: For sql-49 Exercise 1, require `ma6_history_rows = 6`, `ma12_history_rows = 12`, and a non-NULL twelve-month seasonal value before any model is scored. All four models must have identical eligible months and equal `scored_rows`; independently recompute each MAPE.
--    Hint ladder, rung 1: For sql-49 Exercise 1, count each CTE before reshaping models: `month_spine` and `forecast_rows` hold 46 months, the first 6 rows have `ma6_history_rows < 6` and the first 12 have `ma12_history_rows < 12`, so `common_scoring_rows` keeps 34 months from 2024-02-01 and the four-model reshape holds 136 rows.
-- 2. Produce a combined forecast blending 50% seasonal-naive and 50% MA(6).
--    Inputs: For sql-49 Exercise 2, aggregate `orders` into 46 calendar months in `monthly`, then in `forecasted` add `LAG(revenue, 12)` as `seasonal_naive` and `AVG(revenue)` over `ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING` as `ma6_forecast`, and blend them 50/50 for every month that has a value a year earlier.
--    Expected result/shape: For sql-49 Exercise 2, expected output: 34 rows, one per `month` from 2024-02-01 to 2026-11-01, with columns `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast`, ordered by `month DESC`, so the partial current month comes first.
--    Verify: For sql-49 Exercise 2, confirm 34 distinct months and that `forecasted` holds exactly 12 rows with a `NULL` `seasonal_naive` (2023-02 to 2024-01), which the `WHERE` removes. Recompute the oldest row by hand: 2024-02 has `actual` 14,823.22, `seasonal_naive` 1,203.26 from 2023-02, `ma6_forecast` 11,859.69 (the mean of 2023-08 to 2024-01), and `blended_forecast` 6,531.47, their average. Then, in a transaction, delete the 91 orders from 2025-03, rerun, and confirm 33 rows and that 2026-03 now takes 33,302.51 from 2025-02 as its "seasonal" value, a 13-month lag; `ROLLBACK`.
--    Hint ladder, rung 1: For sql-49 Exercise 2, run `monthly` (46 rows) and `forecasted` (46 rows) before filtering, and count the `NULL` values in `seasonal_naive` (12) and `ma6_forecast` (1, the first month) so you know exactly which months the filter will drop.
-- 3. Prediction: explain why evaluating a moving average on the same rows used
--    to calculate it leaks the current actual and understates error.
--    Inputs: For sql-49 Exercise 3, aggregate `orders` into 46 calendar months in `monthly` and compute two six-month averages over the same `ORDER BY month` window: `leaky_ma6` with `ROWS BETWEEN 5 PRECEDING AND CURRENT ROW`, and `honest_ma6` with `ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING`.
--    Expected result/shape: For sql-49 Exercise 3, expected output: 46 rows, one per `month` from 2023-02-01 to 2026-11-01, with columns `month`, `revenue`, `leaky_ma6`, and `honest_ma6`, ordered by `month`; only the first row has a `NULL` `honest_ma6`.
--    Verify: For sql-49 Exercise 3, recompute the first three months by hand: 2023-02 has `leaky_ma6` 1,203.26 (its own revenue) and `honest_ma6` `NULL`; 2023-03 has 1,503.345 and 1,203.26; 2023-04 has 2,197.18 and 1,503.345. Then confirm with `LAG(leaky_ma6) OVER (ORDER BY month)` that every row's `honest_ma6` equals the previous row's `leaky_ma6` (0 mismatches over 46 rows), which shows the leaky forecast for a month is the honest one shifted to include the month being forecast. There is no `PARTITION BY`, so there is no partition reset to test; the frame first holds six rows at 2023-07 (leaky) and 2023-08 (honest).
--    Hint ladder, rung 1: For sql-49 Exercise 3, run `monthly` alone and confirm 46 unique months; then list the first eight rows of both windows and mark where each frame first holds a full six rows before you compare any errors.
-- 4. Construction: create a complete monthly spine before LAG(..., 12), then
--    distinguish a missing month from a true zero-revenue month.
--    Inputs: For sql-49 Exercise 4, take the first and last order months from `orders` in `bounds`, build every calendar month between them with `generate_series` in `spine`, `LEFT JOIN` the monthly revenue in `actual` to it in `complete`, and apply `LAG(revenue, 12)` to the spine rather than to the observed months.
--    Expected result/shape: For sql-49 Exercise 4, expected output: 46 rows, one per calendar `month` from 2023-02-01 to 2026-11-01, with columns `month`, `revenue`, `had_source_rows`, and `seasonal_forecast`, ordered by `month`; `seasonal_forecast` is `NULL` for the first 12 months.
--    Verify: For sql-49 Exercise 4, confirm `had_source_rows` is true on all 46 rows today and that 2024-02 takes 1,203.26 from 2023-02. Then, in a transaction, delete the 91 orders from 2025-03 and rerun: the spine still has 46 rows, 2025-03 shows `revenue` `NULL` and `had_source_rows` false, 2026-03 gets a `NULL` `seasonal_forecast` instead of February's 33,302.51, and `ROLLBACK`. Repeat with `UPDATE ... SET total_amount = 0` for those orders instead: 2025-03 shows `revenue` 0.00 with `had_source_rows` true, and 2026-03 gets 0.00.
--    Hint ladder, rung 1: For sql-49 Exercise 4, run `bounds` (2023-02-01 and 2026-11-01), then `spine` (46 rows), then `complete`, and compare its row count with `actual`; any month in `spine` but not in `actual` is one the 12-row lag would otherwise skip.
-- 5. Debugging: repair MAPE when actual revenue is zero and report how many
--    observations were excluded from the percentage error.
--    Inputs: For sql-49 Exercise 5, use the `toy` `VALUES` fixture `(100, 90), (0, 10), (50, 60)` of `actual` and `forecast` and compute MAPE as `AVG(ABS(actual - forecast) / NULLIF(actual, 0))`, counting scored rows and excluded zero actuals.
--    Expected result/shape: For sql-49 Exercise 5, expected output: one row with `mape` 0.1500, `scored_rows` 2, and `excluded_zero_actuals` 1. The final columns are `mape`, `scored_rows`, and `excluded_zero_actuals`.
--    Verify: For sql-49 Exercise 5, confirm by hand that the two scored errors are 10/100 = 0.10 and 10/50 = 0.20, whose mean is 0.15, and that the zero-actual row adds nothing because `NULLIF(actual, 0)` makes its ratio NULL, which `AVG` skips.
--    Hint ladder, rung 1: For sql-49 Exercise 5, compute each row's ratio `ABS(actual - forecast) / NULLIF(actual, 0)` in a plain `SELECT` before you average it.
-- 6. Edge case: compare MAE and MAPE when one low-revenue month has a modest
--    absolute miss but a very large percentage miss.
--    Inputs: For sql-49 Exercise 6, use the `toy` fixture `(1000, 900), (10, 20)` and compute MAE, `AVG(ABS(actual - forecast))`, and MAPE, `AVG(ABS(actual - forecast) / NULLIF(actual, 0))`.
--    Expected result/shape: For sql-49 Exercise 6, expected output: one row with `mae` 55 and `mape` 0.55. The final columns are `mae` and `mape`.
--    Verify: For sql-49 Exercise 6, confirm by hand that the absolute errors are 100 and 10 (mean 55) and the percentage errors are 0.10 and 1.00 (mean 0.55); the output shows that the small month's modest miss dominates MAPE, while the large month dominates MAE.
--    Hint ladder, rung 1: For sql-49 Exercise 6, list each row's absolute and percentage error in a plain `SELECT` before you average them.
ROLLBACK;
