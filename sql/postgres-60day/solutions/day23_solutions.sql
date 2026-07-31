-- Day 23 executable solutions
-- SOLUTION READING MAP — sql-23: CTEs Intro
-- Explanation: sql/postgres-60day/solutions/day23_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day23_solutions.sql
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
-- Focus: Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability—not forced materialization—is the default goal.
-- Assumptions: Each CTE declares its output grain. PostgreSQL 16 may inline a side-effect-free single-use CTE unless `MATERIALIZED` is requested.
-- Pitfall: A CTE does not automatically improve performance; duplicated rows or ambiguous names remain logical bugs even when split into stages.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Build order-level net value in one CTE and summarize it by customer in the outer query.
-- Why: Name the one-row-per-order grain before changing to customer grain.
-- Expected: One row per ordering customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders AS o
  JOIN order_items AS oi
    ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id
)
SELECT ov.customer_id,
       COUNT(*) AS order_count,
       ROUND(SUM(ov.order_value), 2) AS net_revenue
FROM order_values AS ov
GROUP BY ov.customer_id
ORDER BY net_revenue DESC, ov.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Use one category-revenue CTE twice to return the highest category and total revenue.
-- Why: A named aggregate can support multiple scalar reads without repeating the business formula.
-- Expected: One summary row.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
-- - `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
WITH category_revenue AS (
  SELECT p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items AS oi
  JOIN products AS p
    ON p.product_id = oi.product_id
  GROUP BY p.category
)
SELECT (
         SELECT cr.category
         FROM category_revenue AS cr
         ORDER BY cr.revenue DESC, cr.category
         LIMIT 1
       ) AS top_category,
       ROUND((SELECT SUM(cr.revenue) FROM category_revenue AS cr), 2) AS all_revenue;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Create staged payment reconciliation CTEs at order grain.
-- Why: Aggregate payment detail before joining to orders and preserve unpaid orders with a left join.
-- Expected: One row per order.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `COALESCE`: replaces NULL only where the lesson explicitly defines a missing value as a concrete fallback.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH paid AS (
  SELECT p.order_id,
         SUM(p.amount) AS paid_amount
  FROM payments AS p
  GROUP BY p.order_id
), reconciled AS (
  SELECT o.order_id,
         o.total_amount,
         COALESCE(paid.paid_amount, 0) AS paid_amount
  FROM orders AS o
  LEFT JOIN paid
    ON paid.order_id = o.order_id
)
SELECT order_id,
       ROUND(total_amount, 2) AS order_total,
       ROUND(paid_amount, 2) AS paid_amount,
       ROUND(total_amount - paid_amount, 2) AS unpaid_balance
FROM reconciled
ORDER BY ABS(total_amount - paid_amount) DESC, order_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Compare `MATERIALIZED` and `NOT MATERIALIZED` syntax on a side-effect-free filtered order CTE without claiming one is universally faster.
-- Why: Both return the same rows; planning effects require `EXPLAIN` evidence in a representative environment.
-- Expected: Two count rows with equal values.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH materialized_orders AS MATERIALIZED (
  SELECT o.order_id
  FROM orders AS o
  WHERE o.status = 'delivered'
), inline_orders AS NOT MATERIALIZED (
  SELECT o.order_id
  FROM orders AS o
  WHERE o.status = 'delivered'
)
SELECT 'materialized' AS variant, COUNT(*) AS row_count
FROM materialized_orders
UNION ALL
SELECT 'not_materialized' AS variant, COUNT(*) AS row_count
FROM inline_orders
ORDER BY variant;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Repair a multi-stage query whose repeated `total` column names are ambiguous by assigning grain-specific aliases.
-- Why: Name measures `order_value`, `customer_revenue`, and similar rather than carrying generic `total`.
-- Expected: One row per country.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH order_values AS (
  SELECT o.order_id,
         o.customer_id,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value
  FROM orders AS o
  JOIN order_items AS oi
    ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id
), customer_revenue AS (
  SELECT ov.customer_id,
         SUM(ov.order_value) AS customer_revenue
  FROM order_values AS ov
  GROUP BY ov.customer_id
)
SELECT c.country,
       ROUND(SUM(cr.customer_revenue), 2) AS country_revenue
FROM customer_revenue AS cr
JOIN customers AS c
  ON c.customer_id = cr.customer_id
GROUP BY c.country
ORDER BY country_revenue DESC, c.country;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Use a data-modifying CTE to demonstrate an update and inspect its returned rows without persistence.
-- Why: The outer lesson transaction rolls back; the CTE exposes changed rows as a relation.
-- Expected: One summary row for a bounded three-product update.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `UPDATE`: changes only the target rows selected by its predicate; preview that population before executing.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
-- - `LIMIT`: is applied after ordering and is meaningful only when the query first defines which rows come first.
-- - `RETURNING`: shows the rows changed by DML, providing immediate evidence of the affected population.
-- - savepoint control: creates or restores an inner transaction checkpoint while the lesson's outer rollback remains the final guard.
SAVEPOINT exercise_6;
WITH candidates AS (
  SELECT p.product_id
  FROM products AS p
  ORDER BY p.product_id
  LIMIT 3
), updated AS (
  UPDATE products AS p
  SET price = ROUND(p.price * 1.01, 2)
  WHERE p.product_id IN (SELECT c.product_id FROM candidates AS c)
  RETURNING p.product_id, p.price
)
SELECT COUNT(*) AS updated_rows,
       MIN(product_id) AS first_updated_product,
       MAX(product_id) AS last_updated_product
FROM updated;
ROLLBACK TO SAVEPOINT exercise_6;

-- No course answer persists changes or temporary objects.
ROLLBACK;
