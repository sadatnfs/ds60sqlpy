-- Day 45: Phase 3 Project - Performance Optimization
-- BEGINNER WORKFLOW — sql-45: Phase3 Optimization Project
-- Guide: sql/postgres-60day/companion-guides/day45_phase3_optimization_project.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-45/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, orders, order_items.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
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
--    Inputs: For sql-45 Exercise 1, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-45 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`.
--    Verify: For sql-45 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-45 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 2. Construction: capture EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) for the
--    baseline and rewrite, then compare root-node execution time and buffers.
--    Inputs: For sql-45 Exercise 2, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-45 Exercise 2, expected output: one row per `customer_id`. The final columns are `customer_id`, and `revenue`.
--    Verify: For sql-45 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-45 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.
-- 3. Debugging: prove that the pre-aggregated rewrite returns the same country
--    totals as the direct join by comparing them with EXCEPT in both directions.
--    Inputs: For sql-45 Exercise 3, read from `orders`, `customers`, and `order_items`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-45 Exercise 3, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
--    Verify: For sql-45 Exercise 3, project `order_id` plus the raw source columns from `orders`, `customers`, and `order_items` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-45 Exercise 3, run `direct`, `items`, and `preaggregated` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 4. Edge case: test a date window with zero matching orders and ensure every
--    rewrite returns the same empty result rather than an invented zero row.
--    Inputs: For sql-45 Exercise 4, read from `orders`. Build the answer toward `impossible_window_rows`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-45 Exercise 4, expected output: one row per `order_id`. The final columns are `impossible_window_rows`.
--    Verify: For sql-45 Exercise 4, run an anti-check that counts rows where NOT ((order_date >= timestamptz '1900-01-01 00:00:00+00' AND order_date < timestamptz '1900-01-02 00:00:00+00')); require unique `order_id` where the expected grain is one row per key and confirm the projected `impossible_window_rows` against `orders`. Insert rows immediately before, exactly at, and immediately after `order_date >= timestamptz '1900-01-01 00:00:00+00'`, and `order_date < timestamptz '1900-01-02 00:00:00+00'`; identify which rows pass each inclusive or exclusive comparison.
--    Hint ladder, rung 1: For sql-45 Exercise 4, inspect the source keys that survive `WHERE`.
-- 5. Design: propose one composite or covering index, state the exact query it
--    serves, and explain its write/storage tradeoff.
--    Inputs: For sql-45 Exercise 5, read from `pg_indexes`. Build the answer toward `indexname`, and `indexdef`; keep `indexname` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-45 Exercise 5, expected output: one row per `indexname`. The final columns are `indexname`, and `indexdef`. The final order is `indexname`.
--    Verify: For sql-45 Exercise 5, run an anti-check that counts rows where NOT ((schemaname = 'training' AND indexname LIKE '%solution')); require unique `indexname` where the expected grain is one row per key and confirm the projected `indexname`, and `indexdef` against `pg_indexes`. Add one row for which `(schemaname = 'training' AND indexname LIKE '%solution')` is true and one for which it is false; verify only the matching `indexname` value is returned.
--    Hint ladder, rung 1: For sql-45 Exercise 5, inspect the source keys that survive `WHERE`; then check `indexname` before applying the row cap.
-- 6. Explanation: write a short optimization report separating semantic
--    equivalence, planner evidence, and environment-dependent timing.
--    Inputs: For sql-45 Exercise 6, complete the write an optimization report separating semantics plans and  written analysis and support its claims with read-only evidence from `customers`, `orders`, and `order_items`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-45 Exercise 6, expected output: a completed the write an optimization report separating semantics plans and  written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
--    Verify: For sql-45 Exercise 6, check the write an optimization report separating semantics plans and  written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-45 Exercise 6, check the write an optimization report separating semantics plans and  written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.

ROLLBACK;
