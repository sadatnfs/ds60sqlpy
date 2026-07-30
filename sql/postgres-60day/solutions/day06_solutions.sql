-- Day 06 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Combine compatible row sets with explicit duplicate semantics: `UNION`, `UNION ALL`, `INTERSECT`, and `EXCEPT`.
-- Assumptions: Set-operation inputs must have compatible column counts/types. Output order is undefined unless one final `ORDER BY` follows the complete set expression.
-- Pitfall: `UNION` removes duplicates and can hide data multiplicity; `NOT IN` is not a safe substitute for `EXCEPT` when NULL is possible.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Return customer IDs that have either an order or a support event.
-- Why: `UNION` expresses set membership and removes duplicates across both sources.
-- Expected: One distinct customer ID per qualifying customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.customer_id
FROM orders AS o
UNION
SELECT e.customer_id
FROM events AS e
WHERE e.event_type = 'support'
ORDER BY customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Return customer IDs that have both an order and a support event.
-- Why: `INTERSECT` keeps keys present in both compatible sets.
-- Expected: One distinct customer ID in both sets.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.customer_id
FROM orders AS o
INTERSECT
SELECT e.customer_id
FROM events AS e
WHERE e.event_type = 'support'
ORDER BY customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Return customers who have no orders.
-- Why: `EXCEPT` subtracts the order-customer set from all customers.
-- Expected: One row per customer absent from orders.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id
FROM customers AS c
EXCEPT
SELECT o.customer_id
FROM orders AS o
ORDER BY customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Compare row counts produced by `UNION` and `UNION ALL` for two overlapping status lists.
-- Why: `UNION ALL` preserves every input row; `UNION` returns distinct rows.
-- Expected: Two labeled summary rows showing all-count >= distinct-count.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH combined_all AS (
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('paid', 'shipped')
  UNION ALL
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('shipped', 'delivered')
), combined_distinct AS (
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('paid', 'shipped')
  UNION
  SELECT o.status
  FROM orders AS o
  WHERE o.status IN ('shipped', 'delivered')
)
SELECT 'UNION ALL' AS operation,
       COUNT(*) AS row_count
FROM combined_all
UNION ALL
SELECT 'UNION' AS operation,
       COUNT(*) AS row_count
FROM combined_distinct
ORDER BY operation;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Repair a set operation whose branches return incompatible meanings or types by aligning aliases and casts.
-- Why: Each branch below returns one text label and one numeric amount at the same report grain.
-- Expected: Rows identify revenue and expense measures with compatible types.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT 'order_revenue'::text AS measure,
       SUM(o.total_amount)::numeric AS amount
FROM orders AS o
UNION ALL
SELECT 'expense'::text AS measure,
       SUM(e.amount)::numeric AS amount
FROM expenses AS e
ORDER BY measure;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Return the symmetric difference between customers with orders and customers with support events.
-- Why: Subtract each set from the other, then union the two differences.
-- Expected: Customers present in exactly one of the two source sets.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH ordering_customers AS (
  SELECT DISTINCT o.customer_id
  FROM orders AS o
), support_customers AS (
  SELECT DISTINCT e.customer_id
  FROM events AS e
  WHERE e.event_type = 'support'
), only_orders AS (
  SELECT customer_id FROM ordering_customers
  EXCEPT
  SELECT customer_id FROM support_customers
), only_support AS (
  SELECT customer_id FROM support_customers
  EXCEPT
  SELECT customer_id FROM ordering_customers
)
SELECT customer_id, 'orders_only' AS source
FROM only_orders
UNION ALL
SELECT customer_id, 'support_only' AS source
FROM only_support
ORDER BY customer_id, source;

-- No course answer persists changes or temporary objects.
ROLLBACK;
