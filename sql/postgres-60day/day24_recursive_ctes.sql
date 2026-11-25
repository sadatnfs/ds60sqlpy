-- Day 24: Recursive CTEs
-- BEGINNER WORKFLOW - sql-24: Recursive CTEs
-- Guide: sql/postgres-60day/companion-guides/day24_recursive_ctes.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-24.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: employees.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Build recursive CTEs from compatible anchor and recursive members, carrying depth/path evidence and an explicit termination or cycle rule.
-- Assumptions: Employee hierarchy roots have `manager_id IS NULL`; multiple roots are valid. Array paths use integer employee IDs.
-- Pitfall: `UNION ALL` without a cycle/termination guard can recurse indefinitely; `UNION` duplicate removal is not a substitute for a path rule.
-- Predict row grain and NULL/order behavior before executing each example.
-- Organization hierarchy traversal
WITH RECURSIVE org AS (
  SELECT
    e.employee_id,
    e.full_name,
    e.manager_id,
    1 AS depth,
    ARRAY[e.employee_id] AS path
  FROM
    employees e
  WHERE
    e.manager_id IS NULL
  UNION ALL
  SELECT
    e.employee_id,
    e.full_name,
    e.manager_id,
    o.depth + 1,
    o.path || e.employee_id
  FROM
    employees e
    JOIN org o ON e.manager_id = o.employee_id
    -- A path is evidence of traversal and a guard against malformed cycles.
  WHERE
    NOT e.employee_id = ANY (o.path))
SELECT
  employee_id,
  full_name,
  manager_id,
  depth,
  path
FROM
  org
ORDER BY
  depth,
  full_name,
  employee_id
LIMIT 100;

-- Generate a sequence of dates (first day of month for last 12 months)
WITH RECURSIVE months AS (
  SELECT
    date_trunc('month', CURRENT_DATE)::date AS m,
    1 AS n
  UNION ALL
  SELECT
    (m - interval '1 month')::date,
    n + 1
  FROM
    months
  WHERE
    n < 12
)
SELECT
  m AS month_start,
  n AS step
FROM
  months
ORDER BY
  month_start;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List every manager's direct and indirect reports with depth and path.
