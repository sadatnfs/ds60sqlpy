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

## Edge cases

- Prepared parameters can prevent partial-predicate implication at plan time.
- Heap correlation changes as updates rewrite pages.
- Statistics and usage counters reset or lag.
- Index size alone does not measure cache or WAL cost.

