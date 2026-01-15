# Day 19 — Solutions (Running Aggregates and Moving Windows)

We compute rolling averages on daily revenue and cumulative per‑customer spend and order counts. Emphasis on fixed‑row frames and stable ordering.

Setup
- Tables: orders(order_date, total_amount)
- Use ROWS frames for exact window sizes; ORDER BY includes a deterministic tiebreak when needed

Exercise 1 — 7‑day and 28‑day moving averages
```sql
WITH daily AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY DATE_TRUNC('day', o.order_date)
)
SELECT d,
       revenue,
       ROUND(AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING  AND CURRENT ROW), 2) AS ma7,
       ROUND(AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 27 PRECEDING AND CURRENT ROW), 2) AS ma28
FROM daily
ORDER BY d DESC
LIMIT 60;
```
Reasoning
- ROWS frames enforce exact window width regardless of duplicate values; RANGE would expand to all peers with equal ordering key.
- Early days naturally average over fewer observations until the window fills.

Exercise 2 — Per‑customer cumulative spend and order count
```sql
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount,
       SUM(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cum_spend,
       COUNT(*) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cum_orders
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 300;
```
Notes
- Include order_id in ORDER BY to break ties within the same timestamp for deterministic cumulative results.
- For running distinct counts, consider approximate methods (e.g., HyperLogLog) or windowed COUNT(DISTINCT) in engines that support it.
