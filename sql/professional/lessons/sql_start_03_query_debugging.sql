-- SQL-START-03: Query Construction and Debugging
-- Guide: sql/professional/companion-guides/sql_start_03_query_debugging.md
-- Use Create/open guided SQL notebook and the ignored learner copy.
-- Run the complete file with psql -X -v ON_ERROR_STOP=1.
-- Only the local disposable advanced_sql_training database is permitted.
-- Setup is supplied. Write attempts before the final ROLLBACK.
BEGIN;
DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
END
$course_target$;
SET LOCAL TIME ZONE 'UTC';
SET LOCAL statement_timeout = '15s';
CREATE TEMP TABLE start_tasks (
  task_id integer PRIMARY KEY,
  team text NOT NULL,
  status text NOT NULL,
  effort integer
) ON COMMIT DROP;
INSERT INTO start_tasks (task_id, team, status, effort)
VALUES
  (1, 'Red', 'open', 2),
  (2, 'Red', 'closed', 5),
  (3, 'Blue', 'open', NULL),
  (4, 'Blue', 'open', 3),
  (5, 'Red', 'open', 3),
  (6, 'Blue', 'blocked', 0);
-- Example 1: Watch a predicate narrow the identities
-- Expected: Four rows, columns task_id, team, status, effort; IDs 1,3,4,5. ID 3 still has NULL effort.
SELECT
  task_id,
  team,
  status,
  effort
FROM
  start_tasks
WHERE
  status = 'open'
ORDER BY
  task_id;
-- Example 2: Compute a label without using it too early
-- Expected: Three rows with columns task_id, doubled_effort: (2,10), (4,6), (5,6).
SELECT
  task_id,
  effort * 2 AS doubled_effort
FROM
  start_tasks
WHERE
  effort * 2 >= 6
ORDER BY
  doubled_effort DESC,
  task_id;
-- Exercises
-- Keep predictions and attempts in your own working copy.
-- 1. Build a stage.
-- Inputs/evidence: For sql-start-03 Exercise 1, Return Red open tasks with task_id, team, status, effort. First predict all Red IDs and then the IDs remaining after the open restriction.
-- Expected result/shape: For sql-start-03 Exercise 1, Two task rows with columns task_id, team, status, effort; final ORDER BY task_id: IDs 1 and 5. The Red-only checkpoint has IDs 1,2,5.
-- Verify: For sql-start-03 Exercise 1, Inspect the Red-only stage IDs 1,2,5, then confirm only 1,5 remain after the status filter. Task 2 is the closed negative control.
-- Hint: Add one AND restriction after confirming the first filter.
-- 2. Repair alias scope.
-- Inputs/evidence: For sql-start-03 Exercise 2, Repair SELECT task_id, effort * 2 AS doubled_effort FROM start_tasks WHERE doubled_effort >= 6. Return task_id, doubled_effort in ascending task_id order without introducing a subquery.
-- Expected result/shape: For sql-start-03 Exercise 2, Three task rows, columns task_id, doubled_effort; final ORDER BY task_id: (2,10),(4,6),(5,6). The original same-level alias reference produces undefined_column, SQLSTATE 42703.
-- Verify: For sql-start-03 Exercise 2, Inspect pairs (2,10),(4,6),(5,6), preserving both inclusive boundary values of 6. The original alias attempt reports undefined_column SQLSTATE 42703.
-- Hint: WHERE sees input columns; SELECT creates the alias later in the logical model.
-- 3. Repair Boolean grouping.
-- Inputs/evidence: For sql-start-03 Exercise 3, Return Red tasks whose status is open or blocked, with task_id, team, status. Diagnose the unparenthesized predicate team = 'Red' AND status = 'open' OR status = 'blocked'.
-- Expected result/shape: For sql-start-03 Exercise 3, Two task rows with columns task_id, team, status; final ORDER BY task_id: IDs 1 and 5. The faulty predicate also returns Blue blocked task 6.
-- Verify: For sql-start-03 Exercise 3, Trace Blue blocked task 6 through the faulty and repaired predicates. It appears only before grouping the status alternatives; the repaired IDs are 1,5.
-- Hint: Trace task 6 through each part of the original expression.
-- 4. Separate spelling from meaning.
-- Inputs/evidence: For sql-start-03 Exercise 4, Diagnose SELECT task_id, effrot FROM start_tasks and repair it to return task_id, effort for every task. State the error category before changing code.
-- Expected result/shape: For sql-start-03 Exercise 4, Six rows with columns task_id, effort; final ORDER BY task_id. The misspelled input name produces undefined_column, SQLSTATE 42703; the corrected result includes ID 3 with NULL effort.
-- Verify: For sql-start-03 Exercise 4, Capture undefined_column SQLSTATE 42703 for the misspelling in a separate attempted run, then inspect six corrected task identities and the retained NULL effort at ID 3.
-- Hint: Compare the requested column against the fixture declaration.
-- 5. Debug a threshold boundary.
-- Inputs/evidence: For sql-start-03 Exercise 5, Return open tasks with known effort at least 3, projecting task_id, effort. Explain the difference between >= 3 and > 3 on this fixture.
-- Expected result/shape: For sql-start-03 Exercise 5, Two task rows, columns task_id, effort; final ORDER BY task_id: (4,3),(5,3). The strict > 3 version returns zero rows; missing effort does not qualify.
-- Verify: For sql-start-03 Exercise 5, Require IDs 4 and 5 with effort 3. Independently try the strict comparison and observe zero qualifying open rows; closed ID 2 remains excluded in either case.
-- Hint: At least includes the boundary value itself.
-- 6. Combine a small reporting contract.
-- Inputs/evidence: For sql-start-03 Exercise 6, Return the first two open tasks ranked by largest effort, keeping unknown effort last, with task_id, team, effort. Explain every clause and its logical role.
-- Expected result/shape: For sql-start-03 Exercise 6, Two task rows, columns task_id, team, effort; final ORDER BY effort DESC NULLS LAST, task_id: IDs 4 and 5, both effort 3. ID 3 is unknown, and closed task 2 is ineligible.
-- Verify: For sql-start-03 Exercise 6, Compare final IDs 4,5 with the open-stage identities 1,3,4,5. Closed task 2 cannot enter despite its larger effort, and unknown task 3 cannot rank first.
-- Hint: Filter eligibility before defining the ranking and row limit.
ROLLBACK;
