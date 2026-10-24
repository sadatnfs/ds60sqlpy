-- Day 38: Transactions & ACID, Isolation Levels
-- BEGINNER WORKFLOW — sql-38: Transactions Isolation
-- Guide: sql/postgres-60day/companion-guides/day38_transactions_isolation.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-38/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: txn_demo.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Show current isolation level
SHOW TRANSACTION ISOLATION LEVEL;

-- Set per-transaction isolation level (demo)
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Demo table
CREATE TEMP TABLE txn_demo(id int PRIMARY KEY, qty int);
INSERT INTO txn_demo VALUES (1, 10), (2, 20), (3, 30);

-- Read snapshot under REPEATABLE READ
SELECT * FROM txn_demo ORDER BY id;

-- In a second session (instruction):
--   BEGIN; UPDATE txn_demo SET qty = qty + 5 WHERE id = 2; COMMIT;
-- Back here, under REPEATABLE READ snapshot, we still see old value
SELECT * FROM txn_demo WHERE id = 2;

-- Now switch to READ COMMITTED to see new row versions on each statement
-- Note: This affects only subsequent transactions; included here for demo
-- COMMIT;  -- would end current tx; but we keep everything safe and roll back at end
-- BEGIN; SET TRANSACTION ISOLATION LEVEL READ COMMITTED; SELECT * FROM txn_demo WHERE id=2;

-- Savepoint / rollback demo
SAVEPOINT sp1;
UPDATE txn_demo SET qty = qty + 100 WHERE id = 1;
SELECT * FROM txn_demo WHERE id = 1; -- shows +100 within tx
ROLLBACK TO SAVEPOINT sp1;
SELECT * FROM txn_demo WHERE id = 1; -- back to original in this tx

-- Exercises
-- 1. In two sessions, reproduce non-repeatable reads under READ COMMITTED.
--    Inputs: For sql-38 Exercise 1, read from `isolation_lab`. Build the answer toward `qty`; keep `qty` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-38 Exercise 1, expected output: one row per `qty`. The final columns are `qty`.
--    Verify: For sql-38 Exercise 1, run an anti-check that counts rows where NOT ((id = 1)); require unique `qty` where the expected grain is one row per key and confirm the projected `qty` against `isolation_lab`. Add one row for which `(id = 1)` is true and one for which it is false; verify only the matching `qty` value is returned.
--    Hint ladder, rung 1: For sql-38 Exercise 1, inspect the source keys that survive `WHERE`.
-- 2. Demonstrate phantom reads between two SELECT COUNT(*) with concurrent INSERTs.
--    Inputs: For sql-38 Exercise 2, read the target keys from `training.isolation_lab` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-38 Exercise 2, expected output: the command tag and an independently counted set of affected `affected_row_count` values. The final columns are `affected_row_count`, and `command_tag`.
--    Verify: For sql-38 Exercise 2, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `training.isolation_lab` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.
--    Hint ladder, rung 1: For sql-38 Exercise 2, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `training.isolation_lab` again and prove rollback or idempotent retry.
-- 3. Use SERIALIZABLE and observe serialization failures under contention.
--    Inputs: For sql-38 Exercise 3, read from `training.isolation_lab`. Build the answer toward `serializable`; keep `serializable` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-38 Exercise 3, expected output: one row per `serializable`. The final columns are `serializable`.
--    Verify: For sql-38 Exercise 3, run an anti-check that counts rows where NOT ((id = 1) OR (id = 2) OR (id >= 3)); require unique `serializable` where the expected grain is one row per key and confirm the projected `serializable` against `training.isolation_lab`. Add one row for which `(id = 1) OR (id = 2) OR (id >= 3)` is true and one for which it is false; verify only the matching `serializable` value is returned.
--    Hint ladder, rung 1: For sql-38 Exercise 3, inspect the source keys that survive `WHERE`.
-- 4. Prediction: after ROLLBACK TO SAVEPOINT, decide whether the savepoint
--    itself still exists; release it and verify PostgreSQL's behavior.
--    Inputs: For sql-38 Exercise 4, read from `isolation_solution`. Build the answer toward `release`; keep `release` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-38 Exercise 4, expected output: one row per `release`. The final columns are `release`. The final order is `id`.
--    Verify: For sql-38 Exercise 4, run an anti-check that counts rows where NOT ((id = 2)); require unique `release` where the expected grain is one row per key and confirm the projected `release` against `isolation_solution`. Add one row for which `(id = 2)` is true and one for which it is false; verify only the matching `release` value is returned.
--    Hint ladder, rung 1: For sql-38 Exercise 4, inspect the source keys that survive `WHERE`; then check `id` before applying the row cap.
-- 5. Construction: implement a transfer between two temp accounts that checks
--    the debit balance and updates both rows atomically.
--    Inputs: For sql-38 Exercise 5, read from `transfer_accounts`. Build the answer toward `available`; keep `available` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-38 Exercise 5, expected output: one row per `available`. The final columns are `available`.
--    Verify: For sql-38 Exercise 5, run an anti-check that counts rows where NOT ((account_id = 1 FOR UPDATE) OR (account_id = 1) OR (account_id = 2)); require unique `available` where the expected grain is one row per key and confirm the projected `available` against `transfer_accounts`. Add one row for which `(account_id = 1 FOR UPDATE) OR (account_id = 1) OR (account_id = 2)` is true and one for which it is false; verify only the matching `available` value is returned.
--    Hint ladder, rung 1: For sql-38 Exercise 5, inspect the source keys that survive `WHERE`.
-- 6. Debugging: provoke a unique-key error after a savepoint, recover with
--    ROLLBACK TO SAVEPOINT, and prove the surrounding transaction remains usable.
--    Inputs: For sql-38 Exercise 6, read from `isolation_solution`. Build the answer toward `still_usable`; keep `still_usable` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-38 Exercise 6, expected output: one row per `still_usable`. The final columns are `still_usable`.
--    Verify: For sql-38 Exercise 6, reselect the returned keys directly from the source; require unique `still_usable` where the expected grain is one row per key and confirm the projected `still_usable` against `isolation_solution`. Add duplicate source candidates for `still_usable`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
--    Hint ladder, rung 1: For sql-38 Exercise 6, select `still_usable` from `isolation_solution` before adding derived columns.
-- 7. Edge case: explain why a read-only transaction can still need a consistent
--    isolation choice when several SELECT statements must describe one snapshot.
--    Inputs: For sql-38 Exercise 7, use two labeled terminals and only `txn_demo`, `isolation_solution`, and `transfer_accounts`. Write the statement order, expected wait/SQLSTATE, and cleanup step before opening either transaction.
--    Expected result/shape: For sql-38 Exercise 7, expected output: a statement-by-statement Session A/Session B transcript followed by the committed fixture state and cleanup evidence. The final columns are `session`, `statement_number`, `outcome`, and `sqlstate`.
--    Verify: For sql-38 Exercise 7, compare every observed value, wait, and SQLSTATE with the written schedule; query `txn_demo`, `isolation_solution`, and `transfer_accounts` after each commit/rollback and finish with both sessions idle and the fixture reset. Repeat the exact interleaving after cleanup and confirm the same wait, SQLSTATE, and committed final rows.
--    Hint ladder, rung 1: For sql-38 Exercise 7, compare every observed value, wait, and SQLSTATE with the written schedule; query `txn_demo`, `isolation_solution`, and `transfer_accounts` after each commit/rollback and finish with both sessions idle and the fixture reset.

ROLLBACK;
