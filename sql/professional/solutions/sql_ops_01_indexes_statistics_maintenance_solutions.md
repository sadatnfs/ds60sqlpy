# SQL-OPS-01 Solutions — Indexes and Maintenance


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_ops_01_indexes_statistics_maintenance_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_ops_01_indexes_statistics_maintenance_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Access method, Operator class, Partial index, Expression index, Covering index, BRIN range. Its worked-model focus is:
The fixture inserts 6,000 events in timestamp order. That physical correlation makes time a plausible BRIN candidate in a much larger append-oriented table. The teaching table is intentionally small, so PostgreSQL may still prefer a sequential scan; that is a valid cost decision.

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
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_ops_01_indexes_statistics_maintenance_solutions.sql
```

The solution rolls back `pro_ops_lab` and performs no vacuum or configuration
change.

## Exercise 1 — Covering partial index

The solution pairs its exact high-severity device-history query with:

```sql
CREATE INDEX events_high_device_time_covering
ON pro_ops_lab.events (device_id, occurred_at DESC)
INCLUDE (severity, message)
WHERE severity >= 4;
```

Device equality and time order are keys. Severity/message are returned payload.
The query explicitly includes `severity >= 4`, so it implies the partial
predicate. Whether an index-only scan occurs also depends on visibility and
cost.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 1, match the query's equality/range/order/projection with a partial covering btree on `(device_id, occurred_at DESC)` including severity/message and predicated on `severity >= 4`.
- **Expected result/shape:** For sql-ops-01 Exercise 1, expected output: catalog command evidence, one EXPLAIN plan, and up to 25 underlying rows with `occurred_at`, `severity`, and `message` for device-005 in descending time order.
- **Independent verification:** For sql-ops-01 Exercise 1, assert every result satisfies the partial predicate, compare returned rows with the same SELECT without planner settings, inspect the exact index predicate/include columns, and treat scan type as observed evidence—not a guaranteed contract.

## Exercise 2 — Operator compatibility

- GIN array ops support containment/overlap, not arbitrary element
  transformations.
- GiST point ops support geometry and distance, not text equality.
- SP-GiST text ops support their prefix/ordering family, not array containment.
- BRIN time min/max summaries help range predicates when heap order correlates,
  not random lookup on an unrelated column.

An index method name alone is incomplete; inspect the data type and operator
class.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 2, map GIN, GiST, SP-GiST, and BRIN to concrete type/operator workloads and state one important trade-off for each.
- **Expected result/shape:** For sql-ops-01 Exercise 2, expected output: four ordered rows with `method`, `suitable_types`, `target_operators`, and `tradeoff`.
- **Independent verification:** For sql-ops-01 Exercise 2, identify the exact operator class available for the target type, test representative data distribution/write cost, and reject any recommendation that names only an access method without its query operator.

## Exercise 3 — Correlated statistics

The fixture deliberately correlates `category` and `severity`. Dependencies and
MCV statistics can improve combined-filter cardinality after `ANALYZE`.
Statistics shape estimates; they do not force an access method and need refresh
as data distribution changes.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 3, create dependency and MCV extended statistics on the correlated `category`/`severity` pair, ANALYZE, then inspect `pg_stats_ext`.
- **Expected result/shape:** For sql-ops-01 Exercise 3, expected output: exactly one statistics row with its name, kinds, and attribute names.
- **Independent verification:** For sql-ops-01 Exercise 3, compare EXPLAIN estimated rows before/after ANALYZE for a correlated predicate, retain actual counts as control, and do not claim extended statistics replace ordinary column statistics.

## Exercise 4 — Lifecycle review

The solution inventories size, scans, predicate, uniqueness, and primary-key
ownership. A real decision also records stats-reset/restart time, full workload
cycle, replica usage, query regressions, write amplification, and rollback
evidence. Constraint-owned indexes are not casual drop candidates.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 4, inventory each events index with size, observed scan count, uniqueness/primary flags, predicate, observation timestamp, and database statistics-reset timestamp.
- **Expected result/shape:** For sql-ops-01 Exercise 4, expected output: one row per index ordered by `index_name`, including the primary and partial covering indexes.
- **Independent verification:** For sql-ops-01 Exercise 4, reconcile index identities with `pg_index`, record workload observation window and stats reset, and require query/constraint/replica evidence before any reviewed drop; zero scans alone is never sufficient.

## Exercise 5 — Maintenance

VACUUM makes dead tuple space reusable, advances freeze safety, and updates
visibility. ANALYZE samples values for estimates. Autovacuum triggers each using
table-size/change thresholds and can be tuned per table after measurement.
Ordinary VACUUM usually does not shrink the relation file; `VACUUM FULL` rewrites
and locks, so it is exceptional maintenance.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 5, return a matrix distinguishing VACUUM, ANALYZE, VACUUM ANALYZE, and VACUUM FULL by evidence domain, effect, and limit.
- **Expected result/shape:** For sql-ops-01 Exercise 5, expected output: four ordered rows with `command`, `evidence_domain`, `primary_effect`, and `important_limit`; the lesson executes no VACUUM inside its transaction.
- **Independent verification:** For sql-ops-01 Exercise 5, compare each matrix row with observed dead-tuple/freeze/visibility or estimate evidence, assert the command's stated effect and limit, and require a lock/rewrite test result before VACUUM FULL.

## Exercise 6 — Statement statistics

A safe `pg_stat_statements` plan requires approved preload/extension ownership,
restricted view access, retention/reset rules, normalized `queryid` analysis,
and redaction awareness. Do not expose raw query text by default; literals can
contain confidential values. This course does not enable the extension or alter
`shared_preload_libraries`.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 6, read-only probe whether pg_stat_statements is absent, installed-not-preloaded, missing its view, permission-denied, not collecting, or readable; never install it or select query text.
- **Expected result/shape:** For sql-ops-01 Exercise 6, expected output: exactly one capability-state row plus four privacy controls with owner; all host states produce a safe result or SAFE SKIP.
- **Independent verification:** For sql-ops-01 Exercise 6, test absent and installed/preload variants where available, distinguish capability from permission, and require restricted access, redaction, bounded retention, and aggregate-only exports before production use.

## Exercise 7 — Redundancy is a hypothesis

Compare index key attributes in order, INCLUDE columns, predicate,
`indisunique`/constraint ownership, expressions, collations, sort direction,
NULL ordering, and operator classes. A left-prefix match can produce a review
candidate, but a differently ordered, partial, unique, or specialized index is
not equivalent.

Then inspect representative plans and a full workload observation window on
primary and replicas. Output a candidate report with evidence and owner; never
generate/drop automatically from catalog similarity or one zero scan count.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 7, inventory index definition plus predicate, key expressions, INCLUDE columns, operator classes, collations, uniqueness, and primary status.
- **Expected result/shape:** For sql-ops-01 Exercise 7, expected output: one row per events index ordered by `index_name`, with key and included attributes separated using `indnkeyatts`.
- **Independent verification:** For sql-ops-01 Exercise 7, compare semantic properties rather than similar SQL text or names, account for constraints and replicas, and emit candidates for human review without automatically dropping anything.

## Exercise 8 — Expression index and collation

An index on `lower(device_name) COLLATE ...` helps a query only when its
expression/operator/collation is compatible. PostgreSQL will not infer every
semantically similar spelling. The function must be index-safe (IMMUTABLE from
the database's perspective).

Record the normalization and collation contract. Provider/version changes can
invalidate ordering assumptions and require review/reindex. A generated
normalized column is often clearer when many writers/queries must share and
inspect the exact transformed value.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 8, create an index on `lower(device_id)` and use the identical expression/collation in both EXPLAIN and the underlying SELECT.
- **Expected result/shape:** For sql-ops-01 Exercise 8, expected output: one plan followed by the first ten deterministic `(event_id, device_id)` rows matching device-007.
- **Independent verification:** For sql-ops-01 Exercise 8, compare expression trees and collation/operator semantics, assert all displayed device IDs normalize to device-007, and show that a different expression need not use this index.

## Exercise 9 — HOT and dead tuples

HOT can avoid new index entries when no indexed column changes and the same heap
page has room. Lower fillfactor may reserve that room at a storage/scan cost.
Updating an indexed value, a full page, or an incompatible chain prevents HOT.

Use before/after stats with a controlled workload and account for asynchronous
collector visibility and reset time. Long transactions retain old tuple
versions; vacuum may run yet be unable to remove them. Tune from measured table
behavior, not one universal dead-tuple percentage.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 9, update 100 rows on a nonindexed column, inspect immediate transaction-local counters in `pg_stat_xact_user_tables`, then display cumulative historical counters separately.
- **Expected result/shape:** For sql-ops-01 Exercise 9, expected output: a transaction-local row reporting 100 updates and the observed HOT subset, plus a separate cumulative stats row that may lag.
- **Independent verification:** For sql-ops-01 Exercise 9, assert the xact update count rather than the asynchronous cumulative value, treat HOT rate as observational, and relate it to indexed columns, tuple size/page space, and vacuum horizons.

## Exercise 10 — Partitioned indexing

Partition pruning removes irrelevant children when bounds can be inferred.
Indexes and statistics are physically per partition even when declared through
the partitioned parent; verify new/attached partitions and analyze data
distribution individually.

PostgreSQL has no general global index spanning partitions, so global uniqueness
normally must include the partition key or use another design. Plan index build,
attach validation, locks, detached-partition queries, and lifecycle automation.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 10, create a disposable range-partitioned table with January/February partitions, a parent-declared index, and four routed rows; query only February.
- **Expected result/shape:** For sql-ops-01 Exercise 10, expected output: an EXPLAIN plan naming only the February partition, one matching row, three `pg_partition_tree` rows with bounds, and two child-index catalog rows derived from the parent partitioned index.
- **Independent verification:** For sql-ops-01 Exercise 10, assert the query result independently, inspect child indexes and bounds, prove January is pruned, and state that cross-partition uniqueness normally includes the partition key because PostgreSQL has no general global index.

## Exercise 11 — Reading plan instrumentation safely

Plain EXPLAIN estimates without executing. EXPLAIN ANALYZE executes and adds
actual timing/rows; BUFFERS shows cache/I/O counters, WAL shows generated WAL,
and TIMING can add measurable overhead. A data-changing statement really
changes data unless isolated and rolled back.

Compare cold/warm cache, parameters, concurrency, row counts, server settings,
and repeated runs. Planning/execution time in one tiny transaction is evidence
about that setup, not a production capacity claim.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 11, run EXPLAIN ANALYZE BUFFERS only on a read-only aggregate, then execute the underlying SELECT and return an execution-safety matrix.
- **Expected result/shape:** For sql-ops-01 Exercise 11, expected output: one plan, one scalar `matching_rows` control, and three statement-class warnings; ANALYZE is execution, not hypothetical planning.
- **Independent verification:** For sql-ops-01 Exercise 11, reconcile plan actual rows with the scalar control, label cache/fixture effects, and require rollback-only disposable targets before EXPLAIN ANALYZE on INSERT/UPDATE/DELETE.

## Exercise 12 — Owned maintenance scorecard

Track semantic signals: relation/index growth, dead/live tuples, last analyze,
invalid indexes, long transactions, lock waits, WAL/replica lag, query latency,
and error/regression evidence. Attach source, observation window, reset state,
budget, owner, runbook, and review cadence to each.

Thresholds depend on workload and capacity. Use trends and service objectives,
define warning/critical escalation, suppress known maintenance windows
carefully, and require human review before invasive maintenance.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 12, build an owned operational scorecard for dead tuples, invalid indexes, lock waits, and replication lag.
- **Expected result/shape:** For sql-ops-01 Exercise 12, expected output: four rows with `signal`, `evidence_source`, `owner`, `budget`, `cadence`, `escalation`, `runbook`, and `action`.
- **Independent verification:** For sql-ops-01 Exercise 12, replace illustrative budgets/runbook paths with service-approved values, test each escalation route, and require every alert to identify evidence, owner, decision threshold, and safe next action.

## Edge cases

- Prepared parameters can prevent partial-predicate implication at plan time.
- Heap correlation changes as updates rewrite pages.
- Statistics and usage counters reset or lag.
- Index size alone does not measure cache or WAL cost.
