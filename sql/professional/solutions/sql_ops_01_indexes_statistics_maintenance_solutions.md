# SQL-OPS-01 Solutions — Indexes and Maintenance

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

## Exercise 2 — Operator compatibility

- GIN array ops support containment/overlap, not arbitrary element
  transformations.
- GiST point ops support geometry and distance, not text equality.
- SP-GiST text ops support their prefix/ordering family, not array containment.
- BRIN time min/max summaries help range predicates when heap order correlates,
  not random lookup on an unrelated column.

An index method name alone is incomplete; inspect the data type and operator
class.

## Exercise 3 — Correlated statistics

The fixture deliberately correlates `category` and `severity`. Dependencies and
MCV statistics can improve combined-filter cardinality after `ANALYZE`.
Statistics shape estimates; they do not force an access method and need refresh
as data distribution changes.

## Exercise 4 — Lifecycle review

The solution inventories size, scans, predicate, uniqueness, and primary-key
ownership. A real decision also records stats-reset/restart time, full workload
cycle, replica usage, query regressions, write amplification, and rollback
evidence. Constraint-owned indexes are not casual drop candidates.

## Exercise 5 — Maintenance

VACUUM makes dead tuple space reusable, advances freeze safety, and updates
visibility. ANALYZE samples values for estimates. Autovacuum triggers each using
table-size/change thresholds and can be tuned per table after measurement.
Ordinary VACUUM usually does not shrink the relation file; `VACUUM FULL` rewrites
and locks, so it is exceptional maintenance.

## Exercise 6 — Statement statistics

A safe `pg_stat_statements` plan requires approved preload/extension ownership,
restricted view access, retention/reset rules, normalized `queryid` analysis,
and redaction awareness. Do not expose raw query text by default; literals can
contain confidential values. This course does not enable the extension or alter
`shared_preload_libraries`.

## Exercise 7 — Redundancy is a hypothesis

Compare index key attributes in order, INCLUDE columns, predicate,
`indisunique`/constraint ownership, expressions, collations, sort direction,
NULL ordering, and operator classes. A left-prefix match can produce a review
candidate, but a differently ordered, partial, unique, or specialized index is
not equivalent.

Then inspect representative plans and a full workload observation window on
primary and replicas. Output a candidate report with evidence and owner; never
generate/drop automatically from catalog similarity or one zero scan count.

## Exercise 8 — Expression index and collation

An index on `lower(device_name) COLLATE ...` helps a query only when its
expression/operator/collation is compatible. PostgreSQL will not infer every
semantically similar spelling. The function must be index-safe (IMMUTABLE from
the database's perspective).

Record the normalization and collation contract. Provider/version changes can
invalidate ordering assumptions and require review/reindex. A generated
normalized column is often clearer when many writers/queries must share and
inspect the exact transformed value.

## Exercise 9 — HOT and dead tuples

HOT can avoid new index entries when no indexed column changes and the same heap
page has room. Lower fillfactor may reserve that room at a storage/scan cost.
Updating an indexed value, a full page, or an incompatible chain prevents HOT.

Use before/after stats with a controlled workload and account for asynchronous
collector visibility and reset time. Long transactions retain old tuple
versions; vacuum may run yet be unable to remove them. Tune from measured table
behavior, not one universal dead-tuple percentage.

## Exercise 10 — Partitioned indexing

Partition pruning removes irrelevant children when bounds can be inferred.
Indexes and statistics are physically per partition even when declared through
the partitioned parent; verify new/attached partitions and analyze data
distribution individually.

PostgreSQL has no general global index spanning partitions, so global uniqueness
normally must include the partition key or use another design. Plan index build,
attach validation, locks, detached-partition queries, and lifecycle automation.

## Exercise 11 — Reading plan instrumentation safely

Plain EXPLAIN estimates without executing. EXPLAIN ANALYZE executes and adds
actual timing/rows; BUFFERS shows cache/I/O counters, WAL shows generated WAL,
and TIMING can add measurable overhead. A data-changing statement really
changes data unless isolated and rolled back.

Compare cold/warm cache, parameters, concurrency, row counts, server settings,
and repeated runs. Planning/execution time in one tiny transaction is evidence
about that setup, not a production capacity claim.

## Exercise 12 — Owned maintenance scorecard

Track semantic signals: relation/index growth, dead/live tuples, last analyze,
invalid indexes, long transactions, lock waits, WAL/replica lag, query latency,
and error/regression evidence. Attach source, observation window, reset state,
budget, owner, runbook, and review cadence to each.

Thresholds depend on workload and capacity. Use trends and service objectives,
define warning/critical escalation, suppress known maintenance windows
carefully, and require human review before invasive maintenance.

## Edge cases

- Prepared parameters can prevent partial-predicate implication at plan time.
- Heap correlation changes as updates rewrite pages.
- Statistics and usage counters reset or lag.
- Index size alone does not measure cache or WAL cost.
