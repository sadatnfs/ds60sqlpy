# sql-deep-06: Explained reference solutions

Read [Cohort Denominators, Follow-Up Maturity, and Point-in-Time Quality](../companion-guides/sql_deep_06.md) and attempt its six queries before comparing. The [complete reference script](sql_deep_06_solutions.sql) recreates the same temporary fixture, runs every answer inside its own savepoint, compares exact JSON row sets with fail-fast assertions, then rolls back. No permanent table, role or service is changed.

## Exercises and reasoning

### Exercise 1: Expose invalid event relationships before aggregation

Return event_id, user_id, reason for events with an unknown user or occurrence before that user's signup. One diagnostic row represents one invalid event, ordered by event_id. Classify unknown_user before comparing signup time.

**Expected:** Event 7, user 1 is before_signup; event 8, user 99 is unknown_user. Future availability alone is not a malformed relationship and is handled separately.

```sql
SELECT e.event_id,e.user_id,
 CASE WHEN u.user_id IS NULL THEN 'unknown_user' ELSE 'before_signup' END AS reason
FROM deep6_events AS e LEFT JOIN deep6_users AS u ON u.user_id=e.user_id
WHERE u.user_id IS NULL OR e.occurred_at<u.signup_at
ORDER BY e.event_id;
```

The left join preserves orphan events that an inner join would erase before the quality report. Key absence is classified before a timestamp comparison because the unknown user has no signup time to compare. These defects are intentionally retained in the teaching fixture, but a real publication needs a documented repair or exclusion policy and a gate. A final rate that looks reasonable does not validate its source relationships.

### Exercise 2: Define denominator eligibility using both clocks

As ofJanuary 10 UTC, return user_id, cohort_day, eligible for each user. A day 7 label is eligible only when signup+8days is no later than both the report cutoff and observed_through. Preserve one row per user ordered by user_id.

**Expected:** Users 1,3,5 are eligible; users 2 and 4 are pending. User 2 has elapsed calendar time but an incomplete observation watermark. User 3 ends its window exactly at the cutoff and is eligible.

```sql
SELECT user_id,signup_at::date AS cohort_day,
 observed_through>=signup_at+INTERVAL '8 days'
 AND TIMESTAMPTZ '2026-01-10T00:00Z'>=signup_at+INTERVAL '8 days' AS eligible
FROM deep6_users ORDER BY user_id;
```

Eligibility concerns the end of the entire outcome window, not merely reaching its start. Both elapsed follow-up and trustworthy observation coverage are required. The equality case is deliberate: coverage through the exclusive endpoint completes all times inside the window. The watermark is a source contract that must be credible in real systems; writing this comparison does not independently prove ingestion completeness.

### Exercise 3: Create one nullable retention label per user

Return user_id, eligible, day 7_retained from a user-level label CTE. Use EXISTS for available events in[signup+7days, signup+8days), and leave day 7_retained NULL when ineligible. Require event available_at no later than the historical cutoff. Order by user_id.

**Expected:** Users 1 and 3 are true, user 5 is false, and users 2 and 4 are NULL. User 1's multiple day 7 events still produce one true label; its exact window-end event is excluded.

```sql
WITH eligibility AS (
 SELECT u.*,u.signup_at::date AS cohort_day,
        u.signup_at+INTERVAL '7 days' AS window_start,
        u.signup_at+INTERVAL '8 days' AS window_end,
        u.observed_through>=u.signup_at+INTERVAL '8 days'
        AND TIMESTAMPTZ '2026-01-10T00:00Z'>=u.signup_at+INTERVAL '8 days' AS eligible
 FROM deep6_users AS u
), labels AS (
 SELECT e.user_id,e.cohort_day,e.eligible,
 CASE WHEN e.eligible THEN EXISTS(
  SELECT 1 FROM deep6_events AS a WHERE a.user_id=e.user_id
   AND a.occurred_at>=e.window_start AND a.occurred_at<e.window_end
   AND a.available_at<=TIMESTAMPTZ '2026-01-10T00:00Z'
 ) END AS retained
 FROM eligibility AS e
)
SELECT user_id,eligible,retained AS day7_retained FROM labels ORDER BY user_id;
```

The eligibility CTE defines the window and denominator at user grain before the event lookup. EXISTS produces a Boolean regardless of how many qualifying events occur, preventing activity volume from multiplying retained users. CASE preserves pending follow-up as NULL rather than false. The availability filter enforces historical knowledge, while the half-open occurrence filter enforces the outcome definition; both clocks are necessary.

### Exercise 4: Report cohort rates with their denominators

Aggregate user labels to cohort_day, total_users, eligible_users, retained_users, retention_rate, ordered by cohort_day. Count only eligible users in the rate denominator and only true labels in the numerator. Return NULL when no user is eligible, preserving the pending cohort.

**Expected:** January 1 has 3 total,2 eligible,1 retained, rate 0.5; January 2 has 1,1,1, rate 1; January 9 has 1,0,0, rateNULL.

