# Cohort Denominators, Follow-Up Maturity, and Point-in-Time Quality

**Stable ID:** `sql-deep-06`. **Estimated time:** 150 minutes, split across reading and query investigation.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **PostgreSQL** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Use the private reader's **Create/open guided SQL notebook** action. It creates the ignored editable copy at `.learning/sql/sql-deep-06/lesson/workspace/sql/professional/lessons/sql_deep_06.sql`. Read the supplied fixture, write a prediction, edit that copy and run the complete script. The prepared target must be the local disposable `advanced_sql_training` database. These lessons never require a production connection or a new cloud service.

The learner file starts a transaction, checks the database name, creates only temporary tables, runs two worked examples and ends with ROLLBACK. Your six query attempts belong before that final rollback. Re-run the complete file after an error so the fixture and transaction state are known. Output appears in the notebook or terminal as named columns and bounded rows; a command tag alone does not verify a SELECT result.

Windows PowerShell fallback, from the repository root:

```powershell
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql/professional/lessons/sql_deep_06.sql"
```

macOS/Linux fallback, from the repository root:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_deep_06.sql
```

If the prepared database is unavailable, return to classroom setup rather than changing the target. Keep credentials outside lesson files and command text. Read the [learner SQL](../lessons/sql_deep_06.sql); keep [explanatory solutions](../solutions/sql_deep_06_solutions.md) and [executable solutions](../solutions/sql_deep_06_solutions.sql) closed until an attempt or an explicit worked comparison. PostgreSQL 16+ syntax is used; the canonical runtime is PostgreSQL 17.

## Level and prerequisites

- **Level:** Advanced. The guide defines each new mechanism before relying on it.
- **Prerequisites:** [`sql-analytics-01`](sql_analytics_01_query_patterns.md), [`sql-quality-01`](sql_quality_01_bags_and_fanout.md), [`sql-deep-03`](sql_deep_03.md).
- **Artifacts:** [Learner SQL](../lessons/sql_deep_06.sql), [explained reference](../solutions/sql_deep_06_solutions.md), and [executable reference](../solutions/sql_deep_06_solutions.sql). Every fixture is local, deterministic and rolled back; no prior lesson state is required.

## Learning objectives

- State the output grain and identity before writing a query, including the NULL and duplicate policies.
- Explain the new SQL mechanism, produce each exact projected result and expose the listed counterexample.
- Verify rollback-safe behavior from inspected result rows and assertions without relying on a final success message.

## Vocabulary and concepts

- **Cohort:** A set of entities sharing a defined start event or period, such as a UTC signup day.

- **Follow-up maturity:** Whether enough trustworthy observation time exists to evaluate a specified outcome window for an entity.

- **Observation watermark:** A source-provided statement of how far event coverage is complete; elapsed calendar time alone does not establish completeness.

- **Calendar spine:** An explicit set of reporting dates joined to aggregates so absent groups remain visible rather than disappearing.

A retention percentage is a numerator and denominator policy expressed in SQL. Day 7 retention in this lesson means at least one event in the half-open interval[signup+7days, signup+8days). It does not mean any return within seven days, a calendar-week label or activity exactly seven 24-hour periods after signup. All timestamps are UTC and the chosen daily windows are fixed elapsed intervals.

Not every signed-up user can yet be labeled retained or not retained. A user whose outcome window is still in the future is pending follow-up. A user whose window has elapsed but whose observation watermark has not reached its end is also pending. Treating either as a nonretained zero biases recent or incompletely observed cohorts downward. Preserve a nullable label until eligibility is established.

Event availability is distinct from event occurrence. A record describing January 8 but arriving January 11 cannot be used in a historical report as of January 10. Filtering only occurred_at leaks later information into the past. The fixture includes such a late event and an incomplete observation watermark for its user, so the label remains pending rather than an unjustified zero.

Repeated events should not multiply retained users. EXISTS naturally produces one Boolean outcome per eligible user; counting distinct user identities is another approach when joining events. Aggregating event rows directly can overstate retention for highly active users. Build the user-level label table first, then aggregate cohorts from that grain.

Data quality remains a separate gate. The fixture intentionally includes an orphan event and a pre-signup event for diagnosis. A real publication must resolve or explicitly govern those defects rather than assume a correct final percentage excuses invalid input. The exercise calculations retain the defects so you can observe which filters and joins would otherwise hide them.

A calendar spine distinguishes an empty cohort from a cohort containing only pending users. Both can have zero eligible users and a NULL retention rate, but their operational meanings differ. Return total, eligible and retained counts alongside rates, and use state labels when reporting dates with no denominator. Neither a missing row nor a zero percentage communicates all of that information.

## Worked example / walkthrough

### Example 1

```sql
WITH activity(event_id,user_id) AS (VALUES(1,10),(2,10),(3,20))
SELECT 'observed_activity' AS metric_id,count(*) AS event_count,count(DISTINCT user_id) AS active_users
FROM activity;
```

The one-row output has metric_id, event_count, active_users with values observed_activity,3,2. Two events belong to the same user, so counting events would overstate the number of active people. The identifier used by COUNT DISTINCT must match the denominator's entity grain.

### Example 2

```sql
WITH instants(position,at) AS (VALUES
 (1,TIMESTAMPTZ '2026-01-08T00:00Z'),
 (2,TIMESTAMPTZ '2026-01-08T12:00Z'),
 (3,TIMESTAMPTZ '2026-01-09T00:00Z'))
