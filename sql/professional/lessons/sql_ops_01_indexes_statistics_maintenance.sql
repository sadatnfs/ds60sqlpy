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
--    Inputs: For sql-ops-01 Exercise 1, change only `events_high_device_time_covering`, and `pro_ops_lab.events` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `information_schema.columns` rows.
--    Expected result/shape: For sql-ops-01 Exercise 1, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `object_name`, `catalog_definition`, `accepted_case`, and `rejected_sqlstate`.
--    Verify: For sql-ops-01 Exercise 1, inspect `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `information_schema.columns` for `events_high_device_time_covering`, and `pro_ops_lab.events`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 1, inspect `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `information_schema.columns` for `events_high_device_time_covering`, and `pro_ops_lab.events`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
-- 2. Explain which operators each GIN, GiST, SP-GiST, and BRIN example serves.
--    Show one superficially similar query that cannot use that operator class.
--
--    Inputs: For sql-ops-01 Exercise 2, read from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Build the answer toward `access_methods_answer`; keep `access_methods_answer` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-01 Exercise 2, expected output: one row per `access_methods_answer`. The final columns are `access_methods_answer`.
--    Verify: For sql-ops-01 Exercise 2, reselect the returned keys directly from the source; require unique `access_methods_answer` where the expected grain is one row per key and confirm the projected `access_methods_answer` against `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Add one source row with a new `access_methods_answer`; verify the result gains exactly one row carrying that `access_methods_answer` value.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 2, select `access_methods_answer` from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index` before adding derived columns.
-- 3. Create useful extended statistics for two correlated filter columns,
--    ANALYZE, and inspect pg_stats_ext. Explain why statistics do not force a
--    plan.
--
--    Inputs: For sql-ops-01 Exercise 3, read from `pro_ops_lab.events`, `pg_catalog.pg_stats_ext`, and `events_category_severity_stats`. Build the answer toward `statistics_name`, `kinds`, and `attnames`; keep `statistics_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-01 Exercise 3, expected output: one row per `statistics_name`. The final columns are `statistics_name`, `kinds`, and `attnames`. The final order is `s.statistics_name`.
--    Verify: For sql-ops-01 Exercise 3, run an anti-check that counts rows where NOT ((s.schemaname = 'pro_ops_lab')); require unique `statistics_name` where the expected grain is one row per key and confirm the projected `statistics_name`, `kinds`, and `attnames` against `pro_ops_lab.events`, `pg_catalog.pg_stats_ext`, and `events_category_severity_stats`. Add one row for which `(s.schemaname = 'pro_ops_lab')` is true and one for which it is false; verify only the matching `statistics_name` value is returned.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 3, inspect the source keys that survive `WHERE`; then check `s.statistics_name` before applying the row cap.
-- 4. Build an index lifecycle review using pg_stat_user_indexes, relation size,
--    write cost, constraint ownership, and a representative observation window.
--    Do not drop an index from a single zero idx_scan snapshot.
--
--    Inputs: For sql-ops-01 Exercise 4, read from `pg_catalog.pg_index`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_stat_user_indexes`, and `pg_catalog.pg_indexes`. Build the answer toward `index_name`, `index_bytes`, `observed_scans`, `indisunique`, `indisprimary`, and `predicate`; keep `index_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-01 Exercise 4, expected output: one row per `index_name`. The final columns are `index_name`, `index_bytes`, `observed_scans`, `indisunique`, `indisprimary`, and `predicate`. The final order is `ci.relname`.
--    Verify: For sql-ops-01 Exercise 4, project `index_name` plus the raw source columns from `pg_catalog.pg_index`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_stat_user_indexes`, and `pg_catalog.pg_indexes` at each join stage; record row count and distinct `index_name`, then assert the final `index_name`, `index_bytes`, `observed_scans`, `indisunique`, `indisprimary`, and `predicate` values match those staged rows without unintended fanout or loss. Insert rows immediately before, exactly at, and immediately after `severity >= 4`; identify which rows pass each inclusive or exclusive comparison.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 4, start with the first relation in `pg_catalog.pg_index`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_stat_user_indexes`, and `pg_catalog.pg_indexes`; after each join, record total rows and distinct `index_name` so the exact fanout or loss is visible.
-- 5. Explain VACUUM, ANALYZE, autovacuum, dead tuples, visibility, and bloat.
--    The DBA-only command below is documentation, not part of this transaction:
--      VACUUM (ANALYZE, VERBOSE) pro_ops_lab.events;
--
--    Inputs: For sql-ops-01 Exercise 5, read from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Build the answer toward `maintenance_answer`; keep `maintenance_answer` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-01 Exercise 5, expected output: one row per `maintenance_answer`. The final columns are `maintenance_answer`.
--    Verify: For sql-ops-01 Exercise 5, reselect the returned keys directly from the source; require unique `maintenance_answer` where the expected grain is one row per key and confirm the projected `maintenance_answer` against `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Add one source row with a new `maintenance_answer`; verify the result gains exactly one row carrying that `maintenance_answer` value.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 5, select `maintenance_answer` from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index` before adding derived columns.
-- 6. Describe a safe pg_stat_statements review. Query text can contain sensitive
--    literals; do not enable the extension or expose query text in this lesson.
--
--    Inputs: For sql-ops-01 Exercise 6, complete the statement statistics written analysis and support its claims with read-only evidence from `pg_stat_statements`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-ops-01 Exercise 6, expected output: a completed the statement statistics written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `queryid`, and `shared_preload_libraries`.
--    Verify: For sql-ops-01 Exercise 6, check the statement statistics written analysis against `queryid`, and `shared_preload_libraries`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 6, check the statement statistics written analysis against `queryid`, and `shared_preload_libraries`.
-- 7. Detect indexes whose leading columns and predicates make another index
--    appear redundant. Then list the evidence that can disprove redundancy:
--    uniqueness, operator class, collation, ordering, INCLUDE columns, and
--    representative plans. Produce candidates, never an automatic DROP script.
--
--    Inputs: For sql-ops-01 Exercise 7, read from `pg_catalog.pg_index`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`. Build the answer toward `index_name`, `indisunique`, `indisprimary`, `index_definition`, and `predicate`; keep `index_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-01 Exercise 7, expected output: one row per `index_name`. The final columns are `index_name`, `indisunique`, `indisprimary`, `index_definition`, and `predicate`. The final order is `ci.relname`.
--    Verify: For sql-ops-01 Exercise 7, project `index_name` plus the raw source columns from `pg_catalog.pg_index`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` at each join stage; record row count and distinct `index_name`, then assert the final `index_name`, `indisunique`, `indisprimary`, `index_definition`, and `predicate` values match those staged rows without unintended fanout or loss. Add duplicate source candidates for `index_name`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 7, start with the first relation in `pg_catalog.pg_index`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `index_name` so the exact fanout or loss is visible.
-- 8. Design an expression index for case-insensitive device lookup. Explain
--    expression matching, collation/version drift, function volatility, and
--    when a generated normalized column gives a clearer contract.
--
--    Inputs: For sql-ops-01 Exercise 8, run the underlying read-only query over `pro_ops_lab.events`, and `events_device_lower_idx` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-ops-01 Exercise 8, expected output: one row per `event_id`. The final columns are `event_id`, and `device_id`. The final order is `e.event_id`.
--    Verify: For sql-ops-01 Exercise 8, run the underlying query without `EXPLAIN` and preserve its `event_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 8, run the underlying query without `EXPLAIN` and preserve its `event_id` rows.
-- 9. Run a controlled update workload and inspect HOT-update and dead-tuple
--    statistics. Explain how indexed columns, page free space, fillfactor,
--    autovacuum thresholds, and long transactions affect the result.
--
--    Inputs: For sql-ops-01 Exercise 9, read from `pro_ops_lab.events`, and `pg_catalog.pg_stat_user_tables`. Build the answer toward `relname`, `n_tup_upd`, `n_tup_hot_upd`, `n_dead_tup`, `last_autovacuum`, and `last_autoanalyze`; keep `relname` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-01 Exercise 9, expected output: one row per `relname`. The final columns are `relname`, `n_tup_upd`, `n_tup_hot_upd`, `n_dead_tup`, `last_autovacuum`, and `last_autoanalyze`.
--    Verify: For sql-ops-01 Exercise 9, run an anti-check that counts rows where NOT ((e.event_id <= 100) OR (s.schemaname = 'pro_ops_lab' AND s.relname = 'events')); require unique `relname` where the expected grain is one row per key and confirm the projected `relname`, `n_tup_upd`, `n_tup_hot_upd`, `n_dead_tup`, `last_autovacuum`, and `last_autoanalyze` against `pro_ops_lab.events`, and `pg_catalog.pg_stat_user_tables`. Insert rows immediately before, exactly at, and immediately after `e.event_id <= 100`; identify which rows pass each inclusive or exclusive comparison.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 9, inspect the source keys that survive `WHERE`.
-- 10. Design indexes for a range-partitioned event table. Compare local indexes,
--     partition pruning, per-partition statistics, attach/detach operations,
--     and the absence of a general PostgreSQL global index.
--
--    Inputs: For sql-ops-01 Exercise 10, read from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Build the answer toward `partition_indexes_answer`; keep `partition_indexes_answer` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-01 Exercise 10, expected output: one row per `partition_indexes_answer`. The final columns are `partition_indexes_answer`.
--    Verify: For sql-ops-01 Exercise 10, reselect the returned keys directly from the source; require unique `partition_indexes_answer` where the expected grain is one row per key and confirm the projected `partition_indexes_answer` against `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index`. Add duplicate source candidates for `partition_indexes_answer`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 10, select `partition_indexes_answer` from `pro_ops_lab.events`, `generate_series`, and `pg_catalog.pg_index` before adding derived columns.
-- 11. Compare EXPLAIN, EXPLAIN ANALYZE, BUFFERS, WAL, and TIMING. State which
--     forms execute writes, how to test a write safely, and why one warm-cache
--     plan is not a production benchmark.
--
--    Inputs: For sql-ops-01 Exercise 11, run the underlying read-only query over `pro_ops_lab.events` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-ops-01 Exercise 11, expected output: one row per `explain`. The final columns are `explain`.
--    Verify: For sql-ops-01 Exercise 11, run the underlying query without `EXPLAIN` and preserve its `explain` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
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
--    Inputs: For sql-ops-01 Exercise 12, read from the inline `VALUES` fixture. Build the answer toward `signal`, `evidence_source`, and `owner`; keep `signal` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-01 Exercise 12, expected output: one row per `signal`. The final columns are `signal`, `evidence_source`, and `owner`. The final order is `signal`.
--    Verify: For sql-ops-01 Exercise 12, reselect the returned keys directly from the source; require unique `signal` where the expected grain is one row per key and confirm the projected `signal`, `evidence_source`, and `owner` against the inline `VALUES` fixture. Add one source row with a new `signal`; verify the result gains exactly one row carrying that `signal` value.
--    Hint ladder, rung 1: For sql-ops-01 Exercise 12, check `signal` before applying the row cap.

ROLLBACK;
\echo 'SQL-OPS-01 complete: pro_ops_lab was rolled back'
