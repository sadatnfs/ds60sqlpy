-- Day 49 solutions: revenue forecast backtesting
SET search_path TO training, public;

WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
), forecasts AS (
  SELECT month,
         revenue,
         AVG(revenue) OVER (
           ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
         ) AS ma6_forecast,
         AVG(revenue) OVER (
           ORDER BY month ROWS BETWEEN 12 PRECEDING AND 1 PRECEDING
         ) AS ma12_forecast,
         LAG(revenue, 12) OVER (ORDER BY month) AS seasonal_naive
  FROM monthly
), scored AS (
  SELECT *,
         ABS(revenue - ma6_forecast) / NULLIF(revenue, 0) AS ape_ma6,
         ABS(revenue - ma12_forecast) / NULLIF(revenue, 0) AS ape_ma12,
         ABS(revenue - seasonal_naive) / NULLIF(revenue, 0) AS ape_seasonal,
         0.5 * seasonal_naive + 0.5 * ma6_forecast AS blended_forecast
  FROM forecasts
)
-- Exercise 1: compare out-of-sample-style one-step forecast errors.
SELECT 'MA(6)' AS model, ROUND(AVG(ape_ma6), 4) AS mape
FROM scored
WHERE ma6_forecast IS NOT NULL
UNION ALL
SELECT 'MA(12)', ROUND(AVG(ape_ma12), 4)
FROM scored
WHERE ma12_forecast IS NOT NULL
UNION ALL
SELECT 'seasonal naive', ROUND(AVG(ape_seasonal), 4)
FROM scored
WHERE seasonal_naive IS NOT NULL
UNION ALL
SELECT '50% seasonal + 50% MA(6)',
       ROUND(AVG(ABS(revenue - blended_forecast) / NULLIF(revenue, 0)), 4)
FROM scored
WHERE blended_forecast IS NOT NULL
ORDER BY model;

-- Exercise 2: forecast the next three months. This compact answer holds the
-- latest six-month average flat and blends it with each month last year.
WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
), latest_six AS (
  SELECT AVG(revenue) AS ma6_forecast
  FROM (
    SELECT revenue
    FROM monthly
    ORDER BY month DESC
    LIMIT 6
  ) recent
), future AS (
  SELECT (
           date_trunc('month', CURRENT_DATE)
           + n * interval '1 month'
         )::date AS forecast_month
  FROM generate_series(1, 3) AS g(n)
)
SELECT f.forecast_month,
       ROUND(seasonal.revenue, 2) AS seasonal_naive,
       ROUND(m.ma6_forecast, 2) AS ma6_forecast,
       ROUND(0.5 * seasonal.revenue + 0.5 * m.ma6_forecast, 2)
         AS blended_forecast
FROM future f
CROSS JOIN latest_six m
LEFT JOIN monthly seasonal
  ON seasonal.month = (f.forecast_month - interval '12 months')::date
ORDER BY f.forecast_month;
