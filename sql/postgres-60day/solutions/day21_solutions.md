# Day 21 — Solutions (Distribution Functions: Percentiles, Quantiles, Ntiles)

We compute percentiles/quantiles, use ordered-set aggregates, and bucket rows with NTILE. We explain window vs aggregate usage and performance considerations.

Setup
- Tables: orders(total_amount, order_date, customer_id), order_items(...)
- Postgres supports ordered-set aggregates: percentile_cont/percentile_disc WITHIN GROUP (ORDER BY ...)

Exercise 1 — Median and percentile bands of order totals
```sql
SELECT 
  percentile_cont(0.5)  WITHIN GROUP (ORDER BY o.total_amount) AS p50,
  percentile_cont(0.9)  WITHIN GROUP (ORDER BY o.total_amount) AS p90,
  percentile_cont(0.95) WITHIN GROUP (ORDER BY o.total_amount) AS p95
FROM orders o;
```
Explanation
- percentile_cont returns a continuous percentile (interpolated). Use percentile_disc for discrete selection among observed values.
- WITHIN GROUP applies to the entire input set since we have no GROUP BY.

Exercise 2 — Monthly P50/P90 order totals
```sql
SELECT date_trunc('month', o.order_date)::date AS month,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY o.total_amount) AS p50,
       percentile_cont(0.9) WITHIN GROUP (ORDER BY o.total_amount) AS p90,
       COUNT(*) AS orders
FROM orders o
GROUP BY date_trunc('month', o.order_date)
ORDER BY month;
```
Notes
- Ordered-set aggregates compute per-group quantiles directly; no subqueries required.
- COUNT(*) alongside percentiles gives context for sample size.

Exercise 3 — Bucket customers into deciles by lifetime revenue
```sql
WITH order_values AS (
  SELECT o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
), ltv AS (
  SELECT customer_id, SUM(order_value) AS lifetime_revenue
  FROM order_values
  GROUP BY customer_id
)
SELECT customer_id,
       lifetime_revenue,
       NTILE(10) OVER (ORDER BY lifetime_revenue DESC) AS decile
FROM ltv
ORDER BY decile, lifetime_revenue DESC
LIMIT 200;
```
Why and pitfalls
- NTILE(k) partitions ordered rows into k buckets as evenly as possible. The sort direction matters for which side gets higher values.
- For ties, buckets may be uneven; for strict quantile boundaries use percentile_cont and join thresholds.
