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

- **Inputs/evidence:** For sql-ops-01 Exercise 1, change only `events_high_device_time_covering`, and `pro_ops_lab.events` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `information_schema.columns` rows.
- **Expected result/shape:** For sql-ops-01 Exercise 1, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `object_name`, `catalog_definition`, `accepted_case`, and `rejected_sqlstate`.
- **Independent verification:** For sql-ops-01 Exercise 1, inspect `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `information_schema.columns` for `events_high_device_time_covering`, and `pro_ops_lab.events`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
- **Intermediate relation check:** For sql-ops-01 Exercise 1, inspect `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `information_schema.columns` for `events_high_device_time_covering`, and `pro_ops_lab.events`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
- **Clause check:** For sql-ops-01 Exercise 1, the solution actually uses `WHERE`. Read only those operations: begin at `events_high_device_time_covering`, and `pro_ops_lab.events`, preserve one row per `object_name`, and finish with `object_name`, `catalog_definition`, `accepted_case`, and `rejected_sqlstate`.
- **Alternative/trade-off:** For sql-ops-01 Exercise 1, the chosen form is justified by this lesson-specific rationale: The solution pairs its exact high-severity device-history query with: Device equality and time order are keys. Evaluate another form against the concrete expected result (the requested DDL command tag plus catalog rows and one accepted and one rejected behavior) and the verification above.
- **Edge case:** Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.

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

- **Inputs/evidence:** For sql-ops-01 Exercise 2, read from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Build the answer toward `access_methods_answer`; keep `access_methods_answer` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-01 Exercise 2, expected output: one row per `access_methods_answer`. The final columns are `access_methods_answer`.
- **Independent verification:** For sql-ops-01 Exercise 2, reselect the returned keys directly from the source; require unique `access_methods_answer` where the expected grain is one row per key and confirm the projected `access_methods_answer` against `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Add one source row with a new `access_methods_answer`; verify the result gains exactly one row carrying that `access_methods_answer` value.
- **Intermediate relation check:** For sql-ops-01 Exercise 2, select `access_methods_answer` from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index` before adding derived columns.
- **Clause check:** For sql-ops-01 Exercise 2, the solution actually uses `WITH`. Read only those operations: begin at `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`, preserve one row per `access_methods_answer`, and finish with `access_methods_answer`.
- **Alternative/trade-off:** For sql-ops-01 Exercise 2, the chosen form is justified by this lesson-specific rationale: - GIN array ops support containment/overlap, not arbitrary element transformations. Evaluate another form against the concrete expected result (one row per `access_methods_answer`) and the verification above.
- **Edge case:** Add one source row with a new `access_methods_answer`; verify the result gains exactly one row carrying that `access_methods_answer` value.

## Exercise 3 — Correlated statistics

The fixture deliberately correlates `category` and `severity`. Dependencies and
MCV statistics can improve combined-filter cardinality after `ANALYZE`.
Statistics shape estimates; they do not force an access method and need refresh
as data distribution changes.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 3, read from `pro_ops_lab.events`, `pg_catalog.pg_stats_ext`, and `events_category_severity_stats`. Build the answer toward `statistics_name`, `kinds`, and `attnames`; keep `statistics_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-01 Exercise 3, expected output: one row per `statistics_name`. The final columns are `statistics_name`, `kinds`, and `attnames`. The final order is `s.statistics_name`.
- **Independent verification:** For sql-ops-01 Exercise 3, run an anti-check that counts rows where NOT ((s.schemaname = 'pro_ops_lab')); require unique `statistics_name` where the expected grain is one row per key and confirm the projected `statistics_name`, `kinds`, and `attnames` against `pro_ops_lab.events`, `pg_catalog.pg_stats_ext`, and `events_category_severity_stats`. Add one row for which `(s.schemaname = 'pro_ops_lab')` is true and one for which it is false; verify only the matching `statistics_name` value is returned.
- **Intermediate relation check:** For sql-ops-01 Exercise 3, inspect the source keys that survive `WHERE`; then check `s.statistics_name` before applying the row cap.
- **Clause check:** For sql-ops-01 Exercise 3, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_ops_lab.events`, `pg_catalog.pg_stats_ext`, and `events_category_severity_stats`, preserve one row per `statistics_name`, and finish with `statistics_name`, `kinds`, and `attnames` ordered by `s.statistics_name`.
- **Alternative/trade-off:** For sql-ops-01 Exercise 3, the chosen form is justified by this lesson-specific rationale: The fixture deliberately correlates `category` and `severity`. Evaluate another form against the concrete expected result (one row per `statistics_name`) and the verification above.
- **Edge case:** Add one row for which `(s.schemaname = 'pro_ops_lab')` is true and one for which it is false; verify only the matching `statistics_name` value is returned.

## Exercise 4 — Lifecycle review

