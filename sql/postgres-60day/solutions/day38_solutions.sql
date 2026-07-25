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

ROLLBACK;
