# SQL-REPL-01 Solutions — Replication, CDC, and HA

Run:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_repl_01_cdc_high_availability_solutions.sql
```

The solution creates no replication objects and rolls back.

## Exercise 1 — Publisher crash

Commit business state and outbox intent together. A crash before publisher
acknowledgement leaves `published=false`; a later worker discovers it. Mark
published only after durable downstream acknowledgement. Monitor old
unpublished rows and retry with backoff/ownership.

## Exercise 2 — Consumer uncertainty

Inbox plus projection is atomic when both live in one database transaction.
For an external API, send `event_id` as an idempotency key to a service that
durably stores it and returns the original result on retry. After a timeout,
query/reconcile by key; do not assume failure means no effect. Bind the key to a
canonical request fingerprint and reject key reuse with different content.

## Exercise 3 — Ordering and gaps

The executable delivers v3 before v2. The projection update condition accepts
only a greater aggregate version, so v2 cannot regress v3. Inbox contains
versions 2 and 3; comparing with generated contiguous versions reveals the
missing v1 gap. Policy may pause/replay, fetch a canonical snapshot, or accept a
documented compaction—not silently ignore it.

## Exercise 4 — Physical versus logical

Physical replication streams WAL/storage changes for the cluster and supports
standby recovery; it needs compatible PostgreSQL/storage/extensions. Logical
replication decodes selected table DML through publication/subscription and can
support version/platform differences, but schema DDL, sequences, large objects,
and conflict policy need separate handling.

## Exercise 5 — Slot operations

Track slot owner/consumer, active state, restart/confirmed LSN, retained WAL
bytes versus disk budget, consumer lag/rate, last success, and alert/runbook
threshold. Confirm consumer decommission or new restart position before
dropping a slot. A disconnected but recoverable consumer may still need retained
WAL.

## Exercise 6 — Failover

Detect with quorum-aware health, fence the old writer, determine replay/loss
against RPO, promote one target, update routing, reconnect clients with retry,
verify data/application/slots/subscribers, establish a new replica and backup,
and record the new timeline. Define abort/rollback boundaries before promotion;
after divergent writes, “fail back” is reconciliation, not a simple switch.

## Exercise 7 — Publication and replica identity contract

Publish only reviewed rows/columns and test inserts, updates crossing the row
filter, deletes, NULL boundaries, and every tenant. UPDATE/DELETE need a replica
identity that identifies the old row—usually a suitable primary key; FULL
increases WAL and has limitations.

Logical replication does not automatically maintain sequence state or replicate
general DDL. Filtering defines movement scope, not subscriber authorization, so
test for leaks end to end.

## Exercise 8 — Snapshot-to-stream bootstrap

Create/own the slot and exported snapshot, record its start LSN, read initial
data under that snapshot, then consume from the matching position before
handoff. Deduplicate by stable source identity and checkpoint only durable work.

Monitor retained WAL versus disk. On abandonment, prove no consumer needs the
slot before cleanup; an orphan slot is a disk-growth hazard.

## Exercise 9 — Read-after-write on replicas

Define user-visible consistency: immediate own-write visibility, maximum
staleness, or best effort. Compare primary pinning, a commit-LSN token and replay
wait, bounded-lag routing, and timeout fallback.

Byte/time lag does not prove one transaction is visible. Observe replay LSN and
application caches, cap waits, and specify paused-replay/failover behavior.

## Exercise 10 — Multi-writer conflicts

Wall clocks skew, so last timestamp wins can discard a causally later change.
Prefer single-writer ownership; otherwise use expected versions, deterministic
domain merge, and quarantine irreconcilable conflicts with source evidence.

Do not advance checkpoints silently past unresolved data. Provide canonical
snapshot/replay repair, idempotency, authorization, and an audit of the choice.

## Exercise 11 — DDL compatibility sequencing

Matrix publisher, subscriber, decoder/apply, and old/new application schemas.
Add nullable columns first, deploy tolerant readers/writers, backfill/reconcile,
validate constraints, and remove only after every consumer stops using old
shape.

Defaults, generated values, replica identity, types, row filters, and column
lists need explicit tests. DDL requires its own ordered deployment channel.

## Exercise 12 — Failback and reseed

Protect a verified new-primary backup and keep the old primary fenced. Compare
timelines/LSNs and use rewind only when prerequisites/WAL exist; otherwise
rebuild. Recreate and verify replicas, slots, subscriptions, and checkpoints.

Before routing writes, reconcile data and critical queries, establish backup/HA,
monitor retry/lag/conflicts, and record authority/evidence. A diverged former
primary cannot be restored by reversing DNS.

## Edge cases

- Poison events need quarantine without blocking every later aggregate forever.
- Publisher concurrency needs leases/locks and retry visibility.
- Synchronous replication trades latency/availability for lower acknowledged
  data-loss risk.
- Logical subscriber conflicts require explicit ownership.
