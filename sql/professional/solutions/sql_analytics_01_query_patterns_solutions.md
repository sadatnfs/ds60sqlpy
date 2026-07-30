# SQL-ANALYTICS-01 Solutions — Analytical Patterns

Run:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_analytics_01_query_patterns_solutions.sql
```

The executable solution demonstrates safe, deterministic versions of all
fourteen prompts; the reasoning below explains the definitions and trade-offs
that query output alone cannot establish.

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

## Exercise 8 — Dense trailing seven-day activity

Generate one row per calendar date in the requested business zone and LEFT JOIN
deduplicated activity by local date. For each spine date, count distinct users
whose activity date is between that date minus six days and the date, inclusive.

`ROWS 6 PRECEDING` means six prior *rows*, so missing dates shorten the calendar
window. Daily distinct counts also cannot be summed for weekly uniques because
one user can appear on several days; retain user/date grain until the window.

## Exercise 9 — Session percentiles

First derive one row per session with duration. Then use
`percentile_cont(ARRAY[0.5,0.9]) WITHIN GROUP (ORDER BY duration)` over non-NULL
durations. Continuous percentile can interpolate; `percentile_disc` chooses an
observed value.

Expose session and NULL counts beside percentiles. Average answers a different
question and can hide a long tail; tiny cohorts need explicit caution.

## Exercise 10 — Ranking ties

Aggregate to one row per `(user_id,event_name)`, then calculate all three
functions ordered by count descending. `row_number` chooses exactly N rows;
`rank` gives ties one rank and leaves gaps; `dense_rank` leaves no gaps and can
return more than N rows.

Decide whether “top two” means exactly two categories or every category tied in
the top two score levels. Use a stable final display order without accidentally
destroying intentional score ties.

## Exercise 11 — Cycle-safe recursive hierarchy

Seed roots in a recursive CTE and carry `depth` plus an array path of visited
IDs. Recurse only when the next ID is absent from the path; emit or quarantine a
cycle flag so malformed data is visible rather than silently ignored.

The output grain is one reachable path/node relationship, not necessarily one
row per node in a multi-parent graph. Add operational depth/row guards, but
enforce the intended parent/cycle policy on writes when possible.

## Exercise 12 — Keep zero-activity dates

Start from a date spine and LEFT JOIN events with event predicates in `ON`.
Conditional aggregate each step without filtering away the preserved date.
Name each denominator and use `NULLIF(denominator,0)`.

Return numerators and denominators beside rates. Zero means an observed date
with no events; NULL can mean undefined rate or unavailable source.

## Exercise 13 — Approximate distinct counts

PostgreSQL core provides exact `count(DISTINCT user_id)`; approximation commonly
uses an approved sketch such as HyperLogLog outside this base lesson. Specify
error at expected cardinalities, memory, serialization, merge compatibility,
version ownership, privacy, and rebuild behavior before adoption.

Continuously compare sampled periods with exact counts. Daily estimates cannot
be summed for weekly uniques unless the sketch itself is mergeable.

## Exercise 14 — Parameterized analytical contract

Use typed start/end instants, zone, cohort, and threshold. Reject unknown zones,
nonpositive intervals, and `end <= start`; use half-open time filtering and
convert to local calendar labels only after defining instants.

Document result grain and stable order. Test duplicate sources, output-key
uniqueness, NULLs, empty windows, exact endpoints, timestamp ties, and a
daylight-saving transition.

## Edge cases

- Late events can rewrite sessions/funnels unless an as-of cutoff is recorded.
- Identity resolution across devices can change user grain.
- Calendar cohorts require an explicit business time zone.
- Attribution windows and models need versioning when definitions change.
