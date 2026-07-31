-- SQL-REPL-01 executable solutions: local simulation only.
-- SOLUTION READING MAP — sql-repl-01: Replication, Change Data Capture, and High Availability
-- Explanation: sql/professional/solutions/sql_repl_01_cdc_high_availability_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_repl_01_cdc_high_availability_solutions.sql
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
CREATE SCHEMA pro_replication_lab;

CREATE TABLE pro_replication_lab.outbox_events (
    event_id text PRIMARY KEY,
    aggregate_key text NOT NULL,
    aggregate_version integer NOT NULL CHECK (aggregate_version > 0),
    payload jsonb NOT NULL,
    published boolean NOT NULL DEFAULT false,
    UNIQUE (aggregate_key, aggregate_version)
);

CREATE TABLE pro_replication_lab.inbox (
    consumer_name text NOT NULL,
    event_id text NOT NULL,
    payload_sha256 text NOT NULL,
    PRIMARY KEY (consumer_name, event_id)
);

CREATE TABLE pro_replication_lab.projection (
    consumer_name text NOT NULL,
    aggregate_key text NOT NULL,
    aggregate_version integer NOT NULL,
    status text NOT NULL,
    PRIMARY KEY (consumer_name, aggregate_key)
);

INSERT INTO pro_replication_lab.outbox_events
VALUES
    ('E-v1', 'ORDER-1', 1, '{"status":"open"}', false),
    ('E-v2', 'ORDER-1', 2, '{"status":"paid"}', false),
    ('E-v3', 'ORDER-1', 3, '{"status":"cancelled"}', false);

CREATE PROCEDURE pro_replication_lab.deliver_event(
    p_consumer text,
    p_event_id text
)
LANGUAGE plpgsql
SECURITY INVOKER
AS $procedure$
DECLARE
    e pro_replication_lab.outbox_events%ROWTYPE;
    event_payload_sha256 text;
BEGIN
    SELECT o.*
    INTO STRICT e
    FROM pro_replication_lab.outbox_events AS o
    WHERE o.event_id = p_event_id
    FOR UPDATE;

    event_payload_sha256 := encode(
        sha256(e.payload::text::bytea),
        'hex'
    );

    INSERT INTO pro_replication_lab.inbox (
        consumer_name,
        event_id,
        payload_sha256
    )
    VALUES (p_consumer, e.event_id, event_payload_sha256)
    ON CONFLICT DO NOTHING;

    IF FOUND THEN
        INSERT INTO pro_replication_lab.projection (
            consumer_name, aggregate_key, aggregate_version, status
        )
        VALUES (
            p_consumer,
            e.aggregate_key,
            e.aggregate_version,
            e.payload ->> 'status'
        )
        ON CONFLICT (consumer_name, aggregate_key) DO UPDATE
        SET aggregate_version = EXCLUDED.aggregate_version,
            status = EXCLUDED.status
        WHERE EXCLUDED.aggregate_version
              > pro_replication_lab.projection.aggregate_version;
    ELSIF NOT EXISTS (
        SELECT 1
        FROM pro_replication_lab.inbox AS i
        WHERE i.consumer_name = p_consumer
          AND i.event_id = e.event_id
          AND i.payload_sha256 = event_payload_sha256
    ) THEN
        RAISE EXCEPTION
            'event id % was reused with a different payload',
            e.event_id
            USING ERRCODE = 'check_violation';
    END IF;

END
$procedure$;

-- Publisher acknowledgement is a separate boundary from consumer processing.
-- This local procedure stands in only for “broker accepted this event”; a
-- production publisher must call it after broker acknowledgement, not after one
-- particular consumer's side effect.
CREATE PROCEDURE pro_replication_lab.mark_published(p_event_id text)
LANGUAGE plpgsql
SECURITY INVOKER
AS $procedure$
BEGIN
    UPDATE pro_replication_lab.outbox_events AS o
    SET published = true
    WHERE o.event_id = p_event_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'unknown outbox event %', p_event_id
            USING ERRCODE = 'P0002';
    END IF;
END
$procedure$;

