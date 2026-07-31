-- SQL-EXT-01 executable solutions: built-ins only, no CREATE EXTENSION.
-- SOLUTION READING MAP — sql-ext-01: PostgreSQL Extensions, Spatial Data, and Vectors
-- Explanation: sql/professional/solutions/sql_ext_01_extensions_spatial_vector_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_ext_01_extensions_spatial_vector_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_extensions_lab;

-- Exercise 2: a stored lower-case key is a narrow built-in case-folding
-- contract; the Markdown solution explains its collation/citext limits.
CREATE TABLE pro_extensions_lab.items (
    item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_name text NOT NULL,
    normalized_name text GENERATED ALWAYS AS (lower(item_name)) STORED,
    location point NOT NULL,
    embedding double precision[] NOT NULL CHECK (cardinality(embedding) = 3),
    payload text NOT NULL,
    payload_sha256 text GENERATED ALWAYS AS (
        encode(sha256(payload::bytea), 'hex')
    ) STORED
);

CREATE UNIQUE INDEX items_normalized_name_uk
ON pro_extensions_lab.items (normalized_name);

INSERT INTO pro_extensions_lab.items (
    item_name, location, embedding, payload
)
VALUES
    ('Alpha', point(0, 0), ARRAY[0, 0, 0]::double precision[], 'alpha-v1'),
    ('Bravo', point(3, 4), ARRAY[3, 4, 0]::double precision[], 'bravo-v1');

CREATE FUNCTION pro_extensions_lab.checked_l2(
    p_left double precision[],
    p_right double precision[]
)
RETURNS double precision
LANGUAGE plpgsql
IMMUTABLE
STRICT
PARALLEL SAFE
SET search_path = pg_catalog
AS $function$
DECLARE
    result double precision;
BEGIN
    IF cardinality(p_left) <> cardinality(p_right) THEN
        RAISE EXCEPTION 'vector dimensions differ: % versus %',
            cardinality(p_left), cardinality(p_right)
            USING ERRCODE = 'check_violation';
    END IF;

    SELECT sqrt(sum(power(l.value - r.value, 2)))
    INTO result
    FROM unnest(p_left) WITH ORDINALITY AS l(value, position)
    JOIN unnest(p_right) WITH ORDINALITY AS r(value, position)
      USING (position);
    RETURN result;
END
$function$;

-- Exercise 3: point distance is planar grid distance, not geodesy.
-- Exercise 4: checked_l2 validates dimensions and performs an exact tiny scan.
SELECT
    i.item_name,
    i.location <-> point(1, 1) AS planar_distance,
    pro_extensions_lab.checked_l2(
        i.embedding,
        ARRAY[0, 0, 0]::double precision[]
    ) AS vector_distance,
    i.payload_sha256
FROM pro_extensions_lab.items AS i
ORDER BY vector_distance, i.item_id;

-- Exercise 5: payload_sha256 is an integrity digest, not encryption or a
-- password-storage construction.
DO $solution$
BEGIN
    BEGIN
        PERFORM pro_extensions_lab.checked_l2(
            ARRAY[1, 2]::double precision[],
            ARRAY[1, 2, 3]::double precision[]
        );
        RAISE EXCEPTION 'dimension mismatch unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected vector-dimension rejection: %', SQLERRM;
    END;
END
$solution$;

-- Exercise 6: a timestamped local snapshot is the safe executable stand-in for
-- an approved FDW design; no remote connection or credential is created.
CREATE TABLE pro_extensions_lab.remote_snapshot (
    snapshot_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_key text NOT NULL,
    fetched_at timestamptz NOT NULL,
    payload jsonb NOT NULL
);

INSERT INTO pro_extensions_lab.remote_snapshot (
    source_key, fetched_at, payload
)
VALUES
    ('K-1', TIMESTAMPTZ '2026-05-01 10:00+00', '{"version":1}'),
    ('K-1', TIMESTAMPTZ '2026-05-01 11:00+00', '{"version":2}');

