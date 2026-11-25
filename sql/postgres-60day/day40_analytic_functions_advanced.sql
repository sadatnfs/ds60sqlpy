-- Day 40: Analytic Functions - Advanced (statistics and distributions)
-- BEGINNER WORKFLOW - sql-40: Analytic Functions Advanced
-- Guide: sql/postgres-60day/companion-guides/day40_analytic_functions_advanced.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-40.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  SELECT
    date_trunc('day', o.order_date) AS d,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
)
SELECT
  d,
  revenue,
  ROUND(AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW), 2) AS ma15,
  ROUND(STDDEV_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW), 2) AS sd15,
  ROUND(VAR_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW), 2) AS var15
FROM
  daily
ORDER BY
  d DESC
LIMIT 60;

-- Percentiles using PERCENTILE_CONT (continuous) within month
WITH monthly AS (
  SELECT
    date_trunc('month', o.order_date) AS m,
    o.total_amount AS amt
  FROM
    orders o
)
SELECT
  m,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amt) AS p50,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY amt) AS p90,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM
  monthly
GROUP BY
  m
ORDER BY
  m DESC
LIMIT 12;

-- Ratio to total (ratio_to_report equivalent)
WITH cat AS (
  SELECT
    p.category,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    order_items oi
    JOIN products p ON p.product_id = oi.product_id
  GROUP BY
    p.category
)
SELECT
  category,
  ROUND(revenue, 2) AS revenue,
  ROUND(revenue / NULLIF (SUM(revenue) OVER (), 0), 4) AS share_of_total
FROM
  cat
ORDER BY
  revenue DESC;

