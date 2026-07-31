-- Day 11 executable solutions
-- SOLUTION READING MAP — sql-11: Case Expressions
-- Explanation: sql/postgres-60day/solutions/day11_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day11_solutions.sql
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
-- Focus: Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.
-- Assumptions: Searched `CASE` uses first-match wins. Status/category labels are illustrative course rules, not universal business definitions.
-- Pitfall: Overlapping broad conditions placed first make later branches unreachable; an omitted `ELSE` produces NULL.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Classify orders as small, medium, or large by total amount.
-- Why: Validate boundaries and place the highest threshold first.
-- Expected: One row per order with exactly one size label.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT o.order_id,
       o.total_amount,
       CASE
         WHEN o.total_amount >= 500 THEN 'large'
         WHEN o.total_amount >= 100 THEN 'medium'
         ELSE 'small'
       END AS order_size
FROM orders AS o
ORDER BY o.order_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation.
-- Why: Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator.
-- Expected: One summary row.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
SELECT COUNT(*) FILTER (WHERE o.status IN ('paid', 'shipped', 'delivered')) AS paid_like,
       COUNT(*) FILTER (WHERE o.status = 'placed') AS open_orders,
       COUNT(*) FILTER (WHERE o.status = 'returned') AS returned_orders,
       COUNT(*) AS all_orders
FROM orders AS o;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Label missing customer segments separately from known segment values.
-- Why: Test `IS NULL` before comparing text values.
-- Expected: One row per customer with an explicit segment label.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.segment,
       CASE
         WHEN c.segment IS NULL THEN 'missing'
         WHEN c.segment IN ('gold', 'platinum') THEN 'premium'
         ELSE 'core'
       END AS segment_group
FROM customers AS c
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Predict the label for 500 when `>= 100` appears before `>= 500`, then repair the branch order.
-- Why: First-match wins, so specific/high thresholds must precede broader/lower ones.
-- Expected: A value of 500 is labeled high.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT amount,
       CASE
         WHEN amount >= 500 THEN 'high'
         WHEN amount >= 100 THEN 'medium'
         ELSE 'low'
       END AS corrected_label
FROM (VALUES (50::numeric), (100::numeric), (500::numeric)) AS sample(amount)
ORDER BY amount;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Replace a CASE expression that returns mixed numeric and text types with one consistent output type.
-- Why: All result branches must resolve to a compatible PostgreSQL type.
-- Expected: Three rows with text labels.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT value,
       CASE
         WHEN value IS NULL THEN 'missing'
         WHEN value = 0 THEN 'zero'
         ELSE 'nonzero'
       END AS value_state
FROM (VALUES (NULL::integer), (0), (2)) AS sample(value)
ORDER BY value NULLS FIRST;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Create payment-method display labels and preserve unknown future methods with an explicit fallback.
-- Why: A simple CASE fits equality mapping; `ELSE` prevents silent NULL labels.
-- Expected: One row per payment method and display label.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT p.method,
       CASE p.method
         WHEN 'card' THEN 'Card'
         WHEN 'paypal' THEN 'PayPal'
         WHEN 'bank' THEN 'Bank transfer'
         WHEN 'credit' THEN 'Store credit'
         ELSE 'Other'
       END AS method_label,
       COUNT(*) AS payment_count
FROM payments AS p
GROUP BY p.method
ORDER BY p.method;

-- No course answer persists changes or temporary objects.
ROLLBACK;
