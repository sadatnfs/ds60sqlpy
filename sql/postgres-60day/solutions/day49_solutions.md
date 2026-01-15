# Day 49 — Solutions (Project 2: Finance/Operations, Part 1 — Revenue Forecasting)

We build monthly revenue, year‑over‑year comparisons, and simple forecasts. Exercises focus on MA(6)/MA(12) and error metrics vs seasonal naive.

Reference monthly revenue
```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT * FROM monthly ORDER BY month DESC LIMIT 24;
```

Exercise 1 — MA(6) and MA(12) and compare MAPEs vs seasonal naive
Goal
- Compute three forecasts for each month t: seasonal_naive(t) = revenue(t−12), MA6(t) = avg(revenue of last 6 months), MA12(t) = avg(last 12 months). Evaluate MAPE over a trailing window.

Solution
```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), feats AS (
  SELECT month,
         revenue,
         LAG(revenue, 12) OVER (ORDER BY month) AS seasonal_naive,
         AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING)  AS ma6,
         AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) AS ma12
  FROM monthly
), mape AS (
  SELECT month,
         revenue AS actual,
         seasonal_naive,
         ma6,
         ma12,
         CASE WHEN revenue IS NULL OR revenue = 0 OR seasonal_naive IS NULL THEN NULL
              ELSE ABS(revenue - seasonal_naive) / revenue END AS ape_seasonal,
         CASE WHEN revenue IS NULL OR revenue = 0 OR ma6 IS NULL THEN NULL
              ELSE ABS(revenue - ma6) / revenue END AS ape_ma6,
         CASE WHEN revenue IS NULL OR revenue = 0 OR ma12 IS NULL THEN NULL
              ELSE ABS(revenue - ma12) / revenue END AS ape_ma12
  FROM feats
)
SELECT month,
       ROUND(actual,2) AS actual,
       ROUND(seasonal_naive,2) AS fc_seasonal,
       ROUND(ma6,2) AS fc_ma6,
       ROUND(ma12,2) AS fc_ma12,
       ROUND(ape_seasonal,4) AS ape_seasonal,
       ROUND(ape_ma6,4) AS ape_ma6,
       ROUND(ape_ma12,4) AS ape_ma12
FROM mape
ORDER BY month DESC
LIMIT 24;
```
Line‑by‑line notes
- LAG(...,12): aligns last year’s same month.
- ROWS BETWEEN N PRECEDING AND 1 PRECEDING: moving average excluding current month to avoid leakage.
- APE guards: return NULL when actual is 0 or forecast missing.

Aggregate MAPEs over evaluation window (optional)
```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), feats AS (
  SELECT month,
         revenue,
         LAG(revenue, 12) OVER (ORDER BY month) AS seasonal_naive,
         AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING)  AS ma6,
         AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 11 PRECEDING AND 1 PRECEDING) AS ma12
  FROM monthly
), mape AS (
  SELECT month,
         revenue AS actual,
         seasonal_naive,
         ma6,
         ma12,
         CASE WHEN revenue IS NULL OR revenue = 0 OR seasonal_naive IS NULL THEN NULL
              ELSE ABS(revenue - seasonal_naive) / revenue END AS ape_seasonal,
         CASE WHEN revenue IS NULL OR revenue = 0 OR ma6 IS NULL THEN NULL
              ELSE ABS(revenue - ma6) / revenue END AS ape_ma6,
         CASE WHEN revenue IS NULL OR revenue = 0 OR ma12 IS NULL THEN NULL
              ELSE ABS(revenue - ma12) / revenue END AS ape_ma12
  FROM feats
)
SELECT ROUND(AVG(ape_seasonal),4) AS mape_seasonal,
       ROUND(AVG(ape_ma6),4)      AS mape_ma6,
       ROUND(AVG(ape_ma12),4)     AS mape_ma12
FROM mape
WHERE month >= (SELECT MIN(month) + interval '24 months' FROM mape);
```
Notes
- The WHERE clause ensures enough history exists for MA12/seasonal prior to evaluation.

Exercise 2 — Combined forecast: 50% seasonal naive + 50% MA(6)
```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), feats AS (
  SELECT month,
         revenue,
         LAG(revenue, 12) OVER (ORDER BY month) AS seasonal_naive,
         AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING) AS ma6
  FROM monthly
)
SELECT month,
       ROUND(revenue,2) AS actual,
       ROUND(0.5*seasonal_naive + 0.5*ma6, 2) AS fc_blend,
       CASE WHEN revenue IS NULL OR revenue = 0 OR seasonal_naive IS NULL OR ma6 IS NULL THEN NULL
            ELSE ROUND(ABS(revenue - (0.5*seasonal_naive + 0.5*ma6)) / revenue, 4)
       END AS ape_blend
FROM feats
ORDER BY month DESC
LIMIT 24;
```
Notes
- Blending stabilizes forecasts: seasonal captures yearly seasonality; MA6 captures local trend.
