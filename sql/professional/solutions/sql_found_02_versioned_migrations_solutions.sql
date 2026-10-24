-- SQL-FOUND-02 executable solutions
-- SOLUTION READING MAP — sql-found-02: Versioned Schema Migrations and Safe Evolution
-- Explanation: sql/professional/solutions/sql_found_02_versioned_migrations_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_found_02_versioned_migrations_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
-- Normal completion removes pro_migration_lab.

\set ON_ERROR_STOP on
\ir ../fixtures/migrations/reset.sql
-- Stop after the expand migration first so Exercise 2 can prove the actual
-- compatibility window instead of merely describing it after the old column
-- has already been removed.
\ir ../fixtures/migrations/001_create_service_requests.sql
\ir ../fixtures/migrations/002_expand_priority.sql
\ir ../fixtures/migrations/seed_priority_levels.sql

-- Exercise 2: at version 2, old storage remains populated while the additive
-- column is nullable. The stable view shields readers with COALESCE.
SELECT
    sr.request_key,
    sr.urgency_label AS legacy_storage,
    sr.priority_code AS expanded_storage,
    api.priority_code AS stable_api_value
FROM pro_migration_lab.service_requests AS sr
JOIN pro_migration_lab.service_requests_api AS api
  ON api.request_id = sr.request_id
ORDER BY sr.request_key;

SELECT *
FROM (
    VALUES
        (1, 'expand storage', 'old and new readers', 'old writers allowed',
         'nullable priority_code and compatible view deployed'),
        (2, 'deploy compatible code', 'old and new readers', 'dual-compatible writers',
         'new code reads the view and can populate priority_code'),
        (3, 'backfill', 'old and new readers', 'writes monitored or fenced',
         'zero NULL priority_code rows and key-by-key reconciliation'),
        (4, 'validate relationship', 'new readers preferred', 'new writers required',
         'foreign key validated and application error rate acceptable'),
        (5, 'contract storage', 'new readers only', 'new writers only',
         'old-writer traffic is zero before urgency_label is removed')
) AS rollout(
    step_number,
    deployment_step,
    compatible_readers,
    writes_allowed,
    promotion_gate
)
ORDER BY step_number;

-- Complete the cataloged fixture sequence without rewriting versions 1-2.
\ir ../fixtures/migrations/003_backfill_priority.sql
\ir ../fixtures/migrations/004_contract_priority.sql
\ir ../fixtures/migrations/005_forward_fix_priority_rank.sql
\ir ../fixtures/migrations/verify.sql

-- Exercise 1: deterministic metadata manifest.
SELECT
    sm.migration_id,
    sm.migration_name,
    sm.content_tag
FROM pro_migration_lab.schema_migrations AS sm
WHERE sm.migration_id BETWEEN 1 AND 5
ORDER BY sm.migration_id;

DO $solution$
DECLARE
    observed_versions integer[];
BEGIN
    SELECT array_agg(sm.migration_id ORDER BY sm.migration_id)
    INTO observed_versions
    FROM pro_migration_lab.schema_migrations AS sm
    WHERE sm.migration_id BETWEEN 1 AND 5;

    IF observed_versions <> ARRAY[1, 2, 3, 4, 5] THEN
        RAISE EXCEPTION 'unexpected migration manifest: %', observed_versions;
    END IF;
END
$solution$;

-- Exercise 3, migration 006: expand with a nullable column. Existing readers of
-- service_requests_api still see the same five-column interface.
BEGIN;
ALTER TABLE pro_migration_lab.service_requests
    ADD COLUMN assigned_team text;

INSERT INTO pro_migration_lab.schema_migrations (
    migration_id,
    migration_name,
    content_tag
)
VALUES (6, 'expand_assigned_team', 'course-solution-006-v1');
COMMIT;

SELECT
    api.request_key,
    api.priority_code
FROM pro_migration_lab.service_requests_api AS api
ORDER BY api.request_key;

-- Exercise 3, migration 007: backfill in a separate forward step.
BEGIN;
UPDATE pro_migration_lab.service_requests AS sr
SET assigned_team = CASE
    WHEN sr.priority_code IN ('high', 'critical') THEN 'response'
    ELSE 'general'
END
WHERE sr.assigned_team IS NULL;

DO $solution$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pro_migration_lab.service_requests AS sr
        WHERE sr.assigned_team IS NULL
    ) THEN
        RAISE EXCEPTION 'assigned_team backfill left NULL rows';
    END IF;
