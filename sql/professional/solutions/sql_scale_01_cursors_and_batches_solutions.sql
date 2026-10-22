-- SQL-SCALE-01: executable solutions and fail-fast checks

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

CREATE TEMP TABLE scale_events (
  event_id integer PRIMARY KEY, received_seq integer UNIQUE NOT NULL,
  occurred_at timestamptz
) ON COMMIT DROP;
INSERT INTO scale_events VALUES
(1,1,TIMESTAMPTZ '2024-01-01 10:00+00'),
(2,2,TIMESTAMPTZ '2024-01-01 10:00+00'),
(3,3,TIMESTAMPTZ '2024-01-01 11:00+00'),
(4,4,NULL), (5,5,TIMESTAMPTZ '2024-01-01 09:00+00'),
(6,6,TIMESTAMPTZ '2024-01-01 12:00+00');
CREATE INDEX ON scale_events (occurred_at DESC NULLS LAST,event_id DESC);

CREATE FUNCTION pg_temp.assert_true(ok boolean, message text)
RETURNS void LANGUAGE plpgsql AS $assert$
BEGIN
  IF ok IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'Contract failed: %', message;
  END IF;
END
$assert$;

-- Exercises: one isolated answer and verification per prompt.

-- 1. Record an exact first-page boundary
SAVEPOINT exercise_1;
SELECT event_id,occurred_at FROM scale_events ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2;
CREATE TEMP TABLE solution_answer_1 ON COMMIT DROP AS
SELECT event_id,occurred_at FROM scale_events ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2;
SELECT pg_temp.assert_true((SELECT array_agg(event_id ORDER BY occurred_at DESC NULLS LAST,event_id DESC) FROM solution_answer_1) = ARRAY[6,3], 'sql-scale-01 exercise 1');

ROLLBACK TO SAVEPOINT exercise_1;
RELEASE SAVEPOINT exercise_1;

-- 2. Traverse a timestamp tie without overlap
SAVEPOINT exercise_2;
SELECT event_id,occurred_at FROM scale_events WHERE (occurred_at,event_id) < (TIMESTAMPTZ '2024-01-01 11:00+00',3) ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2;
CREATE TEMP TABLE solution_answer_2 ON COMMIT DROP AS
SELECT event_id,occurred_at FROM scale_events WHERE (occurred_at,event_id) < (TIMESTAMPTZ '2024-01-01 11:00+00',3) ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2;
SELECT pg_temp.assert_true((SELECT array_agg(event_id ORDER BY occurred_at DESC NULLS LAST,event_id DESC) FROM solution_answer_2)=ARRAY[2,1] AND NOT EXISTS (SELECT 1 FROM solution_answer_2 WHERE event_id IN (6,3)), 'sql-scale-01 exercise 2');

ROLLBACK TO SAVEPOINT exercise_2;
RELEASE SAVEPOINT exercise_2;

-- 3. Cross into the unknown-timestamp phase
SAVEPOINT exercise_3;
SELECT event_id,occurred_at FROM scale_events
WHERE occurred_at < TIMESTAMPTZ '2024-01-01 09:00+00'
   OR (occurred_at = TIMESTAMPTZ '2024-01-01 09:00+00' AND event_id < 5)
   OR occurred_at IS NULL
ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2;
CREATE TEMP TABLE solution_answer_3 ON COMMIT DROP AS
SELECT event_id,occurred_at FROM scale_events
WHERE occurred_at < TIMESTAMPTZ '2024-01-01 09:00+00'
   OR (occurred_at = TIMESTAMPTZ '2024-01-01 09:00+00' AND event_id < 5)
   OR occurred_at IS NULL
ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2;
SELECT pg_temp.assert_true((SELECT count(*)=1 AND min(event_id)=4 AND bool_and(occurred_at IS NULL) FROM solution_answer_3) AND NOT EXISTS (SELECT 1 FROM scale_events WHERE occurred_at IS NULL AND event_id<4), 'sql-scale-01 exercise 3');

ROLLBACK TO SAVEPOINT exercise_3;
RELEASE SAVEPOINT exercise_3;

