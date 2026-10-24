-- sql-deep-06: complete reference queries and exact result assertions
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
CREATE TEMP TABLE deep6_users (
  user_id integer PRIMARY KEY,
  signup_at timestamptz NOT NULL,
  observed_through timestamptz NOT NULL
) ON COMMIT DROP;
INSERT INTO deep6_users
VALUES
  (1, '2026-01-01T00:00Z', '2026-01-10T00:00Z'),
  (2, '2026-01-01T00:00Z', '2026-01-08T00:00Z'),
  (3, '2026-01-02T00:00Z', '2026-01-10T00:00Z'),
  (4, '2026-01-09T00:00Z', '2026-01-10T00:00Z'),
  (5, '2026-01-01T00:00Z', '2026-01-10T00:00Z');
CREATE TEMP TABLE deep6_events (
  event_id integer PRIMARY KEY,
  user_id integer NOT NULL,
  occurred_at timestamptz NOT NULL,
  available_at timestamptz NOT NULL
) ON COMMIT DROP;
INSERT INTO deep6_events
VALUES
  (1, 1, '2026-01-08T00:00Z', '2026-01-08T00:00Z'),
  (2, 1, '2026-01-08T12:00Z', '2026-01-08T12:00Z'),
  (3, 1, '2026-01-09T00:00Z', '2026-01-09T00:00Z'),
  (4, 3, '2026-01-09T09:00Z', '2026-01-09T09:00Z'),
  (5, 2, '2026-01-08T10:00Z', '2026-01-11T00:00Z'),
  (6, 4, '2026-01-09T00:00Z', '2026-01-09T00:00Z'),
  (7, 1, '2025-12-31T00:00Z', '2025-12-31T00:00Z'),
  (8, 99, '2026-01-08T00:00Z', '2026-01-08T00:00Z'),
  (9, 1, '2026-01-12T00:00Z', '2026-01-12T00:00Z');
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
  -- Exercises
  -- 1. Expose invalid event relationships before aggregation
  SAVEPOINT exercise_1;
  CREATE TEMP TABLE answer_1 ON COMMIT DROP AS
  SELECT
    e.event_id, e.user_id, CASE WHEN u.user_id IS NULL THEN
      'unknown_user'
    ELSE
      'before_signup'
    END AS reason
  FROM
    deep6_events AS e
  LEFT JOIN deep6_users AS u ON u.user_id = e.user_id
WHERE
  u.user_id IS NULL
  OR e.occurred_at < u.signup_at
ORDER BY
  e.event_id;
  SELECT
    event_id,
    user_id,
    reason
  FROM
    answer_1
  ORDER BY
    event_id;
    SELECT
      pg_temp.assert_true ((
        SELECT
          COALESCE(jsonb_agg(to_jsonb (answer_1)
          ORDER BY event_id), '[]'::jsonb)
        FROM answer_1) = '[{"event_id": 7, "user_id": 1, "reason": "before_signup"}, {"event_id": 8, "user_id": 99, "reason": "unknown_user"}]'::jsonb, 'sql-deep-06 exercise 1');
ROLLBACK TO SAVEPOINT exercise_1;
RELEASE SAVEPOINT exercise_1;
-- 2. Define denominator eligibility using both clocks
SAVEPOINT exercise_2;
CREATE TEMP TABLE answer_2 ON COMMIT DROP AS
SELECT
  user_id, signup_at::date AS cohort_day, observed_through >= signup_at + INTERVAL '8 days'
  AND TIMESTAMPTZ '2026-01-10T00:00Z' >= signup_at + INTERVAL '8 days' AS eligible
FROM
  deep6_users
ORDER BY
  user_id;
  SELECT
    user_id,
    cohort_day,
    eligible
  FROM
    answer_2
  ORDER BY
    user_id;
    SELECT
      pg_temp.assert_true ((
        SELECT
          COALESCE(jsonb_agg(to_jsonb (answer_2)
          ORDER BY user_id), '[]'::jsonb)
        FROM answer_2) = '[{"user_id": 1, "cohort_day": "2026-01-01", "eligible": true}, {"user_id": 2, "cohort_day": "2026-01-01", "eligible": false}, {"user_id": 3, "cohort_day": "2026-01-02", "eligible": true}, {"user_id": 4, "cohort_day": "2026-01-09", "eligible": false}, {"user_id": 5, "cohort_day": "2026-01-01", "eligible": true}]'::jsonb, 'sql-deep-06 exercise 2');
