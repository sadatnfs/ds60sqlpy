-- Migration 003: migrate existing rows, then validate the new relationship.
\set ON_ERROR_STOP on
BEGIN;

SELECT pg_catalog.pg_advisory_xact_lock(
    pg_catalog.hashtextextended('ds60sqlpy:pro_migration_lab', 0)
);

DO $preflight$
DECLARE
    id_exists boolean;
    identity_matches boolean;
BEGIN
    IF to_regclass('pro_migration_lab.schema_migrations') IS NULL THEN
        RAISE EXCEPTION 'migration 003 requires the verified migration manifest';
    END IF;

    SELECT
        EXISTS (
            SELECT 1 FROM pro_migration_lab.schema_migrations
            WHERE migration_id = 3
        ),
        EXISTS (
            SELECT 1 FROM pro_migration_lab.schema_migrations
            WHERE migration_id = 3
              AND migration_name = 'backfill_priority'
              AND content_tag = 'course-fixture-003-v1'
        )
    INTO id_exists, identity_matches;

    IF id_exists AND NOT identity_matches THEN
        RAISE EXCEPTION 'migration 003 identity mismatch; refusing to skip';
    END IF;

    IF identity_matches AND (
        EXISTS (
            SELECT 1
            FROM pro_migration_lab.service_requests
            WHERE priority_code IS NULL
        )
        OR NOT EXISTS (
            SELECT 1
            FROM pg_catalog.pg_constraint
            WHERE conrelid = 'pro_migration_lab.service_requests'::regclass
              AND conname = 'service_requests_priority_fk'
              AND convalidated
        )
    ) THEN
        RAISE EXCEPTION
            'migration 003 manifest matches but backfill/constraint drifted';
    END IF;

    PERFORM pg_catalog.set_config(
        'ds60.migration_applied', identity_matches::text, true
    );
END
$preflight$;

SELECT pg_catalog.current_setting('ds60.migration_applied')::boolean
    AS migration_applied
\gset

\if :migration_applied
    \echo 'Migration 003 identity and schema contract verified; skipping body'
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
