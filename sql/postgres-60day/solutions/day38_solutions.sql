-- Day 38 solutions: transactions and isolation
BEGIN;
SET search_path TO training, public;

-- Isolation anomalies require two concurrent database sessions; one .sql file
-- cannot create genuine concurrency by itself. This runnable portion verifies
-- the session and demonstrates a recoverable savepoint.
SHOW transaction_isolation;

CREATE TEMP TABLE isolation_solution (
  id int PRIMARY KEY,
  quantity int NOT NULL
);
INSERT INTO isolation_solution VALUES (1, 10), (2, 20);

SAVEPOINT before_change;
UPDATE isolation_solution SET quantity = quantity + 5 WHERE id = 1;
SELECT * FROM isolation_solution ORDER BY id;
ROLLBACK TO SAVEPOINT before_change;
SELECT * FROM isolation_solution ORDER BY id;

-- Manual Exercise 1, two terminals. Prepare the shared table once in either
-- terminal before opening the two transactions:
-- DROP TABLE IF EXISTS training.isolation_solution_shared;
-- CREATE TABLE training.isolation_solution_shared (
--   id int PRIMARY KEY,
--   quantity int NOT NULL
-- );
-- INSERT INTO training.isolation_solution_shared VALUES (1, 10), (2, 20);
--
-- A: BEGIN ISOLATION LEVEL READ COMMITTED;
-- A: SELECT quantity FROM isolation_solution_shared WHERE id = 1;
-- B: BEGIN; UPDATE isolation_solution_shared SET quantity=99 WHERE id=1; COMMIT;
-- A: SELECT quantity FROM isolation_solution_shared WHERE id = 1; -- changed
--
-- Exercise 2 repeats SELECT COUNT(*) in A while B inserts and commits.
-- Exercise 3 uses BEGIN ISOLATION LEVEL SERIALIZABLE in both sessions and
-- performs conflicting read/modify/write work; retry the transaction that
-- PostgreSQL aborts with SQLSTATE 40001.
--
-- Clean up after the manual exercises:
-- DROP TABLE training.isolation_solution_shared;

-- Exercise 4: ROLLBACK TO keeps the named savepoint available. RELEASE removes
-- it after the partial recovery is complete.
SAVEPOINT reusable_point;
UPDATE isolation_solution SET quantity = quantity + 1 WHERE id = 2;
ROLLBACK TO SAVEPOINT reusable_point;
RELEASE SAVEPOINT reusable_point;
SELECT * FROM isolation_solution ORDER BY id;

-- Exercise 5: both balance changes are one atomic unit. The guarded DO block
-- raises before either UPDATE if the debit account cannot cover the transfer.
CREATE TEMP TABLE transfer_accounts (
  account_id int PRIMARY KEY,
  balance numeric(12, 2) NOT NULL CHECK (balance >= 0)
);
INSERT INTO transfer_accounts VALUES (1, 100.00), (2, 40.00);
DO $transfer$
DECLARE
  transfer_amount numeric(12, 2) := 25.00;
  available numeric(12, 2);
BEGIN
  SELECT balance INTO available
  FROM transfer_accounts
  WHERE account_id = 1
  FOR UPDATE;
  IF available < transfer_amount THEN
    RAISE EXCEPTION 'insufficient balance';
  END IF;
  UPDATE transfer_accounts
  SET balance = balance - transfer_amount WHERE account_id = 1;
  UPDATE transfer_accounts
  SET balance = balance + transfer_amount WHERE account_id = 2;
END
$transfer$;
SELECT SUM(balance) AS conserved_total FROM transfer_accounts;

-- Exercise 6: an EXCEPTION block is implemented with an internal savepoint.
-- Catching the expected unique violation leaves the outer transaction usable.
DO $recover_unique$
BEGIN
  BEGIN
    INSERT INTO isolation_solution VALUES (1, 999);
  EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'duplicate rejected; outer transaction remains usable';
  END;
END
$recover_unique$;
SELECT COUNT(*) AS still_usable FROM isolation_solution;

-- Exercise 7 is a design answer: use REPEATABLE READ for several SELECTs that
-- must describe one snapshot; READ COMMITTED is fine when per-statement
-- freshness is intended. Read-only does not mean snapshot choice is irrelevant.

ROLLBACK;
