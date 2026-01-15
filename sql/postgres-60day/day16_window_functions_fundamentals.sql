-- Day 16: Window Functions Fundamentals
-- OVER(), PARTITION BY, ORDER BY, frames
BEGIN;
SET search_path TO training, public;

-- Convert GROUP BY to window function: revenue per category and share
WITH line AS (
  SELECT p.category,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
)
SELECT category,
       ROUND(SUM(revenue) OVER (PARTITION BY category),2) AS category_revenue,
       ROUND(SUM(revenue) OVER (),2) AS total_revenue,
       ROUND(SUM(revenue) OVER (PARTITION BY category)
             / NULLIF(SUM(revenue) OVER (),0), 4) AS category_share
FROM line
GROUP BY category
ORDER BY category_revenue DESC;

-- Row-wise metrics without collapsing rows
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       o.total_amount,
       ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id),2) AS avg_customer_order,
       COUNT(*) OVER (PARTITION BY o.customer_id) AS orders_per_customer
FROM orders o
ORDER BY o.customer_id, o.order_date
LIMIT 100;

-- Frame example (default = RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
WITH daily AS (
  SELECT date_trunc('day', o.order_date) AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT d,
       revenue,
       SUM(revenue) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7d
FROM daily
ORDER BY d DESC
LIMIT 30;

-- Exercises
-- 1) Compute each customer's order total and the customer's lifetime total alongside each order.
-- 2) For each category, show each product's revenue and its share of category revenue.

ROLLBACK;
