-- Day 09 executable solutions
-- SOLUTION READING MAP — sql-09: Correlated Subqueries
-- Explanation: sql/postgres-60day/solutions/day09_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day09_solutions.sql
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
-- Focus: Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.
-- Assumptions: `EXISTS` tests whether at least one row qualifies and ignores selected values. `NOT EXISTS` remains safe when inner columns can be NULL.
-- Pitfall: A correlated subquery can run conceptually per outer row; do not use it when a join or pre-aggregation states the grain more clearly.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Return customers who have at least one delivered order.
-- Why: `EXISTS` expresses the yes/no question without multiplying customer rows.
-- Expected: One row per qualifying customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name
FROM customers AS c
WHERE EXISTS (
  SELECT 1
  FROM orders AS o
  WHERE o.customer_id = c.customer_id
    AND o.status = 'delivered'
)
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Return products that have never been sold.
-- Why: `NOT EXISTS` correlates on product ID and is not confused by NULL membership.
-- Expected: One row per unsold product.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT p.product_id,
       p.name,
       p.category
FROM products AS p
WHERE NOT EXISTS (
  SELECT 1
  FROM order_items AS oi
  WHERE oi.product_id = p.product_id
)
ORDER BY p.product_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Return each customer's orders that are above that customer's average order total.
-- Why: Correlate the average to the current order's customer, not to the current order ID.
-- Expected: Order rows above their own customer average.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.customer_id,
       o.total_amount
FROM orders AS o
WHERE o.total_amount > (
  SELECT AVG(peer.total_amount)
  FROM orders AS peer
  WHERE peer.customer_id = o.customer_id
)
ORDER BY o.customer_id, o.total_amount DESC, o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Explain and avoid the `NOT IN` plus NULL trap by finding customers without orders using `NOT EXISTS`.
-- Why: Correlate on the customer key; a matching row alone determines exclusion.
-- Expected: One row per customer with no order.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name
FROM customers AS c
WHERE NOT EXISTS (
  SELECT 1
  FROM orders AS o
  WHERE o.customer_id = c.customer_id
)
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Return only each customer's most recent order without an arbitrary `LIMIT 1`.
-- Why: Compare to the correlated `MAX(order_date)` and break timestamp ties with the maximum ID at that timestamp.
-- Expected: At most one deterministic order per customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
-- - `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
SELECT o.order_id,
       o.customer_id,
       o.order_date
FROM orders AS o
WHERE o.order_id = (
  SELECT candidate.order_id
  FROM orders AS candidate
  WHERE candidate.customer_id = o.customer_id
  ORDER BY candidate.order_date DESC, candidate.order_id DESC
  LIMIT 1
)
ORDER BY o.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Return customers for whom every order has at least one payment, excluding customers with no orders.
-- Why: Require an order to exist, then prove no order lacks a payment using double `NOT EXISTS`.
-- Expected: One row per customer satisfying the universal condition.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name
FROM customers AS c
WHERE EXISTS (
  SELECT 1 FROM orders AS any_order
  WHERE any_order.customer_id = c.customer_id
)
  AND NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
      AND NOT EXISTS (
        SELECT 1
        FROM payments AS p
        WHERE p.order_id = o.order_id
      )
  )
ORDER BY c.customer_id;

-- No course answer persists changes or temporary objects.
ROLLBACK;
