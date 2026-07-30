-- SQL-OPS-01 executable solutions
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

ROLLBACK;

