# SQL-ANALYTICS-01 — Reusable Analytical Query Patterns

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-30` and `sql-test-01`
- **Prerequisites:** [SQL Day 30 Phase 2 project](../../postgres-60day/companion-guides/day30_phase2_project.md),
  CTEs, window functions, conditional aggregation, intervals, and
  [SQL-TEST-01](sql_test_01_contracts_migrations.md).
- **Artifacts:** [learner SQL](../lessons/sql_analytics_01_query_patterns.sql) ·
  [solution reasoning](../solutions/sql_analytics_01_query_patterns_solutions.md) ·
  [executable solution](../solutions/sql_analytics_01_query_patterns_solutions.sql)

Run from the repository root:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_analytics_01_query_patterns.sql
```

Every timestamp is explicit and interpreted in UTC for business grouping. The
lab rolls back its fixture.

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-ANALYTICS-01 — Reusable Analytical Query Patterns** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-analytics-01/lesson/workspace/sql/professional/lessons/sql_analytics_01_query_patterns.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_analytics_01_query_patterns.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_analytics_01_query_patterns.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Grain, Canonical row, Session, Gap/island, Funnel, Attribution window. Its worked SQL reads or creates `pro_analytics_lab.users`, `pro_analytics_lab.events`, `pro_analytics_lab.daily_activity`, `pro_analytics_lab.campaign_touches`, `pro_analytics_lab.tier_history`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: The raw event grain is one ingestion attempt, so sourceeventid can repeat. The canonical view partitions by source ID and chooses latest ingestedat, then identity as a final tie-break. Deduplication happens before every downstream pattern to avoid double-counting retries.
The first runnable example has a concrete contract: Example 1 must print the expected DDL command tag for `pro_analytics_lab.users`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state. Its final projection is the columns written in the final `SELECT`. Verify the command tag in `pg_catalog`/`information_schema`, run one accepted value and one value the declared rule rejects, and confirm the lesson rollback removes the course-owned object. Where this query can emit `NULL`, identify the exact source expression and explain whether the output preserves, classifies, or rejects it.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/professional/lessons/sql_analytics_01_query_patterns.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TABLE pro_analytics_lab.users (
    user_id bigint PRIMARY KEY,
    signup_at timestamptz NOT NULL
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must print the expected DDL command tag for `pro_analytics_lab.users`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

### Example 2

```sql
CREATE TABLE pro_analytics_lab.events (
    ingestion_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_event_id text NOT NULL,
    user_id bigint NOT NULL REFERENCES pro_analytics_lab.users (user_id),
    event_name text NOT NULL,
    event_at timestamptz NOT NULL,
    ingested_at timestamptz NOT NULL
);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 2 must print the expected DDL command tag for `pro_analytics_lab.users`, and `pro_analytics_lab.events`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

## Learning objectives

- Implement deterministic deduplication, sessionization, and gaps-and-islands
  patterns.
- Build ordered funnels, bounded last-touch attribution, temporal as-of joins,
  and cohort retention.
- State grain, time-zone/boundary assumptions, tie breaks, denominators, and
  validation queries for each pattern.

## Vocabulary and concepts

- **Grain:** what one input/output row represents.
- **Canonical row:** deterministic winner selected from duplicate versions.
- **Session:** ordered events grouped by an inactivity threshold.
- **Gap/island:** break or consecutive run in ordered values.
- **Funnel:** ordered sequence of qualifying steps.
- **Attribution window:** bounded period in which a touch may receive credit.
- **As-of join:** match fact time to the version valid at that instant.
- **Half-open interval:** includes lower bound and excludes upper `[from,to)`.
- **Cohort:** entities sharing a start period.
- **Retention denominator:** original eligible cohort population, not merely
  users who later returned.

## Worked example / walkthrough

The raw event grain is one ingestion attempt, so `source_event_id` can repeat.
The canonical view partitions by source ID and chooses latest `ingested_at`,
then identity as a final tie-break. Deduplication happens before every downstream
pattern to avoid double-counting retries.

Sessionization orders each user's canonical events, compares with `LAG`, marks a
new session after more than 30 minutes, and cumulatively sums markers. `ROWS`
makes the window frame explicit. The output grain is one user-session.

Gaps and islands subtracts row number from each unique activity date. Consecutive
dates share the same derived key. Duplicate dates must be removed first or they
distort row numbers.

The funnel computes each step only at or after the prior step. Independently
taking each event type's minimum can count out-of-order behavior as conversion.
Output counts retain all signed-up users through LEFT joins.

Attribution starts from each purchase and uses a LEFT LATERAL query for the
latest touch no later than purchase and no earlier than seven days before.
Touch identity breaks timestamp ties. LEFT preserves unattributed purchases.
This is one declared model, not causal proof.

The as-of join uses `valid_from <= event_at` and
`event_at < valid_to`, with NULL as open-ended. A fact exactly at `valid_to`
belongs to the successor row. Production history needs a constraint or test
preventing overlaps; `LIMIT 1` must not hide invalid overlapping versions.

Cohort retention derives UTC signup month, distinct active months, cohort size,
and retained users before division. The denominator remains the starting cohort
size. Month arithmetic is calendar-based, not a fixed number of days.

## Exercises

Complete all fourteen prompts and add fail-fast checks from SQL-TEST-01. For every
query, write input grain, output grain, duplicate rule, time zone, interval
bounds, NULL behavior, and deterministic order before editing SQL.

Treat attribution and retention as definitions that stakeholders must approve,
not universal mathematical truths.

For every answer, state input grain, output grain, duplicate policy, NULL
policy, time zone, half-open bounds, tie-break, and an invariant query:

1. **Deduplication:** prove one canonical row per source event and justify the
   winner order.
   **Inputs/evidence:** For sql-analytics-01 Exercise 1, complete the deduplication written analysis and support its claims with read-only evidence from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-analytics-01 Exercise 1, expected output: a completed the deduplication written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `source_event_id`, `ingested_at`, and `ingestion_id`.
   **Verify:** For sql-analytics-01 Exercise 1, check the deduplication written analysis against `source_event_id`, `ingested_at`, and `ingestion_id`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
2. **Sessions:** use a 60-minute rule, calculate duration, and test the exact
   threshold.
   **Inputs/evidence:** For sql-analytics-01 Exercise 2, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `user_id`, `session_number`, `started_at`, `ended_at`, `duration`, and `events`; keep `user_id`, and `session_number` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-analytics-01 Exercise 2, expected output: one row per `user_id`, and `session_number`. The final columns are `user_id`, `session_number`, `started_at`, `ended_at`, `duration`, and `events`. The final order is `user_id, session_number`.
   **Verify:** For sql-analytics-01 Exercise 2, independently aggregate `pro_analytics_lab.deduplicated_events` by `user_id`, and `session_number`; require one output row for every distinct `user_id`, and `session_number` tuple and compare `duration`, and `events` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `duration`, and `events` for the existing `user_id`, and `session_number` tuple and verify the new tuple appears exactly once.
3. **Funnel:** produce one ordered row per user and reject step regressions.
   **Inputs/evidence:** For sql-analytics-01 Exercise 3, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at`; keep `user_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-analytics-01 Exercise 3, expected output: one row per `user_id`. The final columns are `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at`. The final order is `c.user_id`.
   **Verify:** For sql-analytics-01 Exercise 3, reselect the returned keys directly from the source; require unique `user_id` where the expected grain is one row per key and confirm the projected `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at` against `pro_analytics_lab.deduplicated_events`. Add one source row with a new `user_id`; verify the result gains exactly one row carrying that `user_id` value.
4. **Islands:** retain islands with at least two active days and verify gaps.
   **Inputs/evidence:** For sql-analytics-01 Exercise 4, read from `pro_analytics_lab.deduplicated_events`. Compute `user_id`, `island_start`, `island_end`, and `active_days` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-analytics-01 Exercise 4, expected output: one row per user-date. The final columns are `user_id`, `island_start`, `island_end`, and `active_days`. The final order is `n.user_id, island_start`.
   **Verify:** For sql-analytics-01 Exercise 4, evaluate each of `island_start`, `island_end`, and `active_days` in a separate control `SELECT` over `pro_analytics_lab.deduplicated_events`; require one final row and compare every value. Add one row to an existing group and one row for a new group; recompute `island_start`, `island_end`, and `active_days` for the existing `user_id`, and `island_key` tuple and verify the new tuple appears exactly once.
5. **Attribution:** test missing touches and timestamp ties with a deterministic
   winner.
   **Inputs/evidence:** For sql-analytics-01 Exercise 5, read from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Build the answer toward `touched_at`, and `touch_id`; keep `touch_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-analytics-01 Exercise 5, expected output: one row per `touch_id`. The final columns are `touched_at`, and `touch_id`.
   **Verify:** For sql-analytics-01 Exercise 5, reselect the returned keys directly from the source; require unique `touch_id` where the expected grain is one row per key and confirm the projected `touched_at`, and `touch_id` against `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Add two tied candidates and prove `touch_id` identifies both without accidental loss.
6. **Retention:** independently verify cohort size, retained numerator, and
   division.
   **Inputs/evidence:** For sql-analytics-01 Exercise 6, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `cohort_month`, `cohort_users`, and `month_1_users`; keep `cohort_month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-analytics-01 Exercise 6, expected output: one row per `cohort_month`. The final columns are `cohort_month`, `cohort_users`, and `month_1_users`. The final order is `c.cohort_month`.
   **Verify:** For sql-analytics-01 Exercise 6, independently aggregate `pro_analytics_lab.deduplicated_events` by `cohort_month`; require one output row for every distinct `cohort_month` tuple and compare `cohort_users`, and `month_1_users` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `cohort_users`, and `month_1_users` for the existing `cohort_month` tuple and verify the new tuple appears exactly once.
7. **As-of join:** test an event at an upper boundary and require one successor.
   **Inputs/evidence:** For sql-analytics-01 Exercise 7, read from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Build the answer toward `valid_from`, `event_at`, and `valid_to`; keep `valid_from` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-analytics-01 Exercise 7, expected output: one row per `valid_from`. The final columns are `valid_from`, `event_at`, and `valid_to`.
   **Verify:** For sql-analytics-01 Exercise 7, reselect the returned keys directly from the source; require unique `valid_from` where the expected grain is one row per key and confirm the projected `valid_from`, `event_at`, and `valid_to` against `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
8. **Trailing window:** use a dense date spine and compare `ROWS` with `RANGE`.
   **Inputs/evidence:** For sql-analytics-01 Exercise 8, read from `pro_analytics_lab.deduplicated_events`. Compute `report_date`, and `trailing_7d_active_users` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-analytics-01 Exercise 8, expected output: one row per calendar date in the requested business zone and LEFT JOIN deduplicated activity by local date. The final columns are `report_date`, and `trailing_7d_active_users`. The final order is `s.report_date`.
   **Verify:** For sql-analytics-01 Exercise 8, evaluate each of `report_date`, and `trailing_7d_active_users` in a separate control `SELECT` over `pro_analytics_lab.deduplicated_events`; require one final row and compare every value. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
9. **Percentiles:** calculate median/P90 session duration and document
   interpolation and NULL behavior.
   **Inputs/evidence:** For sql-analytics-01 Exercise 9, use `pro_analytics_lab.deduplicated_events` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-analytics-01 Exercise 9, expected output: one row per session with duration. The final columns are `session_count`, and `median_and_p90`.
   **Verify:** For sql-analytics-01 Exercise 9, restore into an isolated target and reconcile `pro_analytics_lab.deduplicated_events` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
10. **Top-N:** compare `row_number`, `rank`, and `dense_rank` under ties.
   **Inputs/evidence:** For sql-analytics-01 Exercise 10, read from `pro_analytics_lab.deduplicated_events`. Compute `user_id`, and `event_name` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-analytics-01 Exercise 10, expected output: one row per `(user_id,event_name)`, then calculate all three functions ordered by count descending. The final columns are `user_id`, and `event_name`. The final order is `c.user_id, row_number_position`.
   **Verify:** For sql-analytics-01 Exercise 10, evaluate each of `event_name` in a separate control `SELECT` over `pro_analytics_lab.deduplicated_events`; require one final row and compare every value. Give two rows the same `c.user_id` value and different `row_number_position` values; verify `c.user_id, row_number_position` produces the intended rank and display order.
11. **Hierarchy:** traverse recursively with depth, path, and cycle protection.
   **Inputs/evidence:** For sql-analytics-01 Exercise 11, read from `pro_analytics_lab.campaign_nodes`, and `tree`. Compute `campaign_id`, `parent_campaign_id`, `depth`, and `path` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-analytics-01 Exercise 11, expected output: one row per node in a multi-parent graph. The final columns are `campaign_id`, `parent_campaign_id`, `depth`, and `path`. The final order is `path`.
   **Verify:** For sql-analytics-01 Exercise 11, evaluate each of `parent_campaign_id`, `depth`, and `path` in a separate control `SELECT` over `pro_analytics_lab.campaign_nodes`, and `tree`; require one final row and compare every value. Add one source row with a new `campaign_id`; verify the result gains exactly one row carrying that `campaign_id` value.
12. **Zero-activity funnel:** retain empty dates and make denominators explicit.
   **Inputs/evidence:** For sql-analytics-01 Exercise 12, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `report_date`, `signups`, and `purchasers`; keep `report_date` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-analytics-01 Exercise 12, expected output: one row per `report_date`. The final columns are `report_date`, `signups`, and `purchasers`. The final order is `s.report_date`.
   **Verify:** For sql-analytics-01 Exercise 12, independently aggregate `pro_analytics_lab.deduplicated_events` by `report_date`; require one output row for every distinct `report_date` tuple and compare `signups`, and `purchasers` tuple by tuple. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
13. **Approximation:** specify error, scale, merge, refresh, and exact-check
    requirements before proposing approximate distinct counts.
   **Inputs/evidence:** For sql-analytics-01 Exercise 13, read the target keys from `pro_analytics_lab.deduplicated_events` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-analytics-01 Exercise 13, expected output: the command tag and an independently counted set of affected `exact_distinct_users` values. The final columns are `exact_distinct_users`.
   **Verify:** For sql-analytics-01 Exercise 13, materialize the intended `exact_distinct_users` target set first; require the command tag/`RETURNING` set to match it, then query `pro_analytics_lab.deduplicated_events` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `exact_distinct_users` values in both cases.
14. **Reusable query:** validate parameters and add grain, duplicate, NULL,
    ordering, and time-boundary contracts.
   **Inputs/evidence:** For sql-analytics-01 Exercise 14, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `source_event_id`, and `event_at`; keep `source_event_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-analytics-01 Exercise 14, expected output: one row per `source_event_id`. The final columns are `source_event_id`, and `event_at`. The final order is `de.event_at, de.source_event_id`.
   **Verify:** For sql-analytics-01 Exercise 14, project `source_event_id` plus the raw source columns from `pro_analytics_lab.deduplicated_events` at each join stage; record row count and distinct `source_event_id`, then assert the final `source_event_id`, and `event_at` values match those staged rows without unintended fanout or loss. Repeat with `NULL` in `source_event_id`, and `event_at` and state whether the row is kept, rejected, or classified.

## Self-check

- Does deduplication produce exactly one deterministic row per source event?
- Is the session threshold boundary (`>` versus `>=`) explicit?
- Do islands start from unique ordered dates?
- Can no user reach a funnel step before its predecessor?
- Are unattributed purchases preserved?
- Can an as-of fact match at most one history row?
- Are cohort numerator and denominator independently inspectable?
- Do every final sort and tie-break produce deterministic output?

## Common pitfalls

- Window functions over raw retries silently duplicate sessions and funnels.
- Default window frames can change running calculations when timestamps tie.
- Inner joins discard non-converters and unattributed facts.
- `LIMIT 1` can conceal overlapping temporal history.
- Local-time month boundaries differ from UTC; choose the business zone.
- Funnel minima without step dependency count out-of-order events.
- Last-touch attribution is a convention, not causal impact.
- Retention rates using active users as denominator are not cohort retention.
- Integer division truncates unless one side is numeric.

## Next step

Continue to [SQL-OPS-02 — backup, restore, and recovery rehearsals](sql_ops_02_backup_restore_recovery.md).
Use the contract-test module to freeze each analytical definition and add
edge-case fixtures before turning a pattern into a metric.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-analytics-01 — Reusable Analytical Query Patterns.

I have completed the direct catalog prerequisites: `sql-30`, `sql-test-01`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_analytics_01_query_patterns.md
- Answer-free learner SQL: sql/professional/lessons/sql_analytics_01_query_patterns.sql

Key terms to teach in context: Grain, Canonical row, Session, Gap/island, Funnel, Attribution window. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The raw event grain is one ingestion attempt, so sourceeventid can repeat. The canonical view partitions by source ID and chooses latest ingestedat, then identity as a final tie-break. Deduplication happens before every downstream pattern to avoid double-counting retries.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-analytics-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
