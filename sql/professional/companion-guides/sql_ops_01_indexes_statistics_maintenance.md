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

Complete all six prompts: a predicate-compatible covering index, access-method
operator mapping, extended statistics, a cautious lifecycle review, maintenance
semantics, and a safe statement-statistics plan. Include the exact target query
beside every proposed index.

Use `EXPLAIN` as evidence, not as a pass/fail assertion that one node type must
appear on every machine or data size.

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
