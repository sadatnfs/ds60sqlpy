-- Day 39: Locks & Deadlock Prevention
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
-- 2. Implement consistent lock ordering to avoid the deadlock.
-- 3. Use SELECT FOR UPDATE SKIP LOCKED for job-queue style processing.
-- 4. Prediction: compare FOR UPDATE NOWAIT with ordinary FOR UPDATE when
--    another session already owns the row lock.
-- 5. Construction: claim at most five queued rows with FOR UPDATE SKIP LOCKED,
--    update them, and return exactly the rows claimed.
-- 6. Debugging: identify why ordering inside a CTE is not enough unless the
--    locking SELECT preserves that same deterministic key order.
-- 7. Edge case: use pg_try_advisory_xact_lock and explain why transaction-level
--    advisory locks avoid a forgotten manual unlock.

ROLLBACK;
