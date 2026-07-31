# SQL-ANALYTICS-01 Solutions — Analytical Patterns


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_analytics_01_query_patterns_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_analytics_01_query_patterns_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Grain, Canonical row, Session, Gap/island, Funnel, Attribution window. Its worked-model focus is:
The raw event grain is one ingestion attempt, so sourceeventid can repeat. The canonical view partitions by source ID and chooses latest ingestedat, then identity as a final tie-break. Deduplication happens before every downstream pattern to avoid double-counting retries.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 1, compare raw `pro_analytics_lab.events` with `deduplicated_events`, choosing one canonical row per `source_event_id` by `ingested_at DESC, ingestion_id DESC` before any downstream analysis.
- **Expected result/shape:** For sql-analytics-01 Exercise 1, expected output: one row per source event with `source_event_id`, `canonical_rows`, `winner_ingested_at`, and `winner_ingestion_id`, ordered by source ID; every canonical count is 1, and the conflicting-payload diagnostic is empty.
- **Independent verification:** For sql-analytics-01 Exercise 1, independently rank raw deliveries, test an equal-timestamp tie, require the greater ingestion ID to win, and separately flag one source ID whose retries disagree on business payload.

## Exercise 2 — Sixty-minute sessions

The solution uses `gap > interval '60 minutes'`, so an event exactly 60 minutes
later remains in the session. Change to `>=` if the definition says 60 minutes
starts a new session. Duration is `max(event_at)-min(event_at)`; a one-event
session has zero observed duration, not an estimate of user attention.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 2, order canonical events by `event_at, source_event_id` per user, mark a new session only when the previous gap exceeds 60 minutes, cumulatively number sessions, then aggregate.
- **Expected result/shape:** For sql-analytics-01 Exercise 2, expected output: one row per `(user_id, session_number)` with `started_at`, `ended_at`, `duration`, and `events`, ordered by user and session; a one-event session has zero duration.
- **Independent verification:** For sql-analytics-01 Exercise 2, prove an exact 60-minute gap stays in the session while 60 minutes and one second starts another, and reconcile the sum of session event counts with the canonical event count.

## Exercise 3 — Ordered funnel

Each correlated step selects its first event no earlier than the prior
timestamp. NULL propagates: a missing view means no add or purchase can qualify.
Validate `signup <= view <= add <= purchase` for non-NULL steps and retain
non-converters.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 3, anchor each user at the earliest canonical signup and select the first view, add-to-cart, and purchase at or after the already-chosen predecessor timestamp.
- **Expected result/shape:** For sql-analytics-01 Exercise 3, expected output: one row per signed-up user with `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at`, ordered by user; an absent predecessor leaves all later steps NULL.
- **Independent verification:** For sql-analytics-01 Exercise 3, assert every non-NULL timestamp chain is nondecreasing, prove a view-only user is excluded, and prove a signup-only user remains once with NULL later timestamps.

## Exercise 4 — Multi-day islands

After deriving `activity_date - row_number()`, group by user/island key and use
`HAVING COUNT(*) >= 2`. Input must first have one row per user-date. The output
grain is one consecutive run.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 4, reduce canonical events to distinct `(user_id, activity_date)` rows, subtract row number from each date to form an island key, and group by user plus island.
- **Expected result/shape:** For sql-analytics-01 Exercise 4, expected output: one row per consecutive-day island lasting at least two days, with `user_id`, `island_start`, `island_end`, and `active_days`, ordered by user and start date.
- **Independent verification:** For sql-analytics-01 Exercise 4, test a two-day run, a one-day run, a gap, and duplicate same-day events; require only qualifying consecutive runs and prove duplicates do not inflate active-day counts.

## Exercise 5 — Attribution ties and missing touches

Use a LEFT LATERAL join ordered by `touched_at DESC, touch_id DESC`. The identity
defines the same-timestamp winner. A purchase with no qualifying seven-day touch
remains with NULL campaign. Never turn the join inner unless the metric excludes
unattributed purchases by definition.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 5, start from each canonical purchase in `pro_analytics_lab.deduplicated_events` and use a LEFT LATERAL lookup in `pro_analytics_lab.campaign_touches` for at most one touch in the preceding seven days, ordered by `touched_at DESC, touch_id DESC`.
- **Expected result/shape:** For sql-analytics-01 Exercise 5, expected output: one row per purchase with `source_event_id`, `user_id`, `purchased_at`, `touch_id`, `campaign`, and `touched_at`, ordered by source ID; unmatched purchases retain NULL attribution and the greater touch ID wins an equal-time tie.
- **Independent verification:** For sql-analytics-01 Exercise 5, reconcile output count and unique source IDs with all purchases, test one unattributed purchase, and remove the ID tie-breaker in a disposable copy to expose nondeterministic attribution.

