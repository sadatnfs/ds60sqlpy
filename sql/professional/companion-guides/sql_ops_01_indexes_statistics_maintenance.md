# SQL-OPS-01 — Index Types, Statistics, and Maintenance Lifecycle

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-35` and `sql-types-01`
- **Prerequisites:** SQL Days 31–34 on plans and B-tree indexes,
  [SQL Day 35 query pitfalls](../../postgres-60day/companion-guides/day35_avoiding_pitfalls.md),
  plus
  [SQL-TYPES-01](sql_types_01_native_types_search.md) for array/range operators.
- **Artifacts:** [learner SQL](../lessons/sql_ops_01_indexes_statistics_maintenance.sql) ·
  [solution reasoning](../solutions/sql_ops_01_indexes_statistics_maintenance_solutions.md) ·
  [executable solution](../solutions/sql_ops_01_indexes_statistics_maintenance_solutions.sql)

Run from the repository root:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_ops_01_indexes_statistics_maintenance.sql
```

The same command works in PowerShell and POSIX shells. The default lab rolls
back. It reads configuration/statistics but never changes host settings, runs
`VACUUM`, or enables `pg_stat_statements`.

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

2. Open **SQL-OPS-01 — Index Types, Statistics, and Maintenance Lifecycle** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-ops-01/lesson/workspace/sql/professional/lessons/sql_ops_01_indexes_statistics_maintenance.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_ops_01_indexes_statistics_maintenance.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_ops_01_indexes_statistics_maintenance.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Access method, Operator class, Partial index, Expression index, Covering index, BRIN range. Its worked SQL reads or creates `pro_ops_lab.events`, `pg_catalog.pg_index`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_am`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: The fixture inserts 6,000 events in timestamp order. That physical correlation makes time a plausible BRIN candidate in a much larger append-oriented table. The teaching table is intentionally small, so PostgreSQL may still prefer a sequential scan; that is a valid cost decision.
The first runnable example has a concrete contract: Example 1 must print the expected DDL command tag for `pro_ops_lab.events`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state. Its final projection is the columns written in the final `SELECT`. Verify the command tag in `pg_catalog`/`information_schema`, run one accepted value and one value the declared rule rejects, and confirm the lesson rollback removes the course-owned object. Where this query can emit `NULL`, identify the exact source expression and explain whether the output preserves, classifies, or rejects it.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/professional/lessons/sql_ops_01_indexes_statistics_maintenance.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TABLE pro_ops_lab.events (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    device_id text NOT NULL,
    occurred_at timestamptz NOT NULL,
    severity smallint NOT NULL CHECK (severity BETWEEN 1 AND 5),
    tags text[] NOT NULL DEFAULT ARRAY[]::text[],
    location point NOT NULL,
    message text NOT NULL
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must print the expected DDL command tag for `pro_ops_lab.events`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

### Example 2

```sql
INSERT INTO pro_ops_lab.events (
    device_id,
    occurred_at,
    severity,
    tags,
    location,
    message
)
SELECT
    'device-' || lpad(((g.n % 40) + 1)::text, 3, '0'),
    TIMESTAMPTZ '2026-01-01 00:00:00+00'
        + g.n * INTERVAL '1 minute',
    ((g.n % 5) + 1)::smallint,
    CASE
        WHEN g.n % 3 = 0 THEN ARRAY['network', 'retry']
        WHEN g.n % 3 = 1 THEN ARRAY['storage']
        ELSE ARRAY['application', 'latency']
    END,
    point((g.n % 100)::double precision, ((g.n * 7) % 100)::double precision),
    CASE
        WHEN g.n % 10 = 0 THEN 'Connection retry threshold reached'
        ELSE 'Routine device observation'
    END
