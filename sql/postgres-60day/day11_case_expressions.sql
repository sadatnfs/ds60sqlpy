-- Day 11: CASE expressions and conditional logic
BEGIN;
SET search_path TO training, public;

-- Label orders by size
SELECT o.order_id, o.total_amount,
  CASE
    WHEN o.total_amount >= 1000 THEN 'XL'
    WHEN o.total_amount >= 300 THEN 'L'
    WHEN o.total_amount >= 100 THEN 'M'
    ELSE 'S'
  END AS order_size
FROM orders o
ORDER BY o.total_amount DESC
LIMIT 50;

-- Conditional aggregation with CASE
SELECT p.category,
  SUM(CASE WHEN o.order_date >= now() - interval '30 days' THEN oi.quantity ELSE 0 END) AS qty_30d,
  SUM(CASE WHEN o.order_date >= now() - interval '90 days' THEN oi.quantity ELSE 0 END) AS qty_90d
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY qty_30d DESC;

-- Exercises
-- 1) Segment customers into tiers by lifetime revenue using CASE.
-- 2) Create a CASE that buckets order hour into morning/afternoon/evening/night.

ROLLBACK;
