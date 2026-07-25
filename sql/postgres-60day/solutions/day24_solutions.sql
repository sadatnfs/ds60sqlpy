-- Day 24 solutions: recursive CTEs
SET search_path TO training, public;

-- Exercise 1: every manager's direct and indirect reports.
WITH RECURSIVE reports AS (
  SELECT m.employee_id AS manager_id,
         e.employee_id AS report_id,
         1 AS depth,
         ARRAY[m.employee_id, e.employee_id] AS path
  FROM employees m
  JOIN employees e ON e.manager_id = m.employee_id

  UNION ALL

  SELECT r.manager_id,
         e.employee_id,
         r.depth + 1,
         r.path || e.employee_id
  FROM reports r
  JOIN employees e ON e.manager_id = r.report_id
  WHERE NOT e.employee_id = ANY(r.path)
)
SELECT r.manager_id,
       m.full_name AS manager,
       r.report_id,
       e.full_name AS report,
       r.depth,
       r.path
FROM reports r
JOIN employees m ON m.employee_id = r.manager_id
JOIN employees e ON e.employee_id = r.report_id
ORDER BY r.manager_id, r.depth, r.report_id;

-- Exercise 2: generate 1 through 100 and sum recursively.
WITH RECURSIVE numbers(n) AS (
  VALUES (1)
  UNION ALL
  SELECT n + 1
  FROM numbers
  WHERE n < 100
)
SELECT SUM(n) AS sum_1_to_100
FROM numbers;
