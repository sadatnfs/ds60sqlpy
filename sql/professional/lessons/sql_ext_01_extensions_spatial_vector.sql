-- SQL-EXT-01: Extensions, spatial data, and vectors
-- Target: PostgreSQL 16+
-- This default path never executes CREATE EXTENSION.

\set ON_ERROR_STOP on
\echo 'SQL-EXT-01: inspect extension capabilities without enabling anything'

WITH requested(name, purpose) AS (
    VALUES
        ('pg_trgm'::text, 'trigram similarity and wildcard indexes'::text),
        ('citext', 'case-insensitive text type'),
        ('pgcrypto', 'cryptographic digest/encryption helpers'),
        ('postgis', 'coordinate reference systems and spatial operations'),
        ('vector', 'vector type and nearest-neighbour indexes'),
        ('postgres_fdw', 'foreign PostgreSQL tables')
)
SELECT
    requested.name,
    requested.purpose,
    available.default_version,
    available.installed_version,
    available.name IS NOT NULL AS available_on_server,
    available.installed_version IS NOT NULL AS installed_in_database
FROM requested
LEFT JOIN pg_catalog.pg_available_extensions AS available
  ON available.name = requested.name
ORDER BY requested.name;

BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_extensions_lab;

-- Built-in fallback for a narrow case-insensitive identifier requirement.
CREATE TABLE pro_extensions_lab.resources (
    resource_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    display_name text NOT NULL CHECK (btrim(display_name) <> ''),
    normalized_name text GENERATED ALWAYS AS (lower(display_name)) STORED,
    summary text NOT NULL,
    location point NOT NULL,
    embedding double precision[] NOT NULL
        CHECK (cardinality(embedding) = 3),
    payload text NOT NULL,
    payload_sha256 text GENERATED ALWAYS AS (
        encode(sha256(payload::bytea), 'hex')
    ) STORED
);

CREATE UNIQUE INDEX resources_normalized_name_uk
ON pro_extensions_lab.resources (normalized_name);

CREATE INDEX resources_normalized_prefix_idx
ON pro_extensions_lab.resources (normalized_name text_pattern_ops);

CREATE INDEX resources_location_gist
ON pro_extensions_lab.resources
USING gist (location);

CREATE INDEX resources_search_gin
ON pro_extensions_lab.resources
USING gin (
    to_tsvector(
        'english'::regconfig,
        display_name || ' ' || summary
    )
);

INSERT INTO pro_extensions_lab.resources (
    display_name,
    summary,
    location,
    embedding,
    payload
)
VALUES
    (
        'PostgreSQL Guide',
        'Safe migration and operations reference',
        point(0, 0),
        ARRAY[0.10, 0.20, 0.30]::double precision[],
        'guide-v1'
    ),
    (
        'Spatial Notes',
        'Abstract grid coordinates for the built-in point type',
        point(3, 4),
        ARRAY[0.15, 0.18, 0.33]::double precision[],
        'spatial-v1'
    ),
    (
        'Vector Primer',
        'Small exact-distance example without an extension index',
        point(8, 2),
        ARRAY[0.90, 0.10, 0.05]::double precision[],
        'vector-v1'
    );

\echo 'Generated lower-case key: narrow citext-style fallback'
SELECT
    r.resource_id,
    r.display_name,
    r.normalized_name
FROM pro_extensions_lab.resources AS r
WHERE r.normalized_name LIKE 'post%'
ORDER BY r.normalized_name, r.resource_id;

DO $expected_failure$
BEGIN
    BEGIN
        INSERT INTO pro_extensions_lab.resources (
            display_name, summary, location, embedding, payload
        )
        VALUES (
            'postgresql guide',
            'Case-only duplicate',
            point(1, 1),
            ARRAY[0.0, 0.0, 0.0]::double precision[],
            'duplicate'
        );
        RAISE EXCEPTION 'case-insensitive duplicate unexpectedly succeeded';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Expected normalized-name rejection: %', SQLERRM;
    END;
END
$expected_failure$;

\echo 'Built-in point/GiST fallback: planar grid distance, not geodesy'
SELECT
    r.resource_id,
    r.display_name,
    r.location,
    r.location <-> point(1, 1) AS planar_distance
FROM pro_extensions_lab.resources AS r
ORDER BY r.location <-> point(1, 1), r.resource_id
LIMIT 3;

