-- Day 16 executable solutions
-- SOLUTION READING MAP — sql-16: Window Functions Fundamentals
-- Explanation: sql/postgres-60day/solutions/day16_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day16_solutions.sql
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
-- Focus: Use window functions to add partition-level context while preserving row grain, with explicit partition and ordering semantics.
-- Assumptions: Window aggregates do not collapse rows. When order matters, use a unique tie-breaker and declare the frame in later cumulative lessons.
-- Pitfall: Filtering a window result in the same query level is invalid; compute it in a subquery or CTE first.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Show each order with the customer's average order total.
-- Why: Partition by customer ID and keep one output row per order.
-- Expected: One row per order.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id), 2) AS customer_average
FROM orders AS o
ORDER BY o.customer_id, o.order_date, o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Show each employee salary with department average, minimum, and maximum.
-- Why: Partition all three window aggregates by department.
-- Expected: One row per employee.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT e.employee_id,
       e.department_id,
       e.salary,
       ROUND(AVG(e.salary) OVER (PARTITION BY e.department_id), 2) AS department_average,
       MIN(e.salary) OVER (PARTITION BY e.department_id) AS department_minimum,
       MAX(e.salary) OVER (PARTITION BY e.department_id) AS department_maximum
FROM employees AS e
ORDER BY e.department_id, e.employee_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Calculate every order's share of its customer's stored revenue.
-- Why: Use a partition total denominator and guard it with `NULLIF`.
-- Expected: One row per order with shares summing near one per customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.customer_id,
       o.total_amount,
       ROUND(
         o.total_amount
           / NULLIF(SUM(o.total_amount) OVER (PARTITION BY o.customer_id), 0),
         4
       ) AS customer_revenue_share
FROM orders AS o
ORDER BY o.customer_id, o.order_date, o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Compare `GROUP BY customer_id` with `AVG(...) OVER (PARTITION BY customer_id)` and report their row counts.
-- Why: Grouping collapses to one row per customer; a window preserves every order row.
-- Expected: Two labeled count rows.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH grouped AS (
  SELECT o.customer_id, AVG(o.total_amount) AS average_total
  FROM orders AS o
  GROUP BY o.customer_id
), windowed AS (
  SELECT o.order_id,
         AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS average_total
  FROM orders AS o
)
SELECT 'grouped' AS method, COUNT(*) AS row_count FROM grouped
UNION ALL
SELECT 'windowed' AS method, COUNT(*) AS row_count FROM windowed
ORDER BY method;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Return orders above their customer average without placing a window function in `WHERE`.
-- Why: Compute the window value in a CTE, then filter the named column outside.
-- Expected: Order rows above their customer mean.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH scored AS (
  SELECT o.*,
         AVG(o.total_amount) OVER (PARTITION BY o.customer_id) AS customer_average
  FROM orders AS o
)
SELECT order_id,
       customer_id,
       total_amount,
       ROUND(customer_average, 2) AS customer_average
FROM scored
WHERE total_amount > customer_average
ORDER BY customer_id, total_amount DESC, order_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Show order count and revenue context at both customer and country levels in the same row.
-- Why: Use different partitions for independent analytical contexts.
-- Expected: One row per order with customer and country totals.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `OVER (...)`: computes an analytic value while preserving detail rows; partition, order, and frame define its peer set.
-- - `PARTITION BY`: restarts a window calculation independently for each partition key.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.customer_id,
       c.country,
       COUNT(*) OVER (PARTITION BY o.customer_id) AS customer_order_count,
       SUM(o.total_amount) OVER (PARTITION BY o.customer_id) AS customer_revenue,
       SUM(o.total_amount) OVER (PARTITION BY c.country) AS country_revenue
FROM orders AS o
JOIN customers AS c
  ON c.customer_id = o.customer_id
ORDER BY c.country, o.customer_id, o.order_date, o.order_id;

-- No course answer persists changes or temporary objects.
ROLLBACK;