## Exercise 6 — Retention

Calculate and expose three fields separately: original cohort size, distinct
returning users in month N, and numeric division. Add a user with no later
activity to prove the denominator does not shrink. Decide whether signup itself
counts as month-zero activity.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 6, define cohort month from each user's earliest canonical event, reduce activity to distinct user/month rows, and LEFT JOIN activity so nonretained cohort members remain in the denominator.
- **Expected result/shape:** For sql-analytics-01 Exercise 6, expected output: one row per `cohort_month` with `cohort_users`, `month_1_users`, and four-decimal `month_1_rate`, ordered by cohort; zero denominators are protected with `NULLIF`.
- **Independent verification:** For sql-analytics-01 Exercise 6, independently list cohort and month-one member IDs, compare both distinct counts, and add one nonretained member to prove only the denominator and rate change.

## Exercise 7 — As-of boundary

Use `valid_from <= event_at AND event_at < valid_to`, treating NULL `valid_to` as
open-ended. At the boundary the old row is excluded and the successor included.
Also assert that every fact matches at most one history row; `LIMIT 1` alone can
hide overlap corruption.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 7, join `pro_analytics_lab.event_probes` to adjacent half-open rows in `pro_analytics_lab.user_tiers` using `valid_from <= event_at` and `event_at < COALESCE(valid_to, infinity)`, retaining probe grain.
- **Expected result/shape:** For sql-analytics-01 Exercise 7, expected output: one row per probe with `probe_id`, `event_at`, `tier_name`, validity bounds, and `matching_tiers`, ordered by probe; the shared-boundary probe matches the successor exactly once.
- **Independent verification:** For sql-analytics-01 Exercise 7, require no probe to match more than one tier, test just before/at/after the shared boundary, and inject an overlap to prove the assertion fails instead of hiding ambiguity with a row limit.

## Exercise 8 — Dense trailing seven-day activity

Generate one row per calendar date in the requested business zone and LEFT JOIN
deduplicated activity by local date. For each spine date, count distinct users
whose activity date is between that date minus six days and the date, inclusive.

`ROWS 6 PRECEDING` means six prior *rows*, so missing dates shorten the calendar
window. Daily distinct counts also cannot be summed for weekly uniques because
one user can appear on several days; retain user/date grain until the window.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 8, generate every UTC report date from 2026-01-01 through 2026-01-08 and count distinct users in the inclusive seven-calendar-day window ending on each date.
- **Expected result/shape:** For sql-analytics-01 Exercise 8, expected output: exactly eight ordered rows with `report_date` and `trailing_7d_active_users`; dates without events remain because the dense date spine is the preserved side.
- **Independent verification:** For sql-analytics-01 Exercise 8, independently list distinct users for two half-open seven-day windows and add the same user on another day to prove weekly distinct count rises by at most one.

## Exercise 9 — Session percentiles

First derive one row per session with duration. Then use
`percentile_cont(ARRAY[0.5,0.9]) WITHIN GROUP (ORDER BY duration)` over non-NULL
durations. Continuous percentile can interpolate; `percentile_disc` chooses an
observed value.

Expose session and NULL counts beside percentiles. Average answers a different
question and can hide a long tail; tiny cohorts need explicit caution.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 9, derive one row per session with the 60-minute rule, then pass non-NULL session durations—not raw events—to ordered-set percentile aggregates.
- **Expected result/shape:** For sql-analytics-01 Exercise 9, expected output: one aggregate row with `session_count` and a two-element interval array `median_and_p90` from continuous percentiles 0.5 and 0.9.
- **Independent verification:** For sql-analytics-01 Exercise 9, materialize and sort session durations, reconcile the session count, compare continuous percentile, discrete percentile, and average on a skewed fixture, and confirm empty input yields NULL percentiles.

## Exercise 10 — Ranking ties

Aggregate to one row per `(user_id,event_name)`, then calculate all three
functions ordered by count descending. `row_number` chooses exactly N rows;
`rank` gives ties one rank and leaves gaps; `dense_rank` leaves no gaps and can
return more than N rows.

Decide whether “top two” means exactly two categories or every category tied in
the top two score levels. Use a stable final display order without accidentally
destroying intentional score ties.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 10, aggregate canonical events to `(user_id, event_name)` counts and calculate `row_number`, `rank`, and `dense_rank` side by side within each user.
- **Expected result/shape:** For sql-analytics-01 Exercise 10, expected output: one row per user/event type with `event_count` and all three rank positions, ordered by user and deterministic row-number position; only row number breaks count ties by event name.
- **Independent verification:** For sql-analytics-01 Exercise 10, create tied counts and prove `row_number <= 2` returns exactly two rows while tie-preserving rank filters can return more, then state the report's chosen meaning of top two.

