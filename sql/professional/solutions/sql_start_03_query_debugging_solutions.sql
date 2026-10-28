-- SQL-START-03: executable solutions and fail-fast checks
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

CREATE FUNCTION pg_temp.assert_true (ok boolean, message text)
  RETURNS void
  LANGUAGE plpgsql
  AS $assert$
BEGIN
  IF ok IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'Contract failed: %', message;
  END IF;
END
$assert$
;
-- Exercises: one isolated answer and verification per prompt.
-- 1. Build a checkpoint
SAVEPOINT exercise_1;

SELECT
  task_id,
  team,
  status,
  effort
FROM
  start_tasks
WHERE
  team = 'Red'
  AND status = 'open'
ORDER BY
  task_id;

CREATE TEMP TABLE solution_answer_1 ON COMMIT DROP AS
SELECT
  task_id, team, status, effort
FROM
  start_tasks
WHERE
  team = 'Red'
  AND status = 'open'
ORDER BY
  task_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(task_id ORDER BY task_id)
    FROM solution_answer_1) = ARRAY[1, 5], 'sql-start-03 exercise 1');

ROLLBACK TO SAVEPOINT exercise_1;

RELEASE SAVEPOINT exercise_1;

-- 2. Repair alias scope
SAVEPOINT exercise_2;

SELECT
  task_id,
  effort * 2 AS doubled_effort
FROM
  start_tasks
WHERE
  effort * 2 >= 6
ORDER BY
  task_id;

CREATE TEMP TABLE solution_answer_2 ON COMMIT DROP AS
SELECT
  task_id, effort * 2 AS doubled_effort
FROM
  start_tasks
WHERE
  effort * 2 >= 6
ORDER BY
  task_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(task_id ORDER BY task_id) = ARRAY[2, 4, 5]
    AND array_agg(doubled_effort ORDER BY task_id) = ARRAY[10, 6, 6] FROM solution_answer_2), 'sql-start-03 exercise 2');

ROLLBACK TO SAVEPOINT exercise_2;

RELEASE SAVEPOINT exercise_2;

-- 3. Repair Boolean grouping
SAVEPOINT exercise_3;

SELECT
  task_id,
  team,
  status
FROM
  start_tasks
WHERE
  team = 'Red'
  AND (status = 'open'
    OR status = 'blocked')
ORDER BY
  task_id;

CREATE TEMP TABLE solution_answer_3 ON COMMIT DROP AS
SELECT
  task_id, team, status
FROM
  start_tasks
WHERE
  team = 'Red'
  AND (status = 'open'
    OR status = 'blocked')
ORDER BY
  task_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(task_id ORDER BY task_id)
    FROM solution_answer_3) = ARRAY[1, 5], 'sql-start-03 exercise 3');

ROLLBACK TO SAVEPOINT exercise_3;

RELEASE SAVEPOINT exercise_3;

-- 4. Separate spelling from meaning
SAVEPOINT exercise_4;

SELECT
  task_id,
  effort
FROM
  start_tasks
ORDER BY
  task_id;

CREATE TEMP TABLE solution_answer_4 ON COMMIT DROP AS
SELECT
  task_id, effort
FROM
  start_tasks
ORDER BY
  task_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      count(*) = 6
    AND count(effort) = 5
    AND array_agg(task_id ORDER BY task_id) = ARRAY[1, 2, 3, 4, 5, 6] FROM solution_answer_4), 'sql-start-03 exercise 4');

ROLLBACK TO SAVEPOINT exercise_4;

RELEASE SAVEPOINT exercise_4;

-- 5. Debug a threshold boundary
SAVEPOINT exercise_5;

SELECT
  task_id,
  effort
FROM
  start_tasks
WHERE
  status = 'open'
  AND effort >= 3
ORDER BY
  task_id;

CREATE TEMP TABLE solution_answer_5 ON COMMIT DROP AS
SELECT
  task_id, effort
FROM
  start_tasks
WHERE
  status = 'open'
  AND effort >= 3
ORDER BY
  task_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(task_id ORDER BY task_id) = ARRAY[4, 5]
    AND min(effort) = 3
    AND max(effort) = 3 FROM solution_answer_5), 'sql-start-03 exercise 5');

ROLLBACK TO SAVEPOINT exercise_5;

RELEASE SAVEPOINT exercise_5;

-- 6. Combine a small reporting contract
SAVEPOINT exercise_6;

SELECT
  task_id,
  team,
  effort
FROM
  start_tasks
WHERE
  status = 'open'
ORDER BY
  effort DESC NULLS LAST,
  task_id
LIMIT 2;

CREATE TEMP TABLE solution_answer_6 ON COMMIT DROP AS
SELECT
  task_id, team, effort
FROM
  start_tasks
WHERE
  status = 'open'
ORDER BY
  effort DESC NULLS LAST, task_id
LIMIT 2;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(task_id ORDER BY effort DESC NULLS LAST, task_id)
    FROM solution_answer_6) = ARRAY[4, 5], 'sql-start-03 exercise 6');

ROLLBACK TO SAVEPOINT exercise_6;

RELEASE SAVEPOINT exercise_6;

ROLLBACK;
