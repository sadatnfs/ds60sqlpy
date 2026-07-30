-- Migration 004: contract only after old writers are retired and backfill
-- verification has passed.
\set ON_ERROR_STOP on
BEGIN;

SELECT EXISTS (
    SELECT 1
    FROM pro_migration_lab.schema_migrations AS sm
    WHERE sm.migration_id = 4
) AS migration_applied
\gset

\if :migration_applied
    \echo 'Migration 004 already applied; skipping immutable body'
\else
    ALTER TABLE pro_migration_lab.service_requests
        ALTER COLUMN priority_code SET DEFAULT 'normal',
        ALTER COLUMN priority_code SET NOT NULL;

    -- The old view depends on urgency_label, so replace the dependency and
    -- storage column atomically inside this migration.
    DROP VIEW pro_migration_lab.service_requests_api;

    ALTER TABLE pro_migration_lab.service_requests
        DROP COLUMN urgency_label;

    CREATE VIEW pro_migration_lab.service_requests_api AS
    SELECT
        sr.request_id,
        sr.request_key,
        sr.summary,
        sr.priority_code,
        sr.opened_at
    FROM pro_migration_lab.service_requests AS sr;

    INSERT INTO pro_migration_lab.schema_migrations (
        migration_id,
        migration_name,
        content_tag
    )
    VALUES (
        4,
        'contract_priority',
        'course-fixture-004-v1'
    );
\endif

COMMIT;

