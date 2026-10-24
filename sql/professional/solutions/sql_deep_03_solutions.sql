-- sql-deep-03: complete reference queries and exact result assertions

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

CREATE TEMP TABLE deep3_events(event_id integer PRIMARY KEY,customer_id text NOT NULL,occurred_at timestamptz NOT NULL,amount integer NOT NULL) ON COMMIT DROP;
INSERT INTO deep3_events VALUES
 (1,'a','2026-01-01T10:00Z',1),(2,'a','2026-01-01T10:00Z',2),
 (3,'a','2026-01-01T10:10Z',3),(4,'a','2026-01-01T10:40Z',4),
 (5,'a','2026-01-01T11:11Z',5),(6,'b','2026-01-01T10:05Z',10),
 (7,'b','2026-01-01T10:35Z',20);

CREATE FUNCTION pg_temp.assert_true(ok boolean, message text)
RETURNS void LANGUAGE plpgsql AS $assert$
BEGIN
  IF ok IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'Contract failed: %', message;
  END IF;
END
$assert$;

-- Exercises

-- 1. Compare row and peer running totals
SAVEPOINT exercise_1;
CREATE TEMP TABLE answer_1 ON COMMIT DROP AS
SELECT event_id,
 sum(amount) OVER(ORDER BY occurred_at,event_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS row_total,
 sum(amount) OVER(ORDER BY occurred_at RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS peer_total
FROM deep3_events WHERE customer_id='a' ORDER BY event_id;
SELECT event_id,row_total,peer_total FROM answer_1 ORDER BY event_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_1) ORDER BY event_id),'[]'::jsonb) FROM answer_1) = '[{"event_id": 1, "row_total": 1, "peer_total": 3}, {"event_id": 2, "row_total": 3, "peer_total": 3}, {"event_id": 3, "row_total": 6, "peer_total": 6}, {"event_id": 4, "row_total": 10, "peer_total": 10}, {"event_id": 5, "row_total": 15, "peer_total": 15}]'::jsonb,'sql-deep-03 exercise 1');
ROLLBACK TO SAVEPOINT exercise_1;
RELEASE SAVEPOINT exercise_1;

-- 2. Compare neighboring rows with neighboring peer groups
SAVEPOINT exercise_2;
CREATE TEMP TABLE answer_2 ON COMMIT DROP AS
SELECT event_id,
 sum(amount) OVER(ORDER BY occurred_at,event_id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS two_rows,
 sum(amount) OVER(ORDER BY occurred_at GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW) AS two_groups
FROM deep3_events WHERE customer_id='a' ORDER BY event_id;
SELECT event_id,two_rows,two_groups FROM answer_2 ORDER BY event_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_2) ORDER BY event_id),'[]'::jsonb) FROM answer_2) = '[{"event_id": 1, "two_rows": 1, "two_groups": 3}, {"event_id": 2, "two_rows": 3, "two_groups": 3}, {"event_id": 3, "two_rows": 5, "two_groups": 6}, {"event_id": 4, "two_rows": 7, "two_groups": 7}, {"event_id": 5, "two_rows": 9, "two_groups": 9}]'::jsonb,'sql-deep-03 exercise 2');
ROLLBACK TO SAVEPOINT exercise_2;
RELEASE SAVEPOINT exercise_2;

-- 3. Distinguish the three exclusion policies
SAVEPOINT exercise_3;
CREATE TEMP TABLE answer_3 ON COMMIT DROP AS
SELECT event_id,
 sum(amount) OVER(ORDER BY occurred_at RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE CURRENT ROW) AS without_current,
 sum(amount) OVER(ORDER BY occurred_at RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE GROUP) AS without_group,
 sum(amount) OVER(ORDER BY occurred_at RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE TIES) AS without_other_ties
FROM deep3_events WHERE customer_id='a' ORDER BY event_id;
SELECT event_id,without_current,without_group,without_other_ties FROM answer_3 ORDER BY event_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_3) ORDER BY event_id),'[]'::jsonb) FROM answer_3) = '[{"event_id": 1, "without_current": 2, "without_group": null, "without_other_ties": 1}, {"event_id": 2, "without_current": 1, "without_group": null, "without_other_ties": 2}, {"event_id": 3, "without_current": 3, "without_group": 3, "without_other_ties": 6}, {"event_id": 4, "without_current": 6, "without_group": 6, "without_other_ties": 10}, {"event_id": 5, "without_current": 10, "without_group": 10, "without_other_ties": 15}]'::jsonb,'sql-deep-03 exercise 3');
ROLLBACK TO SAVEPOINT exercise_3;
RELEASE SAVEPOINT exercise_3;

