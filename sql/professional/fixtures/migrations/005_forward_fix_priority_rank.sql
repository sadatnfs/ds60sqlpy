-- Migration 005: forward fix. Migration 002 may already be deployed, so its
-- rank constraint is not edited in place when a fourth rank becomes necessary.
\set ON_ERROR_STOP on
BEGIN;

SELECT EXISTS (
    SELECT 1
    FROM pro_migration_lab.schema_migrations AS sm
    WHERE sm.migration_id = 5
) AS migration_applied
\gset

\if :migration_applied
    \echo 'Migration 005 already applied; skipping immutable body'
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

