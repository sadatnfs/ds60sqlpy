-- Day 26: CTEs with Window Functions
BEGIN;
SET search_path TO training, public;

WITH line AS (
  SELECT o.order_id, o.customer_id, o.order_date,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id, o.order_date
), ranked AS (
  SELECT *, RANK() OVER (PARTITION BY customer_id ORDER BY order_total DESC) AS rnk
  FROM line
)
SELECT * FROM ranked WHERE rnk <= 3
ORDER BY customer_id, rnk;

-- Exercises
-- 1) Build multi-stage CTE: compute monthly totals, then compute MoM growth using window functions.
-- 2) For each product, compute top 5 orders by value using CTE + window rank.

ROLLBACK;