-- Exercise 3: out-of-order v3, then v2 must not regress.
CALL pro_replication_lab.deliver_event('projection', 'E-v3');
CALL pro_replication_lab.deliver_event('projection', 'E-v2');
CALL pro_replication_lab.deliver_event('projection', 'E-v3');
CALL pro_replication_lab.mark_published('E-v2');
CALL pro_replication_lab.mark_published('E-v3');

SELECT
    p.consumer_name,
    p.aggregate_key,
    p.aggregate_version,
    p.status
FROM pro_replication_lab.projection AS p
ORDER BY p.consumer_name, p.aggregate_key;

WITH source_versions AS (
    SELECT
        o.aggregate_key,
        array_agg(o.aggregate_version ORDER BY o.aggregate_version)
            AS expected_versions
    FROM pro_replication_lab.outbox_events AS o
    GROUP BY o.aggregate_key
),
accepted_versions AS (
    SELECT
        o.aggregate_key,
        array_agg(o.aggregate_version ORDER BY o.aggregate_version)
            AS accepted_versions
    FROM pro_replication_lab.inbox AS i
    JOIN pro_replication_lab.outbox_events AS o
      ON o.event_id = i.event_id
    WHERE i.consumer_name = 'projection'
    GROUP BY o.aggregate_key
)
SELECT
    sv.aggregate_key,
    sv.expected_versions,
    COALESCE(av.accepted_versions, ARRAY[]::integer[]) AS accepted_versions,
    ARRAY(
        SELECT expected.version
        FROM unnest(sv.expected_versions) AS expected(version)
        WHERE NOT expected.version = ANY (
            COALESCE(av.accepted_versions, ARRAY[]::integer[])
        )
        ORDER BY expected.version
    ) AS missing_versions
FROM source_versions AS sv
LEFT JOIN accepted_versions AS av
  ON av.aggregate_key = sv.aggregate_key
ORDER BY sv.aggregate_key;

DO $solution$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pro_replication_lab.projection AS p
        WHERE p.aggregate_key = 'ORDER-1'
          AND p.aggregate_version = 3
          AND p.status = 'cancelled'
    ) THEN
        RAISE EXCEPTION 'out-of-order delivery regressed projection';
    END IF;
    IF (
        SELECT COUNT(*)
        FROM pro_replication_lab.inbox AS i
        WHERE i.consumer_name = 'projection'
    ) <> 2 THEN
        RAISE EXCEPTION 'redelivery bypassed inbox idempotency';
    END IF;
    IF NOT EXISTS (
        SELECT 1
        FROM pro_replication_lab.outbox_events AS source_event
        WHERE source_event.aggregate_key = 'ORDER-1'
          AND source_event.aggregate_version = 1
          AND NOT EXISTS (
              SELECT 1
              FROM pro_replication_lab.inbox AS accepted
              WHERE accepted.consumer_name = 'projection'
                AND accepted.event_id = source_event.event_id
          )
    ) THEN
        RAISE EXCEPTION 'leading source-version gap was not detected';
    END IF;
END
$solution$;

-- Exercise 1: E-v1 models a committed business/outbox event whose publisher
-- acknowledgement was lost. It remains discoverable for retry.
SELECT
    o.event_id,
    o.aggregate_key,
    o.aggregate_version
FROM pro_replication_lab.outbox_events AS o
WHERE NOT o.published
ORDER BY o.aggregate_key, o.aggregate_version;

-- Exercise 2: the duplicate E-v3 call produced only one inbox row. An external
-- side effect also needs event_id plus a canonical request fingerprint as a
-- durable idempotency contract at the external service.
SELECT
    i.consumer_name,
    i.event_id,
    COUNT(*) AS accepted_rows
FROM pro_replication_lab.inbox AS i
GROUP BY i.consumer_name, i.event_id
ORDER BY i.consumer_name, i.event_id;

-- Exercise 4: this single-node fixture creates no replication object. Physical
-- streaming covers cluster storage/WAL; logical publications select table DML
-- and require separate DDL/sequence handling.
SELECT
    pg_catalog.pg_is_in_recovery() AS connected_to_recovery_node,
    current_setting('server_version') AS server_version;

