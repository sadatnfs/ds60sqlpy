# Day 49 Solutions — Revenue Forecast Backtesting

The exercises compare moving-average and seasonal-naive forecasts, then inspect
a 50/50 blend. These are historical backtests, not a production forecasting
model. See [`day49_solutions.sql`](day49_solutions.sql).

## Exercise 1 — MA(6), MA(12), seasonal naive, and MAPE

```sql
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
```

Expected shape: four model rows. Lower MAPE is better on the months each model
can score.

## Exercise 2 — Month-by-month blended forecast

```sql
SET search_path TO training, public;

WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
), forecasted AS (
  SELECT month,
         revenue,
         LAG(revenue, 12) OVER (ORDER BY month) AS seasonal_naive,
         AVG(revenue) OVER (
           ORDER BY month ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
         ) AS ma6_forecast
  FROM monthly
)
SELECT month,
       ROUND(revenue, 2) AS actual,
       ROUND(seasonal_naive, 2) AS seasonal_naive,
       ROUND(ma6_forecast, 2) AS ma6_forecast,
       ROUND(0.5 * seasonal_naive + 0.5 * ma6_forecast, 2) AS blended_forecast
FROM forecasted
WHERE seasonal_naive IS NOT NULL
ORDER BY month DESC;
```

## Reasoning, safety, and pitfalls

- Every window ends at `1 PRECEDING`; including the current month's actual would
  leak the answer into its forecast.
- `LAG(..., 12)` assumes one row per calendar month. If a month can be absent,
  join to a complete month calendar first.
- MAPE excludes zero actuals via `NULLIF`; disclose how many periods were
  excluded and compare MAE when zeros are common.
- Different models have different warm-up periods, so a rigorous comparison
  should score all models over the same common months.
