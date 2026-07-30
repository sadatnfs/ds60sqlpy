-- Day 28: JSON/XML Handling
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
-- 2. [Query writing] Find mobile-channel customers using JSONB containment.
--    Hint: `@>` tests whether the left JSONB contains the declared object.
-- 3. [Query writing] Count event rows with missing device metadata separately from present values.
--    Hint: Use `?` to test key existence rather than comparing extracted text to NULL.
-- 4. [Prediction] Aggregate event-type counts into a JSONB object per customer and predict key ordering expectations.
--    Hint: JSON objects are mappings; do not treat key order as a semantic contract.
-- 5. [Debugging] Extract order ID and status text from XML documents without assuming XPath returns a scalar.
--    Hint: Index the XML array returned by `xpath`, cast through text, and strip element markup with `string(...)` XPath.
-- 6. [Extension] Safely cast a numeric JSON text field from sample payloads, returning NULL for missing or malformed values.
--    Hint: Validate extracted text with a numeric regex before casting.

ROLLBACK;