-- 4. Expose positional drift after an insertion
SAVEPOINT exercise_4;
WITH changed AS (
 SELECT event_id,occurred_at FROM scale_events
 UNION ALL SELECT 7,TIMESTAMPTZ '2024-01-01 13:00+00'
), positional AS (
 SELECT event_id,occurred_at FROM changed ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2 OFFSET 2
), continuation AS (
 SELECT event_id,occurred_at FROM changed WHERE (occurred_at,event_id)<(TIMESTAMPTZ '2024-01-01 11:00+00',3)
 ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2
)
SELECT 'offset' AS path,event_id,occurred_at FROM positional
UNION ALL SELECT 'cursor',event_id,occurred_at FROM continuation
ORDER BY path,occurred_at DESC NULLS LAST,event_id DESC;
CREATE TEMP TABLE solution_answer_4 ON COMMIT DROP AS
WITH changed AS (
 SELECT event_id,occurred_at FROM scale_events
 UNION ALL SELECT 7,TIMESTAMPTZ '2024-01-01 13:00+00'
), positional AS (
 SELECT event_id,occurred_at FROM changed ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2 OFFSET 2
), continuation AS (
 SELECT event_id,occurred_at FROM changed WHERE (occurred_at,event_id)<(TIMESTAMPTZ '2024-01-01 11:00+00',3)
 ORDER BY occurred_at DESC NULLS LAST,event_id DESC LIMIT 2
)
SELECT 'offset' AS path,event_id,occurred_at FROM positional
UNION ALL SELECT 'cursor',event_id,occurred_at FROM continuation
ORDER BY path,occurred_at DESC NULLS LAST,event_id DESC;
SELECT pg_temp.assert_true((SELECT array_agg(event_id ORDER BY occurred_at DESC NULLS LAST,event_id DESC) FROM solution_answer_4 WHERE path='cursor')=ARRAY[2,1] AND (SELECT array_agg(event_id ORDER BY occurred_at DESC NULLS LAST,event_id DESC) FROM solution_answer_4 WHERE path='offset')=ARRAY[3,2], 'sql-scale-01 exercise 4');

ROLLBACK TO SAVEPOINT exercise_4;
RELEASE SAVEPOINT exercise_4;

-- 5. Exclude a late arrival with a declared sealed prefix
SAVEPOINT exercise_5;
WITH incoming AS (
 SELECT event_id,received_seq,occurred_at FROM scale_events
 UNION ALL SELECT 7,7,TIMESTAMPTZ '2024-01-01 10:30+00'
)
SELECT event_id,received_seq,occurred_at FROM incoming
WHERE received_seq <= 6 AND ((occurred_at,event_id)<(TIMESTAMPTZ '2024-01-01 11:00+00',3) OR occurred_at IS NULL)
ORDER BY occurred_at DESC NULLS LAST,event_id DESC;
CREATE TEMP TABLE solution_answer_5 ON COMMIT DROP AS
WITH incoming AS (
 SELECT event_id,received_seq,occurred_at FROM scale_events
 UNION ALL SELECT 7,7,TIMESTAMPTZ '2024-01-01 10:30+00'
)
SELECT event_id,received_seq,occurred_at FROM incoming
WHERE received_seq <= 6 AND ((occurred_at,event_id)<(TIMESTAMPTZ '2024-01-01 11:00+00',3) OR occurred_at IS NULL)
ORDER BY occurred_at DESC NULLS LAST,event_id DESC;
SELECT pg_temp.assert_true((SELECT array_agg(event_id ORDER BY occurred_at DESC NULLS LAST,event_id DESC) FROM solution_answer_5)=ARRAY[2,1,5,4] AND (SELECT max(received_seq) FROM solution_answer_5)<=6, 'sql-scale-01 exercise 5');

ROLLBACK TO SAVEPOINT exercise_5;
RELEASE SAVEPOINT exercise_5;

-- 6. Prove bounded traversal covers the static fixture
SAVEPOINT exercise_6;
WITH ordered AS (
 SELECT event_id,row_number() OVER (ORDER BY occurred_at DESC NULLS LAST,event_id DESC) AS position FROM scale_events
)
SELECT ((position-1)/2+1)::integer AS batch_no,array_agg(event_id ORDER BY position) AS event_ids,count(*) AS row_count
FROM ordered GROUP BY (position-1)/2+1 ORDER BY batch_no;
CREATE TEMP TABLE solution_answer_6 ON COMMIT DROP AS
WITH ordered AS (
 SELECT event_id,row_number() OVER (ORDER BY occurred_at DESC NULLS LAST,event_id DESC) AS position FROM scale_events
)
SELECT ((position-1)/2+1)::integer AS batch_no,array_agg(event_id ORDER BY position) AS event_ids,count(*) AS row_count
FROM ordered GROUP BY (position-1)/2+1 ORDER BY batch_no;
SELECT pg_temp.assert_true((SELECT count(*)=3 AND sum(row_count)=6 FROM solution_answer_6) AND (SELECT event_ids FROM solution_answer_6 WHERE batch_no=1)=ARRAY[6,3] AND (SELECT event_ids FROM solution_answer_6 WHERE batch_no=2)=ARRAY[2,1] AND (SELECT event_ids FROM solution_answer_6 WHERE batch_no=3)=ARRAY[5,4], 'sql-scale-01 exercise 6');

ROLLBACK TO SAVEPOINT exercise_6;
RELEASE SAVEPOINT exercise_6;

ROLLBACK;
