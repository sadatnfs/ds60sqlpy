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

- **Inputs/evidence:** For sql-repl-01 Exercise 1, read from `pro_replication_lab.outbox`. Build the answer toward `event_id`, `aggregate_key`, and `aggregate_version`; keep `event_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-repl-01 Exercise 1, expected output: one row per `event_id`. The final columns are `event_id`, `aggregate_key`, and `aggregate_version`. The final order is `o.aggregate_key, o.aggregate_version`.
- **Independent verification:** For sql-repl-01 Exercise 1, run an anti-check that counts rows where NOT ((NOT o.published)); require unique `event_id` where the expected grain is one row per key and confirm the projected `event_id`, `aggregate_key`, and `aggregate_version` against `pro_replication_lab.outbox`. Add one row for which `(NOT o.published)` is true and one for which it is false; verify only the matching `event_id` value is returned.
- **Intermediate relation check:** For sql-repl-01 Exercise 1, inspect the source keys that survive `WHERE`; then check `o.aggregate_key, o.aggregate_version` before applying the row cap.
- **Clause check:** For sql-repl-01 Exercise 1, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_replication_lab.outbox`, preserve one row per `event_id`, and finish with `event_id`, `aggregate_key`, and `aggregate_version` ordered by `o.aggregate_key, o.aggregate_version`.
- **Alternative/trade-off:** For sql-repl-01 Exercise 1, the chosen form is justified by this lesson-specific rationale: Commit business state and outbox intent together. Evaluate another form against the concrete expected result (one row per `event_id`) and the verification above.
- **Edge case:** Add one row for which `(NOT o.published)` is true and one for which it is false; verify only the matching `event_id` value is returned.

## Exercise 2 — Consumer uncertainty

Inbox plus projection is atomic when both live in one database transaction.
For an external API, send `event_id` as an idempotency key to a service that
durably stores it and returns the original result on retry. After a timeout,
query/reconcile by key; do not assume failure means no effect. Bind the key to a
canonical request fingerprint and reject key reuse with different content.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 2, read from `pro_replication_lab.inbox`. Build the answer toward `consumer_name`, `event_id`, and `accepted_rows`; keep `consumer_name`, and `event_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-repl-01 Exercise 2, expected output: one row per `consumer_name`, and `event_id`. The final columns are `consumer_name`, `event_id`, and `accepted_rows`. The final order is `i.consumer_name, i.event_id`.
- **Independent verification:** For sql-repl-01 Exercise 2, independently aggregate `pro_replication_lab.inbox` by `consumer_name`, and `event_id`; require one output row for every distinct `consumer_name`, and `event_id` tuple and compare `accepted_rows` tuple by tuple. Add duplicate source candidates for `consumer_name`, and `event_id`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-repl-01 Exercise 2, confirm the groups are `consumer_name`, and `event_id`; then check `i.consumer_name, i.event_id` before applying the row cap.
- **Clause check:** For sql-repl-01 Exercise 2, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_replication_lab.inbox`, preserve one row per `consumer_name`, and `event_id`, and finish with `consumer_name`, `event_id`, and `accepted_rows` ordered by `i.consumer_name, i.event_id`.
- **Alternative/trade-off:** For sql-repl-01 Exercise 2, the chosen form is justified by this lesson-specific rationale: Inbox plus projection is atomic when both live in one database transaction. Evaluate another form against the concrete expected result (one row per `consumer_name`, and `event_id`) and the verification above.
- **Edge case:** Add duplicate source candidates for `consumer_name`, and `event_id`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Exercise 3 — Ordering and gaps

