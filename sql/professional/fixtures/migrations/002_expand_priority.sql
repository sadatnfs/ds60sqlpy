-- Migration 002: expand. Keep the old column while adding the new model.
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
        RAISE EXCEPTION 'migration 002 requires the verified migration manifest';
    END IF;

    SELECT
        EXISTS (
            SELECT 1 FROM pro_migration_lab.schema_migrations
            WHERE migration_id = 2
        ),
        EXISTS (
            SELECT 1 FROM pro_migration_lab.schema_migrations
            WHERE migration_id = 2
              AND migration_name = 'expand_priority'
              AND content_tag = 'course-fixture-002-v1'
        )
    INTO id_exists, identity_matches;

    IF id_exists AND NOT identity_matches THEN
        RAISE EXCEPTION 'migration 002 identity mismatch; refusing to skip';
    END IF;

    IF identity_matches AND (
        to_regclass('pro_migration_lab.priority_levels') IS NULL
        OR NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'pro_migration_lab'
              AND table_name = 'service_requests'
              AND column_name = 'priority_code'
              AND data_type = 'text'
        )
        OR NOT EXISTS (
            SELECT 1
            FROM pg_catalog.pg_constraint
            WHERE conrelid = 'pro_migration_lab.service_requests'::regclass
              AND conname = 'service_requests_priority_fk'
              AND contype = 'f'
        )
    ) THEN
        RAISE EXCEPTION
            'migration 002 manifest matches but schema contract drifted';
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
    \echo 'Migration 002 identity and schema contract verified; skipping body'
\else
    CREATE TABLE pro_migration_lab.priority_levels (
        priority_code text PRIMARY KEY,
        display_name text NOT NULL UNIQUE,
        sort_rank integer NOT NULL,
        CONSTRAINT priority_levels_sort_rank_ck
            CHECK (sort_rank BETWEEN 1 AND 3)
    );

    \ir seed_priority_levels.sql

    ALTER TABLE pro_migration_lab.service_requests
        ADD COLUMN priority_code text;

    -- NOT VALID avoids a historical-table scan while the new column is
    -- backfilled. New and updated non-NULL values are still checked.
    ALTER TABLE pro_migration_lab.service_requests
        ADD CONSTRAINT service_requests_priority_fk
        FOREIGN KEY (priority_code)
        REFERENCES pro_migration_lab.priority_levels (priority_code)
        NOT VALID;

    CREATE OR REPLACE VIEW pro_migration_lab.service_requests_api AS
    SELECT
        sr.request_id,
        sr.request_key,
        sr.summary,
        COALESCE(sr.priority_code, sr.urgency_label) AS priority_code,
        sr.opened_at
    FROM pro_migration_lab.service_requests AS sr;

    INSERT INTO pro_migration_lab.schema_migrations (
        migration_id,
        migration_name,
        content_tag
    )
    VALUES (
        2,
        'expand_priority',
        'course-fixture-002-v1'
    );
\endif

COMMIT;
