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
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 2. Construction: capture EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) for the
--    baseline and rewrite, then compare root-node execution time and buffers.
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 3. Debugging: prove that the pre-aggregated rewrite returns the same country
--    totals as the direct join by comparing them with EXCEPT in both directions.
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 4. Edge case: test a date window with zero matching orders and ensure every
--    rewrite returns the same empty result rather than an invented zero row.
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Design: propose one composite or covering index, state the exact query it
--    serves, and explain its write/storage tradeoff.
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 6. Explanation: write a short optimization report separating semantic
--    equivalence, planner evidence, and environment-dependent timing.
--    Inputs: Use only the declared lesson objects (customers, orders, order_items) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
