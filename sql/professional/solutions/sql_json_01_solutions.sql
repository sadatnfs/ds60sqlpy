-- SQL-JSON-01: complete typed-projection references and exact grain/value assertions
\set ON_ERROR_STOP on
BEGIN;
DO $target$
BEGIN
 IF current_database()<>'advanced_sql_training' OR current_setting('server_version_num')::integer<170000 THEN
  RAISE EXCEPTION 'Use the disposable advanced_sql_training PostgreSQL 17 runtime';
 END IF;
END
$target$;

CREATE TEMP TABLE j17_documents (
  document_id integer PRIMARY KEY,
  payload jsonb NOT NULL
) ON COMMIT DROP;

INSERT INTO j17_documents
VALUES
  (1, '{"shipping_fee":4.00,"items":[{"sku":"P","qty":2,"price":5.00},{"sku":"Q","qty":1,"price":3.00}]}'),
  (2, '{"shipping_fee":0.00,"items":[]}'),
  (3, '{"shipping_fee":2.00}'),
  (4, '{"shipping_fee":1.00,"items":[{"sku":"R","qty":null,"price":7.00},{"sku":"S","price":2.00}]}');

CREATE TEMP VIEW j17_lines AS
SELECT
  d.document_id,
  j.item_no,
  j.sku,
  j.qty,
  j.unit_price
FROM
  j17_documents AS d
  CROSS JOIN JSON_TABLE (d.payload, '$.items[*]' COLUMNS (item_no FOR ORDINALITY, sku text PATH '$.sku', qty integer PATH '$.qty' DEFAULT 1 ON EMPTY ERROR ON ERROR, unit_price numeric(10, 2)
  PATH '$.price' ERROR ON EMPTY ERROR ON ERROR)) AS j;

CREATE TEMP VIEW j17_outer AS
SELECT
  d.document_id,
  j.item_no,
  j.sku,
  j.qty,
  j.unit_price
FROM
  j17_documents AS d
  LEFT JOIN LATERAL JSON_TABLE (d.payload, '$.items[*]' COLUMNS (item_no FOR ORDINALITY, sku text PATH '$.sku', qty integer PATH '$.qty' DEFAULT 1 ON EMPTY ERROR ON ERROR, unit_price numeric(10, 2)
  PATH '$.price' ERROR ON EMPTY ERROR ON ERROR)) AS j ON true;

CREATE FUNCTION pg_temp.assert_equal (actual jsonb, expected jsonb, label text)
  RETURNS void
  LANGUAGE plpgsql
  AS $assert$
BEGIN
 IF actual IS DISTINCT FROM expected THEN RAISE EXCEPTION 'JSON projection contract failed: %; actual %',label,actual;END IF;
END
$assert$
;
-- Exercises: complete executable references
-- 1. two actual items become four LEFT rows after preserving parents.
SELECT
  pg_temp.assert_equal (to_jsonb (count(*)), '2', 'cross item rows for documents1-3')
FROM
  j17_lines
WHERE
  document_id <= 3;

SELECT
  pg_temp.assert_equal (to_jsonb (count(*)), '4', 'left rows for documents1-3')
FROM
  j17_outer
WHERE
  document_id <= 3;

SELECT
  d.document_id,
  d.payload ? 'items' AS items_field_present,
  jsonb_typeof(d.payload -> 'items') AS items_type
FROM
  j17_documents AS d
WHERE
  document_id <= 3
ORDER BY
  document_id;

-- 2. the typed relation preserves four actual item positions, including unknown qty.
SELECT
  document_id,
  item_no,
  sku,
  qty,
  unit_price
FROM
  j17_lines
ORDER BY
  document_id,
  item_no;

SELECT
  pg_temp.assert_equal ((
    SELECT
      jsonb_agg(to_jsonb (l)
    ORDER BY document_id, item_no)
    FROM j17_lines AS l), '[{"document_id":1,"item_no":1,"sku":"P","qty":2,"unit_price":5},{"document_id":1,"item_no":2,"sku":"Q","qty":1,"unit_price":3},{"document_id":4,"item_no":1,"sku":"R","qty":null,"unit_price":7},{"document_id":4,"item_no":2,"sku":"S","qty":1,"unit_price":2}]', 'typed item identity and values');

SELECT
  pg_temp.assert_equal (to_jsonb (count(*)), '4', 'composite item positions are unique')
FROM ( SELECT DISTINCT
    document_id,
    item_no
  FROM
    j17_lines) AS keys;

-- 3. ON EMPTY is not the error policy or a replacement for explicit JSON null.
CREATE TEMP TABLE answer_3 ON COMMIT DROP AS
SELECT
  j.item_no, j.qty, j.qty_present
FROM
  JSON_TABLE ('{"items":[{"qty":null},{}]}', '$.items[*]' COLUMNS (item_no FOR ORDINALITY, qty integer PATH '$.qty' DEFAULT 1 ON EMPTY ERROR ON ERROR, qty_present boolean EXISTS PATH '$.qty')) AS j;