END
$solution$;

INSERT INTO pro_migration_lab.schema_migrations (
    migration_id,
    migration_name,
    content_tag
)
VALUES (7, 'backfill_assigned_team', 'course-solution-007-v1');
COMMIT;

-- Exercise 3, migration 008: contract after compatible writers are deployed.
BEGIN;
ALTER TABLE pro_migration_lab.service_requests
    ALTER COLUMN assigned_team SET DEFAULT 'general',
    ALTER COLUMN assigned_team SET NOT NULL;

ALTER TABLE pro_migration_lab.service_requests
    ADD CONSTRAINT service_requests_assigned_team_ck
    CHECK (assigned_team IN ('general', 'response'));

INSERT INTO pro_migration_lab.schema_migrations (
    migration_id,
    migration_name,
    content_tag
)
VALUES (8, 'contract_assigned_team', 'course-solution-008-v1');
COMMIT;

SELECT
    sr.request_key,
    sr.priority_code,
    sr.assigned_team
FROM pro_migration_lab.service_requests AS sr
ORDER BY sr.request_key;

SELECT
    sm.migration_id,
    sm.migration_name,
    sm.content_tag
FROM pro_migration_lab.schema_migrations AS sm
WHERE sm.migration_id BETWEEN 6 AND 8
ORDER BY sm.migration_id;

SELECT
    c.column_name,
    c.data_type,
    c.is_nullable,
    c.column_default
FROM information_schema.columns AS c
WHERE c.table_schema = 'pro_migration_lab'
  AND c.table_name = 'service_requests'
  AND c.column_name = 'assigned_team';

SELECT
    con.conname AS constraint_name,
    con.convalidated AS is_validated,
    pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_catalog.pg_constraint AS con
WHERE con.conrelid = 'pro_migration_lab.service_requests'::regclass
  AND con.conname = 'service_requests_assigned_team_ck';

DO $solution$
DECLARE
    observed_versions integer[];
BEGIN
    SELECT array_agg(sm.migration_id ORDER BY sm.migration_id)
    INTO observed_versions
    FROM pro_migration_lab.schema_migrations AS sm;

    IF observed_versions <> ARRAY[1, 2, 3, 4, 5, 6, 7, 8] THEN
        RAISE EXCEPTION
            'expected migration versions 1-8, observed %',
            observed_versions;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM pro_migration_lab.service_requests AS sr
        WHERE sr.assigned_team IS NULL
           OR sr.assigned_team NOT IN ('general', 'response')
    ) THEN
        RAISE EXCEPTION 'assigned_team contract verification failed';
    END IF;
END
$solution$;

-- Exercise 4: make the runner boundary and recovery distinction inspectable.
-- These are operational decisions, so the answer is a deterministic plan
-- matrix rather than pretend DDL executed by this disposable lesson.
SELECT *
FROM (
    VALUES
        (1, 'CREATE DATABASE', 'outside a transaction block',
         'PostgreSQL rejects it inside BEGIN/COMMIT',
         'drop only the verified disposable database or investigate'),
        (2, 'VACUUM', 'outside a transaction block',
         'VACUUM manages its own transaction lifecycle',
         'rerun after the blocking/error cause is understood'),
        (3, 'CREATE INDEX CONCURRENTLY', 'outside a transaction block',
         'the concurrent build spans multiple transactions',
         'inspect indisvalid/indisready before retry or reviewed drop'),
        (4, 'lossy UPDATE or representation change', 'reviewed transaction or batch',
         'old values may be discarded or observed externally',
         'pause writes, reconcile, then choose restore or forward fix')
) AS boundary_plan(
    step_number,
    operation,
    transaction_requirement,
    reason,
    recovery_policy
)
ORDER BY step_number;

-- Exercise 5: classify retry state before doing anything. Only
-- (manifest present + exact observed contract) is safely "already applied";
-- every partial or incompatible state must stop for investigation.
SELECT
    EXISTS (
        SELECT 1
        FROM pro_migration_lab.schema_migrations AS sm
        WHERE sm.migration_id = 6
          AND sm.content_tag = 'course-solution-006-v1'
    ) AS manifest_matches,
    EXISTS (
        SELECT 1
        FROM information_schema.columns AS c
        WHERE c.table_schema = 'pro_migration_lab'
          AND c.table_name = 'service_requests'
          AND c.column_name = 'assigned_team'
          AND c.data_type = 'text'
    ) AS schema_matches;

