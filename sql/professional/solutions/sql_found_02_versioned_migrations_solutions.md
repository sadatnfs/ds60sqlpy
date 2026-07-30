# SQL-FOUND-02 Solutions — Versioned Migrations

Run the complete solution from the repository root:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_found_02_versioned_migrations_solutions.sql
```

It resets the isolated fixture, verifies versions 1–5, implements exercise
versions 6–8, checks them, and removes `pro_migration_lab`.

## Exercise 1 — Deterministic manifest

The manifest must order by version explicitly:

```sql
SELECT
    sm.migration_id,
    sm.migration_name,
    sm.content_tag
FROM pro_migration_lab.schema_migrations AS sm
WHERE sm.migration_id BETWEEN 1 AND 5
ORDER BY sm.migration_id;
```

The solution also compares `array_agg(... ORDER BY migration_id)` with
`ARRAY[1,2,3,4,5]`. A row count of five is insufficient because versions
`1,2,3,4,9` also have a count of five.

The fixture's `content_tag` is educational metadata, not a cryptographic file
checksum. A production runner should calculate a checksum from migration bytes,
store it on first application, and fail if the same applied version later has
different bytes.

## Exercise 2 — Compatibility and deployment order

At version 2, old storage remains in `urgency_label`, the new
`priority_code` is nullable, and the view returns
`COALESCE(priority_code, urgency_label)`. Existing rows therefore retain a
priority before backfill, while new application code can begin writing the new
column.

A safe high-level order is:

1. Deploy the additive schema and dual-compatible view.
2. Deploy application readers that accept the stable interface and writers that
   populate the new representation while old writers can still operate.
3. Backfill in measured batches and reconcile old versus new values.
4. Stop or upgrade every old writer.
5. Enforce the new constraints and remove the old representation.

Real deployment gates require traffic, lock, error, replica-lag, and data-quality
evidence. The tiny fixture proves logic, not production timing.

## Exercise 3 — Versions 6–8

The solution uses three separate transactions:

- Version 6 adds nullable `assigned_team`.
- Version 7 backfills `high`/`critical` to `response` and everything else to
  `general`, then asserts no NULL remains.
- Version 8 adds the default, `NOT NULL`, and allowed-values `CHECK`.

This separation creates an application compatibility window. A single
transaction containing all three statements would be atomic, but it would not
allow independently deployed application versions or a large online backfill
to coexist.

The exercise uses migrations 6–8 rather than changing a prior file. Metadata is
inserted last in each transaction so a failed body cannot advertise success.

## Exercise 4 — Boundaries and recovery

Examples that require an explicit nontransactional boundary include:

- `CREATE DATABASE`
- `VACUUM`
- `CREATE INDEX CONCURRENTLY`

A capable runner marks and executes such a step deliberately; it does not wrap
every file in a transaction and hope PostgreSQL accepts it. Operationally large
backfills may also deserve their own batched, restartable boundary even though
ordinary `UPDATE` is transactional.

A universal down migration is unsafe because deletion, aggregation, and
representation changes can lose information. External clients may also have
observed the new state. Rolling schema syntax backward does not reconstruct
discarded values or undo side effects. If an applied migration is wrong, freeze
it, assess impact, and normally ship a reviewed forward fix. Restore or rollback
is an evidence-based incident decision, not a filename convention.

## Edge cases and alternatives

- Parallel deployers need an advisory lock or a migration tool that serializes
  the manifest; this single-session fixture does not simulate a deployment race.
- `NOT VALID` reduces the initial validation work but does not make a malformed
  foreign key acceptable forever.
- A production backfill should be restartable and report progress, failed keys,
  WAL/replica impact, and reconciliation counts.
- Reference seeds need an ownership policy. `ON CONFLICT DO UPDATE` can overwrite
  operator-owned changes if ownership is not clear.
- An additive view contract helps readers, but writers need a deliberately
  compatible API, trigger, or application rollout plan of their own.

