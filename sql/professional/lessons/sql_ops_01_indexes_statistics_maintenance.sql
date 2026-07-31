-- SQL-OPS-01: Index types, statistics, and maintenance lifecycle
-- BEGINNER WORKFLOW — sql-ops-01: Index Types, Statistics, and Maintenance Lifecycle
-- Guide: sql/professional/companion-guides/sql_ops_01_indexes_statistics_maintenance.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-ops-01/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pro_ops_lab.events, pg_catalog.pg_index, pg_catalog.pg_class, pg_catalog.pg_namespace, pg_catalog.pg_am.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Target: PostgreSQL 16+
-- VACUUM and host configuration changes are intentionally not executed.

\set ON_ERROR_STOP on
\echo 'SQL-OPS-01: disposable index and statistics lab'
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_ops_lab;

CREATE TABLE pro_ops_lab.events (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    device_id text NOT NULL,
    occurred_at timestamptz NOT NULL,
    severity smallint NOT NULL CHECK (severity BETWEEN 1 AND 5),
    tags text[] NOT NULL DEFAULT ARRAY[]::text[],
    location point NOT NULL,
    message text NOT NULL
);

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

-- B-tree: equality and ordered/range access.
CREATE INDEX events_device_time_btree
ON pro_ops_lab.events (device_id, occurred_at DESC)
INCLUDE (severity);

-- BRIN: compact summaries for a large table physically correlated with time.
CREATE INDEX events_occurred_at_brin
ON pro_ops_lab.events
USING brin (occurred_at)
WITH (pages_per_range = 8);

-- GIN: inverted membership over array elements.
CREATE INDEX events_tags_gin
ON pro_ops_lab.events
USING gin (tags);

-- GiST: nearest-neighbour and geometric operators for point.
CREATE INDEX events_location_gist
ON pro_ops_lab.events
USING gist (location);

-- SP-GiST: partitioned search structure with a text operator class.
CREATE INDEX events_device_spgist
ON pro_ops_lab.events
USING spgist (device_id);

-- Expression and partial indexes require query expressions/predicates that are
-- compatible with their stored expressions.
CREATE INDEX events_lower_message_btree
ON pro_ops_lab.events (lower(message));

CREATE INDEX events_high_severity_partial
ON pro_ops_lab.events (occurred_at DESC, device_id)
WHERE severity >= 4;

CREATE STATISTICS events_device_severity_stats (dependencies, mcv)
ON device_id, severity
FROM pro_ops_lab.events;

ANALYZE pro_ops_lab.events;

\echo 'Catalog every index method, definition, predicate, and measured size'
SELECT
    ci.relname AS index_name,
    am.amname AS access_method,
    pg_catalog.pg_get_indexdef(i.indexrelid) AS index_definition,
    pg_catalog.pg_get_expr(i.indpred, i.indrelid) AS predicate,
    pg_catalog.pg_relation_size(i.indexrelid) AS index_bytes
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci
  ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct
  ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = ct.relnamespace
JOIN pg_catalog.pg_am AS am
  ON am.oid = ci.relam
WHERE n.nspname = 'pro_ops_lab'
  AND ct.relname = 'events'
ORDER BY ci.relname;

\echo 'Plans are environment evidence, not promises'
EXPLAIN (COSTS OFF)
SELECT
    e.event_id,
    e.occurred_at,
    e.severity
FROM pro_ops_lab.events AS e
WHERE e.device_id = 'device-007'
ORDER BY e.occurred_at DESC
LIMIT 20;

EXPLAIN (COSTS OFF)
SELECT
    e.event_id,
    e.tags
FROM pro_ops_lab.events AS e
WHERE e.tags @> ARRAY['network']::text[]
ORDER BY e.event_id;

EXPLAIN (COSTS OFF)
SELECT
    e.event_id,
    e.location
FROM pro_ops_lab.events AS e
ORDER BY e.location <-> point(50, 50)
LIMIT 5;

EXPLAIN (COSTS OFF)
SELECT
    COUNT(*)
FROM pro_ops_lab.events AS e
WHERE e.occurred_at >= TIMESTAMPTZ '2026-01-04 00:00:00+00'
  AND e.occurred_at < TIMESTAMPTZ '2026-01-05 00:00:00+00';