FROM generate_series(1, 6000) AS g(n);
```

**How to read it:** Example 2 changes rows inside the lesson's declared transaction. The command tag reports affected rows, but a follow-up query must prove the intended before/after invariant.

**Expected result/shape:** Example 2 returns one row per `smallint`, and `END` with columns `smallint`, and `END` from `pro_ops_lab.events`, and `generate_series`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

## Learning objectives

- Match B-tree, GIN, GiST, SP-GiST, and BRIN operator classes to concrete query
  shapes.
- Build expression, partial, and covering indexes and create extended
  statistics.
- Review planner evidence without promising a universal plan and design an
  index/ANALYZE/VACUUM/autovacuum maintenance lifecycle.

## Vocabulary and concepts

- **Access method:** index structure such as B-tree, GIN, GiST, SP-GiST, or
  BRIN.
- **Operator class:** data-type/operator semantics implemented by an index.
- **Partial index:** index containing only rows satisfying a fixed predicate.
- **Expression index:** index over a computed immutable expression.
- **Covering index:** key columns plus `INCLUDE` payload that may permit an
  index-only scan when visibility allows.
- **BRIN range:** block-range summary rather than one entry per row.
- **Statistics target:** sampling/detail budget used for planner estimates.
- **Extended statistics:** cross-column dependencies, most-common values, or
  distinct-count evidence.
- **Dead tuple:** obsolete row version awaiting vacuum reuse.
- **Visibility map:** page-level evidence that can support index-only scans.
- **Bloat:** space/layout inefficiency requiring measured diagnosis, not a
  universal percentage threshold.

## Worked example / walkthrough

The fixture inserts 6,000 events in timestamp order. That physical correlation
makes time a plausible BRIN candidate in a much larger append-oriented table.
The teaching table is intentionally small, so PostgreSQL may still prefer a
sequential scan; that is a valid cost decision.

- B-tree serves device equality plus descending time order.
- BRIN summarizes time-correlated heap ranges compactly.
- GIN maps tag elements to rows for array containment.
- GiST supports point distance/nearest-neighbour operations.
- SP-GiST partitions text search space for its supported operators.
- An expression index stores `lower(message)`.
- A partial index stores only severity 4–5 rows.

A query must match the indexed expression and operator. `lower(message) = ...`
can use the expression index; plain `message = ...` is a different expression.
A partial-index query must logically imply `severity >= 4`; a parameterized
predicate whose value is unknown at planning time may not.

`CREATE STATISTICS ... (dependencies, mcv)` supplies correlation evidence after
`ANALYZE`. It improves estimates; it cannot force a join type or index. Compare
estimated versus observed rows with representative, safe `EXPLAIN (ANALYZE)`
only when executing the query is acceptable. Remember that `ANALYZE` after a
write actually performs the write query.

Index lifecycle review combines workload observation, query latency/plans,
constraint ownership, size, cache effects, maintenance/write cost, and a full
business cycle. A zero `idx_scan` after a restart or short window is not proof
that an index is disposable.

VACUUM reclaims dead-row space for reuse and maintains visibility/freeze state;
it does not usually shrink the file. ANALYZE refreshes planner statistics.
Autovacuum schedules both using per-table change thresholds. Changing its
configuration or running aggressive vacuum modes is DBA work outside this
transactional lab.

`pg_stat_statements` requires approved extension/preload configuration and its
query text may contain sensitive literals. The lesson checks only installation
status. A production review needs access control and normalized query IDs.

### DBA-only statement-statistics boundary

The following is an operator runbook fragment, not a learner command. A DBA
must first approve adding `pg_stat_statements` to
`shared_preload_libraries` and restarting the PostgreSQL service. Only then,
and only in the intended database, would an administrator run:

```sql
CREATE EXTENSION pg_stat_statements;

SELECT
    queryid,
    calls,
    total_exec_time,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

Grant monitoring access narrowly, prefer `queryid` for aggregation, and decide
whether query text is safe to expose. Removing the extension from one database
does not undo the server-wide preload setting; configuration rollback and
restart belong in the same approved change plan.

## Exercises

Complete all twelve prompts. Begin with a predicate-compatible covering index, access-method
operator mapping, extended statistics, a cautious lifecycle review, maintenance
semantics, and a safe statement-statistics plan; then address redundancy,
expressions, HOT, partitioning, plan instrumentation, and an owned scorecard.
Include the exact target query beside every proposed index.

