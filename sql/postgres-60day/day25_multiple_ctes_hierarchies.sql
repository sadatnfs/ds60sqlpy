-- Day 25: Multiple CTEs & Complex Hierarchies
-- BEGINNER WORKFLOW — sql-25: Multiple CTEs Hierarchies
-- Guide: sql/postgres-60day/companion-guides/day25_multiple_ctes_hierarchies.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-25/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
  SELECT e.employee_id,
         e.manager_id,
         e.department_id,
         e.salary,
         1 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT e.employee_id,
         e.manager_id,
         e.department_id,
         e.salary,
         b.depth + 1,
         b.path || e.employee_id
  FROM employees e
  JOIN base_org b ON e.manager_id = b.employee_id
  WHERE NOT e.employee_id = ANY(b.path)
), dept_counts AS (
  -- Aggregate the traversed employee relation so the hierarchy CTE is an
  -- observable, testable stage rather than an unused declaration.
  SELECT department_id,
         COUNT(*) AS reachable_headcount,
         ROUND(AVG(salary), 2) AS avg_salary,
         MAX(depth) AS deepest_level
  FROM base_org
  GROUP BY department_id
)
SELECT d.department_id,
       d.name AS department,
       COALESCE(dc.reachable_headcount, 0) AS reachable_headcount,
       dc.avg_salary,
       dc.deepest_level
FROM departments d
LEFT JOIN dept_counts dc ON dc.department_id = d.department_id
ORDER BY reachable_headcount DESC, d.department_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Build a root-based organization CTE and report headcount and payroll by depth.
--    Hint: Assign depth during recursion, then aggregate employee rows once.
--    Inputs: For sql-25 Exercise 1, read from `employees`, and `organization`. Build the answer toward `depth`, `headcount`, and `payroll`; keep `depth` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-25 Exercise 1, expected output: One row per hierarchy depth. The final columns are `depth`, `headcount`, and `payroll`. The final order is `depth`.
--    Verify: For sql-25 Exercise 1, independently aggregate `employees`, and `organization` by `depth`; require one output row for every distinct `depth` tuple and compare `headcount`, and `payroll` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `headcount`, and `payroll` for the existing `depth` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-25 Exercise 1, start with the first relation in `employees`, and `organization`; after each join, record total rows and distinct `depth` so the exact fanout or loss is visible.
-- 2. [Query writing] Report each manager's direct-report count and payroll.
--    Hint: Direct-team grain needs one self join, not full recursive descendants.
--    Inputs: For sql-25 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll`; keep `employee_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-25 Exercise 2, expected output: One row per manager with at least one direct report. The final columns are `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll`. The final order is `dt.direct_reports DESC, manager.employee_id`.
--    Verify: For sql-25 Exercise 2, project `employee_id` plus the raw source columns from `employees` at each join stage; record row count and distinct `employee_id`, then assert the final `employee_id`, `full_name`, `direct_reports`, and `direct_report_payroll` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
--    Hint ladder, rung 1: For sql-25 Exercise 2, run `direct_teams` one at a time. Record each CTE's row count and `employee_id` uniqueness before the next stage uses it.
-- 3. [Query writing] Identify hierarchy roots and leaves in one report.
--    Hint: Create root and leaf CTEs at employee grain, then union compatible labeled rows.
--    Inputs: For sql-25 Exercise 3, read from `employees`. Build the answer toward `node_type`, `employee_id`, and `full_name`; keep `employee_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-25 Exercise 3, expected output: One labeled row per root or leaf employee. The final columns are `node_type`, `employee_id`, and `full_name`. The final order is `node_type, employee_id`.
--    Verify: For sql-25 Exercise 3, reselect the returned keys directly from the source; require unique `employee_id` where the expected grain is one row per key and confirm the projected `node_type`, `employee_id`, and `full_name` against `employees`. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
--    Hint ladder, rung 1: For sql-25 Exercise 3, run `roots`, and `leaves` one at a time. Record each CTE's row count and `employee_id` uniqueness before the next stage uses it.
-- 4. [Prediction] Count employees reachable from roots and compare with total employees.
--    Hint: A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema.
--    Inputs: For sql-25 Exercise 4, read from `employees`, and `organization`. Build the answer toward `all_employees`, `reachable_employees`, and `unreachable_employees`; keep `employee_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-25 Exercise 4, expected output: One row with zero unreachable employees. The final columns are `all_employees`, `reachable_employees`, and `unreachable_employees`.
--    Verify: For sql-25 Exercise 4, project `employee_id` plus the raw source columns from `employees`, and `organization` at each join stage; record row count and distinct `employee_id`, then assert the final `all_employees`, `reachable_employees`, and `unreachable_employees` values match those staged rows without unintended fanout or loss. Add one source row with a new `employee_id`; verify the result gains exactly one row carrying that `employee_id` value.
--    Hint ladder, rung 1: For sql-25 Exercise 4, start with the first relation in `employees`, and `organization`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
-- 5. [Debugging] Calculate full-subtree report counts per manager without counting the manager as their own report.
--    Hint: Seed direct edges and recurse descendants while carrying the original manager.
--    Inputs: For sql-25 Exercise 5, read from `employees`, and `descendants`. Build the answer toward `manager_id`, and `all_descendant_reports`; keep `manager_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-25 Exercise 5, expected output: One row per manager with descendant count. The final columns are `manager_id`, and `all_descendant_reports`. The final order is `all_descendant_reports DESC, manager_id`.
--    Verify: For sql-25 Exercise 5, independently aggregate `employees`, and `descendants` by `manager_id`; require one output row for every distinct `manager_id` tuple and compare `all_descendant_reports` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `all_descendant_reports` for the existing `manager_id` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-25 Exercise 5, start with the first relation in `employees`, and `descendants`; after each join, record total rows and distinct `manager_id` so the exact fanout or loss is visible.
-- 6. [Extension] Report department headcount split between managers and nonmanagers.
--    Hint: First derive the manager ID set, then conditionally aggregate employees once.
--    Inputs: For sql-25 Exercise 6, read from `employees`, and `departments`. Build the answer toward `department_id`, `name`, `headcount`, `managers`, and `nonmanagers`; keep `department_id`, and `name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-25 Exercise 6, expected output: One row per department. The final columns are `department_id`, `name`, `headcount`, `managers`, and `nonmanagers`. The final order is `d.department_id`.
--    Verify: For sql-25 Exercise 6, independently aggregate `employees`, and `departments` by `department_id`, and `name`; require one output row for every distinct `department_id`, and `name` tuple and compare `headcount`, `managers`, and `nonmanagers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `headcount`, `managers`, and `nonmanagers` for the existing `department_id`, and `name` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-25 Exercise 6, run `managers` one at a time. Record each CTE's row count and `department_id`, and `name` uniqueness before the next stage uses it.

ROLLBACK;