-- Exercise 6: these reviewed templates are intentionally not executed in this
-- fixture because CREATE INDEX CONCURRENTLY needs a runner-owned boundary:
--   CREATE INDEX CONCURRENTLY service_requests_team_idx
--     ON pro_migration_lab.service_requests (assigned_team);
-- A low-lock CHECK rollout uses ADD ... NOT VALID, remediation, and a separate
-- VALIDATE CONSTRAINT step with timeouts and monitoring.

SELECT *
FROM (
    VALUES
        (1, 'preflight', 'read only',
         'capture duplicate count, table size, locks, replica lag, and free disk',
         'abort if data violates the intended key or resource budget'),
        (2, 'build index', 'outside transaction',
         'CREATE INDEX CONCURRENTLY service_requests_team_idx ...',
         'abort on lock/lag/disk threshold'),
        (3, 'verify index', 'read only',
         'inspect pg_index.indisready and indisvalid plus query plan',
         'never blindly retry or drop an unknown same-named index'),
        (4, 'add CHECK', 'short transaction',
         'ADD CONSTRAINT ... CHECK (...) NOT VALID',
         'abort on lock timeout or rejected new writes'),
        (5, 'remediate history', 'restartable batches',
         'update bounded primary-key ranges and reconcile each batch',
         'pause on error-rate, WAL, lag, or count mismatch'),
        (6, 'validate CHECK', 'separate transaction',
         'VALIDATE CONSTRAINT after zero known violations',
         'abort on timeout; keep NOT VALID constraint protecting new writes'),
        (7, 'postflight', 'read only',
         'recheck catalog validity, violations, plans, lag, and error rate',
         'do not promote until all evidence matches'),
        (8, 'promote', 'deployment gate',
         'record owner, timestamps, commands, and observed evidence',
         'forward-fix or restore only from a reviewed incident decision')
) AS rollout_plan(
    step_number,
    rollout_step,
    transaction_boundary,
    required_evidence,
    abort_condition
)
ORDER BY step_number;