--    Hint: Seed every direct edge, carry the original manager, and reject IDs already in the path.
--    Inputs: For sql-24 Exercise 1, read `employees` twice in the anchor, joining each report to its manager on `report.manager_id = manager.employee_id` (94 direct pairs), then join the recursive `reports` CTE back to `employees` on `report.manager_id = r.report_id`, appending to `path` and refusing any `employee_id` already in it.
--    Expected result/shape: For sql-24 Exercise 1, expected output: 186 rows, 94 at depth 1 and 92 at depth 2, for only three managers: employee 1 with 93 reports, employee 8 with 92, and employee 2 with 1. The final columns are `manager_id`, `report_id`, `depth`, and `path`. The final order is `manager_id, depth, report_id`.
--    Verify: For sql-24 Exercise 1, confirm the 94 depth-1 rows match `SELECT COUNT(*) FROM employees WHERE manager_id IS NOT NULL` and that all 92 depth-2 rows belong to manager 1 with a `path` starting `{1,8}`; then, inside `BEGIN ... ROLLBACK`, run `UPDATE employees SET manager_id = 9 WHERE employee_id = 1` to close the loop 1, 8, 9, 1 and confirm the query still finishes, now with 280 rows and a maximum depth of 3.
--    Hint ladder, rung 1: For sql-24 Exercise 1, start with the first relation in `employees`, and `reports`; after each join, record total rows and distinct `manager_id` so the exact fanout or loss is visible.
-- 2. [Query writing] Generate integers 1 through 100 recursively and return their sum.
--    Hint: Anchor at 1 and stop producing rows after 100.
--    Inputs: For sql-24 Exercise 2, no table is read: the recursive `numbers` CTE starts from `VALUES (1)` and adds `n + 1` while `n < 100`, and the outer query applies one `SUM` with no `GROUP BY`.
--    Expected result/shape: For sql-24 Exercise 2, expected output: exactly one row, `sum_1_to_100` = 5050. The final columns are `sum_1_to_100`.
--    Verify: For sql-24 Exercise 2, compare with the non-recursive control `SELECT SUM(n) FROM generate_series(1, 100) AS n`, which also returns 5050, and add `COUNT(*)` to see exactly 100 generated rows; then change the stop test to `n <= 100` and confirm the CTE produces 101 rows and a sum of 5151, the classic off-by-one in a recursive stop condition.
--    Hint ladder, rung 1: For sql-24 Exercise 2, inspect the source keys that survive `WHERE`.
-- 3. [Query writing] Generate the first day of the current and prior 11 months recursively.
--    Hint: Carry a counter as an explicit termination condition.
--    Inputs: For sql-24 Exercise 3, no table is read: the recursive `months` CTE starts at `date_trunc('month', CURRENT_DATE)::date` with `step` 1 and subtracts `INTERVAL '1 month'` while `step < 12`, so the result moves with the run date.
--    Expected result/shape: For sql-24 Exercise 3, expected output: exactly 12 rows, all on day 1 of a month, from 11 months before the current month up to the current month (2025-12-01 through 2026-11-01 when run in November 2026). The final columns are `month_start`. The final order is `month_start`.
--    Verify: For sql-24 Exercise 3, confirm `COUNT(*)` is 12, `COUNT(DISTINCT month_start)` is 12, `MAX(month_start)` equals `date_trunc('month', CURRENT_DATE)::date`, and no row fails `EXTRACT(DAY FROM month_start) = 1`; then start the same recursion from `DATE '2026-03-31'` without `date_trunc` and see the values drift to 2026-02-28 and 2026-01-28, which is why the anchor truncates first.
--    Hint ladder, rung 1: For sql-24 Exercise 3, inspect the source keys that survive `WHERE`; then check `month_start` before applying the row cap.
-- 4. [Prediction] Traverse a local graph containing a cycle and prove a path-array guard terminates.
--    Hint: Reject a destination already present in the path before adding it.
--    Inputs: For sql-24 Exercise 4, no table is read: the `edges` CTE holds four `VALUES` pairs, (1, 2), (2, 3), (3, 1), and (2, 4), with the cycle 1, 2, 3, 1; the recursive `walk` CTE starts at `VALUES (1, ARRAY[1])` and follows edges while `NOT e.destination = ANY (w.path)`.
--    Expected result/shape: For sql-24 Exercise 4, expected output: exactly 4 rows, `{1}`, `{1,2}`, `{1,2,3}`, and `{1,2,4}`, with nodes 1, 2, 3, and 4; the edge from 3 back to 1 is never taken. The final columns are `node`, and `path`. The final order is `array_length(path, 1), path`.
--    Verify: For sql-24 Exercise 4, confirm no `path` repeats a node, for example `SELECT COUNT(*) FROM walk WHERE array_length(path, 1) <> (SELECT COUNT(DISTINCT x) FROM unnest(path) AS x)` returns 0; then replace the path guard with a depth cap `array_length(w.path, 1) < 5` and confirm two extra rows, `{1,2,3,1}` and `{1,2,3,1,2}`, revisit node 1, so only the `ANY (path)` guard makes the walk end on its own.
--    Hint ladder, rung 1: For sql-24 Exercise 4, start with the first relation in `walk`, and `edges`; after each join, record total rows and distinct `node` so the exact fanout or loss is visible.
-- 5. [Debugging] Walk upward from every employee to ancestors while preventing cycles.
--    Hint: The recursive step follows current manager ID to the manager row and appends it to path.
--    Inputs: For sql-24 Exercise 5, read `employees`: the anchor takes the 94 rows with a non-NULL `manager_id`, and the recursive `ancestors` CTE joins `employees` as `manager` on `manager.employee_id = a.ancestor_id`, climbing while `manager.manager_id IS NOT NULL` and the manager is not already in `path`.
--    Expected result/shape: For sql-24 Exercise 5, expected output: 186 rows for 94 origin employees, 94 at depth 1 and 92 at depth 2; employee 9 has ancestor 8 at depth 1 and ancestor 1 at depth 2, while employee 8 has only ancestor 1. The final columns are `origin_employee_id`, `ancestor_id`, and `depth`. The final order is `origin_employee_id, depth`.
--    Verify: For sql-24 Exercise 5, confirm `COUNT(DISTINCT origin_employee_id)` is 94, matching `SELECT COUNT(*) FROM employees WHERE manager_id IS NOT NULL`, and that removing the outer `ancestor_id IS NOT NULL` filter leaves 186 rows; then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm the query returns 374 rows with a maximum depth of 4, and that employee 1 now lists ancestors 9, 8, and itself at depths 1, 2, and 3.
--    Hint ladder, rung 1: For sql-24 Exercise 5, start with the first relation in `employees`, and `ancestors`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
-- 6. [Extension] Summarize employee count by hierarchy depth from all roots.
--    Hint: Build the guarded root traversal first, then aggregate only after depth is assigned.
--    Inputs: For sql-24 Exercise 6, read `employees`: the anchor of the recursive `organization` CTE takes the 6 roots with `manager_id IS NULL` at depth 0, the recursive step joins children on `child.manager_id = parent.employee_id`, and the outer query counts rows per `depth`.
--    Expected result/shape: For sql-24 Exercise 6, expected output: exactly 3 rows, depth 0 with 6 employees, depth 1 with 2, and depth 2 with 92. The final columns are `depth`, and `employee_count`. The final order is `depth`.
--    Verify: For sql-24 Exercise 6, confirm the counts add to 100, matching `SELECT COUNT(*) FROM employees`, and that the depth-1 count of 2 matches `SELECT COUNT(*) FROM employees WHERE manager_id IN (SELECT employee_id FROM employees WHERE manager_id IS NULL)`; then, inside `BEGIN ... ROLLBACK`, set `manager_id = 9` for employee 1 and confirm only 6 employees remain (5 at depth 0, 1 at depth 1), because the 94 people in the loop through employee 1 no longer hang from any root.
--    Hint ladder, rung 1: For sql-24 Exercise 6, start with the first relation in `employees`, and `organization`; after each join, record total rows and distinct `depth` so the exact fanout or loss is visible.
ROLLBACK;
