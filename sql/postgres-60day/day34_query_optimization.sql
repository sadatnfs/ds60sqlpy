-- Day 34: Query Optimization Techniques
BEGIN;
SET search_path TO training, public;

-- Predicate pushdown by filtering early in CTE
WITH filtered_orders AS (
  SELECT order_id, customer_id FROM orders WHERE order_date >= now() - interval '30 days'
)
SELECT c.country, COUNT(*)
FROM filtered_orders fo
JOIN customers c ON c.customer_id = fo.customer_id
GROUP BY c.country
ORDER BY COUNT(*) DESC;

-- Avoid SELECT * and unnecessary columns to reduce I/O
EXPLAIN ANALYZE
SELECT o.order_id, o.customer_id
FROM orders o
WHERE o.order_date >= now() - interval '7 days';

-- Join order rewrite (ensure correct join conditions, indexes)
EXPLAIN
SELECT p.category, SUM(oi.quantity) AS qty
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.status IN ('paid','shipped','delivered')
GROUP BY p.category;

-- Exercises
-- 1) Replace subqueries with joins and compare plans.
-- 2) Limit rows as early as possible and compare performance.

ROLLBACK;
