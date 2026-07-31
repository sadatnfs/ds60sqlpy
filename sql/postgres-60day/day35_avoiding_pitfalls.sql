-- Day 35: Avoiding Common Performance Pitfalls
-- BEGINNER WORKFLOW — sql-35: Avoiding Pitfalls
-- Guide: sql/postgres-60day/companion-guides/day35_avoiding_pitfalls.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-35/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Pitfall: function on column prevents index usage
EXPLAIN ANALYZE SELECT * FROM orders WHERE date_trunc('day', order_date) = date_trunc('day', now());
-- Better:
EXPLAIN ANALYZE SELECT * FROM orders WHERE order_date >= date_trunc('day', now()) AND order_date < date_trunc('day', now()) + interval '1 day';

-- Pitfall: Correlated subquery per row
EXPLAIN ANALYZE
SELECT c.customer_id,
       (SELECT SUM(o.total_amount) FROM orders o WHERE o.customer_id = c.customer_id)
FROM customers c;
-- Better: pre-aggregate and join
EXPLAIN ANALYZE
WITH agg AS (
  SELECT customer_id, SUM(total_amount) AS sum_total FROM orders GROUP BY customer_id
)
SELECT c.customer_id, a.sum_total
FROM customers c LEFT JOIN agg a ON a.customer_id = c.customer_id;

-- N+1 pattern in application layer (illustrated only)
-- Prefer set-based queries over per-row queries.

-- Exercises
-- 1. Rewrite 3 queries to avoid functions on indexed columns.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Replace correlated subqueries with joins/CTEs.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Prediction: compare LIKE 'A%' with LIKE '%A%'. State which pattern can use
--    a normal B-tree text index more directly and why the leading wildcard
--    changes the search.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: replace an OFFSET-based “next page” query with keyset
--    pagination ordered by (order_date DESC, order_id DESC).
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Debugging: find and repair a join that calculates revenue after joining
--    both payments and order_items at their raw grains.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 6. Edge case: compare COUNT(*) and COUNT(email) for customers, and explain
--    why nullable inputs make the two counts intentionally different.
--    Inputs: Use only the declared lesson objects (orders, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
