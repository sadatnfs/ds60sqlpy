-- Day 19: Running Aggregates with Window Functions
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Define cumulative and moving window frames explicitly so peers, boundaries, and partition resets match the business question.
-- Assumptions: Ordered money windows use exact numeric. `ROWS` counts physical ordered rows; `RANGE` groups peers with equal ordering values.
-- Pitfall: Relying on the default frame can include tied peers unexpectedly; a moving-row window is not automatically a moving-time window.
-- Predict row grain and NULL/order behavior before executing each example.

-- Running total per customer by order date
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount,
       SUM(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 200;

-- Moving average across seven observed UTC dates. Densify the calendar first
-- if the business meaning requires exactly seven consecutive calendar dates.
WITH daily AS (
  SELECT (order_date AT TIME ZONE 'UTC')::date AS d_utc,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY d_utc
)
SELECT d_utc,
       revenue,
       ROUND(AVG(revenue) OVER (
         ORDER BY d_utc
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ),2) AS ma7
FROM daily
ORDER BY d_utc DESC
LIMIT 40;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate cumulative stored revenue across all orders.
--    Hint: Order by timestamp and unique ID; declare `ROWS ... CURRENT ROW`.
-- 2. [Query writing] Calculate each customer's cumulative stored spend.
--    Hint: Partition by customer and reset the explicit row frame for every customer.
-- 3. [Query writing] Calculate a trailing seven-order average within each customer.
--    Hint: A seven-row frame is based on observations, not seven calendar days.
-- 4. [Prediction] Compare `ROWS` and `RANGE` cumulative sums when two rows share the same ordering value.
--    Hint: `RANGE` includes ordering peers together; `ROWS` advances one physical row at a time.
-- 5. [Debugging] Reset a running expense total at each category and month.
--    Hint: Partition by both reset keys and order by date plus expense ID.
-- 6. [Extension] Prove the final cumulative stored revenue equals the ordinary stored-revenue sum.
--    Hint: Select the last ordered cumulative value and compare it with an independent aggregate.

ROLLBACK;
