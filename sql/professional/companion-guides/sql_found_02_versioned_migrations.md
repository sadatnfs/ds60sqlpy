# SQL-FOUND-02 — Versioned Schema Migrations and Safe Evolution

## Level and prerequisites

- **Level:** Intermediate
- **Catalog prerequisite:** `sql-found-01`
- **Prerequisites:** [SQL-FOUND-01 — relational design](sql_found_01_relational_design.md),
  transactions, constraints, and permission to create/drop an isolated schema
  in `advanced_sql_training`.
- **Artifacts:** [learner SQL](../lessons/sql_found_02_versioned_migrations.sql) ·
  [fixture migrations](../fixtures/migrations/README.md) ·
  [solution reasoning](../solutions/sql_found_02_versioned_migrations_solutions.md) ·
  [executable solution](../solutions/sql_found_02_versioned_migrations_solutions.sql)

Run from the repository root in Windows PowerShell, macOS, or Linux:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_found_02_versioned_migrations.sql
```

That command drops and recreates only `pro_migration_lab`, upgrades it through
five versions, verifies it, and drops it on normal completion. If you interrupt
the script, run the explicit
[`cleanup.sql`](../fixtures/migrations/cleanup.sql) command shown in the
[professional-track README](../README.md).

## Learning objectives

- Explain why applied migrations are immutable, read a migration manifest, and
  separate repeatable seeds from schema versions.
- Execute an expand–migrate–contract change and verify a backfill before
  tightening constraints.
- Identify PostgreSQL transactional-DDL boundaries and choose a forward fix
  when editing deployed history would be unsafe.

## Vocabulary and concepts

- **Migration:** one ordered, reviewed change from a known schema version to the
  next version.
- **Migration metadata:** durable evidence of which version, name, content tag
  or checksum, and application time were recorded.
- **Immutable migration:** an applied file whose bytes and meaning are not
  rewritten; later corrections receive a new version.
- **Seed:** controlled reference or fixture data inserted independently of
  arbitrary user data. An idempotent seed converges on the same result.
- **Idempotent:** safe to repeat with the same intended state, not merely
  “ignores every error.”
- **Expand–migrate–contract:** add a compatible representation, backfill and
  move writers/readers, then remove the obsolete representation.
- **Backfill:** a bounded update that populates a new representation for
  existing rows.
- **Compatibility window:** the period when multiple application versions and
  schema representations must coexist.
- **Forward fix:** a new migration that corrects or extends already-deployed
  history.
- **Transactional DDL:** PostgreSQL data-definition work that can commit or
  roll back atomically inside a transaction.

## Worked example / walkthrough

The fixture owns one schema and five ordered files. Every migration starts a
transaction, checks `schema_migrations`, performs its body only when absent,
records metadata last, and commits. A failed statement prevents the metadata row
from lying about a partial migration.

Version 1 creates `service_requests`, deterministic fixture rows, and a stable
`service_requests_api` view. The view exposes `priority_code` even though the
baseline storage column is named `urgency_label`. Applications that respect the
view contract are insulated from the later storage rename.

Version 2 is **expand**:

- create normalized `priority_levels` reference data;
- add nullable `priority_code`;
- add a foreign key as `NOT VALID`;
- keep `urgency_label`; and
- change the API view to `COALESCE(new, old)`.

A `NOT VALID` foreign key avoids the initial historical-row scan while still
checking new and changed non-NULL values. It is not permission to ignore old
rows forever. Version 3 backfills in a deterministic update, asserts that zero
NULLs remain, and validates the foreign key.

Version 4 is **contract**. Only after compatible application code is deployed
and old writers are retired does it set the default and `NOT NULL`, replace the
dependent view, and remove `urgency_label`. The stable view still exposes the
same columns.

Version 5 demonstrates a forward fix. The rank constraint created by migration
2 allowed values 1–3. A later requirement needs rank 4. Editing migration 2
would give clean installs different history from upgraded databases, so version
5 replaces the constraint and adds `critical`.

`seed_priority_levels.sql` uses `INSERT ... ON CONFLICT DO UPDATE`. It updates
the reference rows it owns but does not delete unrecognized rows. Production
seed ownership and deletion policy must be reviewed explicitly.

Most PostgreSQL DDL is transactional, including table creation and many
`ALTER TABLE` operations. Important exceptions need runner-level boundaries:
`CREATE DATABASE`, `VACUUM`, and `CREATE INDEX CONCURRENTLY` cannot run inside a
normal transaction block. Large backfills and validation scans may also need
separate commits, batching, lock timeouts, and observability even when the
syntax is technically transactional.

## Exercises

Complete the four prompts in the learner file. First build a deterministic
manifest query. Then narrate the compatibility window and deployment order.
Finally design versions 6–8 for `assigned_team` without modifying versions 1–5,
and explain transactional boundaries and why a lossy migration cannot be
universally reversed.

Use a scratch copy for migration experiments. Keep version numbers unique,
record metadata only after invariants pass, qualify every object, and rerun the
fixture verifier after each change.

## Self-check

- Does a clean schema reach versions 1–5 in order?
- Does a second `run_all.sql` execution skip applied migration bodies and leave
  the same rows?
- Does the seed remain at the expected cardinality when run twice?
- Can the stable API return a priority during both the old-only and dual-column
  stages?
- Is the backfill verified before `NOT NULL` and column removal?
- Can you identify exactly which application version must deploy before
  contract?
- Does normal learner/solution execution remove `pro_migration_lab`?

## Common pitfalls

- `IF NOT EXISTS` scattered across DDL is not a substitute for version metadata;
  it can hide a partially applied or drifted schema.
- Recording metadata before the body commits creates false success evidence.
- Editing an applied file splits fresh-install history from upgrade history.
- A repeatable reference seed should not silently delete business-owned rows.
- Backfilling millions of rows in one transaction can cause long locks, WAL
  growth, replica lag, and difficult recovery even when a tiny fixture succeeds.
- `ALTER TABLE ... SET NOT NULL` and constraint validation need scan/lock review.
- A rollback script cannot reconstruct information that a deployed migration
  discarded or external clients already observed.
- Arbitrary migrations are not safely reversible merely because a `down`
  filename exists.

## Next step

Continue to [SQL-SEC-01 — roles, privileges, and row-level security](sql_sec_01_roles_privileges_rls.md)
after SQL Day 39. Later professional modules can add migration regression tests,
routine deployment, operational rehearsal, and application-coordinated release
evidence.
