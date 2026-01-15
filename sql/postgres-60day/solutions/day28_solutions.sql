-- Day 28 - Solutions: JSON/JSONB and XML
-- Assumes: events(id, customer_id, occurred_at, payload JSONB), xml_docs(id, doc XML)

/*
Exercise 1) Extract campaign and channel from events.payload and compute conversion by channel.
Why: Use ->> to extract text fields; GROUP BY channel and compute simple rates.
*/
WITH clicks AS (
  SELECT customer_id,
         payload->>'channel'  AS channel,
         payload->>'campaign' AS campaign
  FROM events
  WHERE payload @> '{"event":"click"}'
), purchases AS (
  SELECT DISTINCT customer_id FROM events WHERE payload @> '{"event":"purchase"}'
)
SELECT c.channel,
       COUNT(*) AS clicks,
       COUNT(*) FILTER (WHERE c.customer_id IN (SELECT customer_id FROM purchases)) AS converters,
       ROUND(
         COUNT(*) FILTER (WHERE c.customer_id IN (SELECT customer_id FROM purchases))::numeric / NULLIF(COUNT(*),0)
       , 4) AS conv_rate
FROM clicks c
GROUP BY c.channel
ORDER BY conv_rate DESC NULLS LAST;

/* Portable alternative: replace FILTER with SUM(CASE WHEN … THEN 1 ELSE 0 END) */

/*
Exercise 2) Create a GIN index and compare performance of @> queries before/after.
*/
-- CREATE INDEX IF NOT EXISTS idx_events_payload ON events USING gin (payload jsonb_path_ops);
-- EXPLAIN ANALYZE SELECT * FROM events WHERE payload @> '{"channel":"Web"}';

/*
Exercise 3) Flatten line items embedded in an orders JSON and compute item-level revenue.
Assume orders_json(id, doc JSONB) with doc.items as an array of {sku, qty, price}.
*/
SELECT o.id,
       (item->>'sku')       AS sku,
       ((item->>'qty')::int * (item->>'price')::numeric) AS line_rev
FROM orders_json o
CROSS JOIN LATERAL jsonb_array_elements(o.doc->'items') AS item;

/*
XML example (brief): extract values via xpath
*/
-- SELECT id, xpath('//order/total/text()', doc) FROM xml_docs;

-- End of Day 28 solutions
