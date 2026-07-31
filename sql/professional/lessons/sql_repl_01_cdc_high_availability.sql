-- SQL-REPL-01: Replication, CDC, and high availability
-- BEGINNER WORKFLOW — sql-repl-01: Replication, Change Data Capture, and High Availability
-- Guide: sql/professional/companion-guides/sql_repl_01_cdc_high_availability.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-repl-01/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Target: PostgreSQL 16+
-- Default path is one-database outbox/idempotency simulation plus read-only
-- capability inspection. It creates no publication, subscription, or slot.

\set ON_ERROR_STOP on
\echo 'SQL-REPL-01: read-only replication capability summary'
SELECT
    current_database() AS database_name,
    current_setting('wal_level') AS wal_level,
    current_setting('max_wal_senders') AS max_wal_senders,
    current_setting('max_replication_slots') AS max_replication_slots,
    current_setting('hot_standby') AS hot_standby,
    pg_catalog.pg_is_in_recovery() AS is_in_recovery;

SELECT
    (SELECT COUNT(*) FROM pg_catalog.pg_replication_slots) AS slot_count,
    (
        SELECT COUNT(*)
        FROM pg_catalog.pg_replication_slots AS s
        WHERE s.active
    ) AS active_slot_count,
    (SELECT COUNT(*) FROM pg_catalog.pg_publication) AS publication_count,
    (SELECT COUNT(*) FROM pg_catalog.pg_subscription) AS subscription_count,
    (SELECT COUNT(*) FROM pg_catalog.pg_stat_replication) AS sender_count,
    (SELECT COUNT(*) FROM pg_catalog.pg_stat_wal_receiver) AS receiver_count;

\echo 'SQL-REPL-01: disposable transactional outbox lab'
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_replication_lab;

CREATE TABLE pro_replication_lab.orders (
    order_key text PRIMARY KEY,
    status text NOT NULL CHECK (status IN ('open', 'paid', 'cancelled')),
    aggregate_version integer NOT NULL CHECK (aggregate_version > 0),
    updated_at timestamptz NOT NULL
);

CREATE TABLE pro_replication_lab.outbox_events (
    event_id text PRIMARY KEY,
    aggregate_type text NOT NULL,
    aggregate_key text NOT NULL,
    aggregate_version integer NOT NULL CHECK (aggregate_version > 0),
    event_type text NOT NULL,
    payload jsonb NOT NULL CHECK (jsonb_typeof(payload) = 'object'),
    occurred_at timestamptz NOT NULL,
    published_at timestamptz,
    delivery_attempts integer NOT NULL DEFAULT 0 CHECK (delivery_attempts >= 0),
    UNIQUE (aggregate_type, aggregate_key, aggregate_version)
);

CREATE TABLE pro_replication_lab.consumer_inbox (
    consumer_name text NOT NULL,
    event_id text NOT NULL,
    accepted_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    payload_sha256 text NOT NULL CHECK (
        payload_sha256 ~ '^[0-9a-f]{64}$'
    ),
    PRIMARY KEY (consumer_name, event_id)
);

CREATE TABLE pro_replication_lab.projected_orders (
    consumer_name text NOT NULL,
    order_key text NOT NULL,
    status text NOT NULL,
    aggregate_version integer NOT NULL,
    last_event_id text NOT NULL,
    PRIMARY KEY (consumer_name, order_key)
);

-- Business state and event are committed by the same database transaction.
INSERT INTO pro_replication_lab.orders (
    order_key, status, aggregate_version, updated_at
)
VALUES (
    'ORD-100',
    'open',
    1,
    TIMESTAMPTZ '2026-06-01 10:00:00+00'
);

INSERT INTO pro_replication_lab.outbox_events (
    event_id,
    aggregate_type,
    aggregate_key,
    aggregate_version,
    event_type,
    payload,
    occurred_at
)
VALUES (
    'EVT-100-v1',
    'order',
    'ORD-100',
    1,
    'order.opened',
    '{"order_key":"ORD-100","status":"open"}',
    TIMESTAMPTZ '2026-06-01 10:00:00+00'
);

UPDATE pro_replication_lab.orders AS o
SET status = 'paid',
    aggregate_version = 2,
    updated_at = TIMESTAMPTZ '2026-06-01 10:05:00+00'