CREATE FUNCTION pro_extensions_lab.array_l2_distance(
    p_left double precision[],
    p_right double precision[]
)
RETURNS double precision
LANGUAGE sql
IMMUTABLE
STRICT
PARALLEL SAFE
SET search_path = pg_catalog
AS $function$
    SELECT sqrt(sum(power(l.value - r.value, 2)))
    FROM unnest(p_left) WITH ORDINALITY AS l(value, position)
    JOIN unnest(p_right) WITH ORDINALITY AS r(value, position)
      USING (position)
    HAVING COUNT(*) = cardinality(p_left)
       AND cardinality(p_left) = cardinality(p_right)
$function$;

\echo 'Built-in array fallback: exact scan for a tiny three-dimensional fixture'
SELECT
    r.resource_id,
    r.display_name,
    pro_extensions_lab.array_l2_distance(
        r.embedding,
        ARRAY[0.12, 0.19, 0.31]::double precision[]
    ) AS l2_distance
FROM pro_extensions_lab.resources AS r
ORDER BY l2_distance, r.resource_id;

\echo 'Built-in SHA-256 detects payload drift; it is not encryption'
SELECT
    r.resource_id,
    r.display_name,
    r.payload_sha256
FROM pro_extensions_lab.resources AS r
ORDER BY r.resource_id;

-- Local snapshot fallback for an FDW boundary. One row is one version fetched
-- from a named remote source; no server, user mapping, or credentials exist.
CREATE TABLE pro_extensions_lab.remote_snapshot (
    snapshot_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_system text NOT NULL,
    source_key text NOT NULL,
    fetched_at timestamptz NOT NULL,
    payload jsonb NOT NULL CHECK (jsonb_typeof(payload) = 'object'),
    UNIQUE (source_system, source_key, fetched_at)
);

INSERT INTO pro_extensions_lab.remote_snapshot (
    source_system, source_key, fetched_at, payload
)
VALUES
    ('catalog-demo', 'R-100', TIMESTAMPTZ '2026-04-01 10:00:00+00', '{"status":"old"}'),
    ('catalog-demo', 'R-100', TIMESTAMPTZ '2026-04-01 11:00:00+00', '{"status":"current"}'),
    ('catalog-demo', 'R-101', TIMESTAMPTZ '2026-04-01 10:30:00+00', '{"status":"current"}');

SELECT DISTINCT ON (rs.source_system, rs.source_key)
    rs.source_system,
    rs.source_key,
    rs.fetched_at,
    rs.payload
FROM pro_extensions_lab.remote_snapshot AS rs
ORDER BY
    rs.source_system,
    rs.source_key,
    rs.fetched_at DESC,
    rs.snapshot_id DESC;

-- Exercises:
--
-- 1. Classify each requested extension as unavailable, available-but-not-
--    installed, or installed. Record exact versions; do not infer CREATE
--    privilege from availability.
-- 2. Explain where generated lower(display_name) differs from citext, including
--    Unicode/collation, operators, joins, and every writer's contract.
-- 3. Compare built-in point distance with PostGIS geometry/geography and SRIDs.
--    State why latitude/longitude must not be treated as an abstract point grid.
-- 4. Extend array_l2_distance with explicit dimension validation and compare an
--    exact scan with pgvector HNSW/IVFFlat recall, build, memory, and write cost.
-- 5. Compare built-in SHA-256, pgcrypto digest/crypt/PGP functions, and external
--    key management. Never use a fast digest alone for password storage.
-- 6. Design an approved postgres_fdw boundary: server ownership, user mapping
--    secrets, imported-column contract, pushdown, transaction consistency,
--    failure isolation, and local snapshot fallback.
-- 7. Explain pg_trgm similarity versus prefix LIKE and full-text search. Name
--    the exact operators an optional trigram index must serve.

DO $self_check$
BEGIN
    IF (SELECT COUNT(*) FROM pro_extensions_lab.resources) <> 3 THEN
        RAISE EXCEPTION 'unexpected resource count';
    END IF;
    IF pro_extensions_lab.array_l2_distance(
        ARRAY[0, 0, 0]::double precision[],
        ARRAY[3, 4, 0]::double precision[]
    ) <> 5 THEN
        RAISE EXCEPTION 'array distance check failed';
    END IF;
END
$self_check$;

ROLLBACK;
\echo 'SQL-EXT-01 complete: no extension was created and schema was rolled back'
