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
--    Inputs: Use only the declared lesson objects (txn_demo) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 2. Demonstrate phantom reads between two SELECT COUNT(*) with concurrent INSERTs.
--    Inputs: Use only the declared lesson objects (txn_demo) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Use SERIALIZABLE and observe serialization failures under contention.
--    Inputs: Use only the declared lesson objects (txn_demo) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 4. Prediction: after ROLLBACK TO SAVEPOINT, decide whether the savepoint
--    itself still exists; release it and verify PostgreSQL's behavior.
--    Inputs: Use only the declared lesson objects (txn_demo) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 5. Construction: implement a transfer between two temp accounts that checks
--    the debit balance and updates both rows atomically.
--    Inputs: Use only the declared lesson objects (txn_demo) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 6. Debugging: provoke a unique-key error after a savepoint, recover with
--    ROLLBACK TO SAVEPOINT, and prove the surrounding transaction remains usable.
--    Inputs: Use only the declared lesson objects (txn_demo) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 7. Edge case: explain why a read-only transaction can still need a consistent
--    isolation choice when several SELECT statements must describe one snapshot.
--    Inputs: Use only the declared lesson objects (txn_demo) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
