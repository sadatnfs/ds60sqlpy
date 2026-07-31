-- SQL-FOUND-02: Versioned schema migrations and safe evolution
-- BEGINNER WORKFLOW — sql-found-02: Versioned Schema Migrations and Safe Evolution
-- Guide: sql/professional/companion-guides/sql_found_02_versioned_migrations.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-found-02/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pro_migration_lab.schema_migrations, pro_migration_lab.service_requests, pro_migration_lab.service_requests_api.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Target: PostgreSQL 16+
--
-- This script intentionally resets and later removes only pro_migration_lab.
-- Every included migration uses its own transaction and records metadata.

\set ON_ERROR_STOP on
\echo 'SQL-FOUND-02: reset the isolated migration lab'
\ir ../fixtures/migrations/reset.sql

\echo 'Version 1: baseline storage and a stable application-facing view'
\ir ../fixtures/migrations/001_create_service_requests.sql

SELECT
    sm.migration_id,
    sm.migration_name,
    sm.content_tag
FROM pro_migration_lab.schema_migrations AS sm
ORDER BY sm.migration_id;

\echo 'Version 2: expand with nullable priority_code while urgency_label remains'
\ir ../fixtures/migrations/002_expand_priority.sql

-- An idempotent reference seed converges to the same three base rows. Running
-- it twice neither duplicates rows nor deletes unknown values.
\ir ../fixtures/migrations/seed_priority_levels.sql
\ir ../fixtures/migrations/seed_priority_levels.sql

SELECT
    sr.request_key,
    sr.urgency_label AS legacy_storage,
    sr.priority_code AS new_storage,
    api.priority_code AS stable_api_value
FROM pro_migration_lab.service_requests AS sr
JOIN pro_migration_lab.service_requests_api AS api
  ON api.request_id = sr.request_id
ORDER BY sr.request_key;

\echo 'Version 3: backfill and validate before making the new column required'
\ir ../fixtures/migrations/003_backfill_priority.sql

SELECT
    sr.request_key,
    sr.urgency_label,
    sr.priority_code
FROM pro_migration_lab.service_requests AS sr
ORDER BY sr.request_key;

\echo 'Version 4: contract after old writers are assumed retired'
\ir ../fixtures/migrations/004_contract_priority.sql

\echo 'Version 5: use a forward fix instead of rewriting applied migration 002'
\ir ../fixtures/migrations/005_forward_fix_priority_rank.sql

\ir ../fixtures/migrations/verify.sql

