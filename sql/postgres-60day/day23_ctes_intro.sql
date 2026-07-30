-- Day 23: CTEs Introduction
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability—not forced materialization—is the default goal.
-- Assumptions: Each CTE declares its output grain. PostgreSQL 16 may inline a side-effect-free single-use CTE unless `MATERIALIZED` is requested.
-- Pitfall: A CTE does not automatically improve performance; duplicated rows or ambiguous names remain logical bugs even when split into stages.
-- Predict row grain and NULL/order behavior before executing each example.

-- Rewrite subqueries as CTEs
WITH order_lines AS (
  SELECT o.order_id,
         o.customer_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id
), top_customers AS (
  SELECT customer_id,
         SUM(order_total) AS lifetime_revenue
  FROM order_lines
  GROUP BY customer_id
)
SELECT tc.customer_id, tc.lifetime_revenue
FROM top_customers tc
ORDER BY lifetime_revenue DESC, tc.customer_id
LIMIT 20;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Build order-level net value in one CTE and summarize it by customer in the outer query.
--    Hint: Name the one-row-per-order grain before changing to customer grain.
-- 2. [Query writing] Use one category-revenue CTE twice to return the highest category and total revenue.
--    Hint: A named aggregate can support multiple scalar reads without repeating the business formula.
-- 3. [Query writing] Create staged payment reconciliation CTEs at order grain.
--    Hint: Aggregate payment detail before joining to orders and preserve unpaid orders with a left join.
-- 4. [Prediction] Compare `MATERIALIZED` and `NOT MATERIALIZED` syntax on a side-effect-free filtered order CTE without claiming one is universally faster.
--    Hint: Both return the same rows; planning effects require `EXPLAIN` evidence in a representative environment.
-- 5. [Debugging] Repair a multi-stage query whose repeated `total` column names are ambiguous by assigning grain-specific aliases.
--    Hint: Name measures `order_value`, `customer_revenue`, and similar rather than carrying generic `total`.
-- 6. [Extension] Use a data-modifying CTE to demonstrate an update and inspect its returned rows without persistence.
--    Hint: The outer lesson transaction rolls back; the CTE exposes changed rows as a relation.

ROLLBACK;
