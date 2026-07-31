-- Day 34: Query Optimization Techniques
-- BEGINNER WORKFLOW — sql-34: Query Optimization
-- Guide: sql/postgres-60day/companion-guides/day34_query_optimization.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-34/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Predicate pushdown by filtering early in CTE
WITH filtered_orders AS (
  SELECT order_id, customer_id FROM orders WHERE order_date >= now() - interval '30 days'
)
SELECT c.country, COUNT(*)
FROM filtered_orders fo
JOIN customers c ON c.customer_id = fo.customer_id
GROUP BY c.country
ORDER BY COUNT(*) DESC;

-- Avoid SELECT * and unnecessary columns to reduce I/O
EXPLAIN ANALYZE
SELECT o.order_id, o.customer_id
FROM orders o
WHERE o.order_date >= now() - interval '7 days';

-- Join order rewrite (ensure correct join conditions, indexes)
EXPLAIN
SELECT p.category, SUM(oi.quantity) AS qty
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.status IN ('paid','shipped','delivered')
GROUP BY p.category;

-- Exercises
-- 1. Replace subqueries with joins and compare plans.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 2. Limit rows as early as possible and compare performance.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 3. Prediction: compare a MATERIALIZED CTE with NOT MATERIALIZED for a recent
--    orders query. Predict which version permits more planner reordering.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: pre-aggregate order_items to one row per order before
--    joining orders and customers; verify that totals match the direct join.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: repair a query that joins orders and payments before
--    order_items and therefore multiplies both payment and line-item amounts.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: replace NOT IN with NOT EXISTS for an anti-join and explain how
--    a NULL in the subquery changes NOT IN semantics.
--    Inputs: Use only the declared lesson objects (orders, customers, order_items, products) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
