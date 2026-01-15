-- Day 13: Date/Time functions
BEGIN;
SET search_path TO training, public;

-- Age of customer in system
SELECT customer_id, full_name,
       now() - created_at AS tenure,
       date_trunc('month', created_at) AS cohort_month
FROM customers
ORDER BY tenure DESC
LIMIT 50;

-- Rolling 7-day revenue
WITH daily AS (
  SELECT date_trunc('day', o.order_date) AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY d
)
SELECT d, revenue,
       SUM(revenue) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rev_7d
FROM daily
ORDER BY d DESC
LIMIT 30;

-- Exercises
-- 1) Compute fiscal quarter for each order.
-- 2) Calculate days since last order per customer.

ROLLBACK;
