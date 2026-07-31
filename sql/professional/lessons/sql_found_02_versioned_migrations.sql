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
--    Inputs: For sql-found-02 Exercise 1, read from `pro_migration_lab.schema_migrations`. Build the answer toward `migration_id`, `migration_name`, and `content_tag`; keep `migration_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-found-02 Exercise 1, expected output: one row per `migration_id`. The final columns are `migration_id`, `migration_name`, and `content_tag`. The final order is `sm.migration_id`.
--    Verify: For sql-found-02 Exercise 1, run an anti-check that counts rows where NOT ((sm.migration_id BETWEEN 1 AND 5)); require unique `migration_id` where the expected grain is one row per key and confirm the projected `migration_id`, `migration_name`, and `content_tag` against `pro_migration_lab.schema_migrations`. Add one row for which `(sm.migration_id BETWEEN 1 AND 5)` is true and one for which it is false; verify only the matching `migration_id` value is returned.
--    Hint ladder, rung 1: For sql-found-02 Exercise 1, inspect the source keys that survive `WHERE`; then check `sm.migration_id` before applying the row cap.
-- 2. At the end of version 2, explain why the stable API view supports an old
--    reader while priority_code is still NULL in storage. List a safe deployment
--    order for old writers, dual-compatible application code, backfill, and the
--    contract migration.
--
--    Inputs: For sql-found-02 Exercise 2, complete the compatibility written analysis and support its claims with read-only evidence from `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-found-02 Exercise 2, expected output: a completed the compatibility written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `urgency_label`, and `priority_code`.
--    Verify: For sql-found-02 Exercise 2, check the compatibility written analysis against `urgency_label`, and `priority_code`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-found-02 Exercise 2, check the compatibility written analysis against `urgency_label`, and `priority_code`.
-- 3. Design three forward migrations for a new assigned_team column:
--    * expand with a nullable text column;
--    * backfill high/critical requests to 'response' and the rest to 'general';
--    * enforce NOT NULL, a default of 'general', and an allowed-values CHECK.
--    Record a separate metadata row for each version. Do not edit versions 1-5.
--
--    Inputs: For sql-found-02 Exercise 3, complete the forward series written analysis and support its claims with read-only evidence from `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-found-02 Exercise 3, expected output: a completed the forward series written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `assigned_team`, `high`, `critical`, `response`, and `general`.
--    Verify: For sql-found-02 Exercise 3, check the forward series written analysis against `assigned_team`, `high`, `critical`, `response`, and `general`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-found-02 Exercise 3, check the forward series written analysis against `assigned_team`, `high`, `critical`, `response`, and `general`.
-- 4. Name three PostgreSQL operations that require an explicit nontransactional
--    runner boundary. Explain why "just run the down migration" is not a safe
--    universal recovery policy after a lossy data change.
--
--    Inputs: For sql-found-02 Exercise 4, change only `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_class` rows.
--    Expected result/shape: For sql-found-02 Exercise 4, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `vacuum`, and `update`.
--    Verify: For sql-found-02 Exercise 4, inspect `pg_catalog.pg_class` for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
--    Hint ladder, rung 1: For sql-found-02 Exercise 4, inspect `pg_catalog.pg_class` for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
-- 5. Make the version-006 expand migration safely retryable after a client loses
--    its connection between DDL and metadata recording. Explain why sprinkling
--    IF NOT EXISTS everywhere can hide drift instead of proving idempotency.
--
--    Inputs: For sql-found-02 Exercise 5, read from `pro_migration_lab.schema_migrations`, and `information_schema.columns`. Compute `manifest_matches`, and `schema_matches` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-found-02 Exercise 5, expected output: exactly one aggregate summary row. The final columns are `manifest_matches`, and `schema_matches`.
--    Verify: For sql-found-02 Exercise 5, evaluate each of `manifest_matches`, and `schema_matches` in a separate control `SELECT` over `pro_migration_lab.schema_migrations`, and `information_schema.columns`; require one final row and compare every value. Add one source row with a new `version`; verify the result gains exactly one row carrying that `version` value.
--    Hint ladder, rung 1: For sql-found-02 Exercise 5, inspect the source keys that survive `WHERE`.
-- 6. Design a large-table index rollout using CREATE INDEX CONCURRENTLY and a
--    CHECK constraint rollout using NOT VALID followed by VALIDATE CONSTRAINT.
--    Mark the transaction boundaries and the monitoring/abort evidence.
--
--    Inputs: For sql-found-02 Exercise 6, change only `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_constraint` rows.
--    Expected result/shape: For sql-found-02 Exercise 6, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `object_name`, `catalog_definition`, `accepted_case`, and `rejected_sqlstate`.
--    Verify: For sql-found-02 Exercise 6, inspect `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_constraint` for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
--    Hint ladder, rung 1: For sql-found-02 Exercise 6, inspect `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_constraint` for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
-- 7. Write a schema-drift report comparing an expected manifest of columns,
--    types, nullability, defaults, constraints, and indexes with pg_catalog.
--    Distinguish missing, unexpected, and changed objects deterministically.
--
--    Inputs: For sql-found-02 Exercise 7, read from `information_schema.columns`, `expected`, and `pg_get_expr`. Build the answer toward `column_name`; keep `column_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-found-02 Exercise 7, expected output: one row per `column_name`. The final columns are `column_name`. The final order is `column_name`.
--    Verify: For sql-found-02 Exercise 7, project `column_name` plus the raw source columns from `information_schema.columns`, `expected`, and `pg_get_expr` at each join stage; record row count and distinct `column_name`, then assert the final `column_name` values match those staged rows without unintended fanout or loss. Add one source row with a new `column_name`; verify the result gains exactly one row carrying that `column_name` value.
--    Hint ladder, rung 1: For sql-found-02 Exercise 7, run `observed` one at a time. Record each CTE's row count and `column_name` uniqueness before the next stage uses it.
-- 8. Draft a failed-deployment recovery plan for each expand/contract phase.
--    State which application versions can run, which writes must be paused,
--    what is reversible, and what backup or reconciliation evidence is needed.
--    Inputs: For sql-found-02 Exercise 8, use the inline `VALUES` fixture in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-found-02 Exercise 8, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`. The final order is `phase`.
--    Verify: For sql-found-02 Exercise 8, restore into an isolated target and reconcile the inline `VALUES` fixture using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-found-02 Exercise 8, restore into an isolated target and reconcile the inline `VALUES` fixture using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.

\echo 'SQL-FOUND-02: remove the isolated migration lab after normal completion'
\ir ../fixtures/migrations/cleanup.sql
\echo 'SQL-FOUND-02 complete'
