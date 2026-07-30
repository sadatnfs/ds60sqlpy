-- Day 25 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Compose multiple CTEs so hierarchy traversal, employee grain, and management summaries remain individually testable.
-- Assumptions: The employee graph can have multiple roots. Payroll uses exact salary numeric and each employee should contribute once per intended output grain.
-- Pitfall: Joining ancestor-descendant pairs to employee facts can count one employee multiple times; state whether output is direct-team or full-subtree grain.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Build a root-based organization CTE and report headcount and payroll by depth.
-- Why: Assign depth during recursion, then aggregate employee rows once.
-- Expected: One row per hierarchy depth.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH RECURSIVE organization AS (
  SELECT e.employee_id,
         e.manager_id,
         e.salary,
         0 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees AS e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT child.employee_id,
         child.manager_id,
         child.salary,
         parent.depth + 1,
         parent.path || child.employee_id
  FROM organization AS parent
  JOIN employees AS child
    ON child.manager_id = parent.employee_id
  WHERE NOT child.employee_id = ANY(parent.path)
)
SELECT depth,
       COUNT(*) AS headcount,
       ROUND(SUM(salary), 2) AS payroll
FROM organization
GROUP BY depth
ORDER BY depth;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Report each manager's direct-report count and payroll.
-- Why: Direct-team grain needs one self join, not full recursive descendants.
-- Expected: One row per manager with at least one direct report.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH direct_teams AS (
  SELECT e.manager_id,
         COUNT(*) AS direct_reports,
         SUM(e.salary) AS direct_report_payroll
  FROM employees AS e
  WHERE e.manager_id IS NOT NULL
  GROUP BY e.manager_id
)
SELECT manager.employee_id,
       manager.full_name,
       dt.direct_reports,
       ROUND(dt.direct_report_payroll, 2) AS direct_report_payroll
FROM direct_teams AS dt
JOIN employees AS manager
  ON manager.employee_id = dt.manager_id
ORDER BY dt.direct_reports DESC, manager.employee_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Identify hierarchy roots and leaves in one report.
-- Why: Create root and leaf CTEs at employee grain, then union compatible labeled rows.
-- Expected: One labeled row per root or leaf employee.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH roots AS (
  SELECT e.employee_id, e.full_name
  FROM employees AS e
  WHERE e.manager_id IS NULL
), leaves AS (
  SELECT e.employee_id, e.full_name
  FROM employees AS e
  WHERE NOT EXISTS (
    SELECT 1 FROM employees AS child
    WHERE child.manager_id = e.employee_id
  )
)
SELECT 'root' AS node_type, employee_id, full_name FROM roots
UNION ALL
SELECT 'leaf' AS node_type, employee_id, full_name FROM leaves
ORDER BY node_type, employee_id;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Count employees reachable from roots and compare with total employees.
-- Why: A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema.
-- Expected: One row with zero unreachable employees.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
WITH RECURSIVE organization AS (
  SELECT e.employee_id, ARRAY[e.employee_id] AS path
  FROM employees AS e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT child.employee_id, parent.path || child.employee_id
  FROM organization AS parent
  JOIN employees AS child
    ON child.manager_id = parent.employee_id
  WHERE NOT child.employee_id = ANY(parent.path)
)
SELECT (SELECT COUNT(*) FROM employees) AS all_employees,
       COUNT(DISTINCT employee_id) AS reachable_employees,
       (SELECT COUNT(*) FROM employees) - COUNT(DISTINCT employee_id) AS unreachable_employees
FROM organization;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Calculate full-subtree report counts per manager without counting the manager as their own report.
-- Why: Seed direct edges and recurse descendants while carrying the original manager.
-- Expected: One row per manager with descendant count.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH RECURSIVE descendants AS (
  SELECT parent.employee_id AS manager_id,
         child.employee_id AS report_id,
         ARRAY[parent.employee_id, child.employee_id] AS path
  FROM employees AS parent
  JOIN employees AS child
    ON child.manager_id = parent.employee_id
  UNION ALL
  SELECT d.manager_id,
         child.employee_id,
         d.path || child.employee_id
  FROM descendants AS d
  JOIN employees AS child
    ON child.manager_id = d.report_id
  WHERE NOT child.employee_id = ANY(d.path)
)
SELECT manager_id,
       COUNT(DISTINCT report_id) AS all_descendant_reports
FROM descendants
GROUP BY manager_id
ORDER BY all_descendant_reports DESC, manager_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Report department headcount split between managers and nonmanagers.
-- Why: First derive the manager ID set, then conditionally aggregate employees once.
-- Expected: One row per department.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH managers AS (
  SELECT DISTINCT e.manager_id AS employee_id
  FROM employees AS e
  WHERE e.manager_id IS NOT NULL
)
SELECT d.department_id,
       d.name,
       COUNT(e.employee_id) AS headcount,
       COUNT(e.employee_id) FILTER (
         WHERE m.employee_id IS NOT NULL
       ) AS managers,
       COUNT(e.employee_id) FILTER (
         WHERE m.employee_id IS NULL
       ) AS nonmanagers
FROM departments AS d
LEFT JOIN employees AS e
  ON e.department_id = d.department_id
LEFT JOIN managers AS m
  ON m.employee_id = e.employee_id
GROUP BY d.department_id, d.name
ORDER BY d.department_id;

-- No course answer persists changes or temporary objects.
ROLLBACK;