SELECT *
FROM (
    VALUES
        ('physical streaming'::text, 'cluster WAL/block changes'::text, 'carried as physical WAL'::text, 'physical sequence state follows storage', 'HA/read replicas and whole-cluster recovery', 'same-major-version/storage compatibility and coarse filtering'),
        ('logical replication', 'selected table DML via publications', 'not replicated; subscriber schema must be compatible', 'sequence state is not replicated', 'selective data distribution and version transitions', 'DDL/sequence coordination, replica identity and apply conflicts')
) AS replication_methods(
    mechanism,
    replicated_scope,
    ddl_behavior,
    sequence_behavior,
    common_use,
    major_limit
)
ORDER BY mechanism;

-- Exercise 5: read-only slot inventory. Empty results are a valid capability
-- state; never drop a disconnected slot without consumer ownership evidence.
WITH local_position AS (
    SELECT CASE
        WHEN pg_catalog.pg_is_in_recovery()
        THEN pg_catalog.pg_last_wal_replay_lsn()
        ELSE pg_catalog.pg_current_wal_lsn()
    END AS current_or_replay_lsn
)
SELECT
    s.slot_name,
    s.slot_type,
    s.active,
    s.restart_lsn,
    s.confirmed_flush_lsn,
    CASE
        WHEN s.restart_lsn IS NULL
          OR p.current_or_replay_lsn IS NULL
        THEN NULL
        ELSE pg_catalog.pg_wal_lsn_diff(
            p.current_or_replay_lsn,
            s.restart_lsn
        )
    END AS retained_wal_bytes,
    s.wal_status,
    s.safe_wal_size
FROM pg_catalog.pg_replication_slots AS s
CROSS JOIN local_position AS p
ORDER BY s.slot_name;

SELECT *
FROM (
    VALUES
        (1, 'ownership', 'slot maps to a named consumer/service owner'),
        (2, 'progress', 'active state plus restart/flush LSN movement and last progress time'),
        (3, 'capacity', 'retained bytes, wal_status, safe_wal_size and disk budget'),
        (4, 'alert', 'warning/critical thresholds with response owner and runbook'),
        (5, 'retirement', 'consumer decommission approval, catch-up/reseed decision and backup evidence')
) AS slot_policy(check_number, check_name, required_evidence)
ORDER BY check_number;

-- Exercise 6: promotion requires quorum-aware diagnosis, old-primary fencing,
-- data-loss evidence, controlled routing, timeline/CDC verification, a new
-- replica and backup, and recorded RPO/RTO plus stop/fallback boundaries.
SELECT *
FROM (
    VALUES
        (1, 'authority and diagnosis', 'incident commander, quorum and candidate health', 'uncertain quorum or candidate'),
        (2, 'fence old primary', 'write fencing confirmed from every client path', 'old writer is reachable'),
        (3, 'data-loss decision', 'candidate replay position and RPO evidence', 'loss exceeds approved RPO'),
        (4, 'promote and route', 'timeline, write smoke test, DNS/client reconnect', 'writes or routing fail'),
        (5, 'CDC and redundancy', 'slots/subscriptions reconciled; new replica and backup', 'CDC lineage or backup incomplete'),
        (6, 'close and audit', 'achieved RPO/RTO, gaps, owners and fallback record', 'unowned unresolved risk')
) AS failover_runbook(step_number, phase, required_evidence, stop_condition)
ORDER BY step_number;

-- Exercise 7: publication scope needs row/column leak tests and an UPDATE/DELETE
-- replica identity. The local table's primary key is the intended identity.
SELECT
    n.nspname AS schema_name,
    rel.relname AS table_name,
    CASE rel.relreplident
        WHEN 'd' THEN 'default'
        WHEN 'n' THEN 'nothing'
        WHEN 'f' THEN 'full'
        WHEN 'i' THEN 'index'
    END AS replica_identity
FROM pg_catalog.pg_class AS rel
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = rel.relnamespace
WHERE n.nspname = 'pro_replication_lab'
  AND rel.relname = 'outbox';

