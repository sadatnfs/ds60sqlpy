-- SQL-REPL-01 executable solutions: local simulation only.
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

ROLLBACK;
