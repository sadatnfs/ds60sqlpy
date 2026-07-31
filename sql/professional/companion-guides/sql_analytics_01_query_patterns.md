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
   **Inputs/evidence:** For sql-analytics-01 Exercise 1, compare raw `pro_analytics_lab.events` with `deduplicated_events`, choosing one canonical row per `source_event_id` by `ingested_at DESC, ingestion_id DESC` before any downstream analysis.
   **Expected result/shape:** For sql-analytics-01 Exercise 1, expected output: one row per source event with `source_event_id`, `canonical_rows`, `winner_ingested_at`, and `winner_ingestion_id`, ordered by source ID; every canonical count is 1, and the conflicting-payload diagnostic is empty.
   **Verify:** For sql-analytics-01 Exercise 1, independently rank raw deliveries, test an equal-timestamp tie, require the greater ingestion ID to win, and separately flag one source ID whose retries disagree on business payload.
2. **Sessions:** use a 60-minute rule, calculate duration, and test the exact
   threshold.
   **Inputs/evidence:** For sql-analytics-01 Exercise 2, order canonical events by `event_at, source_event_id` per user, mark a new session only when the previous gap exceeds 60 minutes, cumulatively number sessions, then aggregate.
   **Expected result/shape:** For sql-analytics-01 Exercise 2, expected output: one row per `(user_id, session_number)` with `started_at`, `ended_at`, `duration`, and `events`, ordered by user and session; a one-event session has zero duration.
   **Verify:** For sql-analytics-01 Exercise 2, prove an exact 60-minute gap stays in the session while 60 minutes and one second starts another, and reconcile the sum of session event counts with the canonical event count.
3. **Funnel:** produce one ordered row per user and reject step regressions.
   **Inputs/evidence:** For sql-analytics-01 Exercise 3, anchor each user at the earliest canonical signup and select the first view, add-to-cart, and purchase at or after the already-chosen predecessor timestamp.
   **Expected result/shape:** For sql-analytics-01 Exercise 3, expected output: one row per signed-up user with `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at`, ordered by user; an absent predecessor leaves all later steps NULL.
   **Verify:** For sql-analytics-01 Exercise 3, assert every non-NULL timestamp chain is nondecreasing, prove a view-only user is excluded, and prove a signup-only user remains once with NULL later timestamps.
4. **Islands:** retain islands with at least two active days and verify gaps.
   **Inputs/evidence:** For sql-analytics-01 Exercise 4, reduce canonical events to distinct `(user_id, activity_date)` rows, subtract row number from each date to form an island key, and group by user plus island.
   **Expected result/shape:** For sql-analytics-01 Exercise 4, expected output: one row per consecutive-day island lasting at least two days, with `user_id`, `island_start`, `island_end`, and `active_days`, ordered by user and start date.
   **Verify:** For sql-analytics-01 Exercise 4, test a two-day run, a one-day run, a gap, and duplicate same-day events; require only qualifying consecutive runs and prove duplicates do not inflate active-day counts.
5. **Attribution:** test missing touches and timestamp ties with a deterministic
   winner.
   **Inputs/evidence:** For sql-analytics-01 Exercise 5, start from each canonical purchase in `pro_analytics_lab.deduplicated_events` and use a LEFT LATERAL lookup in `pro_analytics_lab.campaign_touches` for at most one touch in the preceding seven days, ordered by `touched_at DESC, touch_id DESC`.
   **Expected result/shape:** For sql-analytics-01 Exercise 5, expected output: one row per purchase with `source_event_id`, `user_id`, `purchased_at`, `touch_id`, `campaign`, and `touched_at`, ordered by source ID; unmatched purchases retain NULL attribution and the greater touch ID wins an equal-time tie.
   **Verify:** For sql-analytics-01 Exercise 5, reconcile output count and unique source IDs with all purchases, test one unattributed purchase, and remove the ID tie-breaker in a disposable copy to expose nondeterministic attribution.
6. **Retention:** independently verify cohort size, retained numerator, and
   division.
   **Inputs/evidence:** For sql-analytics-01 Exercise 6, define cohort month from each user's earliest canonical event, reduce activity to distinct user/month rows, and LEFT JOIN activity so nonretained cohort members remain in the denominator.
   **Expected result/shape:** For sql-analytics-01 Exercise 6, expected output: one row per `cohort_month` with `cohort_users`, `month_1_users`, and four-decimal `month_1_rate`, ordered by cohort; zero denominators are protected with `NULLIF`.
   **Verify:** For sql-analytics-01 Exercise 6, independently list cohort and month-one member IDs, compare both distinct counts, and add one nonretained member to prove only the denominator and rate change.
7. **As-of join:** test an event at an upper boundary and require one successor.
   **Inputs/evidence:** For sql-analytics-01 Exercise 7, join `pro_analytics_lab.event_probes` to adjacent half-open rows in `pro_analytics_lab.user_tiers` using `valid_from <= event_at` and `event_at < COALESCE(valid_to, infinity)`, retaining probe grain.
   **Expected result/shape:** For sql-analytics-01 Exercise 7, expected output: one row per probe with `probe_id`, `event_at`, `tier_name`, validity bounds, and `matching_tiers`, ordered by probe; the shared-boundary probe matches the successor exactly once.
   **Verify:** For sql-analytics-01 Exercise 7, require no probe to match more than one tier, test just before/at/after the shared boundary, and inject an overlap to prove the assertion fails instead of hiding ambiguity with a row limit.
