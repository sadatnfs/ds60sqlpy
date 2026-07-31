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
--    Inputs: For sql-repl-01 Exercise 1, Insert business state and its row in `pro_replication_lab.outbox_events` in one transaction, commit, and leave `published_at` NULL to represent a crash before publisher acknowledgement.
--    Expected result/shape: For sql-repl-01 Exercise 1, One row per unpublished `event_id`, with `event_id`, `aggregate_key`, and `aggregate_version`, ordered by `aggregate_key, aggregate_version, event_id`.
--    Verify: For sql-repl-01 Exercise 1, Query only `published_at IS NULL`, require unique `event_id`, and prove the committed event remains after a new session connects. Mark a different event published in a savepoint and prove it leaves this result. Hint ladder, rung 1: The durable outbox row—not process memory—is what lets a publisher retry after a crash.
-- 2. Simulate consumer redelivery after an external side effect but before
--    acknowledgement. Explain why an inbox transaction works only when the
--    effect shares its database; design an idempotency key for an external API.
--    Inputs: For sql-repl-01 Exercise 2, Deliver the same event twice to one consumer. Use `(consumer_name, event_id)` as the inbox key and retain a canonical payload hash; describe a separate idempotency key for any external API effect.
--    Expected result/shape: For sql-repl-01 Exercise 2, One row per `(consumer_name, event_id)`, with `consumer_name`, `event_id`, and `accepted_rows`, ordered by both keys; every `accepted_rows` value is 1.
--    Verify: For sql-repl-01 Exercise 2, The duplicate call leaves one inbox row and one database projection effect. Reuse the event ID with different payload and prove SQLSTATE `23514`; explain that an external API must persist/replay the same idempotency key because the local inbox cannot roll that effect back. Hint ladder, rung 1: Duplicate delivery is expected; idempotency means the same logical effect is accepted once, not that the broker sends once.
-- 3. Deliver aggregate version 3 before version 2 to a fresh consumer and prove
--    the projection never regresses. Define how gaps are detected/repaired.
--    Inputs: For sql-repl-01 Exercise 3, Deliver version 3, then version 2, then redeliver version 3 for `ORDER-1`. Compare consumer inbox versions with the authoritative outbox sequence, whose valid sequence begins at version 1.
--    Expected result/shape: For sql-repl-01 Exercise 3, The projection result has one row per `(consumer_name, aggregate_key)`, with `consumer_name`, `aggregate_key`, `aggregate_version`, and `status`. A second result has one row per `aggregate_key`, with `expected_versions`, `accepted_versions`, and `missing_versions`; it reports missing version 1.
--    Verify: For sql-repl-01 Exercise 3, Projection remains at version 3/cancelled after version 2 arrives. The gap diagnostic must compare against the source sequence, not generate only from the minimum accepted version; after version 1 is accepted, `missing_versions` becomes empty. Hint ladder, rung 1: Monotonic projection updates prevent regression but do not prove the consumer saw every earlier event.
-- 4. Explain physical streaming versus logical replication/publications, and
--    whether schema DDL and sequences are replicated by the chosen mechanism.
--    Inputs: For sql-repl-01 Exercise 4, Read local `pg_is_in_recovery()` and `server_version`, then build a comparison matrix for physical streaming and logical replication.
--    Expected result/shape: For sql-repl-01 Exercise 4, Exactly one local capability row with `connected_to_recovery_node` and `server_version`. The matrix has one row per mechanism and columns for replicated scope, DDL, sequence state, filtering, compatibility, failover use, and major limitation.
--    Verify: For sql-repl-01 Exercise 4, Trace each matrix claim to PostgreSQL documentation or observed catalog state. State explicitly that logical replication does not carry DDL or sequence state and schema mismatch can halt apply; no replication object is created in this lesson. Hint ladder, rung 1: Local server state is evidence about this connection; it does not reveal an unconfigured topology.
-- 5. Design slot monitoring around retained WAL bytes, active state, consumer
--    lag, disk budget, alert threshold, and safe slot retirement. Never drop a
--    slot merely because its consumer is temporarily disconnected.
--    Inputs: For sql-repl-01 Exercise 5, Read `pg_replication_slots` only; derive local current/replay LSN and retained WAL bytes from each non-NULL `restart_lsn`. Add an operations policy without creating or dropping slots.
--    Expected result/shape: For sql-repl-01 Exercise 5, Zero or one row per `slot_name`, with `slot_name`, `slot_type`, `active`, `restart_lsn`, `confirmed_flush_lsn`, `retained_wal_bytes`, `wal_status`, and `safe_wal_size`, ordered by `slot_name`. Empty output is valid on an unconfigured course server.
--    Verify: For sql-repl-01 Exercise 5, Reconcile retained bytes with `pg_wal_lsn_diff`; the policy names consumer owner, lag/disk budgets, alert thresholds, last progress, incident response, and evidence required before retirement. Never create a slot merely to make this exercise nonempty. Hint ladder, rung 1: Inactive means disconnected now; it does not prove the consumer is abandoned or the retained WAL is safe to discard.
-- 6. Write a failover runbook covering health/quorum, fencing the old primary,
--    data-loss evidence, DNS/client reconnect, timeline, slot/subscriber state,
--    RPO/RTO, rollback, and post-failover backups.
--    Inputs: For sql-repl-01 Exercise 6, Write a topology-specific failover runbook; this local transaction cannot promote or fence a server. Include authority, health/quorum, old-primary fencing, data-loss evidence, routing, reconnect, timeline, slots/subscriptions, RPO/RTO, fallback, backup, and audit.
--    Expected result/shape: For sql-repl-01 Exercise 6, One reviewed row per `step_number`, with `phase`, `action`, `required_evidence`, `stop_condition`, and `owner`.
--    Verify: For sql-repl-01 Exercise 6, Tabletop-test one unreachable-but-not-failed primary and one lagged candidate. Promotion remains blocked until fencing/quorum and data-loss evidence satisfy the runbook; after promotion, verify writes, routing, CDC state, a replacement replica, and a new protected backup. Hint ladder, rung 1: Failover without fencing can create two writers; that is a correctness incident, not merely an availability issue.
-- 7. Design a logical publication for one table with a row filter and column
--    list. Explain replica identity for UPDATE/DELETE, unsupported schema
--    changes, sequence state, initial copy, and how to prove no tenant leaks.
--    Inputs: For sql-repl-01 Exercise 7, Inspect local `pg_class`/`pg_namespace` metadata for `pro_replication_lab.outbox_events`. Separately write, but do not run, a publication DDL contract with one row filter and explicit column list.
--    Expected result/shape: For sql-repl-01 Exercise 7, One local evidence row per `(schema_name, table_name)`, with `schema_name`, `table_name`, and `replica_identity`. The design record lists published columns/filter, UPDATE/DELETE replica identity, initial copy, DDL/sequence handling, subscriber compatibility, and tenant-leak tests.
--    Verify: For sql-repl-01 Exercise 7, Prove the identity supports published UPDATE/DELETE keys and test allowed, denied, NULL, INSERT, UPDATE-transition, and DELETE cases in an approved isolated topology. The local catalog row alone does not prove publication scope or leak prevention. Hint ladder, rung 1: Schema plus table is the relation identity; schema name alone is not the output grain.
-- 8. Document a consistent snapshot-to-stream bootstrap. Relate exported
--    snapshot, start LSN, replication slot, initial copy, handoff, deduplication,
--    restart, WAL retention, and cleanup after an abandoned bootstrap.
--    Inputs: For sql-repl-01 Exercise 8, Build an inline ordered bootstrap plan connecting one exported snapshot, start LSN/slot, copy progress, stream handoff, deduplication, durable checkpoint, WAL budget, restart, and abandoned-bootstrap cleanup.
--    Expected result/shape: For sql-repl-01 Exercise 8, One row per `step_number`, with `step_number` and `required_evidence`, ordered numerically by `step_number`.
--    Verify: For sql-repl-01 Exercise 8, Each step consumes evidence produced by the prior step; the snapshot identity and start LSN remain paired. Simulate interruption before and after handoff and prove restart avoids gaps/duplicates and abandoned slots/resources are cleaned only with owner evidence. Hint ladder, rung 1: Snapshot copy and streaming overlap must share one exact boundary; two unrelated “latest” points can create gaps.
-- 9. Specify a read-after-write contract for traffic sent to replicas. Compare
--    primary pinning, LSN tokens/waits, bounded staleness, session guarantees,
--    timeout fallback, and what lag metric users actually experience.
--    Inputs: For sql-repl-01 Exercise 9, Capture the local current WAL LSN on a primary or last replay LSN on a recovery node as a visibility token; compare read-after-write strategies without claiming a replica exists.
--    Expected result/shape: For sql-repl-01 Exercise 9, Exactly one local row with `local_visibility_lsn`. A strategy matrix covers primary pinning, replica wait for token, bounded staleness/session guarantee, timeout, and fallback.
--    Verify: For sql-repl-01 Exercise 9, In an approved topology, carry the commit token to the read path and wait until the chosen replica replay position reaches it; test timeout and fallback. This local token alone is not evidence that any remote replica replayed the write. Hint ladder, rung 1: Byte lag is an operations measure; user-visible consistency asks whether a particular commit is observable.
-- 10. Design conflict handling for accidental multi-writer topology. Explain
--     why wall-clock last-write-wins is unsafe, and compare single-writer
--     ownership, version checks, deterministic merge, quarantine, and repair.
--    Inputs: For sql-repl-01 Exercise 10, Read current projection rows; compare single-writer ownership, expected-version rejection, deterministic domain merge, quarantine, and canonical snapshot/replay repair. Perform no multi-writer mutation here.
--    Expected result/shape: For sql-repl-01 Exercise 10, One row per `(consumer_name, aggregate_key)`, with `consumer_name`, `aggregate_key`, `aggregate_version`, and `status`, ordered by both identity columns. The strategy matrix names prerequisites, conflicts handled, failure mode, audit evidence, and repair.
--    Verify: For sql-repl-01 Exercise 10, Walk clock-skew and concurrent-version counterexamples; wall-clock last-write-wins must fail review. Each accepted strategy either prevents a second writer or detects/quarantines a version conflict without silently overwriting the canonical state. Hint ladder, rung 1: Version/ownership evidence is causal; unsynchronized wall-clock timestamps are not a safe conflict order.
-- 11. Create a DDL compatibility matrix for publisher/subscriber versions.
--     Sequence additive columns, defaults, constraints, type changes, indexes,
--     application deployments, validation, and removal without stopping CDC.
--    Inputs: For sql-repl-01 Exercise 11, Encode the required lifecycle order as an inline matrix: expand → deploy → backfill/validate → contract. Include publisher, subscriber, and application compatibility at every phase.
--    Expected result/shape: For sql-repl-01 Exercise 11, One row per `step_number`, with `step_number`, `phase`, and `compatibility_gate`, ordered by `step_number`—never lexicographically by phase text.
--    Verify: For sql-repl-01 Exercise 11, The numeric sequence is exactly `{1,2,3,4}` and phase array is exactly `{expand,deploy,backfill,contract}`. Test additive columns, defaults, constraints, type changes, indexes, old/new readers/writers, and rollback; logical replication's separate DDL/sequence handling is explicit. Hint ladder, rung 1: Compatibility is a time-ordered protocol, not an alphabetically sorted checklist.
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
--    Inputs: For sql-repl-01 Exercise 12, Write a topology-specific failback/reseed plan after promotion; this local SQL file cannot rewind, rebuild, route clients, or manipulate replication objects.
--    Expected result/shape: For sql-repl-01 Exercise 12, One row per `step_number`, with `phase`, `required_evidence`, `decision`, `owner`, and `stop_condition`. Cover a protected new-primary backup, old-primary fencing, timeline divergence, rewind/rebuild choice, slots/subscriptions, client routing, data checks, new redundancy/backup, and audit.
--    Verify: For sql-repl-01 Exercise 12, Tabletop both a rewind-eligible and rewind-ineligible former primary. Rejoin stays blocked until lineage/data checks pass, no client can write the fenced node, CDC state is rebuilt/reconciled, and rollback/stop authority is explicit. Hint ladder, rung 1: Failback is another migration with data-lineage risk, not simply “point traffic back.”

ROLLBACK;
\echo 'SQL-REPL-01 complete: no replication object was created'
