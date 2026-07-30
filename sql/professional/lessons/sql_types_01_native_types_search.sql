-- SQL-TYPES-01: PostgreSQL-native types and searchable documents
-- Target: PostgreSQL 16+

\set ON_ERROR_STOP on
\echo 'SQL-TYPES-01: disposable native-type and search lab'
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_types_lab;

CREATE DOMAIN pro_types_lab.email_address AS text
CHECK (
    VALUE ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
);

CREATE TYPE pro_types_lab.document_state AS ENUM (
    'draft',
    'published',
    'retired'
);

CREATE TABLE pro_types_lab.documents (
    document_id uuid PRIMARY KEY,
    owner_email pro_types_lab.email_address NOT NULL,
    state pro_types_lab.document_state NOT NULL DEFAULT 'draft',
    title text NOT NULL CHECK (btrim(title) <> ''),
    body text NOT NULL,
    tags text[] NOT NULL DEFAULT ARRAY[]::text[],
    availability daterange NOT NULL
        CHECK (NOT isempty(availability)),
    blackout_windows datemultirange NOT NULL
        DEFAULT '{}'::datemultirange,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(metadata) = 'object'),
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(
            to_tsvector('english'::regconfig, COALESCE(title, '')),
            'A'
        )
        ||
        setweight(
            to_tsvector('english'::regconfig, COALESCE(body, '')),
            'B'
        )
    ) STORED
);

INSERT INTO pro_types_lab.documents (
    document_id,
    owner_email,
    state,
    title,
    body,
    tags,
    availability,
    blackout_windows,
    metadata
)
VALUES
    (
        '00000000-0000-0000-0000-000000000101',
        'avery@example.test',
        'published',
        'Safe schema migrations',
        'Plan additive changes, backfill data, verify invariants, and contract later.',
        ARRAY['postgresql', 'sql', 'operations'],
        daterange(DATE '2026-01-01', DATE '2027-01-01', '[)'),
        datemultirange(
            daterange(DATE '2026-07-01', DATE '2026-07-08', '[)')
        ),
        '{"audience":["developer","operator"],"difficulty":"advanced","minutes":45}'
    ),
    (
        '00000000-0000-0000-0000-000000000102',
        'morgan@example.test',
        'published',
        'Analytical SQL patterns',
        'Use windows and explicit grain for sessions, funnels, and retention.',
        ARRAY['postgresql', 'sql', 'analytics'],
        daterange(DATE '2026-03-01', DATE '2026-10-01', '[)'),
        '{}'::datemultirange,
        '{"audience":["analyst"],"difficulty":"intermediate","minutes":35}'
    ),
    (
        '00000000-0000-0000-0000-000000000103',
        'taylor@example.test',
        'draft',
        'Python service notes',
        'Validate configuration and add request identifiers to structured logs.',
        ARRAY['python', 'services'],
        daterange(DATE '2026-05-01', DATE '2026-12-01', '[)'),
        datemultirange(
            daterange(DATE '2026-08-10', DATE '2026-08-12', '[)'),
            daterange(DATE '2026-09-03', DATE '2026-09-05', '[)')
        ),
        '{"audience":["developer"],"difficulty":"intermediate","minutes":25}'
    );

-- Operator-compatible indexes. Index presence does not promise planner use.
CREATE INDEX documents_tags_gin
ON pro_types_lab.documents
USING gin (tags);

CREATE INDEX documents_metadata_path_gin
ON pro_types_lab.documents
USING gin (metadata jsonb_path_ops);

CREATE INDEX documents_search_vector_gin
ON pro_types_lab.documents
USING gin (search_vector);

CREATE INDEX documents_availability_gist
ON pro_types_lab.documents
USING gist (availability);

\echo 'Arrays: containment and scalar membership are different questions'
SELECT
    d.document_id,
    d.title,
    d.tags
FROM pro_types_lab.documents AS d
WHERE d.tags @> ARRAY['sql']::text[]
  AND 'postgresql' = ANY(d.tags)
ORDER BY d.document_id;

\echo 'Ranges use explicit [lower, upper) boundary semantics'
SELECT
    d.document_id,
    d.title,
    lower(d.availability) AS starts_on,
    upper(d.availability) AS ends_before,
    d.availability @> DATE '2026-06-15' AS available_on_test_date,
    d.blackout_windows @> DATE '2026-07-03' AS blacked_out_on_test_date
FROM pro_types_lab.documents AS d
WHERE d.availability && daterange(
    DATE '2026-06-01',
    DATE '2026-07-01',
    '[)'
)
ORDER BY d.document_id;

\echo 'JSONPath predicates keep document-shape assumptions explicit'
SELECT
    d.document_id,
    d.title,
    d.metadata ->> 'difficulty' AS difficulty,
    (d.metadata ->> 'minutes')::integer AS minutes
FROM pro_types_lab.documents AS d
WHERE d.metadata @? '$.audience[*] ? (@ == "analyst")'
ORDER BY d.document_id;

\echo 'Full-text search parses, normalizes, and ranks language-aware lexemes'
WITH query AS (
    SELECT websearch_to_tsquery(
        'english'::regconfig,
        'safe migration'
    ) AS ts_query
)
SELECT
    d.document_id,
    d.title,
    ts_rank_cd(d.search_vector, query.ts_query) AS rank_score
FROM pro_types_lab.documents AS d
CROSS JOIN query
WHERE d.search_vector @@ query.ts_query
ORDER BY rank_score DESC, d.document_id;

\echo 'Index catalog and optional extension availability'
SELECT
    i.indexname,
    i.indexdef
FROM pg_catalog.pg_indexes AS i
WHERE i.schemaname = 'pro_types_lab'
ORDER BY i.indexname;

SELECT
    e.name,
    e.default_version,
    e.installed_version
FROM pg_catalog.pg_available_extensions AS e
WHERE e.name = 'pg_trgm';

-- Exercises:
--
-- 1. Return published documents tagged with both postgresql and operations.
--    Explain why @> is a better fit than two ANY expressions for this question.
--
-- 2. Find documents available on 2026-08-11 but not inside a blackout window.
--    State the inclusive/exclusive boundary rule.
--
-- 3. Use JSONPath to return documents whose numeric minutes exceed 30. Avoid
--    assuming that every arbitrary JSON value can be cast safely.
--
-- 4. Search for the web-style query '"schema migration" verify' and rank
--    matches deterministically.
--
-- 5. Compare jsonb_ops with jsonb_path_ops, and GIN full-text search with an
--    optional pg_trgm similarity index. State which operators and update costs
--    matter before choosing.
--
-- 6. Decide which modeled fields deserve a domain, enum, reference table,
--    array, range, JSONB document, or ordinary normalized relation.

DO $self_check$
BEGIN
    IF (SELECT COUNT(*) FROM pro_types_lab.documents) <> 3 THEN
        RAISE EXCEPTION 'unexpected document count';
    END IF;
    IF (
        SELECT COUNT(*)
        FROM pro_types_lab.documents AS d
        WHERE d.search_vector @@ plainto_tsquery(
            'english'::regconfig,
            'migrations'
        )
    ) <> 1 THEN
        RAISE EXCEPTION 'generated search vector check failed';
    END IF;
END
$self_check$;

ROLLBACK;
\echo 'SQL-TYPES-01 complete: pro_types_lab was rolled back'

