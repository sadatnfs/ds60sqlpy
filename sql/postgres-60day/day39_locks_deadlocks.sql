-- Day 39: Locks & Deadlock Prevention
-- BEGINNER WORKFLOW - sql-39: Locks Deadlocks
-- Guide: sql/postgres-60day/companion-guides/day39_locks_deadlocks.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-39.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
SELECT
  pid,
  locktype,
  relation::regclass,
  mode,
  granted
FROM
  pg_locks
  LEFT JOIN pg_class ON pg_locks.relation = pg_class.oid
ORDER BY
  granted DESC,
  relation;

-- Row-level locking for concurrent updates
-- Session A:
--   BEGIN; SELECT * FROM orders WHERE order_id = 1 FOR UPDATE;
-- Session B:
--   BEGIN; SELECT * FROM orders WHERE order_id = 1 FOR UPDATE; -- will wait
-- Deadlock demo (do NOT run in prod):
--   A locks row X then tries row Y; B locks row Y then tries row X -> deadlock
-- Correct lock ordering strategy: every transaction locks shared rows in the
-- same key order. ORDER BY belongs in the locking SELECT itself; LockRows locks
-- rows in that order. An ORDER BY hidden inside a CTE does not control the
-- order in which an outer SELECT ... FOR UPDATE acquires its row locks.
SELECT
  o.order_id,
  o.total_amount
FROM
  orders AS o
WHERE
  o.total_amount > 900
ORDER BY
  o.order_id
LIMIT 5
FOR UPDATE;