Use `EXPLAIN` as evidence, not as a pass/fail assertion that one node type must
appear on every machine or data size.

Every recommendation needs target query, operator, representative data,
before/after evidence, write/storage cost, owner, review date, and rollback:

1. **Covering partial index:** make the query predicate imply the index
   predicate and identify which columns are keys versus payload.
   **Inputs/evidence:** For sql-ops-01 Exercise 1, change only `events_high_device_time_covering`, and `pro_ops_lab.events` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `information_schema.columns` rows.
   **Expected result/shape:** For sql-ops-01 Exercise 1, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `object_name`, `catalog_definition`, `accepted_case`, and `rejected_sqlstate`.
   **Verify:** For sql-ops-01 Exercise 1, inspect `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `information_schema.columns` for `events_high_device_time_covering`, and `pro_ops_lab.events`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
2. **Access methods:** map each GIN, GiST, SP-GiST, and BRIN index to supported
   operators and one nonmatching query.
   **Inputs/evidence:** For sql-ops-01 Exercise 2, read from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Build the answer toward `access_methods_answer`; keep `access_methods_answer` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-01 Exercise 2, expected output: one row per `access_methods_answer`. The final columns are `access_methods_answer`.
   **Verify:** For sql-ops-01 Exercise 2, reselect the returned keys directly from the source; require unique `access_methods_answer` where the expected grain is one row per key and confirm the projected `access_methods_answer` against `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Add one source row with a new `access_methods_answer`; verify the result gains exactly one row carrying that `access_methods_answer` value.
3. **Extended statistics:** choose correlated columns, analyze, inspect, and
   explain the planner’s freedom.
   **Inputs/evidence:** For sql-ops-01 Exercise 3, read from `pro_ops_lab.events`, `pg_catalog.pg_stats_ext`, and `events_category_severity_stats`. Build the answer toward `statistics_name`, `kinds`, and `attnames`; keep `statistics_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-01 Exercise 3, expected output: one row per `statistics_name`. The final columns are `statistics_name`, `kinds`, and `attnames`. The final order is `s.statistics_name`.
   **Verify:** For sql-ops-01 Exercise 3, run an anti-check that counts rows where NOT ((s.schemaname = 'pro_ops_lab')); require unique `statistics_name` where the expected grain is one row per key and confirm the projected `statistics_name`, `kinds`, and `attnames` against `pro_ops_lab.events`, `pg_catalog.pg_stats_ext`, and `events_category_severity_stats`. Add one row for which `(s.schemaname = 'pro_ops_lab')` is true and one for which it is false; verify only the matching `statistics_name` value is returned.
4. **Lifecycle review:** combine usage window, size, writes, constraints, and
   plans without producing an automatic drop list.
   **Inputs/evidence:** For sql-ops-01 Exercise 4, read from `pg_catalog.pg_index`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_stat_user_indexes`, and `pg_catalog.pg_indexes`. Build the answer toward `index_name`, `index_bytes`, `observed_scans`, `indisunique`, `indisprimary`, and `predicate`; keep `index_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-01 Exercise 4, expected output: one row per `index_name`. The final columns are `index_name`, `index_bytes`, `observed_scans`, `indisunique`, `indisprimary`, and `predicate`. The final order is `ci.relname`.
   **Verify:** For sql-ops-01 Exercise 4, project `index_name` plus the raw source columns from `pg_catalog.pg_index`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_stat_user_indexes`, and `pg_catalog.pg_indexes` at each join stage; record row count and distinct `index_name`, then assert the final `index_name`, `index_bytes`, `observed_scans`, `indisunique`, `indisprimary`, and `predicate` values match those staged rows without unintended fanout or loss. Insert rows immediately before, exactly at, and immediately after `severity >= 4`; identify which rows pass each inclusive or exclusive comparison.
