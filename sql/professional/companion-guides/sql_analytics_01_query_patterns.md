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
2. **Sessions:** use a 60-minute rule, calculate duration, and test the exact
   threshold.
3. **Funnel:** produce one ordered row per user and reject step regressions.
4. **Islands:** retain islands with at least two active days and verify gaps.
5. **Attribution:** test missing touches and timestamp ties with a deterministic
   winner.
6. **Retention:** independently verify cohort size, retained numerator, and
   division.
7. **As-of join:** test an event at an upper boundary and require one successor.
8. **Trailing window:** use a dense date spine and compare `ROWS` with `RANGE`.
9. **Percentiles:** calculate median/P90 session duration and document
   interpolation and NULL behavior.
10. **Top-N:** compare `row_number`, `rank`, and `dense_rank` under ties.
11. **Hierarchy:** traverse recursively with depth, path, and cycle protection.
12. **Zero-activity funnel:** retain empty dates and make denominators explicit.
13. **Approximation:** specify error, scale, merge, refresh, and exact-check
    requirements before proposing approximate distinct counts.
14. **Reusable query:** validate parameters and add grain, duplicate, NULL,
    ordering, and time-boundary contracts.

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
