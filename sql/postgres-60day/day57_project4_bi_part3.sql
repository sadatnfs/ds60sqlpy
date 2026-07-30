-- Day 57: Project 4 - Complex BI (Part 3)
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
-- 2. Flag top-10 positive and negative anomalies in the last 6 months with both SD and MAD methods.
-- 3. Prediction: remove the calendar spine and explain why LAG(revenue, 7) now
--    means seven observed rows rather than seven calendar days.
-- 4. Construction: calculate MAE, RMSE, MAPE, and the number of scored rows for
--    both models over one identical evaluation window.
-- 5. Debugging: repair a backtest whose moving-average frame includes CURRENT
--    ROW, and prove the corrected forecast uses no information from the target day.
-- 6. Edge case: create a constant-valued test series and preserve NULL SD/MAD
--    scores when dispersion is zero; do not silently label them normal.

ROLLBACK;
