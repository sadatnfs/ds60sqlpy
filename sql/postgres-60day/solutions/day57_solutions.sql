-- Day 57 solutions: forecast accuracy and robust anomaly detection
-- SOLUTION READING MAP — sql-57: Project4 BI Part3
-- Explanation: sql/postgres-60day/solutions/day57_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day57_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
SET search_path TO training, public;

-- Exercise 1: compare prior-seven-day average with seven-day seasonal naive.
WITH bounds AS (
  SELECT MIN(order_date)::date AS min_day,
         MAX(order_date)::date AS max_day
  FROM orders
), calendar AS (
  SELECT day::date
  FROM bounds
  CROSS JOIN LATERAL generate_series(min_day, max_day, interval '1 day') AS day
), daily AS (
  SELECT order_date::date AS day, SUM(total_amount) AS revenue
  FROM orders
  GROUP BY order_date::date
), complete AS (
  SELECT c.day, COALESCE(d.revenue, 0) AS revenue
  FROM calendar c
  LEFT JOIN daily d USING (day)
), forecasts AS (
  SELECT day,
         revenue,
         AVG(revenue) OVER (
           ORDER BY day ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
         ) AS ma7_forecast,
         LAG(revenue, 7) OVER (ORDER BY day) AS seasonal_naive
  FROM complete
)
SELECT 'MA(7)' AS model,
       ROUND(AVG(ABS(revenue - ma7_forecast) / NULLIF(revenue, 0)), 4) AS mape
FROM forecasts
WHERE day >= CURRENT_DATE - 180
  AND ma7_forecast IS NOT NULL
UNION ALL
SELECT 'seasonal naive (lag 7)',
       ROUND(AVG(ABS(revenue - seasonal_naive) / NULLIF(revenue, 0)), 4)
FROM forecasts
WHERE day >= CURRENT_DATE - 180
  AND seasonal_naive IS NOT NULL
ORDER BY model;

-- Exercise 2: rank positive and negative anomalies using both standard and
-- median-absolute-deviation scores.
WITH daily AS (
  SELECT order_date::date AS day, SUM(total_amount) AS revenue
  FROM orders
  WHERE order_date >= CURRENT_TIMESTAMP - interval '6 months'
  GROUP BY order_date::date
), moments AS (
  SELECT AVG(revenue) AS mean_revenue,
         STDDEV_SAMP(revenue) AS sd_revenue
  FROM daily
), median AS (
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY revenue) AS median_revenue
  FROM daily
), deviations AS (
  SELECT d.*,
         m.median_revenue,
         ABS(d.revenue - m.median_revenue) AS absolute_deviation
  FROM daily d
  CROSS JOIN median m
), mad AS (
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY absolute_deviation) AS mad
  FROM deviations
), scored AS (
  SELECT d.day,
         d.revenue,
         (d.revenue - mo.mean_revenue) / NULLIF(mo.sd_revenue, 0) AS sd_z,
         0.6745 * (d.revenue - d.median_revenue) / NULLIF(mad.mad, 0)
           AS modified_z
  FROM deviations d
  CROSS JOIN moments mo
  CROSS JOIN mad
), ranked AS (
  SELECT *,
         CASE WHEN revenue >= (SELECT mean_revenue FROM moments)
              THEN 'positive' ELSE 'negative' END AS direction,
         ROW_NUMBER() OVER (
           PARTITION BY (
             CASE WHEN revenue >= (SELECT mean_revenue FROM moments)
                  THEN 'positive' ELSE 'negative' END
           )
           ORDER BY ABS(sd_z) + ABS(modified_z) DESC, day
         ) AS anomaly_rank
  FROM scored
)
SELECT direction,
       anomaly_rank,
       day,
       ROUND(revenue, 2) AS revenue,
       ROUND(sd_z::numeric, 3) AS sd_z,
       ROUND(modified_z::numeric, 3) AS modified_z
FROM ranked
WHERE anomaly_rank <= 10
ORDER BY direction DESC, anomaly_rank;

-- Exercise 3: show exactly why the calendar spine matters.
-- `observed_daily` has one row only when orders exist, so LAG(..., 7) means
-- “seven prior observations.” `calendar_daily` has one row per calendar date,
-- so the same offset means “seven calendar days.”
WITH bounds AS (
  SELECT MIN(order_date)::date AS min_day,
         MAX(order_date)::date AS max_day
  FROM orders
), observed_daily AS (
  SELECT order_date::date AS day, SUM(total_amount) AS revenue
  FROM orders
  GROUP BY order_date::date
), observed_lag AS (
  SELECT day, revenue, LAG(revenue, 7) OVER (ORDER BY day) AS observed_row_lag7
  FROM observed_daily
), calendar_daily AS (
  SELECT calendar.day::date AS day,
         COALESCE(observed.revenue, 0) AS revenue
  FROM bounds
  CROSS JOIN LATERAL generate_series(
    bounds.min_day, bounds.max_day, interval '1 day'
  ) AS calendar(day)
  LEFT JOIN observed_daily observed ON observed.day = calendar.day::date
), calendar_lag AS (
  SELECT day, revenue, LAG(revenue, 7) OVER (ORDER BY day) AS calendar_day_lag7
  FROM calendar_daily
)
SELECT c.day,
       c.revenue,
       o.observed_row_lag7,
       c.calendar_day_lag7
