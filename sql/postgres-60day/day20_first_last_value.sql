-- Day 20: FIRST_VALUE and LAST_VALUE
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.
-- Assumptions: First/last refer to ordered rows, not minimum/maximum values unless ordering states that. Ties need unique keys for deterministic row identity.
-- Pitfall: The default `LAST_VALUE` frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.
-- Predict row grain and NULL/order behavior before executing each example.

-- First and last order amount per customer
SELECT o.customer_id,
       o.order_id,
       o.order_date,
       o.total_amount,
       FIRST_VALUE(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS first_order_amount,
       LAST_VALUE(o.total_amount) OVER (
         PARTITION BY o.customer_id
         ORDER BY o.order_date, o.order_id
         ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
       ) AS last_order_amount
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 100;

-- Compare current to first/last
WITH per_cust AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         o.total_amount,
         FIRST_VALUE(o.total_amount) OVER (
           PARTITION BY o.customer_id
           ORDER BY o.order_date, o.order_id
           ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
         ) AS first_amt
  FROM orders o
)
SELECT *, ROUND(total_amount - first_amt, 2) AS delta_from_first
FROM per_cust
ORDER BY customer_id, order_date, order_id
LIMIT 100;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Show every order with the customer's first and last order timestamps.
--    Hint: Use one full-partition frame from unbounded preceding through unbounded following.
-- 2. [Query writing] Show each product with the cheapest and most expensive price in its category.
--    Hint: Order by price and use a full frame; values tie without needing row identity.
-- 3. [Query writing] Compare every payment with the first and last payment amount for its order.
--    Hint: Partition by order, order by timestamp/payment ID, and keep the full frame.
-- 4. [Prediction] Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.
--    Hint: The default ends at the current row; explicit following reaches the true last row.
-- 5. [Debugging] Return one first and one last order per customer without using window output as an accidental duplicate report.
--    Hint: Compute first/last IDs with full-frame windows, then select distinct customer-level output.
-- 6. [Extension] Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.
--    Hint: `DISTINCT ON` keeps the first row under its mandatory leading order keys.

ROLLBACK;
