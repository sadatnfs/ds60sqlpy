# Day 43 — Solutions (Backup and Recovery)

We cover backup/restore strategies for PostgreSQL: logical backups (pg_dump/pg_restore), physical/base backups with WAL archiving, point‑in‑time recovery (PITR), and restore testing. We emphasize repeatability, automation, and verification.

Setup
- Logical: pg_dump (schema/data dumps), pg_restore for custom format (-Fc)
- Physical: pg_basebackup + WAL archiving (archive_mode=on; archive_command)
- Verify: restore on a clean instance; checksum/row counts; smoke queries

Exercise 1 — Logical backup and restore (single DB)
```bash
# Backup (custom format) — includes schema + data
pg_dump -h localhost -U app_user -d app_db -Fc -f /backups/app_db_$(date +%F).dump

# Restore to a new database
createdb -h localhost -U app_user app_db_restore
pg_restore -h localhost -U app_user -d app_db_restore -j 4 /backups/app_db_2026-01-13.dump
```
Notes
- -Fc enables parallel restore (-j workers) and selective object restore.
- For schema‑only: pg_dump -s; data‑only: pg_dump -a; include/exclude objects with -t/-n.

Exercise 2 — Table‑level logical backup/restore
```bash
# Dump a specific schema/table
pg_dump -h localhost -U app_user -d app_db -t public.orders -Fc -f /backups/orders_$(date +%F).dump
# Restore just that table into an existing DB (create table if missing)
pg_restore -h localhost -U app_user -d app_db_restore --create -t public.orders /backups/orders_2026-01-13.dump
```
Caveats
- Referential integrity: restoring a single table without dependencies may require order or constraints deferral.

Exercise 3 — Physical base backup (hot) with WAL archiving
postgresql.conf:
```conf
archive_mode = on
archive_command = 'test ! -f /wal_archive/%f && cp %p /wal_archive/%f'
wal_level = replica
max_wal_senders = 5
```
Take a base backup:
```bash
pg_basebackup -h localhost -U repl_user -D /backups/base_2026_01_13 -X stream -P -R
```
Explanation
- -X stream fetches WALs during backup; -R writes recovery.conf (PG12+: standby.signal) for standby configuration.
- Archive_command ships completed WAL segments for PITR.

Exercise 4 — Point‑in‑time recovery (PITR) workflow
1) Record target timestamp/LSN for recovery.
2) Stop Postgres and move aside data directory.
3) Restore base backup to data directory.
4) Ensure WAL archive is accessible at restore_command.
5) postgresql.conf (PG12+ recovery parameters):
```conf
restore_command = 'cp /wal_archive/%f %p'
recovery_target_time = '2026-01-13 21:15:00+00'
# or recovery_target_lsn = '0/16B6C80'
```
6) Start the server; it replays WALs to the target, then promotes.

Exercise 5 — Verify restores (crucial)
- Checksums: compare row counts per table: SELECT COUNT(*) FROM ...
- Sampling: compare checksums/hashes over key columns; run smoke queries/EXPLAINs.
- App‑level tests: run read‑only regression against the restore.

Automation and safety
- Rotate backups; test restores regularly (tabletop + real drills).
- Encrypt backups at rest; secure credentials; store copies offsite.
- Monitor archive lag, backup duration, and restore SLA.
