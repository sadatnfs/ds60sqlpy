# Day 16 — Solutions (Window Functions Fundamentals)

We compute per-customer lifetime revenue alongside each order, a 30‑day rolling average of daily revenue, and per‑category product shares using window functions. Explanations focus on PARTITION BY, ORDER BY, and frame clauses.

Setup
- Schema: training; tables: orders(order_id, customer_id, order_date, total_amount), order_items, products
- Frames: Use ROWS frames for precise row counts; UNBOUNDED PRECEDING/FOLLOWING to span full partitions

Exercise 1 — Order total vs customer lifetime revenue and share
```sql
SELECT o.customer_id,
       o.order_id,
       o.total_amount AS order_total,
       ROUND(
         SUM(o.total_amount) OVER (
           PARTITION BY o.customer_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
         )
       , 2) AS customer_lifetime_rev,
       ROUND(
         o.total_amount / NULLIF(
           SUM(o.total_amount) OVER (PARTITION BY o.customer_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
         , 0)
       , 4) AS order_share_of_lifetime
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 200;
```
Line‑by‑line
- SUM(...) OVER (PARTITION BY customer_id ...): Adds each order’s value to a running total that covers the entire customer partition (frame spans the whole partition).
- Share = order_total / lifetime; NULLIF avoids divide‑by‑zero for degenerate cases (e.g., zero totals).
- ORDER BY in the outer query is for readability; the window result is the same regardless because the frame spans full partition.

Exercise 2 — 30‑day rolling average of daily revenue (ROWS vs RANGE)
```sql
WITH daily AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY DATE_TRUNC('day', o.order_date)
)
SELECT d,
       revenue,
       ROUND(
         AVG(revenue) OVER (
           ORDER BY d
           ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
         )
       ,2) AS ma30_rows
FROM daily
ORDER BY d DESC
LIMIT 60;
```
Explanation
- Pre-aggregate to daily grain for a compact series.
- ROWS BETWEEN 29 PRECEDING AND CURRENT ROW takes exactly 30 rows (days) even if multiple days share the same revenue; RANGE may expand when peers exist and is not appropriate for fixed‑width moving windows.
- Early days will average over fewer rows until 30 days accumulate.

Exercise 3 — Product revenue and share within category
```sql
WITH prod_rev AS (
  SELECT p.category,
         oi.product_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, oi.product_id
)
SELECT category,
       product_id,
       ROUND(revenue,2) AS revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (PARTITION BY category),0), 4) AS share_in_category
FROM prod_rev
ORDER BY category, share_in_category DESC
LIMIT 300;
```
Notes
- SUM(...) OVER (PARTITION BY category) gives the category total as the denominator without collapsing rows.
- Use ROUND only for presentation; keep internal arithmetic at full precision.
