# SQL-ANALYTICS-01 Solutions — Analytical Patterns

Run:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_analytics_01_query_patterns_solutions.sql
```

The executable solution focuses on deduplication, 60-minute sessions, and an
ordered per-user funnel; the reasoning below completes the remaining prompts.

## Exercise 1 — Deduplication proof

Group the canonical view by `source_event_id` and fail on any count other than
one. Latest `ingested_at` wins because the source may retry/correct delivery;
`ingestion_id DESC` is the deterministic final tie-break. A real producer
contract must say whether later delivery is actually authoritative.

## Exercise 2 — Sixty-minute sessions

The solution uses `gap > interval '60 minutes'`, so an event exactly 60 minutes
later remains in the session. Change to `>=` if the definition says 60 minutes
starts a new session. Duration is `max(event_at)-min(event_at)`; a one-event
session has zero observed duration, not an estimate of user attention.

## Exercise 3 — Ordered funnel

Each correlated step selects its first event no earlier than the prior
timestamp. NULL propagates: a missing view means no add or purchase can qualify.
Validate `signup <= view <= add <= purchase` for non-NULL steps and retain
non-converters.

## Exercise 4 — Multi-day islands

After deriving `activity_date - row_number()`, group by user/island key and use
`HAVING COUNT(*) >= 2`. Input must first have one row per user-date. The output
grain is one consecutive run.

## Exercise 5 — Attribution ties and missing touches

Use a LEFT LATERAL join ordered by `touched_at DESC, touch_id DESC`. The identity
defines the same-timestamp winner. A purchase with no qualifying seven-day touch
remains with NULL campaign. Never turn the join inner unless the metric excludes
unattributed purchases by definition.

## Exercise 6 — Retention

Calculate and expose three fields separately: original cohort size, distinct
returning users in month N, and numeric division. Add a user with no later
activity to prove the denominator does not shrink. Decide whether signup itself
counts as month-zero activity.

## Exercise 7 — As-of boundary

Use `valid_from <= event_at AND event_at < valid_to`, treating NULL `valid_to` as
open-ended. At the boundary the old row is excluded and the successor included.
Also assert that every fact matches at most one history row; `LIMIT 1` alone can
hide overlap corruption.

## Edge cases

- Late events can rewrite sessions/funnels unless an as-of cutoff is recorded.
- Identity resolution across devices can change user grain.
- Calendar cohorts require an explicit business time zone.
- Attribution windows and models need versioning when definitions change.