The solution inventories size, scans, predicate, uniqueness, and primary-key
ownership. A real decision also records stats-reset/restart time, full workload
cycle, replica usage, query regressions, write amplification, and rollback
evidence. Constraint-owned indexes are not casual drop candidates.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 4, read from `pg_catalog.pg_index`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_stat_user_indexes`, and `pg_catalog.pg_indexes`. Build the answer toward `index_name`, `index_bytes`, `observed_scans`, `indisunique`, `indisprimary`, and `predicate`; keep `index_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-01 Exercise 4, expected output: one row per `index_name`. The final columns are `index_name`, `index_bytes`, `observed_scans`, `indisunique`, `indisprimary`, and `predicate`. The final order is `ci.relname`.
- **Independent verification:** For sql-ops-01 Exercise 4, project `index_name` plus the raw source columns from `pg_catalog.pg_index`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_stat_user_indexes`, and `pg_catalog.pg_indexes` at each join stage; record row count and distinct `index_name`, then assert the final `index_name`, `index_bytes`, `observed_scans`, `indisunique`, `indisprimary`, and `predicate` values match those staged rows without unintended fanout or loss. Insert rows immediately before, exactly at, and immediately after `severity >= 4`; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-ops-01 Exercise 4, start with the first relation in `pg_catalog.pg_index`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_stat_user_indexes`, and `pg_catalog.pg_indexes`; after each join, record total rows and distinct `index_name` so the exact fanout or loss is visible.
- **Clause check:** For sql-ops-01 Exercise 4, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_catalog.pg_index`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_stat_user_indexes`, and `pg_catalog.pg_indexes`, preserve one row per `index_name`, and finish with `index_name`, `index_bytes`, `observed_scans`, `indisunique`, `indisprimary`, and `predicate` ordered by `ci.relname`.
- **Alternative/trade-off:** For sql-ops-01 Exercise 4, the chosen form is justified by this lesson-specific rationale: The solution inventories size, scans, predicate, uniqueness, and primary-key ownership. Evaluate another form against the concrete expected result (one row per `index_name`) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after `severity >= 4`; identify which rows pass each inclusive or exclusive comparison.

## Exercise 5 — Maintenance

VACUUM makes dead tuple space reusable, advances freeze safety, and updates
visibility. ANALYZE samples values for estimates. Autovacuum triggers each using
table-size/change thresholds and can be tuned per table after measurement.
Ordinary VACUUM usually does not shrink the relation file; `VACUUM FULL` rewrites
and locks, so it is exceptional maintenance.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 5, read from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Build the answer toward `maintenance_answer`; keep `maintenance_answer` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-01 Exercise 5, expected output: one row per `maintenance_answer`. The final columns are `maintenance_answer`.
- **Independent verification:** For sql-ops-01 Exercise 5, reselect the returned keys directly from the source; require unique `maintenance_answer` where the expected grain is one row per key and confirm the projected `maintenance_answer` against `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Add one source row with a new `maintenance_answer`; verify the result gains exactly one row carrying that `maintenance_answer` value.
- **Intermediate relation check:** For sql-ops-01 Exercise 5, select `maintenance_answer` from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index` before adding derived columns.
- **Clause check:** For sql-ops-01 Exercise 5, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ops-01 Exercise 5, the chosen form is justified by this lesson-specific rationale: VACUUM makes dead tuple space reusable, advances freeze safety, and updates visibility. Evaluate another form against the concrete expected result (one row per `maintenance_answer`) and the verification above.
- **Edge case:** Add one source row with a new `maintenance_answer`; verify the result gains exactly one row carrying that `maintenance_answer` value.

## Exercise 6 — Statement statistics

