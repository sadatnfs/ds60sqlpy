-- Day 18: LAG and LEAD
BEGIN;
SET search_path TO training, public;

-- Period-over-period change per customer
WITH cust_orders AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         o.total_amount
  FROM orders o
)
SELECT customer_id,
       order_id,
       order_date,
       total_amount,
       LAG(total_amount)  OVER (PARTITION BY customer_id ORDER BY order_date) AS prev_order_amount,
       total_amount - COALESCE(LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date),0) AS delta_from_prev,
       LEAD(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS next_order_amount
FROM cust_orders
ORDER BY customer_id, order_date
LIMIT 100;

-- YoY comparison by month
WITH monthly AS (
  SELECT date_trunc('month', order_date) AS m,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY 1
)
SELECT m,
       revenue,
       LAG(revenue, 12) OVER (ORDER BY m) AS revenue_prev_year,
       ROUND((revenue - COALESCE(LAG(revenue,12) OVER (ORDER BY m),0))
            / NULLIF(LAG(revenue,12) OVER (ORDER BY m),0), 4) AS yoy_growth
FROM monthly
ORDER BY m DESC
LIMIT 36;

-- Exercises
-- 1) For each product, compute monthly sales and previous month sales with LAG.
-- 2) For each employee, show salary and next higher salary within department using LEAD.

ROLLBACK;
