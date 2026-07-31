-- Day 31: Query Execution Plans (EXPLAIN/ANALYZE)
-- BEGINNER WORKFLOW — sql-31: Explain Analyze
-- Guide: sql/postgres-60day/companion-guides/day31_explain_analyze.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-31/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers, order_items.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Baseline query
EXPLAIN SELECT o.order_id, o.total_amount FROM orders o WHERE o.total_amount > 500;
EXPLAIN ANALYZE SELECT o.order_id, o.total_amount FROM orders o WHERE o.total_amount > 500 LIMIT 100;

-- Join with filter
EXPLAIN
SELECT c.country, SUM(oi.quantity) AS qty
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_date >= now() - interval '90 days'
GROUP BY c.country
ORDER BY qty DESC;

-- Using an index candidate (to be added on Day 32) and compare
-- Rerun EXPLAIN after creating indexes in Day 32 to observe plan changes.

-- Exercises
-- 1. Add WHERE predicates and observe selectivity effects.
--    Inputs: For sql-31 Exercise 1, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-31 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`, and `total_amount`.
--    Verify: For sql-31 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-31 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 2. Compare EXPLAIN vs EXPLAIN ANALYZE outputs; note actual vs estimated rows.
--    Inputs: For sql-31 Exercise 2, run the underlying read-only query over `orders`, `customers`, and `order_items` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-31 Exercise 2, expected output: one row per `country`. The final columns are `country`, and `units`.
--    Verify: For sql-31 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `country` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-31 Exercise 2, start with the first relation in `orders`, `customers`, and `order_items`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
-- 3. Prediction: before running it, decide whether total_amount > 0 or
--    total_amount > 900 should produce the smaller row estimate. Run both with
--    EXPLAIN (ANALYZE, BUFFERS) and record estimated rows, actual rows, and
--    shared buffer hits.
--    Inputs: For sql-31 Exercise 3, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-31 Exercise 3, expected output: one row per `order_id`. The final columns are `order_id`.
--    Verify: For sql-31 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-31 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 4. Construction: explain a customer -> orders join filtered to one country.
--    Include VERBOSE and identify the scan node, join node, and aggregate node.
--    Inputs: For sql-31 Exercise 4, run the underlying read-only query over `customers`, and `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-31 Exercise 4, expected output: one row per `country`. The final columns are `country`, and `order_count`.
--    Verify: For sql-31 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `country` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-31 Exercise 4, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
-- 5. Debugging: explain why EXPLAIN ANALYZE is unsafe around an UPDATE you do
--    not intend to execute. Demonstrate safely by wrapping a no-op UPDATE
--    (SET status = status) in a savepoint and rolling back to it.
--    Inputs: For sql-31 Exercise 5, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-31 Exercise 5, expected output: one row per `order_id`. The final columns are `update`, and `analyze`.
--    Verify: For sql-31 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-31 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 6. Edge case: find one predicate that returns zero rows. Compare the estimate
--    with the actual count and write one sentence about stale statistics versus
--    data that is merely rare.
--    Inputs: For sql-31 Exercise 6, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-31 Exercise 6, expected output: one row per `order_id`. The final columns are `order_id`.
--    Verify: For sql-31 Exercise 6, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-31 Exercise 6, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.

ROLLBACK;