ROLLBACK TO SAVEPOINT exercise_2;
RELEASE SAVEPOINT exercise_2;
-- 3. Create one nullable retention label per user
SAVEPOINT exercise_3;
CREATE TEMP TABLE answer_3 ON COMMIT DROP AS
WITH eligibility AS (
  SELECT
    u.*,
    u.signup_at::date AS cohort_day,
    u.signup_at + INTERVAL '7 days' AS window_start,
    u.signup_at + INTERVAL '8 days' AS window_end,
    u.observed_through >= u.signup_at + INTERVAL '8 days'
    AND TIMESTAMPTZ '2026-01-10T00:00Z' >= u.signup_at + INTERVAL '8 days' AS eligible
  FROM
    deep6_users AS u
),
labels AS (
  SELECT
    e.user_id,
    e.cohort_day,
    e.eligible,
    CASE WHEN e.eligible THEN
      EXISTS (
        SELECT
          1
        FROM
          deep6_events AS a
        WHERE
          a.user_id = e.user_id
          AND a.occurred_at >= e.window_start
          AND a.occurred_at < e.window_end
          AND a.available_at <= TIMESTAMPTZ '2026-01-10T00:00Z')
    END AS retained
  FROM
    eligibility AS e
)
SELECT
  user_id, eligible, retained AS day7_retained
FROM
  labels
ORDER BY
  user_id;
  SELECT
    user_id,
    eligible,
    day7_retained
  FROM
    answer_3
  ORDER BY
    user_id;
    SELECT
      pg_temp.assert_true ((
        SELECT
          COALESCE(jsonb_agg(to_jsonb (answer_3)
          ORDER BY user_id), '[]'::jsonb)
        FROM answer_3) = '[{"user_id": 1, "eligible": true, "day7_retained": true}, {"user_id": 2, "eligible": false, "day7_retained": null}, {"user_id": 3, "eligible": true, "day7_retained": true}, {"user_id": 4, "eligible": false, "day7_retained": null}, {"user_id": 5, "eligible": true, "day7_retained": false}]'::jsonb, 'sql-deep-06 exercise 3');
ROLLBACK TO SAVEPOINT exercise_3;
RELEASE SAVEPOINT exercise_3;
-- 4. Report cohort rates with their denominators
SAVEPOINT exercise_4;
CREATE TEMP TABLE answer_4 ON COMMIT DROP AS
WITH eligibility AS (
  SELECT
    u.*,
    u.signup_at::date AS cohort_day,
    u.signup_at + INTERVAL '7 days' AS window_start,
    u.signup_at + INTERVAL '8 days' AS window_end,
    u.observed_through >= u.signup_at + INTERVAL '8 days'
    AND TIMESTAMPTZ '2026-01-10T00:00Z' >= u.signup_at + INTERVAL '8 days' AS eligible
  FROM
    deep6_users AS u
),
labels AS (
  SELECT
    e.user_id,
    e.cohort_day,
    e.eligible,
    CASE WHEN e.eligible THEN
      EXISTS (
        SELECT
          1
        FROM
          deep6_events AS a
        WHERE
          a.user_id = e.user_id
          AND a.occurred_at >= e.window_start
          AND a.occurred_at < e.window_end
          AND a.available_at <= TIMESTAMPTZ '2026-01-10T00:00Z')
    END AS retained
  FROM
    eligibility AS e
)
SELECT
  cohort_day, count(*) AS total_users, count(*) FILTER (WHERE eligible) AS eligible_users, count(*) FILTER (WHERE retained) AS retained_users, (count(*) FILTER (WHERE retained))::numeric / NULLIF (count(*) FILTER (WHERE eligible), 0) AS retention_rate
FROM
  labels
GROUP BY
  cohort_day
ORDER BY
  cohort_day;
  SELECT
    cohort_day,
    total_users,
    eligible_users,
    retained_users,
    retention_rate
  FROM
    answer_4
  ORDER BY
    cohort_day;
    SELECT
      pg_temp.assert_true ((
        SELECT
          COALESCE(jsonb_agg(to_jsonb (answer_4)
          ORDER BY cohort_day), '[]'::jsonb)
        FROM answer_4) = '[{"cohort_day": "2026-01-01", "total_users": 3, "eligible_users": 2, "retained_users": 1, "retention_rate": 0.5}, {"cohort_day": "2026-01-02", "total_users": 1, "eligible_users": 1, "retained_users": 1, "retention_rate": 1}, {"cohort_day": "2026-01-09", "total_users": 1, "eligible_users": 0, "retained_users": 0, "retention_rate": null}]'::jsonb, 'sql-deep-06 exercise 4');
ROLLBACK TO SAVEPOINT exercise_4;
RELEASE SAVEPOINT exercise_4;
-- 5. Detect a historical feature or label leakage candidate
SAVEPOINT exercise_5;
CREATE TEMP TABLE answer_5 ON COMMIT DROP AS
SELECT
  event_id, user_id, occurred_at <= TIMESTAMPTZ '2026-01-10T00:00Z' AS event_before_cutoff, available_at <= TIMESTAMPTZ '2026-01-10T00:00Z' AS available_by_cutoff
FROM
  deep6_events