The executable delivers v3 before v2. The projection update condition accepts
only a greater aggregate version, so v2 cannot regress v3. Inbox contains
versions 2 and 3; comparing with generated contiguous versions reveals the
missing v1 gap. Policy may pause/replay, fetch a canonical snapshot, or accept a
documented compaction—not silently ignore it.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 3, read from `pro_replication_lab.projection`, `pro_replication_lab.inbox`, and `pro_replication_lab.outbox`. Build the answer toward `consumer_name`, `aggregate_key`, `aggregate_version`, and `status`; keep `status` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-repl-01 Exercise 3, expected output: one row per `status`. The final columns are `consumer_name`, `aggregate_key`, `aggregate_version`, and `status`. The final order is `av.aggregate_key`.
- **Independent verification:** For sql-repl-01 Exercise 3, project `status` plus the raw source columns from `pro_replication_lab.projection`, `pro_replication_lab.inbox`, and `pro_replication_lab.outbox` at each join stage; record row count and distinct `status`, then assert the final `consumer_name`, `aggregate_key`, `aggregate_version`, and `status` values match those staged rows without unintended fanout or loss. Add one source row with a new `status`; verify the result gains exactly one row carrying that `status` value.
- **Intermediate relation check:** For sql-repl-01 Exercise 3, run `accepted_versions` one at a time. Record each CTE's row count and `status` uniqueness before the next stage uses it.
- **Clause check:** For sql-repl-01 Exercise 3, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_replication_lab.projection`, `pro_replication_lab.inbox`, and `pro_replication_lab.outbox`, preserve one row per `status`, and finish with `consumer_name`, `aggregate_key`, `aggregate_version`, and `status` ordered by `av.aggregate_key`.
- **Alternative/trade-off:** For sql-repl-01 Exercise 3, the chosen form is justified by this lesson-specific rationale: The executable delivers v3 before v2. Evaluate another form against the concrete expected result (one row per `status`) and the verification above.
- **Edge case:** Add one source row with a new `status`; verify the result gains exactly one row carrying that `status` value.

## Exercise 4 — Physical versus logical

Physical replication streams WAL/storage changes for the cluster and supports
standby recovery; it needs compatible PostgreSQL/storage/extensions. Logical
replication decodes selected table DML through publication/subscription and can
support version/platform differences, but schema DDL, sequences, large objects,
and conflict policy need separate handling.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 4, read from `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription`. Compute `connected_to_recovery_node`, and `server_version` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-repl-01 Exercise 4, expected output: exactly one aggregate summary row. The final columns are `connected_to_recovery_node`, and `server_version`.
- **Independent verification:** For sql-repl-01 Exercise 4, evaluate each of `server_version` in a separate control `SELECT` over `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription`; require one final row and compare every value. Add one source row with a new `connected_to_recovery_node`; verify the result gains exactly one row carrying that `connected_to_recovery_node` value.
- **Intermediate relation check:** For sql-repl-01 Exercise 4, select `connected_to_recovery_node` from `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` before adding derived columns.
- **Clause check:** For sql-repl-01 Exercise 4, the solution actually uses `SELECT`. Read only those operations: begin at `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription`, preserve exactly one summary row, and finish with `connected_to_recovery_node`, and `server_version`.
- **Alternative/trade-off:** For sql-repl-01 Exercise 4, the chosen form is justified by this lesson-specific rationale: Physical replication streams WAL/storage changes for the cluster and supports standby recovery; it needs compatible PostgreSQL/storage/extensions. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add one source row with a new `connected_to_recovery_node`; verify the result gains exactly one row carrying that `connected_to_recovery_node` value.

## Exercise 5 — Slot operations

Track slot owner/consumer, active state, restart/confirmed LSN, retained WAL
bytes versus disk budget, consumer lag/rate, last success, and alert/runbook
threshold. Confirm consumer decommission or new restart position before
dropping a slot. A disconnected but recoverable consumer may still need retained
WAL.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 5, read from `pg_catalog.pg_replication_slots`. Build the answer toward `slot_name`, `slot_type`, `active`, `restart_lsn`, and `confirmed_flush_lsn`; keep `slot_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-repl-01 Exercise 5, expected output: one row per `slot_name`. The final columns are `slot_name`, `slot_type`, `active`, `restart_lsn`, and `confirmed_flush_lsn`. The final order is `s.slot_name`.
- **Independent verification:** For sql-repl-01 Exercise 5, reselect the returned keys directly from the source; require unique `slot_name` where the expected grain is one row per key and confirm the projected `slot_name`, `slot_type`, `active`, `restart_lsn`, and `confirmed_flush_lsn` against `pg_catalog.pg_replication_slots`. Add one source row with a new `slot_name`; verify the result gains exactly one row carrying that `slot_name` value.
- **Intermediate relation check:** For sql-repl-01 Exercise 5, check `s.slot_name` before applying the row cap.
- **Clause check:** For sql-repl-01 Exercise 5, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_catalog.pg_replication_slots`, preserve one row per `slot_name`, and finish with `slot_name`, `slot_type`, `active`, `restart_lsn`, and `confirmed_flush_lsn` ordered by `s.slot_name`.
- **Alternative/trade-off:** For sql-repl-01 Exercise 5, the chosen form is justified by this lesson-specific rationale: Track slot owner/consumer, active state, restart/confirmed LSN, retained WAL bytes versus disk budget, consumer lag/rate, last success, and alert/runbook threshold. Evaluate another form against the concrete expected result (one row per `slot_name`) and the verification above.
- **Edge case:** Add one source row with a new `slot_name`; verify the result gains exactly one row carrying that `slot_name` value.

## Exercise 6 — Failover

Detect with quorum-aware health, fence the old writer, determine replay/loss
against RPO, promote one target, update routing, reconnect clients with retry,
verify data/application/slots/subscribers, establish a new replica and backup,
and record the new timeline. Define abort/rollback boundaries before promotion;
after divergent writes, “fail back” is reconciliation, not a simple switch.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 6, use `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-repl-01 Exercise 6, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
- **Independent verification:** For sql-repl-01 Exercise 6, restore into an isolated target and reconcile `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-repl-01 Exercise 6, restore into an isolated target and reconcile `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-repl-01 Exercise 6, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` or label it as proposed policy.
- **Alternative/trade-off:** For sql-repl-01 Exercise 6, the chosen form is justified by this lesson-specific rationale: Detect with quorum-aware health, fence the old writer, determine replay/loss against RPO, promote one target, update routing, reconnect clients with retry, verify data/application/slots/subscribers, establish a. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Exercise 7 — Publication and replica identity contract

Publish only reviewed rows/columns and test inserts, updates crossing the row
filter, deletes, NULL boundaries, and every tenant. UPDATE/DELETE need a replica
identity that identifies the old row—usually a suitable primary key; FULL
increases WAL and has limitations.

Logical replication does not automatically maintain sequence state or replicate
general DDL. Filtering defines movement scope, not subscriber authorization, so
test for leaks end to end.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 7, read from `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`. Build the answer toward `schema_name`, `table_name`, and `replica_identity`; keep `schema_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-repl-01 Exercise 7, expected output: one row per `schema_name`. The final columns are `schema_name`, `table_name`, and `replica_identity`.
- **Independent verification:** For sql-repl-01 Exercise 7, project `schema_name` plus the raw source columns from `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` at each join stage; record row count and distinct `schema_name`, then assert the final `schema_name`, `table_name`, and `replica_identity` values match those staged rows without unintended fanout or loss. Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.
- **Intermediate relation check:** For sql-repl-01 Exercise 7, start with the first relation in `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `schema_name` so the exact fanout or loss is visible.
- **Clause check:** For sql-repl-01 Exercise 7, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, and `SELECT`. Read only those operations: begin at `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`, preserve one row per `schema_name`, and finish with `schema_name`, `table_name`, and `replica_identity`.
- **Alternative/trade-off:** For sql-repl-01 Exercise 7, the chosen form is justified by this lesson-specific rationale: Publish only reviewed rows/columns and test inserts, updates crossing the row filter, deletes, NULL boundaries, and every tenant. Evaluate another form against the concrete expected result (one row per `schema_name`) and the verification above.
- **Edge case:** Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.

## Exercise 8 — Snapshot-to-stream bootstrap

Create/own the slot and exported snapshot, record its start LSN, read initial
data under that snapshot, then consume from the matching position before
handoff. Deduplicate by stable source identity and checkpoint only durable work.

Monitor retained WAL versus disk. On abandonment, prove no consumer needs the
slot before cleanup; an orphan slot is a disk-growth hazard.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 8, read from `matching`. Build the answer toward `step_number`, and `required_evidence`; keep `step_number` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-repl-01 Exercise 8, expected output: one row per `step_number`. The final columns are `step_number`, and `required_evidence`. The final order is `step_number`.
- **Independent verification:** For sql-repl-01 Exercise 8, reselect the returned keys directly from the source; require unique `step_number` where the expected grain is one row per key and confirm the projected `step_number`, and `required_evidence` against `matching`. Add one source row with a new `step_number`; verify the result gains exactly one row carrying that `step_number` value.
- **Intermediate relation check:** For sql-repl-01 Exercise 8, check `step_number` before applying the row cap.
- **Clause check:** For sql-repl-01 Exercise 8, the solution actually uses `WITH`, `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `matching`, preserve one row per `step_number`, and finish with `step_number`, and `required_evidence` ordered by `step_number`.
- **Alternative/trade-off:** For sql-repl-01 Exercise 8, the chosen form is justified by this lesson-specific rationale: Create/own the slot and exported snapshot, record its start LSN, read initial data under that snapshot, then consume from the matching position before handoff. Evaluate another form against the concrete expected result (one row per `step_number`) and the verification above.
- **Edge case:** Add one source row with a new `step_number`; verify the result gains exactly one row carrying that `step_number` value.