SELECT *
FROM (
    VALUES
        (1, 'published relation', 'schema/table, explicit columns and row filter'),
        (2, 'replica identity', 'UPDATE/DELETE key is present and published'),
        (3, 'initial copy', 'snapshot boundary and row/column filter evidence'),
        (4, 'leak tests', 'allowed, denied, NULL and UPDATE-transition cases'),
        (5, 'compatibility', 'subscriber schema, DDL and sequence plan')
) AS publication_review(check_number, check_name, required_evidence)
ORDER BY check_number;

-- Exercise 8: a consistent bootstrap owns one exported snapshot/start LSN,
-- initial copy, stream handoff, durable checkpoint, WAL budget, retry, and
-- abandoned-slot cleanup record.
SELECT *
FROM (
    VALUES
        (1, 'create slot and export snapshot'::text),
        (2, 'copy under snapshot and record progress'),
        (3, 'consume from matching LSN with idempotency'),
        (4, 'verify handoff, then release bootstrap resources')
) AS bootstrap(step_number, required_evidence)
ORDER BY step_number;

-- Exercise 9: read-your-write should use transaction visibility evidence such
-- as a commit/replay LSN token, not byte lag alone.
SELECT
    CASE
        WHEN pg_catalog.pg_is_in_recovery()
        THEN pg_catalog.pg_last_wal_replay_lsn()
        ELSE pg_catalog.pg_current_wal_lsn()
    END AS local_visibility_lsn;

SELECT *
FROM (
    VALUES
        ('primary pinning'::text, 'route reads to writer for a bounded session', 'higher primary load'),
        ('LSN token wait', 'wait until replica replay reaches commit token', 'requires timeout and fallback'),
        ('bounded staleness', 'accept age/position budget by endpoint', 'not strict read-your-write'),
        ('fallback', 'route to primary or return explicit retry result', 'must be observable and bounded')
) AS consistency_strategies(strategy, contract, tradeoff)
ORDER BY strategy;

-- Exercise 10: wall-clock last-write-wins is unsafe under skew. Prefer one
-- writer per key; otherwise use expected versions, deterministic merge, or
-- quarantine with canonical snapshot/replay repair and an audit.
SELECT
    p.consumer_name,
    p.aggregate_key,
    p.aggregate_version,
    p.status
FROM pro_replication_lab.projection AS p
ORDER BY p.consumer_name, p.aggregate_key;

SELECT *
FROM (
    VALUES
        ('single writer per key'::text, 'ownership/lease or routing proof', 'prevents concurrent authorities'),
        ('expected version', 'compare-and-set against aggregate version', 'rejects stale write for retry'),
        ('deterministic merge', 'domain-specific associative/commutative rule', 'only for fields with proved merge semantics'),
        ('quarantine and repair', 'retain both events plus audit and canonical replay', 'manual or automated repair path')
) AS conflict_strategies(strategy, required_evidence, behavior)
ORDER BY strategy;

-- Exercise 11: DDL uses an explicit compatibility sequence outside logical
-- replication, with publisher/subscriber/application checks at every phase.
SELECT *
FROM (
    VALUES
        (1, 'expand'::text, 'nullable/additive on compatible endpoints'::text),
        (2, 'deploy', 'tolerant readers and dual-compatible writers'),
        (3, 'backfill', 'reconcile before validating constraints'),
        (4, 'contract', 'remove only after all consumers stop old shape')
) AS ddl_matrix(step_number, phase, compatibility_gate)
ORDER BY step_number;

-- Exercise 12: failback/reseed begins with a protected new-primary backup and a
-- fenced former primary, then chooses rewind or rebuild from timeline/WAL
-- evidence and revalidates data, slots, subscriptions, routing, backup, and HA.
SELECT *
FROM (
    VALUES
        (1, 'protect new primary', 'verified backup plus current timeline/LSN evidence'),
        (2, 'keep former primary fenced', 'no write/client path reaches it'),
        (3, 'choose rewind or rebuild', 'timeline divergence, WAL and compatibility evidence'),
        (4, 'reseed and validate', 'data checks plus slots/subscriptions rebuilt or reconciled'),
        (5, 'restore routing/redundancy', 'clients, replica, backup and monitoring pass'),
        (6, 'audit and stop boundary', 'owners, achieved RPO/RTO, gaps and rollback decision')
) AS failback_plan(step_number, phase, required_evidence)
ORDER BY step_number;

ROLLBACK;
