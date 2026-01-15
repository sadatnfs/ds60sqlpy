-- Day 14: Numeric functions & casting
BEGIN;
SET search_path TO training, public;

-- Rounding and casting
SELECT order_id,
       total_amount,
       round(total_amount, 0) AS rounded,
       cast(total_amount AS int) AS as_int
FROM orders
ORDER BY total_amount DESC
LIMIT 50;

-- Safe division and null handling
SELECT p.category,
       SUM(oi.quantity) AS qty,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)) / NULLIF(SUM(oi.quantity),0), 2) AS avg_price
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY avg_price DESC;

-- Exercises
-- 1) Use ceil/floor on product prices to create buckets.
-- 2) Cast attributes->>'channel' to text and group by it.

ROLLBACK;
