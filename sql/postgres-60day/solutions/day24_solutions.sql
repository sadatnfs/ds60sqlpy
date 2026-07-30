-- Day 24 executable solutions
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Build recursive CTEs from compatible anchor and recursive members, carrying depth/path evidence and an explicit termination or cycle rule.
-- Assumptions: Employee hierarchy roots have `manager_id IS NULL`; multiple roots are valid. Array paths use integer employee IDs.
-- Pitfall: `UNION ALL` without a cycle/termination guard can recurse indefinitely; `UNION` duplicate removal is not a substitute for a path rule.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: List every manager's direct and indirect reports with depth and path.
-- Why: Seed every direct edge, carry the original manager, and reject IDs already in the path.
-- Expected: One row per ancestor-descendant pair.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH RECURSIVE reports AS (
  SELECT manager.employee_id AS manager_id,
         report.employee_id AS report_id,
         1 AS depth,
         ARRAY[manager.employee_id, report.employee_id] AS path
  FROM employees AS manager
  JOIN employees AS report
    ON report.manager_id = manager.employee_id
  UNION ALL
  SELECT r.manager_id,
         report.employee_id,
         r.depth + 1,
         r.path || report.employee_id
  FROM reports AS r
  JOIN employees AS report
    ON report.manager_id = r.report_id
  WHERE NOT report.employee_id = ANY(r.path)
)
SELECT manager_id,
       report_id,
       depth,
       path
FROM reports
ORDER BY manager_id, depth, report_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Generate integers 1 through 100 recursively and return their sum.
-- Why: Anchor at 1 and stop producing rows after 100.
-- Expected: Exactly one row with 5050.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
WITH RECURSIVE numbers(n) AS (
  VALUES (1)
  UNION ALL
  SELECT n + 1
  FROM numbers
  WHERE n < 100
)
SELECT SUM(n) AS sum_1_to_100
FROM numbers;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Generate the first day of the current and prior 11 months recursively.
-- Why: Carry a counter as an explicit termination condition.
-- Expected: Exactly 12 chronological month rows.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - time normalization: makes reporting boundaries explicit; UTC is applied before deriving calendar buckets where required.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH RECURSIVE months(month_start, step) AS (
  SELECT date_trunc('month', CURRENT_DATE)::date, 1
  UNION ALL
  SELECT (month_start - INTERVAL '1 month')::date, step + 1
  FROM months
  WHERE step < 12
)
SELECT month_start
FROM months
ORDER BY month_start;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Traverse a local graph containing a cycle and prove a path-array guard terminates.
-- Why: Reject a destination already present in the path before adding it.
-- Expected: Finite paths starting from node 1; no repeated node inside a path.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH RECURSIVE edges(source, destination) AS (
  VALUES (1, 2), (2, 3), (3, 1), (2, 4)
), walk(node, path) AS (
  VALUES (1, ARRAY[1])
  UNION ALL
  SELECT e.destination,
         w.path || e.destination
  FROM walk AS w
  JOIN edges AS e
    ON e.source = w.node
  WHERE NOT e.destination = ANY(w.path)
)
SELECT node, path
FROM walk
ORDER BY array_length(path, 1), path;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Walk upward from every employee to ancestors while preventing cycles.
-- Why: The recursive step follows current manager ID to the manager row and appends it to path.
-- Expected: One row per employee-ancestor relation.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH RECURSIVE ancestors AS (
  SELECT e.employee_id AS origin_employee_id,
         e.manager_id AS ancestor_id,
         1 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees AS e
  WHERE e.manager_id IS NOT NULL
  UNION ALL
  SELECT a.origin_employee_id,
         manager.manager_id,
         a.depth + 1,
         a.path || manager.employee_id
  FROM ancestors AS a
  JOIN employees AS manager
    ON manager.employee_id = a.ancestor_id
  WHERE manager.manager_id IS NOT NULL
    AND NOT manager.employee_id = ANY(a.path)
)
SELECT origin_employee_id,
       ancestor_id,
       depth
FROM ancestors
WHERE ancestor_id IS NOT NULL
ORDER BY origin_employee_id, depth;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Summarize employee count by hierarchy depth from all roots.
-- Why: Build the guarded root traversal first, then aggregate only after depth is assigned.
-- Expected: One row per observed depth.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH RECURSIVE`: defines the anchor and repeated step; the stop or cycle rule is part of correctness.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `JOIN ... ON`: combines relations and may multiply rows; the match predicate and each input's grain must agree.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - set operation: combines compatible result shapes; the presence or absence of `ALL` controls duplicate preservation.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH RECURSIVE organization AS (
  SELECT e.employee_id,
         e.manager_id,
         0 AS depth,
         ARRAY[e.employee_id] AS path
  FROM employees AS e
  WHERE e.manager_id IS NULL
  UNION ALL
  SELECT child.employee_id,
         child.manager_id,
         parent.depth + 1,
         parent.path || child.employee_id
  FROM organization AS parent
  JOIN employees AS child
    ON child.manager_id = parent.employee_id
  WHERE NOT child.employee_id = ANY(parent.path)
)
SELECT depth,
       COUNT(*) AS employee_count
FROM organization
GROUP BY depth
ORDER BY depth;

-- No course answer persists changes or temporary objects.
ROLLBACK;
