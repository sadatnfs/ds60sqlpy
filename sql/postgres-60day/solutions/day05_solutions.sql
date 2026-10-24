-- Day 05 executable solutions
-- SOLUTION READING MAP — sql-05: Cross Self Joins
-- Explanation: sql/postgres-60day/solutions/day05_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day05_solutions.sql
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
-- Focus: Use cross joins for intentional combinations and self joins for relationships within one table, with explicit cardinality controls.
-- Assumptions: The employee hierarchy uses `manager_id`; equality pairs need a strict key ordering to avoid self-pairs and mirrored duplicates.
-- Pitfall: An accidental cross join multiplies row counts. Estimate left × right cardinality before materializing combinations.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: List every employee with their direct manager when present.
-- Why: Self join employees and use a left join so top-level employees remain visible.
-- Expected: One row per employee.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT e.employee_id,
       e.full_name AS employee_name,
       m.employee_id AS manager_id,
       m.full_name AS manager_name
FROM employees AS e
LEFT JOIN employees AS m
  ON m.employee_id = e.manager_id
ORDER BY e.employee_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Find employees who manage nobody.
-- Why: Left join candidate managers to reports and retain managers with no right-side match.
-- Expected: One row per leaf employee.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT e.employee_id,
       e.full_name
FROM employees AS e
LEFT JOIN employees AS report
  ON report.manager_id = e.employee_id
WHERE report.employee_id IS NULL
ORDER BY e.employee_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Build a complete grid of six recent months and all expense categories.
-- Why: Cross join two small declared dimensions; do not cross join raw fact tables.
-- Expected: Six rows per distinct expense category.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH months AS (
  SELECT generate_series(
           date_trunc('month', CURRENT_DATE) - INTERVAL '5 months',
           date_trunc('month', CURRENT_DATE),
           INTERVAL '1 month'
         )::date AS month_start
), categories AS (
  SELECT DISTINCT e.category
  FROM expenses AS e
)
SELECT c.category,
       m.month_start
FROM categories AS c
CROSS JOIN months AS m
ORDER BY c.category, m.month_start;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Predict the count from crossing six departments with twelve months, then verify it without materializing extra columns.
-- Why: Cross-join cardinality is the product of input row counts.
-- Expected: One row containing 72.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
WITH months AS (
  SELECT generate_series(1, 12) AS month_number
)
SELECT COUNT(*) AS department_month_combinations
FROM departments AS d
CROSS JOIN months AS m;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: List unique employee pairs in the same department without self-pairs or mirrored duplicates.
-- Why: Use `left.employee_id < right.employee_id` as both the join condition and uniqueness rule.
-- Expected: One row per unordered same-department pair.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT left_employee.department_id,
       left_employee.employee_id AS first_employee_id,
       right_employee.employee_id AS second_employee_id
FROM employees AS left_employee
JOIN employees AS right_employee
  ON right_employee.department_id = left_employee.department_id
 AND left_employee.employee_id < right_employee.employee_id
ORDER BY left_employee.department_id,
         left_employee.employee_id,
         right_employee.employee_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Show each employee, their manager, and their manager's manager.
-- Why: Use two independently aliased left self joins; NULLs indicate the hierarchy ends.
-- Expected: One row per employee with up to two ancestor columns.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT e.employee_id,
       e.full_name AS employee_name,
       manager.full_name AS manager_name,
       grandmanager.full_name AS grandmanager_name
FROM employees AS e
LEFT JOIN employees AS manager
  ON manager.employee_id = e.manager_id
LEFT JOIN employees AS grandmanager
  ON grandmanager.employee_id = manager.manager_id
ORDER BY e.employee_id;

-- No course answer persists changes or temporary objects.
ROLLBACK;
