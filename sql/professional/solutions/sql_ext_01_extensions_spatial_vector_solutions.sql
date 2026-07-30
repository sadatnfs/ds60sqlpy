-- SQL-EXT-01 executable solutions: built-ins only, no CREATE EXTENSION.
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_extensions_lab;

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

ROLLBACK;
