-- Day 26 - Solutions: CTEs with Window Functions (Layered Analytics)
-- Assumes: orders, order_items, products, customers

/*
Exercise 1) Build a CTE daily_revenue(day, category, rev), then compute 7‑day moving averages by category.
Why: Pre-aggregate to daily×category grain; use ROWS frames for exact window sizes.
*/
WITH daily AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS rev
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY DATE_TRUNC('day', o.order_date), p.category
)
SELECT d,
       category,
       rev,
       ROUND(AVG(rev) OVER (PARTITION BY category ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS ma7
FROM daily
ORDER BY d DESC, category
LIMIT 300;

/*
Exercise 2) Compute each category’s share of monthly revenue and the global cumulative monthly revenue.
Why: Windowed sums provide denominators and cumulative totals across aggregated rows.
*/
WITH monthly AS (
  SELECT DATE_TRUNC('month', o.order_date)::date AS m,
         p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS rev
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY DATE_TRUNC('month', o.order_date), p.category
)
SELECT m,
       category,
       ROUND(rev,2) AS rev,
       ROUND(rev / NULLIF(SUM(rev) OVER (PARTITION BY m),0), 4) AS share_in_month,
       ROUND(SUM(rev) OVER (ORDER BY m ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS global_cum_rev
FROM monthly
ORDER BY m DESC, rev DESC
LIMIT 300;
