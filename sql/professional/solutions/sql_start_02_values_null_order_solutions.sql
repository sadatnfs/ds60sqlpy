-- SQL-START-02: executable solutions and fail-fast checks
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

CREATE TEMP TABLE start_shipments (
  shipment_id integer PRIMARY KEY,
  weight numeric,
  label text
) ON COMMIT DROP;

INSERT INTO start_shipments (shipment_id, weight, label)
VALUES
  (1, 0, ''),
  (2, NULL, NULL),
  (3, 5, 'ready'),
  (4, 5, ''),
  (5, NULL, 'hold');

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
-- 1. Inspect missingness
SAVEPOINT exercise_1;

SELECT
  shipment_id,
  weight,
  weight IS NULL AS is_missing
FROM
  start_shipments
ORDER BY
  shipment_id;

CREATE TEMP TABLE solution_answer_1 ON COMMIT DROP AS
SELECT
  shipment_id, weight, weight IS NULL AS is_missing
FROM
  start_shipments
ORDER BY
  shipment_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(shipment_id ORDER BY shipment_id)
    FROM solution_answer_1
    WHERE
      is_missing) = ARRAY[2, 5], 'sql-start-02 exercise 1');

ROLLBACK TO SAVEPOINT exercise_1;

RELEASE SAVEPOINT exercise_1;

-- 2. Compare a complement with missingness
SAVEPOINT exercise_2;

SELECT
  shipment_id,
  weight
FROM
  start_shipments
WHERE
  NOT (weight > 0)
ORDER BY
  shipment_id;

CREATE TEMP TABLE solution_answer_2 ON COMMIT DROP AS
SELECT
  shipment_id, weight
FROM
  start_shipments
WHERE
  NOT (weight > 0)
ORDER BY
  shipment_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(shipment_id ORDER BY shipment_id)
    FROM solution_answer_2) = ARRAY[1], 'sql-start-02 exercise 2');

ROLLBACK TO SAVEPOINT exercise_2;

RELEASE SAVEPOINT exercise_2;

-- 3. Keep unknown and zero as separate categories
SAVEPOINT exercise_3;

SELECT
  shipment_id,
  weight
FROM
  start_shipments
WHERE
  weight = 0
  OR weight IS NULL
ORDER BY
  shipment_id;

CREATE TEMP TABLE solution_answer_3 ON COMMIT DROP AS
SELECT
  shipment_id, weight
FROM
  start_shipments
WHERE
  weight = 0
  OR weight IS NULL
ORDER BY
  shipment_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(shipment_id ORDER BY shipment_id) = ARRAY[1, 2, 5]
    AND count(weight) = 1 FROM solution_answer_3), 'sql-start-02 exercise 3');

ROLLBACK TO SAVEPOINT exercise_3;

RELEASE SAVEPOINT exercise_3;

-- 4. Specify every ordering decision
SAVEPOINT exercise_4;

SELECT
  shipment_id,
  weight
FROM
  start_shipments
ORDER BY
  weight DESC NULLS LAST,
  shipment_id
LIMIT 2;

CREATE TEMP TABLE solution_answer_4 ON COMMIT DROP AS
SELECT
  shipment_id, weight
FROM
  start_shipments
ORDER BY
  weight DESC NULLS LAST, shipment_id
LIMIT 2;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(shipment_id ORDER BY weight DESC NULLS LAST, shipment_id)
    FROM solution_answer_4) = ARRAY[3, 4], 'sql-start-02 exercise 4');

ROLLBACK TO SAVEPOINT exercise_4;

RELEASE SAVEPOINT exercise_4;

-- 5. Debug an empty text display policy
SAVEPOINT exercise_5;

SELECT
  shipment_id,
  label,
  COALESCE(NULLIF (label, ''), '(unlabeled)') AS display_label
FROM
  start_shipments
ORDER BY
  shipment_id;

CREATE TEMP TABLE solution_answer_5 ON COMMIT DROP AS
SELECT
  shipment_id, label, COALESCE(NULLIF (label, ''), '(unlabeled)') AS display_label
FROM
  start_shipments
ORDER BY
  shipment_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(display_label ORDER BY shipment_id)
    FROM solution_answer_5) = ARRAY['(unlabeled)', '(unlabeled)', 'ready', '(unlabeled)', 'hold'], 'sql-start-02 exercise 5');

ROLLBACK TO SAVEPOINT exercise_5;

RELEASE SAVEPOINT exercise_5;

-- 6. Transfer to a NULL-safe change detector
SAVEPOINT exercise_6;

SELECT
  shipment_id,
  old_weight,
  new_weight
FROM (
  VALUES (10, NULL::numeric, NULL::numeric),
    (11, 0, NULL),
    (12, 5, 5),
    (13, NULL, 0)) AS changes (shipment_id, old_weight, new_weight)
WHERE
  old_weight IS DISTINCT FROM new_weight
ORDER BY
  shipment_id;

CREATE TEMP TABLE solution_answer_6 ON COMMIT DROP AS
SELECT
  shipment_id, old_weight, new_weight
FROM (
  VALUES (10, NULL::numeric, NULL::numeric), (11, 0, NULL), (12, 5, 5), (13, NULL, 0)) AS changes (shipment_id, old_weight, new_weight)
WHERE
  old_weight IS DISTINCT FROM new_weight
ORDER BY
  shipment_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(shipment_id ORDER BY shipment_id)
    FROM solution_answer_6) = ARRAY[11, 13], 'sql-start-02 exercise 6');

ROLLBACK TO SAVEPOINT exercise_6;

RELEASE SAVEPOINT exercise_6;

ROLLBACK;