\echo 'Extended statistics and table/index lifecycle observations'
SELECT
    s.statistics_name,
    s.kinds,
    s.attnames
FROM pg_catalog.pg_stats_ext AS s
WHERE s.schemaname = 'pro_ops_lab'
ORDER BY s.statistics_name;

SELECT
    st.relname,
    st.seq_scan,
    st.idx_scan,
    st.n_live_tup,
    st.n_dead_tup,
    st.last_analyze,
    st.last_autoanalyze,
    st.last_autovacuum
FROM pg_catalog.pg_stat_all_tables AS st
WHERE st.schemaname = 'pro_ops_lab'
ORDER BY st.relname;

SELECT
    psui.indexrelname,
    psui.idx_scan,
    psui.idx_tup_read,
    psui.idx_tup_fetch
FROM pg_catalog.pg_stat_user_indexes AS psui
WHERE psui.schemaname = 'pro_ops_lab'
ORDER BY psui.indexrelname;

SELECT
    setting.name,
    setting.setting,
    setting.unit,
    setting.source
FROM pg_catalog.pg_settings AS setting
WHERE setting.name IN (
    'autovacuum',
    'autovacuum_analyze_scale_factor',
    'autovacuum_vacuum_scale_factor',
    'default_statistics_target',
    'shared_preload_libraries'
)
ORDER BY setting.name;

SELECT
    EXISTS (
        SELECT 1
        FROM pg_catalog.pg_extension AS ext
        WHERE ext.extname = 'pg_stat_statements'
    ) AS pg_stat_statements_installed;

