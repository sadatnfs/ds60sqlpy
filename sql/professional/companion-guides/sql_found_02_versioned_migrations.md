# SQL-FOUND-02: Versioned Schema Migrations and Safe Evolution

## How to run this lesson

Start **sql-found-02** from `./classroom` using the shared [run steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Choose **Whole SQL lesson (psql)**; it keeps the relative `\ir` includes of
`sql/professional/fixtures/migrations` working, which **SQL snippet** cannot.
Unlike most professional lessons, this script does not end in `ROLLBACK`. It
includes `reset.sql`, which drops only `pro_migration_lab` in
`advanced_sql_training`, then applies versions 001 to 005. Each version takes
an advisory lock, runs in its own `BEGIN` and `COMMIT`, and skips its body when
the manifest already holds a matching row. The seed file runs twice to show it
converges, `verify.sql` checks the result, and `cleanup.sql` drops the schema.
An interrupted run therefore leaves committed versions behind until the next
reset or a manual `cleanup.sql`. Save attempts in
`.learning/sql/sql-found-02/lesson/workspace/sql/professional/lessons/sql_found_02_versioned_migrations.sql`.

The optional notebook route starts with `uv run --no-sync python scripts/course.py sql notebook sql-found-02`; see the [study guide](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

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

Run from the repository root on Linux, macOS, or Windows through WSL 2:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_found_02_versioned_migrations.sql
```

That command drops and recreates only `pro_migration_lab`, upgrades it through
five versions, verifies it, and drops it on normal completion. If you interrupt
the script, run the explicit
[`cleanup.sql`](../fixtures/migrations/cleanup.sql) command shown in the
[professional-track README](../README.md).

## A beginner's mental model for this lesson

Here the stored facts describe the schema itself. `schema_migrations` records
which versions have run, and the vocabulary below explains why a recorded
version is never edited and why replacing `urgency_label` with `priority_code`
takes versions 2, 3 and 4 instead of one `ALTER`.

Two grains matter. In `schema_migrations` one row is one applied version keyed
by `migration_id`, so a manifest query should show each version once, in order,
with no gaps. In `service_requests` one row is one request, `REQ-100` to
`REQ-102`, and the `service_requests_api` view keeps that grain while it hides
which storage column is current. The study guide covers the general [reading
order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).

The walkthrough follows the five fixture files in order. Each one checks
`schema_migrations` for its own ID, name and content tag, refuses to continue
if the ID exists with a different name or tag, runs its body only when the row
is absent, writes the metadata row last and commits. Because that insert is in
the same transaction as the body, a failed statement leaves no row claiming a
partial migration.

## Two worked SQL examples

Example 1 runs right after version 1, and Example 2 right after version 2 and
its seed.

### Example 1

```sql
SELECT
  sm.migration_id,
  sm.migration_name,
  sm.content_tag
FROM
  pro_migration_lab.schema_migrations AS sm
ORDER BY
  sm.migration_id;
```

**How to read it:** This is the manifest straight after
`001_create_service_requests.sql`. One row is one applied version,
`migration_id` gives the order, and `content_tag` is what each later preflight
compares, so an edited version is refused instead of silently skipped.

**Expected result/shape:** Exactly one row at this point: `1`,
`create_service_requests`, `course-fixture-001-v1`. Exercise 1 later asks for
the full five-row manifest after version 5.

### Example 2

```sql
SELECT
  sr.request_key,
  sr.urgency_label AS legacy_storage,
  sr.priority_code AS new_storage,
  api.priority_code AS stable_api_value
FROM
  pro_migration_lab.service_requests AS sr
  JOIN pro_migration_lab.service_requests_api AS api ON api.request_id = sr.request_id
ORDER BY
  sr.request_key;
```

**How to read it:** Version 2 added a nullable `priority_code` without filling
it and rebuilt the view as
`COALESCE(sr.priority_code, sr.urgency_label) AS priority_code`. The join on
`request_id` is one-to-one because the view selects straight from
`service_requests`, so the result keeps one row per request.

**Expected result/shape:** Three rows, `REQ-100` to `REQ-102`. `legacy_storage`
shows `low`, `high` and `normal`, `new_storage` is NULL in every row, and
`stable_api_value` repeats the legacy value, which is why an old reader of the
view sees no change.

## Learning objectives

- Explain why applied migrations are immutable, read a migration manifest, and
  separate repeatable seeds from schema versions.
- Execute an expand-migrate-contract change and verify a backfill before
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
- **Expand-migrate-contract:** add a compatible representation, backfill and
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
2 allowed values 1-3. A later requirement needs rank 4. Editing migration 2
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
Finally design versions 6-8 for `assigned_team` without modifying versions 1-5,
then cover retry state, low-lock boundaries, drift evidence, and failed-phase
recovery. Explain why a lossy migration cannot be universally reversed.

Use a scratch copy for migration experiments. Keep version numbers unique,
record metadata only after invariants pass, qualify every object, and rerun the
fixture verifier after each change.

For every migration, record precondition, change, verification, compatibility
window, recovery action, and cleanup:

1. **Manifest:** return versions 1-5 once and in order with stable metadata.
   **Inputs/evidence:** For sql-found-02 Exercise 1, read versions 1-5 from `pro_migration_lab.schema_migrations`, preserving the immutable migration identity fields `migration_id`, `migration_name`, and `content_tag`.
   **Expected result/shape:** For sql-found-02 Exercise 1, expected output: exactly five rows at one-row-per-migration grain, columns `migration_id`, `migration_name`, and `content_tag`, ordered by `migration_id`; the independent invariant is the exact array `[1, 2, 3, 4, 5]`.
   **Verify:** For sql-found-02 Exercise 1, assert the exact ordered ID array, count five distinct IDs, compare each name/tag with the reviewed fixture manifest, and prove that a missing, duplicate, reordered, or altered identity fails rather than being silently accepted.
2. **Compatibility:** explain the version-2 view and order schema, reader,
   writer, backfill, validation, and contract deployments.
   **Inputs/evidence:** For sql-found-02 Exercise 2, inspect version-2 storage and `service_requests_api` before the backfill, then return a five-step deployment matrix covering expand, compatible code, backfill, validation, and contract.
   **Expected result/shape:** For sql-found-02 Exercise 2, expected output: three request rows showing NULL `expanded_storage` but unchanged `stable_api_value`, followed by five ordered rollout rows with `step_number`, compatibility, write policy, and promotion gate.
   **Verify:** For sql-found-02 Exercise 2, assert every stable API value equals `COALESCE(expanded_storage, legacy_storage)`, the API keeps its five-column interface, and the contract step is gated on zero old-writer traffic plus a complete backfill.
3. **Forward series:** design versions 6-8 for `assigned_team` as separate
   expand, backfill, and contract steps.
   **Inputs/evidence:** For sql-found-02 Exercise 3, apply three new immutable migrations: nullable `assigned_team`, deterministic backfill, then default/NOT NULL/allowed-values CHECK; record metadata last inside each transaction.
   **Expected result/shape:** For sql-found-02 Exercise 3, expected output: command tags for migrations 6-8; one row per request with `assigned_team`; three manifest rows; one column-catalog row proving text, NOT NULL, and `'general'` default; and one validated CHECK definition.
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

- Does a clean schema reach versions 1-5 in order?
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

The lesson and expected observations are sufficient offline. For optional
coaching, copy:

```text
Tutor me through sql-found-02: Versioned Schema Migrations and Safe Evolution.

I have completed the direct catalog prerequisites: `sql-found-01`, `sql-39`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_found_02_versioned_migrations.md
- Answer-free learner SQL: sql/professional/lessons/sql_found_02_versioned_migrations.sql

Key terms to teach in context: Migration, Migration metadata, Immutable migration, Seed, Idempotent, Expand-migrate-contract. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The fixture owns one schema and five ordered files. Every migration starts a transaction, checks `schema_migrations`, performs its body only when absent, records metadata last, and commits. A failed statement prevents the metadata row from lying about a partial migration.

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
