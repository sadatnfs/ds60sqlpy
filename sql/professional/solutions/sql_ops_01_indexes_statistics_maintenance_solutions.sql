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
WHERE e.device_id = 'device-005'
  AND e.severity >= 4
ORDER BY e.occurred_at DESC
LIMIT 25;

SELECT
    e.occurred_at,
    e.severity,
    e.message
FROM pro_ops_lab.events AS e
WHERE e.device_id = 'device-005'
  AND e.severity >= 4
ORDER BY e.occurred_at DESC
LIMIT 25;

-- Exercise 2: access method, operator class, and query operator form one
-- contract. An index family name alone is not a design.
SELECT *
FROM (
    VALUES
        ('GIN'::text, 'jsonb, arrays, tsvector'::text,
         'containment/membership/full-text', 'fast reads; heavier writes; no natural ordering'),
        ('GiST', 'ranges, geometry, nearest-neighbor types',
         'overlap/containment/distance', 'lossy checks and workload-specific opclasses'),
        ('SP-GiST', 'partitionable search spaces such as inet/text points',
         'prefix/nearest search by opclass', 'excellent for matching distributions, not universal'),
        ('BRIN', 'physically correlated large tables',
         'range exclusion by block summaries', 'tiny and cheap, but returns lossy candidate blocks')
) AS access_method(
    method,
    suitable_types,
    target_operators,
    tradeoff
)
ORDER BY method;

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
    pg_catalog.pg_get_expr(i.indpred, i.indrelid) AS predicate,
    clock_timestamp() AS observed_at,
    d.stats_reset
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci
  ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct
  ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = ct.relnamespace
LEFT JOIN pg_catalog.pg_stat_user_indexes AS si
  ON si.indexrelid = i.indexrelid
LEFT JOIN pg_catalog.pg_stat_database AS d
  ON d.datid = (SELECT oid FROM pg_catalog.pg_database WHERE datname = current_database())
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

-- Exercise 5: this transaction does not run VACUUM. Return a maintenance
-- decision matrix that separates reclaim/freeze/visibility from estimates.
SELECT *
FROM (
    VALUES
        ('VACUUM'::text, 'dead tuples, freeze age, visibility map'::text,
         'reclaim reusable space and prevent transaction-ID wraparound'::text,
         'does not usually shrink the relation file'),
        ('ANALYZE', 'sampled value distribution and correlation',
         'refresh planner estimates', 'does not reclaim dead tuples'),
        ('VACUUM (ANALYZE)', 'both maintenance signals',
         'perform both jobs when the operational budget permits',
         'still requires lock/WAL/runtime monitoring'),
        ('VACUUM FULL', 'exceptional file compaction evidence',
         'rewrite and return file space to the OS',
         'takes an ACCESS EXCLUSIVE lock; not routine maintenance')
) AS maintenance(
    command,
    evidence_domain,
    primary_effect,
    important_limit
)
ORDER BY command;

-- Exercise 6: detect capability state without enabling an extension or
-- exposing query text. Query-text access and retention require privacy review.
CREATE TEMP TABLE ds60_pgss_probe (
    capability_state text NOT NULL,
    detail text NOT NULL
) ON COMMIT DROP;

DO $solution$
DECLARE
    installed boolean;
    preloaded boolean;
    view_name regclass;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM pg_catalog.pg_extension
        WHERE extname = 'pg_stat_statements'
    ) INTO installed;

    preloaded :=
        'pg_stat_statements' = ANY (
            pg_catalog.regexp_split_to_array(
                COALESCE(
                    pg_catalog.current_setting(
                        'shared_preload_libraries',
                        true
                    ),
                    ''
                ),
                '\s*,\s*'
            )
        );

    SELECT to_regclass(
        pg_catalog.quote_ident(n.nspname) || '.pg_stat_statements'
    )
    INTO view_name
    FROM pg_catalog.pg_extension AS e
    JOIN pg_catalog.pg_namespace AS n
      ON n.oid = e.extnamespace
    WHERE e.extname = 'pg_stat_statements';

    IF NOT installed THEN
        INSERT INTO ds60_pgss_probe
        VALUES ('absent', 'extension is not installed; no change was attempted');
    ELSIF NOT preloaded THEN
        INSERT INTO ds60_pgss_probe
        VALUES (
            'installed_not_preloaded',
            'catalog objects exist but collection may require server preload/restart'
        );
    ELSIF view_name IS NULL THEN
        INSERT INTO ds60_pgss_probe
        VALUES ('installed_missing_view', 'extension catalog and view disagree');
    ELSE
        BEGIN
            EXECUTE pg_catalog.format('SELECT 1 FROM %s LIMIT 1', view_name);
            INSERT INTO ds60_pgss_probe
            VALUES (
                'readable',
                'view is readable; query text is intentionally not selected'
            );
        EXCEPTION
            WHEN insufficient_privilege THEN
                INSERT INTO ds60_pgss_probe
                VALUES ('permission_denied', 'extension exists but caller cannot read it');
            WHEN object_not_in_prerequisite_state THEN
                INSERT INTO ds60_pgss_probe
                VALUES ('not_collecting', 'extension exists but prerequisite state is absent');
        END;
    END IF;
