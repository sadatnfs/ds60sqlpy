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
\ir ../fixtures/migrations/run_all.sql

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

-- Exercise 2: compatibility is demonstrated above: the stable API query still
-- has its original interface while migrations 6-8 evolve only storage.

-- Exercise 4: CREATE DATABASE, VACUUM, and CREATE INDEX CONCURRENTLY need a
-- runner-managed nontransactional boundary. Lossy recovery is a restore or
-- forward-fix decision, not an automatic down-file convention.

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
-- fixture because CREATE INDEX CONCURRENTLY cannot run in a transaction:
--   CREATE INDEX CONCURRENTLY service_requests_team_idx
--     ON pro_migration_lab.service_requests (assigned_team);
-- A low-lock CHECK rollout uses ADD ... NOT VALID, remediation, and a separate
-- VALIDATE CONSTRAINT step with timeouts and monitoring.

-- Exercise 7: a compact expected-versus-observed column drift report. Production
-- contracts should extend this pattern to defaults, constraints, and indexes.
WITH expected(column_name, data_type, is_nullable) AS (
    VALUES
        ('request_key'::text, 'text'::text, 'NO'::text),
        ('assigned_team'::text, 'text'::text, 'NO'::text)
),
observed AS (
    SELECT c.column_name, c.data_type, c.is_nullable
    FROM information_schema.columns AS c
    WHERE c.table_schema = 'pro_migration_lab'
      AND c.table_name = 'service_requests'
      AND c.column_name IN ('request_key', 'assigned_team')
)
SELECT
    COALESCE(e.column_name, o.column_name) AS column_name,
    CASE
        WHEN e.column_name IS NULL THEN 'unexpected'
        WHEN o.column_name IS NULL THEN 'missing'
        WHEN (e.data_type, e.is_nullable)
             IS DISTINCT FROM (o.data_type, o.is_nullable) THEN 'changed'
        ELSE 'matches'
    END AS drift_status
FROM expected AS e
FULL JOIN observed AS o USING (column_name)
ORDER BY column_name;

-- Exercise 8: recovery is phase-specific; this deterministic matrix is a
-- runbook skeleton, not permission to mutate a real environment.
SELECT *
FROM (
    VALUES
        ('expand', 'keep additive schema; forward-fix if compatible'),
        ('backfill', 'pause writers; choose source of truth; reconcile keys'),
        ('contract', 'keep old writers fenced; restore or forward-fix by evidence')
) AS recovery(phase, primary_action)
ORDER BY phase;

\ir ../fixtures/migrations/cleanup.sql
