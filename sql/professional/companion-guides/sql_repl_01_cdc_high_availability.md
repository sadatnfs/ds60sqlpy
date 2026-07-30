# SQL-REPL-01 — Replication, CDC, and High Availability

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-ops-02`, `sql-prog-01`, and `sql-test-01`
- **Prerequisites:** [SQL-OPS-02 — recovery](sql_ops_02_backup_restore_recovery.md),
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
timeouts, and accept that “exactly once” is an end-to-end property—not a broker
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

Complete all six prompts: publisher crash, consumer uncertainty, out-of-order
versions, physical/logical semantics, slot retention operations, and a fenced
failover runbook. For every failure, identify durable state before retry and the
evidence needed to distinguish “not applied” from “applied but acknowledgement
lost.”

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

Continue to [SQL-TEMPORAL-01 — temporal and domain modelling](sql_temporal_01_domain_modelling.md).
Combine the outbox with SQL-TEST-01 contracts and SQL-OPS-02 recovery rehearsals
before treating CDC or failover as production-ready.
