-- Day 25: Multiple CTEs & Complex Hierarchies
BEGIN;
SET search_path TO training, public;

WITH RECURSIVE base_org AS (
  SELECT e.employee_id, e.full_name, e.manager_id, 1 AS depth
  FROM employees e WHERE manager_id IS NULL
  UNION ALL
  SELECT e.employee_id, e.full_name, e.manager_id, b.depth+1
  FROM employees e JOIN base_org b ON e.manager_id = b.employee_id
), dept_counts AS (
  SELECT department_id, COUNT(*) AS headcount, ROUND(AVG(salary),2) AS avg_salary
  FROM employees GROUP BY department_id
)
SELECT d.name AS department, dc.headcount, dc.avg_salary
FROM dept_counts dc
LEFT JOIN departments d ON d.department_id = dc.department_id
ORDER BY headcount DESC;

-- Exercises
-- 1) Build a 3-level hierarchical report combining org and department aggregates.
-- 2) Create a CTE chain: filter -> enrich -> aggregate -> present.

ROLLBACK;
