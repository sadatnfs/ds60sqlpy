-- Day 19 - Solutions: Running Aggregates and Moving Windows
-- Assumes: orders(order_date, total_amount)

/*
Exercise 1) Daily revenue rolling 7 and 28-day averages; plot and discuss lag.
Why: Pre-aggregate to daily grain, then use ROWS frames to get exactly the last N rows, avoiding RANGE peer expansion.
*/
WITH daily AS (
  SELECT DATE_TRUNC('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY DATE_TRUNC('day', o.order_date)
)
SELECT d,
       revenue,
       ROUND(AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING  AND CURRENT ROW), 2) AS ma7,
       ROUND(AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 27 PRECEDING AND CURRENT ROW), 2) AS ma28
FROM daily
ORDER BY d DESC
LIMIT 60;

/*
Exercise 2) Per-customer cumulative spend and count of orders.
Why: PARTITION BY customer_id, ORDER BY order_date with UNBOUNDED PRECEDING → cumulative running totals per customer.
*/
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount,
       SUM(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cum_spend,
       COUNT(*) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS cum_orders
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 300;

-- End of Day 19 solutions
