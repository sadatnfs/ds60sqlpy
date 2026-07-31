-- SQL-TYPES-01: PostgreSQL-native types and searchable documents
-- BEGINNER WORKFLOW — sql-types-01: PostgreSQL-Native Types and Searchable Documents
-- Guide: sql/professional/companion-guides/sql_types_01_native_types_search.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-types-01/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
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
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 2. Find documents available on 2026-08-11 but not inside a blackout window.
--    State the inclusive/exclusive boundary rule.
--
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Use JSONPath to return documents whose numeric minutes exceed 30. Avoid
--    assuming that every arbitrary JSON value can be cast safely.
--
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 4. Search for the web-style query '"schema migration" verify' and rank
--    matches deterministically.
--
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 5. Compare jsonb_ops with jsonb_path_ops, and GIN full-text search with an
--    optional pg_trgm similarity index. State which operators and update costs
--    matter before choosing.
--
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 6. Decide which modeled fields deserve a domain, enum, reference table,
--    array, range, JSONB document, or ordinary normalized relation.
--
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 7. Model recurring availability with datemultirange. Normalize overlapping
--    input ranges, find gaps inside August 2026, and state whether adjacent
--    ranges should merge for this domain.
--
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 8. Add inet client addresses and cidr network rules. Return the most-specific
--    containing network for each address using network operators, prefix length,
--    and deterministic tie-breaking; identify a suitable index family.
--
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 9. Define a domain for a nonnegative monetary amount with fixed scale.
--    Compare numeric with bigint minor units and double precision for equality,
--    aggregation, range, rounding, and application interoperability.
--
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 10. Promote one frequently queried JSONB property into a stored generated
--     column. Guard shape and type, index the promoted value, and explain how
--     schema evolution can make a formerly valid payload fail on write.
--
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 11. Inspect to_tsvector output and explain dictionaries, stop words,
--     stemming, weights, and language configuration. Design a policy for rows
--     whose language differs from the default English configuration.
--
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 12. Replace the tags array with normalized document_tags rows and a foreign
--     key to tags. Compare containment queries, order/duplicates, constraints,
--     write amplification, and when an array remains the clearer model.

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
--    Inputs: Use only the declared lesson objects (pro_types_lab.documents, pg_catalog.pg_indexes, pg_catalog.pg_available_extensions) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.

ROLLBACK;
\echo 'SQL-TYPES-01 complete: pro_types_lab was rolled back'
