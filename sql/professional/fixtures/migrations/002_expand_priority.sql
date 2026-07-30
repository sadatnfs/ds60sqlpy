-- Migration 002: expand. Keep the old column while adding the new model.
\set ON_ERROR_STOP on
BEGIN;

SELECT EXISTS (
    SELECT 1
    FROM pro_migration_lab.schema_migrations AS sm
    WHERE sm.migration_id = 2
) AS migration_applied
\gset

\if :migration_applied
    \echo 'Migration 002 already applied; skipping immutable body'
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

