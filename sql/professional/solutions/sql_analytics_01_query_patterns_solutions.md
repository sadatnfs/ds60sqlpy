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

- **Inputs/evidence:** For sql-analytics-01 Exercise 1, complete the deduplication written analysis and support its claims with read-only evidence from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-analytics-01 Exercise 1, expected output: a completed the deduplication written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `source_event_id`, `ingested_at`, and `ingestion_id`.
- **Independent verification:** For sql-analytics-01 Exercise 1, check the deduplication written analysis against `source_event_id`, `ingested_at`, and `ingestion_id`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-analytics-01 Exercise 1, check the deduplication written analysis against `source_event_id`, `ingested_at`, and `ingestion_id`.
- **Clause check:** For sql-analytics-01 Exercise 1, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity` or label it as proposed policy.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 1, the chosen form is justified by this lesson-specific rationale: Group the canonical view by `source_event_id` and fail on any count other than one. Evaluate another form against the concrete expected result (a completed the deduplication written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 2 — Sixty-minute sessions

The solution uses `gap > interval '60 minutes'`, so an event exactly 60 minutes
later remains in the session. Change to `>=` if the definition says 60 minutes
starts a new session. Duration is `max(event_at)-min(event_at)`; a one-event
session has zero observed duration, not an estimate of user attention.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 2, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `user_id`, `session_number`, `started_at`, `ended_at`, `duration`, and `events`; keep `user_id`, and `session_number` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-analytics-01 Exercise 2, expected output: one row per `user_id`, and `session_number`. The final columns are `user_id`, `session_number`, `started_at`, `ended_at`, `duration`, and `events`. The final order is `user_id, session_number`.
- **Independent verification:** For sql-analytics-01 Exercise 2, independently aggregate `pro_analytics_lab.deduplicated_events` by `user_id`, and `session_number`; require one output row for every distinct `user_id`, and `session_number` tuple and compare `duration`, and `events` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `duration`, and `events` for the existing `user_id`, and `session_number` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-analytics-01 Exercise 2, run `lagged`, and `numbered` one at a time. Record each CTE's row count and `user_id`, and `session_number` uniqueness before the next stage uses it.
- **Clause check:** For sql-analytics-01 Exercise 2, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_analytics_lab.deduplicated_events`, preserve one row per `user_id`, and `session_number`, and finish with `user_id`, `session_number`, `started_at`, `ended_at`, `duration`, and `events` ordered by `user_id, session_number`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 2, the chosen form is justified by this lesson-specific rationale: The solution uses `gap > interval '60 minutes'`, so an event exactly 60 minutes later remains in the session. Evaluate another form against the concrete expected result (one row per `user_id`, and `session_number`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `duration`, and `events` for the existing `user_id`, and `session_number` tuple and verify the new tuple appears exactly once.

## Exercise 3 — Ordered funnel

Each correlated step selects its first event no earlier than the prior
timestamp. NULL propagates: a missing view means no add or purchase can qualify.
Validate `signup <= view <= add <= purchase` for non-NULL steps and retain
non-converters.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 3, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at`; keep `user_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-analytics-01 Exercise 3, expected output: one row per `user_id`. The final columns are `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at`. The final order is `c.user_id`.
- **Independent verification:** For sql-analytics-01 Exercise 3, reselect the returned keys directly from the source; require unique `user_id` where the expected grain is one row per key and confirm the projected `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at` against `pro_analytics_lab.deduplicated_events`. Add one source row with a new `user_id`; verify the result gains exactly one row carrying that `user_id` value.
- **Intermediate relation check:** For sql-analytics-01 Exercise 3, run `signup`, `funnel`, and `completed` one at a time. Record each CTE's row count and `user_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-analytics-01 Exercise 3, the solution actually uses `WITH`, `FROM`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_analytics_lab.deduplicated_events`, preserve one row per `user_id`, and finish with `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at` ordered by `c.user_id`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 3, the chosen form is justified by this lesson-specific rationale: Each correlated step selects its first event no earlier than the prior timestamp. Evaluate another form against the concrete expected result (one row per `user_id`) and the verification above.
- **Edge case:** Add one source row with a new `user_id`; verify the result gains exactly one row carrying that `user_id` value.

## Exercise 4 — Multi-day islands

After deriving `activity_date - row_number()`, group by user/island key and use
`HAVING COUNT(*) >= 2`. Input must first have one row per user-date. The output
grain is one consecutive run.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 4, read from `pro_analytics_lab.deduplicated_events`. Compute `user_id`, `island_start`, `island_end`, and `active_days` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-analytics-01 Exercise 4, expected output: one row per user-date. The final columns are `user_id`, `island_start`, `island_end`, and `active_days`. The final order is `n.user_id, island_start`.
- **Independent verification:** For sql-analytics-01 Exercise 4, evaluate each of `island_start`, `island_end`, and `active_days` in a separate control `SELECT` over `pro_analytics_lab.deduplicated_events`; require one final row and compare every value. Add one row to an existing group and one row for a new group; recompute `island_start`, `island_end`, and `active_days` for the existing `user_id`, and `island_key` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-analytics-01 Exercise 4, run `active_days`, and `numbered` one at a time. Record each CTE's row count and `user_id`, and `island_key` uniqueness before the next stage uses it.
- **Clause check:** For sql-analytics-01 Exercise 4, the solution actually uses `WITH`, `FROM`, `GROUP BY`, `HAVING`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_analytics_lab.deduplicated_events`, preserve one row per `user_id`, and `island_key`, and finish with `user_id`, `island_start`, `island_end`, and `active_days` ordered by `n.user_id, island_start`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 4, the chosen form is justified by this lesson-specific rationale: After deriving `activity_date - row_number()`, group by user/island key and use `HAVING COUNT() >= 2`. Evaluate another form against the concrete expected result (one row per user-date) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `island_start`, `island_end`, and `active_days` for the existing `user_id`, and `island_key` tuple and verify the new tuple appears exactly once.

## Exercise 5 — Attribution ties and missing touches

Use a LEFT LATERAL join ordered by `touched_at DESC, touch_id DESC`. The identity
defines the same-timestamp winner. A purchase with no qualifying seven-day touch
remains with NULL campaign. Never turn the join inner unless the metric excludes
unattributed purchases by definition.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 5, read from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Build the answer toward `touched_at`, and `touch_id`; keep `touch_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-analytics-01 Exercise 5, expected output: one row per `touch_id`. The final columns are `touched_at`, and `touch_id`.
- **Independent verification:** For sql-analytics-01 Exercise 5, reselect the returned keys directly from the source; require unique `touch_id` where the expected grain is one row per key and confirm the projected `touched_at`, and `touch_id` against `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Add two tied candidates and prove `touch_id` identifies both without accidental loss.
- **Intermediate relation check:** For sql-analytics-01 Exercise 5, select `touch_id` from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity` before adding derived columns.
- **Clause check:** For sql-analytics-01 Exercise 5, the solution actually uses `WITH`. Read only those operations: begin at `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`, preserve one row per `touch_id`, and finish with `touched_at`, and `touch_id`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 5, the chosen form is justified by this lesson-specific rationale: Use a LEFT LATERAL join ordered by `touched_at DESC, touch_id DESC`. Evaluate another form against the concrete expected result (one row per `touch_id`) and the verification above.
- **Edge case:** Add two tied candidates and prove `touch_id` identifies both without accidental loss.

## Exercise 6 — Retention

Calculate and expose three fields separately: original cohort size, distinct
returning users in month N, and numeric division. Add a user with no later
activity to prove the denominator does not shrink. Decide whether signup itself
counts as month-zero activity.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 6, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `cohort_month`, `cohort_users`, and `month_1_users`; keep `cohort_month` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-analytics-01 Exercise 6, expected output: one row per `cohort_month`. The final columns are `cohort_month`, `cohort_users`, and `month_1_users`. The final order is `c.cohort_month`.
- **Independent verification:** For sql-analytics-01 Exercise 6, independently aggregate `pro_analytics_lab.deduplicated_events` by `cohort_month`; require one output row for every distinct `cohort_month` tuple and compare `cohort_users`, and `month_1_users` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `cohort_users`, and `month_1_users` for the existing `cohort_month` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-analytics-01 Exercise 6, run `cohorts`, and `activity` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
- **Clause check:** For sql-analytics-01 Exercise 6, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_analytics_lab.deduplicated_events`, preserve one row per `cohort_month`, and finish with `cohort_month`, `cohort_users`, and `month_1_users` ordered by `c.cohort_month`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 6, the chosen form is justified by this lesson-specific rationale: Calculate and expose three fields separately: original cohort size, distinct returning users in month N, and numeric division. Evaluate another form against the concrete expected result (one row per `cohort_month`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `cohort_users`, and `month_1_users` for the existing `cohort_month` tuple and verify the new tuple appears exactly once.

## Exercise 7 — As-of boundary

Use `valid_from <= event_at AND event_at < valid_to`, treating NULL `valid_to` as
open-ended. At the boundary the old row is excluded and the successor included.
Also assert that every fact matches at most one history row; `LIMIT 1` alone can
hide overlap corruption.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 7, read from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Build the answer toward `valid_from`, `event_at`, and `valid_to`; keep `valid_from` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-analytics-01 Exercise 7, expected output: one row per `valid_from`. The final columns are `valid_from`, `event_at`, and `valid_to`.
- **Independent verification:** For sql-analytics-01 Exercise 7, reselect the returned keys directly from the source; require unique `valid_from` where the expected grain is one row per key and confirm the projected `valid_from`, `event_at`, and `valid_to` against `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-analytics-01 Exercise 7, select `valid_from` from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity` before adding derived columns.
- **Clause check:** For sql-analytics-01 Exercise 7, the solution actually uses `WITH`, `ORDER BY`, and `LIMIT`. Read only those operations: begin at `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`, preserve one row per `valid_from`, and finish with `valid_from`, `event_at`, and `valid_to`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 7, the chosen form is justified by this lesson-specific rationale: Use `valid_from <= event_at AND event_at < valid_to`, treating NULL `valid_to` as open-ended. Evaluate another form against the concrete expected result (one row per `valid_from`) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.

## Exercise 8 — Dense trailing seven-day activity

Generate one row per calendar date in the requested business zone and LEFT JOIN
deduplicated activity by local date. For each spine date, count distinct users
whose activity date is between that date minus six days and the date, inclusive.

`ROWS 6 PRECEDING` means six prior *rows*, so missing dates shorten the calendar
window. Daily distinct counts also cannot be summed for weekly uniques because
one user can appear on several days; retain user/date grain until the window.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 8, read from `pro_analytics_lab.deduplicated_events`. Compute `report_date`, and `trailing_7d_active_users` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-analytics-01 Exercise 8, expected output: one row per calendar date in the requested business zone and LEFT JOIN deduplicated activity by local date. The final columns are `report_date`, and `trailing_7d_active_users`. The final order is `s.report_date`.
- **Independent verification:** For sql-analytics-01 Exercise 8, evaluate each of `report_date`, and `trailing_7d_active_users` in a separate control `SELECT` over `pro_analytics_lab.deduplicated_events`; require one final row and compare every value. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-analytics-01 Exercise 8, run `spine` one at a time. Record each CTE's row count and `report_date` uniqueness before the next stage uses it.
- **Clause check:** For sql-analytics-01 Exercise 8, the solution actually uses `WITH`, `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_analytics_lab.deduplicated_events`, preserve exactly one summary row, and finish with `report_date`, and `trailing_7d_active_users` ordered by `s.report_date`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 8, the chosen form is justified by this lesson-specific rationale: Generate one row per calendar date in the requested business zone and LEFT JOIN deduplicated activity by local date. Evaluate another form against the concrete expected result (one row per calendar date in the requested business zone and LEFT JOIN deduplicated activity by local date) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.

## Exercise 9 — Session percentiles

First derive one row per session with duration. Then use
`percentile_cont(ARRAY[0.5,0.9]) WITHIN GROUP (ORDER BY duration)` over non-NULL
durations. Continuous percentile can interpolate; `percentile_disc` chooses an
observed value.

Expose session and NULL counts beside percentiles. Average answers a different
question and can hide a long tail; tiny cohorts need explicit caution.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 9, use `pro_analytics_lab.deduplicated_events` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-analytics-01 Exercise 9, expected output: one row per session with duration. The final columns are `session_count`, and `median_and_p90`.
- **Independent verification:** For sql-analytics-01 Exercise 9, restore into an isolated target and reconcile `pro_analytics_lab.deduplicated_events` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-analytics-01 Exercise 9, run `lagged`, `numbered`, and `sessions` one at a time. Record each CTE's row count and `artifact_name` and `restored_object` uniqueness before the next stage uses it.
- **Clause check:** For sql-analytics-01 Exercise 9, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_analytics_lab.deduplicated_events`, preserve exactly one summary row, and finish with `session_count`, and `median_and_p90`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 9, the chosen form is justified by this lesson-specific rationale: First derive one row per session with duration. Evaluate another form against the concrete expected result (one row per session with duration) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Exercise 10 — Ranking ties

Aggregate to one row per `(user_id,event_name)`, then calculate all three
functions ordered by count descending. `row_number` chooses exactly N rows;
`rank` gives ties one rank and leaves gaps; `dense_rank` leaves no gaps and can
return more than N rows.

Decide whether “top two” means exactly two categories or every category tied in
the top two score levels. Use a stable final display order without accidentally
destroying intentional score ties.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 10, read from `pro_analytics_lab.deduplicated_events`. Compute `user_id`, and `event_name` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-analytics-01 Exercise 10, expected output: one row per `(user_id,event_name)`, then calculate all three functions ordered by count descending. The final columns are `user_id`, and `event_name`. The final order is `c.user_id, row_number_position`.
- **Independent verification:** For sql-analytics-01 Exercise 10, evaluate each of `event_name` in a separate control `SELECT` over `pro_analytics_lab.deduplicated_events`; require one final row and compare every value. Give two rows the same `c.user_id` value and different `row_number_position` values; verify `c.user_id, row_number_position` produces the intended rank and display order.
- **Intermediate relation check:** For sql-analytics-01 Exercise 10, run `counts` one at a time. Record each CTE's row count and `user_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-analytics-01 Exercise 10, the solution actually uses `WITH`, `FROM`, `GROUP BY`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_analytics_lab.deduplicated_events`, preserve exactly one summary row, and finish with `user_id`, and `event_name` ordered by `c.user_id, row_number_position`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 10, the chosen form is justified by this lesson-specific rationale: Aggregate to one row per `(user_id,event_name)`, then calculate all three functions ordered by count descending. Evaluate another form against the concrete expected result (one row per `(user_id,event_name)`, then calculate all three functions ordered by count descending) and the verification above.
- **Edge case:** Give two rows the same `c.user_id` value and different `row_number_position` values; verify `c.user_id, row_number_position` produces the intended rank and display order.

## Exercise 11 — Cycle-safe recursive hierarchy

Seed roots in a recursive CTE and carry `depth` plus an array path of visited
IDs. Recurse only when the next ID is absent from the path; emit or quarantine a
cycle flag so malformed data is visible rather than silently ignored.

The output grain is one reachable path/node relationship, not necessarily one
row per node in a multi-parent graph. Add operational depth/row guards, but
enforce the intended parent/cycle policy on writes when possible.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 11, read from `pro_analytics_lab.campaign_nodes`, and `tree`. Compute `campaign_id`, `parent_campaign_id`, `depth`, and `path` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-analytics-01 Exercise 11, expected output: one row per node in a multi-parent graph. The final columns are `campaign_id`, `parent_campaign_id`, `depth`, and `path`. The final order is `path`.
- **Independent verification:** For sql-analytics-01 Exercise 11, evaluate each of `parent_campaign_id`, `depth`, and `path` in a separate control `SELECT` over `pro_analytics_lab.campaign_nodes`, and `tree`; require one final row and compare every value. Add one source row with a new `campaign_id`; verify the result gains exactly one row carrying that `campaign_id` value.
- **Intermediate relation check:** For sql-analytics-01 Exercise 11, start with the first relation in `pro_analytics_lab.campaign_nodes`, and `tree`; after each join, record total rows and distinct `campaign_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-analytics-01 Exercise 11, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_analytics_lab.campaign_nodes`, and `tree`, preserve exactly one summary row, and finish with `campaign_id`, `parent_campaign_id`, `depth`, and `path` ordered by `path`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 11, the chosen form is justified by this lesson-specific rationale: Seed roots in a recursive CTE and carry `depth` plus an array path of visited IDs. Evaluate another form against the concrete expected result (one row per node in a multi-parent graph) and the verification above.
- **Edge case:** Add one source row with a new `campaign_id`; verify the result gains exactly one row carrying that `campaign_id` value.

## Exercise 12 — Keep zero-activity dates

Start from a date spine and LEFT JOIN events with event predicates in `ON`.
Conditional aggregate each step without filtering away the preserved date.
Name each denominator and use `NULLIF(denominator,0)`.

Return numerators and denominators beside rates. Zero means an observed date
with no events; NULL can mean undefined rate or unavailable source.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 12, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `report_date`, `signups`, and `purchasers`; keep `report_date` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-analytics-01 Exercise 12, expected output: one row per `report_date`. The final columns are `report_date`, `signups`, and `purchasers`. The final order is `s.report_date`.
- **Independent verification:** For sql-analytics-01 Exercise 12, independently aggregate `pro_analytics_lab.deduplicated_events` by `report_date`; require one output row for every distinct `report_date` tuple and compare `signups`, and `purchasers` tuple by tuple. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-analytics-01 Exercise 12, run `spine` one at a time. Record each CTE's row count and `report_date` uniqueness before the next stage uses it.
- **Clause check:** For sql-analytics-01 Exercise 12, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_analytics_lab.deduplicated_events`, preserve one row per `report_date`, and finish with `report_date`, `signups`, and `purchasers` ordered by `s.report_date`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 12, the chosen form is justified by this lesson-specific rationale: Start from a date spine and LEFT JOIN events with event predicates in `ON`. Evaluate another form against the concrete expected result (one row per `report_date`) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.

## Exercise 13 — Approximate distinct counts

PostgreSQL core provides exact `count(DISTINCT user_id)`; approximation commonly
uses an approved sketch such as HyperLogLog outside this base lesson. Specify
error at expected cardinalities, memory, serialization, merge compatibility,
version ownership, privacy, and rebuild behavior before adoption.

Continuously compare sampled periods with exact counts. Daily estimates cannot
be summed for weekly uniques unless the sketch itself is mergeable.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 13, read the target keys from `pro_analytics_lab.deduplicated_events` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-analytics-01 Exercise 13, expected output: the command tag and an independently counted set of affected `exact_distinct_users` values. The final columns are `exact_distinct_users`.
- **Independent verification:** For sql-analytics-01 Exercise 13, materialize the intended `exact_distinct_users` target set first; require the command tag/`RETURNING` set to match it, then query `pro_analytics_lab.deduplicated_events` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `exact_distinct_users` values in both cases.
- **Intermediate relation check:** For sql-analytics-01 Exercise 13, materialize the intended `exact_distinct_users` target set first; require the command tag/`RETURNING` set to match it, then query `pro_analytics_lab.deduplicated_events` again and prove rollback or idempotent retry.
- **Clause check:** For sql-analytics-01 Exercise 13, the solution actually uses `FROM`, and `SELECT`. Read only those operations: begin at `pro_analytics_lab.deduplicated_events`, preserve one row per `exact_distinct_users`, and finish with `exact_distinct_users`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 13, the chosen form is justified by this lesson-specific rationale: PostgreSQL core provides exact `count(DISTINCT user_id)`; approximation commonly uses an approved sketch such as HyperLogLog outside this base lesson. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `exact_distinct_users` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `exact_distinct_users` values in both cases.

## Exercise 14 — Parameterized analytical contract

Use typed start/end instants, zone, cohort, and threshold. Reject unknown zones,
nonpositive intervals, and `end <= start`; use half-open time filtering and
convert to local calendar labels only after defining instants.

Document result grain and stable order. Test duplicate sources, output-key
uniqueness, NULLs, empty windows, exact endpoints, timestamp ties, and a
daylight-saving transition.

### Reasoning and verification

- **Inputs/evidence:** For sql-analytics-01 Exercise 14, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `source_event_id`, and `event_at`; keep `source_event_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-analytics-01 Exercise 14, expected output: one row per `source_event_id`. The final columns are `source_event_id`, and `event_at`. The final order is `de.event_at, de.source_event_id`.
- **Independent verification:** For sql-analytics-01 Exercise 14, project `source_event_id` plus the raw source columns from `pro_analytics_lab.deduplicated_events` at each join stage; record row count and distinct `source_event_id`, then assert the final `source_event_id`, and `event_at` values match those staged rows without unintended fanout or loss. Repeat with `NULL` in `source_event_id`, and `event_at` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-analytics-01 Exercise 14, run `parameters` one at a time. Record each CTE's row count and `source_event_id` uniqueness before the next stage uses it.
- **Clause check:** For sql-analytics-01 Exercise 14, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_analytics_lab.deduplicated_events`, preserve one row per `source_event_id`, and finish with `source_event_id`, and `event_at` ordered by `de.event_at, de.source_event_id`.
- **Alternative/trade-off:** For sql-analytics-01 Exercise 14, the chosen form is justified by this lesson-specific rationale: Use typed start/end instants, zone, cohort, and threshold. Evaluate another form against the concrete expected result (one row per `source_event_id`) and the verification above.
- **Edge case:** Repeat with `NULL` in `source_event_id`, and `event_at` and state whether the row is kept, rejected, or classified.

## Edge cases

- Late events can rewrite sessions/funnels unless an as-of cutoff is recorded.
- Identity resolution across devices can change user grain.
- Calendar cohorts require an explicit business time zone.
- Attribution windows and models need versioning when definitions change.