WHERE o.order_key = 'ORD-100';

INSERT INTO pro_replication_lab.outbox_events (
    event_id,
    aggregate_type,
    aggregate_key,
    aggregate_version,
    event_type,
    payload,
    occurred_at
)
VALUES (
    'EVT-100-v2',
    'order',
    'ORD-100',
    2,
    'order.paid',
    '{"order_key":"ORD-100","status":"paid"}',
    TIMESTAMPTZ '2026-06-01 10:05:00+00'
);

CREATE PROCEDURE pro_replication_lab.consume_outbox_batch(
    p_consumer_name text,
    p_batch_size integer
)
LANGUAGE plpgsql
SECURITY INVOKER
AS $procedure$
DECLARE
    event_row pro_replication_lab.outbox_events%ROWTYPE;
    event_payload_sha256 text;
BEGIN
    IF p_consumer_name IS NULL OR btrim(p_consumer_name) = '' THEN
        RAISE EXCEPTION 'consumer name must not be blank'
            USING ERRCODE = 'check_violation';
    END IF;
    IF p_batch_size < 1 OR p_batch_size > 1000 THEN
        RAISE EXCEPTION 'batch size must be between 1 and 1000'
            USING ERRCODE = 'check_violation';
    END IF;

    FOR event_row IN
        SELECT oe.*
        FROM pro_replication_lab.outbox_events AS oe
        WHERE oe.published_at IS NULL
        ORDER BY
            oe.occurred_at,
            oe.aggregate_key,
            oe.aggregate_version,
            oe.event_id
        FOR UPDATE SKIP LOCKED
        LIMIT p_batch_size
    LOOP
        event_payload_sha256 := encode(
            sha256(event_row.payload::text::bytea),
            'hex'
        );

        INSERT INTO pro_replication_lab.consumer_inbox (
            consumer_name,
            event_id,
            payload_sha256
        )
        VALUES (
            p_consumer_name,
            event_row.event_id,
            event_payload_sha256
        )
        ON CONFLICT (consumer_name, event_id) DO NOTHING;

        -- FOUND is true only when this consumer accepted the event for the first
        -- time. Redelivery therefore does not repeat the projection side effect.
        IF FOUND THEN
            INSERT INTO pro_replication_lab.projected_orders (
                consumer_name,
                order_key,
                status,
                aggregate_version,
                last_event_id
            )
            VALUES (
                p_consumer_name,
                event_row.aggregate_key,
                event_row.payload ->> 'status',
                event_row.aggregate_version,
                event_row.event_id
            )
            ON CONFLICT (consumer_name, order_key) DO UPDATE
            SET status = EXCLUDED.status,
                aggregate_version = EXCLUDED.aggregate_version,
                last_event_id = EXCLUDED.last_event_id
            WHERE EXCLUDED.aggregate_version
                  > pro_replication_lab.projected_orders.aggregate_version;
        ELSIF NOT EXISTS (
            SELECT 1
            FROM pro_replication_lab.consumer_inbox AS ci
            WHERE ci.consumer_name = p_consumer_name
              AND ci.event_id = event_row.event_id
              AND ci.payload_sha256 = event_payload_sha256
        ) THEN
            RAISE EXCEPTION
                'event id % was reused with a different payload',
                event_row.event_id
                USING ERRCODE = 'check_violation';
        END IF;

        UPDATE pro_replication_lab.outbox_events AS oe
        SET published_at = clock_timestamp(),
            delivery_attempts = oe.delivery_attempts + 1
        WHERE oe.event_id = event_row.event_id;
    END LOOP;
END
$procedure$;

\echo 'First at-least-once delivery: consumer accepts two unique events'
CALL pro_replication_lab.consume_outbox_batch('order_projection', 10);

SELECT
    po.consumer_name,
    po.order_key,
    po.status,
    po.aggregate_version,
    po.last_event_id
FROM pro_replication_lab.projected_orders AS po
ORDER BY po.consumer_name, po.order_key;

