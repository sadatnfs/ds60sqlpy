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
--    Inputs: For sql-types-01 Exercise 1, filter `documents` to published rows whose `tags` array contains both `postgresql` and `operations` using one `@>` containment predicate.
--    Expected result/shape: For sql-types-01 Exercise 1, expected output: exactly one row at document grain with `document_id` and `title`, ordered by `document_id`.
--    Verify: For sql-types-01 Exercise 1, compare the result with an independent unnest/distinct-tag control, prove both required tags—not either one—are present, and explain that array GIN supports containment while two `= ANY` predicates express separate membership tests.
--    Hint ladder, rung 1: For sql-types-01 Exercise 1, check the tag containment written analysis against `any`.
-- 2. Find documents available on 2026-08-11 but not inside a blackout window.
--    State the inclusive/exclusive boundary rule.
--
--    Inputs: For sql-types-01 Exercise 2, require `availability @> probe_date` and NOT `blackout_windows @> probe_date`, then probe the lower and upper endpoints of both `[)` ranges for document 201.
--    Expected result/shape: For sql-types-01 Exercise 2, expected output: document 202 for 2026-08-11 plus four boundary rows showing availability lower included, blackout lower excluded from use, blackout upper available, and availability upper excluded.
--    Verify: For sql-types-01 Exercise 2, assert the `[lower, upper)` truth table directly and distinguish an unavailable document from a missing result row; test both range and multirange containment at exact endpoints.
--    Hint ladder, rung 1: For sql-types-01 Exercise 2, check the range subtraction written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
-- 3. Use JSONPath to return documents whose numeric minutes exceed 30. Avoid
--    assuming that every arbitrary JSON value can be cast safely.
--
--    Inputs: For sql-types-01 Exercise 3, use JSONPath to require a JSON number greater than 30 before casting its text representation to unbounded `numeric`.
--    Expected result/shape: For sql-types-01 Exercise 3, expected output: one row per matching document with `document_id`, `title`, and `minutes_numeric`; the supplied fixture returns documents 201 and 202.
--    Verify: For sql-types-01 Exercise 3, add string, missing, fractional, and very large numeric values; prove JSONPath excludes nonnumbers, numeric preserves fractional/range values, and no arbitrary JSON value reaches an unsafe integer cast.
--    Hint ladder, rung 1: For sql-types-01 Exercise 3, check the typed jsonpath written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
-- 4. Search for the web-style query '"schema migration" verify' and rank
--    matches deterministically.
--
--    Inputs: For sql-types-01 Exercise 4, build one English `websearch_to_tsquery` for the phrase and term, match it against the stored weighted search vector, and compute `ts_rank_cd`.
--    Expected result/shape: For sql-types-01 Exercise 4, expected output: matching `document_id`, `title`, and `rank_score`, ordered by rank descending then `document_id`; the fixture returns document 201.
--    Verify: For sql-types-01 Exercise 4, display the parsed tsquery and source lexemes, assert every returned vector satisfies `@@`, and retain the document-ID tie-breaker because equal rank scores are possible.
--    Hint ladder, rung 1: For sql-types-01 Exercise 4, check the full-text query written analysis against `websearch_to_tsquery`.
-- 5. Compare jsonb_ops with jsonb_path_ops, and GIN full-text search with an
--    optional pg_trgm similarity index. State which operators and update costs
--    matter before choosing.
--
--    Inputs: For sql-types-01 Exercise 5, return an operator-first matrix mapping four real predicates to candidate index families and one superficially related query that each index does not serve.
--    Expected result/shape: For sql-types-01 Exercise 5, expected output: four rows with `workload`, `matching_operator`, `candidate_index`, `nonmatching_query`, and `reason`, covering arrays, JSONB, full-text, and ranges.
--    Verify: For sql-types-01 Exercise 5, inspect operator classes and compare EXPLAIN plans only after representative data exists; distinguish `jsonb_ops` flexibility from `jsonb_path_ops` size/supported-operator trade-offs and treat pg_trgm as optional.
--    Hint ladder, rung 1: For sql-types-01 Exercise 5, select `jsonb_ops` from `pg_trgm` before adding derived columns.
-- 6. Decide which modeled fields deserve a domain, enum, reference table,
--    array, range, JSONB document, or ordinary normalized relation.
--
--    Inputs: For sql-types-01 Exercise 6, classify modeled field shapes against domain, CHECK/enum, reference table, array, range/multirange, JSONB, and normalized relation choices.
--    Expected result/shape: For sql-types-01 Exercise 6, expected output: seven deterministic rows with `field_shape`, `candidate_type`, and a concrete `decision_rule`.
--    Verify: For sql-types-01 Exercise 6, challenge each choice with one evolution/query/integrity counterexample, and prefer the type whose operators and constraints match the domain rather than the most exotic type.
--    Hint ladder, rung 1: For sql-types-01 Exercise 6, check the type decision written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
-- 7. Model recurring availability with datemultirange. Normalize overlapping
--    input ranges, find gaps inside August 2026, and state whether adjacent
--    ranges should merge for this domain.
--
--    Inputs: For sql-types-01 Exercise 7, construct a `datemultirange` from overlapping and adjacent half-open date ranges, then subtract it from the August 2026 month range.
--    Expected result/shape: For sql-types-01 Exercise 7, expected output: exactly one row with canonical `normalized_availability` and `august_gaps`; adjacent/overlapping discrete ranges merge.
--    Verify: For sql-types-01 Exercise 7, independently test every August date for membership in either availability or gaps, require no overlap and complete month coverage, and state whether adjacency should merge in this business domain.
--    Hint ladder, rung 1: For sql-types-01 Exercise 7, run `schedule` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
-- 8. Add inet client addresses and cidr network rules. Return the most-specific
--    containing network for each address using network operators, prefix length,
--    and deterministic tie-breaking; identify a suitable index family.
--
--    Inputs: For sql-types-01 Exercise 8, preserve every client with `LEFT JOIN LATERAL`; inside the lateral query choose the containing CIDR with greatest mask length and `rule_id` tie-breaker.
--    Expected result/shape: For sql-types-01 Exercise 8, expected output: one row per client with `client_id`, `address`, `rule_id`, and `network`; matched clients receive their longest prefix and the unmatched client retains NULL rule fields.
--    Verify: For sql-types-01 Exercise 8, assert output count equals client count, validate each chosen network contains its address, prove no more-specific candidate exists, and test both IPv4, IPv6, and unmatched addresses.
--    Hint ladder, rung 1: For sql-types-01 Exercise 8, run `ranked` one at a time. Record each CTE's row count and `client_id` uniqueness before the next stage uses it.
-- 9. Define a domain for a nonnegative monetary amount with fixed scale.
--    Compare numeric with bigint minor units and double precision for equality,
--    aggregation, range, rounding, and application interoperability.
--
--    Inputs: For sql-types-01 Exercise 9, define a nonnegative `numeric(12,2)` domain, demonstrate exact arithmetic and rounding, and compare it with bigint minor units and double precision.
--    Expected result/shape: For sql-types-01 Exercise 9, expected output: one scalar evidence row plus a three-row storage matrix; the domain cast of NULL remains NULL because NOT NULL belongs on the consuming column.
--    Verify: For sql-types-01 Exercise 9, reject a negative value, assert exact sum `30.30` and declared rounding `10.13`, test NULL at both domain and NOT NULL column boundaries, and document currency/scale when using minor units.
--    Hint ladder, rung 1: For sql-types-01 Exercise 9, select `declared_rounding_example` from `pro_types_lab.nonnegative_money` before adding derived columns.
-- 10. Promote one frequently queried JSONB property into a stored generated
--     column. Guard shape and type, index the promoted value, and explain how
--     schema evolution can make a formerly valid payload fail on write.
--
--    Inputs: For sql-types-01 Exercise 10, add a stored generated integer that accepts only JSON numbers that are integral and within PostgreSQL integer range; otherwise return NULL, then index it.
--    Expected result/shape: For sql-types-01 Exercise 10, expected output: boundary rows for string, missing, fractional, and out-of-range minutes, all safely classified as NULL; valid integral seed values remain queryable.
--    Verify: For sql-types-01 Exercise 10, prove all four malformed-for-the-property payloads insert without cast errors, valid 35/45 values materialize, the index exists, and the application policy distinguishes invalid from absent rather than silently treating both as zero.
--    Hint ladder, rung 1: For sql-types-01 Exercise 10, inspect the source keys that survive `WHERE`; then check `d.document_id` before applying the row cap.
-- 11. Inspect to_tsvector output and explain dictionaries, stop words,
--     stemming, weights, and language configuration. Design a policy for rows
--     whose language differs from the default English configuration.
--
--    Inputs: For sql-types-01 Exercise 11, convert each title/body pair with an explicit English text-search configuration and expose the resulting lexemes.
--    Expected result/shape: For sql-types-01 Exercise 11, expected output: one row per document with `document_id` and `lexemes`, ordered by `document_id`.
--    Verify: For sql-types-01 Exercise 11, inspect stemming and stop-word behavior with known tokens, compare a non-English sample under the English and appropriate configurations, and keep the configured language explicit in stored-vector policy.
--    Hint ladder, rung 1: For sql-types-01 Exercise 11, check `d.document_id` before applying the row cap.
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
--    Inputs: For sql-types-01 Exercise 12, normalize legacy tag arrays with `lower(btrim(tag))`, insert distinct vocabulary rows, and insert distinct `(document_id, tag_id)` bridge rows.
--    Expected result/shape: For sql-types-01 Exercise 12, expected output: one normalized vocabulary row per canonical tag, one bridge row per document/tag pair despite duplicate legacy spellings, and document 201 for the two-tag relational query.
--    Verify: For sql-types-01 Exercise 12, inject `python`, ` Python `, and duplicate `python` in one array, assert only one bridge pair survives, verify foreign-key and composite-primary-key enforcement, and record that array order/case/whitespace are intentionally discarded.
--    Hint ladder, rung 1: For sql-types-01 Exercise 12, start with the first relation in `pro_types_lab.documents`, `pro_types_lab.tags`, and `pro_types_lab.document_tags`; after each join, record total rows and distinct `document_id`, and `title` so the exact fanout or loss is visible.

ROLLBACK;
\echo 'SQL-TYPES-01 complete: pro_types_lab was rolled back'
