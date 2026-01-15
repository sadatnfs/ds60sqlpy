-- Day 9: Correlated Subqueries, EXISTS/IN
BEGIN;
SET search_path TO training, public;

-- EXISTS: customers who purchased Electronics
SELECT c.*
FROM customers c
WHERE EXISTS (
  SELECT 1
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.customer_id = c.customer_id
    AND p.category = 'Electronics'
);

-- IN with correlated condition
SELECT p.product_id, p.name
FROM products p
WHERE p.product_id IN (
  SELECT DISTINCT oi.product_id
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  WHERE o.order_date >= now() - interval '30 days'
);

-- Exercises
-- 1) Customers with any order over $1000 using EXISTS.
-- 2) Products never purchased using NOT EXISTS.

ROLLBACK;
