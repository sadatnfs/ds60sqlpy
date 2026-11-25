-- Day 25: Multiple CTEs & Complex Hierarchies
-- BEGINNER WORKFLOW - sql-25: Multiple CTEs and Hierarchies
-- Guide: sql/postgres-60day/companion-guides/day25_multiple_ctes_hierarchies.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-25.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: employees, departments.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Compose multiple CTEs so hierarchy traversal, employee grain, and management summaries remain individually testable.
-- Assumptions: The employee graph can have multiple roots. Payroll uses exact salary numeric and each employee should contribute once per intended output grain.
-- Pitfall: Joining ancestor-descendant pairs to employee facts can count one employee multiple times; state whether output is direct-team or full-subtree grain.
-- Predict row grain and NULL/order behavior before executing each example.
WITH RECURSIVE base_org AS (
  SELECT
    e.employee_id,
    e.manager_id,
    e.department_id,
    e.salary,
    1 AS depth,
    ARRAY[e.employee_id] AS path
  FROM
    employees e
  WHERE
    e.manager_id IS NULL
  UNION ALL
  SELECT
    e.employee_id,
    e.manager_id,
    e.department_id,
    e.salary,
    b.depth + 1,
    b.path || e.employee_id
  FROM
    employees e
    JOIN base_org b ON e.manager_id = b.employee_id
  WHERE
    NOT e.employee_id = ANY (b.path)
),
dept_counts AS (
  -- Aggregate the traversed employee relation so the hierarchy CTE is an
  -- observable, testable stage rather than an unused declaration.
  SELECT
    department_id,
    COUNT(*) AS reachable_headcount,
    ROUND(AVG(salary), 2) AS avg_salary,
    MAX(depth) AS deepest_level
  FROM
    base_org
  GROUP BY
    department_id
)
SELECT
  d.department_id,
  d.name AS department,
  COALESCE(dc.reachable_headcount, 0) AS reachable_headcount,
  dc.avg_salary,
  dc.deepest_level
FROM
  departments d
  LEFT JOIN dept_counts dc ON dc.department_id = d.department_id
ORDER BY
  reachable_headcount DESC,
  d.department_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Build a root-based organization CTE and report headcount and payroll by depth.
