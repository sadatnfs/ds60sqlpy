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
--    Inputs: For sql-types-01 Exercise 1, complete the tag containment written analysis and support its claims with read-only evidence from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-types-01 Exercise 1, expected output: a completed the tag containment written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `any`.
--    Verify: For sql-types-01 Exercise 1, check the tag containment written analysis against `any`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-types-01 Exercise 1, check the tag containment written analysis against `any`.
-- 2. Find documents available on 2026-08-11 but not inside a blackout window.
--    State the inclusive/exclusive boundary rule.
--
--    Inputs: For sql-types-01 Exercise 2, complete the range subtraction written analysis and support its claims with read-only evidence from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-types-01 Exercise 2, expected output: a completed the range subtraction written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
--    Verify: For sql-types-01 Exercise 2, check the range subtraction written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-types-01 Exercise 2, check the range subtraction written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
-- 3. Use JSONPath to return documents whose numeric minutes exceed 30. Avoid
--    assuming that every arbitrary JSON value can be cast safely.
--
--    Inputs: For sql-types-01 Exercise 3, complete the typed jsonpath written analysis and support its claims with read-only evidence from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-types-01 Exercise 3, expected output: a completed the typed jsonpath written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
--    Verify: For sql-types-01 Exercise 3, check the typed jsonpath written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-types-01 Exercise 3, check the typed jsonpath written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
-- 4. Search for the web-style query '"schema migration" verify' and rank
--    matches deterministically.
--
--    Inputs: For sql-types-01 Exercise 4, complete the full-text query written analysis and support its claims with read-only evidence from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-types-01 Exercise 4, expected output: a completed the full-text query written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `websearch_to_tsquery`.
--    Verify: For sql-types-01 Exercise 4, check the full-text query written analysis against `websearch_to_tsquery`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-types-01 Exercise 4, check the full-text query written analysis against `websearch_to_tsquery`.
-- 5. Compare jsonb_ops with jsonb_path_ops, and GIN full-text search with an
--    optional pg_trgm similarity index. State which operators and update costs
--    matter before choosing.
--
--    Inputs: For sql-types-01 Exercise 5, read from `pg_trgm`. Build the answer toward `jsonb_ops`, `jsonb_path_ops`, and `tsvector`; keep `jsonb_ops` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-types-01 Exercise 5, expected output: one row per `jsonb_ops`. The final columns are `jsonb_ops`, `jsonb_path_ops`, and `tsvector`.
--    Verify: For sql-types-01 Exercise 5, reselect the returned keys directly from the source; require unique `jsonb_ops` where the expected grain is one row per key and confirm the projected `jsonb_ops`, `jsonb_path_ops`, and `tsvector` against `pg_trgm`. Add one source row with a new `jsonb_ops`; verify the result gains exactly one row carrying that `jsonb_ops` value.
--    Hint ladder, rung 1: For sql-types-01 Exercise 5, select `jsonb_ops` from `pg_trgm` before adding derived columns.
-- 6. Decide which modeled fields deserve a domain, enum, reference table,
--    array, range, JSONB document, or ordinary normalized relation.
--
--    Inputs: For sql-types-01 Exercise 6, complete the type decision written analysis and support its claims with read-only evidence from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-types-01 Exercise 6, expected output: a completed the type decision written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
--    Verify: For sql-types-01 Exercise 6, check the type decision written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-types-01 Exercise 6, check the type decision written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
-- 7. Model recurring availability with datemultirange. Normalize overlapping
--    input ranges, find gaps inside August 2026, and state whether adjacent
--    ranges should merge for this domain.
--
--    Inputs: For sql-types-01 Exercise 7, read from `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`. Compute `normalized_availability`, and `august_gaps` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-types-01 Exercise 7, expected output: one row per day. The final columns are `normalized_availability`, and `august_gaps`.
--    Verify: For sql-types-01 Exercise 7, evaluate each of `normalized_availability`, and `august_gaps` in a separate control `SELECT` over `pro_types_lab.documents`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_available_extensions`; require one final row and compare every value. Add one source row with a new `day`; verify the result gains exactly one row carrying that `day` value.
--    Hint ladder, rung 1: For sql-types-01 Exercise 7, run `schedule` one at a time. Record each CTE's row count and `day` uniqueness before the next stage uses it.
-- 8. Add inet client addresses and cidr network rules. Return the most-specific
--    containing network for each address using network operators, prefix length,
--    and deterministic tie-breaking; identify a suitable index family.
--
--    Inputs: For sql-types-01 Exercise 8, read from `clients`, and `rules`. Build the answer toward `client_id`, `address`, `rule_id`, and `network`; keep `client_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-types-01 Exercise 8, expected output: one row per `client_id`. The final columns are `client_id`, `address`, `rule_id`, and `network`. The final order is `client_id`.
--    Verify: For sql-types-01 Exercise 8, project `client_id` plus the raw source columns from `clients`, and `rules` at each join stage; record row count and distinct `client_id`, then assert the final `client_id`, `address`, `rule_id`, and `network` values match those staged rows without unintended fanout or loss. Add one row for which `(match_rank = 1)` is true and one for which it is false; verify only the matching `client_id` value is returned.
--    Hint ladder, rung 1: For sql-types-01 Exercise 8, run `ranked` one at a time. Record each CTE's row count and `client_id` uniqueness before the next stage uses it.
-- 9. Define a domain for a nonnegative monetary amount with fixed scale.
--    Compare numeric with bigint minor units and double precision for equality,
--    aggregation, range, rounding, and application interoperability.
--
--    Inputs: For sql-types-01 Exercise 9, read from `pro_types_lab.nonnegative_money`. Compute `exact_decimal_sum`, and `declared_rounding_example` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-types-01 Exercise 9, expected output: exactly one aggregate summary row. The final columns are `exact_decimal_sum`, and `declared_rounding_example`.
--    Verify: For sql-types-01 Exercise 9, evaluate each of `exact_decimal_sum` in a separate control `SELECT` over `pro_types_lab.nonnegative_money`; require one final row and compare every value. Add one source row with a new `declared_rounding_example`; verify the result gains exactly one row carrying that `declared_rounding_example` value.
--    Hint ladder, rung 1: For sql-types-01 Exercise 9, select `declared_rounding_example` from `pro_types_lab.nonnegative_money` before adding derived columns.
-- 10. Promote one frequently queried JSONB property into a stored generated
--     column. Guard shape and type, index the promoted value, and explain how
--     schema evolution can make a formerly valid payload fail on write.
--
--    Inputs: For sql-types-01 Exercise 10, read from `pro_types_lab.documents`, and `documents_estimated_minutes_idx`. Build the answer toward `document_id`, and `estimated_minutes`; keep `document_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-types-01 Exercise 10, expected output: one row per `document_id`. The final columns are `document_id`, and `estimated_minutes`. The final order is `d.document_id`.
--    Verify: For sql-types-01 Exercise 10, run an anti-check that counts rows where NOT ((d.estimated_minutes > 30)); require unique `document_id` where the expected grain is one row per key and confirm the projected `document_id`, and `estimated_minutes` against `pro_types_lab.documents`, and `documents_estimated_minutes_idx`. Insert rows immediately before, exactly at, and immediately after `d.estimated_minutes > 30`; identify which rows pass each inclusive or exclusive comparison.
--    Hint ladder, rung 1: For sql-types-01 Exercise 10, inspect the source keys that survive `WHERE`; then check `d.document_id` before applying the row cap.
-- 11. Inspect to_tsvector output and explain dictionaries, stop words,
--     stemming, weights, and language configuration. Design a policy for rows
--     whose language differs from the default English configuration.
--
--    Inputs: For sql-types-01 Exercise 11, read from `pro_types_lab.documents`. Build the answer toward `document_id`, and `lexemes`; keep `document_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-types-01 Exercise 11, expected output: one row per `document_id`. The final columns are `document_id`, and `lexemes`. The final order is `d.document_id`.
--    Verify: For sql-types-01 Exercise 11, reselect the returned keys directly from the source; require unique `document_id` where the expected grain is one row per key and confirm the projected `document_id`, and `lexemes` against `pro_types_lab.documents`. Add one source row with a new `document_id`; verify the result gains exactly one row carrying that `document_id` value.
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
--    Inputs: For sql-types-01 Exercise 12, read from `pro_types_lab.documents`, `pro_types_lab.tags`, and `pro_types_lab.document_tags`. Build the answer toward `tag_name`; keep `document_id`, and `title` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-types-01 Exercise 12, expected output: one row per `document_id`, and `title`. The final columns are `tag_name`. The final order is `d.document_id`.
--    Verify: For sql-types-01 Exercise 12, independently aggregate `pro_types_lab.documents`, `pro_types_lab.tags`, and `pro_types_lab.document_tags` by `document_id`, and `title`; require one output row for every distinct `document_id`, and `title` tuple satisfying `(t.tag_name IN ('postgresql', 'operations'))` and compare `tag_name` tuple by tuple. Add duplicate source candidates for `document_id`, and `title`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
--    Hint ladder, rung 1: For sql-types-01 Exercise 12, start with the first relation in `pro_types_lab.documents`, `pro_types_lab.tags`, and `pro_types_lab.document_tags`; after each join, record total rows and distinct `document_id`, and `title` so the exact fanout or loss is visible.

ROLLBACK;
\echo 'SQL-TYPES-01 complete: pro_types_lab was rolled back'
