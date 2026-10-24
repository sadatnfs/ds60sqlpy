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
    embedding double precision[] NOT NULL CHECK (
        cardinality(embedding) = 3
        AND array_position(embedding, NULL) IS NULL
        AND array_position(embedding, 'NaN'::double precision) IS NULL
        AND array_position(embedding, 'Infinity'::double precision) IS NULL
        AND array_position(embedding, '-Infinity'::double precision) IS NULL
    ),
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

SELECT
    c.column_name,
    c.is_generated,
    c.generation_expression,
    i.indexdef
FROM information_schema.columns AS c
JOIN pg_catalog.pg_indexes AS i
  ON i.schemaname = c.table_schema
 AND i.tablename = c.table_name
 AND i.indexname = 'items_normalized_name_uk'
WHERE c.table_schema = 'pro_extensions_lab'
  AND c.table_name = 'items'
  AND c.column_name = 'normalized_name';

CREATE TABLE pro_extensions_lab.normalization_checks (
    case_id text PRIMARY KEY,
    candidate_name text NOT NULL,
    normalized_name text NOT NULL,
    expected_outcome text NOT NULL,
    observed_sqlstate text
);

DO $solution$
DECLARE
    actual_sqlstate text;
BEGIN
    INSERT INTO pro_extensions_lab.items (
        item_name, location, embedding, payload
    )
    VALUES (
        'Charlie',
        point(1, 1),
        ARRAY[1, 1, 1]::double precision[],
        'charlie-v1'
    );

    INSERT INTO pro_extensions_lab.normalization_checks
    VALUES ('distinct', 'Charlie', lower('Charlie'), 'accepted', NULL);

    BEGIN
        INSERT INTO pro_extensions_lab.items (
            item_name, location, embedding, payload
        )
        VALUES (
            'alpha',
            point(2, 2),
            ARRAY[2, 2, 2]::double precision[],
            'alpha-v2'
        );
        RAISE EXCEPTION 'case-fold collision unexpectedly succeeded';
    EXCEPTION
        WHEN unique_violation THEN
            GET STACKED DIAGNOSTICS actual_sqlstate = RETURNED_SQLSTATE;
    END;

    INSERT INTO pro_extensions_lab.normalization_checks
    VALUES ('case-fold-collision', 'alpha', lower('alpha'), 'rejected', actual_sqlstate);
END
$solution$;

SELECT *
FROM pro_extensions_lab.normalization_checks
ORDER BY case_id;

CREATE FUNCTION pro_extensions_lab.checked_l2(
    p_left double precision[],
    p_right double precision[]
)
RETURNS double precision
LANGUAGE plpgsql
IMMUTABLE
PARALLEL SAFE
SET search_path = pg_catalog
AS $function$
DECLARE
    result double precision;
BEGIN
    IF p_left IS NULL OR p_right IS NULL THEN
        RAISE EXCEPTION 'vectors must be non-NULL'
            USING ERRCODE = 'check_violation';
    END IF;

    IF cardinality(p_left) = 0
       OR cardinality(p_left) <> cardinality(p_right) THEN
        RAISE EXCEPTION 'vector dimensions must be equal and positive: % versus %',
            cardinality(p_left), cardinality(p_right)
            USING ERRCODE = 'check_violation';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM unnest(p_left || p_right) AS element(value)
        WHERE element.value IS NULL
           OR element.value = 'NaN'::double precision
           OR element.value = 'Infinity'::double precision
           OR element.value = '-Infinity'::double precision
    ) THEN
        RAISE EXCEPTION 'vector elements must be finite and non-NULL'
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
    i.item_id,
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
SELECT
    i.item_id,
    i.item_name,
    i.payload_sha256
FROM pro_extensions_lab.items AS i
ORDER BY i.item_id;

