-- Day 25: Multiple CTEs & Complex Hierarchies
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
-- 2. [Query writing] Report each manager's direct-report count and payroll.
--    Hint: Direct-team grain needs one self join, not full recursive descendants.
-- 3. [Query writing] Identify hierarchy roots and leaves in one report.
--    Hint: Create root and leaf CTEs at employee grain, then union compatible labeled rows.
-- 4. [Prediction] Count employees reachable from roots and compare with total employees.
--    Hint: A correct acyclic traversal should reach every employee exactly once in this parent-pointer schema.
-- 5. [Debugging] Calculate full-subtree report counts per manager without counting the manager as their own report.
--    Hint: Seed direct edges and recurse descendants while carrying the original manager.
-- 6. [Extension] Report department headcount split between managers and nonmanagers.
--    Hint: First derive the manager ID set, then conditionally aggregate employees once.

ROLLBACK;