## Exercise 11 — Cycle-safe recursive hierarchy

Seed roots in a recursive CTE and carry `depth` plus an array path of visited
IDs. Recurse only when the next ID is absent from the path; emit or quarantine a
cycle flag so malformed data is visible rather than silently ignored.

The output grain is one reachable path/node relationship, not necessarily one
row per node in a multi-parent graph. Add operational depth/row guards, but
enforce the intended parent/cycle policy on writes when possible.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 11, traverse `pro_analytics_lab.campaign_nodes` from roots with a recursive CTE carrying depth and an integer-array path, refusing any child already present in that path.
- **Expected result/shape:** For sql-analytics-01 Exercise 11, expected output: one ordered hierarchy row per root-reachable node/path with `campaign_id`, `parent_campaign_id`, `depth`, and `path`, plus a diagnostic result listing unreachable IDs from the rootless cycle.
- **Independent verification:** For sql-analytics-01 Exercise 11, require no repeated ID in any returned path, prove recursion terminates, and reconcile reachable plus unreachable campaign IDs with every fixture ID.

## Exercise 12 — Keep zero-activity dates

Start from a date spine and LEFT JOIN events with event predicates in `ON`.
Conditional aggregate each step without filtering away the preserved date.
Name each denominator and use `NULLIF(denominator,0)`.

Return numerators and denominators beside rates. Zero means an observed date
with no events; NULL can mean undefined rate or unavailable source.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 12, start from a four-day spine and LEFT JOIN canonical events with half-open UTC day bounds, applying signup and purchase conditions inside aggregate filters.
- **Expected result/shape:** For sql-analytics-01 Exercise 12, expected output: exactly four rows with `report_date`, `signups`, and `purchasers`, ordered by date; dates with no activity remain and show numeric zero.
- **Independent verification:** For sql-analytics-01 Exercise 12, compare each day with direct control queries and move an event condition to WHERE in a disposable copy to demonstrate why NULL-extended dates would disappear.

## Exercise 13 — Approximate distinct counts

PostgreSQL core provides exact `count(DISTINCT user_id)`; approximation commonly
uses an approved sketch such as HyperLogLog outside this base lesson. Specify
error at expected cardinalities, memory, serialization, merge compatibility,
version ownership, privacy, and rebuild behavior before adoption.

Continuously compare sampled periods with exact counts. Daily estimates cannot
be summed for weekly uniques unless the sketch itself is mergeable.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 13, compute core PostgreSQL's exact distinct-user count from `pro_analytics_lab.deduplicated_events` and separately review an adoption matrix for any optional approximate sketch.
- **Expected result/shape:** For sql-analytics-01 Exercise 13, expected output: one scalar `exact_distinct_users` row plus an ordered review matrix with `criterion_number`, `criterion`, and `required_evidence`, covering implementation/version, error budget, mergeability, fallback, and ownership; no unavailable extension is presented as executed.
- **Independent verification:** For sql-analytics-01 Exercise 13, compare the scalar result with a distinct-user subquery and, for any approved sketch, measure relative error across representative cardinalities; unavailable capability or excess error must select the exact fallback.

## Exercise 14 — Parameterized analytical contract

Use typed start/end instants, zone, cohort, and threshold. Reject unknown zones,
nonpositive intervals, and `end <= start`; use half-open time filtering and
convert to local calendar labels only after defining instants.

Document result grain and stable order. Test duplicate sources, output-key
uniqueness, NULLs, empty windows, exact endpoints, timestamp ties, and a
daylight-saving transition.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 14, validate typed start/end instants before filtering canonical events with a half-open time window, rejecting NULL, equal, or reversed bounds as invalid parameters.
- **Expected result/shape:** For sql-analytics-01 Exercise 14, expected output: one row per canonical source event inside the valid interval with `source_event_id` and `event_at`, ordered by time and source ID; invalid bounds raise SQLSTATE `22023`.
- **Independent verification:** For sql-analytics-01 Exercise 14, test both endpoints, equal/reversed/NULL bounds, duplicate deliveries, timestamp ties, an empty valid interval, and a daylight-saving transition expressed as absolute instants.

## Edge cases

- Late events can rewrite sessions/funnels unless an as-of cutoff is recorded.
- Identity resolution across devices can change user grain.
- Calendar cohorts require an explicit business time zone.
- Attribution windows and models need versioning when definitions change.