DO $expected_payload_conflict$
BEGIN
    BEGIN
        UPDATE pro_replication_lab.outbox_events
        SET payload = '{"order_key":"ORD-100","status":"cancelled"}',
            published_at = NULL
        WHERE event_id = 'EVT-100-v1';

        CALL pro_replication_lab.consume_outbox_batch(
            'order_projection',
            10
        );
        RAISE EXCEPTION 'event-id payload conflict unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected idempotency-payload rejection: %', SQLERRM;
    END;
END
$expected_payload_conflict$;

\echo 'Simulated redelivery: inbox key prevents repeated side effects'
UPDATE pro_replication_lab.outbox_events
SET published_at = NULL;

CALL pro_replication_lab.consume_outbox_batch('order_projection', 10);

SELECT
    oe.event_id,
    oe.aggregate_version,
    oe.delivery_attempts,
    (oe.published_at IS NOT NULL) AS acknowledged
FROM pro_replication_lab.outbox_events AS oe
ORDER BY oe.aggregate_key, oe.aggregate_version, oe.event_id;

SELECT
    ci.consumer_name,
    COUNT(*) AS accepted_unique_events
FROM pro_replication_lab.consumer_inbox AS ci
GROUP BY ci.consumer_name
ORDER BY ci.consumer_name;

-- Exercises:
--
-- 1. Simulate a process crash after the business transaction commits but before
--    publication. Prove the unpublished outbox event remains discoverable.
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Simulate consumer redelivery after an external side effect but before
--    acknowledgement. Explain why an inbox transaction works only when the
--    effect shares its database; design an idempotency key for an external API.
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 3. Deliver aggregate version 3 before version 2 to a fresh consumer and prove
--    the projection never regresses. Define how gaps are detected/repaired.
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 4. Explain physical streaming versus logical replication/publications, and
--    whether schema DDL and sequences are replicated by the chosen mechanism.
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 5. Design slot monitoring around retained WAL bytes, active state, consumer
--    lag, disk budget, alert threshold, and safe slot retirement. Never drop a
--    slot merely because its consumer is temporarily disconnected.
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 6. Write a failover runbook covering health/quorum, fencing the old primary,
--    data-loss evidence, DNS/client reconnect, timeline, slot/subscriber state,
--    RPO/RTO, rollback, and post-failover backups.
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 7. Design a logical publication for one table with a row filter and column
--    list. Explain replica identity for UPDATE/DELETE, unsupported schema
--    changes, sequence state, initial copy, and how to prove no tenant leaks.
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 8. Document a consistent snapshot-to-stream bootstrap. Relate exported
--    snapshot, start LSN, replication slot, initial copy, handoff, deduplication,
--    restart, WAL retention, and cleanup after an abandoned bootstrap.
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 9. Specify a read-after-write contract for traffic sent to replicas. Compare
--    primary pinning, LSN tokens/waits, bounded staleness, session guarantees,
--    timeout fallback, and what lag metric users actually experience.
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 10. Design conflict handling for accidental multi-writer topology. Explain
--     why wall-clock last-write-wins is unsafe, and compare single-writer
--     ownership, version checks, deterministic merge, quarantine, and repair.
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 11. Create a DDL compatibility matrix for publisher/subscriber versions.
--     Sequence additive columns, defaults, constraints, type changes, indexes,
--     application deployments, validation, and removal without stopping CDC.
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 12. Write failback/reseed steps after promotion. Cover new-primary backup,
--     old-primary fencing, timeline divergence, rewind or rebuild choice,
--     replication slots, subscriptions, client routing, data checks, and audit.

DO $self_check$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM pro_replication_lab.consumer_inbox AS ci
        WHERE ci.consumer_name = 'order_projection'
    ) <> 2 THEN
        RAISE EXCEPTION 'idempotent inbox accepted a duplicate event';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pro_replication_lab.projected_orders AS po
        WHERE po.consumer_name = 'order_projection'
          AND po.order_key = 'ORD-100'
          AND po.status = 'paid'
          AND po.aggregate_version = 2
    ) THEN
        RAISE EXCEPTION 'order projection is not at latest aggregate version';
    END IF;
END
$self_check$;
--    Inputs: Use only the declared lesson objects (pg_catalog.pg_replication_slots, pg_catalog.pg_publication, pg_catalog.pg_subscription, pg_catalog.pg_stat_replication, pg_catalog.pg_stat_wal_receiver) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
\echo 'SQL-REPL-01 complete: no replication object was created'
