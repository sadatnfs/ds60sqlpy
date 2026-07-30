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

Complete all six prompts: schema fingerprinting, corruption negative control,
RPO/RTO strategy, exact isolated logical restore plan, PITR/retention reasoning,
and evidence standards. Record backup and restore elapsed time, artifact size,
server/tool versions, verification results, and cleanup when performing an
approved optional rehearsal.

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
