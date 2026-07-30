-- Day 24: Recursive CTEs
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Build recursive CTEs from compatible anchor and recursive members, carrying depth/path evidence and an explicit termination or cycle rule.
-- Assumptions: Employee hierarchy roots have `manager_id IS NULL`; multiple roots are valid. Array paths use integer employee IDs.
-- Pitfall: `UNION ALL` without a cycle/termination guard can recurse indefinitely; `UNION` duplicate removal is not a substitute for a path rule.
-- Predict row grain and NULL/order behavior before executing each example.

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
  -- A path is evidence of traversal and a guard against malformed cycles.
  WHERE NOT e.employee_id = ANY(o.path)
)
SELECT employee_id, full_name, manager_id, depth, path
FROM org
ORDER BY depth, full_name, employee_id
LIMIT 100;

-- Generate a sequence of dates (first day of month for last 12 months)
WITH RECURSIVE months AS (
  SELECT date_trunc('month', CURRENT_DATE)::date AS m, 1 AS n
  UNION ALL
  SELECT (m - interval '1 month')::date, n+1 FROM months WHERE n < 12
)
SELECT m AS month_start, n AS step
FROM months
ORDER BY month_start;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List every manager's direct and indirect reports with depth and path.
--    Hint: Seed every direct edge, carry the original manager, and reject IDs already in the path.
-- 2. [Query writing] Generate integers 1 through 100 recursively and return their sum.
--    Hint: Anchor at 1 and stop producing rows after 100.
-- 3. [Query writing] Generate the first day of the current and prior 11 months recursively.
--    Hint: Carry a counter as an explicit termination condition.
-- 4. [Prediction] Traverse a local graph containing a cycle and prove a path-array guard terminates.
--    Hint: Reject a destination already present in the path before adding it.
-- 5. [Debugging] Walk upward from every employee to ancestors while preventing cycles.
--    Hint: The recursive step follows current manager ID to the manager row and appends it to path.
-- 6. [Extension] Summarize employee count by hierarchy depth from all roots.
--    Hint: Build the guarded root traversal first, then aggregate only after depth is assigned.

ROLLBACK;
