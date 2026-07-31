-- SQL-EXT-01: Extensions, spatial data, and vectors
-- BEGINNER WORKFLOW — sql-ext-01: PostgreSQL Extensions, Spatial Data, and Vectors
-- Guide: sql/professional/companion-guides/sql_ext_01_extensions_spatial_vector.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-ext-01/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pg_catalog.pg_available_extensions, pro_extensions_lab.resources, pro_extensions_lab.remote_snapshot.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
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
--    Inputs: For sql-ext-01 Exercise 1, complete the capability matrix written analysis and support its claims with read-only evidence from `pg_available_extensions`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-ext-01 Exercise 1, expected output: a completed the capability matrix written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `installed_version`.
--    Verify: For sql-ext-01 Exercise 1, check the capability matrix written analysis against `installed_version`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 1, check the capability matrix written analysis against `installed_version`.
-- 2. Explain where generated lower(display_name) differs from citext, including
--    Unicode/collation, operators, joins, and every writer's contract.
--    Inputs: For sql-ext-01 Exercise 2, read from `pro_extensions_lab.items`, `items_normalized_name_uk`, and `pro_extensions_lab.checked_l2`. Build the answer toward `result`; keep `result` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ext-01 Exercise 2, expected output: one row per `result`. The final columns are `result`.
--    Verify: For sql-ext-01 Exercise 2, project `result` plus the raw source columns from `pro_extensions_lab.items`, `items_normalized_name_uk`, and `pro_extensions_lab.checked_l2` at each join stage; record row count and distinct `result`, then assert the final `result` values match those staged rows without unintended fanout or loss. Add one source row with a new `result`; verify the result gains exactly one row carrying that `result` value.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 2, start with the first relation in `pro_extensions_lab.items`, `items_normalized_name_uk`, and `pro_extensions_lab.checked_l2`; after each join, record total rows and distinct `result` so the exact fanout or loss is visible.
-- 3. Compare built-in point distance with PostGIS geometry/geography and SRIDs.
--    State why latitude/longitude must not be treated as an abstract point grid.
--    Inputs: For sql-ext-01 Exercise 3, read from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Build the answer toward `point`; keep `point` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ext-01 Exercise 3, expected output: one row per `point`. The final columns are `point`.
--    Verify: For sql-ext-01 Exercise 3, reselect the returned keys directly from the source; require unique `point` where the expected grain is one row per key and confirm the projected `point` against `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Add one source row with a new `point`; verify the result gains exactly one row carrying that `point` value.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 3, select `point` from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` before adding derived columns.
-- 4. Extend array_l2_distance with explicit dimension validation and compare an
--    exact scan with pgvector HNSW/IVFFlat recall, build, memory, and write cost.
--    Inputs: For sql-ext-01 Exercise 4, read from `pro_extensions_lab.items`. Build the answer toward `item_name`, `planar_distance`, `vector_distance`, and `payload_sha256`; keep `planar_distance` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ext-01 Exercise 4, expected output: one row per `planar_distance`. The final columns are `item_name`, `planar_distance`, `vector_distance`, and `payload_sha256`. The final order is `vector_distance, i.item_id`.
--    Verify: For sql-ext-01 Exercise 4, reselect the returned keys directly from the source; require unique `planar_distance` where the expected grain is one row per key and confirm the projected `item_name`, `planar_distance`, `vector_distance`, and `payload_sha256` against `pro_extensions_lab.items`. Add one source row with a new `planar_distance`; verify the result gains exactly one row carrying that `planar_distance` value.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 4, check `vector_distance, i.item_id` before applying the row cap.
-- 5. Compare built-in SHA-256, pgcrypto digest/crypt/PGP functions, and external
--    key management. Never use a fast digest alone for password storage.
--    Inputs: For sql-ext-01 Exercise 5, use `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-ext-01 Exercise 5, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `crypt`.
--    Verify: For sql-ext-01 Exercise 5, restore into an isolated target and reconcile `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 5, restore into an isolated target and reconcile `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
-- 6. Design an approved postgres_fdw boundary: server ownership, user mapping
--    secrets, imported-column contract, pushdown, transaction consistency,
--    failure isolation, and local snapshot fallback.
--    Inputs: For sql-ext-01 Exercise 6, read from `pro_extensions_lab.remote_snapshot`, and `pg_catalog.pg_extension`. Build the answer toward `source_key`, `fetched_at`, and `payload`; keep `source_key` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ext-01 Exercise 6, expected output: one row per `source_key`. The final columns are `source_key`, `fetched_at`, and `payload`. The final order is `rs.source_key, rs.fetched_at DESC, rs.snapshot_id DESC`.
--    Verify: For sql-ext-01 Exercise 6, reselect the returned keys directly from the source; require unique `source_key` where the expected grain is one row per key and confirm the projected `source_key`, `fetched_at`, and `payload` against `pro_extensions_lab.remote_snapshot`, and `pg_catalog.pg_extension`. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 6, inspect the source keys that survive `WHERE`; then check `rs.source_key, rs.fetched_at DESC, rs.snapshot_id DESC` before applying the row cap.
-- 7. Explain pg_trgm similarity versus prefix LIKE and full-text search. Name
--    the exact operators an optional trigram index must serve.
--    Inputs: For sql-ext-01 Exercise 7, read from `requested`, `pg_catalog.pg_available_extensions`, and `pg_catalog.pg_extension`. Build the answer toward `extension_name`, `default_version`, `installed_version`, and `installed_owner`; keep `extension_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ext-01 Exercise 7, expected output: one row per `extension_name`. The final columns are `extension_name`, `default_version`, `installed_version`, and `installed_owner`. The final order is `r.extension_name`.
--    Verify: For sql-ext-01 Exercise 7, project `extension_name` plus the raw source columns from `requested`, `pg_catalog.pg_available_extensions`, and `pg_catalog.pg_extension` at each join stage; record row count and distinct `extension_name`, then assert the final `extension_name`, `default_version`, `installed_version`, and `installed_owner` values match those staged rows without unintended fanout or loss. Add one source row with a new `extension_name`; verify the result gains exactly one row carrying that `extension_name` value.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 7, start with the first relation in `requested`, `pg_catalog.pg_available_extensions`, and `pg_catalog.pg_extension`; after each join, record total rows and distinct `extension_name` so the exact fanout or loss is visible.
-- 8. Build an extension lifecycle inventory: owner, installed/default/available
--    versions, dependencies, trusted flag, update path, publisher, approval,
--    backup/restore needs, and rollback test. Do not upgrade anything here.
--    Inputs: For sql-ext-01 Exercise 8, use `pg_extension` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-ext-01 Exercise 8, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
--    Verify: For sql-ext-01 Exercise 8, restore into an isolated target and reconcile `pg_extension` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 8, restore into an isolated target and reconcile `pg_extension` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
-- 9. Detect collation provider/version drift and explain why affected indexes
--    may require REINDEX after operating-system or ICU changes. Separate
--    detection, impact analysis, remediation, and validation.
--    Inputs: For sql-ext-01 Exercise 9, read from `pg_catalog.pg_collation`. Build the answer toward `collname`, `collprovider`, `recorded_version`, and `actual_version`; keep `collname` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ext-01 Exercise 9, expected output: one row per `collname`. The final columns are `collname`, `collprovider`, `recorded_version`, and `actual_version`. The final order is `c.collname`.
--    Verify: For sql-ext-01 Exercise 9, run an anti-check that counts rows where NOT ((c.collversion IS NOT NULL AND c.collversion IS DISTINCT FROM pg_catalog.pg_collation_actual_version(c.oid))); require unique `collname` where the expected grain is one row per key and confirm the projected `collname`, `collprovider`, `recorded_version`, and `actual_version` against `pg_catalog.pg_collation`. Add one row for which `(c.collversion IS NOT NULL AND c.collversion IS DISTINCT FROM pg_catalog.pg_collation_actual_version(c.oid))` is true and one for which it is false; verify only the matching `collname` value is returned.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 9, inspect the source keys that survive `WHERE`; then check `c.collname` before applying the row cap.
-- 10. If PostGIS is approved elsewhere, design a nearest-resource query using
--     geography and a GiST index. Address SRID, units, antimeridian/poles,
--     ST_DWithin prefiltering, exact distance, and deterministic ties.
--    Inputs: For sql-ext-01 Exercise 10, complete the postgis nearest written analysis and support its claims with read-only evidence from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-ext-01 Exercise 10, expected output: a completed the postgis nearest written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `st_dwithin`, and `st_distance`.
--    Verify: For sql-ext-01 Exercise 10, check the postgis nearest written analysis against `st_dwithin`, and `st_distance`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 10, check the postgis nearest written analysis against `st_dwithin`, and `st_distance`.
-- 11. If pgvector is approved elsewhere, compare cosine, inner-product, and L2
--     operators plus HNSW and IVFFlat. State normalization, recall benchmark,
--     build/update cost, filtering, dimension, and exact fallback requirements.
--    Inputs: For sql-ext-01 Exercise 11, read from `pro_extensions_lab.items`. Build the answer toward `item_id`, `item_name`, and `exact_l2`; keep `item_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ext-01 Exercise 11, expected output: one row per `item_id`. The final columns are `item_id`, `item_name`, and `exact_l2`. The final order is `exact_l2, i.item_id`.
--    Verify: For sql-ext-01 Exercise 11, reselect the returned keys directly from the source; require unique `item_id` where the expected grain is one row per key and confirm the projected `item_id`, `item_name`, and `exact_l2` against `pro_extensions_lab.items`. Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 11, check `exact_l2, i.item_id` before applying the row cap.
-- 12. Extend the FDW design for credential rotation, connection limits, remote
--     schema drift, timeouts, pushdown inspection, partial failure, observability,
--     and a last-known-good snapshot. Never put credentials in learner SQL.
--    Inputs: For sql-ext-01 Exercise 12, read from `pro_extensions_lab.remote_snapshot`. Build the answer toward `source_key`, `snapshot_watermark`, and `retained_versions`; keep `source_key` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ext-01 Exercise 12, expected output: one row per `source_key`. The final columns are `source_key`, `snapshot_watermark`, and `retained_versions`. The final order is `rs.source_key`.
--    Verify: For sql-ext-01 Exercise 12, independently aggregate `pro_extensions_lab.remote_snapshot` by `source_key`; require one output row for every distinct `source_key` tuple and compare `snapshot_watermark`, and `retained_versions` tuple by tuple. Tie two rows on `rs.source_key` and give them different `rs.source_key` values; verify `rs.source_key` chooses a stable first/last row.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 12, confirm the groups are `source_key`; then check `rs.source_key` before applying the row cap.
-- 13. Write a supply-chain review for an extension unavailable from the trusted
--     package source. Cover source/build provenance, native-code privilege,
--     CVEs, reproducibility, licensing, patch ownership, and removal testing.
--    Inputs: For sql-ext-01 Exercise 13, read from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Build the answer toward `supply_chain_answer`; keep `supply_chain_answer` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ext-01 Exercise 13, expected output: one row per `supply_chain_answer`. The final columns are `supply_chain_answer`.
--    Verify: For sql-ext-01 Exercise 13, reselect the returned keys directly from the source; require unique `supply_chain_answer` where the expected grain is one row per key and confirm the projected `supply_chain_answer` against `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources`. Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 13, select `supply_chain_answer` from `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` before adding derived columns.
-- 14. Plan an extension upgrade rehearsal in a restored disposable database.
--     Capture dependencies and plans before/after, application canaries,
--     performance/correctness checks, backup compatibility, and rollback limits.

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
--    Inputs: For sql-ext-01 Exercise 14, use `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-ext-01 Exercise 14, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
--    Verify: For sql-ext-01 Exercise 14, restore into an isolated target and reconcile `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-ext-01 Exercise 14, restore into an isolated target and reconcile `requested`, `pg_catalog.pg_available_extensions`, and `pro_extensions_lab.resources` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.

ROLLBACK;
\echo 'SQL-EXT-01 complete: no extension was created and schema was rolled back'
