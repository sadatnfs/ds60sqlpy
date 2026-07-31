-- Day 39: Locks & Deadlock Prevention
-- BEGINNER WORKFLOW — sql-39: Locks Deadlocks
-- Guide: sql/postgres-60day/companion-guides/day39_locks_deadlocks.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-39/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Observe locks (requires access to pg_catalog)
SELECT pid, locktype, relation::regclass, mode, granted
FROM pg_locks
LEFT JOIN pg_class ON pg_locks.relation = pg_class.oid
ORDER BY granted DESC, relation;

-- Row-level locking for concurrent updates
-- Session A:
--   BEGIN; SELECT * FROM orders WHERE order_id = 1 FOR UPDATE;
-- Session B:
--   BEGIN; SELECT * FROM orders WHERE order_id = 1 FOR UPDATE; -- will wait
-- Deadlock demo (do NOT run in prod):
--   A locks row X then tries row Y; B locks row Y then tries row X -> deadlock

-- Correct lock ordering strategy: always lock rows in a consistent order
WITH to_lock AS (
  SELECT order_id FROM orders WHERE total_amount > 900 ORDER BY order_id LIMIT 5
)
SELECT * FROM orders o
JOIN to_lock t ON t.order_id = o.order_id
FOR UPDATE; -- consistent order prevents deadlocks

-- Explicit advisory locks (application-level)
-- SELECT pg_try_advisory_lock(42);  -- returns boolean
-- SELECT pg_advisory_unlock(42);

-- Exercises
-- 1. Simulate a deadlock in two sessions and capture with pg_locks.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Implement consistent lock ordering to avoid the deadlock.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Use SELECT FOR UPDATE SKIP LOCKED for job-queue style processing.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 4. Prediction: compare FOR UPDATE NOWAIT with ordinary FOR UPDATE when
--    another session already owns the row lock.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 5. Construction: claim at most five queued rows with FOR UPDATE SKIP LOCKED,
--    update them, and return exactly the rows claimed.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 6. Debugging: identify why ordering inside a CTE is not enough unless the
--    locking SELECT preserves that same deterministic key order.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 7. Edge case: use pg_try_advisory_xact_lock and explain why transaction-level
--    advisory locks avoid a forgotten manual unlock.
--    Inputs: Use only the declared lesson objects (orders) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
