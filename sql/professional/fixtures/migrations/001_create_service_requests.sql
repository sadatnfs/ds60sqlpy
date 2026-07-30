-- Migration 001: baseline schema and stable application-facing view.
\set ON_ERROR_STOP on
BEGIN;

CREATE SCHEMA IF NOT EXISTS pro_migration_lab;

CREATE TABLE IF NOT EXISTS pro_migration_lab.schema_migrations (
    migration_id integer PRIMARY KEY,
    migration_name text NOT NULL UNIQUE,
    content_tag text NOT NULL,
    applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

SELECT EXISTS (
    SELECT 1
    FROM pro_migration_lab.schema_migrations AS sm
    WHERE sm.migration_id = 1
) AS migration_applied
\gset

\if :migration_applied
    \echo 'Migration 001 already applied; skipping immutable body'
\else
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