```sql
WITH eligibility AS (
 SELECT u.*,u.signup_at::date AS cohort_day,
        u.signup_at+INTERVAL '7 days' AS window_start,
        u.signup_at+INTERVAL '8 days' AS window_end,
        u.observed_through>=u.signup_at+INTERVAL '8 days'
        AND TIMESTAMPTZ '2026-01-10T00:00Z'>=u.signup_at+INTERVAL '8 days' AS eligible
 FROM deep6_users AS u
), labels AS (
 SELECT e.user_id,e.cohort_day,e.eligible,
 CASE WHEN e.eligible THEN EXISTS(
  SELECT 1 FROM deep6_events AS a WHERE a.user_id=e.user_id
   AND a.occurred_at>=e.window_start AND a.occurred_at<e.window_end
   AND a.available_at<=TIMESTAMPTZ '2026-01-10T00:00Z'
 ) END AS retained
 FROM eligibility AS e
)
SELECT cohort_day,count(*) AS total_users,
 count(*) FILTER(WHERE eligible) AS eligible_users,
 count(*) FILTER(WHERE retained) AS retained_users,
 (count(*) FILTER(WHERE retained))::numeric/NULLIF(count(*) FILTER(WHERE eligible),0) AS retention_rate
FROM labels GROUP BY cohort_day ORDER BY cohort_day;
```

The aggregation starts from one row per user, so a retained person contributes exactly one numerator count. FILTER separates total population, completed follow-up and positive outcomes explicitly. NULLIF preserves an undefined zero-denominator rate for January 9, rather than reporting zero retention for people whose window has not matured. The result is a defined historical observation summary, not by itself a causal claim about product changes.

### Exercise 5: Detect a historical feature or label leakage candidate

Return event_id, user_id, event_before_cutoff, available_by_cutoff for events occurring no later thanJanuary 10 but available only afterward. One row represents one late-arriving historical event, ordered by event_id. Do not include events that themselves occur after the cutoff.

**Expected:** Only event 5 for user 2 appears, with event_before_cutoff=true and available_by_cutoff=false. Event 9 is future occurrence and is outside this particular late-arrival diagnostic.

```sql
SELECT event_id,user_id,occurred_at<=TIMESTAMPTZ '2026-01-10T00:00Z' AS event_before_cutoff,
 available_at<=TIMESTAMPTZ '2026-01-10T00:00Z' AS available_by_cutoff
FROM deep6_events
WHERE occurred_at<=TIMESTAMPTZ '2026-01-10T00:00Z'
 AND available_at>TIMESTAMPTZ '2026-01-10T00:00Z'
ORDER BY event_id;
```

A later warehouse extract can contain records that describe an earlier period but were unavailable to the original decision. Filtering only occurrence time would leak that later knowledge into a replay or model feature. This diagnostic isolates late availability from genuinely future events, which require a different exclusion reason. Retaining both timestamps and dataset versions is necessary to reproduce historical evidence accurately.

### Exercise 6: Distinguish empty cohorts from pending-only cohorts

Create a daily cohort spine forJanuary 1 throughJanuary 10 and left-join the cohort label summary. Return cohort_day, cohort_state, eligible_users, retention_rate ordered by cohort_day. Use empty for no signup rows, pending_only for signups but no eligible users, and has_eligible otherwise.

**Expected:** January 1 is has_eligible,2,0.5; January 2 has_eligible,1,1; January 9 pending_only,0, NULL; the other seven dates are empty,0, NULL. Ten date rows must remain.

```sql
WITH eligibility AS (
 SELECT u.*,u.signup_at::date AS cohort_day,
        u.signup_at+INTERVAL '7 days' AS window_start,
        u.signup_at+INTERVAL '8 days' AS window_end,
        u.observed_through>=u.signup_at+INTERVAL '8 days'
        AND TIMESTAMPTZ '2026-01-10T00:00Z'>=u.signup_at+INTERVAL '8 days' AS eligible
 FROM deep6_users AS u
), labels AS (
 SELECT e.user_id,e.cohort_day,e.eligible,
 CASE WHEN e.eligible THEN EXISTS(
  SELECT 1 FROM deep6_events AS a WHERE a.user_id=e.user_id
   AND a.occurred_at>=e.window_start AND a.occurred_at<e.window_end
   AND a.available_at<=TIMESTAMPTZ '2026-01-10T00:00Z'
 ) END AS retained
 FROM eligibility AS e
), summary AS (
 SELECT cohort_day,count(*) AS total_users,count(*) FILTER(WHERE eligible) AS eligible_users,
 count(*) FILTER(WHERE retained) AS retained_users FROM labels GROUP BY cohort_day
), spine AS (
 SELECT day::date AS cohort_day FROM generate_series(DATE '2026-01-01',DATE '2026-01-10',INTERVAL '1 day') AS day
)
SELECT s.cohort_day,
 CASE WHEN m.total_users IS NULL THEN 'empty' WHEN m.eligible_users=0 THEN 'pending_only' ELSE 'has_eligible' END AS cohort_state,
 COALESCE(m.eligible_users,0) AS eligible_users,
 m.retained_users::numeric/NULLIF(m.eligible_users,0) AS retention_rate
FROM spine AS s LEFT JOIN summary AS m ON m.cohort_day=s.cohort_day ORDER BY s.cohort_day;
```

The spine defines the reporting domain independently of observed data, so dates without signups do not vanish. The left join preserves their absence as a NULL summary, which is distinguishable from a real cohort whose eligible count is zero. Coalescing only the count makes the table convenient without inventing a zero retention rate. This separation prevents dashboards from presenting no data, pending follow-up and observed nonretention as the same state.

## Verification and transaction boundary

Every answer is materialized into a temporary answer table and compared with a literal expected row set, including column names, NULL values and deterministic order. The assertion function rejects both false and unknown Boolean results, so a NULL comparison cannot silently pass. Each exercise rolls back to its own savepoint, ensuring mutations used for one boundary case do not alter the next. The final ROLLBACK removes the full fixture. Read the first error if a contract fails; a later row count or command tag cannot repair an earlier failed assertion.
