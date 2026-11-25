# SQL-REPL-01: Replication, CDC, and High Availability

## How to run this lesson

Start **sql-repl-01** from `./classroom` using the shared [run steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Choose **Whole SQL lesson (psql)**. The script first reads replication settings
and catalog counts on `advanced_sql_training` without changing any of them. It
then opens a transaction and builds a one-node outbox lab: an `orders` row for
`ORD-100` and two outbox events (`EVT-100-v1` open, `EVT-100-v2` paid) written
in the same transaction, a `consumer_inbox` keyed by consumer and event id, and
a `projected_orders` table. The procedure `consume_outbox_batch` delivers both
events, every event is then marked unpublished and delivered again, and the
inbox still holds 2 rows. One `NOTICE` beginning
`Expected idempotency-payload rejection` is the intended result. `ROLLBACK`
removes the schema and no slot, publication or subscription is ever created.
Save attempts in
`.learning/sql/sql-repl-01/lesson/workspace/sql/professional/lessons/sql_repl_01_cdc_high_availability.sql`.

The optional notebook route starts with `uv run --no-sync python scripts/course.py sql notebook sql-repl-01`; see the [study guide](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-ops-02`, `sql-prog-01`, and `sql-test-01`
- **Prerequisites:** [SQL-OPS-02; recovery](sql_ops_02_backup_restore_recovery.md),
  [SQL-PROG-01](sql_prog_01_routines_triggers.md),
  [SQL-TEST-01](sql_test_01_contracts_migrations.md), transactions, locking,
  idempotency, RPO, and RTO.
- **Artifacts:** [learner SQL](../lessons/sql_repl_01_cdc_high_availability.sql) ·
  [solution reasoning](../solutions/sql_repl_01_cdc_high_availability_solutions.md) ·
  [executable solution](../solutions/sql_repl_01_cdc_high_availability_solutions.sql)

Run the single-database offline simulation:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_repl_01_cdc_high_availability.sql
```

It reads capability/count catalogs and rolls back local tables. It never changes
`wal_level`, creates publications/subscriptions/slots, promotes a server, or
contacts another node.

## A beginner's mental model for this lesson

Replication copies committed changes from one server to another; change data
capture (CDC) hands those changes to other systems. Both deliver messages at
least once, so a consumer must treat a repeated event as already done. This
lesson shows that on one database: the outbox row is committed with the
business change, and the consumer inbox key turns a redelivery into a no-op.
The vocabulary below (WAL, physical and logical replication, CDC, outbox, inbox
key) names each part.

The settings query returns exactly one row for the current database, and the
count query returns exactly one row of six counts. In the lab,
`projected_orders` has one row per consumer and order, `consumer_inbox` one row
per consumer and accepted event id, and the delivery report one row per outbox
event. A repeated delivery must not add an inbox row, and an older
`aggregate_version` must not overwrite a newer projection.

The capability queries are evidence, not permission: they report the WAL level,
sender and slot limits and object counts, never slot names, hosts or connection
strings, and a managed service may need a monitoring role even to read the
counts. The outbox lab then shows why a consumer must be idempotent.
`INSERT ... ON CONFLICT (consumer_name, event_id) DO NOTHING` sets `FOUND` only
on first acceptance, so the projection update runs once per event no matter how
many times delivery is retried.

## Two worked SQL examples

Example 1 reads replication settings and Example 2 counts replication objects;
both are read-only.

### Example 1

```sql
SELECT
  current_database() AS database_name,
  current_setting('wal_level') AS wal_level,
  current_setting('max_wal_senders') AS max_wal_senders,
  current_setting('max_replication_slots') AS max_replication_slots,
  current_setting('hot_standby') AS hot_standby,
  pg_catalog.pg_is_in_recovery() AS is_in_recovery;
```

**How to read it:** Each column is a single `current_setting(...)` call or
`pg_is_in_recovery()`; there is no `FROM`, so the result has one row. A primary
reports `false` for `is_in_recovery`, a standby `true`.

**Expected result/shape:** One row with `database_name`, `wal_level`,
`max_wal_senders`, `max_replication_slots`, `hot_standby` and `is_in_recovery`.
A classroom container usually shows `replica` for `wal_level`; logical decoding
needs `logical`.

### Example 2

```sql
SELECT
  (
    SELECT
      COUNT(*)
    FROM
      pg_catalog.pg_replication_slots) AS slot_count,
  (
    SELECT
      COUNT(*)
    FROM
      pg_catalog.pg_replication_slots AS s
    WHERE
      s.active) AS active_slot_count,
  (
    SELECT
      COUNT(*)
    FROM
      pg_catalog.pg_publication) AS publication_count,
  (
    SELECT
      COUNT(*)
    FROM
      pg_catalog.pg_subscription) AS subscription_count,
  (
    SELECT
      COUNT(*)
    FROM
      pg_catalog.pg_stat_replication) AS sender_count,
  (
    SELECT
      COUNT(*)
    FROM
      pg_catalog.pg_stat_wal_receiver) AS receiver_count;
```

**How to read it:** Six scalar subqueries each count one catalog view.
`active_slot_count` counts only slots with a connected consumer; an inactive
slot still retains WAL.

**Expected result/shape:** One row of six counts. On a single classroom server
every count is usually 0, which is a valid result: it means nothing is
replicating, not that the query failed.

## Learning objectives

- Implement a transactional outbox and an idempotent consumer with immutable
  event fingerprints.
- Reason about at-least-once delivery, aggregate ordering, and replication
  posture through safe inspection.
- Compare physical and logical replication, explain slot/WAL retention, and
  design failover/RPO/RTO evidence without mistaking replication for backup.

## Vocabulary and concepts

- **WAL:** ordered write-ahead log used by crash and replication recovery.
- **Physical replication:** byte/block-level WAL streaming for a compatible
  PostgreSQL cluster.
- **Logical replication:** table-change stream decoded into publications and
  subscriptions.
- **CDC:** change data capture delivered to downstream consumers.
- **Transactional outbox:** business change and event intent committed in one
  database transaction.
- **Inbox/idempotency key:** durable consumer record preventing repeated effect.
- **Replication slot:** server-side retention position that can keep WAL/catalog
  state for a consumer.
- **Failover:** promote/switch service to a healthy replica.
- **Fencing:** prevent the former primary from accepting conflicting writes.
- **Split brain:** multiple writable primaries diverging.

## Worked example / walkthrough

The capability query reports WAL level and counts only; it does not print slot,
publication, subscription, host, or query identities. Counts can still require
monitoring privileges on managed services. Capability settings are evidence, not
authorization to mutate them.

The outbox transaction writes order state and a unique
`(aggregate_type,key,version)` event together. If the process dies after commit
but before delivery, the event remains. This closes the dual-write gap between
business data and a separately published message.

`consume_outbox_batch` claims ordered unpublished rows with
`FOR UPDATE SKIP LOCKED`, inserts `(consumer,event_id)` with `ON CONFLICT DO
NOTHING`, applies a projection only when the inbox insert is new, and records
delivery attempts. Resetting `published_at` simulates redelivery: attempts
increase, but inbox cardinality and projection side effect do not.

An idempotency key is also an immutability contract. The inbox stores a
canonical JSONB payload fingerprint and rejects the same event ID with a
different fingerprint; silently treating those two requests as equivalent
would hide producer corruption. The local procedure intentionally collapses
one relay and one consumer into a teaching transaction. Real fan-out publishes
once to a broker/log and tracks delivery or offsets per consumer group rather
than using one global `published_at` value as every consumer's position.

This same-database simulation can atomically combine inbox and projection.
An external API effect cannot share the transaction. Send the stable event or
operation ID to an API that durably enforces idempotency, reconcile uncertain
timeouts, and accept that “exactly once” is an end-to-end property, not a broker
checkbox.

Aggregate version protects the projection from late older delivery. A consumer
should detect version gaps rather than silently accept missing history, then
retry, replay, or fetch a canonical snapshot according to its contract.

Physical streaming reproduces the cluster and supports standby/failover but
requires compatible binaries/storage semantics. Logical replication selects
tables and can cross versions/use different indexes, but schema DDL and sequence
state need separate coordination. Neither retained replica alone protects
against a replicated accidental delete.

Slots protect a consumer's restart position by retaining WAL. An abandoned slot
can fill disk and threaten the primary. Monitor retained bytes/LSN lag, activity,
consumer ownership, alert/runbook thresholds, and only retire a slot after
proving the consumer no longer needs it.

Failover requires health/quorum, fencing, loss/replay evidence, client routing,
timeline/slot/subscriber repair, verification, and a new backup. Promotion is
irreversible history branching, not a health-check button.

### Optional multi-node boundary

A physical/logical lab requires an approved pinned multi-container environment,
separate ports/volumes, replication credentials, initialized publications or
standbys, controlled network faults, disk monitoring, and exact cleanup. It may
need a one-time image pull. It is intentionally not implemented by this SQL
module; never create slots/subscriptions or alter WAL settings on the host course
cluster merely to make an exercise appear complete.

## Exercises

Complete all twelve prompts. Begin with publisher crash, consumer uncertainty, out-of-order
versions, physical/logical semantics, slot retention operations, and a fenced
failover runbook; then cover publications, bootstrap, replica consistency,
conflict handling, DDL sequencing, and failback. For every failure, identify
durable state before retry and the evidence needed to distinguish “not applied”
from “applied but acknowledgement lost.”

Keep the local SQL as a single-node model; multi-node actions remain reviewed
runbook work:

1. **Publisher crash:** prove a committed, unacknowledged outbox row is durable.
   **Inputs/evidence:** For sql-repl-01 Exercise 1, Insert business state and its row in `pro_replication_lab.outbox_events` in one transaction, commit, and leave `published_at` NULL to represent a crash before publisher acknowledgement.
   **Expected result/shape:** For sql-repl-01 Exercise 1, One row per unpublished `event_id`, with `event_id`, `aggregate_key`, and `aggregate_version`, ordered by `aggregate_key, aggregate_version, event_id`.
   **Verify:** For sql-repl-01 Exercise 1, Query only `published_at IS NULL`, require unique `event_id`, and prove the committed event remains after a new session connects. Mark a different event published in a savepoint and prove it leaves this result. Hint ladder, rung 1: The durable outbox row, not process memory, is what lets a publisher retry after a crash.
2. **Consumer uncertainty:** distinguish database-local idempotency from an
   external side effect and design its key.
   **Inputs/evidence:** For sql-repl-01 Exercise 2, Deliver the same event twice to one consumer. Use `(consumer_name, event_id)` as the inbox key and retain a canonical payload hash; describe a separate idempotency key for any external API effect.
   **Expected result/shape:** For sql-repl-01 Exercise 2, One row per `(consumer_name, event_id)`, with `consumer_name`, `event_id`, and `accepted_rows`, ordered by both keys; every `accepted_rows` value is 1.
   **Verify:** For sql-repl-01 Exercise 2, The duplicate call leaves one inbox row and one database projection effect. Reuse the event ID with different payload and prove SQLSTATE `23514`; explain that an external API must persist/replay the same idempotency key because the local inbox cannot roll that effect back. Hint ladder, rung 1: Duplicate delivery is expected; idempotency means the same logical effect is accepted once, not that the broker sends once.
3. **Ordering:** deliver versions out of order, prevent regression, and detect
   gaps.
   **Inputs/evidence:** For sql-repl-01 Exercise 3, Deliver version 3, then version 2, then redeliver version 3 for `ORDER-1`. Compare consumer inbox versions with the authoritative outbox sequence, whose valid sequence begins at version 1.
   **Expected result/shape:** For sql-repl-01 Exercise 3, The projection result has one row per `(consumer_name, aggregate_key)`, with `consumer_name`, `aggregate_key`, `aggregate_version`, and `status`. A second result has one row per `aggregate_key`, with `expected_versions`, `accepted_versions`, and `missing_versions`; it reports missing version 1.
   **Verify:** For sql-repl-01 Exercise 3, Projection remains at version 3/cancelled after version 2 arrives. The gap diagnostic must compare against the source sequence, not generate only from the minimum accepted version; after version 1 is accepted, `missing_versions` becomes empty. Hint ladder, rung 1: Monotonic projection updates prevent regression but do not prove the consumer saw every earlier event.
4. **Mechanisms:** compare physical streaming with logical publication,
   including DDL and sequence behavior.
   **Inputs/evidence:** For sql-repl-01 Exercise 4, Read local `pg_is_in_recovery()` and `server_version`, then build a comparison matrix for physical streaming and logical replication.
   **Expected result/shape:** For sql-repl-01 Exercise 4, Exactly one local capability row with `connected_to_recovery_node` and `server_version`. The matrix has one row per mechanism and columns for replicated scope, DDL, sequence state, filtering, compatibility, failover use, and major limitation.
   **Verify:** For sql-repl-01 Exercise 4, Trace each matrix claim to PostgreSQL documentation or observed catalog state. State explicitly that logical replication does not carry DDL or sequence state and schema mismatch can halt apply; no replication object is created in this lesson. Hint ladder, rung 1: Local server state is evidence about this connection; it does not reveal an unconfigured topology.
5. **Slots:** define WAL-byte, active-state, lag, disk, alert, ownership, and
   retirement evidence.
   **Inputs/evidence:** For sql-repl-01 Exercise 5, Read `pg_replication_slots` only; derive local current/replay LSN and retained WAL bytes from each non-NULL `restart_lsn`. Add an operations policy without creating or dropping slots.
   **Expected result/shape:** For sql-repl-01 Exercise 5, Zero or one row per `slot_name`, with `slot_name`, `slot_type`, `active`, `restart_lsn`, `confirmed_flush_lsn`, `retained_wal_bytes`, `wal_status`, and `safe_wal_size`, ordered by `slot_name`. Empty output is valid on an unconfigured course server.
   **Verify:** For sql-repl-01 Exercise 5, Reconcile retained bytes with `pg_wal_lsn_diff`; the policy names consumer owner, lag/disk budgets, alert thresholds, last progress, incident response, and evidence required before retirement. Never create a slot merely to make this exercise nonempty. Hint ladder, rung 1: Inactive means disconnected now; it does not prove the consumer is abandoned or the retained WAL is safe to discard.
6. **Failover:** cover quorum, fencing, loss, routing, timeline, CDC state,
   objectives, fallback, verification, and new backup.
   **Inputs/evidence:** For sql-repl-01 Exercise 6, Write a topology-specific failover runbook; this local transaction cannot promote or fence a server. Include authority, health/quorum, old-primary fencing, data-loss evidence, routing, reconnect, timeline, slots/subscriptions, RPO/RTO, fallback, backup, and audit.
   **Expected result/shape:** For sql-repl-01 Exercise 6, One reviewed row per `step_number`, with `phase`, `action`, `required_evidence`, `stop_condition`, and `owner`.
   **Verify:** For sql-repl-01 Exercise 6, Tabletop-test one unreachable-but-not-failed primary and one lagged candidate. Promotion remains blocked until fencing/quorum and data-loss evidence satisfy the runbook; after promotion, verify writes, routing, CDC state, a replacement replica, and a new protected backup. Hint ladder, rung 1: Failover without fencing can create two writers; that is a correctness incident, not merely an availability issue.
7. **Publication contract:** design row/column scope, replica identity, initial
   copy, updates/deletes, and tenant-leak tests.
   **Inputs/evidence:** For sql-repl-01 Exercise 7, Inspect local `pg_class`/`pg_namespace` metadata for `pro_replication_lab.outbox_events`. Separately write, but do not run, a publication DDL contract with one row filter and explicit column list.
   **Expected result/shape:** For sql-repl-01 Exercise 7, One local evidence row per `(schema_name, table_name)`, with `schema_name`, `table_name`, and `replica_identity`. The design record lists published columns/filter, UPDATE/DELETE replica identity, initial copy, DDL/sequence handling, subscriber compatibility, and tenant-leak tests.
   **Verify:** For sql-repl-01 Exercise 7, Prove the identity supports published UPDATE/DELETE keys and test allowed, denied, NULL, INSERT, UPDATE-transition, and DELETE cases in an approved isolated topology. The local catalog row alone does not prove publication scope or leak prevention. Hint ladder, rung 1: Schema plus table is the relation identity; schema name alone is not the output grain.
8. **Bootstrap:** align consistent snapshot and start LSN with slot retention,
   deduplication, restart, handoff, and abandoned-run cleanup.
   **Inputs/evidence:** For sql-repl-01 Exercise 8, Build an inline ordered bootstrap plan connecting one exported snapshot, start LSN/slot, copy progress, stream handoff, deduplication, durable checkpoint, WAL budget, restart, and abandoned-bootstrap cleanup.
   **Expected result/shape:** For sql-repl-01 Exercise 8, One row per `step_number`, with `step_number` and `required_evidence`, ordered numerically by `step_number`.
   **Verify:** For sql-repl-01 Exercise 8, Each step consumes evidence produced by the prior step; the snapshot identity and start LSN remain paired. Simulate interruption before and after handoff and prove restart avoids gaps/duplicates and abandoned slots/resources are cleaned only with owner evidence. Hint ladder, rung 1: Snapshot copy and streaming overlap must share one exact boundary; two unrelated “latest” points can create gaps.
9. **Read consistency:** define user-visible staleness and compare primary
   pinning, LSN waits, bounded lag, timeout, and fallback.
   **Inputs/evidence:** For sql-repl-01 Exercise 9, Capture the local current WAL LSN on a primary or last replay LSN on a recovery node as a visibility token; compare read-after-write strategies without claiming a replica exists.
   **Expected result/shape:** For sql-repl-01 Exercise 9, Exactly one local row with `local_visibility_lsn`. A strategy matrix covers primary pinning, replica wait for token, bounded staleness/session guarantee, timeout, and fallback.
   **Verify:** For sql-repl-01 Exercise 9, In an approved topology, carry the commit token to the read path and wait until the chosen replica replay position reaches it; test timeout and fallback. This local token alone is not evidence that any remote replica replayed the write. Hint ladder, rung 1: Byte lag is an operations measure; user-visible consistency asks whether a particular commit is observable.
10. **Conflicts:** compare single-writer ownership, versions, merge, quarantine,
    and repair; reject naive wall-clock wins.
   **Inputs/evidence:** For sql-repl-01 Exercise 10, Read current projection rows; compare single-writer ownership, expected-version rejection, deterministic domain merge, quarantine, and canonical snapshot/replay repair. Perform no multi-writer mutation here.
   **Expected result/shape:** For sql-repl-01 Exercise 10, One row per `(consumer_name, aggregate_key)`, with `consumer_name`, `aggregate_key`, `aggregate_version`, and `status`, ordered by both identity columns. The strategy matrix names prerequisites, conflicts handled, failure mode, audit evidence, and repair.
   **Verify:** For sql-repl-01 Exercise 10, Walk clock-skew and concurrent-version counterexamples; wall-clock last-write-wins must fail review. Each accepted strategy either prevents a second writer or detects/quarantines a version conflict without silently overwriting the canonical state. Hint ladder, rung 1: Version/ownership evidence is causal; unsynchronized wall-clock timestamps are not a safe conflict order.
11. **DDL sequencing:** build publisher/subscriber/application compatibility
    across additive, validating, contract, and removal phases.
   **Inputs/evidence:** For sql-repl-01 Exercise 11, Encode the required lifecycle order as an inline matrix: expand → deploy → backfill/validate → contract. Include publisher, subscriber, and application compatibility at every phase.
   **Expected result/shape:** For sql-repl-01 Exercise 11, One row per `step_number`, with `step_number`, `phase`, and `compatibility_gate`, ordered by `step_number`, never lexicographically by phase text.
   **Verify:** For sql-repl-01 Exercise 11, The numeric sequence is exactly `{1,2,3,4}` and phase array is exactly `{expand,deploy,backfill,contract}`. Test additive columns, defaults, constraints, type changes, indexes, old/new readers/writers, and rollback; logical replication's separate DDL/sequence handling is explicit. Hint ladder, rung 1: Compatibility is a time-ordered protocol, not an alphabetically sorted checklist.
12. **Failback/reseed:** choose rewind/rebuild safely and verify timelines,
    slots, subscriptions, routing, data, backup, and audit.
   **Inputs/evidence:** For sql-repl-01 Exercise 12, Write a topology-specific failback/reseed plan after promotion; this local SQL file cannot rewind, rebuild, route clients, or manipulate replication objects.
   **Expected result/shape:** For sql-repl-01 Exercise 12, One row per `step_number`, with `phase`, `required_evidence`, `decision`, `owner`, and `stop_condition`. Cover a protected new-primary backup, old-primary fencing, timeline divergence, rewind/rebuild choice, slots/subscriptions, client routing, data checks, new redundancy/backup, and audit.
   **Verify:** For sql-repl-01 Exercise 12, Tabletop both a rewind-eligible and rewind-ineligible former primary. Rejoin stays blocked until lineage/data checks pass, no client can write the fenced node, CDC state is rebuilt/reconciled, and rollback/stop authority is explicit. Hint ladder, rung 1: Failback is another migration with data-lineage risk, not simply “point traffic back.”

## Self-check

- Are business row and outbox event atomic?
- Does redelivery leave one inbox row/effect per consumer-event?
- Can an older aggregate version never overwrite a newer projection?
- Are version gaps detectable?
- Can you state what schema/sequences the replication mode does not cover?
- Does slot monitoring include retained WAL disk risk?
- Does failover fence the old primary and prove data-loss/RPO?
- Does rollback leave no local schema, publication, subscription, slot, or role?

## Common pitfalls

- Writing business data then publishing separately loses events on a crash.
- Marking published before durable broker acceptance loses delivery.
- Retrying a timed-out external side effect without an idempotency contract can
  duplicate it.
- SKIP LOCKED is a work-distribution tool, not a guarantee of fair ordering.
- Logical replication is not automatic schema migration.
- Unbounded inactive slots can exhaust primary disk.
- Replicas replay deletes/corruption and are not independent backup.
- Failover without fencing creates split brain.
- Async replication can lose acknowledged commits; RPO must reflect reality.
- Monitoring only “replica connected” misses replay/apply lag.

## Next step

Continue to [SQL-TEMPORAL-01; temporal and domain modelling](sql_temporal_01_domain_modelling.md).
Combine the outbox with SQL-TEST-01 contracts and SQL-OPS-02 recovery rehearsals
before treating CDC or failover as production-ready.

## Ask an AI tutor about this lesson

The lesson and expected observations are sufficient offline. For optional
coaching, copy:

```text
Tutor me through sql-repl-01: Replication, Change Data Capture, and High Availability.

I have completed the direct catalog prerequisites: `sql-ops-02`, `sql-prog-01`, `sql-test-01`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_repl_01_cdc_high_availability.md
- Answer-free learner SQL: sql/professional/lessons/sql_repl_01_cdc_high_availability.sql

Key terms to teach in context: WAL, Physical replication, Logical replication, CDC, Transactional outbox, Inbox/idempotency key. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The capability query reports WAL level and counts only; it does not print slot, publication, subscription, host, or query identities. Counts can still require monitoring privileges on managed services. Capability settings are evidence, not authorization to mutate them.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-repl-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
