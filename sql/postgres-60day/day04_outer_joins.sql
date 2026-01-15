-- Day 4: LEFT/RIGHT/FULL OUTER JOINs and NULL handling
BEGIN;
SET search_path TO training, public;

-- LEFT JOIN: customers without orders
SELECT c.customer_id, c.full_name, COUNT(o.order_id) AS orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY orders ASC, c.customer_id
LIMIT 25;

-- RIGHT JOIN: products that appear in orders (or not)
SELECT p.product_id, p.name, COALESCE(SUM(oi.quantity),0) AS sold_qty
FROM order_items oi
RIGHT JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY sold_qty ASC, p.product_id
LIMIT 25;

-- FULL OUTER JOIN: payments vs orders
SELECT o.order_id, o.total_amount, p.amount AS payment_amount
FROM orders o
FULL OUTER JOIN payments p ON p.order_id = o.order_id
WHERE o.order_id IS NULL OR p.order_id IS NULL; -- mismatches

-- Exercises
-- 1) Identify orders with no payments and payments without orders.
-- 2) Find products never purchased.
-- 3) Customers with no orders in last 90 days.

ROLLBACK;
