-- Day 45: Phase 3 Project - Performance Optimization
BEGIN;
SET search_path TO training, public;

-- Baseline (intentionally suboptimal):
EXPLAIN ANALYZE
SELECT c.country, SUM(oi.quantity)
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE date_trunc('day', o.order_date) >= date_trunc('day', now() - interval '180 days')
GROUP BY c.country
ORDER BY 2 DESC;

-- Optimized rewrite: avoid function on column and add helpful index
CREATE INDEX IF NOT EXISTS idx_orders_order_date_only ON orders(order_date);
EXPLAIN ANALYZE
SELECT c.country, SUM(oi.quantity)
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_date >= (date_trunc('day', now()) - interval '180 days')
GROUP BY c.country
ORDER BY 2 DESC;

-- Additional optimization: pre-aggregate items by order to reduce rows early
EXPLAIN ANALYZE
WITH items AS (
  SELECT order_id, SUM(quantity) AS qty
  FROM order_items
  GROUP BY order_id
)
SELECT c.country, SUM(i.qty)
FROM orders o
JOIN items i ON i.order_id = o.order_id
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.order_date >= (date_trunc('day', now()) - interval '180 days')
GROUP BY c.country
ORDER BY 2 DESC;

-- Target: Reduce runtime by >70% vs baseline on your dataset
-- The percentage is a measurement goal, never a guaranteed result on the small
-- deterministic seed. Record plan shape, rows, buffers, and execution time.

-- Exercises
-- 1. Prediction: identify which baseline expression is non-sargable and predict
--    how the half-open timestamp range changes index eligibility.
-- 2. Construction: capture EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) for the
--    baseline and rewrite, then compare root-node execution time and buffers.
-- 3. Debugging: prove that the pre-aggregated rewrite returns the same country
--    totals as the direct join by comparing them with EXCEPT in both directions.
-- 4. Edge case: test a date window with zero matching orders and ensure every
--    rewrite returns the same empty result rather than an invented zero row.
-- 5. Design: propose one composite or covering index, state the exact query it
--    serves, and explain its write/storage tradeoff.
-- 6. Explanation: write a short optimization report separating semantic
--    equivalence, planner evidence, and environment-dependent timing.

ROLLBACK;
