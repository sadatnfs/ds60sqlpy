-- Day 28: JSON/XML Handling
-- BEGINNER WORKFLOW — sql-28: JSON XML
-- Guide: sql/postgres-60day/companion-guides/day28_json_xml.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-28/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: events, xml_docs.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Query JSONB and XML with explicit path, type, missing-key, and safe-cast behavior instead of assuming semi-structured data is schema-free.
-- Assumptions: JSON text extraction with `->>` returns text or NULL. XML XPath results are arrays. Course metadata keys are small and deterministic.
-- Pitfall: Casting missing or malformed JSON text directly raises; broad JSON containment or regex extraction needs validation and appropriate indexing evidence.
-- Predict row grain and NULL/order behavior before executing each example.

-- JSONB: extract fields
SELECT event_id,
       event_type,
       metadata->>'path' AS path,
       metadata->>'device' AS device,
       metadata->>'campaign' AS campaign
FROM events
ORDER BY event_id DESC
LIMIT 50;

-- JSONB: filter and aggregate
SELECT metadata->>'device' AS device,
       COUNT(*) AS cnt
FROM events
WHERE metadata->>'campaign' IN ('spring','summer')
GROUP BY device
ORDER BY cnt DESC, device NULLS LAST;

-- JSONB: array expansion example (simulate array in metadata)
-- SELECT e.event_id, x AS tag
-- FROM events e,
-- LATERAL jsonb_array_elements_text(COALESCE(e.metadata->'tags','[]'::jsonb)) AS t(x);

-- XML: use xpath to extract values
SELECT doc_id,
       xpath('/order/id/text()', payload) AS order_ids,
       xpath('/order/status/text()', payload) AS statuses
FROM xml_docs
ORDER BY doc_id
LIMIT 20;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Extract customer acquisition channel and referrer from JSONB attributes.
--    Hint: `->>` returns text and naturally yields NULL for a missing key.
--    Inputs: Use only the declared lesson objects (events, xml_docs) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 2. [Query writing] Find mobile-channel customers using JSONB containment.
--    Hint: `@>` tests whether the left JSONB contains the declared object.
--    Inputs: Use only the declared lesson objects (events, xml_docs) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 3. [Query writing] Count event rows with missing device metadata separately from present values.
--    Hint: Use `?` to test key existence rather than comparing extracted text to NULL.
--    Inputs: Use only the declared lesson objects (events, xml_docs) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
-- 4. [Prediction] Aggregate event-type counts into a JSONB object per customer and predict key ordering expectations.
--    Hint: JSON objects are mappings; do not treat key order as a semantic contract.
--    Inputs: Use only the declared lesson objects (events, xml_docs) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
-- 5. [Debugging] Extract order ID and status text from XML documents without assuming XPath returns a scalar.
--    Hint: Index the XML array returned by `xpath`, cast through text, and strip element markup with `string(...)` XPath.
--    Inputs: Use only the declared lesson objects (events, xml_docs) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
-- 6. [Extension] Safely cast a numeric JSON text field from sample payloads, returning NULL for missing or malformed values.
--    Hint: Validate extracted text with a numeric regex before casting.
--    Inputs: Use only the declared lesson objects (events, xml_docs) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.

ROLLBACK;
