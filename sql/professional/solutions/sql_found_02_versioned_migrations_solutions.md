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

## Exercise 5 — Retry after uncertain completion

Serialize the runner, begin a transaction, lock/read the manifest row, and
compare both recorded checksum and observed schema precondition. If neither
version nor column exists, apply DDL, verify its exact properties, then insert
metadata and commit. If both match, report “already applied.” If only one exists
or properties differ, stop for investigation.

`IF NOT EXISTS` is not a drift detector: it accepts any same-named object even
when its type, default, nullability, or ownership is wrong. Idempotency means
repeating the operation reaches the same verified state, not suppressing every
error.

## Exercise 6 — Low-lock index and constraint rollout

`CREATE INDEX CONCURRENTLY` must run outside a transaction block and can leave
an invalid index after interruption. Record progress, validity, locks, lag, and
disk before retrying or explicitly dropping only the known invalid artifact.
Attach it as a constraint in a later reviewed transaction when appropriate.

Add a CHECK as `NOT VALID` in a short transaction, observe that new writes are
still checked, remediate existing violations in batches, then run `VALIDATE
CONSTRAINT` separately. “Lower lock” is not “no impact”; define timeouts,
abort thresholds, and postcondition queries.

## Exercise 7 — Semantic drift report

Build expected rows with stable identities such as
`(schema, table, column, ordinal)` and compare them to catalog-derived observed
rows using full joins or `EXCEPT` in both directions. Canonicalize types with
`format_type`, expressions with `pg_get_expr`, constraints with catalog keys and
definitions, and indexes with semantic columns/predicate/operator classes.

Emit `missing`, `unexpected`, and `changed` rows in a deterministic order. Do
not hash OIDs, physical file locations, statistics, or generated names into the
contract unless they are deliberately contractual.

## Exercise 8 — Phase-specific recovery

During expand, old code should still work; recovery may be a forward fix while
the additive object remains. During dual-write/backfill, pause or fence writers
before choosing a source of truth and reconcile every key. During contract,
old writers must already be absent; re-enabling them can corrupt the new rule.

Record compatible application versions, traffic state, lock/lag/error evidence,
backup restore point, lossy transformations, and decision owner at each gate.
A schema rollback is unsafe once new-only writes or external side effects have
occurred unless their data path is explicitly reversible and verified.

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
