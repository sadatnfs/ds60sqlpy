-- Day 19: Running Aggregates with Window Functions
BEGIN;
SET search_path TO training, public;

-- Running total per customer by order date
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount,
       SUM(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM orders o
ORDER BY o.customer_id, o.order_date
LIMIT 200;

-- Moving average revenue per day (7-day)
WITH daily AS (
  SELECT date_trunc('day', order_date) AS d,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY 1
)
SELECT d,
       revenue,
       ROUND(AVG(revenue) OVER (
         ORDER BY d
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ),2) AS ma7
FROM daily
ORDER BY d DESC
LIMIT 40;

-- Exercises
-- 1) Compute a 30-day moving sum and average for revenue.
-- 2) For each category, compute cumulative quantity sold by product order date.

ROLLBACK;
