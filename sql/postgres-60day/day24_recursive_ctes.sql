-- Day 24: Recursive CTEs
-- BEGINNER WORKFLOW — sql-24: Recursive CTEs
-- Guide: sql/postgres-60day/companion-guides/day24_recursive_ctes.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-24/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
--    Inputs: For sql-24 Exercise 1, read from `employees`, and `reports`. Build the answer toward `manager_id`, `report_id`, `depth`, and `path`; keep `manager_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-24 Exercise 1, expected output: One row per ancestor-descendant pair. The final columns are `manager_id`, `report_id`, `depth`, and `path`. The final order is `manager_id, depth, report_id`.
--    Verify: For sql-24 Exercise 1, project `manager_id` plus the raw source columns from `employees`, and `reports` at each join stage; record row count and distinct `manager_id`, then assert the final `manager_id`, `report_id`, `depth`, and `path` values match those staged rows without unintended fanout or loss. Add one source row with a new `manager_id`; verify the result gains exactly one row carrying that `manager_id` value.
--    Hint ladder, rung 1: For sql-24 Exercise 1, start with the first relation in `employees`, and `reports`; after each join, record total rows and distinct `manager_id` so the exact fanout or loss is visible.
-- 2. [Query writing] Generate integers 1 through 100 recursively and return their sum.
--    Hint: Anchor at 1 and stop producing rows after 100.
--    Inputs: For sql-24 Exercise 2, read from `numbers`. Compute `sum_1_to_100` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-24 Exercise 2, expected output: Exactly one row with 5050. The final columns are `sum_1_to_100`.
--    Verify: For sql-24 Exercise 2, evaluate each of `sum_1_to_100` in a separate control `SELECT` over `numbers`; require one final row and compare every value. Force the final predicate to match zero rows and record `sum_1_to_100`; distinguish `COUNT` zero from nullable `SUM` or `AVG` results.
--    Hint ladder, rung 1: For sql-24 Exercise 2, inspect the source keys that survive `WHERE`.
-- 3. [Query writing] Generate the first day of the current and prior 11 months recursively.
--    Hint: Carry a counter as an explicit termination condition.
--    Inputs: For sql-24 Exercise 3, read from `months`. Build the answer toward `month_start`; keep `month_start` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-24 Exercise 3, expected output: Exactly 12 chronological month rows. The final columns are `month_start`. The final order is `month_start`.
--    Verify: For sql-24 Exercise 3, reselect the returned keys directly from the source; require unique `month_start` where the expected grain is one row per key and confirm the projected `month_start` against `months`. Tie two rows on `month_start` and give them different `month_start` values; verify `month_start` chooses a stable first/last row.
--    Hint ladder, rung 1: For sql-24 Exercise 3, inspect the source keys that survive `WHERE`; then check `month_start` before applying the row cap.
-- 4. [Prediction] Traverse a local graph containing a cycle and prove a path-array guard terminates.
--    Hint: Reject a destination already present in the path before adding it.
--    Inputs: For sql-24 Exercise 4, read from `walk`, and `edges`. Build the answer toward `node`, and `path`; keep `node` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-24 Exercise 4, expected output: Finite paths starting from node 1; no repeated node inside a path. The final columns are `node`, and `path`. The final order is `array_length(path, 1), path`.
--    Verify: For sql-24 Exercise 4, project `node` plus the raw source columns from `walk`, and `edges` at each join stage; record row count and distinct `node`, then assert the final `node`, and `path` values match those staged rows without unintended fanout or loss. Add one source row with a new `node`; verify the result gains exactly one row carrying that `node` value.
--    Hint ladder, rung 1: For sql-24 Exercise 4, start with the first relation in `walk`, and `edges`; after each join, record total rows and distinct `node` so the exact fanout or loss is visible.
-- 5. [Debugging] Walk upward from every employee to ancestors while preventing cycles.
--    Hint: The recursive step follows current manager ID to the manager row and appends it to path.
--    Inputs: For sql-24 Exercise 5, read from `employees`, and `ancestors`. Build the answer toward `origin_employee_id`, `ancestor_id`, and `depth`; keep `employee_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-24 Exercise 5, expected output: One row per employee-ancestor relation. The final columns are `origin_employee_id`, `ancestor_id`, and `depth`. The final order is `origin_employee_id, depth`.
--    Verify: For sql-24 Exercise 5, project `employee_id` plus the raw source columns from `employees`, and `ancestors` at each join stage; record row count and distinct `employee_id`, then assert the final `origin_employee_id`, `ancestor_id`, and `depth` values match those staged rows without unintended fanout or loss. Add one row for which `(ancestor_id IS NOT NULL)` is true and one for which it is false; verify only the matching `employee_id` value is returned.
--    Hint ladder, rung 1: For sql-24 Exercise 5, start with the first relation in `employees`, and `ancestors`; after each join, record total rows and distinct `employee_id` so the exact fanout or loss is visible.
-- 6. [Extension] Summarize employee count by hierarchy depth from all roots.
--    Hint: Build the guarded root traversal first, then aggregate only after depth is assigned.
--    Inputs: For sql-24 Exercise 6, read from `employees`, and `organization`. Build the answer toward `depth`, and `employee_count`; keep `depth` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-24 Exercise 6, expected output: One row per observed depth. The final columns are `depth`, and `employee_count`. The final order is `depth`.
--    Verify: For sql-24 Exercise 6, independently aggregate `employees`, and `organization` by `depth`; require one output row for every distinct `depth` tuple and compare `employee_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `employee_count` for the existing `depth` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-24 Exercise 6, start with the first relation in `employees`, and `organization`; after each join, record total rows and distinct `depth` so the exact fanout or loss is visible.

ROLLBACK;
