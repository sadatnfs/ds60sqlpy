# Day 57 — Solutions (Project 4: Complex BI, Part 3 — Trends, Anomalies, Accuracy)

We detect anomalies with z-scores and MAD, and evaluate simple forecasts. Below are detailed, line-by-line solutions to the practice exercises.

Reference (annotated)
```sql
-- Daily revenue baseline with rolling stats
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), stats AS (
  SELECT d,
         revenue,
         -- rolling average of the previous 14 days (excluding today)
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
```
Explanation
- daily: collapse orders to 1 row per day.
- stats: compute rolling avg and standard deviation using a 14-day lookback.
- Output: z_score flags days ±3 SD away from recent trend.

Exercise 1 — Replace MA(7) with seasonal naive (t−7) and compare MAPE
Goal
- Compare forecast error when using the value from 7 days ago vs the MA(7) baseline.

Solution
```sql
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), feats AS (
  SELECT d,
         revenue,
         LAG(revenue, 7) OVER (ORDER BY d) AS seasonal_naive,
         AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS ma7
  FROM daily
), errors AS (
  SELECT d,
         revenue AS actual,
         seasonal_naive,
         ma7,
         CASE WHEN revenue IS NULL OR revenue = 0 OR seasonal_naive IS NULL THEN NULL
              ELSE ABS(revenue - seasonal_naive)/revenue END AS ape_seasonal,
         CASE WHEN revenue IS NULL OR revenue = 0 OR ma7 IS NULL THEN NULL
              ELSE ABS(revenue - ma7)/revenue END AS ape_ma7
  FROM feats
)
SELECT d,
       ROUND(actual,2) AS actual,
       ROUND(seasonal_naive,2) AS fc_t_minus_7,
       ROUND(ma7,2) AS fc_ma7,
       ROUND(ape_seasonal,4) AS ape_t_minus_7,
       ROUND(ape_ma7,4) AS ape_ma7
FROM errors
ORDER BY d DESC
LIMIT 30;
```
Line-by-line notes
- LAG(...,7): aligns same weekday last week; captures weekly seasonality.
- Excluding current day from MA(7) ensures no leakage.
- APE guards: return NULL when actual is 0 or forecast unavailable.

Aggregate MAPE (optional)
```sql
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), feats AS (
  SELECT d,
         revenue,
         LAG(revenue, 7) OVER (ORDER BY d) AS seasonal_naive,
         AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS ma7
  FROM daily
), errors AS (
  SELECT d,
         revenue AS actual,
         seasonal_naive,
         ma7,
         CASE WHEN revenue IS NULL OR revenue = 0 OR seasonal_naive IS NULL THEN NULL
              ELSE ABS(revenue - seasonal_naive)/revenue END AS ape_seasonal,
         CASE WHEN revenue IS NULL OR revenue = 0 OR ma7 IS NULL THEN NULL
              ELSE ABS(revenue - ma7)/revenue END AS ape_ma7
  FROM feats
)
SELECT ROUND(AVG(ape_seasonal),4) AS mape_t_minus_7,
       ROUND(AVG(ape_ma7),4)      AS mape_ma7
FROM errors
WHERE d >= (SELECT MIN(d) + interval '14 days' FROM errors);
```

Exercise 2 — Flag top-10 positive and negative anomalies (last 6 months) with SD and MAD
Goal
- Produce two lists each for SD-based and MAD-based anomalies over the last 6 months: highest positive deviations and lowest negative deviations.

A) SD-based z-score extremes
```sql
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), stats AS (
  SELECT d,
         revenue,
         AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS avg14,
         STDDEV_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS sd14
  FROM daily
), scored AS (
  SELECT d,
         revenue,
         (CASE WHEN sd14 IS NULL OR sd14=0 THEN NULL ELSE (revenue - avg14)/sd14 END) AS z
  FROM stats
), last6 AS (
  SELECT * FROM scored WHERE d >= CURRENT_DATE - interval '6 months'
)
-- Top-10 positive z
SELECT 'sd_top_pos' AS list, d, ROUND(revenue,2) AS revenue, ROUND(z,2) AS score
FROM last6
WHERE z IS NOT NULL
ORDER BY z DESC
LIMIT 10;

-- Top-10 negative z
SELECT 'sd_top_neg' AS list, d, ROUND(revenue,2) AS revenue, ROUND(z,2) AS score
FROM last6
WHERE z IS NOT NULL
ORDER BY z ASC
LIMIT 10;
```
Notes
- Separate queries for positive and negative extremes improve readability.

B) MAD-based modified z-score extremes (robust)
```sql
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), med AS (
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY revenue) AS median_rev FROM daily
), dev AS (
  SELECT d.d, d.revenue, m.median_rev,
         ABS(d.revenue - m.median_rev) AS abs_dev
  FROM daily d CROSS JOIN med m
), mad AS (
  SELECT d,
         revenue,
         median_rev,
         percentile_cont(0.5) WITHIN GROUP (ORDER BY abs_dev) AS mad
  FROM dev
), scored AS (
  SELECT d,
         revenue,
         CASE WHEN mad = 0 THEN NULL ELSE 0.6745 * (revenue - median_rev) / mad END AS mod_z
  FROM mad
), last6 AS (
  SELECT * FROM scored WHERE d >= CURRENT_DATE - interval '6 months'
)
-- Top-10 positive modified z
SELECT 'mad_top_pos' AS list, d, ROUND(revenue,2) AS revenue, ROUND(mod_z,2) AS score
FROM last6
WHERE mod_z IS NOT NULL
ORDER BY mod_z DESC
LIMIT 10;

-- Top-10 negative modified z
SELECT 'mad_top_neg' AS list, d, ROUND(revenue,2) AS revenue, ROUND(mod_z,2) AS score
FROM last6
WHERE mod_z IS NOT NULL
ORDER BY mod_z ASC
LIMIT 10;
```
Line-by-line notes
- med/dev/mad: compute median and median absolute deviation.
- 0.6745 rescales MAD to approximate standard deviations under normality.
- Using last 6 months window focuses on recent operations.

Tips
- Use both SD and MAD; SD is more sensitive to outliers, MAD is robust when distributions are skewed.
- Persist anomaly labels in a table for downstream alerting and BI.
