-- Day 31 solutions: EXPLAIN and EXPLAIN ANALYZE
-- SOLUTION READING MAP — sql-31: Explain Analyze
-- Explanation: sql/postgres-60day/solutions/day31_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day31_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
BEGIN;
SET search_path TO training, public;

-- Exercise 1: compare a broad predicate with a selective predicate.
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE order_date >= CURRENT_TIMESTAMP - interval '3 years';

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE order_date >= CURRENT_TIMESTAMP - interval '7 days'
  AND status = 'returned'
  AND total_amount >= 1000;

-- Exercise 2: EXPLAIN estimates only; EXPLAIN ANALYZE also executes and reports
-- actual timing and row counts. Use read-only SELECTs while learning ANALYZE.
EXPLAIN
SELECT c.country, SUM(o.total_amount) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.country;

EXPLAIN (ANALYZE, BUFFERS)
SELECT c.country, SUM(o.total_amount) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.country;

-- Exercise 3: the broad predicate should estimate/return more rows than the
-- selective predicate. BUFFERS reports pages touched, not just elapsed time.
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id FROM orders WHERE total_amount > 0;

EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id FROM orders WHERE total_amount > 900;

-- Exercise 4: VERBOSE exposes qualified output columns. Read from the scans
-- upward through the join and aggregate to the root sort.
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT c.country, COUNT(*) AS order_count
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE c.country = 'US'
GROUP BY c.country;

-- Exercise 5: ANALYZE executes DML. The impossible key keeps this no-op, while
-- the savepoint demonstrates the safety pattern for a disposable transaction.
SAVEPOINT before_explained_update;
EXPLAIN (ANALYZE, BUFFERS)
UPDATE orders SET status = status WHERE order_id = -1;
ROLLBACK TO SAVEPOINT before_explained_update;
RELEASE SAVEPOINT before_explained_update;

-- Exercise 6: the CHECK constraint makes negative totals impossible. Compare
-- the estimate printed by EXPLAIN with the actual zero rows.
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id FROM orders WHERE total_amount < 0;

ROLLBACK;
