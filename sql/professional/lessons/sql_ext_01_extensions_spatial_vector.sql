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
--    Inputs: For sql-ext-01 Exercise 1, LEFT JOIN the requested extension-name fixture (citext, pg_trgm, pgcrypto, postgis, postgres_fdw, and vector) to `pg_available_extensions` and `pg_extension`. This is read-only discovery.
--    Expected result/shape: For sql-ext-01 Exercise 1, One row per requested `extension_name`, with `extension_name`, `default_version`, `installed_version`, `installed_owner`, and `capability_state`, ordered by `extension_name`. State is `unavailable`, `available_not_installed`, or `installed`.
--    Verify: For sql-ext-01 Exercise 1, Every requested name appears exactly once even when unavailable; compare installed versions directly with `pg_extension`. Record CREATE privilege/approval as unknown unless separately proven—availability does not grant permission. Hint ladder, rung 1: Start from the requested list and LEFT JOIN catalogs, otherwise unavailable names disappear.
-- 2. Explain where generated lower(display_name) differs from citext, including
--    Unicode/collation, operators, joins, and every writer's contract.
--    Inputs: For sql-ext-01 Exercise 2, Inspect generated column `pro_extensions_lab.items.normalized_name` and its unique-index catalog row; compare that narrow `lower(item_name)` rule with optional `citext`.
--    Expected result/shape: For sql-ext-01 Exercise 2, A catalog evidence row names the generated expression and unique index definition. A behavior table has `case_id`, `candidate_name`, `normalized_name`, `expected_outcome`, and `observed_sqlstate` for a distinct insert and a case-fold collision.
--    Verify: For sql-ext-01 Exercise 2, In a savepoint, `Charlie` succeeds and `alpha` conflicts with existing `Alpha` using SQLSTATE `23505`; rollback removes both attempts. Document Unicode/collation, operators/joins, and cross-writer limitations rather than claiming `lower()` is universally equivalent to `citext`. Hint ladder, rung 1: The generated column is a stored key; every lookup and join must use the same explicit normalization contract.
-- 3. Compare built-in point distance with PostGIS geometry/geography and SRIDs.
--    State why latitude/longitude must not be treated as an abstract point grid.
--    Inputs: For sql-ext-01 Exercise 3, Calculate `<->` from each `pro_extensions_lab.items.location` to the built-in point `(1,1)`, and write a comparison matrix for built-in `point`, PostGIS `geometry`, and PostGIS `geography`.
--    Expected result/shape: For sql-ext-01 Exercise 3, One row per `item_id`, with `item_id`, `item_name`, and `planar_distance`, ordered by `planar_distance, item_id`. The matrix names coordinate model, SRID support, distance units, index/operator, and appropriate use for each type.
--    Verify: For sql-ext-01 Exercise 3, Distances may tie, so `item_id`—not distance—is the identity and final tie-break. Prove the built-in result is Cartesian grid distance and explicitly reject interpreting latitude/longitude degrees as meters. Hint ladder, rung 1: A numeric distance has no geographic meaning until the coordinate reference system and units are defined.
-- 4. Extend array_l2_distance with explicit dimension validation and compare an
--    exact scan with pgvector HNSW/IVFFlat recall, build, memory, and write cost.
--    Inputs: For sql-ext-01 Exercise 4, Strengthen `pro_extensions_lab.checked_l2(left,right)` to reject NULL arrays, zero dimensions, unequal dimensions, NULL elements, and non-finite elements before calculating exact L2 distance.
--    Expected result/shape: For sql-ext-01 Exercise 4, One row per `item_id`, with `item_id`, `item_name`, and `vector_distance`, ordered by `vector_distance, item_id`. The supplied `[0,0,0]` to `[3,4,0]` control equals `5`.
--    Verify: For sql-ext-01 Exercise 4, Named negative controls reject dimension mismatch, empty arrays, NULL elements, `Infinity`, and `NaN` with SQLSTATE `23514`; equal distance ties remain separate item IDs. Compare exact scan results with any approved ANN index before reporting recall, memory, build, or write cost. Hint ladder, rung 1: `sum()` silently ignores NULL inputs, so validation must happen before unnesting and aggregation.
-- 5. Compare built-in SHA-256, pgcrypto digest/crypt/PGP functions, and external
--    key management. Never use a fast digest alone for password storage.
--    Inputs: For sql-ext-01 Exercise 5, Read `item_id`, `item_name`, and generated `payload_sha256` from `pro_extensions_lab.items`; separately classify SHA-256, optional `pgcrypto.digest`, `crypt`, PGP encryption, and external key management.
--    Expected result/shape: For sql-ext-01 Exercise 5, One row per `item_id` with the three evidence columns, ordered by `item_id`. A purpose matrix names integrity digest, password hashing, encryption, key custody, and capability/fallback.
--    Verify: For sql-ext-01 Exercise 5, Recompute SHA-256 from `payload` and compare all 64 hex characters; changing payload changes the digest. The matrix must explicitly forbid a fast unsalted digest for password storage and must not claim optional pgcrypto functions ran when unavailable. Hint ladder, rung 1: Hashing, password verification, encryption, and key management solve different threats.
-- 6. Design an approved postgres_fdw boundary: server ownership, user mapping
--    secrets, imported-column contract, pushdown, transaction consistency,
--    failure isolation, and local snapshot fallback.
--    Inputs: For sql-ext-01 Exercise 6, Use local `pro_extensions_lab.remote_snapshot`; no foreign server, user mapping, network connection, or credential is created. Choose the latest row per `source_key` by `fetched_at DESC, snapshot_id DESC`.
--    Expected result/shape: For sql-ext-01 Exercise 6, One row per `source_key`, with `source_key`, `snapshot_id`, `fetched_at`, and `payload`, ordered by `source_key`.
--    Verify: For sql-ext-01 Exercise 6, Add two same-time snapshots and prove greater `snapshot_id` wins. Separately review server ownership, secret location/rotation, imported columns, pushdown, transaction consistency, timeout, failure isolation, and snapshot fallback before any approved FDW deployment. Hint ladder, rung 1: Capability inventory and a local snapshot are safe evidence; neither proves a remote FDW connection is authorized or healthy.
-- 7. Explain pg_trgm similarity versus prefix LIKE and full-text search. Name
--    the exact operators an optional trigram index must serve.
--    Inputs: For sql-ext-01 Exercise 7, Build a reviewed matrix for prefix `LIKE 'term%'`, optional pg_trgm similarity/operators, and built-in full-text search. Name the query operator and matching index/operator class together.
--    Expected result/shape: For sql-ext-01 Exercise 7, One row per `search_method`, with `search_method`, `query_operator`, `index_strategy`, `ranking_semantics`, `strength`, and `limitation`.
--    Verify: For sql-ext-01 Exercise 7, Use one exact prefix, one misspelling, and one multi-token document to show the methods answer different questions. If `pg_trgm` is absent, record that capability as unavailable and run only built-in comparisons. Hint ladder, rung 1: An index helps only operators supported by its operator class; “fuzzy,” “prefix,” and “linguistic” are not synonyms.
-- 8. Build an extension lifecycle inventory: owner, installed/default/available
--    versions, dependencies, trusted flag, update path, publisher, approval,
--    backup/restore needs, and rollback test. Do not upgrade anything here.
--    Inputs: For sql-ext-01 Exercise 8, Extend Exercise 1's read-only requested-extension inventory with available versions/trusted flag, installed schema/owner, dependencies, update path, publisher/package provenance, approval, backup/restore needs, rollback test, and named owner.
--    Expected result/shape: For sql-ext-01 Exercise 8, One row per requested `extension_name`, with catalog facts kept separate from reviewed policy fields. No `CREATE EXTENSION`, `ALTER EXTENSION`, or `DROP EXTENSION` runs.
--    Verify: For sql-ext-01 Exercise 8, Every installed extension has an exact version, owner, schema, dependency inventory, package source, upgrade and restore rehearsal, and rollback limit. Unavailable extensions remain visible with an explicit fallback instead of disappearing. Hint ladder, rung 1: Catalog state is observed evidence; approval, provenance, rollback, and operational ownership are separate decisions.
-- 9. Detect collation provider/version drift and explain why affected indexes
--    may require REINDEX after operating-system or ICU changes. Separate
--    detection, impact analysis, remediation, and validation.
--    Inputs: For sql-ext-01 Exercise 9, Read `pg_collation` and compare non-NULL recorded `collversion` with `pg_collation_actual_version(oid)`. This query detects; it does not reindex or refresh metadata.
--    Expected result/shape: For sql-ext-01 Exercise 9, One row per mismatched `(collation_schema, collation_name, encoding)`, with those identity fields, `collprovider`, `recorded_version`, and `actual_version`, ordered by all three identity fields.
--    Verify: For sql-ext-01 Exercise 9, An empty result means no mismatch was detected, not that every dependent index was inspected. For each returned collation, inventory dependent indexes, rehearse `REINDEX`, validate ordering/uniqueness, and only then refresh version metadata under an approved runbook. Hint ladder, rung 1: `collname` alone is not globally unique; preserve its namespace and encoding.
-- 10. If PostGIS is approved elsewhere, design a nearest-resource query using
--     geography and a GiST index. Address SRID, units, antimeridian/poles,
--     ST_DWithin prefiltering, exact distance, and deterministic ties.
--    Inputs: For sql-ext-01 Exercise 10, Write but do not execute a PostGIS query unless capability and approval are confirmed. Use `geography` with a declared SRID, a GiST indexable `ST_DWithin` radius prefilter, exact `ST_Distance`, and stable `resource_id` tie-break.
--    Expected result/shape: For sql-ext-01 Exercise 10, A reviewed query contract names parameters, coordinate validation, meters as units, output grain/columns/order, antimeridian/pole cases, maximum radius, timeout, fallback, and owner.
--    Verify: For sql-ext-01 Exercise 10, In an approved isolated PostGIS environment, compare the indexed query with a small exact control set, inspect `EXPLAIN (ANALYZE, BUFFERS)`, and test equal distances plus antimeridian/pole fixtures. Otherwise report `not executed: capability unavailable`. Hint ladder, rung 1: Prefilter for indexable radius, then calculate exact distance and order by distance plus stable identity.
-- 11. If pgvector is approved elsewhere, compare cosine, inner-product, and L2
--     operators plus HNSW and IVFFlat. State normalization, recall benchmark,
--     build/update cost, filtering, dimension, and exact fallback requirements.
--    Inputs: For sql-ext-01 Exercise 11, Use validated arrays and `checked_l2` as the built-in exact fallback; separately define optional pgvector cosine, inner-product, and L2 semantics plus HNSW/IVFFlat evaluation.
--    Expected result/shape: For sql-ext-01 Exercise 11, One row per `item_id`, with `item_id`, `item_name`, and `exact_l2`, ordered by `exact_l2, item_id`.
--    Verify: For sql-ext-01 Exercise 11, Compare every ANN candidate set with this exact ordering and report recall at the chosen `k`, filtered recall, latency, build memory/time, update cost, and index size. State normalization assumptions and use `item_id` to keep equal distances deterministic. Hint ladder, rung 1: A fast plan is not sufficient; ANN adoption needs a correctness benchmark against the exact metric.
-- 12. Extend the FDW design for credential rotation, connection limits, remote
--     schema drift, timeouts, pushdown inspection, partial failure, observability,
--     and a last-known-good snapshot. Never put credentials in learner SQL.
--    Inputs: For sql-ext-01 Exercise 12, Aggregate local `pro_extensions_lab.remote_snapshot` by `source_key`; accompany it with an FDW operations contract for secrets, connections, schema drift, timeouts, pushdown, partial failure, and fallback.
--    Expected result/shape: For sql-ext-01 Exercise 12, One row per `source_key`, with `source_key`, `snapshot_watermark`, and `retained_versions`, ordered by `source_key`.
--    Verify: For sql-ext-01 Exercise 12, Independently compare `max(fetched_at)` and counts per key; add a same-time version and confirm the latest-row query uses `snapshot_id` for its tie, while this aggregate correctly increments `retained_versions`. Simulate remote unavailability by using only the timestamped local fallback. Hint ladder, rung 1: A watermark says when the snapshot was fetched, not that the remote source is current or complete.
-- 13. Write a supply-chain review for an extension unavailable from the trusted
--     package source. Cover source/build provenance, native-code privilege,
--     CVEs, reproducibility, licensing, patch ownership, and removal testing.
--    Inputs: For sql-ext-01 Exercise 13, For one unavailable requested extension, assemble observed package availability plus reviewed source/build provenance, SBOM/native dependencies, CVEs, license, reproducibility, signer/hash, patch owner/SLA, restore compatibility, removal test, and approving authority.
--    Expected result/shape: For sql-ext-01 Exercise 13, One row per `review_item`, with `review_item`, `observed_evidence`, `status`, `owner`, and `blocking_reason`. Unknown or missing evidence remains visible and blocks approval.
--    Verify: For sql-ext-01 Exercise 13, A successful local compile is not sufficient. Remove the source signature/SBOM or make the removal rehearsal fail; the final decision must remain `rejected`/`blocked` without installing anything. Hint ladder, rung 1: Native extension code executes inside the database server process, so provenance and patch ownership are security controls.
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
--    Inputs: For sql-ext-01 Exercise 14, Plan an extension upgrade only in a separately restored disposable database. Capture installed/target versions, package build, dependency graph, objects, query plans/results, backup compatibility, application canaries, elapsed/lock/WAL evidence, rollback limit, owner, and cleanup.
--    Expected result/shape: For sql-ext-01 Exercise 14, One row per `phase_number`, with `phase_name`, `before_evidence`, `after_evidence`, `status`, `owner`, and `failure_response`; this transaction emits a plan and changes no extension.
--    Verify: For sql-ext-01 Exercise 14, Every before/after correctness and performance check must pass within explicit tolerances. Inject a changed result or incompatible backup restore and prove approval remains blocked; record when downgrade is not a safe rollback and restore/forward-fix is required. Hint ladder, rung 1: Extension DDL success does not prove application semantics, plans, backup compatibility, or reversibility.

ROLLBACK;
\echo 'SQL-EXT-01 complete: no extension was created and schema was rolled back'
