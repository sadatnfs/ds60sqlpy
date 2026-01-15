-- Day 30 - Solutions: Phase 2 Project — Windows, CTEs, Pivoting
-- Assumes: orders, order_items, customers, products

/*
CTE staging of order lines → monthly/category aggregates → windowed KPIs (rolling, shares) → pivot to presentation shape.
*/
WITH order_lines AS (
  SELECT oi.order_id,
         oi.product_id,
         (oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_rev
  FROM order_items oi
), monthly_cat AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS month,
         p.category,
         SUM(ol.line_rev) AS revenue,
         COUNT(DISTINCT o.order_id) AS orders
  FROM orders o
  JOIN order_lines ol ON ol.order_id = o.order_id
  JOIN products p ON p.product_id = ol.product_id
  GROUP BY DATE_TRUNC('month', o.order_date), p.category
), windowed AS (
  SELECT month,
         category,
         revenue,
         orders,
         ROUND(AVG(revenue) OVER (PARTITION BY category ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS ma3,
         ROUND(revenue / NULLIF(SUM(revenue) OVER (PARTITION BY month),0), 4) AS share_in_month
  FROM monthly_cat
)
SELECT month,
       category,
       revenue,
       orders,
       ma3,
       share_in_month
FROM windowed
ORDER BY month DESC, revenue DESC
LIMIT 500;

-- End of Day 30 solutions
