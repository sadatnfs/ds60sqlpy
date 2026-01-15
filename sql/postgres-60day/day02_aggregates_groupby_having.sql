-- Day 2: Aggregates, GROUP BY, HAVING
BEGIN;
SET search_path TO training, public;

-- Example 1: Orders per country
SELECT c.country, COUNT(*) AS customers
FROM customers c
GROUP BY c.country
ORDER BY customers DESC;

-- Example 2: Revenue by category with HAVING
SELECT p.category, ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
HAVING SUM(oi.unit_price * oi.quantity) > 10000
ORDER BY revenue DESC;

-- Example 3: Monthly orders and average order total
SELECT date_trunc('month', o.order_date) AS month,
       COUNT(*) AS orders,
       ROUND(AVG(o.total_amount),2) AS avg_order
FROM orders o
GROUP BY month
ORDER BY month DESC;

-- Exercises
-- 1) Compute total payments per method, show only methods over 1,000,000.
-- 2) For each country, average customer age in system (now - created_at).
-- 3) Top 5 categories by gross margin (SUM(price - cost) * qty).

ROLLBACK;
