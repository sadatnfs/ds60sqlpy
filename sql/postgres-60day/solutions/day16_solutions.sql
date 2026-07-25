-- Day 16 solutions: window-function fundamentals
SET search_path TO training, public;

-- Exercise 1: each order beside its customer's lifetime total.
SELECT customer_id,
       order_id,
       order_date,
       total_amount AS order_total,
       ROUND(SUM(total_amount) OVER (PARTITION BY customer_id), 2)
         AS customer_lifetime_total,
       ROUND(
         total_amount
           / NULLIF(SUM(total_amount) OVER (PARTITION BY customer_id), 0),
         4
       ) AS order_share_of_lifetime
FROM orders
ORDER BY customer_id, order_date, order_id;

-- Exercise 2: product revenue and share of category revenue.
WITH product_revenue AS (
  SELECT p.category,
         p.product_id,
         p.name,
         COALESCE(
           SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),
           0
         ) AS revenue
  FROM products p
  LEFT JOIN order_items oi USING (product_id)
  GROUP BY p.category, p.product_id, p.name
)
SELECT category,
       product_id,
       name,
       ROUND(revenue, 2) AS product_revenue,
       ROUND(SUM(revenue) OVER (PARTITION BY category), 2) AS category_revenue,
       ROUND(
         revenue / NULLIF(SUM(revenue) OVER (PARTITION BY category), 0),
         4
       ) AS category_revenue_share
FROM product_revenue
ORDER BY category, product_revenue DESC, product_id;
