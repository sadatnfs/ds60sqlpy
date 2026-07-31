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

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-REPL-01 — Replication, Change Data Capture, and High Availability** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-repl-01/sql_repl_01_cdc_high_availability.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Some demonstrations require privileges or server features a normal course role may not have. Run the capability check first. The supported default path still teaches inspection and design without creating cluster-wide roles, extensions, or replication objects.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_repl_01_cdc_high_availability.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_repl_01_cdc_high_availability.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. This lesson introduces or reinforces
WAL, Physical replication, Logical replication, CDC, Transactional outbox, Inbox/idempotency key. Its worked SQL reads or creates `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, `pg_catalog.pg_subscription`, `pg_catalog.pg_stat_replication`, `pg_catalog.pg_stat_wal_receiver`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: The capability query reports WAL level and counts only; it does not print slot, publication, subscription, host, or query identities. Counts can still require monitoring privileges on managed services. Capability settings are evidence, not authorization to mutate them.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/professional/lessons/sql_repl_01_cdc_high_availability.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
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
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

Complete all twelve prompts. Begin with publisher crash, consumer uncertainty, out-of-order
versions, physical/logical semantics, slot retention operations, and a fenced
failover runbook; then cover publications, bootstrap, replica consistency,
conflict handling, DDL sequencing, and failback. For every failure, identify
durable state before retry and the evidence needed to distinguish “not applied”
from “applied but acknowledgement lost.”

Keep the local SQL as a single-node model; multi-node actions remain reviewed
runbook work:

1. **Publisher crash:** prove a committed, unacknowledged outbox row is durable.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. **Consumer uncertainty:** distinguish database-local idempotency from an
   external side effect and design its key.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Ordering:** deliver versions out of order, prevent regression, and detect
   gaps.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
4. **Mechanisms:** compare physical streaming with logical publication,
   including DDL and sequence behavior.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. **Slots:** define WAL-byte, active-state, lag, disk, alert, ownership, and
   retirement evidence.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. **Failover:** cover quorum, fencing, loss, routing, timeline, CDC state,
   objectives, fallback, verification, and new backup.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
7. **Publication contract:** design row/column scope, replica identity, initial
   copy, updates/deletes, and tenant-leak tests.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
8. **Bootstrap:** align consistent snapshot and start LSN with slot retention,
   deduplication, restart, handoff, and abandoned-run cleanup.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
9. **Read consistency:** define user-visible staleness and compare primary
   pinning, LSN waits, bounded lag, timeout, and fallback.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
10. **Conflicts:** compare single-writer ownership, versions, merge, quarantine,
    and repair; reject naive wall-clock wins.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
11. **DDL sequencing:** build publisher/subscriber/application compatibility
    across additive, validating, contract, and removal phases.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
12. **Failback/reseed:** choose rewind/rebuild safely and verify timelines,
    slots, subscriptions, routing, data, backup, and audit.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.

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

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-repl-01 — Replication, Change Data Capture, and High Availability.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/professional/companion-guides/sql_repl_01_cdc_high_availability.md
- Answer-free learner SQL: sql/professional/lessons/sql_repl_01_cdc_high_availability.sql

The lesson concepts include WAL, Physical replication, Logical replication, CDC, Transactional outbox, Inbox/idempotency key. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The capability query reports WAL level and counts only; it does not print slot, publication, subscription, host, or query identities. Counts can still require monitoring privileges on managed services. Capability settings are evidence, not authorization to mutate them.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-repl-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