A safe `pg_stat_statements` plan requires approved preload/extension ownership,
restricted view access, retention/reset rules, normalized `queryid` analysis,
and redaction awareness. Do not expose raw query text by default; literals can
contain confidential values. This course does not enable the extension or alter
`shared_preload_libraries`.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 6, complete the statement statistics written analysis and support its claims with read-only evidence from `pg_stat_statements`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-ops-01 Exercise 6, expected output: a completed the statement statistics written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `queryid`, and `shared_preload_libraries`.
- **Independent verification:** For sql-ops-01 Exercise 6, check the statement statistics written analysis against `queryid`, and `shared_preload_libraries`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-ops-01 Exercise 6, check the statement statistics written analysis against `queryid`, and `shared_preload_libraries`.
- **Clause check:** For sql-ops-01 Exercise 6, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_stat_statements` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ops-01 Exercise 6, the chosen form is justified by this lesson-specific rationale: A safe `pg_stat_statements` plan requires approved preload/extension ownership, restricted view access, retention/reset rules, normalized `queryid` analysis, and redaction awareness. Evaluate another form against the concrete expected result (a completed the statement statistics written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

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

- **Inputs/evidence:** For sql-ops-01 Exercise 7, read from `pg_catalog.pg_index`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`. Build the answer toward `index_name`, `indisunique`, `indisprimary`, `index_definition`, and `predicate`; keep `index_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-01 Exercise 7, expected output: one row per `index_name`. The final columns are `index_name`, `indisunique`, `indisprimary`, `index_definition`, and `predicate`. The final order is `ci.relname`.
- **Independent verification:** For sql-ops-01 Exercise 7, project `index_name` plus the raw source columns from `pg_catalog.pg_index`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` at each join stage; record row count and distinct `index_name`, then assert the final `index_name`, `indisunique`, `indisprimary`, `index_definition`, and `predicate` values match those staged rows without unintended fanout or loss. Add duplicate source candidates for `index_name`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-ops-01 Exercise 7, start with the first relation in `pg_catalog.pg_index`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `index_name` so the exact fanout or loss is visible.
- **Clause check:** For sql-ops-01 Exercise 7, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_catalog.pg_index`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`, preserve one row per `index_name`, and finish with `index_name`, `indisunique`, `indisprimary`, `index_definition`, and `predicate` ordered by `ci.relname`.
- **Alternative/trade-off:** For sql-ops-01 Exercise 7, the chosen form is justified by this lesson-specific rationale: Compare index key attributes in order, INCLUDE columns, predicate, `indisunique`/constraint ownership, expressions, collations, sort direction, NULL ordering, and operator classes. Evaluate another form against the concrete expected result (one row per `index_name`) and the verification above.
- **Edge case:** Add duplicate source candidates for `index_name`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

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