END
$solution$;

SELECT capability_state, detail
FROM ds60_pgss_probe;

SELECT *
FROM (
    VALUES
        (1, 'restrict view access'::text, 'database operator'::text),
        (2, 'normalize/redact literals and identifiers before export', 'privacy owner'),
        (3, 'set bounded retention and deletion', 'data governance owner'),
        (4, 'publish aggregate fingerprints/latency, not raw query text', 'observability owner')
) AS pgss_privacy(step_number, control, owner)
ORDER BY step_number;

-- Exercise 7: show semantic index properties for human review. Similarity is a
-- candidate signal, never an automatic DROP decision.
SELECT
    ci.relname AS index_name,
    i.indisunique,
    i.indisprimary,
    pg_catalog.pg_get_indexdef(i.indexrelid) AS index_definition,
    pg_catalog.pg_get_expr(i.indpred, i.indrelid) AS predicate,
    keys.key_expressions,
    keys.included_columns,
    keys.operator_classes,
    keys.collations
FROM pg_catalog.pg_index AS i
JOIN pg_catalog.pg_class AS ci
  ON ci.oid = i.indexrelid
JOIN pg_catalog.pg_class AS ct
  ON ct.oid = i.indrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = ct.relnamespace
LEFT JOIN LATERAL (
    SELECT
        array_agg(
            pg_catalog.pg_get_indexdef(i.indexrelid, pos.n, false)
            ORDER BY pos.n
        ) FILTER (WHERE pos.n <= i.indnkeyatts) AS key_expressions,
        array_agg(
            pg_catalog.pg_get_indexdef(i.indexrelid, pos.n, false)
            ORDER BY pos.n
        ) FILTER (WHERE pos.n > i.indnkeyatts) AS included_columns,
        array_agg(opc.opcname::text ORDER BY pos.n)
            FILTER (WHERE pos.n <= i.indnkeyatts) AS operator_classes,
        array_agg(coll.collname::text ORDER BY pos.n)
            FILTER (WHERE pos.n <= i.indnkeyatts) AS collations
    FROM generate_series(1, i.indnatts) AS pos(n)
    LEFT JOIN pg_catalog.pg_opclass AS opc
      ON opc.oid = i.indclass[pos.n - 1]
    LEFT JOIN pg_catalog.pg_collation AS coll
      ON coll.oid = i.indcollation[pos.n - 1]
) AS keys
  ON true
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
ORDER BY e.event_id
LIMIT 10;

SELECT e.event_id, e.device_id
FROM pro_ops_lab.events AS e
WHERE lower(e.device_id) = 'device-007'
ORDER BY e.event_id
LIMIT 10;

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
    s.n_tup_hot_upd
FROM pg_catalog.pg_stat_xact_user_tables AS s
WHERE s.schemaname = 'pro_ops_lab'
  AND s.relname = 'events';

-- The cumulative view is historical and can lag the current transaction. It is
-- displayed separately rather than used to assert the immediately preceding
-- UPDATE.
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

-- Exercise 10: disposable two-month fixture proves partition routing, pruning,
-- and per-partition index realization.
CREATE TABLE pro_ops_lab.partitioned_events (
    event_id bigint NOT NULL,
    occurred_on date NOT NULL,
    device_id text NOT NULL,
    PRIMARY KEY (occurred_on, event_id)
) PARTITION BY RANGE (occurred_on);

CREATE TABLE pro_ops_lab.partitioned_events_2026_01
PARTITION OF pro_ops_lab.partitioned_events
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE pro_ops_lab.partitioned_events_2026_02
PARTITION OF pro_ops_lab.partitioned_events
FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE INDEX partitioned_events_device_idx
ON pro_ops_lab.partitioned_events (device_id, occurred_on);

INSERT INTO pro_ops_lab.partitioned_events
VALUES
    (1, DATE '2026-01-10', 'device-007'),
    (2, DATE '2026-01-20', 'device-008'),
    (3, DATE '2026-02-10', 'device-007'),
    (4, DATE '2026-02-20', 'device-009');

