-- Day 7: Week 1 Mini-Project
-- Build a comprehensive report combining joins, aggregates, set ops
BEGIN;
SET search_path TO training, public;

-- Customer revenue by country and category (last 90 days)
WITH recent_orders AS (
  SELECT * FROM orders WHERE order_date >= now() - interval '90 days'
), line AS (
  SELECT ro.order_id, ro.customer_id, c.country, p.category,
         (oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_revenue
  FROM recent_orders ro
  JOIN customers c ON c.customer_id = ro.customer_id
  JOIN order_items oi ON oi.order_id = ro.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT country, category,
       ROUND(SUM(line_revenue),2) AS revenue,
       COUNT(DISTINCT customer_id) AS buyers,
       ROUND(SUM(line_revenue)/NULLIF(COUNT(DISTINCT customer_id),0),2) AS rev_per_buyer
FROM line
GROUP BY country, category
ORDER BY revenue DESC
LIMIT 50;

-- Exercises
-- 1) Add payment method dimension; show revenue by country, category, method.
-- 2) Add a cohort dimension: group customers by month(created_at) and re-run.

ROLLBACK;
