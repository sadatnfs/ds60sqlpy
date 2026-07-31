# SQL-FOUND-02 — Versioned Schema Migrations and Safe Evolution

## Level and prerequisites

- **Level:** Intermediate
- **Catalog prerequisites:** `sql-found-01` — [SQL-FOUND-01 — relational design](sql_found_01_relational_design.md);
  `sql-39` — [SQL Day 39 — locks and deadlocks](../../postgres-60day/companion-guides/day39_locks_deadlocks.md)
- **Prerequisites:** [SQL-FOUND-01 — relational design](sql_found_01_relational_design.md),
  the transaction/locking sequence through SQL Day 39, constraints, and
  permission to create/drop an isolated schema in `advanced_sql_training`.
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
The first runnable example has a concrete contract: Example 1 returns one row per `migration_id` with columns `migration_id`, `migration_name`, and `content_tag` from `pro_migration_lab.schema_migrations`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce. Its final projection is `migration_id`, `migration_name`, and `content_tag`. Reselect the returned key columns from `pro_migration_lab.schema_migrations`, reject duplicate keys when the grain is one row per entity, and check the stated row cap and sort direction only when this example includes them. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

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

**How to read it:** Example 1: Start with `pro_migration_lab.schema_migrations` in `FROM`/`JOIN`. The final `SELECT` displays `migration_id`, `migration_name`, and `content_tag`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `migration_id` with columns `migration_id`, `migration_name`, and `content_tag` from `pro_migration_lab.schema_migrations`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

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