8. **Trailing window:** use a dense date spine and compare `ROWS` with `RANGE`.
   **Inputs/evidence:** For sql-analytics-01 Exercise 8, generate every UTC report date from 2026-01-01 through 2026-01-08 and count distinct users in the inclusive seven-calendar-day window ending on each date.
   **Expected result/shape:** For sql-analytics-01 Exercise 8, expected output: exactly eight ordered rows with `report_date` and `trailing_7d_active_users`; dates without events remain because the dense date spine is the preserved side.
   **Verify:** For sql-analytics-01 Exercise 8, independently list distinct users for two half-open seven-day windows and add the same user on another day to prove weekly distinct count rises by at most one.
9. **Percentiles:** calculate median/P90 session duration and document
   interpolation and NULL behavior.
   **Inputs/evidence:** For sql-analytics-01 Exercise 9, derive one row per session with the 60-minute rule, then pass non-NULL session durations—not raw events—to ordered-set percentile aggregates.
   **Expected result/shape:** For sql-analytics-01 Exercise 9, expected output: one aggregate row with `session_count` and a two-element interval array `median_and_p90` from continuous percentiles 0.5 and 0.9.
   **Verify:** For sql-analytics-01 Exercise 9, materialize and sort session durations, reconcile the session count, compare continuous percentile, discrete percentile, and average on a skewed fixture, and confirm empty input yields NULL percentiles.
10. **Top-N:** compare `row_number`, `rank`, and `dense_rank` under ties.
   **Inputs/evidence:** For sql-analytics-01 Exercise 10, aggregate canonical events to `(user_id, event_name)` counts and calculate `row_number`, `rank`, and `dense_rank` side by side within each user.
   **Expected result/shape:** For sql-analytics-01 Exercise 10, expected output: one row per user/event type with `event_count` and all three rank positions, ordered by user and deterministic row-number position; only row number breaks count ties by event name.
   **Verify:** For sql-analytics-01 Exercise 10, create tied counts and prove `row_number <= 2` returns exactly two rows while tie-preserving rank filters can return more, then state the report's chosen meaning of top two.
11. **Hierarchy:** traverse recursively with depth, path, and cycle protection.
   **Inputs/evidence:** For sql-analytics-01 Exercise 11, traverse `pro_analytics_lab.campaign_nodes` from roots with a recursive CTE carrying depth and an integer-array path, refusing any child already present in that path.
   **Expected result/shape:** For sql-analytics-01 Exercise 11, expected output: one ordered hierarchy row per root-reachable node/path with `campaign_id`, `parent_campaign_id`, `depth`, and `path`, plus a diagnostic result listing unreachable IDs from the rootless cycle.
   **Verify:** For sql-analytics-01 Exercise 11, require no repeated ID in any returned path, prove recursion terminates, and reconcile reachable plus unreachable campaign IDs with every fixture ID.
12. **Zero-activity funnel:** retain empty dates and make denominators explicit.
   **Inputs/evidence:** For sql-analytics-01 Exercise 12, start from a four-day spine and LEFT JOIN canonical events with half-open UTC day bounds, applying signup and purchase conditions inside aggregate filters.
   **Expected result/shape:** For sql-analytics-01 Exercise 12, expected output: exactly four rows with `report_date`, `signups`, and `purchasers`, ordered by date; dates with no activity remain and show numeric zero.
   **Verify:** For sql-analytics-01 Exercise 12, compare each day with direct control queries and move an event condition to WHERE in a disposable copy to demonstrate why NULL-extended dates would disappear.
13. **Approximation:** specify error, scale, merge, refresh, and exact-check
    requirements before proposing approximate distinct counts.
   **Inputs/evidence:** For sql-analytics-01 Exercise 13, compute core PostgreSQL's exact distinct-user count from `pro_analytics_lab.deduplicated_events` and separately review an adoption matrix for any optional approximate sketch.
   **Expected result/shape:** For sql-analytics-01 Exercise 13, expected output: one scalar `exact_distinct_users` row plus an ordered review matrix with `criterion_number`, `criterion`, and `required_evidence`, covering implementation/version, error budget, mergeability, fallback, and ownership; no unavailable extension is presented as executed.
   **Verify:** For sql-analytics-01 Exercise 13, compare the scalar result with a distinct-user subquery and, for any approved sketch, measure relative error across representative cardinalities; unavailable capability or excess error must select the exact fallback.
14. **Reusable query:** validate parameters and add grain, duplicate, NULL,
    ordering, and time-boundary contracts.
   **Inputs/evidence:** For sql-analytics-01 Exercise 14, validate typed start/end instants before filtering canonical events with a half-open time window, rejecting NULL, equal, or reversed bounds as invalid parameters.
   **Expected result/shape:** For sql-analytics-01 Exercise 14, expected output: one row per canonical source event inside the valid interval with `source_event_id` and `event_at`, ordered by time and source ID; invalid bounds raise SQLSTATE `22023`.
   **Verify:** For sql-analytics-01 Exercise 14, test both endpoints, equal/reversed/NULL bounds, duplicate deliveries, timestamp ties, an empty valid interval, and a daylight-saving transition expressed as absolute instants.

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
