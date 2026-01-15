# Day 26 — Solutions (CTEs With Windows: Layering Transformations)

We combine CTEs and window functions to keep complex analytics readable. Patterns include pre-aggregating in CTEs then applying windows, and computing multi-grain metrics without fanout.

Setup
- Tables: orders(order_id, customer_id, order_date, total_amount), order_items, products
- Guidance: Pre-aggregate to the lowest required grain per step, then use windows to add context without collapsing rows

Exercise 1 — Daily revenue with month-to-date (MTD) running total
```sql
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), with_month AS (
  SELECT d,
         revenue,
         date_trunc('month', d)::date AS m
  FROM daily
)
SELECT d,
       revenue,
       SUM(revenue) OVER (
         PARTITION BY m
         ORDER BY d
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS mtd_revenue
FROM with_month
ORDER BY d;
```
Line-by-line
- daily: collapse orders to daily grain.
- with_month: attach month key.
- Window sum over the month partition yields true MTD without collapsing the daily rows.

Exercise 2 — Per-customer order totals with country average attached
```sql
WITH order_totals AS (
  SELECT o.order_id, o.customer_id, o.total_amount, c.country
  FROM orders o JOIN customers c ON c.customer_id = o.customer_id
)
SELECT order_id,
       customer_id,
       country,
       total_amount,
       ROUND(AVG(total_amount) OVER (PARTITION BY country), 2) AS country_avg
FROM order_totals
ORDER BY country, total_amount DESC
LIMIT 200;
```
Why
- Country average is a windowed aggregate on the same row set; no need for a join.

Exercise 3 — Top-3 products by category per month without fanout
```sql
WITH lines AS (
  SELECT date_trunc('month', o.order_date)::date AS m,
         p.category,
         oi.product_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS rev
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY 1,2,3
), ranked AS (
  SELECT m, category, product_id, rev,
         ROW_NUMBER() OVER (PARTITION BY m, category ORDER BY rev DESC, product_id) AS rn
  FROM lines
)
SELECT m, category, product_id, ROUND(rev,2) AS rev
FROM ranked
WHERE rn <= 3
ORDER BY m DESC, category, rev DESC;
```
Notes
- Compute at the (month,category,product) grain in a CTE, then rank per partition.
- ROW_NUMBER guarantees exactly 3 rows per partition (breaks ties deterministically by product_id).
