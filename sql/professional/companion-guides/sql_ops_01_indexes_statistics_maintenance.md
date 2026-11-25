# SQL-OPS-01 - Index Types, Statistics, and Maintenance Lifecycle

## How to run this lesson

Start **sql-ops-01** from `./classroom` using the shared [run steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Choose **Whole SQL lesson (psql)**. The script opens one transaction on
`advanced_sql_training`, loads 6,000 events into `pro_ops_lab`, builds seven
teaching indexes and one extended statistics object, runs `ANALYZE`, prints
four `EXPLAIN (COSTS OFF)` plans and several statistics views, and ends with
`ROLLBACK`. It never runs `VACUUM`, changes a server setting or enables
`pg_stat_statements`. The final `DO` check requires 6,000 rows and at least
eight indexes on `events`. Your plans may differ from a classmate's; that is
expected. Save attempts in
`.learning/sql/sql-ops-01/lesson/workspace/sql/professional/lessons/sql_ops_01_indexes_statistics_maintenance.sql`.

The optional notebook route starts with `uv run --no-sync python scripts/course.py sql notebook sql-ops-01`; see the [study guide](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-35` and `sql-types-01`
- **Prerequisites:** SQL Days 31-34 on plans and B-tree indexes,
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

The same command works on Linux, macOS, and Windows through WSL 2. The
default lab rolls back. It reads configuration/statistics but never changes
host settings, runs `VACUUM`, or enables `pg_stat_statements`.

## A beginner's mental model for this lesson

This lesson is about the physical side of a query: an index changes how
PostgreSQL finds rows, never which rows a correct query returns. The vocabulary
below (access method, operator class, partial, expression and covering index,
BRIN range) names the choices you make when one index should serve one operator
in one workload.

Two kinds of output appear here. The catalog queries return one row per index
or statistics object, which you can count against the DDL: a primary key plus
seven teaching indexes. The `EXPLAIN` blocks are not rows of data at all; they
are the plan PostgreSQL chose for this table size and these statistics, so read
them as evidence about this run.

The walkthrough fixture inserts 6,000 events one minute apart, so physical row
order follows `occurred_at`. That correlation is what makes the BRIN index with
`pages_per_range = 8` a plausible choice in a much larger append-only table.
The teaching table is small, so PostgreSQL may still pick a sequential scan for
the one-day count, and that is a valid cost decision, not a broken index.

## Two worked SQL examples

Example 1 defines the event table and Example 2 generates its 6,000 rows; the
indexes follow them.

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

**How to read it:** Each column feeds a different index type: `device_id` and
`occurred_at` feed the covering B-tree, `occurred_at` alone feeds BRIN, the
`tags` array feeds GIN, `location` (a `point`) feeds GiST, and `message` feeds
an expression index on `lower(message)`.

**Expected result/shape:** `CREATE TABLE`. The seven `CREATE INDEX` statements
and the `CREATE STATISTICS` on `(device_id, severity)` follow, then `ANALYZE`
so the planner has fresh statistics.

### Example 2

```sql
INSERT INTO pro_ops_lab.events (device_id, occurred_at, severity, tags, location, message)
SELECT
  'device-' || lpad(((g.n % 40) + 1)::text, 3, '0'),
  TIMESTAMPTZ '2026-01-01 00:00:00+00' + g.n * INTERVAL '1 minute',
  ((g.n % 5) + 1)::smallint,
  CASE WHEN g.n % 3 = 0 THEN
    ARRAY['network', 'retry']
  WHEN g.n % 3 = 1 THEN
    ARRAY['storage']
  ELSE
    ARRAY['application', 'latency']
  END,
  point((g.n % 100)::double precision, ((g.n * 7) % 100)::double precision),
  CASE WHEN g.n % 10 = 0 THEN
    'Connection retry threshold reached'
  ELSE
    'Routine device observation'
  END
FROM
  generate_series(1, 6000) AS g (n);
```

**How to read it:** `generate_series(1, 6000)` drives every column from `n`.
Devices cycle through 40 values and severity through 5, so each device always
has the same severity, which is the correlation the extended statistics
capture. Every tenth message is the retry warning.

**Expected result/shape:** `INSERT 0 6000`. With 40 devices, `device-007` has
150 events, and one fifth of all rows have severity 5. The partial index
`events_high_severity_partial` covers only the severity 4 and 5 rows.

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
- A partial index stores only severity 4-5 rows.

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
A limited role may not see `shared_preload_libraries` in `pg_settings`.
The executable solution reports `preload_visibility_unavailable` when that
configuration evidence is hidden; a missing visible setting does not prove
that preload is absent. It never grants global setting-reading privileges.

### DBA-only statement-statistics boundary

The following is an operator runbook fragment, not a learner command. A DBA
must first approve adding `pg_stat_statements` to
`shared_preload_libraries` and restarting the PostgreSQL service. Only then,
and only in the intended database, would an administrator run:

```sql external
CREATE EXTENSION pg_stat_statements;

SELECT
  queryid,
  calls,
  total_exec_time,
  rows
FROM
  pg_stat_statements
ORDER BY
  total_exec_time DESC
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
   **Inputs/evidence:** For sql-ops-01 Exercise 1, match the query's equality/range/order/projection with a partial covering btree on `(device_id, occurred_at DESC)` including severity/message and predicated on `severity >= 4`.
   **Expected result/shape:** For sql-ops-01 Exercise 1, expected output: catalog command evidence, one EXPLAIN plan, and up to 25 underlying rows with `occurred_at`, `severity`, and `message` for device-005 in descending time order.
   **Verify:** For sql-ops-01 Exercise 1, assert every result satisfies the partial predicate, compare returned rows with the same SELECT without planner settings, inspect the exact index predicate/include columns, and treat scan type as observed evidence - not a guaranteed contract.
2. **Access methods:** map each GIN, GiST, SP-GiST, and BRIN index to supported
   operators and one nonmatching query.
   **Inputs/evidence:** For sql-ops-01 Exercise 2, map GIN, GiST, SP-GiST, and BRIN to concrete type/operator workloads and state one important trade-off for each.
   **Expected result/shape:** For sql-ops-01 Exercise 2, expected output: four ordered rows with `method`, `suitable_types`, `target_operators`, and `tradeoff`.
   **Verify:** For sql-ops-01 Exercise 2, identify the exact operator class available for the target type, test representative data distribution/write cost, and reject any recommendation that names only an access method without its query operator.
3. **Extended statistics:** choose correlated columns, analyze, inspect, and
   explain the planner’s freedom.
   **Inputs/evidence:** For sql-ops-01 Exercise 3, create dependency and MCV extended statistics on the correlated `category`/`severity` pair, ANALYZE, then inspect `pg_stats_ext`.
   **Expected result/shape:** For sql-ops-01 Exercise 3, expected output: exactly one statistics row with its name, kinds, and attribute names.
   **Verify:** For sql-ops-01 Exercise 3, compare EXPLAIN estimated rows before/after ANALYZE for a correlated predicate, retain actual counts as control, and do not claim extended statistics replace ordinary column statistics.
4. **Lifecycle review:** combine usage window, size, writes, constraints, and
   plans without producing an automatic drop list.
   **Inputs/evidence:** For sql-ops-01 Exercise 4, inventory each events index with size, observed scan count, uniqueness/primary flags, predicate, observation timestamp, and database statistics-reset timestamp.
   **Expected result/shape:** For sql-ops-01 Exercise 4, expected output: one row per index ordered by `index_name`, including the primary and partial covering indexes.
   **Verify:** For sql-ops-01 Exercise 4, reconcile index identities with `pg_index`, record workload observation window and stats reset, and require query/constraint/replica evidence before any reviewed drop; zero scans alone is never sufficient.
5. **Maintenance:** connect vacuum/analyze, visibility, dead tuples, bloat,
   autovacuum, and long transactions.
   **Inputs/evidence:** For sql-ops-01 Exercise 5, return a matrix distinguishing VACUUM, ANALYZE, VACUUM ANALYZE, and VACUUM FULL by evidence domain, effect, and limit.
   **Expected result/shape:** For sql-ops-01 Exercise 5, expected output: four ordered rows with `command`, `evidence_domain`, `primary_effect`, and `important_limit`; the lesson executes no VACUUM inside its transaction.
   **Verify:** For sql-ops-01 Exercise 5, compare each matrix row with observed dead-tuple/freeze/visibility or estimate evidence, assert the command's stated effect and limit, and require a lock/rewrite test result before VACUUM FULL.
6. **Statement statistics:** design restricted, privacy-aware collection and
   review without enabling or exposing it here.
   **Inputs/evidence:** For sql-ops-01 Exercise 6, read-only probe whether pg_stat_statements is absent, installed-not-preloaded, missing its view, permission-denied, not collecting, or readable; never install it or select query text.
   **Expected result/shape:** For sql-ops-01 Exercise 6, expected output: exactly one capability-state row plus four privacy controls with owner; all host states produce a safe result or SAFE SKIP.
   **Verify:** For sql-ops-01 Exercise 6, test absent and installed/preload variants where available, distinguish capability from permission, and require restricted access, redaction, bounded retention, and aggregate-only exports before production use.
7. **Redundancy candidates:** compare keys, order, predicate, operator class,
   collation, INCLUDE data, uniqueness, and plans.
   **Inputs/evidence:** For sql-ops-01 Exercise 7, inventory index definition plus predicate, key expressions, INCLUDE columns, operator classes, collations, uniqueness, and primary status.
   **Expected result/shape:** For sql-ops-01 Exercise 7, expected output: one row per events index ordered by `index_name`, with key and included attributes separated using `indnkeyatts`.
   **Verify:** For sql-ops-01 Exercise 7, compare semantic properties rather than similar SQL text or names, account for constraints and replicas, and emit candidates for human review without automatically dropping anything.
8. **Expression index:** test expression matching and document collation,
   function-volatility, and generated-column alternatives.
   **Inputs/evidence:** For sql-ops-01 Exercise 8, create an index on `lower(device_id)` and use the identical expression/collation in both EXPLAIN and the underlying SELECT.
   **Expected result/shape:** For sql-ops-01 Exercise 8, expected output: one plan followed by the first ten deterministic `(event_id, device_id)` rows matching device-007.
   **Verify:** For sql-ops-01 Exercise 8, compare expression trees and collation/operator semantics, assert all displayed device IDs normalize to device-007, and show that a different expression need not use this index.
9. **HOT updates:** observe a controlled workload and relate indexed columns,
   free space, fillfactor, vacuum, and old snapshots.
   **Inputs/evidence:** For sql-ops-01 Exercise 9, update 100 rows on a nonindexed column, inspect immediate transaction-local counters in `pg_stat_xact_user_tables`, then display cumulative historical counters separately.
   **Expected result/shape:** For sql-ops-01 Exercise 9, expected output: a transaction-local row reporting 100 updates and the observed HOT subset, plus a separate cumulative stats row that may lag.
   **Verify:** For sql-ops-01 Exercise 9, assert the xact update count rather than the asynchronous cumulative value, treat HOT rate as observational, and relate it to indexed columns, tuple size/page space, and vacuum horizons.
10. **Partition indexes:** account for pruning, local indexes, statistics,
    attach/detach, and global uniqueness limitations.
   **Inputs/evidence:** For sql-ops-01 Exercise 10, create a disposable range-partitioned table with January/February partitions, a parent-declared index, and four routed rows; query only February.
   **Expected result/shape:** For sql-ops-01 Exercise 10, expected output: an EXPLAIN plan naming only the February partition, one matching row, three `pg_partition_tree` rows with bounds, and two child-index catalog rows derived from the parent partitioned index.
   **Verify:** For sql-ops-01 Exercise 10, assert the query result independently, inspect child indexes and bounds, prove January is pruned, and state that cross-partition uniqueness normally includes the partition key because PostgreSQL has no general global index.
11. **Plan instrumentation:** distinguish execution and overhead across
    `EXPLAIN` options, especially for writes and cache state.
   **Inputs/evidence:** For sql-ops-01 Exercise 11, run EXPLAIN ANALYZE BUFFERS only on a read-only aggregate, then execute the underlying SELECT and return an execution-safety matrix.
   **Expected result/shape:** For sql-ops-01 Exercise 11, expected output: one plan, one scalar `matching_rows` control, and three statement-class warnings; ANALYZE is execution, not hypothetical planning.
   **Verify:** For sql-ops-01 Exercise 11, reconcile plan actual rows with the scalar control, label cache/fixture effects, and require rollback-only disposable targets before EXPLAIN ANALYZE on INSERT/UPDATE/DELETE.
12. **Maintenance scorecard:** define owners, budgets, cadence, escalation, and
    evidence for growth, health, waits, lag, and slow queries.
   **Inputs/evidence:** For sql-ops-01 Exercise 12, build an owned operational scorecard for dead tuples, invalid indexes, lock waits, and replication lag.
   **Expected result/shape:** For sql-ops-01 Exercise 12, expected output: four rows with `signal`, `evidence_source`, `owner`, `budget`, `cadence`, `escalation`, `runbook`, and `action`.
   **Verify:** For sql-ops-01 Exercise 12, replace illustrative budgets/runbook paths with service-approved values, test each escalation route, and require every alert to identify evidence, owner, decision threshold, and safe next action.

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

Continue to [SQL-TEST-01 - SQL tests, migration checks, and data contracts](sql_test_01_contracts_migrations.md).
Then use [SQL-OPS-02](sql_ops_02_backup_restore_recovery.md) to include index,
statistics, extension, and post-restore verification in a recovery rehearsal.

## Ask an AI tutor about this lesson

The lesson and expected observations are sufficient offline. For optional
coaching, copy:

```text
Tutor me through sql-ops-01: Index Types, Statistics, and Maintenance Lifecycle.

I have completed the direct catalog prerequisites: `sql-35`, `sql-types-01`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_ops_01_indexes_statistics_maintenance.md
- Answer-free learner SQL: sql/professional/lessons/sql_ops_01_indexes_statistics_maintenance.sql

Key terms to teach in context: Access method, Operator class, Partial index, Expression index, Covering index, BRIN range. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The fixture inserts 6,000 events in timestamp order. That physical correlation makes time a plausible BRIN candidate in a much larger append-oriented table. The teaching table is intentionally small, so PostgreSQL may still prefer a sequential scan; that is a valid cost decision.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
