# Day 57 Solutions — Forecast Accuracy and Anomalies

The exercises compare a seven-day moving average with a weekly seasonal naive,
then rank recent positive and negative anomalies using standard-deviation and
MAD scores. See [`day57_solutions.sql`](day57_solutions.sql).

## Exercise 1 — Compare MA(7) and lag-7 MAPE

The calendar spine makes “seven days ago” mean seven calendar days, including
days with no orders as zero revenue.

```sql
SET search_path TO training, public;

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
```

Expected shape: two model rows. Zero-revenue days are excluded from MAPE by
`NULLIF`; disclose that choice.

## Exercise 2 — Top ten positive and negative anomalies

```sql
SET search_path TO training, public;

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
```

Expected shape: up to ten positive and ten negative rows. The combined absolute
score is a ranking heuristic; it is not a calibrated probability.

## Reasoning, safety, and pitfalls

- A moving average must exclude the current day to avoid leakage.
- The SD score is sensitive to extreme values; the MAD score is more robust.
- `NULLIF` handles zero dispersion. An undefined score should not be silently
  relabeled zero.
- The anomaly query groups only days with orders, unlike the forecast query's
  complete calendar. Choose and document the intended population.
- Anomaly detection flags candidates for investigation, not proven incidents.