EXPLAIN (COSTS OFF)
SELECT pe.event_id, pe.occurred_on, pe.device_id
FROM pro_ops_lab.partitioned_events AS pe
WHERE pe.occurred_on >= DATE '2026-02-01'
  AND pe.occurred_on < DATE '2026-03-01'
  AND pe.device_id = 'device-007'
ORDER BY pe.event_id;

SELECT pe.event_id, pe.occurred_on, pe.device_id
FROM pro_ops_lab.partitioned_events AS pe
WHERE pe.occurred_on >= DATE '2026-02-01'
  AND pe.occurred_on < DATE '2026-03-01'
  AND pe.device_id = 'device-007'
ORDER BY pe.event_id;

SELECT
    pt.relid::regclass AS partition_relation,
    pt.parentrelid::regclass AS parent_relation,
    pt.isleaf,
    pt.level,
    pg_catalog.pg_get_expr(c.relpartbound, c.oid) AS partition_bound
FROM pg_catalog.pg_partition_tree(
    'pro_ops_lab.partitioned_events'::regclass
) AS pt
JOIN pg_catalog.pg_class AS c
  ON c.oid = pt.relid
ORDER BY pt.level, pt.relid::regclass::text;

SELECT
    parent_index.relname AS parent_index,
    child_table.relname AS child_partition,
    child_index.relname AS child_index,
    pg_catalog.pg_get_indexdef(child_index.oid) AS child_index_definition
FROM pg_catalog.pg_class AS parent_index
JOIN pg_catalog.pg_namespace AS parent_ns
  ON parent_ns.oid = parent_index.relnamespace
JOIN pg_catalog.pg_inherits AS inh
  ON inh.inhparent = parent_index.oid
JOIN pg_catalog.pg_class AS child_index
  ON child_index.oid = inh.inhrelid
JOIN pg_catalog.pg_index AS child_index_meta
  ON child_index_meta.indexrelid = child_index.oid
JOIN pg_catalog.pg_class AS child_table
  ON child_table.oid = child_index_meta.indrelid
WHERE parent_ns.nspname = 'pro_ops_lab'
  AND parent_index.relname = 'partitioned_events_device_idx'
ORDER BY child_table.relname, child_index.relname;

-- Exercise 11: ANALYZE executes this read. BUFFERS is cache/I/O evidence for
-- this fixture, not a production benchmark.
EXPLAIN (ANALYZE, BUFFERS, COSTS OFF, TIMING OFF)
SELECT COUNT(*)
FROM pro_ops_lab.events AS e
WHERE e.device_id = 'device-005'
  AND e.severity >= 4;

SELECT COUNT(*) AS matching_rows
FROM pro_ops_lab.events AS e
WHERE e.device_id = 'device-005'
  AND e.severity >= 4;

SELECT *
FROM (
    VALUES
        ('SELECT'::text, 'EXPLAIN ANALYZE executes a read-only statement'::text),
        ('UPDATE/DELETE/INSERT', 'EXPLAIN ANALYZE performs the write; use rollback-only fixtures'),
        ('DDL/maintenance', 'test only in disposable targets with explicit lock and recovery plans')
) AS explain_safety(statement_class, execution_warning)
ORDER BY statement_class;

-- Exercise 12: an owned scorecard attaches source, budget, cadence, and action
-- instead of pretending one threshold fits every workload.
SELECT *
FROM (
    VALUES
        ('dead tuples'::text, 'pg_stat_user_tables'::text, 'table owner'::text,
         'workload-specific dead-tuple/age budget'::text, 'daily and after bulk writes'::text,
         'page on freeze risk or sustained SLO breach'::text,
         'runbooks/vacuum.md'::text, 'tune autovacuum or schedule reviewed maintenance'::text),
        ('invalid indexes', 'pg_index.indisvalid', 'database operator',
         'zero unexplained invalid production indexes', 'after every index build and daily',
         'page immediately when a build leaves an invalid artifact',
         'runbooks/index-build.md', 'inspect identity/state before retry or reviewed drop'),
        ('lock wait', 'pg_stat_activity/pg_locks', 'service owner',
         'service latency and lock-wait SLO', 'continuous',
         'page when blocker age or user impact exceeds budget',
         'runbooks/lock-response.md', 'identify blocker; cancel/terminate only by runbook'),
        ('replication lag', 'replay LSN and user SLO', 'HA owner',
         'RPO/RTO-derived byte and time lag', 'continuous',
         'page before recovery-point or read-staleness budget is breached',
         'runbooks/replication-lag.md', 'throttle workload or follow HA incident plan')
) AS scorecard(
    signal,
    evidence_source,
    owner,
    budget,
    cadence,
    escalation,
    runbook,
    action
)
ORDER BY signal;

ROLLBACK;