WHERE
  occurred_at <= TIMESTAMPTZ '2026-01-10T00:00Z'
  AND available_at > TIMESTAMPTZ '2026-01-10T00:00Z'
ORDER BY
  event_id;
  SELECT
    event_id,
    user_id,
    event_before_cutoff,
    available_by_cutoff
  FROM
    answer_5
  ORDER BY
    event_id;
    SELECT
      pg_temp.assert_true ((
        SELECT
          COALESCE(jsonb_agg(to_jsonb (answer_5)
          ORDER BY event_id), '[]'::jsonb)
        FROM answer_5) = '[{"event_id": 5, "user_id": 2, "event_before_cutoff": true, "available_by_cutoff": false}]'::jsonb, 'sql-deep-06 exercise 5');
ROLLBACK TO SAVEPOINT exercise_5;
RELEASE SAVEPOINT exercise_5;
-- 6. Distinguish empty cohorts from pending-only cohorts
SAVEPOINT exercise_6;
CREATE TEMP TABLE answer_6 ON COMMIT DROP AS
WITH eligibility AS (
  SELECT
    u.*,
    u.signup_at::date AS cohort_day,
    u.signup_at + INTERVAL '7 days' AS window_start,
    u.signup_at + INTERVAL '8 days' AS window_end,
    u.observed_through >= u.signup_at + INTERVAL '8 days'
    AND TIMESTAMPTZ '2026-01-10T00:00Z' >= u.signup_at + INTERVAL '8 days' AS eligible
  FROM
    deep6_users AS u
),
labels AS (
  SELECT
    e.user_id,
    e.cohort_day,
    e.eligible,
    CASE WHEN e.eligible THEN
      EXISTS (
        SELECT
          1
        FROM
          deep6_events AS a
        WHERE
          a.user_id = e.user_id
          AND a.occurred_at >= e.window_start
          AND a.occurred_at < e.window_end
          AND a.available_at <= TIMESTAMPTZ '2026-01-10T00:00Z')
    END AS retained
  FROM
    eligibility AS e
),
summary AS (
  SELECT
    cohort_day,
    count(*) AS total_users,
    count(*) FILTER (WHERE eligible) AS eligible_users,
    count(*) FILTER (WHERE retained) AS retained_users
FROM
  labels
GROUP BY
  cohort_day
),
spine AS (
  SELECT
    day::date AS cohort_day
  FROM
    generate_series(DATE '2026-01-01', DATE '2026-01-10', INTERVAL '1 day') AS day
)
SELECT
  s.cohort_day, CASE WHEN m.total_users IS NULL THEN
    'empty'
  WHEN m.eligible_users = 0 THEN
    'pending_only'
  ELSE
    'has_eligible'
  END AS cohort_state, COALESCE(m.eligible_users, 0) AS eligible_users, m.retained_users::numeric / NULLIF (m.eligible_users, 0) AS retention_rate
FROM
  spine AS s
  LEFT JOIN summary AS m ON m.cohort_day = s.cohort_day
ORDER BY
  s.cohort_day;
  SELECT
    cohort_day,
    cohort_state,
    eligible_users,
    retention_rate
  FROM
    answer_6
  ORDER BY
    cohort_day;
    SELECT
      pg_temp.assert_true ((
        SELECT
          COALESCE(jsonb_agg(to_jsonb (answer_6)
          ORDER BY cohort_day), '[]'::jsonb)
        FROM answer_6) = '[{"cohort_day": "2026-01-01", "cohort_state": "has_eligible", "eligible_users": 2, "retention_rate": 0.5}, {"cohort_day": "2026-01-02", "cohort_state": "has_eligible", "eligible_users": 1, "retention_rate": 1}, {"cohort_day": "2026-01-03", "cohort_state": "empty", "eligible_users": 0, "retention_rate": null}, {"cohort_day": "2026-01-04", "cohort_state": "empty", "eligible_users": 0, "retention_rate": null}, {"cohort_day": "2026-01-05", "cohort_state": "empty", "eligible_users": 0, "retention_rate": null}, {"cohort_day": "2026-01-06", "cohort_state": "empty", "eligible_users": 0, "retention_rate": null}, {"cohort_day": "2026-01-07", "cohort_state": "empty", "eligible_users": 0, "retention_rate": null}, {"cohort_day": "2026-01-08", "cohort_state": "empty", "eligible_users": 0, "retention_rate": null}, {"cohort_day": "2026-01-09", "cohort_state": "pending_only", "eligible_users": 0, "retention_rate": null}, {"cohort_day": "2026-01-10", "cohort_state": "empty", "eligible_users": 0, "retention_rate": null}]'::jsonb, 'sql-deep-06 exercise 6');
ROLLBACK TO SAVEPOINT exercise_6;
RELEASE SAVEPOINT exercise_6;
ROLLBACK;