## Exercise 9 — Read-after-write on replicas

Define user-visible consistency: immediate own-write visibility, maximum
staleness, or best effort. Compare primary pinning, a commit-LSN token and replay
wait, bounded-lag routing, and timeout fallback.

Byte/time lag does not prove one transaction is visible. Observe replay LSN and
application caches, cap waits, and specify paused-replay/failover behavior.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 9, read from `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription`. Compute `local_visibility_lsn` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-repl-01 Exercise 9, expected output: exactly one aggregate summary row. The final columns are `local_visibility_lsn`.
- **Independent verification:** For sql-repl-01 Exercise 9, evaluate each of `row_count` in a separate control `SELECT` over `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription`; require one final row and compare every value. Add one source row with a new `local_visibility_lsn`; verify the result gains exactly one row carrying that `local_visibility_lsn` value.
- **Intermediate relation check:** For sql-repl-01 Exercise 9, select `local_visibility_lsn` from `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` before adding derived columns.
- **Clause check:** For sql-repl-01 Exercise 9, the solution actually uses `SELECT`. Read only those operations: begin at `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription`, preserve exactly one summary row, and finish with `local_visibility_lsn`.
- **Alternative/trade-off:** For sql-repl-01 Exercise 9, the chosen form is justified by this lesson-specific rationale: Define user-visible consistency: immediate own-write visibility, maximum staleness, or best effort. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add one source row with a new `local_visibility_lsn`; verify the result gains exactly one row carrying that `local_visibility_lsn` value.