-- Exercises:
--
-- 1. Design a covering partial index for high-severity device history. Write
--    the exact query it serves and make its WHERE clause imply the predicate.
--
--    Inputs: For sql-ops-01 Exercise 1, match the query's equality/range/order/projection with a partial covering btree on `(device_id, occurred_at DESC)` including severity/message and predicated on `severity >= 4`.
--    Expected result/shape: For sql-ops-01 Exercise 1, expected output: catalog command evidence, one EXPLAIN plan, and up to 25 underlying rows with `occurred_at`, `severity`, and `message` for device-005 in descending time order.
--    Verify: For sql-ops-01 Exercise 1, assert every result satisfies the partial predicate, compare returned rows with the same SELECT without planner settings, inspect the exact index predicate/include columns, and treat scan type as observed evidence—not a guaranteed contract.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 1, inspect `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `information_schema.columns` for `events_high_device_time_covering`, and `pro_ops_lab.events`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
-- 2. Explain which operators each GIN, GiST, SP-GiST, and BRIN example serves.
--    Show one superficially similar query that cannot use that operator class.
--
--    Inputs: For sql-ops-01 Exercise 2, map GIN, GiST, SP-GiST, and BRIN to concrete type/operator workloads and state one important trade-off for each.
--    Expected result/shape: For sql-ops-01 Exercise 2, expected output: four ordered rows with `method`, `suitable_types`, `target_operators`, and `tradeoff`.
--    Verify: For sql-ops-01 Exercise 2, identify the exact operator class available for the target type, test representative data distribution/write cost, and reject any recommendation that names only an access method without its query operator.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 2, select `access_methods_answer` from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index` before adding derived columns.
-- 3. Create useful extended statistics for two correlated filter columns,
--    ANALYZE, and inspect pg_stats_ext. Explain why statistics do not force a
--    plan.
--
--    Inputs: For sql-ops-01 Exercise 3, create dependency and MCV extended statistics on the correlated `category`/`severity` pair, ANALYZE, then inspect `pg_stats_ext`.
--    Expected result/shape: For sql-ops-01 Exercise 3, expected output: exactly one statistics row with its name, kinds, and attribute names.
--    Verify: For sql-ops-01 Exercise 3, compare EXPLAIN estimated rows before/after ANALYZE for a correlated predicate, retain actual counts as control, and do not claim extended statistics replace ordinary column statistics.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 3, inspect the source keys that survive `WHERE`; then check `s.statistics_name` before applying the row cap.
-- 4. Build an index lifecycle review using pg_stat_user_indexes, relation size,
--    write cost, constraint ownership, and a representative observation window.
--    Do not drop an index from a single zero idx_scan snapshot.
--
--    Inputs: For sql-ops-01 Exercise 4, inventory each events index with size, observed scan count, uniqueness/primary flags, predicate, observation timestamp, and database statistics-reset timestamp.
--    Expected result/shape: For sql-ops-01 Exercise 4, expected output: one row per index ordered by `index_name`, including the primary and partial covering indexes.
--    Verify: For sql-ops-01 Exercise 4, reconcile index identities with `pg_index`, record workload observation window and stats reset, and require query/constraint/replica evidence before any reviewed drop; zero scans alone is never sufficient.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 4, start with the first relation in `pg_catalog.pg_index`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_stat_user_indexes`, and `pg_catalog.pg_indexes`; after each join, record total rows and distinct `index_name` so the exact fanout or loss is visible.
-- 5. Explain VACUUM, ANALYZE, autovacuum, dead tuples, visibility, and bloat.
--    The DBA-only command below is documentation, not part of this transaction:
--      VACUUM (ANALYZE, VERBOSE) pro_ops_lab.events;
--
--    Inputs: For sql-ops-01 Exercise 5, return a matrix distinguishing VACUUM, ANALYZE, VACUUM ANALYZE, and VACUUM FULL by evidence domain, effect, and limit.
--    Expected result/shape: For sql-ops-01 Exercise 5, expected output: four ordered rows with `command`, `evidence_domain`, `primary_effect`, and `important_limit`; the lesson executes no VACUUM inside its transaction.
--    Verify: For sql-ops-01 Exercise 5, compare each matrix row with observed dead-tuple/freeze/visibility or estimate evidence, assert the command's stated effect and limit, and require a lock/rewrite test result before VACUUM FULL.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 5, select `maintenance_answer` from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index` before adding derived columns.
-- 6. Describe a safe pg_stat_statements review. Query text can contain sensitive
--    literals; do not enable the extension or expose query text in this lesson.
--
--    Inputs: For sql-ops-01 Exercise 6, read-only probe whether pg_stat_statements is absent, installed-not-preloaded, missing its view, permission-denied, not collecting, or readable; never install it or select query text.
--    Expected result/shape: For sql-ops-01 Exercise 6, expected output: exactly one capability-state row plus four privacy controls with owner; all host states produce a safe result or SAFE SKIP.
--    Verify: For sql-ops-01 Exercise 6, test absent and installed/preload variants where available, distinguish capability from permission, and require restricted access, redaction, bounded retention, and aggregate-only exports before production use.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 6, check the statement statistics written analysis against `queryid`, and `shared_preload_libraries`.
-- 7. Detect indexes whose leading columns and predicates make another index
--    appear redundant. Then list the evidence that can disprove redundancy:
--    uniqueness, operator class, collation, ordering, INCLUDE columns, and
--    representative plans. Produce candidates, never an automatic DROP script.
--
--    Inputs: For sql-ops-01 Exercise 7, inventory index definition plus predicate, key expressions, INCLUDE columns, operator classes, collations, uniqueness, and primary status.
--    Expected result/shape: For sql-ops-01 Exercise 7, expected output: one row per events index ordered by `index_name`, with key and included attributes separated using `indnkeyatts`.
--    Verify: For sql-ops-01 Exercise 7, compare semantic properties rather than similar SQL text or names, account for constraints and replicas, and emit candidates for human review without automatically dropping anything.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 7, start with the first relation in `pg_catalog.pg_index`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `index_name` so the exact fanout or loss is visible.
-- 8. Design an expression index for case-insensitive device lookup. Explain
--    expression matching, collation/version drift, function volatility, and
--    when a generated normalized column gives a clearer contract.
--
--    Inputs: For sql-ops-01 Exercise 8, create an index on `lower(device_id)` and use the identical expression/collation in both EXPLAIN and the underlying SELECT.
--    Expected result/shape: For sql-ops-01 Exercise 8, expected output: one plan followed by the first ten deterministic `(event_id, device_id)` rows matching device-007.
--    Verify: For sql-ops-01 Exercise 8, compare expression trees and collation/operator semantics, assert all displayed device IDs normalize to device-007, and show that a different expression need not use this index.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 8, run the underlying query without `EXPLAIN` and preserve its `event_id` rows.
-- 9. Run a controlled update workload and inspect HOT-update and dead-tuple
--    statistics. Explain how indexed columns, page free space, fillfactor,
--    autovacuum thresholds, and long transactions affect the result.
--
--    Inputs: For sql-ops-01 Exercise 9, update 100 rows on a nonindexed column, inspect immediate transaction-local counters in `pg_stat_xact_user_tables`, then display cumulative historical counters separately.
--    Expected result/shape: For sql-ops-01 Exercise 9, expected output: a transaction-local row reporting 100 updates and the observed HOT subset, plus a separate cumulative stats row that may lag.
--    Verify: For sql-ops-01 Exercise 9, assert the xact update count rather than the asynchronous cumulative value, treat HOT rate as observational, and relate it to indexed columns, tuple size/page space, and vacuum horizons.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 9, inspect the source keys that survive `WHERE`.
-- 10. Design indexes for a range-partitioned event table. Compare local indexes,
--     partition pruning, per-partition statistics, attach/detach operations,
--     and the absence of a general PostgreSQL global index.
--
--    Inputs: For sql-ops-01 Exercise 10, create a disposable range-partitioned table with January/February partitions, a parent-declared index, and four routed rows; query only February.
--    Expected result/shape: For sql-ops-01 Exercise 10, expected output: an EXPLAIN plan naming only the February partition, one matching row, three `pg_partition_tree` rows with bounds, and two child-index catalog rows derived from the parent partitioned index.
--    Verify: For sql-ops-01 Exercise 10, assert the query result independently, inspect child indexes and bounds, prove January is pruned, and state that cross-partition uniqueness normally includes the partition key because PostgreSQL has no general global index.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 10, select `partition_indexes_answer` from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index` before adding derived columns.
-- 11. Compare EXPLAIN, EXPLAIN ANALYZE, BUFFERS, WAL, and TIMING. State which
--     forms execute writes, how to test a write safely, and why one warm-cache
--     plan is not a production benchmark.
--
--    Inputs: For sql-ops-01 Exercise 11, run EXPLAIN ANALYZE BUFFERS only on a read-only aggregate, then execute the underlying SELECT and return an execution-safety matrix.
--    Expected result/shape: For sql-ops-01 Exercise 11, expected output: one plan, one scalar `matching_rows` control, and three statement-class warnings; ANALYZE is execution, not hypothetical planning.
--    Verify: For sql-ops-01 Exercise 11, reconcile plan actual rows with the scalar control, label cache/fixture effects, and require rollback-only disposable targets before EXPLAIN ANALYZE on INSERT/UPDATE/DELETE.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 11, run the underlying query without `EXPLAIN` and preserve its `explain` rows.
-- 12. Create a maintenance scorecard with owners and budgets for table/index
--     growth, dead tuples, analyze freshness, invalid indexes, lock wait,
--     replication lag, and slow-query evidence. Define escalation and review
--     cadence rather than universal thresholds.

DO $self_check$
BEGIN
    IF (SELECT COUNT(*) FROM pro_ops_lab.events) <> 6000 THEN
        RAISE EXCEPTION 'unexpected event count';
    END IF;
    IF (
        SELECT COUNT(*)
        FROM pg_catalog.pg_indexes AS i
        WHERE i.schemaname = 'pro_ops_lab'
          AND i.tablename = 'events'
    ) < 8 THEN
        RAISE EXCEPTION 'expected primary-key plus seven teaching indexes';
    END IF;
END
$self_check$;
--    Inputs: For sql-ops-01 Exercise 12, build an owned operational scorecard for dead tuples, invalid indexes, lock waits, and replication lag.
--    Expected result/shape: For sql-ops-01 Exercise 12, expected output: four rows with `signal`, `evidence_source`, `owner`, `budget`, `cadence`, `escalation`, `runbook`, and `action`.
--    Verify: For sql-ops-01 Exercise 12, replace illustrative budgets/runbook paths with service-approved values, test each escalation route, and require every alert to identify evidence, owner, decision threshold, and safe next action.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 12, check `signal` before applying the row cap.

ROLLBACK;
\echo 'SQL-OPS-01 complete: pro_ops_lab was rolled back'
