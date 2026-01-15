-- Day 24: Recursive CTEs
BEGIN;
SET search_path TO training, public;

-- Organization hierarchy traversal
WITH RECURSIVE org AS (
  SELECT e.employee_id,
         e.full_name,
         e.manager_id,
         1 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT e.employee_id,
         e.full_name,
         e.manager_id,
         o.depth + 1,
         o.path || e.employee_id
  FROM employees e
  JOIN org o ON e.manager_id = o.employee_id
)
SELECT * FROM org
ORDER BY depth, full_name
LIMIT 100;

-- Generate a sequence of dates (first day of month for last 12 months)
WITH RECURSIVE months AS (
  SELECT date_trunc('month', CURRENT_DATE)::date AS m, 1 AS n
  UNION ALL
  SELECT (m - interval '1 month')::date, n+1 FROM months WHERE n < 12
)
SELECT * FROM months;

-- Exercises
-- 1) For each manager, list all direct and indirect reports with depth.
-- 2) Generate numbers 1..100 and sum them using a recursive CTE.

ROLLBACK;
