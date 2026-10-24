-- Migration 001: baseline schema and stable application-facing view.
\set ON_ERROR_STOP on
BEGIN;

SELECT pg_catalog.pg_advisory_xact_lock(
    pg_catalog.hashtextextended('ds60sqlpy:pro_migration_lab', 0)
);

-- Fail closed before deciding an existing manifest row is safe to skip.
-- content_tag is a reviewed immutable fixture identity, not a cryptographic
-- file checksum; production runners should record a real content digest.
DO $preflight$
DECLARE
    manifest_exists boolean :=
        to_regclass('pro_migration_lab.schema_migrations') IS NOT NULL;
    id_exists boolean := false;
    identity_matches boolean := false;
BEGIN
    IF manifest_exists THEN
        EXECUTE $sql$
            SELECT
                EXISTS (
                    SELECT 1
                    FROM pro_migration_lab.schema_migrations
                    WHERE migration_id = 1
                ),
                EXISTS (
                    SELECT 1
                    FROM pro_migration_lab.schema_migrations
                    WHERE migration_id = 1
                      AND migration_name = 'create_service_requests'
                      AND content_tag = 'course-fixture-001-v1'
                )
        $sql$
        INTO id_exists, identity_matches;

        IF id_exists AND NOT identity_matches THEN
            RAISE EXCEPTION
                'migration 001 identity mismatch; refusing to skip';
        END IF;

        IF identity_matches AND (
            to_regclass('pro_migration_lab.service_requests') IS NULL
            OR to_regclass('pro_migration_lab.service_requests_api') IS NULL
            OR NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'pro_migration_lab'
                  AND table_name = 'schema_migrations'
                  AND column_name = 'content_tag'
                  AND data_type = 'text'
                  AND is_nullable = 'NO'
            )
            OR NOT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'pro_migration_lab'
                  AND table_name = 'service_requests'
                  AND column_name = 'request_key'
                  AND data_type = 'text'
                  AND is_nullable = 'NO'
            )
        ) THEN
            RAISE EXCEPTION
                'migration 001 manifest matches but schema contract drifted';
        END IF;
    ELSIF EXISTS (
        SELECT 1
        FROM pg_catalog.pg_namespace
        WHERE nspname = 'pro_migration_lab'
    ) THEN
        RAISE EXCEPTION
            'pro_migration_lab exists without the reviewed manifest table';
    END IF;

    PERFORM pg_catalog.set_config(
        'ds60.migration_applied',
        identity_matches::text,
        true
    );
END
$preflight$;

SELECT pg_catalog.current_setting('ds60.migration_applied')::boolean
    AS migration_applied
\gset

\if :migration_applied
    \echo 'Migration 001 identity and schema contract verified; skipping body'
\else
    CREATE SCHEMA pro_migration_lab;

    CREATE TABLE pro_migration_lab.schema_migrations (
        migration_id integer PRIMARY KEY,
        migration_name text NOT NULL UNIQUE,
        content_tag text NOT NULL,
        applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
    );

    CREATE TABLE pro_migration_lab.service_requests (
        request_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        request_key text NOT NULL UNIQUE,
        summary text NOT NULL CHECK (btrim(summary) <> ''),
        urgency_label text NOT NULL DEFAULT 'normal'
            CONSTRAINT service_requests_urgency_label_ck
            CHECK (urgency_label IN ('low', 'normal', 'high')),
        opened_at timestamptz NOT NULL DEFAULT clock_timestamp()
    );

    -- Applications read this view rather than the storage column directly.
    -- Its priority_code interface remains stable across migrations 002-004.
    CREATE VIEW pro_migration_lab.service_requests_api AS
    SELECT
        sr.request_id,
        sr.request_key,
        sr.summary,
        sr.urgency_label AS priority_code,
        sr.opened_at
    FROM pro_migration_lab.service_requests AS sr;

    -- Deterministic fixture rows give the later backfill something to migrate.
    INSERT INTO pro_migration_lab.service_requests (
        request_key,
        summary,
        urgency_label,
        opened_at
    )
    VALUES
        ('REQ-100', 'Replace a worn cable', 'low', TIMESTAMPTZ '2026-01-05 09:00:00+00'),
        ('REQ-101', 'Restore room access', 'high', TIMESTAMPTZ '2026-01-05 10:00:00+00'),
        ('REQ-102', 'Update a contact label', 'normal', TIMESTAMPTZ '2026-01-05 11:00:00+00');

    INSERT INTO pro_migration_lab.schema_migrations (
        migration_id,
        migration_name,
        content_tag
    )
    VALUES (
        1,
        'create_service_requests',
        'course-fixture-001-v1'
    );
\endif

COMMIT;
