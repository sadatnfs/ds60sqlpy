# SQL-REPL-01 Solutions — Replication, CDC, and HA


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_repl_01_cdc_high_availability_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_repl_01_cdc_high_availability_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are WAL, Physical replication, Logical replication, CDC, Transactional outbox, Inbox/idempotency key. Its worked-model focus is:
The capability query reports WAL level and counts only; it does not print slot, publication, subscription, host, or query identities. Counts can still require monitoring privileges on managed services. Capability settings are evidence, not authorization to mutate them.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 1, Insert business state and its row in `pro_replication_lab.outbox_events` in one transaction, commit, and leave `published_at` NULL to represent a crash before publisher acknowledgement.
- **Expected result/shape:** For sql-repl-01 Exercise 1, One row per unpublished `event_id`, with `event_id`, `aggregate_key`, and `aggregate_version`, ordered by `aggregate_key, aggregate_version, event_id`.
- **Independent verification:** For sql-repl-01 Exercise 1, Query only `published_at IS NULL`, require unique `event_id`, and prove the committed event remains after a new session connects. Mark a different event published in a savepoint and prove it leaves this result. Hint ladder, rung 1: The durable outbox row—not process memory—is what lets a publisher retry after a crash.

## Exercise 2 — Consumer uncertainty

Inbox plus projection is atomic when both live in one database transaction.
For an external API, send `event_id` as an idempotency key to a service that
durably stores it and returns the original result on retry. After a timeout,
query/reconcile by key; do not assume failure means no effect. Bind the key to a
canonical request fingerprint and reject key reuse with different content.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 2, Deliver the same event twice to one consumer. Use `(consumer_name, event_id)` as the inbox key and retain a canonical payload hash; describe a separate idempotency key for any external API effect.
- **Expected result/shape:** For sql-repl-01 Exercise 2, One row per `(consumer_name, event_id)`, with `consumer_name`, `event_id`, and `accepted_rows`, ordered by both keys; every `accepted_rows` value is 1.
- **Independent verification:** For sql-repl-01 Exercise 2, The duplicate call leaves one inbox row and one database projection effect. Reuse the event ID with different payload and prove SQLSTATE `23514`; explain that an external API must persist/replay the same idempotency key because the local inbox cannot roll that effect back. Hint ladder, rung 1: Duplicate delivery is expected; idempotency means the same logical effect is accepted once, not that the broker sends once.

## Exercise 3 — Ordering and gaps

The executable delivers v3 before v2. The projection update condition accepts
only a greater aggregate version, so v2 cannot regress v3. Inbox contains
versions 2 and 3; comparing with generated contiguous versions reveals the
missing v1 gap. Policy may pause/replay, fetch a canonical snapshot, or accept a
documented compaction—not silently ignore it.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 3, Deliver version 3, then version 2, then redeliver version 3 for `ORDER-1`. Compare consumer inbox versions with the authoritative outbox sequence, whose valid sequence begins at version 1.
- **Expected result/shape:** For sql-repl-01 Exercise 3, The projection result has one row per `(consumer_name, aggregate_key)`, with `consumer_name`, `aggregate_key`, `aggregate_version`, and `status`. A second result has one row per `aggregate_key`, with `expected_versions`, `accepted_versions`, and `missing_versions`; it reports missing version 1.
- **Independent verification:** For sql-repl-01 Exercise 3, Projection remains at version 3/cancelled after version 2 arrives. The gap diagnostic must compare against the source sequence, not generate only from the minimum accepted version; after version 1 is accepted, `missing_versions` becomes empty. Hint ladder, rung 1: Monotonic projection updates prevent regression but do not prove the consumer saw every earlier event.

## Exercise 4 — Physical versus logical

Physical replication streams WAL/storage changes for the cluster and supports
standby recovery; it needs compatible PostgreSQL/storage/extensions. Logical
replication decodes selected table DML through publication/subscription and can
support version/platform differences, but schema DDL, sequences, large objects,
and conflict policy need separate handling.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 4, Read local `pg_is_in_recovery()` and `server_version`, then build a comparison matrix for physical streaming and logical replication.
- **Expected result/shape:** For sql-repl-01 Exercise 4, Exactly one local capability row with `connected_to_recovery_node` and `server_version`. The matrix has one row per mechanism and columns for replicated scope, DDL, sequence state, filtering, compatibility, failover use, and major limitation.
- **Independent verification:** For sql-repl-01 Exercise 4, Trace each matrix claim to PostgreSQL documentation or observed catalog state. State explicitly that logical replication does not carry DDL or sequence state and schema mismatch can halt apply; no replication object is created in this lesson. Hint ladder, rung 1: Local server state is evidence about this connection; it does not reveal an unconfigured topology.

## Exercise 5 — Slot operations

