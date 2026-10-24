-- Migration 005: forward fix. Migration 002 may already be deployed, so its
-- rank constraint is not edited in place when a fourth rank becomes necessary.
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
        RAISE EXCEPTION 'migration 005 requires the verified migration manifest';
    END IF;

    SELECT
        EXISTS (
            SELECT 1 FROM pro_migration_lab.schema_migrations
            WHERE migration_id = 5
        ),
        EXISTS (
            SELECT 1 FROM pro_migration_lab.schema_migrations
            WHERE migration_id = 5
              AND migration_name = 'forward_fix_priority_rank'
              AND content_tag = 'course-fixture-005-v1'
        )
    INTO id_exists, identity_matches;

    IF id_exists AND NOT identity_matches THEN
        RAISE EXCEPTION 'migration 005 identity mismatch; refusing to skip';
    END IF;

    IF identity_matches AND (
        NOT EXISTS (
            SELECT 1
            FROM pro_migration_lab.priority_levels
            WHERE priority_code = 'critical'
              AND sort_rank = 4
        )
        OR NOT EXISTS (
            SELECT 1
            FROM pg_catalog.pg_constraint
            WHERE conrelid = 'pro_migration_lab.priority_levels'::regclass
              AND conname = 'priority_levels_sort_rank_ck'
              AND pg_catalog.pg_get_constraintdef(oid) LIKE '%sort_rank >= 1%'
              AND pg_catalog.pg_get_constraintdef(oid) LIKE '%sort_rank <= 9%'
        )
    ) THEN
        RAISE EXCEPTION
            'migration 005 manifest matches but forward-fix contract drifted';
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
    \echo 'Migration 005 identity and schema contract verified; skipping body'
\else
    ALTER TABLE pro_migration_lab.priority_levels
        DROP CONSTRAINT priority_levels_sort_rank_ck;

    ALTER TABLE pro_migration_lab.priority_levels
        ADD CONSTRAINT priority_levels_sort_rank_ck
        CHECK (sort_rank BETWEEN 1 AND 9);

    INSERT INTO pro_migration_lab.priority_levels (
        priority_code,
        display_name,
        sort_rank
    )
    VALUES ('critical', 'Critical priority', 4)
    ON CONFLICT (priority_code) DO UPDATE
    SET display_name = EXCLUDED.display_name,
        sort_rank = EXCLUDED.sort_rank;

    INSERT INTO pro_migration_lab.schema_migrations (
        migration_id,
        migration_name,
        content_tag
    )
    VALUES (
        5,
        'forward_fix_priority_rank',
        'course-fixture-005-v1'
    );
\endif

COMMIT;
