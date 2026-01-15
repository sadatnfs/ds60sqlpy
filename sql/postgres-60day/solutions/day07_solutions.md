# Day 07 — Solutions (Week 1 Project Queries and Validation)

This writeup explains the reference queries and the reasoning behind them, plus validation patterns to keep analyses honest.

Setup
- Parameterization: use small CTEs for date windows so you can tweak in one place
- Facts: orders, order_items; Dimensions: products, customers

Q1 — Top categories by revenue over a chosen period
```sql
WITH params AS (
  SELECT DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month' AS start_dt,
         DATE_TRUNC('month', CURRENT_DATE)                     AS end_dt
), lines AS (
  SELECT p.category,
         SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  JOIN orders o   ON o.order_id = oi.order_id
  WHERE o.order_date >= (SELECT start_dt FROM params)
    AND o.order_date <  (SELECT end_dt   FROM params)
  GROUP BY p.category
)
SELECT category, ROUND(revenue,2) AS revenue
FROM lines
ORDER BY revenue DESC
LIMIT 10;
```
Line-by-line
- params: centralizes time window; easy to vary period without touching logic
- SUM(...) uses line-level revenue; we group by category only, not by SKU, to avoid accidental double counting
- ORDER BY revenue DESC and LIMIT 10 yields the leaderboard
Pitfalls
- Grouping by both category and product_id when you really want category totals
- Filtering by month using LIKE on formatted text; always use timestamp comparisons

Q2 — New vs returning customers by month
```sql
WITH firsts AS (
  SELECT o.customer_id,
         MIN(o.order_date) AS first_order_date
  FROM orders o
  GROUP BY o.customer_id
), classified AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS month,
         CASE WHEN o.order_date = f.first_order_date THEN 'new' ELSE 'returning' END AS cust_type,
         o.order_id
  FROM orders o
  JOIN firsts f ON f.customer_id = o.customer_id
)
SELECT month,
       cust_type,
       COUNT(DISTINCT order_id) AS orders
FROM classified
GROUP BY month, cust_type
ORDER BY month, cust_type;
```
Explanation
- firsts: each customer’s first purchase timestamp
- CASE compares current order vs first; equal → new, else returning
- COUNT(DISTINCT order_id) tallies orders; you can also compute revenue similarly
Pitfalls
- Using MIN over all time but then filtering orders downstream; compute firsts on the same cohort if you’re doing cohort-specific analyses

Q3 — Zero-sales products in last N days
```sql
WITH params AS (
  SELECT CURRENT_DATE - INTERVAL '30 days' AS start_dt
)
SELECT p.product_id, p.name, p.category
FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.product_id
LEFT JOIN orders o       ON o.order_id = oi.order_id
  AND o.order_date >= (SELECT start_dt FROM params)
WHERE o.order_id IS NULL
ORDER BY p.product_id
LIMIT 200;
```
Why this way
- RIGHT-side predicates on the ON clause preserve the LEFT join semantics
- WHERE o.order_id IS NULL finds products with no matching orders in the window

Validation patterns (sanity checks)
```sql
WITH params AS (
  SELECT DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month' AS start_dt,
         DATE_TRUNC('month', CURRENT_DATE)                     AS end_dt
), by_lines AS (
  SELECT SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS rev
  FROM order_items oi JOIN orders o ON o.order_id = oi.order_id
  WHERE o.order_date >= (SELECT start_dt FROM params)
    AND o.order_date <  (SELECT end_dt   FROM params)
), by_orders AS (
  SELECT SUM(o.total_amount) AS rev
  FROM orders o
  WHERE o.order_date >= (SELECT start_dt FROM params)
    AND o.order_date <  (SELECT end_dt   FROM params)
)
SELECT (SELECT rev FROM by_lines)  AS rev_by_lines,
       (SELECT rev FROM by_orders) AS rev_by_orders,
       ROUND((SELECT rev FROM by_lines) - (SELECT rev FROM by_orders), 2) AS difference;
```
Notes
- Differences often come from discounts, taxes, shipping, or returns; reconcile definitions before concluding an error