**How to read it:** Example 2: Start with `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api` in `FROM`/`JOIN`. The final `SELECT` displays `request_key`, `legacy_storage`, `new_storage`, and `stable_api_value`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per `request_key` with columns `request_key`, `legacy_storage`, `new_storage`, and `stable_api_value` from `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

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
   **Inputs/evidence:** For sql-found-02 Exercise 1, read versions 1–5 from `pro_migration_lab.schema_migrations`, preserving the immutable migration identity fields `migration_id`, `migration_name`, and `content_tag`.
   **Expected result/shape:** For sql-found-02 Exercise 1, expected output: exactly five rows at one-row-per-migration grain, columns `migration_id`, `migration_name`, and `content_tag`, ordered by `migration_id`; the independent invariant is the exact array `[1, 2, 3, 4, 5]`.
   **Verify:** For sql-found-02 Exercise 1, assert the exact ordered ID array, count five distinct IDs, compare each name/tag with the reviewed fixture manifest, and prove that a missing, duplicate, reordered, or altered identity fails rather than being silently accepted.
2. **Compatibility:** explain the version-2 view and order schema, reader,
   writer, backfill, validation, and contract deployments.
   **Inputs/evidence:** For sql-found-02 Exercise 2, inspect version-2 storage and `service_requests_api` before the backfill, then return a five-step deployment matrix covering expand, compatible code, backfill, validation, and contract.
   **Expected result/shape:** For sql-found-02 Exercise 2, expected output: three request rows showing NULL `expanded_storage` but unchanged `stable_api_value`, followed by five ordered rollout rows with `step_number`, compatibility, write policy, and promotion gate.
   **Verify:** For sql-found-02 Exercise 2, assert every stable API value equals `COALESCE(expanded_storage, legacy_storage)`, the API keeps its five-column interface, and the contract step is gated on zero old-writer traffic plus a complete backfill.
3. **Forward series:** design versions 6–8 for `assigned_team` as separate
   expand, backfill, and contract steps.
   **Inputs/evidence:** For sql-found-02 Exercise 3, apply three new immutable migrations: nullable `assigned_team`, deterministic backfill, then default/NOT NULL/allowed-values CHECK; record metadata last inside each transaction.
   **Expected result/shape:** For sql-found-02 Exercise 3, expected output: command tags for migrations 6–8; one row per request with `assigned_team`; three manifest rows; one column-catalog row proving text, NOT NULL, and `'general'` default; and one validated CHECK definition.
   **Verify:** For sql-found-02 Exercise 3, assert manifest IDs are exactly `[1..8]`, every high/critical request is `response`, every other request is `general`, no NULL or disallowed value remains, the stable API projection is unchanged, and the catalog matches the promised contract.
4. **Runner boundaries:** identify nontransactional operations and explain why
   lossy changes do not have universal “down” migrations.
   **Inputs/evidence:** For sql-found-02 Exercise 4, build an inspectable decision matrix for `CREATE DATABASE`, `VACUUM`, `CREATE INDEX CONCURRENTLY`, and a lossy data change; do not pretend those operations ran inside the disposable lesson.
   **Expected result/shape:** For sql-found-02 Exercise 4, expected output: four rows ordered by `step_number` with columns `operation`, `transaction_requirement`, `reason`, and `recovery_policy`.
   **Verify:** For sql-found-02 Exercise 4, cross-check each PostgreSQL transaction restriction in a disposable environment, distinguish retry/forward-fix from destructive rollback, and require backup plus reconciliation evidence before any recovery from a lossy change.
5. **Interrupted retry:** make version 6 recoverable after an uncertain client
   disconnect, while detecting rather than concealing incompatible drift.
   **Inputs/evidence:** For sql-found-02 Exercise 5, independently test the version-006 manifest identity and the observed `assigned_team` schema contract, returning two labeled booleans in one row.
   **Expected result/shape:** For sql-found-02 Exercise 5, expected output: exactly one row with `manifest_matches` and `schema_matches`; only `(true, true)` is the already-applied state, `(false, false)` is eligible to apply, and either mixed state must stop.
   **Verify:** For sql-found-02 Exercise 5, probe all four manifest/schema truth combinations, verify name and content identity as well as column type/nullability/default, serialize deployers, and prove incompatible same-named state fails instead of being hidden by `IF NOT EXISTS`.
6. **Low-lock rollout:** mark boundaries and evidence for concurrent index
   creation and `NOT VALID`/`VALIDATE CONSTRAINT`.
   **Inputs/evidence:** For sql-found-02 Exercise 6, return an eight-step low-lock rollout plan for concurrent index creation and `CHECK ... NOT VALID`/remediation/`VALIDATE CONSTRAINT`, with explicit transaction boundaries, evidence, and abort conditions.
   **Expected result/shape:** For sql-found-02 Exercise 6, expected output: eight rows ordered by `step_number` with `rollout_step`, `transaction_boundary`, `required_evidence`, and `abort_condition`; the SQL templates remain deliberately unexecuted.
   **Verify:** For sql-found-02 Exercise 6, require pre/post catalog checks for index readiness/validity and constraint validation, bounded lock/lag/WAL/disk thresholds, restartable backfill reconciliation, and an explicit policy for a known invalid index artifact.
7. **Drift report:** compare expected and observed columns, constraints, and
   indexes; label missing, unexpected, and changed objects deterministically.
   **Inputs/evidence:** For sql-found-02 Exercise 7, FULL JOIN expected and unfiltered observed manifests for all `service_requests` columns, constraints, and indexes, comparing semantic properties rather than OIDs or storage details.
   **Expected result/shape:** For sql-found-02 Exercise 7, expected output: three deterministic result sets—one row per column, constraint, and index—with expected/observed evidence and `drift_status` equal to `matches`, `missing`, `unexpected`, or `changed`.
   **Verify:** For sql-found-02 Exercise 7, prove the clean fixture reports only `matches`; inject one disposable missing, unexpected, and changed object; confirm every branch is reachable, defaults and validation state are checked, and ordering uses the displayed object identity.
8. **Failed deployment:** write phase-specific compatibility, pause, restore,
   reconciliation, and decision evidence for recovery.
   **Inputs/evidence:** For sql-found-02 Exercise 8, model expand, backfill, and contract recovery as an ordered inline matrix with compatible versions, write state, reversible action, required evidence, and primary action.
   **Expected result/shape:** For sql-found-02 Exercise 8, expected output: exactly three rows ordered by numeric `step_number` from expand through contract, retaining every recovery field rather than sorting phases lexically.
   **Verify:** For sql-found-02 Exercise 8, walk one failure injected at each phase, prove promotion stops when its evidence is absent, and record that schema reversal cannot reconstruct discarded values or undo externally observed writes.

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

Continue directly to
[SQL-40 — advanced analytic functions](../../postgres-60day/companion-guides/day40_analytic_functions_advanced.md).
The later professional modules then add security, migration regression tests,
routine deployment, operational rehearsal, and application-coordinated release
evidence.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-found-02 — Versioned Schema Migrations and Safe Evolution.

I have completed the direct catalog prerequisites: `sql-found-01`, `sql-39`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
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
