-- Day 26 solutions: CTEs with window functions
SET search_path TO training, public;

-- Exercise 1: monthly totals followed by month-over-month growth.
WITH monthly AS (
  SELECT date_trunc('month', order_date)::date AS month,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY date_trunc('month', order_date)
), compared AS (
  SELECT month,
         revenue,
         LAG(revenue) OVER (ORDER BY month) AS previous_month_revenue
  FROM monthly
)
SELECT month,
       ROUND(revenue, 2) AS revenue,
       ROUND(previous_month_revenue, 2) AS previous_month_revenue,
       ROUND(
         (revenue - previous_month_revenue)
           / NULLIF(previous_month_revenue, 0),
         4
       ) AS month_over_month_growth
FROM compared
ORDER BY month;

-- Exercise 2: each product's five highest-value order lines.
WITH product_orders AS (
  SELECT p.product_id,
         p.name,
         oi.order_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS product_order_value
  FROM products p
  JOIN order_items oi ON oi.product_id = p.product_id
  GROUP BY p.product_id, p.name, oi.order_id
), ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY product_id
           ORDER BY product_order_value DESC, order_id
         ) AS product_order_rank
  FROM product_orders
)
SELECT product_id,
       name,
       order_id,
       ROUND(product_order_value, 2) AS product_order_value,
       product_order_rank
FROM ranked
WHERE product_order_rank <= 5
ORDER BY product_id, product_order_rank;