-- Explicit advisory locks (application-level)
-- SELECT pg_try_advisory_lock(42);  -- returns boolean
-- SELECT pg_advisory_unlock(42);
-- Exercises
-- 1. Simulate a deadlock in two sessions and capture with pg_locks.
--    Inputs: For sql-39 Exercise 1, use two terminals on the seeded `training.orders` rows with `order_id` 1 and 2: Session A locks row 1 then row 2, Session B locks row 2 then row 1 (with `SELECT ... FOR UPDATE` or a no-op `UPDATE ... SET total_amount = total_amount`), and a third terminal reads `pg_locks` while a session waits.
--    Expected result/shape: For sql-39 Exercise 1, expected output: while Session A's second lock request waits, the third terminal shows one ungranted `transactionid` row (`mode = ShareLock`, `granted = false`) for Session A's `pid`; when Session B's second lock request closes the cycle, about one second later (`deadlock_timeout`) Session B fails with SQLSTATE `40P01` (`deadlock detected`) and Session A's waiting statement completes.
--    Verify: For sql-39 Exercise 1, record each session's `pg_backend_pid()`, the waiting `pid` from `pg_locks`, and the two `DETAIL` lines (`Process ... waits for ShareLock on transaction ...`); end both transactions with `ROLLBACK` and confirm that `SELECT order_id, status, total_amount FROM training.orders WHERE order_id IN (1, 2) ORDER BY order_id` returns the same values as before the experiment.
--    Hint ladder, rung 1: For sql-39 Exercise 1, keep Session A's transaction open after its first lock; the cycle forms only when each session holds one row and waits for the other.
-- 2. Implement consistent lock ordering to avoid the deadlock.
--    Inputs: For sql-39 Exercise 2, repeat the Exercise 1 schedule, but let both sessions lock `order_id` 1 and 2 in ascending order with one statement such as `SELECT order_id FROM training.orders WHERE order_id IN (1, 2) ORDER BY order_id FOR UPDATE`.
--    Expected result/shape: For sql-39 Exercise 2, expected output: Session A's locking `SELECT` returns two rows, `order_id` 1 and 2; Session B's identical statement waits instead of deadlocking and returns the same two rows after Session A ends. No session receives SQLSTATE `40P01`.
--    Verify: For sql-39 Exercise 2, while Session B waits, confirm in a third terminal that `SELECT locktype, mode FROM pg_locks WHERE NOT granted` returns exactly one row, a `transactionid` `ShareLock`; then rerun the opposite-order schedule from Exercise 1 to show that only the lock order changed.
--    Hint ladder, rung 1: For sql-39 Exercise 2, the cycle needs two sessions that each hold one key the other wants; ascending order means the second session waits for the first key and holds nothing.
-- 3. Use SELECT FOR UPDATE SKIP LOCKED for job-queue style processing.
--    Inputs: For sql-39 Exercise 3, create the temporary `solution_jobs` queue with four unprocessed jobs (`first` to `fourth`), then select the oldest two unprocessed jobs with `ORDER BY job_id FOR UPDATE SKIP LOCKED LIMIT 2`.
--    Expected result/shape: For sql-39 Exercise 3, expected output: two rows with columns `job_id` and `payload`: `(1, first)` and `(2, second)`, now locked by this transaction.
--    Verify: For sql-39 Exercise 3, recreate the queue as a committed disposable table, run the same claim in a second session while the first session still holds its locks, and confirm that the second session returns jobs `3` and `4` immediately instead of waiting; a temporary table cannot show this, because only its creating session can read it.
--    Hint ladder, rung 1: For sql-39 Exercise 3, `SKIP LOCKED` decides what to do with rows that another transaction has locked; `LIMIT` decides how many free rows one worker takes.
-- 4. Prediction: compare FOR UPDATE NOWAIT with ordinary FOR UPDATE when
--    another session already owns the row lock.
--    Inputs: For sql-39 Exercise 4, lock `order_id = 1` with `SELECT order_id FROM training.orders WHERE order_id = 1 FOR UPDATE` in Session A, then run the same statement in Session B once without and once with `NOWAIT`; the single-session script only plans the `NOWAIT` form with `EXPLAIN`.
--    Expected result/shape: For sql-39 Exercise 4, expected output: without `NOWAIT`, Session B waits until Session A ends; with `NOWAIT`, it fails at once with SQLSTATE `55P03` (`could not obtain lock on row in relation "orders"`). The script's `EXPLAIN` shows a `LockRows` node above an index scan on `orders_pkey`.
--    Verify: For sql-39 Exercise 4, record both outcomes and their SQLSTATE; then run `SET lock_timeout = '2s'` in Session B and confirm that the ordinary `FOR UPDATE` fails after about two seconds with SQLSTATE `55P03` (`canceling statement due to lock timeout`).
--    Hint ladder, rung 1: For sql-39 Exercise 4, `NOWAIT` changes only what happens when the row is already locked; the rows it would lock are the same.
-- 5. Construction: claim at most five queued rows with FOR UPDATE SKIP LOCKED,
--    update them, and return exactly the rows claimed.
--    Inputs: For sql-39 Exercise 5, claim at most five unprocessed `solution_jobs` rows in one statement: a `claimed` CTE with `ORDER BY job_id FOR UPDATE SKIP LOCKED LIMIT 5`, joined by an `UPDATE` that sets `processed_at` and returns `job_id`, `payload`, and `processed_at`.
--    Expected result/shape: For sql-39 Exercise 5, expected output: four rows, `job_id` 1 to 4 with their `payload` and a non-NULL `processed_at`, and the command tag `UPDATE 4`. Jobs 1 and 2 are not skipped even though Exercise 3 locked them, because `SKIP LOCKED` skips only rows locked by other transactions.
--    Verify: For sql-39 Exercise 5, count `SELECT COUNT(*) FROM solution_jobs WHERE processed_at IS NULL` before (`4`) and after (`0`) the claim and compare the difference with `UPDATE 4` and the four returned `job_id` values; a second claim in the same transaction returns zero rows.
--    Hint ladder, rung 1: For sql-39 Exercise 5, lock the candidate keys in the CTE, then update only the rows whose keys the CTE returned.
-- 6. Debugging: identify why ordering inside a CTE is not enough unless the
--    locking SELECT preserves that same deterministic key order.
--    Inputs: For sql-39 Exercise 6, compare a locking query whose only `ORDER BY` is inside a CTE with the repaired form that keeps `ORDER BY o.order_id` in the locking `SELECT ... FOR UPDATE OF o`, over orders with `total_amount > 900`.
--    Expected result/shape: For sql-39 Exercise 6, expected output: five rows with one column, `order_id`: `4`, `8`, `12`, `19`, and `24` on the course seed, returned and locked in ascending order.
--    Verify: For sql-39 Exercise 6, run `EXPLAIN (COSTS OFF)` on both forms: in the repaired form the rows reach `LockRows` already in `order_id` order (on PostgreSQL 17, a nested loop driven by the ordered CTE scan), while the CTE-only form has no outer `ORDER BY`, so its lock order follows whatever join method the planner picks. Confirm that `SELECT COUNT(*) FROM training.orders WHERE total_amount > 900` returns `605`, so the five-row limit is reached.
--    Hint ladder, rung 1: For sql-39 Exercise 6, ask which statement takes the locks; the sort that matters is the one directly below that statement's `LockRows` node.
-- 7. Edge case: use pg_try_advisory_xact_lock and explain why transaction-level
--    advisory locks avoid a forgotten manual unlock.
--    Inputs: For sql-39 Exercise 7, call `pg_try_advisory_xact_lock(3902)` twice inside the lesson transaction, then once from a second session while the first transaction is still open.
--    Expected result/shape: For sql-39 Exercise 7, expected output: two one-row results, `first_attempt = true` and `same_owner_attempt = true`, because the owning backend may take the same lock again; the second session's call returns `false` until the first transaction ends.
--    Verify: For sql-39 Exercise 7, while the first transaction is open, `SELECT locktype, objid, mode, granted FROM pg_locks WHERE locktype = 'advisory'` shows one row with `objid = 3902` and `ExclusiveLock`; after `ROLLBACK`, that query returns no row and the second session's call returns `true`, without any `pg_advisory_unlock`.
--    Hint ladder, rung 1: For sql-39 Exercise 7, a transaction-level advisory lock has no unlock function; the end of the transaction releases it.
ROLLBACK;