- **Inputs/evidence:** For sql-ops-01 Exercise 8, run the underlying read-only query over `pro_ops_lab.events`, and `events_device_lower_idx` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-ops-01 Exercise 8, expected output: one row per `event_id`. The final columns are `event_id`, and `device_id`. The final order is `e.event_id`.
- **Independent verification:** For sql-ops-01 Exercise 8, run the underlying query without `EXPLAIN` and preserve its `event_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-ops-01 Exercise 8, run the underlying query without `EXPLAIN` and preserve its `event_id` rows.
- **Clause check:** For sql-ops-01 Exercise 8, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_ops_lab.events`, and `events_device_lower_idx`, preserve one row per `event_id`, and finish with `event_id`, and `device_id` ordered by `e.event_id`.
- **Alternative/trade-off:** For sql-ops-01 Exercise 8, the chosen form is justified by this lesson-specific rationale: An index on `lower(device_name) COLLATE ...` helps a query only when its expression/operator/collation is compatible. Evaluate another form against the concrete expected result (one row per `event_id`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 9 — HOT and dead tuples

HOT can avoid new index entries when no indexed column changes and the same heap
page has room. Lower fillfactor may reserve that room at a storage/scan cost.
Updating an indexed value, a full page, or an incompatible chain prevents HOT.

Use before/after stats with a controlled workload and account for asynchronous
collector visibility and reset time. Long transactions retain old tuple
versions; vacuum may run yet be unable to remove them. Tune from measured table
behavior, not one universal dead-tuple percentage.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 9, read from `pro_ops_lab.events`, and `pg_catalog.pg_stat_user_tables`. Build the answer toward `relname`, `n_tup_upd`, `n_tup_hot_upd`, `n_dead_tup`, `last_autovacuum`, and `last_autoanalyze`; keep `relname` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-01 Exercise 9, expected output: one row per `relname`. The final columns are `relname`, `n_tup_upd`, `n_tup_hot_upd`, `n_dead_tup`, `last_autovacuum`, and `last_autoanalyze`.
- **Independent verification:** For sql-ops-01 Exercise 9, run an anti-check that counts rows where NOT ((e.event_id <= 100) OR (s.schemaname = 'pro_ops_lab' AND s.relname = 'events')); require unique `relname` where the expected grain is one row per key and confirm the projected `relname`, `n_tup_upd`, `n_tup_hot_upd`, `n_dead_tup`, `last_autovacuum`, and `last_autoanalyze` against `pro_ops_lab.events`, and `pg_catalog.pg_stat_user_tables`. Insert rows immediately before, exactly at, and immediately after `e.event_id <= 100`; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-ops-01 Exercise 9, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-ops-01 Exercise 9, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `pro_ops_lab.events`, and `pg_catalog.pg_stat_user_tables`, preserve one row per `relname`, and finish with `relname`, `n_tup_upd`, `n_tup_hot_upd`, `n_dead_tup`, `last_autovacuum`, and `last_autoanalyze`.
- **Alternative/trade-off:** For sql-ops-01 Exercise 9, the chosen form is justified by this lesson-specific rationale: HOT can avoid new index entries when no indexed column changes and the same heap page has room. Evaluate another form against the concrete expected result (one row per `relname`) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after `e.event_id <= 100`; identify which rows pass each inclusive or exclusive comparison.

## Exercise 10 — Partitioned indexing

Partition pruning removes irrelevant children when bounds can be inferred.
Indexes and statistics are physically per partition even when declared through
the partitioned parent; verify new/attached partitions and analyze data
distribution individually.

PostgreSQL has no general global index spanning partitions, so global uniqueness
normally must include the partition key or use another design. Plan index build,
attach validation, locks, detached-partition queries, and lifecycle automation.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 10, read from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Build the answer toward `partition_indexes_answer`; keep `partition_indexes_answer` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-01 Exercise 10, expected output: one row per `partition_indexes_answer`. The final columns are `partition_indexes_answer`.
- **Independent verification:** For sql-ops-01 Exercise 10, reselect the returned keys directly from the source; require unique `partition_indexes_answer` where the expected grain is one row per key and confirm the projected `partition_indexes_answer` against `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Add duplicate source candidates for `partition_indexes_answer`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-ops-01 Exercise 10, select `partition_indexes_answer` from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index` before adding derived columns.
- **Clause check:** For sql-ops-01 Exercise 10, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ops-01 Exercise 10, the chosen form is justified by this lesson-specific rationale: Partition pruning removes irrelevant children when bounds can be inferred. Evaluate another form against the concrete expected result (one row per `partition_indexes_answer`) and the verification above.
- **Edge case:** Add duplicate source candidates for `partition_indexes_answer`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Exercise 11 — Reading plan instrumentation safely

Plain EXPLAIN estimates without executing. EXPLAIN ANALYZE executes and adds
actual timing/rows; BUFFERS shows cache/I/O counters, WAL shows generated WAL,
and TIMING can add measurable overhead. A data-changing statement really
changes data unless isolated and rolled back.

Compare cold/warm cache, parameters, concurrency, row counts, server settings,
and repeated runs. Planning/execution time in one tiny transaction is evidence
about that setup, not a production capacity claim.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 11, run the underlying read-only query over `pro_ops_lab.events` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-ops-01 Exercise 11, expected output: one row per `explain`. The final columns are `explain`.
- **Independent verification:** For sql-ops-01 Exercise 11, run the underlying query without `EXPLAIN` and preserve its `explain` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-ops-01 Exercise 11, run the underlying query without `EXPLAIN` and preserve its `explain` rows.
- **Clause check:** For sql-ops-01 Exercise 11, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `pro_ops_lab.events`, preserve one row per `explain`, and finish with `explain`.
- **Alternative/trade-off:** For sql-ops-01 Exercise 11, the chosen form is justified by this lesson-specific rationale: Plain EXPLAIN estimates without executing. Evaluate another form against the concrete expected result (one row per `explain`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 12 — Owned maintenance scorecard

Track semantic signals: relation/index growth, dead/live tuples, last analyze,
invalid indexes, long transactions, lock waits, WAL/replica lag, query latency,
and error/regression evidence. Attach source, observation window, reset state,
budget, owner, runbook, and review cadence to each.

Thresholds depend on workload and capacity. Use trends and service objectives,
define warning/critical escalation, suppress known maintenance windows
carefully, and require human review before invasive maintenance.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-01 Exercise 12, read from the inline `VALUES` fixture. Build the answer toward `signal`, `evidence_source`, and `owner`; keep `signal` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-01 Exercise 12, expected output: one row per `signal`. The final columns are `signal`, `evidence_source`, and `owner`. The final order is `signal`.
- **Independent verification:** For sql-ops-01 Exercise 12, reselect the returned keys directly from the source; require unique `signal` where the expected grain is one row per key and confirm the projected `signal`, `evidence_source`, and `owner` against the inline `VALUES` fixture. Add one source row with a new `signal`; verify the result gains exactly one row carrying that `signal` value.
- **Intermediate relation check:** For sql-ops-01 Exercise 12, check `signal` before applying the row cap.
- **Clause check:** For sql-ops-01 Exercise 12, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `signal`, and finish with `signal`, `evidence_source`, and `owner` ordered by `signal`.
- **Alternative/trade-off:** For sql-ops-01 Exercise 12, the chosen form is justified by this lesson-specific rationale: Track semantic signals: relation/index growth, dead/live tuples, last analyze, invalid indexes, long transactions, lock waits, WAL/replica lag, query latency, and error/regression evidence. Evaluate another form against the concrete expected result (one row per `signal`) and the verification above.
- **Edge case:** Add one source row with a new `signal`; verify the result gains exactly one row carrying that `signal` value.

## Edge cases

- Prepared parameters can prevent partial-predicate implication at plan time.
- Heap correlation changes as updates rewrite pages.
- Statistics and usage counters reset or lag.
- Index size alone does not measure cache or WAL cost.
