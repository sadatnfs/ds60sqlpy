-- Day 41: Complex Aggregations (FILTER, conditional metrics, string aggregation)
BEGIN;
SET search_path TO training, public;

-- Multiple metrics with FILTER
SELECT p.category,
       SUM(oi.quantity)                                                   AS total_qty,
       SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '30 days') AS qty_30d,
       SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '90 days') AS qty_90d,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),2)           AS revenue,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount))
             FILTER (WHERE o.order_date >= now() - interval '30 days'),2) AS revenue_30d
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o   ON o.order_id = oi.order_id
GROUP BY p.category
ORDER BY revenue DESC;

-- Conditional aggregation using CASE for multi-metric report
SELECT c.country,
       SUM(CASE WHEN o.status IN ('paid','shipped','delivered') THEN 1 ELSE 0 END) AS successful_orders,
       SUM(CASE WHEN o.status = 'returned' THEN 1 ELSE 0 END)                      AS returned_orders,
       ROUND(SUM(CASE WHEN o.status <> 'returned' THEN o.total_amount ELSE 0 END),2) AS net_revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY net_revenue DESC;

-- String aggregation for labels
SELECT p.category,
       string_agg(DISTINCT p.name, ', ' ORDER BY p.name) AS sample_products
FROM products p
GROUP BY p.category
ORDER BY p.category
LIMIT 10;

-- Exercises
-- 1) Build a 6-metric dashboard by category using FILTER for various time windows.
-- 2) Create a per-country string_agg of top 5 product names by revenue.

ROLLBACK;
