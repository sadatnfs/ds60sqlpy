-- Day 01 executable solutions
-- SOLUTION READING MAP — sql-01: Select Where Orderby
-- Explanation: sql/postgres-60day/solutions/day01_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day01_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Build a result deliberately from projection, filtering, deterministic ordering, and a bounded row count.
-- Assumptions: Timestamps are `timestamptz`; relative-date exercises use the database clock. A result is stable only when its final sort key breaks ties.
-- Pitfall: Never use `= NULL`, depend on implicit row order, or apply `LIMIT` without first defining which rows are first.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: List the 20 newest orders with customer ID and total amount.
-- Why: Sort by `order_date DESC` and add `order_id DESC` as a unique tie-breaker before applying `LIMIT`.
-- Expected: At most 20 rows; one row per order, newest first.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
-- - `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       o.order_date
FROM orders AS o
ORDER BY o.order_date DESC, o.order_id DESC
LIMIT 20;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Find the 10 most expensive products created in the last 90 days.
-- Why: Filter the timestamp directly, then sort by price and a stable product key.
-- Expected: At most 10 product rows; every row is in the 90-day window.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
-- - `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
SELECT p.product_id,
       p.name,
       p.price,
       p.created_at
FROM products AS p
WHERE p.created_at >= CURRENT_TIMESTAMP - INTERVAL '90 days'
ORDER BY p.price DESC, p.product_id
LIMIT 10;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Show customers from GB or DE created in the last year, newest first.
-- Why: Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties.
-- Expected: Only GB/DE customers from the declared window.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name,
       c.country,
       c.created_at
FROM customers AS c
WHERE c.country IN ('GB', 'DE')
  AND c.created_at >= CURRENT_TIMESTAMP - INTERVAL '1 year'
ORDER BY c.created_at DESC, c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Predict which rows survive `email = NULL`, then write a query that counts missing and present emails correctly.
-- Why: Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`.
-- Expected: Exactly one summary row with counts whose sum equals all customers.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
SELECT COUNT(*) FILTER (WHERE c.email IS NULL) AS missing_email_count,
       COUNT(*) FILTER (WHERE c.email IS NOT NULL) AS present_email_count,
       COUNT(*) AS customer_count
FROM customers AS c;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Repair a top-price query that uses `LIMIT 10` without `ORDER BY` and explain why the original is nondeterministic.
-- Why: Define the business ranking first; use a unique final key for tied prices.
-- Expected: At most 10 rows, highest prices first, stable across repeated runs on unchanged data.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
-- - `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
SELECT p.product_id,
       p.name,
       p.price
FROM products AS p
ORDER BY p.price DESC, p.product_id
LIMIT 10;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than `OFFSET`.
-- Why: Use the last `(order_date, order_id)` pair from page one and compare row values in the same descending order.
-- Expected: Up to 10 rows strictly after the first page with no overlap.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
-- - `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
WITH first_page AS (
  SELECT o.order_id,
         o.order_date
  FROM orders AS o
  ORDER BY o.order_date DESC, o.order_id DESC
  LIMIT 10
), cursor_row AS (
  SELECT fp.order_date,
         fp.order_id
  FROM first_page AS fp
  ORDER BY fp.order_date, fp.order_id
  LIMIT 1
)
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       o.order_date
FROM orders AS o
CROSS JOIN cursor_row AS cursor
WHERE (o.order_date, o.order_id) < (cursor.order_date, cursor.order_id)
ORDER BY o.order_date DESC, o.order_id DESC
LIMIT 10;

-- No course answer persists changes or temporary objects.
ROLLBACK;