SELECT *
FROM (
    VALUES
        ('SHA-256 / digest'::text, 'integrity fingerprint', 'not encryption and not password storage'),
        ('crypt with adaptive password hash', 'password verification', 'requires approved pgcrypto capability and work factor'),
        ('PGP encryption', 'protect database-held ciphertext', 'key custody and threat model remain external decisions'),
        ('external KMS/envelope encryption', 'separate key custody and rotation', 'application/service integration required')
) AS crypto_purposes(mechanism, appropriate_purpose, important_limit)
ORDER BY mechanism;

-- Exercise 4 negative controls: every invalid shape/value must fail before
-- aggregation can silently ignore it or return NULL.
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

    BEGIN
        PERFORM pro_extensions_lab.checked_l2(
            ARRAY[]::double precision[],
            ARRAY[]::double precision[]
        );
        RAISE EXCEPTION 'empty vectors unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected empty-vector rejection: %', SQLERRM;
    END;

    BEGIN
        PERFORM pro_extensions_lab.checked_l2(
            ARRAY[1, NULL, 3]::double precision[],
            ARRAY[1, 2, 3]::double precision[]
        );
        RAISE EXCEPTION 'NULL vector element unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected NULL-element rejection: %', SQLERRM;
    END;

    BEGIN
        PERFORM pro_extensions_lab.checked_l2(
            ARRAY[1, 'Infinity'::double precision, 3],
            ARRAY[1, 2, 3]::double precision[]
        );
        RAISE EXCEPTION 'infinite vector element unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected infinite-element rejection: %', SQLERRM;
    END;

    BEGIN
        PERFORM pro_extensions_lab.checked_l2(
            ARRAY[1, 'NaN'::double precision, 3],
            ARRAY[1, 2, 3]::double precision[]
        );
        RAISE EXCEPTION 'NaN vector element unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected NaN-element rejection: %', SQLERRM;
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
    rs.snapshot_id,
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
SELECT *
FROM (
    VALUES
        ('prefix LIKE'::text, 'column LIKE ''term%'''::text, 'B-tree pattern operator class when collation/operator support it'::text, 'ordered prefix', 'does not correct misspellings'),
        ('trigram similarity', '%, similarity(), word_similarity()', 'GIN/GiST gin_trgm_ops or gist_trgm_ops', 'fuzzy character overlap', 'optional pg_trgm; threshold changes semantics'),
        ('full-text search', '@@ over tsvector/tsquery', 'GIN/GiST text-search operator class', 'token/lexeme linguistic match', 'not arbitrary substring similarity')
) AS search_contract(
    search_method,
    query_operator,
    index_strategy,
    ranking_semantics,
    limitation
)
ORDER BY search_method;

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
    pg_catalog.pg_get_userbyid(e.extowner) AS installed_owner,
    CASE
        WHEN a.name IS NULL THEN 'unavailable'
        WHEN e.oid IS NULL THEN 'available_not_installed'
        ELSE 'installed'
    END AS capability_state
FROM requested AS r
LEFT JOIN pg_catalog.pg_available_extensions AS a
  ON a.name = r.extension_name
LEFT JOIN pg_catalog.pg_extension AS e
  ON e.extname = r.extension_name
ORDER BY r.extension_name;

-- Exercise 8 adds lifecycle facts without changing extension state.
WITH requested(extension_name) AS (
    VALUES
        ('citext'::name),
        ('pg_trgm'::name),
        ('pgcrypto'::name),
        ('postgis'::name),
        ('postgres_fdw'::name),
        ('vector'::name)
),
available_versions AS (
    SELECT
        v.name,
        array_agg(v.version ORDER BY v.version) AS available_versions,
        bool_or(v.trusted) AS any_trusted_version,
        array_agg(DISTINCT dependency ORDER BY dependency)
            FILTER (WHERE dependency IS NOT NULL) AS declared_dependencies
    FROM pg_catalog.pg_available_extension_versions AS v
    LEFT JOIN LATERAL unnest(v.requires) AS dependency
      ON true
    GROUP BY v.name
)
SELECT
    r.extension_name,
    a.default_version,
    a.installed_version,
    ns.nspname AS installed_schema,
    pg_catalog.pg_get_userbyid(e.extowner) AS installed_owner,
    versions.available_versions,
    versions.any_trusted_version,
    versions.declared_dependencies
