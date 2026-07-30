-- Day 7: Week 1 Mini-Project
-- Build a comprehensive report combining joins, aggregates, set ops
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.
-- Assumptions: Revenue means exact net line revenue unless a prompt explicitly asks for stored order totals. Every ranked output has a deterministic tie-breaker.
-- Pitfall: A polished result is not trustworthy until its grain, denominator, missing-row policy, and reconciliation are explicit.
-- Predict row grain and NULL/order behavior before executing each example.

-- Customer revenue by country and category (last 90 days)
WITH recent_orders AS (
  SELECT * FROM orders WHERE order_date >= now() - interval '90 days'
), line AS (
  SELECT ro.order_id, ro.customer_id, c.country, p.category,
         (oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_revenue
  FROM recent_orders ro
  JOIN customers c ON c.customer_id = ro.customer_id
  JOIN order_items oi ON oi.order_id = ro.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT country, category,
       ROUND(SUM(line_revenue),2) AS revenue,
       COUNT(DISTINCT customer_id) AS buyers,
       ROUND(SUM(line_revenue)/NULLIF(COUNT(DISTINCT customer_id),0),2) AS rev_per_buyer
FROM line
GROUP BY country, category
ORDER BY revenue DESC, country, category
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Build an order KPI table by status with order count, revenue, average order value, and distinct customers.
--    Hint: Aggregate orders at status grain and round only displayed monetary values.
-- 2. [Query writing] Return the 20 products with the highest net line revenue.
--    Hint: Aggregate order items by product before ranking; use product ID as tie-breaker.
-- 3. [Query writing] Create a customer summary that retains customers with no orders.
--    Hint: Left join from customers and count/order-sum nullable matches with `COALESCE` only where zero has clear meaning.
-- 4. [Debugging] Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows.
--    Hint: Aggregate each detail table to order grain first, then join the one-row-per-order relations.
-- 5. [Prediction] Build a monthly order trend and explain which months are absent rather than zero.
--    Hint: Grouping observed orders alone cannot create empty calendar months.
-- 6. [Extension] Create a compact one-row audit of customer, order, item, and payment coverage.
--    Hint: Use scalar subqueries for independent counts; this avoids accidental cross multiplication.

ROLLBACK;
