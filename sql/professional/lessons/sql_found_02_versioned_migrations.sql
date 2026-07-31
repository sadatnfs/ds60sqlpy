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
--    Inputs: Use `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 must make “Manifest: return versions 1–5 once and in order with stable metadata” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `sm`, `api`, `sr`, `pro_migration_lab.service_requests`.
--    Verify: For Exercise 1, inspect the relevant `pg_catalog` or `information_schema` rows for `sm`, `api`, `sr`, `pro_migration_lab.service_requests`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: State the invariant and object grain first, implement the smallest DDL step, then design its catalog and negative-case proof.
-- 2. At the end of version 2, explain why the stable API view supports an old
--    reader while priority_code is still NULL in storage. List a safe deployment
--    order for old writers, dual-compatible application code, backfill, and the
--    contract migration.
--
--    Inputs: Use `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 must make “Compatibility: explain the version-2 view and order schema, reader, writer, backfill, validation, and contract deployments” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement.
--    Verify: For Exercise 2, inspect the relevant `pg_catalog` or `information_schema` rows for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: State the invariant and object grain first, implement the smallest DDL step, then design its catalog and negative-case proof.
-- 3. Design three forward migrations for a new assigned_team column:
--    * expand with a nullable text column;
--    * backfill high/critical requests to 'response' and the rest to 'general';
--    * enforce NOT NULL, a default of 'general', and an allowed-values CHECK.
--    Record a separate metadata row for each version. Do not edit versions 1-5.
--
--    Inputs: Use `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 returns a table-shaped answer to “Forward series: design versions 6–8 for assignedteam as separate expand, backfill, and contract steps” at one result row per key or group explicitly named in the prompt. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 3, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.
-- 4. Name three PostgreSQL operations that require an explicit nontransactional
--    runner boundary. Explain why "just run the down migration" is not a safe
--    universal recovery policy after a lossy data change.
--
--    Inputs: Use `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 needs a labeled transaction/session transcript that demonstrates “Runner boundaries: identify nontransactional operations and explain why lossy changes do not have universal “down” migrations”. Capture statement order, affected keys/counts, lock or snapshot state, and the expected SQLSTATE when an error is part of the exercise; finish with no open lesson transaction or leftover shared fixture. Named evidence columns/objects: `CONCURRENTLY`.
--    Verify: For Exercise 4, replay the written Session A/Session B order against `advanced_sql_training`, compare the observed values/SQLSTATE with the prediction, then query/drop the disposable fixture and confirm neither session retains a transaction or lock.
--    Hint ladder, rung 1: State the invariant and object grain first, implement the smallest DDL step, then design its catalog and negative-case proof.
-- 5. Make the version-006 expand migration safely retryable after a client loses
--    its connection between DDL and metadata recording. Explain why sprinkling
--    IF NOT EXISTS everywhere can hide drift instead of proving idempotency.
--
--    Inputs: Use `pro_migration_lab.schema_migrations`, `information_schema.columns` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 returns a table-shaped answer to “Interrupted retry: make version 6 recoverable after an uncertain client disconnect, while detecting rather than concealing incompatible drift” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `sm`, `manifest_matches`, `c`, `schema_matches`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 5, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pro_migration_lab.schema_migrations`, `information_schema.columns`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.
-- 6. Design a large-table index rollout using CREATE INDEX CONCURRENTLY and a
--    CHECK constraint rollout using NOT VALID followed by VALIDATE CONSTRAINT.
--    Mark the transaction boundaries and the monitoring/abort evidence.
--
--    Inputs: Use `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 needs a labeled transaction/session transcript that demonstrates “Low-lock rollout: mark boundaries and evidence for concurrent index creation and NOT VALID/VALIDATE CONSTRAINT”. Capture statement order, affected keys/counts, lock or snapshot state, and the expected SQLSTATE when an error is part of the exercise; finish with no open lesson transaction or leftover shared fixture. Named evidence columns/objects: `not`, `valid`, `validate`, `constraint`, `CONCURRENTLY`.
--    Verify: For Exercise 6, replay the written Session A/Session B order against `advanced_sql_training`, compare the observed values/SQLSTATE with the prediction, then query/drop the disposable fixture and confirm neither session retains a transaction or lock.
--    Hint ladder, rung 1: Write the correctness query first, then wrap that unchanged query in `EXPLAIN`; add `ANALYZE` only after confirming it is safe to execute.
-- 7. Write a schema-drift report comparing an expected manifest of columns,
--    types, nullability, defaults, constraints, and indexes with pg_catalog.
--    Distinguish missing, unexpected, and changed objects deterministically.
--
--    Inputs: Use `information_schema.columns` plus only the small disposable fixture explicitly requested by Exercise 7; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 7 needs the plan evidence for “Drift report: compare expected and observed columns, constraints, and indexes; label missing, unexpected, and changed objects deterministically”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one catalog/behavior check per object or invariant. Named evidence columns/objects: `c`, `column_name`, `drift_status`, `e`, `o`.
--    Verify: For Exercise 7, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `information_schema.columns` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers.
--    Hint ladder, rung 1: Write the correctness query first, then wrap that unchanged query in `EXPLAIN`; add `ANALYZE` only after confirming it is safe to execute.
-- 8. Draft a failed-deployment recovery plan for each expand/contract phase.
--    State which application versions can run, which writes must be paused,
--    what is reversible, and what backup or reconciliation evidence is needed.
--    Inputs: Use `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api` plus only the small disposable fixture explicitly requested by Exercise 8; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 8 returns a table-shaped answer to “Failed deployment: write phase-specific compatibility, pause, restore, reconciliation, and decision evidence for recovery” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `recovery`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 8, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.

\echo 'SQL-FOUND-02: remove the isolated migration lab after normal completion'
\ir ../fixtures/migrations/cleanup.sql
\echo 'SQL-FOUND-02 complete'
