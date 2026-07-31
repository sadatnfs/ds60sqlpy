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
--    Inputs: Use only the declared lesson objects (employees, departments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
-- 2. [Query writing] Report each manager's direct-report count and payroll.
--    Hint: Direct-team grain needs one self join, not full recursive descendants.
--    Inputs: Use only the declared lesson objects (employees, departments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 3. [Query writing] Identify hierarchy roots and leaves in one report.
--    Hint: Create root and leaf CTEs at employee grain, then union compatible labeled rows.
--    Inputs: Use only the declared lesson objects (employees, departments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 4. [Prediction] Count employees reachable from roots and compare with total employees.
--    Hint: A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema.
--    Inputs: Use only the declared lesson objects (employees, departments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 5. [Debugging] Calculate full-subtree report counts per manager without counting the manager as their own report.
--    Hint: Seed direct edges and recurse descendants while carrying the original manager.
--    Inputs: Use only the declared lesson objects (employees, departments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
-- 6. [Extension] Report department headcount split between managers and nonmanagers.
--    Hint: First derive the manager ID set, then conditionally aggregate employees once.
--    Inputs: Use only the declared lesson objects (employees, departments) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.

ROLLBACK;
