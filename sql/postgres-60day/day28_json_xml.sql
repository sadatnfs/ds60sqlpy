-- Day 28: JSON/XML Handling
BEGIN;
SET search_path TO training, public;

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
ORDER BY cnt DESC;

-- JSONB: array expansion example (simulate array in metadata)
-- SELECT e.event_id, x AS tag
-- FROM events e,
-- LATERAL jsonb_array_elements_text(COALESCE(e.metadata->'tags','[]'::jsonb)) AS t(x);

-- XML: use xpath to extract values
SELECT doc_id,
       xpath('/order/id/text()', payload) AS order_ids,
       xpath('/order/status/text()', payload) AS statuses
FROM xml_docs
LIMIT 20;

-- Exercises
-- 1) Count events by path segment (e.g., first directory in metadata->>'path').
-- 2) Extract order IDs from xml_docs and join to orders to validate status.

ROLLBACK;