FROM calendar_lag c
LEFT JOIN observed_lag o USING (day)
ORDER BY c.day DESC
LIMIT 30;

-- Exercise 4: score both forecast models on one identical evaluation set.
-- 1. `calendar_daily` establishes one row per date and a documented zero policy.
-- 2. `forecasts` uses only prior rows: MA(7) ends at 1 PRECEDING, while the
--    seasonal model reads exactly seven calendar rows back.
-- 3. LATERAL VALUES reshapes the two model columns to a common tidy model grain.
-- 4. The WHERE clause requires both forecasts, so model comparisons use the
--    same dates. MAPE additionally excludes zero actuals through NULLIF.
WITH bounds AS (
  SELECT MIN(order_date)::date AS min_day,
         MAX(order_date)::date AS max_day
  FROM orders
), daily AS (
  SELECT order_date::date AS day, SUM(total_amount) AS revenue
  FROM orders
  GROUP BY order_date::date
), calendar_daily AS (
  SELECT calendar.day::date AS day, COALESCE(d.revenue, 0) AS revenue
  FROM bounds
  CROSS JOIN LATERAL generate_series(
    bounds.min_day, bounds.max_day, interval '1 day'
  ) AS calendar(day)
  LEFT JOIN daily d ON d.day = calendar.day::date
), forecasts AS (
  SELECT day,
         revenue,
         AVG(revenue) OVER (
           ORDER BY day ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
         ) AS ma7,
         LAG(revenue, 7) OVER (ORDER BY day) AS seasonal_naive
  FROM calendar_daily
), common_scoring_rows AS (
  SELECT f.day,
         f.revenue AS actual,
         model.model_name,
         model.forecast,
         f.revenue - model.forecast AS error
  FROM forecasts f
  CROSS JOIN LATERAL (
    VALUES ('MA(7)', f.ma7), ('seasonal naive', f.seasonal_naive)
  ) AS model(model_name, forecast)
  WHERE f.ma7 IS NOT NULL
    AND f.seasonal_naive IS NOT NULL
    AND f.day >= (SELECT max_day FROM bounds) - 180
)
SELECT model_name,
       COUNT(*) AS scored_rows,
       ROUND(AVG(ABS(error)), 2) AS mae,
       ROUND(SQRT(AVG(POWER(error, 2))), 2) AS rmse,
       ROUND(AVG(ABS(error) / NULLIF(actual, 0)), 4) AS mape,
       COUNT(*) FILTER (WHERE actual = 0) AS zero_actual_rows
FROM common_scoring_rows
GROUP BY model_name
ORDER BY model_name;

-- Exercise 5: place the leaky and honest frames side by side. The leaky result
-- includes the current actual, so it is not a forecast of that day. The honest
-- frame ends at 1 PRECEDING and can be computed before the target is known.
WITH daily AS (
  SELECT order_date::date AS day, SUM(total_amount) AS revenue
  FROM orders
  GROUP BY order_date::date
)
SELECT day,
       revenue,
       AVG(revenue) OVER (
         ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS leaky_window,
       AVG(revenue) OVER (
         ORDER BY day ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
       ) AS forecast_window
FROM daily
ORDER BY day DESC
LIMIT 20;

-- Exercise 6: constant data has zero SD and zero MAD. Both denominators use
-- NULLIF, preserving an undefined score as NULL instead of declaring the points
-- “normal” with a fabricated zero score.
WITH constant(day, revenue) AS (
  VALUES (date '2026-01-01', 100::numeric),
         (date '2026-01-02', 100::numeric),
         (date '2026-01-03', 100::numeric)
), center AS (
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY revenue) AS median_revenue,
         AVG(revenue) AS mean_revenue,
         STDDEV_SAMP(revenue) AS sd_revenue
  FROM constant
), deviations AS (
  SELECT c.*, ctr.*,
         ABS(c.revenue - ctr.median_revenue) AS absolute_deviation
  FROM constant c CROSS JOIN center ctr
), dispersion AS (
  SELECT percentile_cont(0.5) WITHIN GROUP (
           ORDER BY absolute_deviation
         ) AS mad
  FROM deviations
)
SELECT d.day,
       d.revenue,
       (d.revenue - d.mean_revenue) / NULLIF(d.sd_revenue, 0) AS sd_z,
       0.6745 * (d.revenue - d.median_revenue) / NULLIF(p.mad, 0)
         AS modified_mad_z
FROM deviations d
CROSS JOIN dispersion p
ORDER BY d.day;