Track slot owner/consumer, active state, restart/confirmed LSN, retained WAL
bytes versus disk budget, consumer lag/rate, last success, and alert/runbook
threshold. Confirm consumer decommission or new restart position before
dropping a slot. A disconnected but recoverable consumer may still need retained
WAL.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 5, Read `pg_replication_slots` only; derive local current/replay LSN and retained WAL bytes from each non-NULL `restart_lsn`. Add an operations policy without creating or dropping slots.
- **Expected result/shape:** For sql-repl-01 Exercise 5, Zero or one row per `slot_name`, with `slot_name`, `slot_type`, `active`, `restart_lsn`, `confirmed_flush_lsn`, `retained_wal_bytes`, `wal_status`, and `safe_wal_size`, ordered by `slot_name`. Empty output is valid on an unconfigured course server.
- **Independent verification:** For sql-repl-01 Exercise 5, Reconcile retained bytes with `pg_wal_lsn_diff`; the policy names consumer owner, lag/disk budgets, alert thresholds, last progress, incident response, and evidence required before retirement. Never create a slot merely to make this exercise nonempty. Hint ladder, rung 1: Inactive means disconnected now; it does not prove the consumer is abandoned or the retained WAL is safe to discard.

## Exercise 6 — Failover

Detect with quorum-aware health, fence the old writer, determine replay/loss
against RPO, promote one target, update routing, reconnect clients with retry,
verify data/application/slots/subscribers, establish a new replica and backup,
and record the new timeline. Define abort/rollback boundaries before promotion;
after divergent writes, “fail back” is reconciliation, not a simple switch.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 6, Write a topology-specific failover runbook; this local transaction cannot promote or fence a server. Include authority, health/quorum, old-primary fencing, data-loss evidence, routing, reconnect, timeline, slots/subscriptions, RPO/RTO, fallback, backup, and audit.
- **Expected result/shape:** For sql-repl-01 Exercise 6, One reviewed row per `step_number`, with `phase`, `action`, `required_evidence`, `stop_condition`, and `owner`.
- **Independent verification:** For sql-repl-01 Exercise 6, Tabletop-test one unreachable-but-not-failed primary and one lagged candidate. Promotion remains blocked until fencing/quorum and data-loss evidence satisfy the runbook; after promotion, verify writes, routing, CDC state, a replacement replica, and a new protected backup. Hint ladder, rung 1: Failover without fencing can create two writers; that is a correctness incident, not merely an availability issue.

## Exercise 7 — Publication and replica identity contract

Publish only reviewed rows/columns and test inserts, updates crossing the row
filter, deletes, NULL boundaries, and every tenant. UPDATE/DELETE need a replica
identity that identifies the old row—usually a suitable primary key; FULL
increases WAL and has limitations.

Logical replication does not automatically maintain sequence state or replicate
general DDL. Filtering defines movement scope, not subscriber authorization, so
test for leaks end to end.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 7, Inspect local `pg_class`/`pg_namespace` metadata for `pro_replication_lab.outbox_events`. Separately write, but do not run, a publication DDL contract with one row filter and explicit column list.
- **Expected result/shape:** For sql-repl-01 Exercise 7, One local evidence row per `(schema_name, table_name)`, with `schema_name`, `table_name`, and `replica_identity`. The design record lists published columns/filter, UPDATE/DELETE replica identity, initial copy, DDL/sequence handling, subscriber compatibility, and tenant-leak tests.
- **Independent verification:** For sql-repl-01 Exercise 7, Prove the identity supports published UPDATE/DELETE keys and test allowed, denied, NULL, INSERT, UPDATE-transition, and DELETE cases in an approved isolated topology. The local catalog row alone does not prove publication scope or leak prevention. Hint ladder, rung 1: Schema plus table is the relation identity; schema name alone is not the output grain.

## Exercise 8 — Snapshot-to-stream bootstrap

Create/own the slot and exported snapshot, record its start LSN, read initial
data under that snapshot, then consume from the matching position before
handoff. Deduplicate by stable source identity and checkpoint only durable work.

Monitor retained WAL versus disk. On abandonment, prove no consumer needs the
slot before cleanup; an orphan slot is a disk-growth hazard.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 8, Build an inline ordered bootstrap plan connecting one exported snapshot, start LSN/slot, copy progress, stream handoff, deduplication, durable checkpoint, WAL budget, restart, and abandoned-bootstrap cleanup.
- **Expected result/shape:** For sql-repl-01 Exercise 8, One row per `step_number`, with `step_number` and `required_evidence`, ordered numerically by `step_number`.
- **Independent verification:** For sql-repl-01 Exercise 8, Each step consumes evidence produced by the prior step; the snapshot identity and start LSN remain paired. Simulate interruption before and after handoff and prove restart avoids gaps/duplicates and abandoned slots/resources are cleaned only with owner evidence. Hint ladder, rung 1: Snapshot copy and streaming overlap must share one exact boundary; two unrelated “latest” points can create gaps.

## Exercise 9 — Read-after-write on replicas

Define user-visible consistency: immediate own-write visibility, maximum
staleness, or best effort. Compare primary pinning, a commit-LSN token and replay
wait, bounded-lag routing, and timeout fallback.