-- Exercises
-- 1. Compute z-score for daily revenue: (rev - avg15)/sd15.
--    Inputs: For sql-40 Exercise 1, read from `orders`, sum `total_amount` per UTC day in the CTE `daily`, then compute a trailing 15-row mean and sample standard deviation (`ROWS BETWEEN 14 PRECEDING AND CURRENT ROW`) in `rolling` and the z-score `(revenue - avg15) / NULLIF(sd15, 0)`.
--    Expected result/shape: For sql-40 Exercise 1, expected output: 1,080 rows on this load, one per UTC day with orders from 2023-02-13 to 2026-11-23; the second row, 2023-03-07, has `revenue` 1,034.00 against `avg15` 1,118.63 and `z_score` -0.7071. A positive z-score is above the rolling mean; a negative score is below it. The final columns are `order_day`, `revenue`, `avg15`, `sd15`, and `z_score`. The final order is `order_day`.
--    Verify: For sql-40 Exercise 1, confirm one row per `order_day`, so the row count equals `SELECT COUNT(DISTINCT date_trunc('day', order_date)) FROM orders`; the first row has NULL `sd15` and `z_score` because a one-row sample has no standard deviation, and for one later day recompute `avg15` as the mean of that day's and the 14 previous days' `revenue` in `daily`.
--    Hint ladder, rung 1: For sql-40 Exercise 1, run `daily` alone and check one row per `order_day` before `rolling` adds the window statistics.
-- 2. For each category, compute P50 and P90 of order totals.
--    Inputs: For sql-40 Exercise 2, read from `order_items` joined to `products`, sum each order's net lines per category in `category_order_values`, then compute `PERCENTILE_CONT(0.5)` and `PERCENTILE_CONT(0.9)` of those per-order category values and count them per category.
--    Expected result/shape: For sql-40 Exercise 2, expected output: 6 rows, one per category, whose `category_orders` run from 2,145 for Books to 2,192 for Apparel and sum to 13,085, more than the 4,362 orders because an order with lines in several categories counts once in each; `p50_order_value` runs from 146.54 for Home to 150.24 for Electronics on this load. `PERCENTILE_CONT` can interpolate between observed values, so a percentile need not equal an actual order value. The final columns are `category`, `p50_order_value`, `p90_order_value`, and `category_orders`. The final order is `category`.
--    Verify: For sql-40 Exercise 2, confirm 6 rows, one per category, and that `category_orders` equals `SELECT COUNT(DISTINCT oi.order_id) FROM order_items oi JOIN products p USING (product_id) WHERE p.category = <that category>` (for example 2192 for `Apparel`); `p90_order_value` must be at least `p50_order_value` in every row.
--    Hint ladder, rung 1: For sql-40 Exercise 2, run `category_order_values` alone and check that (`category`, `order_id`) is unique before you compute percentiles.
-- 3. Prediction: compare percentile_disc(0.5) with percentile_cont(0.5) for
--    the values (10, 20, 100, 200). Predict both medians before running.
--    Inputs: For sql-40 Exercise 3, use the inline `VALUES` fixture 10, 20, 100, 200 and compute `percentile_disc(0.5)` and `percentile_cont(0.5)` over it.
--    Expected result/shape: For sql-40 Exercise 3, expected output: one row with `discrete_median` 20 and `continuous_median` 60. The final columns are `discrete_median` and `continuous_median`.
--    Verify: For sql-40 Exercise 3, confirm by hand that `percentile_disc(0.5)` returns the first value whose cumulative share reaches 0.5, the second of four values (20), while `percentile_cont(0.5)` interpolates halfway between 20 and 100 (60); add the value 300 and expect both medians to become 100.
--    Hint ladder, rung 1: For sql-40 Exercise 3, list the sorted values with their positions first; with an even count, the two medians differ unless the two middle values are equal.
-- 4. Construction: calculate each category's revenue share within its month,
--    with a deterministic rank for equal revenue.
--    Inputs: For sql-40 Exercise 4, read `orders` for the month, `order_items` for net line revenue `quantity * unit_price * (1 - discount)`, and `products` for `category`; the CTE `category_month` sums revenue per month and category, `SUM(revenue) OVER (PARTITION BY month)` supplies the share denominator, and `ROW_NUMBER() OVER (PARTITION BY month ORDER BY revenue DESC, category)` supplies the rank.
--    Expected result/shape: For sql-40 Exercise 4, expected output: 276 rows on this load, 46 months from 2023-02-01 to 2026-11-01 times all 6 categories, with `category_rank` 1 to 6 in every month; the newest month starts with Sports at 16,427.31 and a `month_share` of 0.1924 and ends with Home at rank 6. The final columns are `month`, `category`, `revenue`, `month_share`, and `category_rank`. The final order is `month DESC, category_rank`.
--    Verify: For sql-40 Exercise 4, confirm 276 distinct `(month, category)` pairs, that the unrounded shares sum to exactly 1 in each of the 46 months while the rounded `month_share` values sum to between 0.9998 and 1.0002, and that `SUM(revenue)` over all rows is 2,355,647.1235, the `order_items` line total; this load has no revenue ties, so `RANK()` matches `ROW_NUMBER()` in every row, but on `VALUES ('Books', 100.00), ('Apparel', 100.00), ('Home', 90.00)` the `category` tiebreaker ranks Apparel 1 and Books 2 where `RANK()` gives both 1.
--    Hint ladder, rung 1: For sql-40 Exercise 4, run `category_month` one at a time. Record each CTE's row count and `month`, and `category` uniqueness before the next stage uses it.
-- 5. Debugging: repair a rolling average that includes the current row when the
--    intended forecast must use only prior observations.
--    Inputs: For sql-40 Exercise 5, read `orders`, sum `total_amount` per `order_date::date` in the CTE `daily`, then average the seven previous order days with `AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING)`, so a day's own revenue never feeds its forecast.
--    Expected result/shape: For sql-40 Exercise 5, expected output: exactly 20 rows on this load, the consecutive days from 2026-11-23 back to 2026-11-04, each with a non-NULL forecast; the top row is 2026-11-23 with `revenue` 742.14 and `prior_seven_forecast` 2,300.43. The final columns are `day`, `revenue`, and `prior_seven_forecast`. The final order is `day DESC`.
--    Verify: For sql-40 Exercise 5, confirm 2,300.43 by averaging the seven `daily` rows before 2026-11-23 (`ORDER BY day DESC LIMIT 7`), and that the leaky frame `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` reports 2,079.31 for that day; then, inside `BEGIN ... ROLLBACK`, insert a 500.00 order on 2026-11-24 and confirm it becomes the top row with forecast 2,079.31, the leaky value shifted one day, while the 20-row window now starts at 2026-11-05.
--    Hint ladder, rung 1: For sql-40 Exercise 5, run `daily` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
-- 6. Edge case: compute a z-score for a constant three-row series and preserve
--    NULL when standard deviation is zero.
--    Inputs: For sql-40 Exercise 6, use the inline `VALUES` fixture `constant`, three rows of 5; `moments` adds `AVG(value) OVER ()` and `STDDEV_SAMP(value) OVER ()` to every row, and the outer query divides `value - mean_value` by `NULLIF(sd_value, 0)`.
--    Expected result/shape: For sql-40 Exercise 6, expected output: three rows, each with `value` 5 and a NULL `z_score`, because the sample standard deviation is 0 and `NULLIF` turns that 0 into NULL. The final columns are `value`, and `z_score`.
--    Verify: For sql-40 Exercise 6, confirm that dividing by `sd_value` without `NULLIF` fails with `division by zero`, that the fixture 5, 5, 6 gives `z_score` values -0.5774, -0.5774, and 1.1547, and that adding a `NULL` row returns four rows with every `z_score` NULL: `STDDEV_SAMP` skips the NULL, so the 5s still have zero spread, and the NULL row's own difference is NULL.
--    Hint ladder, rung 1: For sql-40 Exercise 6, run `moments` one at a time. Record each CTE's row count and `value` uniqueness before the next stage uses it.
ROLLBACK;
