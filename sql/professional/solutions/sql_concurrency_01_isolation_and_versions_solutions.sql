-- SQL-CONCURRENCY-01: executable solutions and fail-fast checks
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

CREATE TEMP TABLE concurrency_stock (
  sku text PRIMARY KEY,
  available integer NOT NULL CHECK (available >= 0),
  version integer NOT NULL CHECK (version > 0)
) ON COMMIT DROP;

INSERT INTO concurrency_stock
VALUES
  ('A', 5, 1),
  ('B', 1, 1);

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
-- 1. Perform a guarded reservation
SAVEPOINT exercise_1;

CREATE TEMP TABLE solution_answer_1 (
  sku text,
  available integer,
  version integer
) ON COMMIT DROP;

WITH changed AS (
  UPDATE
    concurrency_stock
  SET
    available = available - 2,
    version = version + 1
  WHERE
    sku = 'A'
    AND version = 1
    AND available >= 2
  RETURNING
    sku,
    available,
    version)
INSERT INTO solution_answer_1
SELECT
  sku,
  available,
  version
FROM
  changed;

SELECT
  sku,
  available,
  version
FROM
  solution_answer_1
ORDER BY
  sku;

SELECT
  pg_temp.assert_true ((
    SELECT
      count(*) = 1
    AND min(sku) = 'A'
    AND min(available) = 3
    AND min(version) = 2 FROM solution_answer_1), 'sql-concurrency-01 exercise 1');

ROLLBACK TO SAVEPOINT exercise_1;

RELEASE SAVEPOINT exercise_1;

-- 2. Reject a stale expected version
SAVEPOINT exercise_2;

CREATE TEMP TABLE solution_answer_2 (
  sku text,
  available integer,
  version integer
) ON COMMIT DROP;

WITH changed AS (
  UPDATE
    concurrency_stock
  SET
    available = available - 1,
    version = version + 1
  WHERE
    sku = 'A'
    AND version = 99
    AND available >= 1
  RETURNING
    sku,
    available,
    version)
INSERT INTO solution_answer_2
SELECT
  sku,
  available,
  version
FROM
  changed;

SELECT
  sku,
  available,
  version
FROM
  solution_answer_2
ORDER BY
  sku;

SELECT
  pg_temp.assert_true ((
    SELECT
      count(*)
    FROM solution_answer_2) = 0
  AND (
    SELECT
      available = 5
      AND version = 1
    FROM concurrency_stock
    WHERE
      sku = 'A'), 'sql-concurrency-01 exercise 2');

ROLLBACK TO SAVEPOINT exercise_2;

RELEASE SAVEPOINT exercise_2;

-- 3. Reject insufficient capacity independently
SAVEPOINT exercise_3;

CREATE TEMP TABLE solution_answer_3 (
  sku text,
  available integer,
  version integer
) ON COMMIT DROP;

WITH changed AS (
  UPDATE
    concurrency_stock
  SET
    available = available - 2,
    version = version + 1
  WHERE
    sku = 'B'
    AND version = 1
    AND available >= 2
  RETURNING
    sku,
    available,
    version)
INSERT INTO solution_answer_3
SELECT
  sku,
  available,
  version
FROM
  changed;

SELECT
  sku,
  available,
  version
FROM
  solution_answer_3
ORDER BY
  sku;

SELECT
  pg_temp.assert_true ((
    SELECT
      count(*)
    FROM solution_answer_3) = 0
  AND (
    SELECT
      available = 1
      AND version = 1
    FROM concurrency_stock
    WHERE
      sku = 'B'), 'sql-concurrency-01 exercise 3');

ROLLBACK TO SAVEPOINT exercise_3;

RELEASE SAVEPOINT exercise_3;

-- 4. Model two callers sharing an old version
SAVEPOINT exercise_4;

CREATE TEMP TABLE model_trace (
  caller text PRIMARY KEY,
  affected_rows bigint
) ON COMMIT DROP;

WITH changed AS (
  UPDATE
    concurrency_stock
  SET
    available = available - 2,
    version = version + 1
  WHERE
    sku = 'A'
    AND version = 1
    AND available >= 2
  RETURNING
    sku)
INSERT INTO model_trace
SELECT
  'One',
  count(*)
FROM
  changed;

WITH changed AS (
  UPDATE
    concurrency_stock
  SET
    available = available - 1,
    version = version + 1
  WHERE
    sku = 'A'
    AND version = 1
    AND available >= 1
  RETURNING
    sku)
INSERT INTO model_trace
SELECT
  'Two',
  count(*)
FROM
  changed;

SELECT
  caller,
  affected_rows
FROM
  model_trace
ORDER BY
  caller;

CREATE TEMP TABLE solution_answer_4 ON COMMIT DROP AS
SELECT
  caller, affected_rows
FROM
  model_trace;

SELECT
  pg_temp.assert_true ((
    SELECT
      count(*) = 2
    AND sum(affected_rows) = 1 FROM solution_answer_4)
  AND (
    SELECT
      affected_rows
    FROM solution_answer_4
    WHERE
      caller = 'One') = 1
  AND (
    SELECT
      affected_rows
    FROM solution_answer_4
  WHERE
    caller = 'Two') = 0, 'sql-concurrency-01 exercise 4');

ROLLBACK TO SAVEPOINT exercise_4;

RELEASE SAVEPOINT exercise_4;

-- 5. Verify a no-change read result
SAVEPOINT exercise_5;

SELECT
  sku,
  available,
  version
FROM
  concurrency_stock
ORDER BY
  sku;

CREATE TEMP TABLE solution_answer_5 ON COMMIT DROP AS
SELECT
  sku, available, version
FROM
  concurrency_stock
ORDER BY
  sku;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(sku ORDER BY sku) = ARRAY['A', 'B']
    AND array_agg(available ORDER BY sku) = ARRAY[5, 1]
    AND array_agg(version ORDER BY sku) = ARRAY[1, 1] FROM solution_answer_5), 'sql-concurrency-01 exercise 5');

ROLLBACK TO SAVEPOINT exercise_5;

RELEASE SAVEPOINT exercise_5;

-- 6. Transfer the guard to an atomic replenishment
SAVEPOINT exercise_6;

CREATE TEMP TABLE solution_answer_6 (
  sku text,
  available integer,
  version integer
) ON COMMIT DROP;

WITH changed AS (
  UPDATE
    concurrency_stock
  SET
    available = available + 3,
    version = version + 1
  WHERE
    sku = 'B'
    AND version = 1
  RETURNING
    sku,
    available,
    version)
INSERT INTO solution_answer_6
SELECT
  sku,
  available,
  version
FROM
  changed;

SELECT
  sku,
  available,
  version
FROM
  solution_answer_6
ORDER BY
  sku;

SELECT
  pg_temp.assert_true ((
    SELECT
      count(*) = 1
    AND min(sku) = 'B'
    AND min(available) = 4
    AND min(version) = 2 FROM solution_answer_6), 'sql-concurrency-01 exercise 6');

WITH repeated AS (
  UPDATE
    concurrency_stock
  SET
    available = available + 3,
    version = version + 1
  WHERE
    sku = 'B'
    AND version = 1
  RETURNING
    sku
)
SELECT
  pg_temp.assert_true ((
    SELECT
      count(*)
    FROM repeated) = 0, 'old replenishment version rejected');

ROLLBACK TO SAVEPOINT exercise_6;

RELEASE SAVEPOINT exercise_6;

ROLLBACK;
