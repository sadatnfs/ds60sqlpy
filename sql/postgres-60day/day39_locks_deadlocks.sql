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
--    Inputs: For sql-39 Exercise 1, read the target keys from `orders`, and `pg_locks` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-39 Exercise 1, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`.
--    Verify: For sql-39 Exercise 1, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `pg_locks` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
--    Hint ladder, rung 1: For sql-39 Exercise 1, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `pg_locks` again and prove rollback or idempotent retry.
-- 2. Implement consistent lock ordering to avoid the deadlock.
--    Inputs: For sql-39 Exercise 2, read the target keys from `orders` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-39 Exercise 2, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`, and `total_amount`. The final order is `order_id FOR UPDATE`.
--    Verify: For sql-39 Exercise 2, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
--    Hint ladder, rung 1: For sql-39 Exercise 2, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders` again and prove rollback or idempotent retry.
-- 3. Use SELECT FOR UPDATE SKIP LOCKED for job-queue style processing.
--    Inputs: For sql-39 Exercise 3, read the target keys from `orders`, and `SKIP` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-39 Exercise 3, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`, `order_date`, and `status`. The final order is `order_id`.
--    Verify: For sql-39 Exercise 3, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `SKIP` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
--    Hint ladder, rung 1: For sql-39 Exercise 3, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `SKIP` again and prove rollback or idempotent retry.
-- 4. Prediction: compare FOR UPDATE NOWAIT with ordinary FOR UPDATE when
--    another session already owns the row lock.
--    Inputs: For sql-39 Exercise 4, run the underlying read-only query over `orders`, and `NOWAIT` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-39 Exercise 4, expected output: one row per `order_id`. The final columns are `order_id`.
--    Verify: For sql-39 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-39 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 5. Construction: claim at most five queued rows with FOR UPDATE SKIP LOCKED,
--    update them, and return exactly the rows claimed.
--    Inputs: For sql-39 Exercise 5, read the target keys from `solution_jobs`, and `SKIP` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-39 Exercise 5, expected output: up to five unprocessed jobs with `SKIP LOCKED`; the UPDATE joins only those keys and `RETURNING` proves exactly what this worker claimed. The final columns are `returning`.
--    Verify: For sql-39 Exercise 5, materialize the intended `returning` target set first; require the command tag/`RETURNING` set to match it, then query `solution_jobs`, and `SKIP` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `returning` values in both cases.
--    Hint ladder, rung 1: For sql-39 Exercise 5, run `claimed` one at a time. Record each CTE's row count and `returning` uniqueness before the next stage uses it.
-- 6. Debugging: identify why ordering inside a CTE is not enough unless the
--    locking SELECT preserves that same deterministic key order.
--    Inputs: For sql-39 Exercise 6, read the target keys from `orders`, `ordered_keys`, and `OF` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-39 Exercise 6, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `order_id`. The final order is `o.order_id FOR UPDATE OF o`.
--    Verify: For sql-39 Exercise 6, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, `ordered_keys`, and `OF` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
--    Hint ladder, rung 1: For sql-39 Exercise 6, start with the first relation in `orders`, `ordered_keys`, and `OF`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 7. Edge case: use pg_try_advisory_xact_lock and explain why transaction-level
--    advisory locks avoid a forgotten manual unlock.
--    Inputs: For sql-39 Exercise 7, read from `pg_try_advisory_xact_lock`. Compute `ROLLBACK` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-39 Exercise 7, expected output: exactly one aggregate summary row. The final columns are `ROLLBACK`.
--    Verify: For sql-39 Exercise 7, evaluate each of `row_count` in a separate control `SELECT` over `pg_try_advisory_xact_lock`; require one final row and compare every value. Add one source row with a new `ROLLBACK`; verify the result gains exactly one row carrying that `ROLLBACK` value.
--    Hint ladder, rung 1: For sql-39 Exercise 7, select `ROLLBACK` from `pg_try_advisory_xact_lock` before adding derived columns.

ROLLBACK;
