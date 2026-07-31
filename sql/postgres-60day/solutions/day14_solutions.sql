-- Day 14 executable solutions
-- SOLUTION READING MAP — sql-14: Numeric and Casting
-- Explanation: sql/postgres-60day/solutions/day14_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day14_solutions.sql
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
-- Focus: Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.
-- Assumptions: Money is exact `numeric`; division casts denominators to numeric where fractions matter. NULL/zero denominators return NULL through `NULLIF`.
-- Pitfall: Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Calculate product gross margin amount and percentage, returning NULL percentage for zero price.
-- Why: Keep exact numeric arithmetic and guard the denominator with `NULLIF`.
-- Expected: One row per product.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT p.product_id,
       p.price,
       p.cost,
       p.price - p.cost AS margin_amount,
       ROUND((p.price - p.cost) / NULLIF(p.price, 0), 4) AS margin_rate
FROM products AS p
ORDER BY margin_rate DESC NULLS LAST, p.product_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Safely cast a set of text values to numeric only when they match a numeric grammar.
-- Why: Validate with a regex before casting; otherwise return NULL.
-- Expected: One row per sample text.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
-- - pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
SELECT raw_value,
       CASE
         WHEN btrim(raw_value) ~ '^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$'
           THEN btrim(raw_value)::numeric
         ELSE NULL
       END AS parsed_numeric
FROM (VALUES ('42'), (' 3.14 '), ('-0.5'), ('many'), ('')) AS sample(raw_value);

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Show order-item net revenue rounded only after summing.
-- Why: Aggregate exact line expressions first; round the final display value.
-- Expected: One row per order.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT oi.order_id,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS net_order_revenue
FROM order_items AS oi
GROUP BY oi.order_id
ORDER BY oi.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Compare integer division with numeric division for 1 divided by 4.
-- Why: At least one operand must be numeric to preserve the fraction.
-- Expected: One row showing 0 and 0.25.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
SELECT 1 / 4 AS integer_division,
       1::numeric / 4 AS numeric_division;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders.
-- Why: Aggregate payment amount and count distinct order IDs at one common scope.
-- Expected: Exactly one summary row.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `NULLIF`: turns a prohibited denominator into NULL so division reports unknown instead of raising an error.
SELECT ROUND(
         SUM(p.amount) / NULLIF(COUNT(DISTINCT p.order_id), 0),
         2
       ) AS average_paid_amount_per_order
FROM payments AS p;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference.
-- Why: This diagnostic makes the consequence of early rounding visible.
-- Expected: One row with two totals and their signed difference.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
SELECT SUM(ROUND(oi.unit_price * oi.quantity * (1 - oi.discount), 2)) AS sum_of_rounded_lines,
       ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS rounded_exact_total,
       SUM(ROUND(oi.unit_price * oi.quantity * (1 - oi.discount), 2))
         - ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2)
         AS rounding_difference
FROM order_items AS oi;

-- No course answer persists changes or temporary objects.
ROLLBACK;
