-- SQL-CONCURRENCY-01: Isolation Traces and Optimistic Concurrency
-- Guide: sql/professional/companion-guides/sql_concurrency_01_isolation_and_versions.md
-- Use Create/open guided SQL notebook and the ignored learner copy.
-- Run the complete file with psql -X -v ON_ERROR_STOP=1.
-- Only the local disposable advanced_sql_training database is permitted.
-- Setup is supplied. Write attempts before the final ROLLBACK.
BEGIN;
DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
END
$course_target$;
SET LOCAL TIME ZONE 'UTC';
SET LOCAL statement_timeout = '15s';
CREATE TEMP TABLE concurrency_stock (
  sku text PRIMARY KEY,
  available integer NOT NULL CHECK (available >= 0),
  version integer NOT NULL CHECK (version > 0)
) ON COMMIT DROP;
INSERT INTO concurrency_stock
VALUES
  ('A', 5, 1),
  ('B', 1, 1);
-- Example 1: Guard an update and inspect its result
-- Expected: One updated row, columns sku, available, version: (A,3,2). After rollback the fixture is (A,5,1).
SAVEPOINT worked_success;
UPDATE
  concurrency_stock
SET
  available = available - 2,
  version = version + 1
WHERE
  sku = 'A'
  AND version = 1
  AND available >= 2
RETURNING
  sku,
  available,
  version;
ROLLBACK TO SAVEPOINT worked_success;

RELEASE SAVEPOINT worked_success;

-- Example 2: A stale expectation does not write
-- Expected: Zero updated rows, then one inspected row (A,5,1), columns sku, available, version.
UPDATE
  concurrency_stock
SET
  available = available - 1,
  version = version + 1
WHERE
  sku = 'A'
  AND version = 99
  AND available >= 1
RETURNING
  sku,
  available,
  version;

SELECT
  sku,
  available,
  version
FROM
  concurrency_stock
WHERE
  sku = 'A';

-- Exercises
-- Keep predictions and attempts in your own working copy.
-- 1. Perform a guarded reservation.
-- Inputs/evidence: For sql-concurrency-01 Exercise 1, Inside a savepoint, reserve two A units using expected version 1 and a nonnegative-capacity predicate. Return sku, available, version, then roll back the attempt.
-- Expected result/shape: For sql-concurrency-01 Exercise 1, One updated SKU row, columns sku, available, version: (A,3,2). After savepoint rollback, A is (A,5,1). No final ORDER BY is needed for the unique sku update.
-- Verify: For sql-concurrency-01 Exercise 1, Inspect RETURNING (A,3,2), then inspect restored A state (5,1) after savepoint rollback. A successful command tag alone does not establish the version and capacity outcome.
-- Hint: Put version and capacity conditions in WHERE, not only in an earlier SELECT.
-- 2. Reject a stale expected version.
-- Inputs/evidence: For sql-concurrency-01 Exercise 2, Try reserving one A unit with expected version 99. Return sku, available, version for any successful update and inspect the row afterward.
-- Expected result/shape: For sql-concurrency-01 Exercise 2, Zero returned rows with columns sku, available, version. A remains available 5 and version 1; SQL execution itself succeeds with UPDATE 0.
-- Verify: For sql-concurrency-01 Exercise 2, Require zero RETURNING rows and unchanged A state available=5,version=1. Removing the version condition would discard the requested stale-write protection.
-- Hint: A failed precondition is an ordinary zero-row outcome.
-- 3. Reject insufficient capacity independently.
-- Inputs/evidence: For sql-concurrency-01 Exercise 3, Try reserving two B units with correct expected version 1. Return sku, available, version on success and inspect B afterward.
-- Expected result/shape: For sql-concurrency-01 Exercise 3, Zero returned rows, columns sku, available, version. B remains (B,1,1), proving the capacity condition can fail even with a current version.
-- Verify: For sql-concurrency-01 Exercise 3, Require zero RETURNING rows and unchanged B state available=1,version=1. The current version and failed capacity distinguish this outcome from the stale-version case.
-- Hint: Use a boundary that differs from the stale-version example.
-- 4. Model two callers sharing an old version.
-- Inputs/evidence: For sql-concurrency-01 Exercise 4, Inside one savepoint, apply caller One reserving two A units at version 1, then caller Two reserving one A unit with the same old version. Return caller, affected_rows from both attempts.
-- Expected result/shape: For sql-concurrency-01 Exercise 4, Two model-trace rows keyed by caller, columns caller, affected_rows; final ORDER BY caller: One affects 1, Two affects 0. A is temporarily (A,3,2), then rollback restores the fixture. This is a sequential model, not a concurrent trace.
-- Verify: For sql-concurrency-01 Exercise 4, Inspect trace One=1 affected row and Two=0, plus temporary A state (3,2). Rollback restores (5,1). Label the result a sequential model rather than a concurrent execution trace.
-- Hint: Execute the two writes in distinct statements and save their actual returned counts.
-- 5. Verify a no-change read result.
-- Inputs/evidence: For sql-concurrency-01 Exercise 5, Return sku, available, version for both initial stock rows, ordered by sku. State what a single-session read proves and what a two-session isolation claim additionally needs.
-- Expected result/shape: For sql-concurrency-01 Exercise 5, Two SKU rows, columns sku, available, version; final ORDER BY sku: (A,5,1),(B,1,1). A genuine isolation trace also needs session names, isolation level, ordered statements, commit boundary, and observations.
-- Verify: For sql-concurrency-01 Exercise 5, Inspect initial rows (A,5,1),(B,1,1). A separate isolation claim requires actual A-session reads, B-session write/commit order, and the selected isolation level from the optional lab.
-- Hint: The SELECT verifies current fixture state, not the visibility of another transaction.
-- 6. Transfer the guard to an atomic replenishment.
-- Inputs/evidence: For sql-concurrency-01 Exercise 6, Inside a savepoint, add three B units using expected version 1, increment version, and return sku, available, version. Then retry the same old expectation and prove it affects zero rows.
-- Expected result/shape: For sql-concurrency-01 Exercise 6, One initial updated SKU row, columns sku, available, version: (B,4,2). A second attempt using version 1 returns zero rows. Rollback leaves B at (B,1,1).
-- Verify: For sql-concurrency-01 Exercise 6, Inspect initial RETURNING (B,4,2), then require zero rows for repeating old version 1, and inspect restored (B,1,1) after rollback. This tests stale-write protection, not unknown-commit recovery.
-- Hint: Every mutation path must advance the same version contract, including replenishment.
ROLLBACK;