SELECT
  pg_temp.assert_equal ((
    SELECT
      jsonb_agg(to_jsonb (a)
    ORDER BY item_no)
    FROM answer_3 AS a), '[{"item_no":1,"qty":null,"qty_present":true},{"item_no":2,"qty":1,"qty_present":false}]', 'null versus empty');

SELECT
  pg_temp.assert_equal (to_jsonb (qty IS NULL), 'true', 'explicit NULL ON ERROR policy')
FROM
  JSON_TABLE ('{"items":[{"qty":"two"}]}', '$.items[*]' COLUMNS (qty integer PATH '$.qty' NULL ON ERROR)) AS j;

DO $strict_error$
BEGIN
 PERFORM qty FROM JSON_TABLE('{"items":[{"qty":"two"}]}','$.items[*]' COLUMNS(qty integer PATH '$.qty' ERROR ON ERROR)) AS j;
 RAISE EXCEPTION 'Expected strict conversion failure';
EXCEPTION WHEN invalid_text_representation THEN RAISE NOTICE 'Expected22P02';
END
$strict_error$;

-- 4. match counts exclude the null-extended row of an empty parent.
CREATE TEMP TABLE answer_4 ON COMMIT DROP AS
SELECT
  document_id, count(item_no) AS item_count, count(*) FILTER (WHERE item_no IS NOT NULL
    AND qty IS NULL) AS unknown_qty_count
FROM
  j17_outer
GROUP BY
  document_id;

SELECT
  *
FROM
  answer_4
ORDER BY
  document_id;

SELECT
  pg_temp.assert_equal ((
    SELECT
      jsonb_agg(to_jsonb (a)
    ORDER BY document_id)
    FROM answer_4 AS a), '[{"document_id":1,"item_count":2,"unknown_qty_count":0},{"document_id":2,"item_count":0,"unknown_qty_count":0},{"document_id":3,"item_count":0,"unknown_qty_count":0},{"document_id":4,"item_count":2,"unknown_qty_count":1}]', 'outer counts and quantity coverage');

-- 5. preserve partial known value without publishing it as a complete total.
CREATE TEMP TABLE answer_5 ON COMMIT DROP AS
WITH amounts AS (
  SELECT
    document_id,
    count(item_no) AS item_count,
    count(*) FILTER (WHERE item_no IS NOT NULL
      AND qty IS NULL) AS unknown_count,
    COALESCE(sum(qty * unit_price), 0::numeric) AS known_line_value
  FROM
    j17_outer
  GROUP BY
    document_id
)
SELECT
  d.document_id, a.known_line_value, CASE WHEN jsonb_typeof(d.payload -> 'items') IS DISTINCT FROM 'array'
    OR a.unknown_count > 0 THEN
    NULL
  ELSE
    a.known_line_value
  END AS accepted_order_value, CASE WHEN jsonb_typeof(d.payload -> 'items') IS DISTINCT FROM 'array' THEN
    'missing_items_array'
  WHEN a.unknown_count > 0 THEN
    'unknown_quantity'
  ELSE
    'complete'
  END AS coverage_state
FROM
  j17_documents AS d
  JOIN amounts AS a ON a.document_id = d.document_id;

SELECT
  *
FROM
  answer_5
ORDER BY
  document_id;

SELECT
  pg_temp.assert_equal ((
    SELECT
      jsonb_agg(to_jsonb (a)
    ORDER BY document_id)
    FROM answer_5 AS a), '[{"document_id":1,"known_line_value":13,"accepted_order_value":13,"coverage_state":"complete"},{"document_id":2,"known_line_value":0,"accepted_order_value":0,"coverage_state":"complete"},{"document_id":3,"known_line_value":0,"accepted_order_value":null,"coverage_state":"missing_items_array"},{"document_id":4,"known_line_value":2,"accepted_order_value":null,"coverage_state":"unknown_quantity"}]', 'accepted versus partial values');

-- 6. the parent shipping fee is added once after the item grain collapses.
CREATE TEMP TABLE answer_6 ON COMMIT DROP AS
SELECT
  d.document_id, a.accepted_order_value + (d.payload ->> 'shipping_fee')::numeric(10, 2) AS accepted_total
FROM
  j17_documents AS d
  JOIN answer_5 AS a ON a.document_id = d.document_id;

SELECT
  *
FROM
  answer_6
ORDER BY
  document_id;

SELECT
  pg_temp.assert_equal ((
    SELECT
      jsonb_agg(to_jsonb (a)
    ORDER BY document_id)
    FROM answer_6 AS a), '[{"document_id":1,"accepted_total":17},{"document_id":2,"accepted_total":0},{"document_id":3,"accepted_total":null},{"document_id":4,"accepted_total":null}]', 'one parent shipping fee');

SELECT
  pg_temp.assert_equal (to_jsonb (sum(l.qty * l.unit_price + (d.payload ->> 'shipping_fee')::numeric)), '21', 'deliberately wrong parent-fee fanout is observable')
FROM
  j17_documents AS d
  JOIN j17_lines AS l ON l.document_id = d.document_id
WHERE
  d.document_id = 1;

ROLLBACK;