SELECT position,at>=TIMESTAMPTZ '2026-01-08T00:00Z'
 AND at<TIMESTAMPTZ '2026-01-09T00:00Z' AS in_window
FROM instants ORDER BY position;
```

One row per position returns in_window true, true, false. The start is included and the exact end is excluded, preventing adjacent daily windows from both owning one instant. This fixture establishes the boundary policy before the cohort query introduces aggregation.

## Exercises

1. **Expose invalid event relationships before aggregation.** Return event_id, user_id, reason for events with an unknown user or occurrence before that user's signup. One diagnostic row represents one invalid event, ordered by event_id. Classify unknown_user before comparing signup time.

**Inputs/evidence:** For sql-deep-06 Exercise 1, Return event_id, user_id, reason for events with an unknown user or occurrence before that user's signup. One diagnostic row represents one invalid event, ordered by event_id. Classify unknown_user before comparing signup time.

**Expected result/shape:** For sql-deep-06 Exercise 1, Event 7, user 1 is before_signup; event 8, user 99 is unknown_user. Future availability alone is not a malformed relationship and is handled separately.

**Verify:** For sql-deep-06 Exercise 1, compare event and user identities before counting activity; classify orphan, pre-signup and not-yet-available evidence separately so invalid rows cannot enter the numerator.

2. **Define denominator eligibility using both clocks.** As ofJanuary 10 UTC, return user_id, cohort_day, eligible for each user. A day 7 label is eligible only when signup+8days is no later than both the report cutoff and observed_through. Preserve one row per user ordered by user_id.

**Inputs/evidence:** For sql-deep-06 Exercise 2, As ofJanuary 10 UTC, return user_id, cohort_day, eligible for each user. A day 7 label is eligible only when signup+8days is no later than both the report cutoff and observed_through. Preserve one row per user ordered by user_id.

**Expected result/shape:** For sql-deep-06 Exercise 2, Users 1,3,5 are eligible; users 2 and 4 are pending. User 2 has elapsed calendar time but an incomplete observation watermark. User 3 ends its window exactly at the cutoff and is eligible.

**Verify:** For sql-deep-06 Exercise 2, check both event-time maturity and availability-time eligibility at the report cutoff; explain why passing only one clock is insufficient.

3. **Create one nullable retention label per user.** Return user_id, eligible, day 7_retained from a user-level label CTE. Use EXISTS for available events in[signup+7days, signup+8days), and leave day 7_retained NULL when ineligible. Require event available_at no later than the historical cutoff. Order by user_id.

**Inputs/evidence:** For sql-deep-06 Exercise 3, Return user_id, eligible, day 7_retained from a user-level label CTE. Use EXISTS for available events in[signup+7days, signup+8days), and leave day 7_retained NULL when ineligible. Require event available_at no later than the historical cutoff. Order by user_id.

**Expected result/shape:** For sql-deep-06 Exercise 3, Users 1 and 3 are true, user 5 is false, and users 2 and 4 are NULL. User 1's multiple day 7 events still produce one true label; its exact window-end event is excluded.

**Verify:** For sql-deep-06 Exercise 3, construct the expected label from each eligible user event history: one for observed qualifying retention, zero only for complete mature nonretention, and NULL for pending observation.

4. **Report cohort rates with their denominators.** Aggregate user labels to cohort_day, total_users, eligible_users, retained_users, retention_rate, ordered by cohort_day. Count only eligible users in the rate denominator and only true labels in the numerator. Return NULL when no user is eligible, preserving the pending cohort.

**Inputs/evidence:** For sql-deep-06 Exercise 4, Aggregate user labels to cohort_day, total_users, eligible_users, retained_users, retention_rate, ordered by cohort_day. Count only eligible users in the rate denominator and only true labels in the numerator. Return NULL when no user is eligible, preserving the pending cohort.

**Expected result/shape:** For sql-deep-06 Exercise 4, January 1 has 3 total,2 eligible,1 retained, rate 0.5; January 2 has 1,1,1, rate 1; January 9 has 1,0,0, rateNULL.

**Verify:** For sql-deep-06 Exercise 4, sum eligible user labels and denominators independently, checking that pending labels do not silently enter either the retained count or mature denominator.

5. **Detect a historical feature or label leakage candidate.** Return event_id, user_id, event_before_cutoff, available_by_cutoff for events occurring no later thanJanuary 10 but available only afterward. One row represents one late-arriving historical event, ordered by event_id. Do not include events that themselves occur after the cutoff.

**Inputs/evidence:** For sql-deep-06 Exercise 5, Return event_id, user_id, event_before_cutoff, available_by_cutoff for events occurring no later thanJanuary 10 but available only afterward. One row represents one late-arriving historical event, ordered by event_id. Do not include events that themselves occur after the cutoff.

**Expected result/shape:** For sql-deep-06 Exercise 5, Only event 5 for user 2 appears, with event_before_cutoff=true and available_by_cutoff=false. Event 9 is future occurrence and is outside this particular late-arrival diagnostic.

**Verify:** For sql-deep-06 Exercise 5, compare each record availability timestamp with the historical prediction cutoff even when its event timestamp is earlier; identify late-arriving evidence that would leak future knowledge.

6. **Distinguish empty cohorts from pending-only cohorts.** Create a daily cohort spine forJanuary 1 throughJanuary 10 and left-join the cohort label summary. Return cohort_day, cohort_state, eligible_users, retention_rate ordered by cohort_day. Use empty for no signup rows, pending_only for signups but no eligible users, and has_eligible otherwise.

**Inputs/evidence:** For sql-deep-06 Exercise 6, Create a daily cohort spine forJanuary 1 throughJanuary 10 and left-join the cohort label summary. Return cohort_day, cohort_state, eligible_users, retention_rate ordered by cohort_day. Use empty for no signup rows, pending_only for signups but no eligible users, and has_eligible otherwise.

**Expected result/shape:** For sql-deep-06 Exercise 6, January 1 is has_eligible,2,0.5; January 2 has_eligible,1,1; January 9 pending_only,0, NULL; the other seven dates are empty,0, NULL. Ten date rows must remain.

**Verify:** For sql-deep-06 Exercise 6, left join the cohort spine to user-level evidence and distinguish zero users from users with no mature labels; inspect the count columns before interpreting a NULL rate.

## Common mistakes and diagnosis

If recent cohorts look worse, inspect denominator maturity and observation watermarks before fitting a trend. If retention exceeds 100%, check whether event counts replaced user counts. If a historical result improves after a later extraction, compare availability timestamps and source versions for leakage. If empty dates disappear, introduce an explicit calendar spine. If pending users become false labels, preserve NULL until the outcome window is complete. Treat orphan and pre-signup events as quality evidence requiring a policy, not as harmless rows that an inner join happened to remove.

## Self-check

- Explain the row grain after each FROM, JOIN, filter, grouping or window step. Name the identity columns that prove rows were neither lost nor multiplied.
- Reconstruct a boundary result by hand, then compare with the query output. Explain why the tempting wrong query fails even if it returns the same total on an easier fixture.

## Next step

Transfer the same reasoning to a new small fixture before using it on larger data, then continue with [the analytical query patterns guide](sql_analytics_01_query_patterns.md). Keep the result columns, ordering, NULL policy and observation horizon explicit. The [professional SQL track](../README.md) provides the wider route.

## Primary sources and official APIs

- [PostgreSQL17 aggregate FILTER and NULL behavior](https://www.postgresql.org/docs/17/functions-aggregate.html).

- [PostgreSQL17 timestamp functions](https://www.postgresql.org/docs/17/functions-datetime.html).

- [PostgreSQL17 generate_series](https://www.postgresql.org/docs/17/functions-srf.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through sql-deep-06: Cohort Denominators, Follow-Up Maturity, and Point-in-Time Quality.
Read sql/professional/companion-guides/sql_deep_06.md and sql/professional/lessons/sql_deep_06.sql. Direct prerequisites: sql-analytics-01, sql-quality-01, sql-deep-03.
Explain the row grain and SQL clauses, then ask me to predict a concrete result before my attempt. Give one hint at a time and review my exact result rows, identity, NULL behavior and boundary evidence. Ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt.
Use only the prepared local disposable advanced_sql_training database and the complete rollback-safe script. Preserve my ignored working copy and do not start services or redirect to another database.
Done when all six projected-result contracts and their counterexamples have inspected evidence and I can explain why the wrong query fails.
```
