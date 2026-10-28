-- SQL-JSON-01: PostgreSQL 17 JSON_TABLE, typed projection and result grain
-- Guide: sql/professional/companion-guides/sql_json_01_json_table.md
-- Use ./classroom -> PostgreSQL -> sql-json-01 -> Whole SQL lesson (psql).
-- Only the disposable advanced_sql_training database; all objects roll back.
\set ON_ERROR_STOP on
BEGIN;
DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' OR current_setting('server_version_num')::integer < 170000 THEN
    RAISE EXCEPTION 'Use the disposable advanced_sql_training PostgreSQL 17 runtime';
  END IF;
END
$course_target$;

SET LOCAL statement_timeout = '15s';

CREATE TEMP TABLE j17_documents (
  document_id integer PRIMARY KEY,
  payload jsonb NOT NULL
) ON COMMIT DROP;

INSERT INTO j17_documents
VALUES
  (1, '{"shipping_fee":4.00,"items":[{"sku":"P","qty":2,"price":5.00},{"sku":"Q","qty":1,"price":3.00}]}'),
  (2, '{"shipping_fee":0.00,"items":[]}'),
  (3, '{"shipping_fee":2.00}');

-- Worked case 1: CROSS flattening yields item rows; LEFT preserves outer documents.
-- The array ordinality starts at one. It is a position, not a permanent SKU key.
SELECT
  d.document_id,
  j.item_no,
  j.sku,
  j.qty,
  j.unit_price
FROM
  j17_documents AS d
  CROSS JOIN JSON_TABLE (d.payload, '$.items[*]' COLUMNS (item_no FOR ORDINALITY, sku text PATH '$.sku', qty integer PATH '$.qty' DEFAULT 1 ON EMPTY ERROR ON ERROR, unit_price numeric(10, 2)
  PATH '$.price' ERROR ON EMPTY ERROR ON ERROR)) AS j
ORDER BY
  d.document_id,
  j.item_no;

-- Expected: P and Q only, two item-grain rows from document one.
SELECT
  d.document_id,
  j.item_no,
  j.sku,
  j.qty,
  j.unit_price
FROM
  j17_documents AS d
  LEFT JOIN LATERAL JSON_TABLE (d.payload, '$.items[*]' COLUMNS (item_no FOR ORDINALITY, sku text PATH '$.sku', qty integer PATH '$.qty' DEFAULT 1 ON EMPTY ERROR ON ERROR, unit_price numeric(10, 2)
  PATH '$.price' ERROR ON EMPTY ERROR ON ERROR)) AS j ON true
ORDER BY
  d.document_id,
  j.item_no;

-- Expected: four rows; documents two and three have NULL item positions.
-- Worked case 2: an empty path, explicit JSON null and bad text differ.
SELECT
  j.item_no,
  j.qty,
  j.qty_present
FROM
  JSON_TABLE ('{"items":[{"qty":null},{}]}', '$.items[*]' COLUMNS (item_no FOR ORDINALITY, qty integer PATH '$.qty' DEFAULT 1 ON EMPTY ERROR ON ERROR, qty_present boolean EXISTS PATH '$.qty')) AS j
ORDER BY
  j.item_no;

-- Expected: (1,NULL,true), (2,1,false). Default one is a declared policy.
DO $bad_quantity$
BEGIN
  PERFORM qty FROM JSON_TABLE('{"items":[{"qty":"two"}]}','$.items[*]'
    COLUMNS(qty integer PATH '$.qty' ERROR ON ERROR)) AS j;
  RAISE EXCEPTION 'The invalid integer unexpectedly succeeded';
EXCEPTION WHEN invalid_text_representation THEN
  RAISE NOTICE 'Expected 22P02 conversion failure; it was not converted to a zero quantity';
END
$bad_quantity$;

CREATE TEMP TABLE j17_practice_documents (
  LIKE j17_documents INCLUDING ALL
) ON COMMIT DROP;

INSERT INTO j17_practice_documents
SELECT
  document_id,
  payload
FROM
  j17_documents;

INSERT INTO j17_practice_documents
  VALUES (4, '{"shipping_fee":1.00,"items":[{"sku":"R","qty":null,"price":7.00},{"sku":"S","price":2.00}]}');

-- Exercises
-- 1. [Prediction] Compare CROSS and LEFT JSON_TABLE for documents one through three.
-- Inputs: For sql-json-01 Exercise 1, inspect document IDs 1, 2 and 3 in j17_practice_documents. They contain two items, an empty items array and an absent items field respectively.
-- Expected result/shape: For sql-json-01 Exercise 1, cROSS yields two item rows; LEFT yields four outer-preserving rows. Display document_id, item_no, sku ordered by document_id, item_no. Actual child identity is (document_id,item_no); documents 2 and 3 have NULL item positions in the LEFT result.
-- Verify: For sql-json-01 Exercise 1, count non-NULL item_no independently and inspect the original field presence and type. A preserved outer placeholder is not an item, and empty and absent arrays are different source states.
-- Hint ladder, rung 1: Count matched item_no, not the preserved outer placeholder.
SAVEPOINT exercise_1;

