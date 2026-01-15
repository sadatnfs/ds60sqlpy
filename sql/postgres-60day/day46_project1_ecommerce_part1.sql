-- Day 46: Project 1 - E-commerce Analytics (Part 1)
-- Topics: Customer segmentation by lifetime value, cohort setup
BEGIN;
SET search_path TO training, public;

-- Lifetime Value (LTV)
WITH order_values AS (
  SELECT o.customer_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, o.order_id
), ltv AS (
  SELECT customer_id, ROUND(SUM(order_value),2) AS ltv
  FROM order_values
  GROUP BY customer_id
)
SELECT c.customer_id, c.country, c.segment, l.ltv,
       NTILE(4) OVER (ORDER BY l.ltv DESC) AS ltv_quartile
FROM customers c
JOIN ltv l ON l.customer_id = c.customer_id
ORDER BY l.ltv DESC
LIMIT 100;

-- Cohort setup by signup month
SELECT date_trunc('month', created_at)::date AS cohort_month,
       COUNT(*) AS new_customers
FROM customers
GROUP BY 1
ORDER BY cohort_month DESC;

-- Exercises
-- 1) Create LTV segments (gold/silver/bronze) based on thresholds and analyze by country.
-- 2) Compute revenue per cohort month at month offsets 0..12.

ROLLBACK;
