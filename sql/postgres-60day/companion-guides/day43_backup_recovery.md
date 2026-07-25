# Day 43 — Logical Backup and Recovery Patterns

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 42 — data quality and validation](day42_data_quality_validation.md)
- **Artifacts:** [learner SQL](../day43_backup_recovery.sql) ·
  [solution reasoning](../solutions/day43_solutions.md) ·
  [executable solution](../solutions/day43_solutions.sql)

## Learning objectives

- Stage and validate a logical extract before merging it.
- Choose between server-side `COPY` and client-side `psql` `\copy`.

## Vocabulary and concepts

- **Logical backup:** a representation of database objects or rows as SQL or
  data records.
- **Staging table:** an isolated landing relation used for validation.
- **Idempotent merge:** a repeatable load with a defined conflict policy.

## Worked example / walkthrough

Use `\copy (SELECT ... WHERE ...) TO ...` from a path owned by the learner,
import into a staging table, and compare count, keys, types, and sample rows.
Only then merge inside `BEGIN`/`ROLLBACK` with an explicit email conflict
policy.

## Exercises

Complete the prompts in the [learner SQL](../day43_backup_recovery.sql). Repeat
the staged merge and prove it does not create duplicate customers.

## Self-check

- Is the file path interpreted on the intended client or database server?
- Are validation and conflict ownership defined before any persistent restore?

## Next step

Continue to [Day 44 — monitoring and diagnostics](day44_monitoring_diagnostics.md).

## Deep dive and reference

## What you will learn

- Distinguish server-side `COPY` from client-side `psql` `\copy`.
- Restore through a staging table with explicit validation.
- Merge staged customers idempotently with `ON CONFLICT`.

## How the learner script works

The rollback-only SQL creates a temporary `customers_stg` table shaped like
`training.customers`, compares base and staging counts, and leaves file-copy
commands commented because paths and permissions are environment-owned.

`COPY table TO '/path'` reads or writes on the database server and commonly
requires elevated privileges. `\copy` is a `psql` command that reads or writes
on the learner's Windows, macOS, or Linux client.

## Practice — match the learner prompts exactly

1. Export and import a filtered customer subset. A SQL `COPY table` cannot add a
   `WHERE` clause, so use `\copy (SELECT ...) TO ...` and the corresponding
   staged import.
2. In a transaction, restore staged customers into `training.customers` and use
   `ON CONFLICT (email) DO UPDATE` for the reviewed attributes.

## Environment and safety limits

- The learner must choose a path they own. Windows drive/path syntax, directory
  creation, and permissions cannot be prescribed by the repository.
- Stage first; compare counts, keys, types, and representative rows before
  merging.
- Email is the schema's unique conflict key, but a real restore policy must
  decide which source wins for every column.
- Wrap the merge in `BEGIN`/`ROLLBACK` until the result is reconciled.

Logical export is not point-in-time recovery. Production PITR needs tested base
backups, WAL archiving, retention, encryption, and measured RPO/RTO outside this
SQL-only lesson.
