-- Day 23: CTEs Introduction
BEGIN;
SET search_path TO training, public;

-- Rewrite subqueries as CTEs
WITH order_lines AS (
  SELECT o.order_id,
         o.customer_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id
), top_customers AS (
  SELECT customer_id,
         SUM(order_total) AS lifetime_revenue
  FROM order_lines
  GROUP BY customer_id
)
SELECT tc.customer_id, tc.lifetime_revenue
FROM top_customers tc
ORDER BY lifetime_revenue DESC
LIMIT 20;

-- Exercises
-- 1) Create a CTE for monthly revenue, then select top 3 months.
-- 2) Create a CTE that filters Electronics category orders, then aggregate by country.

ROLLBACK;
