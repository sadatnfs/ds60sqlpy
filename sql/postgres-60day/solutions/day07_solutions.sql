-- Day 07 - Solutions: Week 1 Project (Queries and Validation)
-- Purpose: Provide reference queries for common Week 1 project questions and show validation patterns.
-- Assumes: customers, products, orders, order_items exist in schema training

/*
Q1) Top categories by revenue over a chosen period (parameterizable).
Why: Summarize line revenue by category; parameterize date filters for reuse.
*/
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

/*
Q2) New vs returning customers by month.
Why: First compute first_order_date per customer; classify orders as new/returning relative to first purchase.
*/
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

/*
Q3) Zero-sales products in the last N days.
Why: LEFT JOIN and filter NULL matches; parameterize the window.
*/
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

/*
Validation patterns (sanity checks)
- Totals match: SUM(line revenue) for the period equals SUM(order totals) within rounding tolerance
- Row counts: COUNT(DISTINCT order_id) from lines equals orders filtered by date
*/
-- Example: revenue reconciliation
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

-- End of Day 07 solutions
