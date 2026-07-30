-- Day 16: Window Functions Fundamentals
-- OVER(), PARTITION BY, ORDER BY, frames
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use window functions to add partition-level context while preserving row grain, with explicit partition and ordering semantics.
-- Assumptions: Window aggregates do not collapse rows. When order matters, use a unique tie-breaker and declare the frame in later cumulative lessons.
-- Pitfall: Filtering a window result in the same query level is invalid; compute it in a subquery or CTE first.
-- Predict row grain and NULL/order behavior before executing each example.

-- Aggregate once, then use a window over the grouped result to calculate
-- the grand total without a second query.
WITH category_totals AS (
  SELECT p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category
)
SELECT category,
       ROUND(revenue, 2) AS category_revenue,
       ROUND(SUM(revenue) OVER (), 2) AS total_revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (), 0), 4) AS category_share
FROM category_totals
ORDER BY category_revenue DESC, category;

-- Row-wise metrics without collapsing rows
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       o.total_amount,
       ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id),2) AS avg_customer_order,
       COUNT(*) OVER (PARTITION BY o.customer_id) AS orders_per_customer
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
LIMIT 100;

-- Frame example. ROWS counts observed rows, not necessarily seven consecutive
-- calendar days; a dense date spine is required when empty dates matter.
WITH daily AS (
  SELECT (o.order_date AT TIME ZONE 'UTC')::date AS d_utc,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY d_utc
)
SELECT d_utc,
       revenue,
       SUM(revenue) OVER (
         ORDER BY d_utc
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS rolling_7_observed_days
FROM daily
ORDER BY d_utc DESC
LIMIT 30;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Show each order with the customer's average order total.
--    Hint: Partition by customer ID and keep one output row per order.
-- 2. [Query writing] Show each employee salary with department average, minimum, and maximum.
--    Hint: Partition all three window aggregates by department.
-- 3. [Query writing] Calculate every order's share of its customer's stored revenue.
--    Hint: Use a partition total denominator and guard it with `NULLIF`.
-- 4. [Prediction] Compare `GROUP BY customer_id` with `AVG(...) OVER (PARTITION BY customer_id)` and report their row counts.
--    Hint: Grouping collapses to one row per customer; a window preserves every order row.
-- 5. [Debugging] Return orders above their customer average without placing a window function in `WHERE`.
--    Hint: Compute the window value in a CTE, then filter the named column outside.
-- 6. [Extension] Show order count and revenue context at both customer and country levels in the same row.
--    Hint: Use different partitions for independent analytical contexts.

ROLLBACK;