-- 4. Make LAST_VALUE refer to the intended horizon
SAVEPOINT exercise_4;
CREATE TEMP TABLE answer_4 ON COMMIT DROP AS
SELECT event_id,
 last_value(amount) OVER(ORDER BY occurred_at,event_id) AS prefix_last,
 last_value(amount) OVER(ORDER BY occurred_at,event_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS partition_last
FROM deep3_events WHERE customer_id='a' ORDER BY event_id;
SELECT event_id,prefix_last,partition_last FROM answer_4 ORDER BY event_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_4) ORDER BY event_id),'[]'::jsonb) FROM answer_4) = '[{"event_id": 1, "prefix_last": 1, "partition_last": 5}, {"event_id": 2, "prefix_last": 2, "partition_last": 5}, {"event_id": 3, "prefix_last": 3, "partition_last": 5}, {"event_id": 4, "prefix_last": 4, "partition_last": 5}, {"event_id": 5, "prefix_last": 5, "partition_last": 5}]'::jsonb,'sql-deep-03 exercise 4');
ROLLBACK TO SAVEPOINT exercise_4;
RELEASE SAVEPOINT exercise_4;

-- 5. Build a strictly prior elapsed-time feature
SAVEPOINT exercise_5;
CREATE TEMP TABLE answer_5 ON COMMIT DROP AS
SELECT event_id,COALESCE(sum(amount) OVER(
 PARTITION BY customer_id ORDER BY occurred_at
 RANGE BETWEEN INTERVAL '30 minutes' PRECEDING AND CURRENT ROW EXCLUDE GROUP),0) AS prior_30m
FROM deep3_events ORDER BY event_id;
SELECT event_id,prior_30m FROM answer_5 ORDER BY event_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_5) ORDER BY event_id),'[]'::jsonb) FROM answer_5) = '[{"event_id": 1, "prior_30m": 0}, {"event_id": 2, "prior_30m": 0}, {"event_id": 3, "prior_30m": 3}, {"event_id": 4, "prior_30m": 3}, {"event_id": 5, "prior_30m": 0}, {"event_id": 6, "prior_30m": 0}, {"event_id": 7, "prior_30m": 10}]'::jsonb,'sql-deep-03 exercise 5');
ROLLBACK TO SAVEPOINT exercise_5;
RELEASE SAVEPOINT exercise_5;

-- 6. Derive sessions in separate window stages
SAVEPOINT exercise_6;
CREATE TEMP TABLE answer_6 ON COMMIT DROP AS
WITH previous AS (
 SELECT e.*,lag(occurred_at) OVER(PARTITION BY customer_id ORDER BY occurred_at,event_id) AS prior_at
 FROM deep3_events AS e
), flags AS (
 SELECT previous.*,CASE WHEN prior_at IS NULL OR occurred_at-prior_at>INTERVAL '30 minutes' THEN 1 ELSE 0 END AS begins
 FROM previous
), sessions AS (
 SELECT flags.*,sum(begins) OVER(PARTITION BY customer_id ORDER BY occurred_at,event_id ROWS UNBOUNDED PRECEDING) AS session_id
 FROM flags
)
SELECT customer_id,session_id,count(*) AS event_count,
 (array_agg(event_id ORDER BY occurred_at,event_id))[1] AS first_event_id,
 (array_agg(event_id ORDER BY occurred_at DESC,event_id DESC))[1] AS last_event_id
FROM sessions GROUP BY customer_id,session_id ORDER BY customer_id,session_id;
SELECT customer_id,session_id,event_count,first_event_id,last_event_id FROM answer_6 ORDER BY customer_id,session_id;
SELECT pg_temp.assert_true((SELECT COALESCE(jsonb_agg(to_jsonb(answer_6) ORDER BY customer_id,session_id),'[]'::jsonb) FROM answer_6) = '[{"customer_id": "a", "session_id": 1, "event_count": 4, "first_event_id": 1, "last_event_id": 4}, {"customer_id": "a", "session_id": 2, "event_count": 1, "first_event_id": 5, "last_event_id": 5}, {"customer_id": "b", "session_id": 1, "event_count": 2, "first_event_id": 6, "last_event_id": 7}]'::jsonb,'sql-deep-03 exercise 6');
ROLLBACK TO SAVEPOINT exercise_6;
RELEASE SAVEPOINT exercise_6;

ROLLBACK;
