-- SQL-FOUND-02: Versioned schema migrations and safe evolution
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
-- 2. At the end of version 2, explain why the stable API view supports an old
--    reader while priority_code is still NULL in storage. List a safe deployment
--    order for old writers, dual-compatible application code, backfill, and the
--    contract migration.
--
-- 3. Design three forward migrations for a new assigned_team column:
--    * expand with a nullable text column;
--    * backfill high/critical requests to 'response' and the rest to 'general';
--    * enforce NOT NULL, a default of 'general', and an allowed-values CHECK.
--    Record a separate metadata row for each version. Do not edit versions 1-5.
--
-- 4. Name three PostgreSQL operations that require an explicit nontransactional
--    runner boundary. Explain why "just run the down migration" is not a safe
--    universal recovery policy after a lossy data change.

\echo 'SQL-FOUND-02: remove the isolated migration lab after normal completion'
\ir ../fixtures/migrations/cleanup.sql
\echo 'SQL-FOUND-02 complete'

