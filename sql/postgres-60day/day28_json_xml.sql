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
--    Inputs: For sql-28 Exercise 1, read from `customers`. Build the answer toward `customer_id`, `channel`, and `referrer`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-28 Exercise 1, expected output: One row per customer. The final columns are `customer_id`, `channel`, and `referrer`. The final order is `c.customer_id`.
--    Verify: For sql-28 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `channel`, and `referrer` against `customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-28 Exercise 1, check `c.customer_id` before applying the row cap.
-- 2. [Query writing] Find mobile-channel customers using JSONB containment.
--    Hint: `@>` tests whether the left JSONB contains the declared object.
--    Inputs: For sql-28 Exercise 2, read from `customers`. Build the answer toward `customer_id`, `full_name`, and `attributes`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-28 Exercise 2, expected output: Customer rows whose channel is mobile. The final columns are `customer_id`, `full_name`, and `attributes`. The final order is `c.customer_id`.
--    Verify: For sql-28 Exercise 2, run an anti-check that counts rows where NOT ((c.attributes @> '{"channel": "mobile"}'::jsonb)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `full_name`, and `attributes` against `customers`. Add one row for which `(c.attributes @> '{"channel": "mobile"}'::jsonb)` is true and one for which it is false; verify only the matching `customer_id` value is returned.
--    Hint ladder, rung 1: For sql-28 Exercise 2, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
-- 3. [Query writing] Count event rows with missing device metadata separately from present values.
--    Hint: Use `?` to test key existence rather than comparing extracted text to NULL.
--    Inputs: For sql-28 Exercise 3, read from `events`. Build the answer toward `has_device_key`, `missing_device_key`, and `all_events`; keep `has_device_key` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-28 Exercise 3, expected output: One summary row. The final columns are `has_device_key`, `missing_device_key`, and `all_events`.
--    Verify: For sql-28 Exercise 3, reselect the returned keys directly from the source; require unique `has_device_key` where the expected grain is one row per key and confirm the projected `has_device_key`, `missing_device_key`, and `all_events` against `events`. Add one source row with a new `has_device_key`; verify the result gains exactly one row carrying that `has_device_key` value.
--    Hint ladder, rung 1: For sql-28 Exercise 3, inspect the source keys that survive `WHERE`.
-- 4. [Prediction] Aggregate event-type counts into a JSONB object per customer and predict key ordering expectations.
--    Hint: JSON objects are mappings; do not treat key order as a semantic contract.
--    Inputs: For sql-28 Exercise 4, read from `events`. Build the answer toward `customer_id`, and `counts_by_type`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-28 Exercise 4, expected output: One row per customer with events. The final columns are `customer_id`, and `counts_by_type`. The final order is `customer_id`.
--    Verify: For sql-28 Exercise 4, independently aggregate `events` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `counts_by_type` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `counts_by_type` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-28 Exercise 4, run `event_counts` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
-- 5. [Debugging] Extract order ID and status text from XML documents without assuming XPath returns a scalar.
--    Hint: Index the XML array returned by `xpath`, cast through text, and strip element markup with `string(...)` XPath.
--    Inputs: For sql-28 Exercise 5, read from `xml_docs`. Build the answer toward `doc_id`, `order_id`, and `order_status`; keep `doc_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-28 Exercise 5, expected output: One row per XML document. The final columns are `doc_id`, `order_id`, and `order_status`. The final order is `xd.doc_id`.
--    Verify: For sql-28 Exercise 5, reselect the returned keys directly from the source; require unique `doc_id` where the expected grain is one row per key and confirm the projected `doc_id`, `order_id`, and `order_status` against `xml_docs`. Add one source row with a new `doc_id`; verify the result gains exactly one row carrying that `doc_id` value.
--    Hint ladder, rung 1: For sql-28 Exercise 5, check `xd.doc_id` before applying the row cap.
-- 6. [Extension] Safely cast a numeric JSON text field from sample payloads, returning NULL for missing or malformed values.
--    Hint: Validate extracted text with a numeric regex before casting.
--    Inputs: For sql-28 Exercise 6, read from `payloads`. Build the answer toward `payload`, and `safe_amount`; keep `payload` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-28 Exercise 6, expected output: One row per sample payload. The final columns are `payload`, and `safe_amount`.
--    Verify: For sql-28 Exercise 6, reselect the returned keys directly from the source; require unique `payload` where the expected grain is one row per key and confirm the projected `payload`, and `safe_amount` against `payloads`. Repeat with `NULL` in `payload`, and `safe_amount` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-28 Exercise 6, select `payload` from `payloads` before adding derived columns.

ROLLBACK;
