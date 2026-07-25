-- Day 28 solutions: JSONB and XML
SET search_path TO training, public;

-- Exercise 1: count events by the first directory in metadata.path.
WITH paths AS (
  SELECT CASE
           WHEN trim(BOTH '/' FROM metadata->>'path') = '' THEN '[root]'
           ELSE split_part(trim(BOTH '/' FROM metadata->>'path'), '/', 1)
         END AS first_path_segment
  FROM events
)
SELECT first_path_segment, COUNT(*) AS events
FROM paths
GROUP BY first_path_segment
ORDER BY events DESC, first_path_segment;

-- Exercise 2: extract XML values and validate status against relational data.
WITH parsed AS (
  SELECT doc_id,
         ((xpath('/order/id/text()', payload))[1]::text)::int AS order_id,
         (xpath('/order/status/text()', payload))[1]::text AS xml_status
  FROM xml_docs
)
SELECT p.doc_id,
       p.order_id,
       p.xml_status,
       o.status AS relational_status,
       p.xml_status = o.status AS statuses_match
FROM parsed p
LEFT JOIN orders o USING (order_id)
ORDER BY p.doc_id;
