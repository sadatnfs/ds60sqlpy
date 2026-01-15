# Day 43 — Backup and Recovery: pg_dump, WAL, and PITR (Companion Guide)

Learning objectives
- Perform logical backups with pg_dump/pg_restore and understand formats
- Configure WAL archiving and base backups for point‑in‑time recovery (PITR)
- Test restores and document RPO/RTO for your environment

Why this matters
Backups you haven’t restored are not backups. Robust, tested backup/recovery is foundational for availability, compliance, and developer confidence.

Core concepts and deep dive
- Logical backups (pg_dump)
  - Per‑database, schema‑aware, version‑tolerant; great for migrations and small/medium DBs
  - Formats: plain SQL (‑Fp), custom (‑Fc), directory (‑Fd). Use custom/directory for parallel pg_restore
  - Include/exclude objects (‑n schema, ‑t table, ‑T exclude); data‑only/schema‑only
  - pg_restore can parallelize (‑j N), remap schemas, and filter objects on restore
- Physical base backups + WAL (PITR)
  - Base backup with pg_basebackup or filesystem snapshot while archiving WAL
  - WAL archiving: archive_mode=on; archive_command to copy WAL to durable storage
  - Recovery: restore base backup; set restore_command to fetch WAL; optional recovery_target_* (time, XID, name) for PITR
  - Create recovery signal file (Postgres 12+): standby.signal for replica; recovery.signal for PITR
- RPO/RTO
  - Recovery Point Objective: data loss tolerance (set by WAL archive cadence)
  - Recovery Time Objective: time to restore (base backup size, WAL volume, I/O)

Operational playbook
- Nightly logical dumps for critical schemas + continuous WAL archiving for full PITR
- Store backups off‑host and verify checksums; encrypt at rest
- Scheduled restore tests (e.g., monthly) into a staging environment; record duration and steps

Pitfalls
- Restoring into a different major version without pg_dump/pg_restore path matching; use the target version’s pg_restore
- Missing WAL segments due to misconfigured archive_command or retention policies
- Long unvacuumed transactions causing bloated base backups

Practice exercises
1) Create a custom‑format dump of the training database and restore it to a new database
2) Configure archive_mode and simulate archiving to a local directory; verify WAL files appear
3) Perform a PITR to a timestamp just before a simulated bad UPDATE

Further reading
- pg_dump/pg_restore: https://www.postgresql.org/docs/current/app-pgdump.html, https://www.postgresql.org/docs/current/app-pgrestore.html
- PITR: https://www.postgresql.org/docs/current/continuous-archiving.html