5. **Maintenance:** connect vacuum/analyze, visibility, dead tuples, bloat,
   autovacuum, and long transactions.
   **Inputs/evidence:** For sql-ops-01 Exercise 5, read from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Build the answer toward `maintenance_answer`; keep `maintenance_answer` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-01 Exercise 5, expected output: one row per `maintenance_answer`. The final columns are `maintenance_answer`.
   **Verify:** For sql-ops-01 Exercise 5, reselect the returned keys directly from the source; require unique `maintenance_answer` where the expected grain is one row per key and confirm the projected `maintenance_answer` against `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Add one source row with a new `maintenance_answer`; verify the result gains exactly one row carrying that `maintenance_answer` value.
6. **Statement statistics:** design restricted, privacy-aware collection and
   review without enabling or exposing it here.
   **Inputs/evidence:** For sql-ops-01 Exercise 6, complete the statement statistics written analysis and support its claims with read-only evidence from `pg_stat_statements`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-ops-01 Exercise 6, expected output: a completed the statement statistics written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `queryid`, and `shared_preload_libraries`.
   **Verify:** For sql-ops-01 Exercise 6, check the statement statistics written analysis against `queryid`, and `shared_preload_libraries`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
7. **Redundancy candidates:** compare keys, order, predicate, operator class,
   collation, INCLUDE data, uniqueness, and plans.
   **Inputs/evidence:** For sql-ops-01 Exercise 7, read from `pg_catalog.pg_index`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`. Build the answer toward `index_name`, `indisunique`, `indisprimary`, `index_definition`, and `predicate`; keep `index_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-01 Exercise 7, expected output: one row per `index_name`. The final columns are `index_name`, `indisunique`, `indisprimary`, `index_definition`, and `predicate`. The final order is `ci.relname`.
   **Verify:** For sql-ops-01 Exercise 7, project `index_name` plus the raw source columns from `pg_catalog.pg_index`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` at each join stage; record row count and distinct `index_name`, then assert the final `index_name`, `indisunique`, `indisprimary`, `index_definition`, and `predicate` values match those staged rows without unintended fanout or loss. Add duplicate source candidates for `index_name`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
8. **Expression index:** test expression matching and document collation,
   function-volatility, and generated-column alternatives.
   **Inputs/evidence:** For sql-ops-01 Exercise 8, run the underlying read-only query over `pro_ops_lab.events`, and `events_device_lower_idx` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-ops-01 Exercise 8, expected output: one row per `event_id`. The final columns are `event_id`, and `device_id`. The final order is `e.event_id`.
   **Verify:** For sql-ops-01 Exercise 8, run the underlying query without `EXPLAIN` and preserve its `event_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
9. **HOT updates:** observe a controlled workload and relate indexed columns,
   free space, fillfactor, vacuum, and old snapshots.
   **Inputs/evidence:** For sql-ops-01 Exercise 9, read from `pro_ops_lab.events`, and `pg_catalog.pg_stat_user_tables`. Build the answer toward `relname`, `n_tup_upd`, `n_tup_hot_upd`, `n_dead_tup`, `last_autovacuum`, and `last_autoanalyze`; keep `relname` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-01 Exercise 9, expected output: one row per `relname`. The final columns are `relname`, `n_tup_upd`, `n_tup_hot_upd`, `n_dead_tup`, `last_autovacuum`, and `last_autoanalyze`.
   **Verify:** For sql-ops-01 Exercise 9, run an anti-check that counts rows where NOT ((e.event_id <= 100) OR (s.schemaname = 'pro_ops_lab' AND s.relname = 'events')); require unique `relname` where the expected grain is one row per key and confirm the projected `relname`, `n_tup_upd`, `n_tup_hot_upd`, `n_dead_tup`, `last_autovacuum`, and `last_autoanalyze` against `pro_ops_lab.events`, and `pg_catalog.pg_stat_user_tables`. Insert rows immediately before, exactly at, and immediately after `e.event_id <= 100`; identify which rows pass each inclusive or exclusive comparison.
10. **Partition indexes:** account for pruning, local indexes, statistics,
    attach/detach, and global uniqueness limitations.
   **Inputs/evidence:** For sql-ops-01 Exercise 10, read from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Build the answer toward `partition_indexes_answer`; keep `partition_indexes_answer` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-01 Exercise 10, expected output: one row per `partition_indexes_answer`. The final columns are `partition_indexes_answer`.
   **Verify:** For sql-ops-01 Exercise 10, reselect the returned keys directly from the source; require unique `partition_indexes_answer` where the expected grain is one row per key and confirm the projected `partition_indexes_answer` against `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Add duplicate source candidates for `partition_indexes_answer`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
