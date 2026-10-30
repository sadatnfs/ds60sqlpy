# SQL-OPS-02: Backup, Restore, and Recovery Rehearsals

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-ops-02**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-ops-02/lesson/workspace/sql/professional/lessons/sql_ops_02_backup_restore_recovery.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-ops-02
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

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

These worked excerpts come from `sql/professional/lessons/sql_ops_02_backup_restore_recovery.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

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
  account_id bigint NOT NULL REFERENCES pro_recovery_lab.source_accounts (account_id),
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
   **Inputs/evidence:** For sql-ops-02 Exercise 1, canonicalize source and restored column, constraint, and index semantics from information schema and PostgreSQL catalogs, excluding volatile OIDs and generated object names before comparing or hashing.
   **Expected result/shape:** For sql-ops-02 Exercise 1, expected output: ordered semantic rows with contract side, relation role, object kind, item order/name, and JSON definition, followed by one fingerprint row where source and restored hashes match and `mismatch_rows = 0`.
   **Verify:** For sql-ops-02 Exercise 1, compare visible canonical rows before hashes, then alter a default, constraint, and index separately and require each change to produce diagnosable mismatch rows while an OID change remains outside the contract.
2. **Corruption control:** make verification fail, roll back only the injected
   change, and show it passes again.
   **Inputs/evidence:** For sql-ops-02 Exercise 2, record source/restored checksums and counts, corrupt one restored amount after a savepoint, compare again, roll back to that savepoint, and run the comparison a third time.
   **Expected result/shape:** For sql-ops-02 Exercise 2, expected output: baseline, corrupted, and after-savepoint-rollback observations; equality is true, false, then true, with row counts unchanged and the intentional mismatch explicitly observed.
   **Verify:** For sql-ops-02 Exercise 2, supplement digests with row counts and key-level detail, corrupt a second chosen key to prove the detail query identifies it, and require the post-rollback comparison to return to the reviewed baseline.
3. **RPO/RTO:** choose complementary recovery and availability mechanisms from
   written requirements.
   **Inputs/evidence:** For sql-ops-02 Exercise 3, enter explicit service RPO and RTO requirements in `pro_recovery_lab.recovery_plan`, then choose backup and availability strategies separately with their limits.
   **Expected result/shape:** For sql-ops-02 Exercise 3, expected output: one row per service with `service_name`, `rpo`, `rto`, `backup_strategy`, and `availability_strategy`, ordered by service; the example targets five-minute RPO and thirty-minute RTO.
   **Verify:** For sql-ops-02 Exercise 3, map RPO to recoverable data age and RTO to restore-through-application-readiness time, then remove replicas and backups in separate thought experiments to prove neither substitutes for the other.
4. **Logical rehearsal:** write exact isolated dump/restore/verify/cleanup steps.
   **Inputs/evidence:** For sql-ops-02 Exercise 4, review literal dump/create/restore commands outside this transaction and use the SQL matrix to specify evidence for target isolation, catalogs, data, application behavior, and cleanup.
   **Expected result/shape:** For sql-ops-02 Exercise 4, expected output: seven ordered rows with `phase_number`, `phase_name`, and `required_evidence`, covering dump, target creation, restore, catalogs/security, data, application checks, and cleanup; no external command runs here.
   **Verify:** For sql-ops-02 Exercise 4, execute only in a separately created disposable database after peer review, reconcile rows and semantic objects including owners/grants and sequence state, and block completion on any failed phase.
5. **PITR:** connect base backup, WAL, timelines, target, retention, and proof.
   **Inputs/evidence:** For sql-ops-02 Exercise 5, model the PITR evidence chain from a compatible base backup through every required WAL segment, timeline history, target specification, retention overlap, and recovered-state validation.
   **Expected result/shape:** For sql-ops-02 Exercise 5, expected output: six ordered rows with `component_number`, `component`, and `required_evidence`; the lesson records a recovery plan and does not configure archiving.
   **Verify:** For sql-ops-02 Exercise 5, remove one required WAL segment and then the usable base backup as separate negative controls, and assert both scenario results mark the target unrecoverable before application validation.
6. **Evidence:** define why exit zero is necessary but insufficient.
   **Inputs/evidence:** For sql-ops-02 Exercise 6, classify command exit, artifact manifest, isolated restore, catalog/data reconciliation, and application smoke tests as separate evidence layers.
   **Expected result/shape:** For sql-ops-02 Exercise 6, expected output: five ordered rows with `layer_number`, `evidence_layer`, `what_it_proves`, and `what_it_does_not_prove`; exit zero proves only that the backup program reported success.
   **Verify:** For sql-ops-02 Exercise 6, inject a valid-looking but incomplete artifact or omit one critical restored object, and prove early command evidence can pass while later reconciliation blocks a recoverable decision.
7. **Encryption/custody:** cover artifacts, manifests, keys, access, rotation,
   transport, retention, and deletion evidence.
   **Inputs/evidence:** For sql-ops-02 Exercise 7, populate `pro_recovery_lab.artifact_controls` for logical dumps, base backups, and WAL archives, separating encryption, integrity manifest, key owner, and restore role.
   **Expected result/shape:** For sql-ops-02 Exercise 7, expected output: three ordered rows with `artifact_kind`, `encrypted`, `integrity_manifest`, `key_owner`, and `restore_role`; every restorable artifact is encrypted and has integrity evidence.
   **Verify:** For sql-ops-02 Exercise 7, verify key custody is distinct from restore authorization, extend the review to manifest/key records, and rehearse rotation and deletion without making retained backups permanently unrestorable.
8. **Completeness:** verify sequences, large objects, owners, ACLs, defaults,
   extensions, security metadata, and external configuration.
   **Inputs/evidence:** For sql-ops-02 Exercise 8, classify restored data/schema, roles/memberships, sequences/identity, extensions, and external configuration by their authoritative source rather than assuming one artifact contains everything.
   **Expected result/shape:** For sql-ops-02 Exercise 8, expected output: five ordered baseline rows with `component` and `expected_source`; the accompanying checklist extends coverage to large objects, default privileges, and security labels when required.
   **Verify:** For sql-ops-02 Exercise 8, mark each required component as artifact-contained, separately captured, or rebuilt for the chosen backup format, and fail the checklist when any component lacks both a source and validation query.
9. **Major version:** compare logical restore and `pg_upgrade`, then plan
   compatibility, collation, statistics, application, cutover, and rollback.
   **Inputs/evidence:** For sql-ops-02 Exercise 9, query the current database for server version number plus database collation/ctype and separately review logical-restore versus binary-upgrade compatibility, extension, statistics, driver, and rollback evidence.
   **Expected result/shape:** For sql-ops-02 Exercise 9, expected output: exactly one local capability row with `server_version`, `server_version_num`, `datcollate`, and `datctype`; the broader major-version plan remains explicitly review-only.
   **Verify:** For sql-ops-02 Exercise 9, capture the same capability row in the isolated target and block cutover on extension incompatibility, collation drift, missing ANALYZE evidence, or failed driver/application tests even when upgrade tooling exits zero.
10. **Selective restore:** inventory dependencies and state when full isolated
    restore is safer.
   **Inputs/evidence:** For sql-ops-02 Exercise 10, inspect `pg_constraint`, `pg_class`, and `pg_namespace` for recovery-lab relations, then extend the selective-restore inventory to referenced types, functions, sequences, privileges, and downstream consumers.
   **Expected result/shape:** For sql-ops-02 Exercise 10, expected output: one row per semantic constraint dependency with `relation_name`, `constraint_type`, and `dependency_contract`, ordered by all three fields.
   **Verify:** For sql-ops-02 Exercise 10, prove every referenced and referencing object is restored or deliberately remapped, remove one required dependency in an isolated target, and choose a full isolated restore when closure cannot be established.
11. **Capacity:** measure transfer, CPU, I/O, parallelism, WAL, rebuild,
    validation, bottlenecks, and safety margin.
   **Inputs/evidence:** For sql-ops-02 Exercise 11, fill `pro_recovery_lab.capacity_budget` with measured transfer, restore, verification, and routing phases, recording duration, peak bytes, and evidence notes at representative scale.
   **Expected result/shape:** For sql-ops-02 Exercise 11, expected output: four ordered rows with `phase`, `measured_seconds`, `peak_bytes`, and `evidence_note`; NULL measurements in the starter matrix are explicit work still to complete, not passing evidence.
   **Verify:** For sql-ops-02 Exercise 11, sum the measured critical path plus named safety margin against RTO and separately record throughput, CPU, I/O, parallelism, WAL, and free-space headroom instead of linearly extrapolating a tiny fixture.
12. **Game day:** assign roles and preserve chronology, decisions, injected
    failures, achieved objectives, gaps, cleanup, owners, and next rehearsal.
   **Inputs/evidence:** For sql-ops-02 Exercise 12, use the inline authority map for incident commander, recovery operator, application owner, and observer, then attach those roles to a timestamped recovery game-day record.
   **Expected result/shape:** For sql-ops-02 Exercise 12, expected output: four ordered rows with `role_name` and `responsibility`; the completed record also captures decisions, injected failures, achieved RPO/RTO, gaps, cleanup, owners, and next rehearsal date.
   **Verify:** For sql-ops-02 Exercise 12, require exactly one accountable role for every action, link each injected failure to observed evidence, assign owner/due date to every gap, and compare achieved RPO/RTO with Exercise 3 requirements.

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

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

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
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