-- Write your prediction and inspection here.
ROLLBACK TO SAVEPOINT exercise_1;

RELEASE SAVEPOINT exercise_1;

-- 2. [Query writing] Produce the typed item relation for all four documents.
-- Inputs: For sql-json-01 Exercise 2, project every declared items array in the four-document fixture. Missing qty defaults to one, explicit JSON null remains unknown, and prices use the declared exact numeric type.
-- Expected result/shape: For sql-json-01 Exercise 2, display document_id, item_no, sku, qty, unit_price ordered by document_id, item_no as (1,1,P,2,5), (1,2,Q,1,3), (4,1,R,NULL,7), (4,2,S,1,2), one row per (document_id,item_no).
-- Verify: For sql-json-01 Exercise 2, compare all projected values with the original array entries and assert four unique position pairs. R retains unknown quantity; S receives the declared absence default.
-- Hint ladder, rung 1: Define scalar types, path expressions and ordinal position in COLUMNS.
SAVEPOINT exercise_2;

-- Write your query here.
ROLLBACK TO SAVEPOINT exercise_2;

RELEASE SAVEPOINT exercise_2;

-- 3. [Debugging] Compare missing qty, JSON null and qty="two" under explicit error policies.
-- Inputs: For sql-json-01 Exercise 3, use the two-item worked literal with explicit JSON null and an omitted qty, then a separate literal whose qty is the text two.
-- Expected result/shape: For sql-json-01 Exercise 3, for the two-item literal, display item_no, qty, qty_present ordered by item_no as (1,NULL,true), (2,1,false). Invalid text produces SQL NULL under NULL ON ERROR and SQLSTATE 22P02 under ERROR ON ERROR; each generated literal position is identified by item_no.
-- Verify: For sql-json-01 Exercise 3, check presence separately from scalar value and catch only the intended conversion error. Neither policy permits silently converting a malformed quantity to zero revenue.
-- Hint ladder, rung 1: ON EMPTY and ON ERROR govern different conditions.
SAVEPOINT exercise_3;

-- Write your policy comparison here.
ROLLBACK TO SAVEPOINT exercise_3;

RELEASE SAVEPOINT exercise_3;

-- 4. [Verification] Count actual items while retaining all documents.
-- Inputs: For sql-json-01 Exercise 4, use a LEFT JSON_TABLE relation for all four source documents and count only generated item positions when measuring item or unknown-quantity rows.
-- Expected result/shape: For sql-json-01 Exercise 4, display document_id, item_count, unknown_qty_count ordered by document_id as (1,2,0), (2,0,0), (3,0,0), (4,2,1), one row per document_id.
-- Verify: For sql-json-01 Exercise 4, compare actual position counts with source array lengths. COUNT(*) would count an outer placeholder; unknown quantities count only rows with a non-NULL item_no.
-- Hint ladder, rung 1: Count item_no and count unknown qty only when item_no IS NOT NULL.
SAVEPOINT exercise_4;

-- Write your grouped query here.
ROLLBACK TO SAVEPOINT exercise_4;

RELEASE SAVEPOINT exercise_4;

-- 5. [Query writing] Separate known partial line value from accepted complete order value.
-- Inputs: For sql-json-01 Exercise 5, use all four documents, one declared currency and the worked missing-qty policy. Preserve array presence/type and unknown item counts before accepting an order total.
-- Expected result/shape: For sql-json-01 Exercise 5, display document_id, known_line_value, accepted_order_value, coverage_state ordered by document_id, one row per document_id. Accepted values are 13, 0, NULL, NULL; document 4 has known partial value 2 and incomplete coverage.
-- Verify: For sql-json-01 Exercise 5, compare each item contribution and unknown count with the displayed line values before checking the coverage CASE. Document 3 lacks its array, document 4 has an unknown quantity, and a partial SUM must not become a complete accepted amount.
-- Hint ladder, rung 1: Preserve outer document shape and explicit unknown counts before applying COALESCE.
SAVEPOINT exercise_5;

-- Write your value and coverage query here.
ROLLBACK TO SAVEPOINT exercise_5;

RELEASE SAVEPOINT exercise_5;

-- 6. [Extension] Add a document-level shipping fee exactly once after item aggregation.
-- Inputs: For sql-json-01 Exercise 6, use accepted child totals and one shipping_fee from each original document. Aggregate child rows to document grain before adding the parent amount.
-- Expected result/shape: For sql-json-01 Exercise 6, display document_id, accepted_total ordered by document_id as (1,17), (2,0), (3,NULL), (4,NULL), one row per document_id.
-- Verify: For sql-json-01 Exercise 6, assert the deliberately incorrect output value 21 for document 1 when its fee is repeated at item grain, then assert accepted output 17 charges the parent fee four exactly once.
-- Hint ladder, rung 1: Aggregate items first, then join to one parent row per document_id.
SAVEPOINT exercise_6;

-- Write your grain-safe total here.
ROLLBACK TO SAVEPOINT exercise_6;

RELEASE SAVEPOINT exercise_6;

ROLLBACK;
