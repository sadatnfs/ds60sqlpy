-- SQL-START-01: executable solutions and fail-fast checks

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

CREATE TEMP TABLE start_readings (
    reading_id integer PRIMARY KEY,
    station text NOT NULL,
    reading_day date NOT NULL,
    temperature numeric
) ON COMMIT DROP;
INSERT INTO start_readings (reading_id, station, reading_day, temperature) VALUES
(1, 'North', DATE '2024-01-01', 18),
(2, 'North', DATE '2024-01-02', 18),
(3, 'South', DATE '2024-01-01', 0),
(4, 'South', DATE '2024-01-02', NULL),
(5, 'West', DATE '2024-01-01', -4),
(6, 'North', DATE '2024-01-03', 20);

CREATE FUNCTION pg_temp.assert_true(ok boolean, message text)
RETURNS void LANGUAGE plpgsql AS $assert$
BEGIN
  IF ok IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'Contract failed: %', message;
  END IF;
END
$assert$;

-- Exercises: one isolated answer and verification per prompt.

-- 1. Trace identities
SAVEPOINT exercise_1;
SELECT reading_id, station, temperature FROM start_readings ORDER BY reading_id;
CREATE TEMP TABLE solution_answer_1 ON COMMIT DROP AS
SELECT reading_id, station, temperature FROM start_readings ORDER BY reading_id;
SELECT pg_temp.assert_true((SELECT array_agg(reading_id ORDER BY reading_id) FROM solution_answer_1) = ARRAY[1,2,3,4,5,6], 'sql-start-01 exercise 1');

ROLLBACK TO SAVEPOINT exercise_1;
RELEASE SAVEPOINT exercise_1;

-- 2. Reveal repeated visible values
SAVEPOINT exercise_2;
SELECT reading_id, station, reading_day, temperature FROM start_readings WHERE reading_id <= 2 ORDER BY reading_id;
CREATE TEMP TABLE solution_answer_2 ON COMMIT DROP AS
SELECT reading_id, station, reading_day, temperature FROM start_readings WHERE reading_id <= 2 ORDER BY reading_id;
SELECT pg_temp.assert_true((SELECT count(*) = 2 AND min(temperature) = 18 AND max(temperature) = 18 AND count(DISTINCT reading_day) = 2 FROM solution_answer_2), 'sql-start-01 exercise 2');

ROLLBACK TO SAVEPOINT exercise_2;
RELEASE SAVEPOINT exercise_2;

-- 3. Filter observations without losing missing values
SAVEPOINT exercise_3;
SELECT reading_id, station, temperature FROM start_readings WHERE station = 'South' ORDER BY reading_id;
CREATE TEMP TABLE solution_answer_3 ON COMMIT DROP AS
SELECT reading_id, station, temperature FROM start_readings WHERE station = 'South' ORDER BY reading_id;
SELECT pg_temp.assert_true((SELECT array_agg(reading_id ORDER BY reading_id) = ARRAY[3,4] AND count(temperature) = 1 FROM solution_answer_3), 'sql-start-01 exercise 3');

ROLLBACK TO SAVEPOINT exercise_3;
RELEASE SAVEPOINT exercise_3;

-- 4. Calculate without editing storage
SAVEPOINT exercise_4;
SELECT reading_id, temperature, temperature + 2 AS adjusted_temperature FROM start_readings WHERE reading_id IN (1,3) ORDER BY reading_id;
CREATE TEMP TABLE solution_answer_4 ON COMMIT DROP AS
SELECT reading_id, temperature, temperature + 2 AS adjusted_temperature FROM start_readings WHERE reading_id IN (1,3) ORDER BY reading_id;
SELECT pg_temp.assert_true((SELECT array_agg(adjusted_temperature ORDER BY reading_id) FROM solution_answer_4) = ARRAY[20,2]::numeric[] AND (SELECT temperature FROM start_readings WHERE reading_id=1) = 18, 'sql-start-01 exercise 4');

ROLLBACK TO SAVEPOINT exercise_4;
RELEASE SAVEPOINT exercise_4;

-- 5. Distinguish no rows from a missing field
SAVEPOINT exercise_5;
SELECT reading_id, station, temperature FROM start_readings WHERE station = 'East' ORDER BY reading_id;
CREATE TEMP TABLE solution_answer_5 ON COMMIT DROP AS
SELECT reading_id, station, temperature FROM start_readings WHERE station = 'East' ORDER BY reading_id;
SELECT pg_temp.assert_true((SELECT count(*) FROM solution_answer_5) = 0, 'sql-start-01 exercise 5');

ROLLBACK TO SAVEPOINT exercise_5;
RELEASE SAVEPOINT exercise_5;

-- 6. Transfer grain to a new collection
SAVEPOINT exercise_6;
SELECT ticket_id, station, issue FROM (VALUES (11, 'North', 'battery'), (12, 'North', 'screen')) AS tickets(ticket_id, station, issue) ORDER BY ticket_id;
CREATE TEMP TABLE solution_answer_6 ON COMMIT DROP AS
SELECT ticket_id, station, issue FROM (VALUES (11, 'North', 'battery'), (12, 'North', 'screen')) AS tickets(ticket_id, station, issue) ORDER BY ticket_id;
SELECT pg_temp.assert_true((SELECT array_agg(ticket_id ORDER BY ticket_id) = ARRAY[11,12] AND count(DISTINCT station) = 1 FROM solution_answer_6), 'sql-start-01 exercise 6');

ROLLBACK TO SAVEPOINT exercise_6;
RELEASE SAVEPOINT exercise_6;

ROLLBACK;