Byte/time lag does not prove one transaction is visible. Observe replay LSN and
application caches, cap waits, and specify paused-replay/failover behavior.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 9, Capture the local current WAL LSN on a primary or last replay LSN on a recovery node as a visibility token; compare read-after-write strategies without claiming a replica exists.
- **Expected result/shape:** For sql-repl-01 Exercise 9, Exactly one local row with `local_visibility_lsn`. A strategy matrix covers primary pinning, replica wait for token, bounded staleness/session guarantee, timeout, and fallback.
- **Independent verification:** For sql-repl-01 Exercise 9, In an approved topology, carry the commit token to the read path and wait until the chosen replica replay position reaches it; test timeout and fallback. This local token alone is not evidence that any remote replica replayed the write. Hint ladder, rung 1: Byte lag is an operations measure; user-visible consistency asks whether a particular commit is observable.

## Exercise 10 — Multi-writer conflicts

Wall clocks skew, so last timestamp wins can discard a causally later change.
Prefer single-writer ownership; otherwise use expected versions, deterministic
domain merge, and quarantine irreconcilable conflicts with source evidence.

Do not advance checkpoints silently past unresolved data. Provide canonical
snapshot/replay repair, idempotency, authorization, and an audit of the choice.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 10, Read current projection rows; compare single-writer ownership, expected-version rejection, deterministic domain merge, quarantine, and canonical snapshot/replay repair. Perform no multi-writer mutation here.
- **Expected result/shape:** For sql-repl-01 Exercise 10, One row per `(consumer_name, aggregate_key)`, with `consumer_name`, `aggregate_key`, `aggregate_version`, and `status`, ordered by both identity columns. The strategy matrix names prerequisites, conflicts handled, failure mode, audit evidence, and repair.
- **Independent verification:** For sql-repl-01 Exercise 10, Walk clock-skew and concurrent-version counterexamples; wall-clock last-write-wins must fail review. Each accepted strategy either prevents a second writer or detects/quarantines a version conflict without silently overwriting the canonical state. Hint ladder, rung 1: Version/ownership evidence is causal; unsynchronized wall-clock timestamps are not a safe conflict order.

## Exercise 11 — DDL compatibility sequencing

Matrix publisher, subscriber, decoder/apply, and old/new application schemas.
Add nullable columns first, deploy tolerant readers/writers, backfill/reconcile,
validate constraints, and remove only after every consumer stops using old
shape.

Defaults, generated values, replica identity, types, row filters, and column
lists need explicit tests. DDL requires its own ordered deployment channel.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 11, Encode the required lifecycle order as an inline matrix: expand → deploy → backfill/validate → contract. Include publisher, subscriber, and application compatibility at every phase.
- **Expected result/shape:** For sql-repl-01 Exercise 11, One row per `step_number`, with `step_number`, `phase`, and `compatibility_gate`, ordered by `step_number`—never lexicographically by phase text.
- **Independent verification:** For sql-repl-01 Exercise 11, The numeric sequence is exactly `{1,2,3,4}` and phase array is exactly `{expand,deploy,backfill,contract}`. Test additive columns, defaults, constraints, type changes, indexes, old/new readers/writers, and rollback; logical replication's separate DDL/sequence handling is explicit. Hint ladder, rung 1: Compatibility is a time-ordered protocol, not an alphabetically sorted checklist.

## Exercise 12 — Failback and reseed

Protect a verified new-primary backup and keep the old primary fenced. Compare
timelines/LSNs and use rewind only when prerequisites/WAL exist; otherwise
rebuild. Recreate and verify replicas, slots, subscriptions, and checkpoints.

Before routing writes, reconcile data and critical queries, establish backup/HA,
monitor retry/lag/conflicts, and record authority/evidence. A diverged former
primary cannot be restored by reversing DNS.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 12, Write a topology-specific failback/reseed plan after promotion; this local SQL file cannot rewind, rebuild, route clients, or manipulate replication objects.
- **Expected result/shape:** For sql-repl-01 Exercise 12, One row per `step_number`, with `phase`, `required_evidence`, `decision`, `owner`, and `stop_condition`. Cover a protected new-primary backup, old-primary fencing, timeline divergence, rewind/rebuild choice, slots/subscriptions, client routing, data checks, new redundancy/backup, and audit.
- **Independent verification:** For sql-repl-01 Exercise 12, Tabletop both a rewind-eligible and rewind-ineligible former primary. Rejoin stays blocked until lineage/data checks pass, no client can write the fenced node, CDC state is rebuilt/reconciled, and rollback/stop authority is explicit. Hint ladder, rung 1: Failback is another migration with data-lineage risk, not simply “point traffic back.”

## Edge cases

- Poison events need quarantine without blocking every later aggregate forever.
- Publisher concurrency needs leases/locks and retry visibility.
- Synchronous replication trades latency/availability for lower acknowledged
  data-loss risk.
- Logical subscriber conflicts require explicit ownership.
