# SQL-OPS-02 — Backup, Restore, and Recovery Rehearsals

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-43` and `sql-ops-01`
- **Prerequisites:** [SQL Day 43 backup and recovery](../../postgres-60day/companion-guides/day43_backup_recovery.md),
  [SQL-OPS-01](sql_ops_01_indexes_statistics_maintenance.md), constraints, and
  a disposable `advanced_sql_training` database.
- **Default artifact:** [learner SQL](../lessons/sql_ops_02_backup_restore_recovery.sql)
  runs offline and rolls back a restore-verification simulation.
- **Solutions:** [reasoning](../solutions/sql_ops_02_backup_restore_recovery_solutions.md) ·
  [executable SQL](../solutions/sql_ops_02_backup_restore_recovery_solutions.sql)

Run the safe default on Windows, macOS, or Linux:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_ops_02_backup_restore_recovery.sql
```

It creates no files, databases, roles, extensions, or configuration changes.
The optional command-line rehearsal below requires explicit authority, disk
space, and an exact disposable target.

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

2. Open **SQL-OPS-02 — Backup, Restore, and Recovery Rehearsals** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-ops-02/lesson/workspace/sql/professional/lessons/sql_ops_02_backup_restore_recovery.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Backup/restore commands are capability-sensitive and are not hidden inside a transaction. Use only the lesson's isolated dump/rehearsal targets, inspect every path first, and treat a successful restore plus verification queries—not merely a created file—as success.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_ops_02_backup_restore_recovery.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_ops_02_backup_restore_recovery.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Logical backup, Custom format, Physical base backup, WAL, PITR, Timeline. Its worked SQL reads or creates `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, `pro_recovery_lab.backup_manifest`, `pro_recovery_lab.restored_accounts`, `pro_recovery_lab.restored_entries`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: The SQL learner path creates source and independent restored relations, records a deterministic manifest, copies fixture data, and compares ordered MD5 digests and row counts. MD5 here detects accidental fixture drift; it is not a cryptographic authenticity/signing design.
The first runnable example has a concrete contract: Example 1 must print the expected DDL command tag for `pro_recovery_lab.source_accounts`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state. Its final projection is the columns written in the final `SELECT`. Verify the command tag in `pg_catalog`/`information_schema`, run one accepted value and one value the declared rule rejects, and confirm the lesson rollback removes the course-owned object. Where this query can emit `NULL`, identify the exact source expression and explain whether the output preserves, classifies, or rejects it.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/professional/lessons/sql_ops_02_backup_restore_recovery.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TABLE pro_recovery_lab.source_accounts (
    account_id bigint PRIMARY KEY,
    account_key text NOT NULL UNIQUE,
    display_name text NOT NULL
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must print the expected DDL command tag for `pro_recovery_lab.source_accounts`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

### Example 2

```sql
CREATE TABLE pro_recovery_lab.source_entries (
    entry_id bigint PRIMARY KEY,
    account_id bigint NOT NULL
        REFERENCES pro_recovery_lab.source_accounts (account_id),
    amount numeric(12, 2) NOT NULL,
    occurred_at timestamptz NOT NULL,
    note text NOT NULL
);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 2 must print the expected DDL command tag for `pro_recovery_lab.source_accounts`, and `pro_recovery_lab.source_entries`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

## Learning objectives

- Distinguish logical dumps, physical base backups, WAL archiving, replication,
  and point-in-time recovery (PITR).
- Define recovery point objective (RPO) and recovery time objective (RTO).
- Build manifests, checksums, structural/application verification, and isolated
  restore cleanup; explain why only a verified restore proves recoverability.

## Vocabulary and concepts

- **Logical backup:** SQL/object representation produced by `pg_dump`.
- **Custom format:** archive format restored selectively/parallel with
  `pg_restore`.
- **Physical base backup:** copy of a PostgreSQL cluster's storage state.
- **WAL:** write-ahead log recording changes needed for crash/PITR recovery.
- **PITR:** restore a base backup then replay continuous WAL to a target.
- **Timeline:** recovery history branch created after promotion/recovery.
- **RPO:** maximum acceptable data-loss interval.
- **RTO:** target time to restore service.
- **Restore rehearsal:** isolated, timed recovery plus verification and cleanup.
- **Manifest:** backup identity, source/version/time, scope, counts/checksums,
  retention, and ownership evidence.

## Worked example / walkthrough

The SQL learner path creates source and independent restored relations, records
a deterministic manifest, copies fixture data, and compares ordered MD5 digests
and row counts. MD5 here detects accidental fixture drift; it is not a
cryptographic authenticity/signing design.

Data equality is insufficient. The script also checks restored keys and foreign
keys. A real rehearsal verifies columns/types/defaults, constraints, indexes,
sequences, owners, grants, RLS, routines/triggers, extensions, large objects,
application smoke queries, and monitoring. `CREATE TABLE ... LIKE` is only a
simulation; `pg_restore` must be tested for the real artifact.

RPO/RTO drive strategy. A nightly dump cannot satisfy five-minute RPO. Physical
base backups plus continuous WAL can support PITR, but archived WAL is useless
without a compatible usable base backup and tested restore procedure.
Replication improves availability but commonly replicates accidental deletes;
it is not an independent retained backup.

The timeline chooses the last confirmed good event before a destructive change.
PITR replays to a timestamp/transaction/LSN on a separate instance, verifies the
result, and only then follows a controlled cutover. Time synchronization and
target ambiguity require careful evidence.

The read-only posture query reports WAL/archive mode and whether the server is
recovering. It does not print `archive_command`, which can contain sensitive
paths/commands, and it never uses `ALTER SYSTEM`, restart, promotion, or restore
settings.

### Optional logical restore rehearsal

These commands are **operator-only**. Confirm the exact database names first.
They create an ignored local artifact and a disposable database. Never point
`--clean`, `dropdb`, or course reset commands at a valuable database.

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force .\artifacts\backups
pg_dump --format=custom --no-owner --no-privileges --file=.\artifacts\backups\advanced_sql_training.dump advanced_sql_training
createdb ds60_restore_rehearsal
pg_restore --exit-on-error --clean --if-exists --no-owner --no-privileges --dbname=ds60_restore_rehearsal .\artifacts\backups\advanced_sql_training.dump
psql -X -v ON_ERROR_STOP=1 -d ds60_restore_rehearsal -f sql\postgres-60day\00_verify.sql
dropdb ds60_restore_rehearsal
Remove-Item .\artifacts\backups\advanced_sql_training.dump
```

macOS/Linux:

```bash
mkdir -p artifacts/backups
pg_dump --format=custom --no-owner --no-privileges --file=artifacts/backups/advanced_sql_training.dump advanced_sql_training
createdb ds60_restore_rehearsal
pg_restore --exit-on-error --clean --if-exists --no-owner --no-privileges --dbname=ds60_restore_rehearsal artifacts/backups/advanced_sql_training.dump
psql -X -v ON_ERROR_STOP=1 -d ds60_restore_rehearsal -f sql/postgres-60day/00_verify.sql
dropdb ds60_restore_rehearsal
rm -f artifacts/backups/advanced_sql_training.dump
```

Do not execute this block merely to complete the lesson. It assumes local
authentication and enough disk. Review whether `00_verify.sql` targets the
objects included in the dump. A schema-scoped dump needs its own verifier.

### DBA-only physical/PITR boundary

A real PITR lab uses a separate disposable PostgreSQL instance/container,
version-compatible base backup, continuous archived WAL, `pg_verifybackup`,
restore configuration and target, startup/replay logs, promotion decision, and
post-recovery verification. It changes server configuration and consumes
substantial disk/time, so it is not run by course SQL. A container image may
need one connected pull; after caching, the lab can be offline. Never rehearse
PITR by overwriting the active course cluster.

## Exercises

Complete all twelve prompts. Begin with schema fingerprinting, corruption negative control,
RPO/RTO strategy, exact isolated logical restore plan, PITR/retention reasoning,
and evidence standards; then cover custody, completeness, major versions,
selective recovery, capacity, and game days. Record backup and restore elapsed
time, artifact size, server/tool versions, verification results, and cleanup
when performing an approved optional rehearsal.

Treat commands as reviewed plans unless you have explicit authority and an
isolated target:

1. **Schema fingerprint:** verify semantic structure in addition to data.
   **Inputs/evidence:** For sql-ops-02 Exercise 1, read from `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`. Compute `constraints` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-ops-02 Exercise 1, expected output: exactly one aggregate summary row. The final columns are `constraints`.
   **Verify:** For sql-ops-02 Exercise 1, evaluate each of `row_count` in a separate control `SELECT` over `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; require one final row and compare every value. Add one source row with a new `constraints`; verify the result gains exactly one row carrying that `constraints` value.
2. **Corruption control:** make verification fail, roll back only the injected
   change, and show it passes again.
   **Inputs/evidence:** For sql-ops-02 Exercise 2, read the target keys from `pro_recovery_lab.restored_records` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-ops-02 Exercise 2, expected output: the command tag and an independently counted set of affected `affected_row_count` values. The final columns are `affected_row_count`, and `command_tag`.
   **Verify:** For sql-ops-02 Exercise 2, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `pro_recovery_lab.restored_records` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.
3. **RPO/RTO:** choose complementary recovery and availability mechanisms from
   written requirements.
   **Inputs/evidence:** For sql-ops-02 Exercise 3, use `pro_recovery_lab.recovery_plan` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-ops-02 Exercise 3, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `service_name`, `rpo`, `rto`, `backup_strategy`, and `availability_strategy`. The final order is `rp.service_name`.
   **Verify:** For sql-ops-02 Exercise 3, restore into an isolated target and reconcile `pro_recovery_lab.recovery_plan` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
4. **Logical rehearsal:** write exact isolated dump/restore/verify/cleanup steps.
   **Inputs/evidence:** For sql-ops-02 Exercise 4, use `ds60_restore_rehearsal` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-ops-02 Exercise 4, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
   **Verify:** For sql-ops-02 Exercise 4, restore into an isolated target and reconcile `ds60_restore_rehearsal` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
5. **PITR:** connect base backup, WAL, timelines, target, retention, and proof.
   **Inputs/evidence:** For sql-ops-02 Exercise 5, use `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-ops-02 Exercise 5, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
   **Verify:** For sql-ops-02 Exercise 5, restore into an isolated target and reconcile `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
6. **Evidence:** define why exit zero is necessary but insufficient.
   **Inputs/evidence:** For sql-ops-02 Exercise 6, complete the evidence written analysis and support its claims with read-only evidence from `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-ops-02 Exercise 6, expected output: a completed the evidence written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
   **Verify:** For sql-ops-02 Exercise 6, check the evidence written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
7. **Encryption/custody:** cover artifacts, manifests, keys, access, rotation,
   transport, retention, and deletion evidence.
   **Inputs/evidence:** For sql-ops-02 Exercise 7, read from `pro_recovery_lab.artifact_controls`. Build the answer toward `encryptioncustody_answer`; keep `encryptioncustody_answer` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-02 Exercise 7, expected output: one row per `encryptioncustody_answer`. The final columns are `encryptioncustody_answer`. The final order is `artifact_kind`.
   **Verify:** For sql-ops-02 Exercise 7, reselect the returned keys directly from the source; require unique `encryptioncustody_answer` where the expected grain is one row per key and confirm the projected `encryptioncustody_answer` against `pro_recovery_lab.artifact_controls`. Add one source row with a new `encryptioncustody_answer`; verify the result gains exactly one row carrying that `encryptioncustody_answer` value.
8. **Completeness:** verify sequences, large objects, owners, ACLs, defaults,
   extensions, security metadata, and external configuration.
   **Inputs/evidence:** For sql-ops-02 Exercise 8, read from the inline `VALUES` fixture. Build the answer toward `component`, and `expected_source`; keep `component` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-02 Exercise 8, expected output: one row per `component`. The final columns are `component`, and `expected_source`. The final order is `component`.
   **Verify:** For sql-ops-02 Exercise 8, reselect the returned keys directly from the source; require unique `component` where the expected grain is one row per key and confirm the projected `component`, and `expected_source` against the inline `VALUES` fixture. Add one source row with a new `component`; verify the result gains exactly one row carrying that `component` value.
9. **Major version:** compare logical restore and `pg_upgrade`, then plan
   compatibility, collation, statistics, application, cutover, and rollback.
   **Inputs/evidence:** For sql-ops-02 Exercise 9, use `pg_catalog.pg_database`, and `pg_upgrade` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-ops-02 Exercise 9, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `server_version`, `server_version_num`, `datcollate`, and `datctype`.
   **Verify:** For sql-ops-02 Exercise 9, restore into an isolated target and reconcile `pg_catalog.pg_database`, and `pg_upgrade` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
10. **Selective restore:** inventory dependencies and state when full isolated
    restore is safer.
   **Inputs/evidence:** For sql-ops-02 Exercise 10, use `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
   **Expected result/shape:** For sql-ops-02 Exercise 10, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `contype`, and `dependency_contract`. The final order is `rel.relname, con.contype, dependency_contract`.
   **Verify:** For sql-ops-02 Exercise 10, restore into an isolated target and reconcile `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
11. **Capacity:** measure transfer, CPU, I/O, parallelism, WAL, rebuild,
    validation, bottlenecks, and safety margin.
   **Inputs/evidence:** For sql-ops-02 Exercise 11, read from `pro_recovery_lab.capacity_budget`. Build the answer toward `capacity_answer`; keep `capacity_answer` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-02 Exercise 11, expected output: one row per `capacity_answer`. The final columns are `capacity_answer`. The final order is `phase`.
   **Verify:** For sql-ops-02 Exercise 11, reselect the returned keys directly from the source; require unique `capacity_answer` where the expected grain is one row per key and confirm the projected `capacity_answer` against `pro_recovery_lab.capacity_budget`. Add one source row with a new `capacity_answer`; verify the result gains exactly one row carrying that `capacity_answer` value.
12. **Game day:** assign roles and preserve chronology, decisions, injected
    failures, achieved objectives, gaps, cleanup, owners, and next rehearsal.
   **Inputs/evidence:** For sql-ops-02 Exercise 12, read from the inline `VALUES` fixture. Build the answer toward `role_name`, and `responsibility`; keep `role_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-ops-02 Exercise 12, expected output: one row per `role_name`. The final columns are `role_name`, and `responsibility`. The final order is `role_name`.
   **Verify:** For sql-ops-02 Exercise 12, reselect the returned keys directly from the source; require unique `role_name` where the expected grain is one row per key and confirm the projected `role_name`, and `responsibility` against the inline `VALUES` fixture. Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.

## Self-check

- Does the safe default create no host artifact or persistent schema?
- Are row counts and ordered content digests independently compared?
- Are constraints and application queries part of restore verification?
- Can the chosen strategy meet the stated RPO and RTO?
- Are base backup and every required WAL segment retained together?
- Is recovery tested on an isolated target before cutover?
- Are destructive target names exact and reviewed?
- Does cleanup remove the rehearsal database and local dump when authorized?

## Common pitfalls

- A successful backup command is not proof that restore works.
- Testing restore over the source destroys evidence and increases outage risk.
- Logical dumps do not provide physical PITR and may omit cluster-global roles
  and tablespaces.
- Replication repeats logical mistakes and is not retained independent backup.
- Missing one required WAL segment can break a PITR chain.
- Tool/server version compatibility and extensions must be rehearsed.
- Checksums without deterministic ordering are unstable.
- Counts can match while values, constraints, owners, or sequences are wrong.
- Backups can contain sensitive data; encryption, access, retention, and
  disposal are part of the design.

## Next step

Use [SQL-TEST-01](sql_test_01_contracts_migrations.md) to turn restore checks
into fail-fast contracts, then combine migrations, security grants, indexes,
and application smoke tests in a timed local recovery game day. Optional
physical/PITR work remains an explicitly approved isolated specialization.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-ops-02 — Backup, Restore, and Recovery Rehearsals.

I have completed the direct catalog prerequisites: `sql-43`, `sql-ops-01`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_ops_02_backup_restore_recovery.md
- Answer-free learner SQL: sql/professional/lessons/sql_ops_02_backup_restore_recovery.sql

Key terms to teach in context: Logical backup, Custom format, Physical base backup, WAL, PITR, Timeline. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The SQL learner path creates source and independent restored relations, records a deterministic manifest, copies fixture data, and compares ordered MD5 digests and row counts. MD5 here detects accidental fixture drift; it is not a cryptographic authenticity/signing design.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-ops-02/ working copy. Never point setup, reset, DDL, or DML
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
