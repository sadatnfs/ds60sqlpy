-- SQL-FOUND-02 executable solutions
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

\ir ../fixtures/migrations/cleanup.sql