--    Hint: Assign depth during recursion, then aggregate employee rows once.
--    Inputs: For sql-25 Exercise 1, read `employees`: the recursive `organization` CTE starts at the 6 roots with `manager_id IS NULL`, carries each child's `salary` and `depth`, and guards against cycles with `path`; the outer query groups that CTE by `depth`.
--    Expected result/shape: For sql-25 Exercise 1, expected output: exactly 3 rows, depth 0 with 6 people and 241662.99 payroll, depth 1 with 2 and 81187.85, and depth 2 with 92 and 4077058.66. The final columns are `depth`, `headcount`, and `payroll`. The final order is `depth`.
--    Verify: For sql-25 Exercise 1, confirm the headcounts add to 100 and the payrolls to 4399909.50, matching `SELECT COUNT(*), ROUND(SUM(salary), 2) FROM employees`, and that the depth-1 payroll equals the two single-report payrolls in Exercise 2 (40633.52 + 40554.33); then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm only 5 people remain at depth 0 and 1 at depth 1.
--    Hint ladder, rung 1: For sql-25 Exercise 1, start with the first relation in `employees`, and `organization`; after each join, record total rows and distinct `depth` so the exact fanout or loss is visible.
-- 2. [Query writing] Report each manager's direct-report count and payroll.
--    Hint: Direct-team grain needs one self join, not full recursive descendants.
--    Inputs: For sql-25 Exercise 2, read `employees` once in `direct_teams`, grouping the 94 rows with a non-NULL `manager_id` by that `manager_id`, then join the CTE back to `employees` as `manager` to fetch `full_name`.
--    Expected result/shape: For sql-25 Exercise 2, expected output: exactly 3 rows, employee 8 with 92 direct reports and 4077058.66 of payroll, then employees 1 and 2 with 1 report each (40633.52 and 40554.33). The final columns are `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll`. The final order is `dt.direct_reports DESC, manager.employee_id`.
--    Verify: For sql-25 Exercise 2, confirm the `direct_reports` values add to 94 and the payrolls to 4158246.51, matching `SELECT COUNT(*), ROUND(SUM(salary), 2) FROM employees WHERE manager_id IS NOT NULL`, and that `SELECT COUNT(DISTINCT manager_id) FROM employees` also returns 3; employees 1 and 2 tie at one report, so only the `manager.employee_id` tiebreaker keeps employee 1 ahead.
--    Hint ladder, rung 1: For sql-25 Exercise 2, run `direct_teams` one at a time. Record each CTE's row count and `employee_id` uniqueness before the next stage uses it.
-- 3. [Query writing] Identify hierarchy roots and leaves in one report.
--    Hint: Create root and leaf CTEs at employee grain, then union compatible labeled rows.
--    Inputs: For sql-25 Exercise 3, read `employees` in two CTEs: `roots` keeps the 6 rows with `manager_id IS NULL`, and `leaves` keeps rows for which `NOT EXISTS` finds no child pointing at them; the outer query labels each CTE and stacks them with `UNION ALL`.
--    Expected result/shape: For sql-25 Exercise 3, expected output: 103 rows, 97 `leaf` rows followed by 6 `root` rows (employees 1 through 6); employees 3, 4, 5, and 6 appear twice because they have no manager and no reports. The final columns are `node_type`, `employee_id`, and `full_name`. The final order is `node_type, employee_id`.
--    Verify: For sql-25 Exercise 3, count rows by `node_type` and confirm 97 and 6, and that `SELECT employee_id FROM employees e WHERE manager_id IS NULL AND NOT EXISTS (SELECT 1 FROM employees c WHERE c.manager_id = e.employee_id)` returns exactly 3, 4, 5, and 6; then rewrite the leaf test as `employee_id NOT IN (SELECT manager_id FROM employees)` and confirm it returns 0 leaves, because the 6 NULL `manager_id` values make every `NOT IN` test unknown.
--    Hint ladder, rung 1: For sql-25 Exercise 3, run `roots`, and `leaves` one at a time. Record each CTE's row count and `employee_id` uniqueness before the next stage uses it.
-- 4. [Prediction] Count employees reachable from roots and compare with total employees.
--    Hint: A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema.
--    Inputs: For sql-25 Exercise 4, read `employees` twice: the recursive `organization` CTE walks down from the 6 roots with a `path` guard, and two scalar subqueries count the full table; the outer query compares `COUNT(DISTINCT employee_id)` from the CTE with that total and has no `GROUP BY`.
--    Expected result/shape: For sql-25 Exercise 4, expected output: exactly one row, 100 `all_employees`, 100 `reachable_employees`, and 0 `unreachable_employees`. The final columns are `all_employees`, `reachable_employees`, and `unreachable_employees`.
--    Verify: For sql-25 Exercise 4, confirm the CTE returns 100 rows and 100 distinct `employee_id` values, so no employee is reached twice; then, inside `BEGIN ... ROLLBACK`, run `UPDATE employees SET manager_id = 9 WHERE employee_id = 1` and confirm the row changes to 100, 6, and 94, because employee 1, employee 8, and the 92 reports under 8 form a loop with no root.
--    Hint ladder, rung 1: For sql-25 Exercise 4, start with the first relation in `employees`, and `organization`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
-- 5. [Debugging] Calculate full-subtree report counts per manager without counting the manager as their own report.
--    Hint: Seed direct edges and recurse descendants while carrying the original manager.
--    Inputs: For sql-25 Exercise 5, read `employees` twice in the anchor of the recursive `descendants` CTE (each manager joined to direct children, with `path` seeded as `ARRAY[parent, child]`), then keep joining children of `report_id`; the outer query groups by `manager_id`.
--    Expected result/shape: For sql-25 Exercise 5, expected output: exactly 3 rows, manager 1 with 93 descendants, manager 8 with 92, and manager 2 with 1. The final columns are `manager_id`, and `all_descendant_reports`. The final order is `all_descendant_reports DESC, manager_id`.
--    Verify: For sql-25 Exercise 5, confirm manager 8's 92 matches `SELECT COUNT(*) FROM employees WHERE manager_id = 8`, manager 1's 93 is that 92 plus employee 8 itself, `COUNT(*)` equals `COUNT(DISTINCT report_id)` for each manager, and no row has `report_id = manager_id`; then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm managers 1, 8, and 9 each return 93 and still never count themselves.
--    Hint ladder, rung 1: For sql-25 Exercise 5, start with the first relation in `employees`, and `descendants`; after each join, record total rows and distinct `manager_id` so the exact fanout or loss is visible.
-- 6. [Extension] Report department headcount split between managers and nonmanagers.
--    Hint: First derive the manager ID set, then conditionally aggregate employees once.
--    Inputs: For sql-25 Exercise 6, read all 6 `departments`, `LEFT JOIN` their 100 `employees`, and `LEFT JOIN` the `managers` CTE, which holds the 3 distinct non-NULL `manager_id` values; the `FILTER` clauses split each department's count on whether that join found a match.
--    Expected result/shape: For sql-25 Exercise 6, expected output: exactly 6 rows; Sales has 17 people (1 manager), Engineering 17 (2 managers), HR and Finance 17 each, and Marketing and Operations 16 each, all with 0 managers. The final columns are `department_id`, `name`, `headcount`, `managers`, and `nonmanagers`. The final order is `d.department_id`.
--    Verify: For sql-25 Exercise 6, confirm `headcount` adds to 100, `managers` adds to 3, and `managers + nonmanagers = headcount` on every row; then, inside `BEGIN ... ROLLBACK`, run `INSERT INTO departments (department_id, name) VALUES (7, 'Legal')` and confirm a seventh row with 0, 0, and 0, while `COUNT(*)` would wrongly report 1 for that empty department.
--    Hint ladder, rung 1: For sql-25 Exercise 6, run `managers` one at a time. Record each CTE's row count and `department_id`, and `name` uniqueness before the next stage uses it.
ROLLBACK;
