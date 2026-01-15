# Day 18 — Solutions (LAG/LEAD and Intra‑Row Comparisons)

We calculate day‑to‑day deltas and growth, per‑customer gaps between orders, and price changes over time.

Setup
- Tables: orders(order_id, customer_id, order_date, total_amount), products_price_history(product_id, price, effective_at)
- Tips: Protect division by zero with NULLIF; use EXTRACT(...) to turn intervals into numbers

Exercise 1 — Daily revenue delta and growth rate
```sql
WITH daily AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY DATE_TRUNC('day', o.order_date)
)
SELECT d,
       revenue,
       (revenue - LAG(revenue) OVER (ORDER BY d)) AS delta,
       ROUND(
         (revenue - LAG(revenue) OVER (ORDER BY d))
         / NULLIF(LAG(revenue) OVER (ORDER BY d), 0)
       , 4) AS growth_rate
FROM daily
ORDER BY d DESC
LIMIT 60;
```
Explanation
- LAG(revenue) pulls prior day’s value to the current row; subtract to get delta.
- Growth = delta / prior; NULLIF avoids divide‑by‑zero when the prior day’s revenue was 0.

Exercise 2 — Days between orders per customer; flag gaps > 60 days
```sql
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date) AS prev_order,
       EXTRACT(DAY FROM (o.order_date - LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date))) AS days_since_prev,
       CASE WHEN o.order_date - LAG(o.order_date) OVER (PARTITION BY o.customer_id ORDER BY o.order_date) > INTERVAL '60 days'
            THEN TRUE ELSE FALSE END AS gap_gt_60
FROM orders o
ORDER BY o.customer_id, o.order_date
LIMIT 200;
```
Notes
- Window partition by customer computes gaps within each user’s timeline.
- You can also compute median gaps later per user using percentile_disc on days_since_prev.

Exercise 3 — Product price deltas over time
```sql
SELECT product_id,
       effective_at,
       price,
       price - LAG(price) OVER (PARTITION BY product_id ORDER BY effective_at) AS price_delta
FROM products_price_history
ORDER BY product_id, effective_at
LIMIT 200;
```
Tips
- If you need pct change: (price / LAG(price) - 1). Use ROUND as needed for presentation.
- Ensure effective_at has no duplicates per product; otherwise define a secondary tiebreak (e.g., updated_at, product_id).
