# SQL-FOUND-02: Versioned Schema Migrations and Safe Evolution

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-found-02**. The
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
   `.learning/sql/sql-found-02/lesson/workspace/sql/professional/lessons/sql_found_02_versioned_migrations.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-found-02
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Intermediate
- **Catalog prerequisites:** `sql-found-01`; [SQL-FOUND-01; relational design](sql_found_01_relational_design.md);
  `sql-39`; [SQL Day 39; locks and deadlocks](../../postgres-60day/companion-guides/day39_locks_deadlocks.md)
- **Prerequisites:** [SQL-FOUND-01; relational design](sql_found_01_relational_design.md),
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

These worked excerpts come from `sql/professional/lessons/sql_found_02_versioned_migrations.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

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
   **Expected result/shape:** For sql-found-02 Exercise 7, expected output: three deterministic result sets, one row per column, constraint, and index, with expected/observed evidence and `drift_status` equal to `matches`, `missing`, `unexpected`, or `changed`.
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
[SQL-40; advanced analytic functions](../../postgres-60day/companion-guides/day40_analytic_functions_advanced.md).
The later professional modules then add security, migration regression tests,
routine deployment, operational rehearsal, and application-coordinated release
evidence.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

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
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
