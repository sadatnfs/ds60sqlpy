# Day 20 — Solutions (FIRST_VALUE, LAST_VALUE, NTH_VALUE)

We compare current values to first values within a partition, and attach the month’s last value to each row. Proper framing is crucial for these functions.

Setup
- Tables: orders(order_id, order_date, total_amount)
- Frame caution: default frame is `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` in many systems; for FIRST/LAST over the whole partition, specify UNBOUNDED FOLLOWING explicitly

Exercise 1 — Each order vs the customer’s first order amount
```sql
WITH per_order AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         o.total_amount AS order_total
  FROM orders o
)
SELECT customer_id,
       order_id,
       order_date,
       order_total,
       FIRST_VALUE(order_total) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS first_order_amt,
       ROUND(order_total / NULLIF(FIRST_VALUE(order_total) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ), 0), 4) AS vs_first_ratio
FROM per_order
ORDER BY customer_id, order_date, order_id
LIMIT 300;
```
Explanation
- FIRST_VALUE over a full partition gives the baseline. Without the UNBOUNDED FOLLOWING, some engines would use a frame ending at CURRENT ROW, causing FIRST_VALUE to change across rows in certain ORDER BY/FRAME combinations.

Exercise 2 — Month’s last day revenue attached to each day
```sql
WITH daily AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY DATE_TRUNC('day', o.order_date)
), with_month AS (
  SELECT d,
         revenue,
         DATE_TRUNC('month', d)::date AS m
  FROM daily
)
SELECT d,
       revenue,
       LAST_VALUE(revenue) OVER (
         PARTITION BY m ORDER BY d
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS month_last_rev
FROM with_month
ORDER BY d DESC
LIMIT 60;
```
Notes
- LAST_VALUE returns the value at the end of the frame; hence, you must extend the frame to UNBOUNDED FOLLOWING to get the true month‑end value on every row.
- NTH_VALUE works similarly for arbitrary positions; ensure deterministic ORDER BY.