## Exercise 10 — Multi-writer conflicts

Wall clocks skew, so last timestamp wins can discard a causally later change.
Prefer single-writer ownership; otherwise use expected versions, deterministic
domain merge, and quarantine irreconcilable conflicts with source evidence.

Do not advance checkpoints silently past unresolved data. Provide canonical
snapshot/replay repair, idempotency, authorization, and an audit of the choice.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 10, read the target keys from `pro_replication_lab.projection` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-repl-01 Exercise 10, expected output: the command tag and an independently counted set of affected `status` values. The final columns are `aggregate_key`, `aggregate_version`, and `status`. The final order is `p.aggregate_key`.
- **Independent verification:** For sql-repl-01 Exercise 10, materialize the intended `status` target set first; require the command tag/`RETURNING` set to match it, then query `pro_replication_lab.projection` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `status` values in both cases.
- **Intermediate relation check:** For sql-repl-01 Exercise 10, materialize the intended `status` target set first; require the command tag/`RETURNING` set to match it, then query `pro_replication_lab.projection` again and prove rollback or idempotent retry.
- **Clause check:** For sql-repl-01 Exercise 10, the solution actually uses `WITH`, `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_replication_lab.projection`, preserve one row per `status`, and finish with `aggregate_key`, `aggregate_version`, and `status` ordered by `p.aggregate_key`.
- **Alternative/trade-off:** For sql-repl-01 Exercise 10, the chosen form is justified by this lesson-specific rationale: Wall clocks skew, so last timestamp wins can discard a causally later change. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `status` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `status` values in both cases.

