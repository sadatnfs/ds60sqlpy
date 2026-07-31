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
--    Inputs: For sql-repl-01 Exercise 1, read from `pro_replication_lab.outbox`. Build the answer toward `event_id`, `aggregate_key`, and `aggregate_version`; keep `event_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-repl-01 Exercise 1, expected output: one row per `event_id`. The final columns are `event_id`, `aggregate_key`, and `aggregate_version`. The final order is `o.aggregate_key, o.aggregate_version`.
--    Verify: For sql-repl-01 Exercise 1, run an anti-check that counts rows where NOT ((NOT o.published)); require unique `event_id` where the expected grain is one row per key and confirm the projected `event_id`, `aggregate_key`, and `aggregate_version` against `pro_replication_lab.outbox`. Add one row for which `(NOT o.published)` is true and one for which it is false; verify only the matching `event_id` value is returned.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 1, inspect the source keys that survive `WHERE`; then check `o.aggregate_key, o.aggregate_version` before applying the row cap.
-- 2. Simulate consumer redelivery after an external side effect but before
--    acknowledgement. Explain why an inbox transaction works only when the
--    effect shares its database; design an idempotency key for an external API.
--    Inputs: For sql-repl-01 Exercise 2, read from `pro_replication_lab.inbox`. Build the answer toward `consumer_name`, `event_id`, and `accepted_rows`; keep `consumer_name`, and `event_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-repl-01 Exercise 2, expected output: one row per `consumer_name`, and `event_id`. The final columns are `consumer_name`, `event_id`, and `accepted_rows`. The final order is `i.consumer_name, i.event_id`.
--    Verify: For sql-repl-01 Exercise 2, independently aggregate `pro_replication_lab.inbox` by `consumer_name`, and `event_id`; require one output row for every distinct `consumer_name`, and `event_id` tuple and compare `accepted_rows` tuple by tuple. Add duplicate source candidates for `consumer_name`, and `event_id`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 2, confirm the groups are `consumer_name`, and `event_id`; then check `i.consumer_name, i.event_id` before applying the row cap.
-- 3. Deliver aggregate version 3 before version 2 to a fresh consumer and prove
--    the projection never regresses. Define how gaps are detected/repaired.
--    Inputs: For sql-repl-01 Exercise 3, read from `pro_replication_lab.projection`, `pro_replication_lab.inbox`, and `pro_replication_lab.outbox`. Build the answer toward `consumer_name`, `aggregate_key`, `aggregate_version`, and `status`; keep `status` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-repl-01 Exercise 3, expected output: one row per `status`. The final columns are `consumer_name`, `aggregate_key`, `aggregate_version`, and `status`. The final order is `av.aggregate_key`.
--    Verify: For sql-repl-01 Exercise 3, project `status` plus the raw source columns from `pro_replication_lab.projection`, `pro_replication_lab.inbox`, and `pro_replication_lab.outbox` at each join stage; record row count and distinct `status`, then assert the final `consumer_name`, `aggregate_key`, `aggregate_version`, and `status` values match those staged rows without unintended fanout or loss. Add one source row with a new `status`; verify the result gains exactly one row carrying that `status` value.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 3, run `accepted_versions` one at a time. Record each CTE's row count and `status` uniqueness before the next stage uses it.
-- 4. Explain physical streaming versus logical replication/publications, and
--    whether schema DDL and sequences are replicated by the chosen mechanism.
--    Inputs: For sql-repl-01 Exercise 4, read from `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription`. Compute `connected_to_recovery_node`, and `server_version` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-repl-01 Exercise 4, expected output: exactly one aggregate summary row. The final columns are `connected_to_recovery_node`, and `server_version`.
--    Verify: For sql-repl-01 Exercise 4, evaluate each of `server_version` in a separate control `SELECT` over `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription`; require one final row and compare every value. Add one source row with a new `connected_to_recovery_node`; verify the result gains exactly one row carrying that `connected_to_recovery_node` value.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 4, select `connected_to_recovery_node` from `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` before adding derived columns.
-- 5. Design slot monitoring around retained WAL bytes, active state, consumer
--    lag, disk budget, alert threshold, and safe slot retirement. Never drop a
--    slot merely because its consumer is temporarily disconnected.
--    Inputs: For sql-repl-01 Exercise 5, read from `pg_catalog.pg_replication_slots`. Build the answer toward `slot_name`, `slot_type`, `active`, `restart_lsn`, and `confirmed_flush_lsn`; keep `slot_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-repl-01 Exercise 5, expected output: one row per `slot_name`. The final columns are `slot_name`, `slot_type`, `active`, `restart_lsn`, and `confirmed_flush_lsn`. The final order is `s.slot_name`.
--    Verify: For sql-repl-01 Exercise 5, reselect the returned keys directly from the source; require unique `slot_name` where the expected grain is one row per key and confirm the projected `slot_name`, `slot_type`, `active`, `restart_lsn`, and `confirmed_flush_lsn` against `pg_catalog.pg_replication_slots`. Add one source row with a new `slot_name`; verify the result gains exactly one row carrying that `slot_name` value.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 5, check `s.slot_name` before applying the row cap.
-- 6. Write a failover runbook covering health/quorum, fencing the old primary,
--    data-loss evidence, DNS/client reconnect, timeline, slot/subscriber state,
--    RPO/RTO, rollback, and post-failover backups.
--    Inputs: For sql-repl-01 Exercise 6, use `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-repl-01 Exercise 6, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
--    Verify: For sql-repl-01 Exercise 6, restore into an isolated target and reconcile `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 6, restore into an isolated target and reconcile `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
-- 7. Design a logical publication for one table with a row filter and column
--    list. Explain replica identity for UPDATE/DELETE, unsupported schema
--    changes, sequence state, initial copy, and how to prove no tenant leaks.
--    Inputs: For sql-repl-01 Exercise 7, read from `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`. Build the answer toward `schema_name`, `table_name`, and `replica_identity`; keep `schema_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-repl-01 Exercise 7, expected output: one row per `schema_name`. The final columns are `schema_name`, `table_name`, and `replica_identity`.
--    Verify: For sql-repl-01 Exercise 7, project `schema_name` plus the raw source columns from `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` at each join stage; record row count and distinct `schema_name`, then assert the final `schema_name`, `table_name`, and `replica_identity` values match those staged rows without unintended fanout or loss. Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 7, start with the first relation in `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `schema_name` so the exact fanout or loss is visible.
-- 8. Document a consistent snapshot-to-stream bootstrap. Relate exported
--    snapshot, start LSN, replication slot, initial copy, handoff, deduplication,
--    restart, WAL retention, and cleanup after an abandoned bootstrap.
--    Inputs: For sql-repl-01 Exercise 8, read from `matching`. Build the answer toward `step_number`, and `required_evidence`; keep `step_number` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-repl-01 Exercise 8, expected output: one row per `step_number`. The final columns are `step_number`, and `required_evidence`. The final order is `step_number`.
--    Verify: For sql-repl-01 Exercise 8, reselect the returned keys directly from the source; require unique `step_number` where the expected grain is one row per key and confirm the projected `step_number`, and `required_evidence` against `matching`. Add one source row with a new `step_number`; verify the result gains exactly one row carrying that `step_number` value.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 8, check `step_number` before applying the row cap.
-- 9. Specify a read-after-write contract for traffic sent to replicas. Compare
--    primary pinning, LSN tokens/waits, bounded staleness, session guarantees,
--    timeout fallback, and what lag metric users actually experience.
--    Inputs: For sql-repl-01 Exercise 9, read from `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription`. Compute `local_visibility_lsn` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-repl-01 Exercise 9, expected output: exactly one aggregate summary row. The final columns are `local_visibility_lsn`.
--    Verify: For sql-repl-01 Exercise 9, evaluate each of `row_count` in a separate control `SELECT` over `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription`; require one final row and compare every value. Add one source row with a new `local_visibility_lsn`; verify the result gains exactly one row carrying that `local_visibility_lsn` value.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 9, select `local_visibility_lsn` from `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` before adding derived columns.
-- 10. Design conflict handling for accidental multi-writer topology. Explain
--     why wall-clock last-write-wins is unsafe, and compare single-writer
--     ownership, version checks, deterministic merge, quarantine, and repair.
--    Inputs: For sql-repl-01 Exercise 10, read the target keys from `pro_replication_lab.projection` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-repl-01 Exercise 10, expected output: the command tag and an independently counted set of affected `status` values. The final columns are `aggregate_key`, `aggregate_version`, and `status`. The final order is `p.aggregate_key`.
--    Verify: For sql-repl-01 Exercise 10, materialize the intended `status` target set first; require the command tag/`RETURNING` set to match it, then query `pro_replication_lab.projection` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `status` values in both cases.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 10, materialize the intended `status` target set first; require the command tag/`RETURNING` set to match it, then query `pro_replication_lab.projection` again and prove rollback or idempotent retry.
-- 11. Create a DDL compatibility matrix for publisher/subscriber versions.
--     Sequence additive columns, defaults, constraints, type changes, indexes,
--     application deployments, validation, and removal without stopping CDC.
--    Inputs: For sql-repl-01 Exercise 11, read from the inline `VALUES` fixture. Build the answer toward `phase`, and `compatibility_gate`; keep `phase` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-repl-01 Exercise 11, expected output: one row per `phase`. The final columns are `phase`, and `compatibility_gate`. The final order is `phase`.
--    Verify: For sql-repl-01 Exercise 11, reselect the returned keys directly from the source; require unique `phase` where the expected grain is one row per key and confirm the projected `phase`, and `compatibility_gate` against the inline `VALUES` fixture. Add one source row with a new `phase`; verify the result gains exactly one row carrying that `phase` value.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 11, check `phase` before applying the row cap.
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
--    Inputs: For sql-repl-01 Exercise 12, use `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-repl-01 Exercise 12, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
--    Verify: For sql-repl-01 Exercise 12, restore into an isolated target and reconcile `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-repl-01 Exercise 12, restore into an isolated target and reconcile `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.

ROLLBACK;
\echo 'SQL-REPL-01 complete: no replication object was created'
