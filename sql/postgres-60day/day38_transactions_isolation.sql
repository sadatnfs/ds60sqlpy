-- Day 38: Transactions & ACID, Isolation Levels
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
-- 2. Demonstrate phantom reads between two SELECT COUNT(*) with concurrent INSERTs.
-- 3. Use SERIALIZABLE and observe serialization failures under contention.
-- 4. Prediction: after ROLLBACK TO SAVEPOINT, decide whether the savepoint
--    itself still exists; release it and verify PostgreSQL's behavior.
-- 5. Construction: implement a transfer between two temp accounts that checks
--    the debit balance and updates both rows atomically.
-- 6. Debugging: provoke a unique-key error after a savepoint, recover with
--    ROLLBACK TO SAVEPOINT, and prove the surrounding transaction remains usable.
-- 7. Edge case: explain why a read-only transaction can still need a consistent
--    isolation choice when several SELECT statements must describe one snapshot.

ROLLBACK;
