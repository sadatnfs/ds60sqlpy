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

CREATE TABLE pro_replication_lab.outbox (
    event_id text PRIMARY KEY,
    aggregate_key text NOT NULL,
    aggregate_version integer NOT NULL,
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

INSERT INTO pro_replication_lab.outbox
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
    e pro_replication_lab.outbox%ROWTYPE;
    event_payload_sha256 text;
BEGIN
    SELECT o.*
    INTO STRICT e
    FROM pro_replication_lab.outbox AS o
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

    UPDATE pro_replication_lab.outbox AS o
    SET published = true
    WHERE o.event_id = e.event_id;
END
$procedure$;

-- Exercise 3: out-of-order v3, then v2 must not regress.
CALL pro_replication_lab.deliver_event('projection', 'E-v3');
CALL pro_replication_lab.deliver_event('projection', 'E-v2');
CALL pro_replication_lab.deliver_event('projection', 'E-v3');

SELECT
    p.consumer_name,
    p.aggregate_key,
    p.aggregate_version,
    p.status
FROM pro_replication_lab.projection AS p
ORDER BY p.consumer_name, p.aggregate_key;

WITH accepted_versions AS (
    SELECT
        o.aggregate_key,
        array_agg(o.aggregate_version ORDER BY o.aggregate_version) AS versions
    FROM pro_replication_lab.inbox AS i
    JOIN pro_replication_lab.outbox AS o
      ON o.event_id = i.event_id
    WHERE i.consumer_name = 'projection'
    GROUP BY o.aggregate_key
)
SELECT
    av.aggregate_key,
    av.versions,
    (
        SELECT array_agg(v ORDER BY v)
        FROM generate_series(
            av.versions[1],
            av.versions[cardinality(av.versions)]
        ) AS v
    ) AS expected_contiguous_versions
FROM accepted_versions AS av
ORDER BY av.aggregate_key;

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
END
$solution$;

-- Exercise 1: E-v1 models a committed business/outbox event whose publisher
-- acknowledgement was lost. It remains discoverable for retry.
SELECT
    o.event_id,
    o.aggregate_key,
    o.aggregate_version
FROM pro_replication_lab.outbox AS o
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

-- Exercise 5: read-only slot inventory. Empty results are a valid capability
-- state; never drop a disconnected slot without consumer ownership evidence.
SELECT
    s.slot_name,
    s.slot_type,
    s.active,
    s.restart_lsn,
    s.confirmed_flush_lsn
FROM pg_catalog.pg_replication_slots AS s
ORDER BY s.slot_name;

-- Exercise 6: promotion requires quorum-aware diagnosis, old-primary fencing,
-- data-loss evidence, controlled routing, timeline/CDC verification, a new
-- replica and backup, and recorded RPO/RTO plus stop/fallback boundaries.

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

-- Exercise 10: wall-clock last-write-wins is unsafe under skew. Prefer one
-- writer per key; otherwise use expected versions, deterministic merge, or
-- quarantine with canonical snapshot/replay repair and an audit.
SELECT
    p.aggregate_key,
    p.aggregate_version,
    p.status
FROM pro_replication_lab.projection AS p
ORDER BY p.aggregate_key;

-- Exercise 11: DDL uses an explicit compatibility sequence outside logical
-- replication, with publisher/subscriber/application checks at every phase.
SELECT *
FROM (
    VALUES
        ('expand'::text, 'nullable/additive on compatible endpoints'::text),
        ('deploy', 'tolerant readers and dual-compatible writers'),
        ('backfill', 'reconcile before validating constraints'),
        ('contract', 'remove only after all consumers stop old shape')
) AS ddl_matrix(phase, compatibility_gate)
ORDER BY phase;

-- Exercise 12: failback/reseed begins with a protected new-primary backup and a
-- fenced former primary, then chooses rewind or rebuild from timeline/WAL
-- evidence and revalidates data, slots, subscriptions, routing, backup, and HA.

ROLLBACK;