FROM requested AS r
LEFT JOIN pg_catalog.pg_available_extensions AS a
  ON a.name = r.extension_name
LEFT JOIN pg_catalog.pg_extension AS e
  ON e.extname = r.extension_name
LEFT JOIN pg_catalog.pg_namespace AS ns
  ON ns.oid = e.extnamespace
LEFT JOIN available_versions AS versions
  ON versions.name = r.extension_name
ORDER BY r.extension_name;

-- Exercise 9: mismatch detection comes before impact analysis/reindex. Metadata
-- must be refreshed only after affected objects have been remediated.
SELECT
    n.nspname AS collation_schema,
    c.collname AS collation_name,
    c.collencoding AS encoding,
    c.collprovider,
    c.collversion AS recorded_version,
    pg_catalog.pg_collation_actual_version(c.oid) AS actual_version
FROM pg_catalog.pg_collation AS c
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = c.collnamespace
WHERE c.collversion IS NOT NULL
  AND c.collversion IS DISTINCT FROM
      pg_catalog.pg_collation_actual_version(c.oid)
ORDER BY collation_schema, collation_name, encoding;

-- Exercise 10: approved PostGIS uses ST_DWithin for indexed radius prefiltering,
-- then exact ST_Distance and a stable ID. SRID, units, coordinate validation,
-- antimeridian, and poles are part of the query contract.
SELECT *
FROM (
    VALUES
        (1, 'capability', 'PostGIS installed version and approval are recorded'),
        (2, 'inputs', 'validated longitude/latitude converted to geography SRID 4326'),
        (3, 'prefilter', 'ST_DWithin(resource_geography, query_geography, radius_meters)'),
        (4, 'distance', 'ST_Distance returns meters for geography'),
        (5, 'order', 'distance_meters, resource_id gives deterministic ties'),
        (6, 'edge cases', 'antimeridian, poles, equal distance, invalid coordinates'),
        (7, 'evidence', 'exact control result plus EXPLAIN (ANALYZE, BUFFERS)')
) AS postgis_review(check_number, check_name, required_evidence)
ORDER BY check_number;

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
SELECT *
FROM (
    VALUES
        (1, 'source and release provenance', 'blocked until signed source/release hash is verified'),
        (2, 'native dependency SBOM and CVEs', 'blocked until scanned and risk-owned'),
        (3, 'license', 'blocked until distribution/use is approved'),
        (4, 'reproducible build', 'blocked until build inputs and output hash are recorded'),
        (5, 'patch ownership and SLA', 'blocked until an accountable maintainer exists'),
        (6, 'restore/removal rehearsal', 'blocked until backup restore and clean removal pass')
) AS supply_chain_review(review_number, review_item, blocking_rule)
ORDER BY review_number;

-- Exercise 14: an upgrade rehearsal restores a disposable database, captures
-- dependencies/plans/results before and after, runs application/performance
-- canaries, and records backup compatibility plus nonreversible rollback limits.
SELECT *
FROM (
    VALUES
        (1, 'restore baseline', 'version, package, dependency and backup evidence'),
        (2, 'capture before', 'objects, plans, results, timings and application canaries'),
        (3, 'upgrade', 'exact reviewed command, locks, WAL, elapsed time and logs'),
        (4, 'capture after', 'same correctness/performance evidence and tolerances'),
        (5, 'rollback decision', 'downgrade support or restore/forward-fix limit'),
        (6, 'cleanup', 'disposable target disposition and follow-up owners')
) AS upgrade_rehearsal(phase_number, phase_name, required_evidence)
ORDER BY phase_number;

ROLLBACK;
