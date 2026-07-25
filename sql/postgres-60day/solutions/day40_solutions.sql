-- Day 40 solutions: advanced analytics
SET search_path TO training, public;

-- Exercise 1: trailing 15-observation z-score for daily revenue.
WITH daily AS (
  SELECT order_date::date AS day,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY order_date::date
), stats AS (
  SELECT day,
         revenue,
         AVG(revenue) OVER (
           ORDER BY day ROWS BETWEEN 14 PRECEDING AND CURRENT ROW
         ) AS avg15,
         STDDEV_SAMP(revenue) OVER (
           ORDER BY day ROWS BETWEEN 14 PRECEDING AND CURRENT ROW
         ) AS sd15
  FROM daily
)
SELECT day,
       ROUND(revenue, 2) AS revenue,
       ROUND(avg15, 2) AS avg15,
       ROUND(sd15, 2) AS sd15,
       ROUND(((revenue - avg15) / NULLIF(sd15, 0))::numeric, 3) AS z_score
FROM stats
ORDER BY day DESC;

-- Exercise 2: category-level distribution of order value attributable to it.
WITH category_orders AS (
  SELECT p.category,
         oi.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS category_order_total
  FROM order_items oi
  JOIN products p USING (product_id)
  GROUP BY p.category, oi.order_id
)
SELECT category,
       ROUND(
         percentile_cont(0.50) WITHIN GROUP (ORDER BY category_order_total)::numeric,
         2
       ) AS p50_order_total,
       ROUND(
         percentile_cont(0.90) WITHIN GROUP (ORDER BY category_order_total)::numeric,
         2
       ) AS p90_order_total
FROM category_orders
GROUP BY category
ORDER BY category;