11. **Plan instrumentation:** distinguish execution and overhead across
    `EXPLAIN` options, especially for writes and cache state.
   **Inputs/evidence:** For sql-ops-01 Exercise 11, run the underlying read-only query over `pro_ops_lab.events` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-ops-01 Exercise 11, expected output: one row per `explain`. The final columns are `explain`.
   **Verify:** For sql-ops-01 Exercise 11, run the underlying query without `EXPLAIN` and preserve its `explain` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
12. **Maintenance scorecard:** define owners, budgets, cadence, escalation, and
    evidence for growth, health, waits, lag, and slow queries.
   **Inputs/evidence:** For sql-ops-01 Exercise 12, read from the inline `VALUES` fixture. Build the answer toward `signal`, `evidence_source`, and `owner`; keep `signal` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-01 Exercise 12, expected output: one row per `signal`. The final columns are `signal`, `evidence_source`, and `owner`. The final order is `signal`.
   **Verify:** For sql-ops-01 Exercise 12, reselect the returned keys directly from the source; require unique `signal` where the expected grain is one row per key and confirm the projected `signal`, `evidence_source`, and `owner` against the inline `VALUES` fixture. Add one source row with a new `signal`; verify the result gains exactly one row carrying that `signal` value.

## Self-check

- Does each index name a concrete query and compatible operator?
- Is a partial predicate implied by its target query?
- Are expression/query forms identical where required?
- Did `ANALYZE` populate the intended extended statistics?
- Can you explain why a sequential scan may beat an available index?
- Does an unused-index review cover restart timing and a representative cycle?
- Are VACUUM, configuration, extension, and destructive actions left outside
  the rollback-based learner path?

## Common pitfalls

- Adding every plausible index increases writes, WAL, cache pressure, vacuum
  work, backups, and restore time.
- BRIN is not automatically useful on a small or physically uncorrelated table.
- GIN/GiST/SP-GiST are families; the operator class is the real compatibility
  contract.
- Included columns are payload, not search keys.
- Index-only scans still depend on page visibility.
- `REINDEX`, `VACUUM FULL`, and `CLUSTER` have lock/disk implications and are
  not routine first responses.
- Planner settings forced in a demo are not production tuning evidence.
- Query text from monitoring views can disclose confidential literals.

## Next step

Continue to [SQL-TEST-01 — SQL tests, migration checks, and data contracts](sql_test_01_contracts_migrations.md).
Then use [SQL-OPS-02](sql_ops_02_backup_restore_recovery.md) to include index,
statistics, extension, and post-restore verification in a recovery rehearsal.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-ops-01 — Index Types, Statistics, and Maintenance Lifecycle.

I have completed the direct catalog prerequisites: `sql-35`, `sql-types-01`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_ops_01_indexes_statistics_maintenance.md
- Answer-free learner SQL: sql/professional/lessons/sql_ops_01_indexes_statistics_maintenance.sql

Key terms to teach in context: Access method, Operator class, Partial index, Expression index, Covering index, BRIN range. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The fixture inserts 6,000 events in timestamp order. That physical correlation makes time a plausible BRIN candidate in a much larger append-oriented table. The teaching table is intentionally small, so PostgreSQL may still prefer a sequential scan; that is a valid cost decision.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-ops-01/ working copy. Never point setup, reset, DDL, or DML
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
