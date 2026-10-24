-- Verify the final fixture state. Any failed invariant stops psql.
\set ON_ERROR_STOP on

DO $verify$
DECLARE
    observed_versions integer[];
BEGIN
    SELECT array_agg(sm.migration_id ORDER BY sm.migration_id)
    INTO observed_versions
    FROM pro_migration_lab.schema_migrations AS sm;

    IF observed_versions <> ARRAY[1, 2, 3, 4, 5] THEN
        RAISE EXCEPTION
            'expected migration versions 1-5, observed %',
            observed_versions;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns AS c
        WHERE c.table_schema = 'pro_migration_lab'
          AND c.table_name = 'service_requests'
          AND c.column_name = 'urgency_label'
    ) THEN
        RAISE EXCEPTION 'legacy urgency_label still exists';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns AS c
        WHERE c.table_schema = 'pro_migration_lab'
          AND c.table_name = 'service_requests'
          AND c.column_name = 'priority_code'
          AND c.is_nullable = 'NO'
    ) THEN
        RAISE EXCEPTION 'priority_code is missing or still nullable';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM pro_migration_lab.service_requests AS sr
        WHERE sr.priority_code IS NULL
    ) THEN
        RAISE EXCEPTION 'service requests contain NULL priority_code';
    END IF;

    IF (
        SELECT COUNT(*)
        FROM pro_migration_lab.priority_levels AS pl
    ) <> 4 THEN
        RAISE EXCEPTION 'expected four priority reference rows';
    END IF;

    IF (
        SELECT COUNT(*)
        FROM pro_migration_lab.service_requests_api AS api
    ) <> 3 THEN
        RAISE EXCEPTION 'stable API view did not preserve three fixture rows';
    END IF;
END
$verify$;

SELECT
    sm.migration_id,
    sm.migration_name,
    sm.content_tag
FROM pro_migration_lab.schema_migrations AS sm
ORDER BY sm.migration_id;

SELECT
    api.request_key,
    api.summary,
    api.priority_code,
    api.opened_at
FROM pro_migration_lab.service_requests_api AS api
ORDER BY api.request_key;

SELECT
    pl.priority_code,
    pl.display_name,
    pl.sort_rank
FROM pro_migration_lab.priority_levels AS pl
ORDER BY pl.sort_rank, pl.priority_code;

\echo 'Migration fixture verification passed'

