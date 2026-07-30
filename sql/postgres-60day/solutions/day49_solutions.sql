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

-- Exercise 3: the leaky frame includes the target actual; the honest frame ends
-- at 1 PRECEDING. Display both to make the bias observable.
WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders GROUP BY date_trunc('month', order_date)
)
SELECT month, revenue,
       AVG(revenue) OVER (
         ORDER BY month ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
       ) AS leaky_ma6,
       AVG(revenue) OVER (
         ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
       ) AS honest_ma6
FROM monthly
ORDER BY month;

-- Exercise 4: generate the calendar first so LAG(...,12) means 12 calendar
-- months. The observed flag distinguishes missing from explicit zero revenue.
WITH bounds AS (
  SELECT date_trunc('month', MIN(order_date))::date AS first_month,
         date_trunc('month', MAX(order_date))::date AS last_month FROM orders
), spine AS (
  SELECT generate_series(first_month, last_month, interval '1 month')::date AS month
  FROM bounds
), actual AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders GROUP BY date_trunc('month', order_date)
), complete AS (
  SELECT s.month, a.revenue, (a.month IS NOT NULL) AS had_source_rows
  FROM spine s LEFT JOIN actual a USING (month)
)
SELECT month, revenue, had_source_rows,
       LAG(revenue, 12) OVER (ORDER BY month) AS seasonal_forecast
FROM complete
ORDER BY month;

-- Exercise 5: MAPE excludes zero actuals through NULLIF and reports the scoring
-- denominator so the omission is visible.
WITH toy(actual, forecast) AS (
  VALUES (100::numeric, 90::numeric), (0, 10), (50, 60)
)
SELECT ROUND(AVG(ABS(actual - forecast) / NULLIF(actual, 0)), 4) AS mape,
       COUNT(*) FILTER (WHERE actual <> 0) AS scored_rows,
       COUNT(*) FILTER (WHERE actual = 0) AS excluded_zero_actuals
FROM toy;

-- Exercise 6: MAE is currency-scale error; MAPE magnifies the small-actual miss.
WITH toy(actual, forecast) AS (
  VALUES (1000::numeric, 900::numeric), (10, 20)
)
SELECT AVG(ABS(actual - forecast)) AS mae,
       AVG(ABS(actual - forecast) / NULLIF(actual, 0)) AS mape
FROM toy;