## Exercise 11 — DDL compatibility sequencing

Matrix publisher, subscriber, decoder/apply, and old/new application schemas.
Add nullable columns first, deploy tolerant readers/writers, backfill/reconcile,
validate constraints, and remove only after every consumer stops using old
shape.

Defaults, generated values, replica identity, types, row filters, and column
lists need explicit tests. DDL requires its own ordered deployment channel.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 11, read from the inline `VALUES` fixture. Build the answer toward `phase`, and `compatibility_gate`; keep `phase` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-repl-01 Exercise 11, expected output: one row per `phase`. The final columns are `phase`, and `compatibility_gate`. The final order is `phase`.
- **Independent verification:** For sql-repl-01 Exercise 11, reselect the returned keys directly from the source; require unique `phase` where the expected grain is one row per key and confirm the projected `phase`, and `compatibility_gate` against the inline `VALUES` fixture. Add one source row with a new `phase`; verify the result gains exactly one row carrying that `phase` value.
- **Intermediate relation check:** For sql-repl-01 Exercise 11, check `phase` before applying the row cap.
- **Clause check:** For sql-repl-01 Exercise 11, the solution actually uses `WITH`, `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `phase`, and finish with `phase`, and `compatibility_gate` ordered by `phase`.
- **Alternative/trade-off:** For sql-repl-01 Exercise 11, the chosen form is justified by this lesson-specific rationale: Matrix publisher, subscriber, decoder/apply, and old/new application schemas. Evaluate another form against the concrete expected result (one row per `phase`) and the verification above.
- **Edge case:** Add one source row with a new `phase`; verify the result gains exactly one row carrying that `phase` value.

## Exercise 12 — Failback and reseed

Protect a verified new-primary backup and keep the old primary fenced. Compare
timelines/LSNs and use rewind only when prerequisites/WAL exist; otherwise
rebuild. Recreate and verify replicas, slots, subscriptions, and checkpoints.

Before routing writes, reconcile data and critical queries, establish backup/HA,
monitor retry/lag/conflicts, and record authority/evidence. A diverged former
primary cannot be restored by reversing DNS.

### Reasoning and verification

- **Inputs/evidence:** For sql-repl-01 Exercise 12, use `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-repl-01 Exercise 12, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
- **Independent verification:** For sql-repl-01 Exercise 12, restore into an isolated target and reconcile `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-repl-01 Exercise 12, restore into an isolated target and reconcile `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-repl-01 Exercise 12, the solution actually uses `WITH`, and `FROM`. Read only those operations: begin at `pg_catalog.pg_replication_slots`, `pg_catalog.pg_publication`, and `pg_catalog.pg_subscription`, preserve one row per `artifact_name` and `restored_object`, and finish with `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
- **Alternative/trade-off:** For sql-repl-01 Exercise 12, the chosen form is justified by this lesson-specific rationale: Protect a verified new-primary backup and keep the old primary fenced. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Edge cases

- Poison events need quarantine without blocking every later aggregate forever.
- Publisher concurrency needs leases/locks and retry visibility.
- Synchronous replication trades latency/availability for lower acknowledged
  data-loss risk.
- Logical subscriber conflicts require explicit ownership.
