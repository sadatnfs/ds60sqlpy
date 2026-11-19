-- Day 38: Transactions & ACID, Isolation Levels
-- BEGINNER WORKFLOW - sql-38: Transactions Isolation
-- Guide: sql/postgres-60day/companion-guides/day38_transactions_isolation.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-38.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
CREATE TEMP TABLE txn_demo (
  id int PRIMARY KEY,
  qty int
);

INSERT INTO txn_demo
VALUES
  (1, 10),
  (2, 20),
  (3, 30);

-- Read snapshot under REPEATABLE READ
SELECT
  *
FROM
  txn_demo
ORDER BY
  id;

-- txn_demo is session-private and uncommitted; no other session can see it.
-- Isolation needs the committed training.isolation_lab table and two
-- terminals (Exercise 1 and the guide's lab setup). Re-reading here only
-- returns the same row, because no other transaction can change it:
SELECT
  *
FROM
  txn_demo
WHERE
  id = 2;

-- Savepoint / rollback demo (single session)
SAVEPOINT sp1;

UPDATE
  txn_demo
SET
  qty = qty + 100
WHERE
  id = 1;

SELECT
  *
FROM
  txn_demo
WHERE
  id = 1;

-- shows +100 within tx
ROLLBACK TO SAVEPOINT sp1;

SELECT
  *
FROM
  txn_demo
WHERE
  id = 1;

-- back to original in this tx
-- Exercises
-- 1. In two sessions, reproduce non-repeatable reads under READ COMMITTED.
--    Inputs: For sql-38 Exercise 1, use two terminals and the committed lab table `training.isolation_lab` from the lab setup, seeded with rows `(1, 10)` and `(2, 20)`; Session B changes only the row with `id = 1`.
--    Expected result/shape: For sql-38 Exercise 1, expected output: under `READ COMMITTED`, Session A's two `SELECT qty FROM training.isolation_lab WHERE id = 1` statements return one row each, `10` and then `15`, because Session B commits `qty = 15` between them; under `REPEATABLE READ` the second read still returns `10`.
--    Verify: For sql-38 Exercise 1, record both `qty` values, the commit order, and each session's level from `SHOW transaction_isolation`; after both sessions end, `SELECT id, qty FROM training.isolation_lab ORDER BY id` returns `(1, 15)` and `(2, 20)`. Reset `id = 1` to `10` before repeating the schedule at `REPEATABLE READ`.
--    Hint ladder, rung 1: For sql-38 Exercise 1, keep Session A's transaction open between its two reads; the second read must come after Session B's `COMMIT`.
-- 2. Reproduce a phantom under READ COMMITTED with two SELECT COUNT(*) statements
--    and a concurrent INSERT, then show that REPEATABLE READ prevents it.
--    Inputs: For sql-38 Exercise 2, start from `training.isolation_lab` with no row whose `id >= 3`; Session A counts rows matching `qty >= 20` twice while Session B inserts and commits `(3, 30)` between the two counts.
--    Expected result/shape: For sql-38 Exercise 2, expected output: under `READ COMMITTED`, Session A's two one-row `count` results are `1` and then `2`, because the committed row `(3, 30)` is a phantom; under `REPEATABLE READ`, both counts are `1` until Session A ends.
--    Verify: For sql-38 Exercise 2, record both `count` values and the commit order at each isolation level; after each run, `SELECT COUNT(*) FROM training.isolation_lab WHERE id = 3` returns `1`, proving Session B's insert was committed. Delete the row with `id = 3` before repeating the schedule.
--    Hint ladder, rung 1: For sql-38 Exercise 2, a phantom is a new row that starts to match a predicate; use the same `WHERE qty >= 20` for both counts.
-- 3. Use SERIALIZABLE and observe serialization failures under contention.
--    Inputs: For sql-38 Exercise 3, reset `training.isolation_lab` to `(1, 10)` and `(2, 20)`, then open two `SERIALIZABLE` transactions that both read `SUM(qty)` before Session A updates the row with `id = 1` and Session B updates the row with `id = 2`.
--    Expected result/shape: For sql-38 Exercise 3, expected output: both sums are `30`; Session A's `COMMIT` succeeds and Session B's `COMMIT` fails with SQLSTATE `40001` (`could not serialize access due to read/write dependencies among transactions`), leaving committed rows `(1, 11)` and `(2, 20)`.
--    Verify: For sql-38 Exercise 3, capture the error text and SQLSTATE (for example after `\set VERBOSITY verbose`), confirm the committed rows with `SELECT id, qty FROM training.isolation_lab ORDER BY id`, then rerun Session B's whole transaction from `BEGIN ISOLATION LEVEL SERIALIZABLE` and confirm the rows `(1, 11)` and `(2, 21)`.
--    Hint ladder, rung 1: For sql-38 Exercise 3, both transactions must read the table before either writes; the failure appears when the second transaction tries to commit.
-- 4. Prediction: after ROLLBACK TO SAVEPOINT, decide whether the savepoint
--    itself still exists; release it and verify PostgreSQL's behavior.
--    Inputs: For sql-38 Exercise 4, use the temporary `isolation_solution` rows `(1, 10)` and `(2, 20)` inside the lesson transaction; set a savepoint, add `1` to `quantity` for `id = 2`, roll back to the savepoint, then release it.
--    Expected result/shape: For sql-38 Exercise 4, expected output: `RELEASE SAVEPOINT` succeeds because `ROLLBACK TO SAVEPOINT` keeps the savepoint, and the final `SELECT` returns two rows ordered by `id` with columns `id` and `quantity`: `(1, 10)` and `(2, 20)`.
--    Verify: For sql-38 Exercise 4, compare the row with `id = 2` before the savepoint and after the rollback (both `20`); in a scratch transaction, a second `RELEASE SAVEPOINT reusable_point` fails with SQLSTATE `3B001` (`savepoint "reusable_point" does not exist`), which proves the first `RELEASE` removed it.
--    Hint ladder, rung 1: For sql-38 Exercise 4, `ROLLBACK TO SAVEPOINT` undoes the work after the savepoint but does not destroy the savepoint itself.
-- 5. Construction: implement a transfer between two temp accounts that checks
--    the debit balance and updates both rows atomically.
--    Inputs: For sql-38 Exercise 5, create the temporary `transfer_accounts` table with rows `(1, 100.00)` and `(2, 40.00)` and `CHECK (balance >= 0)`; move `25.00` from account 1 to account 2 after locking and checking the debit row.
--    Expected result/shape: For sql-38 Exercise 5, expected output: one `conserved_total` row equal to `140.00`; the account rows become `(1, 75.00)` and `(2, 65.00)`.
--    Verify: For sql-38 Exercise 5, list `account_id` and `balance` before and after the transfer and compare their sums; then attempt a `200.00` transfer after a savepoint, confirm the `insufficient balance` exception with SQLSTATE `P0001`, roll back to the savepoint, and confirm both balances are unchanged.
--    Hint ladder, rung 1: For sql-38 Exercise 5, lock the debit row with `SELECT ... FOR UPDATE` before checking its balance, then change both rows in the same transaction.
-- 6. Debugging: provoke a unique-key error after a savepoint, recover with
--    ROLLBACK TO SAVEPOINT, and prove the surrounding transaction remains usable.
--    Inputs: For sql-38 Exercise 6, insert a duplicate `id = 1` into the temporary `isolation_solution` table inside a protected PL/pgSQL block (or after a savepoint), so the unique violation with SQLSTATE `23505` is caught or rolled back to the savepoint.
--    Expected result/shape: For sql-38 Exercise 6, expected output: a notice that the duplicate was rejected, then one `still_usable` row whose value is `2`, the number of rows in `isolation_solution`.
--    Verify: For sql-38 Exercise 6, in a scratch transaction, repeat the duplicate insert without protection and confirm that the next statement fails with SQLSTATE `25P02` (`current transaction is aborted`); the savepoint recovery is what avoids that state.
--    Hint ladder, rung 1: For sql-38 Exercise 6, an error inside a transaction block aborts the whole transaction unless you return to a savepoint taken before the failing statement.
-- 7. Edge case: explain why a read-only transaction can still need a consistent
--    isolation choice when several SELECT statements must describe one snapshot.
--    Inputs: For sql-38 Exercise 7, consider a report that runs two statements over `training.isolation_lab`, a `COUNT(*)` and a `SUM(qty)`, while another session may commit changes between them.
--    Expected result/shape: For sql-38 Exercise 7, expected output: a short written answer that chooses `REPEATABLE READ` (optionally `READ ONLY`) when both results must describe one snapshot, and `READ COMMITTED` when each statement may show the latest committed data.
--    Verify: For sql-38 Exercise 7, test the claim with the Exercise 2 schedule: under `READ COMMITTED`, a `SUM(qty)` run after Session B commits includes the new row that the earlier `COUNT(*)` did not count; under `REPEATABLE READ`, both values describe the first snapshot.
--    Hint ladder, rung 1: For sql-38 Exercise 7, ask whether the report's statements must agree with each other or only need to be individually fresh.
ROLLBACK;
