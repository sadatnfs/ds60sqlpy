-- SQL-TYPES-01 executable solutions
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_types_lab;

CREATE TABLE pro_types_lab.documents (
    document_id uuid PRIMARY KEY,
    state text NOT NULL CHECK (state IN ('draft', 'published')),
    title text NOT NULL,
    body text NOT NULL,
    tags text[] NOT NULL,
    availability daterange NOT NULL,
    blackout_windows datemultirange NOT NULL DEFAULT '{}'::datemultirange,
    metadata jsonb NOT NULL CHECK (jsonb_typeof(metadata) = 'object'),
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

INSERT INTO pro_types_lab.documents
VALUES
    (
        '00000000-0000-0000-0000-000000000201',
        'published',
        'Safe schema migrations',
        'Verify each schema migration and backfill before contract.',
        ARRAY['postgresql', 'sql', 'operations'],
        daterange(DATE '2026-01-01', DATE '2027-01-01', '[)'),
        datemultirange(
            daterange(DATE '2026-08-10', DATE '2026-08-12', '[)')
        ),
        '{"minutes":45,"audience":["operator"]}',
        DEFAULT
    ),
    (
        '00000000-0000-0000-0000-000000000202',
        'published',
        'SQL analytics',
        'Build retention and funnel queries with explicit grain.',
        ARRAY['postgresql', 'sql', 'analytics'],
        daterange(DATE '2026-01-01', DATE '2027-01-01', '[)'),
        '{}'::datemultirange,
        '{"minutes":35,"audience":["analyst"]}',
        DEFAULT
    ),
    (
        '00000000-0000-0000-0000-000000000203',
        'draft',
        'Python notes',
        'Structured logs and configuration.',
        ARRAY['python'],
        daterange(DATE '2026-01-01', DATE '2026-06-01', '[)'),
        '{}'::datemultirange,
        '{"minutes":20,"audience":["developer"]}',
        DEFAULT
    );

-- Exercise 1.
SELECT
    d.document_id,
    d.title
FROM pro_types_lab.documents AS d
WHERE d.state = 'published'
  AND d.tags @> ARRAY['postgresql', 'operations']::text[]
ORDER BY d.document_id;

-- Exercise 2. The first document is blacked out, so no row is expected.
SELECT
    d.document_id,
    d.title
FROM pro_types_lab.documents AS d
WHERE d.availability @> DATE '2026-08-11'
  AND NOT (d.blackout_windows @> DATE '2026-08-11')
ORDER BY d.document_id;

-- Exercise 3. Fixture ownership guarantees numeric JSON minutes.
SELECT
    d.document_id,
    d.title,
    (d.metadata ->> 'minutes')::integer AS minutes
FROM pro_types_lab.documents AS d
WHERE d.metadata @? '$.minutes ? (@.type() == "number" && @ > 30)'
ORDER BY d.document_id;

-- Exercise 4.
WITH query AS (
    SELECT websearch_to_tsquery(
        'english'::regconfig,
        '"schema migration" verify'
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

DO $solution$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM pro_types_lab.documents AS d
        WHERE d.tags @> ARRAY['postgresql', 'operations']::text[]
    ) <> 1 THEN
        RAISE EXCEPTION 'tag containment solution failed';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM pro_types_lab.documents AS d
        WHERE d.document_id =
            '00000000-0000-0000-0000-000000000201'::uuid
          AND d.availability @> DATE '2026-08-11'
          AND NOT (d.blackout_windows @> DATE '2026-08-11')
    ) THEN
        RAISE EXCEPTION 'blackout exclusion solution failed';
    END IF;
END
$solution$;

ROLLBACK;

