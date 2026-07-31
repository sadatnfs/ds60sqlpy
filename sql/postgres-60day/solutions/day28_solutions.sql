-- Day 28 executable solutions
-- SOLUTION READING MAP — sql-28: JSON XML
-- Explanation: sql/postgres-60day/solutions/day28_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day28_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
-- Target: PostgreSQL 16+; run only in advanced_sql_training.
-- ON_ERROR_STOP is supplied by the documented psql command.

BEGIN;
SET search_path TO training, public;

-- Shared teaching contract
-- Focus: Query JSONB and XML with explicit path, type, missing-key, and safe-cast behavior instead of assuming semi-structured data is schema-free.
-- Assumptions: JSON text extraction with `->>` returns text or NULL. XML XPath results are arrays. Course metadata keys are small and deterministic.
-- Pitfall: Casting missing or malformed JSON text directly raises; broad JSON containment or regex extraction needs validation and appropriate indexing evidence.

-- ---------------------------------------------------------------------------
-- Exercise 1: Query writing
-- Prompt: Extract customer acquisition channel and referrer from JSONB attributes.
-- Why: `->>` returns text and naturally yields NULL for a missing key.
-- Expected: One row per customer.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.attributes ->> 'channel' AS channel,
       c.attributes ->> 'referrer' AS referrer
FROM customers AS c
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 2: Query writing
-- Prompt: Find mobile-channel customers using JSONB containment.
-- Why: `@>` tests whether the left JSONB contains the declared object.
-- Expected: Customer rows whose channel is mobile.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `WHERE`: filters source rows before grouping and window calculation; SQL's unknown NULL comparisons do not pass.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT c.customer_id,
       c.full_name,
       c.attributes
FROM customers AS c
WHERE c.attributes @> '{"channel": "mobile"}'::jsonb
ORDER BY c.customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 3: Query writing
-- Prompt: Count event rows with missing device metadata separately from present values.
-- Why: Use `?` to test key existence rather than comparing extracted text to NULL.
-- Expected: One summary row.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `FILTER (WHERE ...)`: limits one aggregate without removing rows needed by neighboring aggregates.
SELECT COUNT(*) FILTER (WHERE e.metadata ? 'device') AS has_device_key,
       COUNT(*) FILTER (WHERE NOT e.metadata ? 'device') AS missing_device_key,
       COUNT(*) AS all_events
FROM events AS e;

-- ---------------------------------------------------------------------------
-- Exercise 4: Prediction
-- Prompt: Aggregate event-type counts into a JSONB object per customer and predict key ordering expectations.
-- Why: JSON objects are mappings; do not treat key order as a semantic contract.
-- Expected: One row per customer with events.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `GROUP BY`: collapses input rows to the listed key grain; every non-aggregated selected value must belong to that grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
WITH event_counts AS (
  SELECT e.customer_id,
         e.event_type,
         COUNT(*) AS event_count
  FROM events AS e
  GROUP BY e.customer_id, e.event_type
)
SELECT customer_id,
       jsonb_object_agg(event_type, event_count ORDER BY event_type) AS counts_by_type
FROM event_counts
GROUP BY customer_id
ORDER BY customer_id;

-- ---------------------------------------------------------------------------
-- Exercise 5: Debugging
-- Prompt: Extract order ID and status text from XML documents without assuming XPath returns a scalar.
-- Why: Index the XML array returned by `xpath`, cast through text, and strip element markup with `string(...)` XPath.
-- Expected: One row per XML document.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `ORDER BY`: defines presentation or ranking order; a unique final key makes tied values deterministic.
SELECT xd.doc_id,
       ((xpath('string(/order/id)', xd.payload))[1])::text::integer AS order_id,
       ((xpath('string(/order/status)', xd.payload))[1])::text AS order_status
FROM xml_docs AS xd
ORDER BY xd.doc_id;

-- ---------------------------------------------------------------------------
-- Exercise 6: Extension
-- Prompt: Safely cast a numeric JSON text field from sample payloads, returning NULL for missing or malformed values.
-- Why: Validate extracted text with a numeric regex before casting.
-- Expected: One row per sample payload.
-- Review the selected keys, grain, NULL behavior, and ordering before
-- treating the output as evidence.
-- Clause-by-clause reading:
-- - `WITH`: names an intermediate relation so its grain can be checked before later joins or aggregation.
-- - `VALUES`: constructs a small relation explicitly, which makes examples and expected cardinality inspectable.
-- - `SELECT`: defines the output columns at the query's final grain; aliases document the meaning of derived values.
-- - `FROM`: establishes the starting relation and therefore the initial row grain.
-- - `CASE`: encodes ordered business conditions; the first true branch wins and `ELSE` defines the remainder.
-- - pattern predicate: matches text according to the chosen operator; escaping and case sensitivity are intentional semantics.
WITH payloads(payload) AS (
  VALUES
    ('{"amount": "12.50"}'::jsonb),
    ('{"amount": "bad"}'::jsonb),
    ('{}'::jsonb)
)
SELECT payload,
       CASE
         WHEN payload ->> 'amount' ~ '^[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)$'
           THEN (payload ->> 'amount')::numeric
         ELSE NULL
       END AS safe_amount
FROM payloads;

-- No course answer persists changes or temporary objects.
ROLLBACK;