-- Exercise 7: compare three semantic manifests. The observed column set is
-- deliberately not filtered to expected names, so the FULL JOIN can report an
-- unexpected column instead of making that branch unreachable.
WITH expected(
    column_name,
    data_type,
    is_nullable,
    column_default,
    is_identity
) AS (
    VALUES
        ('request_id'::text, 'bigint'::text, 'NO'::text, NULL::text, 'YES'::text),
        ('request_key', 'text', 'NO', NULL, 'NO'),
        ('summary', 'text', 'NO', NULL, 'NO'),
        ('opened_at', 'timestamp with time zone', 'NO', 'clock_timestamp()', 'NO'),
        ('priority_code', 'text', 'NO', '''normal''::text', 'NO'),
        ('assigned_team', 'text', 'NO', '''general''::text', 'NO')
),
observed AS (
    SELECT
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.column_default,
        c.is_identity
    FROM information_schema.columns AS c
    WHERE c.table_schema = 'pro_migration_lab'
      AND c.table_name = 'service_requests'
)
SELECT
    COALESCE(e.column_name, o.column_name) AS column_name,
    e.data_type AS expected_type,
    o.data_type AS observed_type,
    e.is_nullable AS expected_nullable,
    o.is_nullable AS observed_nullable,
    e.column_default AS expected_default,
    o.column_default AS observed_default,
    e.is_identity AS expected_identity,
    o.is_identity AS observed_identity,
    CASE
        WHEN e.column_name IS NULL THEN 'unexpected'
        WHEN o.column_name IS NULL THEN 'missing'
        WHEN (e.data_type, e.is_nullable, e.column_default, e.is_identity)
             IS DISTINCT FROM
             (o.data_type, o.is_nullable, o.column_default, o.is_identity)
            THEN 'changed'
        ELSE 'matches'
    END AS drift_status
FROM expected AS e
FULL JOIN observed AS o USING (column_name)
ORDER BY column_name;

WITH expected(
    constraint_name,
    constraint_type,
    constraint_definition,
    is_validated
) AS (
    VALUES
        ('service_requests_pkey'::text, 'p'::"char",
         'PRIMARY KEY (request_id)'::text, true),
        ('service_requests_priority_fk', 'f'::"char",
         'FOREIGN KEY (priority_code) REFERENCES pro_migration_lab.priority_levels(priority_code)',
         true),
        ('service_requests_request_key_key', 'u'::"char",
         'UNIQUE (request_key)', true),
        ('service_requests_summary_check', 'c'::"char",
         'CHECK ((btrim(summary) <> ''''::text))', true),
        ('service_requests_assigned_team_ck', 'c'::"char",
         'CHECK ((assigned_team = ANY (ARRAY[''general''::text, ''response''::text])))',
         true)
),
observed AS (
    SELECT
        con.conname AS constraint_name,
        con.contype AS constraint_type,
        pg_get_constraintdef(con.oid) AS constraint_definition,
        con.convalidated AS is_validated
    FROM pg_catalog.pg_constraint AS con
    WHERE con.conrelid = 'pro_migration_lab.service_requests'::regclass
)
SELECT
    COALESCE(e.constraint_name, o.constraint_name) AS constraint_name,
    e.constraint_definition AS expected_definition,
    o.constraint_definition AS observed_definition,
    CASE
        WHEN e.constraint_name IS NULL THEN 'unexpected'
        WHEN o.constraint_name IS NULL THEN 'missing'
        WHEN (e.constraint_type, e.constraint_definition, e.is_validated)
             IS DISTINCT FROM
             (o.constraint_type, o.constraint_definition, o.is_validated)
            THEN 'changed'
        ELSE 'matches'
    END AS drift_status
FROM expected AS e
FULL JOIN observed AS o USING (constraint_name)
ORDER BY constraint_name;

WITH expected(index_name, is_unique, key_columns, is_partial) AS (
    VALUES
        ('service_requests_pkey'::text, true, ARRAY['request_id']::text[], false),
        ('service_requests_request_key_key', true, ARRAY['request_key']::text[], false)
),
observed AS (
    SELECT
        idx.relname AS index_name,
        i.indisunique AS is_unique,
        array_agg(att.attname::text ORDER BY keys.ordinality)
            FILTER (WHERE att.attname IS NOT NULL) AS key_columns,
        i.indpred IS NOT NULL AS is_partial
    FROM pg_catalog.pg_index AS i
    JOIN pg_catalog.pg_class AS tbl
      ON tbl.oid = i.indrelid
    JOIN pg_catalog.pg_namespace AS ns
      ON ns.oid = tbl.relnamespace
    JOIN pg_catalog.pg_class AS idx
      ON idx.oid = i.indexrelid
    LEFT JOIN LATERAL unnest(i.indkey)
        WITH ORDINALITY AS keys(attnum, ordinality)
      ON true
    LEFT JOIN pg_catalog.pg_attribute AS att
      ON att.attrelid = tbl.oid
     AND att.attnum = keys.attnum
    WHERE ns.nspname = 'pro_migration_lab'
      AND tbl.relname = 'service_requests'
    GROUP BY idx.relname, i.indisunique, i.indpred
)
SELECT
    COALESCE(e.index_name, o.index_name) AS index_name,
    e.key_columns AS expected_key_columns,
    o.key_columns AS observed_key_columns,
    CASE
        WHEN e.index_name IS NULL THEN 'unexpected'
        WHEN o.index_name IS NULL THEN 'missing'
        WHEN (e.is_unique, e.key_columns, e.is_partial)
             IS DISTINCT FROM
             (o.is_unique, o.key_columns, o.is_partial)
            THEN 'changed'
        ELSE 'matches'
    END AS drift_status
FROM expected AS e
FULL JOIN observed AS o USING (index_name)
ORDER BY index_name;

-- Exercise 8: recovery is phase-specific; this deterministic matrix is a
-- runbook skeleton, not permission to mutate a real environment.
SELECT *
FROM (
    VALUES
        (1, 'expand', 'old and new', 'old and new compatible writes',
         'additive objects can usually remain',
         'catalog snapshot and old/new-reader smoke tests',
         'keep additive schema and forward-fix'),
        (2, 'backfill', 'old and new while compatible', 'pause or fence on mismatch',
         'restart only from reconciled key checkpoints',
         'source-of-truth decision, key counts, rejects, lag, backup point',
         'pause writers, reconcile every key, then resume'),
        (3, 'contract', 'new version only', 'old writers fenced',
         'schema syntax may reverse; discarded data may not',
         'zero old traffic, restore test, lossy-change inventory, owner approval',
         'restore or forward-fix according to evidence')
) AS recovery(
    step_number,
    phase,
    compatible_versions,
    writes_state,
    reversible_action,
    required_evidence,
    primary_action
)
ORDER BY step_number;

\ir ../fixtures/migrations/cleanup.sql
