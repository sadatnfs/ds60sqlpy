-- sql-deep-06: Cohort Denominators, Follow-Up Maturity, and Point-in-Time Quality
-- Guide: sql/professional/companion-guides/sql_deep_06.md
-- Use the complete file in the disposable advanced_sql_training database.

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

CREATE TEMP TABLE deep6_users(user_id integer PRIMARY KEY,signup_at timestamptz NOT NULL,observed_through timestamptz NOT NULL) ON COMMIT DROP;
INSERT INTO deep6_users VALUES
 (1,'2026-01-01T00:00Z','2026-01-10T00:00Z'),
 (2,'2026-01-01T00:00Z','2026-01-08T00:00Z'),
 (3,'2026-01-02T00:00Z','2026-01-10T00:00Z'),
 (4,'2026-01-09T00:00Z','2026-01-10T00:00Z'),
 (5,'2026-01-01T00:00Z','2026-01-10T00:00Z');
CREATE TEMP TABLE deep6_events(event_id integer PRIMARY KEY,user_id integer NOT NULL,occurred_at timestamptz NOT NULL,available_at timestamptz NOT NULL) ON COMMIT DROP;
INSERT INTO deep6_events VALUES
 (1,1,'2026-01-08T00:00Z','2026-01-08T00:00Z'),
 (2,1,'2026-01-08T12:00Z','2026-01-08T12:00Z'),
 (3,1,'2026-01-09T00:00Z','2026-01-09T00:00Z'),
 (4,3,'2026-01-09T09:00Z','2026-01-09T09:00Z'),
 (5,2,'2026-01-08T10:00Z','2026-01-11T00:00Z'),
 (6,4,'2026-01-09T00:00Z','2026-01-09T00:00Z'),
 (7,1,'2025-12-31T00:00Z','2025-12-31T00:00Z'),
 (8,99,'2026-01-08T00:00Z','2026-01-08T00:00Z'),
 (9,1,'2026-01-12T00:00Z','2026-01-12T00:00Z');

-- Worked example 1
WITH activity(event_id,user_id) AS (VALUES(1,10),(2,10),(3,20))
SELECT 'observed_activity' AS metric_id,count(*) AS event_count,count(DISTINCT user_id) AS active_users
FROM activity;

-- Worked example 2
WITH instants(position,at) AS (VALUES
 (1,TIMESTAMPTZ '2026-01-08T00:00Z'),
 (2,TIMESTAMPTZ '2026-01-08T12:00Z'),
 (3,TIMESTAMPTZ '2026-01-09T00:00Z'))
SELECT position,at>=TIMESTAMPTZ '2026-01-08T00:00Z'
 AND at<TIMESTAMPTZ '2026-01-09T00:00Z' AS in_window
FROM instants ORDER BY position;

-- Exercises
-- Write attempts in your ignored working copy before the final ROLLBACK.

-- 1. Expose invalid event relationships before aggregation
-- Inputs/evidence: For sql-deep-06 Exercise 1, Return event_id, user_id, reason for events with an unknown user or occurrence before that user's signup. One diagnostic row represents one invalid event, ordered by event_id. Classify unknown_user before comparing signup time.
-- Expected result/shape: For sql-deep-06 Exercise 1, Event 7, user 1 is before_signup; event 8, user 99 is unknown_user. Future availability alone is not a malformed relationship and is handled separately.
-- Verify: For sql-deep-06 Exercise 1, compare event and user identities before counting activity; classify orphan, pre-signup and not-yet-available evidence separately so invalid rows cannot enter the numerator.

-- 2. Define denominator eligibility using both clocks
-- Inputs/evidence: For sql-deep-06 Exercise 2, As ofJanuary 10 UTC, return user_id, cohort_day, eligible for each user. A day 7 label is eligible only when signup+8days is no later than both the report cutoff and observed_through. Preserve one row per user ordered by user_id.
-- Expected result/shape: For sql-deep-06 Exercise 2, Users 1,3,5 are eligible; users 2 and 4 are pending. User 2 has elapsed calendar time but an incomplete observation watermark. User 3 ends its window exactly at the cutoff and is eligible.
-- Verify: For sql-deep-06 Exercise 2, check both event-time maturity and availability-time eligibility at the report cutoff; explain why passing only one clock is insufficient.

-- 3. Create one nullable retention label per user
-- Inputs/evidence: For sql-deep-06 Exercise 3, Return user_id, eligible, day 7_retained from a user-level label CTE. Use EXISTS for available events in[signup+7days, signup+8days), and leave day 7_retained NULL when ineligible. Require event available_at no later than the historical cutoff. Order by user_id.
-- Expected result/shape: For sql-deep-06 Exercise 3, Users 1 and 3 are true, user 5 is false, and users 2 and 4 are NULL. User 1's multiple day 7 events still produce one true label; its exact window-end event is excluded.
-- Verify: For sql-deep-06 Exercise 3, construct the expected label from each eligible user event history: one for observed qualifying retention, zero only for complete mature nonretention, and NULL for pending observation.

-- 4. Report cohort rates with their denominators
-- Inputs/evidence: For sql-deep-06 Exercise 4, Aggregate user labels to cohort_day, total_users, eligible_users, retained_users, retention_rate, ordered by cohort_day. Count only eligible users in the rate denominator and only true labels in the numerator. Return NULL when no user is eligible, preserving the pending cohort.
-- Expected result/shape: For sql-deep-06 Exercise 4, January 1 has 3 total,2 eligible,1 retained, rate 0.5; January 2 has 1,1,1, rate 1; January 9 has 1,0,0, rateNULL.
-- Verify: For sql-deep-06 Exercise 4, sum eligible user labels and denominators independently, checking that pending labels do not silently enter either the retained count or mature denominator.

-- 5. Detect a historical feature or label leakage candidate
-- Inputs/evidence: For sql-deep-06 Exercise 5, Return event_id, user_id, event_before_cutoff, available_by_cutoff for events occurring no later thanJanuary 10 but available only afterward. One row represents one late-arriving historical event, ordered by event_id. Do not include events that themselves occur after the cutoff.
-- Expected result/shape: For sql-deep-06 Exercise 5, Only event 5 for user 2 appears, with event_before_cutoff=true and available_by_cutoff=false. Event 9 is future occurrence and is outside this particular late-arrival diagnostic.
-- Verify: For sql-deep-06 Exercise 5, compare each record availability timestamp with the historical prediction cutoff even when its event timestamp is earlier; identify late-arriving evidence that would leak future knowledge.

-- 6. Distinguish empty cohorts from pending-only cohorts
-- Inputs/evidence: For sql-deep-06 Exercise 6, Create a daily cohort spine forJanuary 1 throughJanuary 10 and left-join the cohort label summary. Return cohort_day, cohort_state, eligible_users, retention_rate ordered by cohort_day. Use empty for no signup rows, pending_only for signups but no eligible users, and has_eligible otherwise.
-- Expected result/shape: For sql-deep-06 Exercise 6, January 1 is has_eligible,2,0.5; January 2 has_eligible,1,1; January 9 pending_only,0, NULL; the other seven dates are empty,0, NULL. Ten date rows must remain.
-- Verify: For sql-deep-06 Exercise 6, left join the cohort spine to user-level evidence and distinguish zero users from users with no mature labels; inspect the count columns before interpreting a NULL rate.

ROLLBACK;
