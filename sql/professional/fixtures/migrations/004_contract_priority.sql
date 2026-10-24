-- Migration 004: contract only after old writers are retired and backfill
-- verification has passed.
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
        RAISE EXCEPTION 'migration 004 requires the verified migration manifest';
    END IF;

    SELECT
        EXISTS (
            SELECT 1 FROM pro_migration_lab.schema_migrations
            WHERE migration_id = 4
        ),
        EXISTS (
            SELECT 1 FROM pro_migration_lab.schema_migrations
            WHERE migration_id = 4
              AND migration_name = 'contract_priority'
              AND content_tag = 'course-fixture-004-v1'
        )
    INTO id_exists, identity_matches;

    IF id_exists AND NOT identity_matches THEN
        RAISE EXCEPTION 'migration 004 identity mismatch; refusing to skip';
    END IF;

    IF identity_matches AND (
        EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'pro_migration_lab'
              AND table_name = 'service_requests'
              AND column_name = 'urgency_label'
        )
        OR NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'pro_migration_lab'
              AND table_name = 'service_requests'
              AND column_name = 'priority_code'
              AND is_nullable = 'NO'
              AND column_default = '''normal''::text'
        )
        OR to_regclass('pro_migration_lab.service_requests_api') IS NULL
    ) THEN
        RAISE EXCEPTION
            'migration 004 manifest matches but schema contract drifted';
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
    \echo 'Migration 004 identity and schema contract verified; skipping body'
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
