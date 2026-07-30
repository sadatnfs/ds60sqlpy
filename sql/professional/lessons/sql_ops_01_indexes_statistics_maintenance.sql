-- SQL-OPS-01: Index types, statistics, and maintenance lifecycle
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
-- 2. Explain which operators each GIN, GiST, SP-GiST, and BRIN example serves.
--    Show one superficially similar query that cannot use that operator class.
--
-- 3. Create useful extended statistics for two correlated filter columns,
--    ANALYZE, and inspect pg_stats_ext. Explain why statistics do not force a
--    plan.
--
-- 4. Build an index lifecycle review using pg_stat_user_indexes, relation size,
--    write cost, constraint ownership, and a representative observation window.
--    Do not drop an index from a single zero idx_scan snapshot.
--
-- 5. Explain VACUUM, ANALYZE, autovacuum, dead tuples, visibility, and bloat.
--    The DBA-only command below is documentation, not part of this transaction:
--      VACUUM (ANALYZE, VERBOSE) pro_ops_lab.events;
--
-- 6. Describe a safe pg_stat_statements review. Query text can contain sensitive
--    literals; do not enable the extension or expose query text in this lesson.
--
-- 7. Detect indexes whose leading columns and predicates make another index
--    appear redundant. Then list the evidence that can disprove redundancy:
--    uniqueness, operator class, collation, ordering, INCLUDE columns, and
--    representative plans. Produce candidates, never an automatic DROP script.
--
-- 8. Design an expression index for case-insensitive device lookup. Explain
--    expression matching, collation/version drift, function volatility, and
--    when a generated normalized column gives a clearer contract.
--
-- 9. Run a controlled update workload and inspect HOT-update and dead-tuple
--    statistics. Explain how indexed columns, page free space, fillfactor,
--    autovacuum thresholds, and long transactions affect the result.
--
-- 10. Design indexes for a range-partitioned event table. Compare local indexes,
--     partition pruning, per-partition statistics, attach/detach operations,
--     and the absence of a general PostgreSQL global index.
--
-- 11. Compare EXPLAIN, EXPLAIN ANALYZE, BUFFERS, WAL, and TIMING. State which
--     forms execute writes, how to test a write safely, and why one warm-cache
--     plan is not a production benchmark.
--
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

ROLLBACK;
\echo 'SQL-OPS-01 complete: pro_ops_lab was rolled back'