-- Exercises (write answers in a scratch copy before opening the solution).
--
-- 1. Write one deterministic manifest query that proves versions 1-5 exist
--    exactly once and in order. Include migration_name and content_tag.
--
--    Inputs: For sql-found-02 Exercise 1, read versions 1–5 from `pro_migration_lab.schema_migrations`, preserving the immutable migration identity fields `migration_id`, `migration_name`, and `content_tag`.
--    Expected result/shape: For sql-found-02 Exercise 1, expected output: exactly five rows at one-row-per-migration grain, columns `migration_id`, `migration_name`, and `content_tag`, ordered by `migration_id`; the independent invariant is the exact array `[1, 2, 3, 4, 5]`.
--    Verify: For sql-found-02 Exercise 1, assert the exact ordered ID array, count five distinct IDs, compare each name/tag with the reviewed fixture manifest, and prove that a missing, duplicate, reordered, or altered identity fails rather than being silently accepted.
--    Hint ladder, rung 1: For sql-found-02 Exercise 1, inspect the source keys that survive `WHERE`; then check `sm.migration_id` before applying the row cap.
-- 2. At the end of version 2, explain why the stable API view supports an old
--    reader while priority_code is still NULL in storage. List a safe deployment
--    order for old writers, dual-compatible application code, backfill, and the
--    contract migration.
--
--    Inputs: For sql-found-02 Exercise 2, inspect version-2 storage and `service_requests_api` before the backfill, then return a five-step deployment matrix covering expand, compatible code, backfill, validation, and contract.
--    Expected result/shape: For sql-found-02 Exercise 2, expected output: three request rows showing NULL `expanded_storage` but unchanged `stable_api_value`, followed by five ordered rollout rows with `step_number`, compatibility, write policy, and promotion gate.
--    Verify: For sql-found-02 Exercise 2, assert every stable API value equals `COALESCE(expanded_storage, legacy_storage)`, the API keeps its five-column interface, and the contract step is gated on zero old-writer traffic plus a complete backfill.
--    Hint ladder, rung 1: For sql-found-02 Exercise 2, check the compatibility written analysis against `urgency_label`, and `priority_code`.
-- 3. Design three forward migrations for a new assigned_team column:
--    * expand with a nullable text column;
--    * backfill high/critical requests to 'response' and the rest to 'general';
--    * enforce NOT NULL, a default of 'general', and an allowed-values CHECK.
--    Record a separate metadata row for each version. Do not edit versions 1-5.
--
--    Inputs: For sql-found-02 Exercise 3, apply three new immutable migrations: nullable `assigned_team`, deterministic backfill, then default/NOT NULL/allowed-values CHECK; record metadata last inside each transaction.
--    Expected result/shape: For sql-found-02 Exercise 3, expected output: command tags for migrations 6–8; one row per request with `assigned_team`; three manifest rows; one column-catalog row proving text, NOT NULL, and `'general'` default; and one validated CHECK definition.
--    Verify: For sql-found-02 Exercise 3, assert manifest IDs are exactly `[1..8]`, every high/critical request is `response`, every other request is `general`, no NULL or disallowed value remains, the stable API projection is unchanged, and the catalog matches the promised contract.
--    Hint ladder, rung 1: For sql-found-02 Exercise 3, check the forward series written analysis against `assigned_team`, `high`, `critical`, `response`, and `general`.
-- 4. Name three PostgreSQL operations that require an explicit nontransactional
--    runner boundary. Explain why "just run the down migration" is not a safe
--    universal recovery policy after a lossy data change.
--
--    Inputs: For sql-found-02 Exercise 4, build an inspectable decision matrix for `CREATE DATABASE`, `VACUUM`, `CREATE INDEX CONCURRENTLY`, and a lossy data change; do not pretend those operations ran inside the disposable lesson.
--    Expected result/shape: For sql-found-02 Exercise 4, expected output: four rows ordered by `step_number` with columns `operation`, `transaction_requirement`, `reason`, and `recovery_policy`.
--    Verify: For sql-found-02 Exercise 4, cross-check each PostgreSQL transaction restriction in a disposable environment, distinguish retry/forward-fix from destructive rollback, and require backup plus reconciliation evidence before any recovery from a lossy change.
--    Hint ladder, rung 1: For sql-found-02 Exercise 4, inspect `pg_catalog.pg_class` for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
-- 5. Make the version-006 expand migration safely retryable after a client loses
--    its connection between DDL and metadata recording. Explain why sprinkling
--    IF NOT EXISTS everywhere can hide drift instead of proving idempotency.
--
--    Inputs: For sql-found-02 Exercise 5, independently test the version-006 manifest identity and the observed `assigned_team` schema contract, returning two labeled booleans in one row.
--    Expected result/shape: For sql-found-02 Exercise 5, expected output: exactly one row with `manifest_matches` and `schema_matches`; only `(true, true)` is the already-applied state, `(false, false)` is eligible to apply, and either mixed state must stop.
--    Verify: For sql-found-02 Exercise 5, probe all four manifest/schema truth combinations, verify name and content identity as well as column type/nullability/default, serialize deployers, and prove incompatible same-named state fails instead of being hidden by `IF NOT EXISTS`.
--    Hint ladder, rung 1: For sql-found-02 Exercise 5, inspect the source keys that survive `WHERE`.
-- 6. Design a large-table index rollout using CREATE INDEX CONCURRENTLY and a
--    CHECK constraint rollout using NOT VALID followed by VALIDATE CONSTRAINT.
--    Mark the transaction boundaries and the monitoring/abort evidence.
--
--    Inputs: For sql-found-02 Exercise 6, return an eight-step low-lock rollout plan for concurrent index creation and `CHECK ... NOT VALID`/remediation/`VALIDATE CONSTRAINT`, with explicit transaction boundaries, evidence, and abort conditions.
--    Expected result/shape: For sql-found-02 Exercise 6, expected output: eight rows ordered by `step_number` with `rollout_step`, `transaction_boundary`, `required_evidence`, and `abort_condition`; the SQL templates remain deliberately unexecuted.
--    Verify: For sql-found-02 Exercise 6, require pre/post catalog checks for index readiness/validity and constraint validation, bounded lock/lag/WAL/disk thresholds, restartable backfill reconciliation, and an explicit policy for a known invalid index artifact.
--    Hint ladder, rung 1: For sql-found-02 Exercise 6, inspect `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_constraint` for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
-- 7. Write a schema-drift report comparing an expected manifest of columns,
--    types, nullability, defaults, constraints, and indexes with pg_catalog.
--    Distinguish missing, unexpected, and changed objects deterministically.
--
--    Inputs: For sql-found-02 Exercise 7, FULL JOIN expected and unfiltered observed manifests for all `service_requests` columns, constraints, and indexes, comparing semantic properties rather than OIDs or storage details.
--    Expected result/shape: For sql-found-02 Exercise 7, expected output: three deterministic result sets—one row per column, constraint, and index—with expected/observed evidence and `drift_status` equal to `matches`, `missing`, `unexpected`, or `changed`.
--    Verify: For sql-found-02 Exercise 7, prove the clean fixture reports only `matches`; inject one disposable missing, unexpected, and changed object; confirm every branch is reachable, defaults and validation state are checked, and ordering uses the displayed object identity.
--    Hint ladder, rung 1: For sql-found-02 Exercise 7, run `observed` one at a time. Record each CTE's row count and `column_name` uniqueness before the next stage uses it.
-- 8. Draft a failed-deployment recovery plan for each expand/contract phase.
--    State which application versions can run, which writes must be paused,
--    what is reversible, and what backup or reconciliation evidence is needed.
--    Inputs: For sql-found-02 Exercise 8, model expand, backfill, and contract recovery as an ordered inline matrix with compatible versions, write state, reversible action, required evidence, and primary action.
--    Expected result/shape: For sql-found-02 Exercise 8, expected output: exactly three rows ordered by numeric `step_number` from expand through contract, retaining every recovery field rather than sorting phases lexically.
--    Verify: For sql-found-02 Exercise 8, walk one failure injected at each phase, prove promotion stops when its evidence is absent, and record that schema reversal cannot reconstruct discarded values or undo externally observed writes.
--    Hint ladder, rung 1: For sql-found-02 Exercise 8, restore into an isolated target and reconcile the inline `VALUES` fixture using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.

\echo 'SQL-FOUND-02: remove the isolated migration lab after normal completion'
\ir ../fixtures/migrations/cleanup.sql
\echo 'SQL-FOUND-02 complete'
