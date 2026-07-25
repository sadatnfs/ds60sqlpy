-- Day 21 solutions: distribution functions
SET search_path TO training, public;

-- Exercise 1: product deciles by units sold during the last 90 days.
WITH product_units AS (
  SELECT p.product_id,
         p.name,
         p.category,
         COALESCE(
           SUM(oi.quantity) FILTER (
             WHERE o.order_date >= CURRENT_TIMESTAMP - interval '90 days'
           ),
           0
         ) AS units_90d
  FROM products p
  LEFT JOIN order_items oi ON oi.product_id = p.product_id
  LEFT JOIN orders o ON o.order_id = oi.order_id
  GROUP BY p.product_id, p.name, p.category
)
SELECT product_id,
       name,
       category,
       units_90d,
       NTILE(10) OVER (ORDER BY units_90d DESC, product_id) AS sales_decile
FROM product_units
ORDER BY sales_decile, units_90d DESC, product_id;

-- Exercise 2: each order's percentile rank within its customer.
SELECT customer_id,
       order_id,
       total_amount,
       ROUND(
         PERCENT_RANK() OVER (
           PARTITION BY customer_id
           ORDER BY total_amount
         )::numeric,
         4
       ) AS customer_percentile_rank
FROM orders
ORDER BY customer_id, total_amount, order_id;
