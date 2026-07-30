-- Migration 003: migrate existing rows, then validate the new relationship.
\set ON_ERROR_STOP on
BEGIN;

SELECT EXISTS (
    SELECT 1
    FROM pro_migration_lab.schema_migrations AS sm
    WHERE sm.migration_id = 3
) AS migration_applied
\gset

\if :migration_applied
    \echo 'Migration 003 already applied; skipping immutable body'
\else
    UPDATE pro_migration_lab.service_requests AS sr
    SET priority_code = sr.urgency_label
    WHERE sr.priority_code IS NULL;

    DO $migration$
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM pro_migration_lab.service_requests AS sr
            WHERE sr.priority_code IS NULL
        ) THEN
            RAISE EXCEPTION 'priority backfill left NULL rows';
        END IF;
    END
    $migration$;

    ALTER TABLE pro_migration_lab.service_requests
        VALIDATE CONSTRAINT service_requests_priority_fk;

    INSERT INTO pro_migration_lab.schema_migrations (
        migration_id,
        migration_name,
        content_tag
    )
    VALUES (
        3,
        'backfill_priority',
        'course-fixture-003-v1'
    );
\endif

COMMIT;