SELECT DISTINCT ON (rs.source_key)
    rs.source_key,
    rs.fetched_at,
    rs.payload
FROM pro_extensions_lab.remote_snapshot AS rs
ORDER BY rs.source_key, rs.fetched_at DESC, rs.snapshot_id DESC;

DO $solution$
BEGIN
    IF pro_extensions_lab.checked_l2(
        ARRAY[0, 0, 0]::double precision[],
        ARRAY[3, 4, 0]::double precision[]
    ) <> 5 THEN
        RAISE EXCEPTION 'checked vector distance failed';
    END IF;
    IF (SELECT COUNT(*) FROM pg_catalog.pg_extension WHERE extname IN (
        'pg_trgm', 'citext', 'pgcrypto', 'postgis', 'vector', 'postgres_fdw'
    )) <> 0 THEN
        RAISE NOTICE
            'Optional extensions pre-existed; this solution did not change them';
    END IF;
END
$solution$;

-- Exercise 7: trigram, prefix, and full-text search differ by operator and
-- operator class. No optional search extension is enabled by this solution.

-- Exercise 1 and Exercise 8: inventory requested extension capability/lifecycle
-- state without CREATE/ALTER/DROP.
WITH requested(extension_name) AS (
    VALUES
        ('citext'::name),
        ('pg_trgm'::name),
        ('pgcrypto'::name),
        ('postgis'::name),
        ('postgres_fdw'::name),
        ('vector'::name)
)
SELECT
    r.extension_name,
    a.default_version,
    a.installed_version,
    pg_catalog.pg_get_userbyid(e.extowner) AS installed_owner
FROM requested AS r
LEFT JOIN pg_catalog.pg_available_extensions AS a
  ON a.name = r.extension_name
LEFT JOIN pg_catalog.pg_extension AS e
  ON e.extname = r.extension_name
ORDER BY r.extension_name;

-- Exercise 9: mismatch detection comes before impact analysis/reindex. Metadata
-- must be refreshed only after affected objects have been remediated.
SELECT
    c.collname,
    c.collprovider,
    c.collversion AS recorded_version,
    pg_catalog.pg_collation_actual_version(c.oid) AS actual_version
FROM pg_catalog.pg_collation AS c
WHERE c.collversion IS NOT NULL
  AND c.collversion IS DISTINCT FROM
      pg_catalog.pg_collation_actual_version(c.oid)
ORDER BY c.collname;

-- Exercise 10: approved PostGIS uses ST_DWithin for indexed radius prefiltering,
-- then exact ST_Distance and a stable ID. SRID, units, coordinate validation,
-- antimeridian, and poles are part of the query contract.

-- Exercise 11: compare exact metric results before evaluating ANN recall. This
-- built-in fallback remains exact and validates vector dimensions.
SELECT
    i.item_id,
    i.item_name,
    pro_extensions_lab.checked_l2(
        i.embedding,
        ARRAY[1, 1, 1]::double precision[]
    ) AS exact_l2
FROM pro_extensions_lab.items AS i
ORDER BY exact_l2, i.item_id;

-- Exercise 12: FDW operations require external secret rotation, connection and
-- statement bounds, schema drift checks, pushdown evidence, observability,
-- partial-failure policy, and a reconciled last-known-good snapshot.
SELECT
    rs.source_key,
    max(rs.fetched_at) AS snapshot_watermark,
    COUNT(*) AS retained_versions
FROM pro_extensions_lab.remote_snapshot AS rs
GROUP BY rs.source_key
ORDER BY rs.source_key;

-- Exercise 13: unavailable package review must cover provenance, native-code
-- authority, dependencies/SBOM, CVEs, licensing, reproducible build, patch
-- owner/SLA, restore, and removal. Successful compilation is not approval.

-- Exercise 14: an upgrade rehearsal restores a disposable database, captures
-- dependencies/plans/results before and after, runs application/performance
-- canaries, and records backup compatibility plus nonreversible rollback limits.

ROLLBACK;
