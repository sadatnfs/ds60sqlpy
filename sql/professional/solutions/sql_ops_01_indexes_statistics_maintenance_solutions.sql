-- SQL-OPS-01 executable solutions
-- SOLUTION READING MAP — sql-ops-01: Index Types, Statistics, and Maintenance Lifecycle
-- Explanation: sql/professional/solutions/sql_ops_01_indexes_statistics_maintenance_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_ops_01_indexes_statistics_maintenance_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_ops_lab;

CREATE TABLE pro_ops_lab.events (
    event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    device_id text NOT NULL,
    occurred_at timestamptz NOT NULL,
    severity smallint NOT NULL,
    category text NOT NULL,
    message text NOT NULL
);

INSERT INTO pro_ops_lab.events (
    device_id, occurred_at, severity, category, message
)
SELECT
    'device-' || lpad(((g.n % 20) + 1)::text, 3, '0'),
    TIMESTAMPTZ '2026-01-01 00:00:00+00' + g.n * INTERVAL '1 minute',
    ((g.n % 5) + 1)::smallint,
    CASE WHEN g.n % 5 >= 3 THEN 'urgent' ELSE 'routine' END,
    CASE WHEN g.n % 10 = 0 THEN 'Retry warning' ELSE 'Observation' END
FROM generate_series(1, 3000) AS g(n);

-- Exercise 1: query and predicate-compatible covering partial index.
CREATE INDEX events_high_device_time_covering
ON pro_ops_lab.events (device_id, occurred_at DESC)
INCLUDE (severity, message)
WHERE severity >= 4;

EXPLAIN (COSTS OFF)
SELECT
    e.occurred_at,
    e.severity,
    e.message
FROM pro_ops_lab.events AS e
WHERE e.device_id = 'device-007'
  AND e.severity >= 4
ORDER BY e.occurred_at DESC
LIMIT 25;

-- Exercise 3: category and severity are correlated by fixture construction.
CREATE STATISTICS events_category_severity_stats (dependencies, mcv)
ON category, severity
FROM pro_ops_lab.events;

ANALYZE pro_ops_lab.events;

SELECT
    s.statistics_name,
    s.kinds,
    s.attnames
FROM pg_catalog.pg_stats_ext AS s
WHERE s.schemaname = 'pro_ops_lab'
ORDER BY s.statistics_name;

-- Exercise 4: a compact lifecycle inventory, not an automatic drop list.
SELECT
    ci.relname AS index_name,
    pg_catalog.pg_relation_size(ci.oid) AS index_bytes,
    COALESCE(si.idx_scan, 0) AS observed_scans,
    i.indisunique,
    i.indisprimary,
    pg_catalog.pg_get_expr(i.indpred, i.indrelid) AS predicate
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci
  ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct
  ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = ct.relnamespace
LEFT JOIN pg_catalog.pg_stat_user_indexes AS si
  ON si.indexrelid = i.indexrelid
WHERE n.nspname = 'pro_ops_lab'
  AND ct.relname = 'events'
ORDER BY ci.relname;

DO $solution$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_catalog.pg_indexes AS i
        WHERE i.schemaname = 'pro_ops_lab'
          AND i.indexname = 'events_high_device_time_covering'
          AND i.indexdef LIKE '%WHERE (severity >= 4)%'
    ) THEN
        RAISE EXCEPTION 'partial covering index definition missing';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_catalog.pg_stats_ext AS s
        WHERE s.schemaname = 'pro_ops_lab'
          AND s.statistics_name = 'events_category_severity_stats'
    ) THEN
        RAISE EXCEPTION 'extended statistics were not analyzed';
    END IF;
END
$solution$;

-- Exercise 2: access methods are meaningful only with type/operator class and
-- target operator. The Markdown solution maps GIN, GiST, SP-GiST, and BRIN.

-- Exercise 5: this transaction does not run VACUUM. VACUUM reclaims dead-tuple
-- space/freeze safety/visibility; ANALYZE samples values for estimates.

-- Exercise 6: this solution neither enables pg_stat_statements nor exposes
-- query text. Production access and retention require privacy review.

-- Exercise 7: show semantic index properties for human review. Similarity is a
-- candidate signal, never an automatic DROP decision.
SELECT
    ci.relname AS index_name,
    i.indisunique,
    i.indisprimary,
    pg_catalog.pg_get_indexdef(i.indexrelid) AS index_definition,
    pg_catalog.pg_get_expr(i.indpred, i.indrelid) AS predicate
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci
  ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct
  ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = ct.relnamespace
WHERE n.nspname = 'pro_ops_lab'
  AND ct.relname = 'events'
ORDER BY ci.relname;

-- Exercise 8: the query expression must match the indexed expression and its
-- collation/operator semantics.
CREATE INDEX events_device_lower_idx
ON pro_ops_lab.events (lower(device_id));

EXPLAIN (COSTS OFF)
SELECT e.event_id, e.device_id
FROM pro_ops_lab.events AS e
WHERE lower(e.device_id) = 'device-007'
ORDER BY e.event_id;

-- Exercise 9: observe rather than assert a HOT rate; page space, indexed
-- columns, vacuum horizons, and asynchronous statistics affect the result.
UPDATE pro_ops_lab.events AS e
SET category = CASE e.category
    WHEN 'routine' THEN 'routine-reviewed'
    ELSE e.category
END
WHERE e.event_id <= 100;

SELECT
    s.relname,
    s.n_tup_upd,
    s.n_tup_hot_upd,
    s.n_dead_tup,
    s.last_autovacuum,
    s.last_autoanalyze
FROM pg_catalog.pg_stat_user_tables AS s
WHERE s.schemaname = 'pro_ops_lab'
  AND s.relname = 'events';

-- Exercise 10: partition pruning and indexes are validated per partition.
-- PostgreSQL has no general global index, so cross-partition uniqueness usually
-- includes the partition key or uses another ownership design.

-- Exercise 11: ANALYZE executes this read. BUFFERS is cache/I/O evidence for
-- this fixture, not a production benchmark.
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF, TIMING OFF)
SELECT COUNT(*)
FROM pro_ops_lab.events AS e
WHERE e.device_id = 'device-007'
  AND e.severity >= 4;

-- Exercise 12: an owned scorecard attaches source, budget, cadence, and action
-- instead of pretending one threshold fits every workload.
SELECT *
FROM (
    VALUES
        ('dead tuples'::text, 'pg_stat_user_tables'::text, 'table owner'::text),
        ('invalid indexes', 'pg_index.indisvalid', 'database operator'),
        ('lock wait', 'pg_stat_activity/pg_locks', 'service owner'),
        ('replication lag', 'replay LSN and user SLO', 'HA owner')
) AS scorecard(signal, evidence_source, owner)
ORDER BY signal;

ROLLBACK;
