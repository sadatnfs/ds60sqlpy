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

2. Open **SQL-FOUND-02 — Versioned Schema Migrations and Safe Evolution** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-found-02/lesson/workspace/sql/professional/lessons/sql_found_02_versioned_migrations.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

This lesson deliberately uses cataloged `psql` `\ir` includes. Run the complete file from its documented location (or the guided runner) so migration paths resolve correctly; do not paste fragments into a generic query editor and assume the migration sequence ran.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_found_02_versioned_migrations.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_found_02_versioned_migrations.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Migration, Migration metadata, Immutable migration, Seed, Idempotent, Expand–migrate–contract. Its worked SQL reads or creates `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: The fixture owns one schema and five ordered files. Every migration starts a transaction, checks schemamigrations, performs its body only when absent, records metadata last, and commits. A failed statement prevents the metadata row from lying about a partial migration.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/professional/lessons/sql_found_02_versioned_migrations.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT
    sm.migration_id,
    sm.migration_name,
    sm.content_tag
FROM pro_migration_lab.schema_migrations AS sm
ORDER BY sm.migration_id;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT
    sr.request_key,
    sr.urgency_label AS legacy_storage,
    sr.priority_code AS new_storage,
    api.priority_code AS stable_api_value
FROM pro_migration_lab.service_requests AS sr
JOIN pro_migration_lab.service_requests_api AS api
  ON api.request_id = sr.request_id
ORDER BY sr.request_key;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

Complete all eight prompts in the learner file. First build a deterministic
manifest query. Then narrate the compatibility window and deployment order.
Finally design versions 6–8 for `assigned_team` without modifying versions 1–5,
then cover retry state, low-lock boundaries, drift evidence, and failed-phase
recovery. Explain why a lossy migration cannot be universally reversed.

Use a scratch copy for migration experiments. Keep version numbers unique,
record metadata only after invariants pass, qualify every object, and rerun the
fixture verifier after each change.

For every migration, record precondition, change, verification, compatibility
window, recovery action, and cleanup:

1. **Manifest:** return versions 1–5 once and in order with stable metadata.
   **Expected result/shape:** Exercise 1 must make “Manifest: return versions 1–5 once and in order with stable metadata” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `sm`, `api`, `sr`, `pro_migration_lab.service_requests`.
   **Verify:** For Exercise 1, inspect the relevant `pg_catalog` or `information_schema` rows for `sm`, `api`, `sr`, `pro_migration_lab.service_requests`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
2. **Compatibility:** explain the version-2 view and order schema, reader,
   writer, backfill, validation, and contract deployments.
   **Expected result/shape:** Exercise 2 must make “Compatibility: explain the version-2 view and order schema, reader, writer, backfill, validation, and contract deployments” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement.
   **Verify:** For Exercise 2, inspect the relevant `pg_catalog` or `information_schema` rows for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
3. **Forward series:** design versions 6–8 for `assigned_team` as separate
   expand, backfill, and contract steps.
   **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Forward series: design versions 6–8 for assignedteam as separate expand, backfill, and contract steps” at one result row per key or group explicitly named in the prompt. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 3, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
4. **Runner boundaries:** identify nontransactional operations and explain why
   lossy changes do not have universal “down” migrations.
   **Expected result/shape:** Exercise 4 needs a labeled transaction/session transcript that demonstrates “Runner boundaries: identify nontransactional operations and explain why lossy changes do not have universal “down” migrations”. Capture statement order, affected keys/counts, lock or snapshot state, and the expected SQLSTATE when an error is part of the exercise; finish with no open lesson transaction or leftover shared fixture. Named evidence columns/objects: `CONCURRENTLY`.
   **Verify:** For Exercise 4, replay the written Session A/Session B order against `advanced_sql_training`, compare the observed values/SQLSTATE with the prediction, then query/drop the disposable fixture and confirm neither session retains a transaction or lock.
5. **Interrupted retry:** make version 6 recoverable after an uncertain client
   disconnect, while detecting rather than concealing incompatible drift.
   **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Interrupted retry: make version 6 recoverable after an uncertain client disconnect, while detecting rather than concealing incompatible drift” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `sm`, `manifest_matches`, `c`, `schema_matches`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 5, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pro_migration_lab.schema_migrations`, `information_schema.columns`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
6. **Low-lock rollout:** mark boundaries and evidence for concurrent index
   creation and `NOT VALID`/`VALIDATE CONSTRAINT`.
   **Expected result/shape:** Exercise 6 needs a labeled transaction/session transcript that demonstrates “Low-lock rollout: mark boundaries and evidence for concurrent index creation and NOT VALID/VALIDATE CONSTRAINT”. Capture statement order, affected keys/counts, lock or snapshot state, and the expected SQLSTATE when an error is part of the exercise; finish with no open lesson transaction or leftover shared fixture. Named evidence columns/objects: `not`, `valid`, `validate`, `constraint`, `CONCURRENTLY`.
   **Verify:** For Exercise 6, replay the written Session A/Session B order against `advanced_sql_training`, compare the observed values/SQLSTATE with the prediction, then query/drop the disposable fixture and confirm neither session retains a transaction or lock.
7. **Drift report:** compare expected and observed columns, constraints, and
   indexes; label missing, unexpected, and changed objects deterministically.
   **Expected result/shape:** Exercise 7 needs the plan evidence for “Drift report: compare expected and observed columns, constraints, and indexes; label missing, unexpected, and changed objects deterministically”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one catalog/behavior check per object or invariant. Named evidence columns/objects: `c`, `column_name`, `drift_status`, `e`, `o`.
   **Verify:** For Exercise 7, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `information_schema.columns` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers.
8. **Failed deployment:** write phase-specific compatibility, pause, restore,
   reconciliation, and decision evidence for recovery.
   **Expected result/shape:** Exercise 8 returns a table-shaped answer to “Failed deployment: write phase-specific compatibility, pause, restore, reconciliation, and decision evidence for recovery” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `recovery`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 8, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.

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

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-found-02 — Versioned Schema Migrations and Safe Evolution.

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_found_02_versioned_migrations.md
- Answer-free learner SQL: sql/professional/lessons/sql_found_02_versioned_migrations.sql

Key terms to teach in context: Migration, Migration metadata, Immutable migration, Seed, Idempotent, Expand–migrate–contract. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The fixture owns one schema and five ordered files. Every migration starts a transaction, checks schemamigrations, performs its body only when absent, records metadata last, and commits. A failed statement prevents the metadata row from lying about a partial migration.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-found-02/ working copy. Never point setup, reset, DDL, or DML
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
