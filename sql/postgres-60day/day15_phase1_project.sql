-- Day 15: Phase 1 Project - Complex Report
BEGIN;
SET search_path TO training, public;

-- Customer purchase analysis with segmentation and temporal patterns
WITH line AS (
  SELECT o.customer_id,
         date_trunc('month', o.order_date) AS month,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id, date_trunc('month', o.order_date)
),
segment AS (
  SELECT c.customer_id, COALESCE(c.segment,'standard') AS segment, c.country
  FROM customers c
)
SELECT s.segment, s.country, l.month,
       ROUND(SUM(l.revenue),2) AS revenue,
       COUNT(DISTINCT l.customer_id) AS actives,
       ROUND(SUM(l.revenue)/NULLIF(COUNT(DISTINCT l.customer_id),0),2) AS rev_per_active
FROM line l
JOIN segment s ON s.customer_id = l.customer_id
GROUP BY s.segment, s.country, l.month
ORDER BY l.month DESC, revenue DESC
LIMIT 200;

-- Deliverable: Add at least two more dimensions (e.g., payment method, category) and document insights.

ROLLBACK;
