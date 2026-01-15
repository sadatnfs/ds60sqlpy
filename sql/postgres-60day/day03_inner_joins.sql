-- Day 3: INNER JOIN deep dive
BEGIN;
SET search_path TO training, public;

-- Example: Orders with customer and items (3-table join)
SELECT o.order_id, o.order_date, c.full_name, p.name AS product, oi.quantity, oi.unit_price
FROM orders o
JOIN customers c   ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p    ON p.product_id = oi.product_id
ORDER BY o.order_date DESC
LIMIT 50;

-- Multiple joins with filters
SELECT o.order_id, c.country, SUM(oi.quantity) AS total_items
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, c.country
ORDER BY total_items DESC
LIMIT 20;

-- Exercises
-- 1) List top 20 customers by total revenue (join orders + items).
-- 2) Show last 100 paid orders with payment method used (join payments).
-- 3) For each department, list employees and their manager names (self-join preview).

ROLLBACK;
