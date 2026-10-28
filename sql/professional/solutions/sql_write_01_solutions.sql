-- SQL-WRITE-01: complete PostgreSQL 17 references and independent state assertions
\set ON_ERROR_STOP on
BEGIN;
DO $target$
BEGIN
  IF current_database() <> 'advanced_sql_training' OR current_setting('server_version_num')::integer < 170000 THEN
    RAISE EXCEPTION 'Use the disposable advanced_sql_training PostgreSQL 17 runtime';
  END IF;
END
$target$;

CREATE TEMP TABLE w17_practice_stock (
  sku text PRIMARY KEY,
  quantity integer NOT NULL CHECK (quantity >= 0),
  source_version integer NOT NULL CHECK (source_version > 0)
) ON COMMIT DROP;

INSERT INTO w17_practice_stock
VALUES
  ('A', 10, 1),
  ('B', 3, 1),
  ('Z', 5, 1);

CREATE TEMP TABLE w17_practice_feed (
  sku text,
  quantity integer,
  source_version integer
) ON COMMIT DROP;

INSERT INTO w17_practice_feed
VALUES
  ('A', 12, 2),
  ('B', 3, 1),
  ('C', 1, 1);

CREATE FUNCTION pg_temp.check_stock (expected jsonb, label text)
  RETURNS void
  LANGUAGE plpgsql
  AS $check$
DECLARE actual jsonb;
BEGIN
  SELECT jsonb_agg(to_jsonb(s) ORDER BY sku) INTO actual FROM w17_practice_stock AS s;
  IF actual IS DISTINCT FROM expected THEN RAISE EXCEPTION 'Stock contract failed: %; actual %',label,actual; END IF;
END
$check$
;
-- Exercises: complete executable references
-- 1. identity match determines candidates; action conditions choose changes.
SAVEPOINT exercise_1;

MERGE INTO w17_practice_stock AS t
  USING w17_practice_feed AS s ON t.sku = s.sku
  WHEN MATCHED AND s.source_version > t.source_version THEN
    UPDATE SET quantity = s.quantity, source_version = s.source_version
  WHEN NOT MATCHED BY SOURCE THEN
    DELETE
  WHEN NOT MATCHED BY TARGET THEN
    INSERT (sku, quantity, source_version) VALUES (s.sku, s.quantity, s.source_version) RETURNING
  merge_action () AS action, t.sku, t.quantity, t.source_version;

SELECT
  pg_temp.check_stock ('[{"sku":"A","quantity":12,"source_version":2},{"sku":"B","quantity":3,"source_version":1},{"sku":"C","quantity":1,"source_version":1}]', 'full snapshot A/C/Z changed; B unchanged');

ROLLBACK TO SAVEPOINT exercise_1;

RELEASE SAVEPOINT exercise_1;

-- 2. no source-missing deletion is permitted for partial events.
SAVEPOINT exercise_2;

MERGE INTO w17_practice_stock AS t
  USING ( VALUES ('A', 12, 2), ('C', 1, 1)) AS s (sku, quantity, source_version) ON t.sku = s.sku
  WHEN MATCHED AND s.source_version > t.source_version THEN
    UPDATE SET quantity = s.quantity, source_version = s.source_version
  WHEN NOT MATCHED THEN
    INSERT (sku, quantity, source_version) VALUES (s.sku, s.quantity, s.source_version);

SELECT
  sku,
  quantity,
  source_version
FROM
  w17_practice_stock
ORDER BY
  sku;

SELECT
  pg_temp.check_stock ('[{"sku":"A","quantity":12,"source_version":2},{"sku":"B","quantity":3,"source_version":1},{"sku":"C","quantity":1,"source_version":1},{"sku":"Z","quantity":5,"source_version":1}]', 'partial feed preserves B and Z');

ROLLBACK TO SAVEPOINT exercise_2;

RELEASE SAVEPOINT exercise_2;

-- 3. resolve one source version per key before touching the target.
SAVEPOINT exercise_3;

WITH ranked AS (
  SELECT
    sku,
    quantity,
    source_version,
    row_number() OVER (PARTITION BY sku ORDER BY source_version DESC) AS position
  FROM (
    VALUES ('A', 12, 2),
      ('A', 14, 3),
      ('C', 1, 1)) AS feed (sku, quantity, source_version)) MERGE INTO w17_practice_stock AS t
    USING (
      SELECT
        sku, quantity, source_version FROM
        ranked WHERE
        position = 1) AS s ON t.sku = s.sku
    WHEN MATCHED AND s.source_version > t.source_version THEN
      UPDATE SET quantity = s.quantity, source_version = s.source_version
    WHEN NOT MATCHED THEN
      INSERT (sku, quantity, source_version) VALUES (s.sku, s.quantity, s.source_version);

SELECT
  sku,
  quantity,
  source_version
FROM
  w17_practice_stock
ORDER BY
  sku;

SELECT
  pg_temp.check_stock ('[{"sku":"A","quantity":14,"source_version":3},{"sku":"B","quantity":3,"source_version":1},{"sku":"C","quantity":1,"source_version":1},{"sku":"Z","quantity":5,"source_version":1}]', 'greatest unique version per key');

ROLLBACK TO SAVEPOINT exercise_3;

RELEASE SAVEPOINT exercise_3;

-- 4. uniqueness selects the conflict target; WHERE gates stale updates.
SAVEPOINT exercise_4;

INSERT INTO w17_practice_stock AS t (sku, quantity, source_version)
VALUES
  ('A', 14, 3),
  ('B', 999, 1),
  ('D', 4, 1)
ON CONFLICT (sku)
  DO UPDATE SET
    quantity = excluded.quantity,
    source_version = excluded.source_version
  WHERE
    excluded.source_version > t.source_version
  RETURNING
    sku, quantity, source_version;

SELECT
  pg_temp.check_stock ('[{"sku":"A","quantity":14,"source_version":3},{"sku":"B","quantity":3,"source_version":1},{"sku":"D","quantity":4,"source_version":1},{"sku":"Z","quantity":5,"source_version":1}]', 'stale B skipped; only A and D returned');

ROLLBACK TO SAVEPOINT exercise_4;

RELEASE SAVEPOINT exercise_4;

-- 5. repeating the accepted complete snapshot produces no new changes.
SAVEPOINT exercise_5;

MERGE INTO w17_practice_stock AS t
  USING w17_practice_feed AS s ON t.sku = s.sku
  WHEN MATCHED AND s.source_version > t.source_version THEN
    UPDATE SET quantity = s.quantity, source_version = s.source_version
  WHEN NOT MATCHED BY SOURCE THEN
    DELETE
  WHEN NOT MATCHED THEN
    INSERT (sku, quantity, source_version) VALUES (s.sku, s.quantity, s.source_version);

DO $repeat$
DECLARE changed bigint;
BEGIN
 MERGE INTO w17_practice_stock AS t USING w17_practice_feed AS s ON t.sku=s.sku
 WHEN MATCHED AND s.source_version>t.source_version THEN UPDATE SET quantity=s.quantity,source_version=s.source_version
 WHEN NOT MATCHED BY SOURCE THEN DELETE
 WHEN NOT MATCHED THEN INSERT(sku,quantity,source_version) VALUES(s.sku,s.quantity,s.source_version);
 GET DIAGNOSTICS changed=ROW_COUNT;
 IF changed<>0 THEN RAISE EXCEPTION 'Repeated snapshot changed % rows',changed; END IF;
END
$repeat$;

SELECT
  pg_temp.check_stock ('[{"sku":"A","quantity":12,"source_version":2},{"sku":"B","quantity":3,"source_version":1},{"sku":"C","quantity":1,"source_version":1}]', 'repeat converged state');

ROLLBACK TO SAVEPOINT exercise_5;

RELEASE SAVEPOINT exercise_5;

-- 6. completeness is checked before any source-missing deletion.
SAVEPOINT exercise_6;

DO $completeness$
BEGIN
 BEGIN
  IF (SELECT count(*) FROM w17_practice_feed WHERE sku IN('A','C'))<>3 THEN
   RAISE EXCEPTION 'incomplete-snapshot';
  END IF;
  MERGE INTO w17_practice_stock AS t USING(SELECT * FROM w17_practice_feed WHERE sku IN('A','C')) AS s ON t.sku=s.sku
  WHEN NOT MATCHED BY SOURCE THEN DELETE;
  RAISE EXCEPTION 'Incomplete source was not refused';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM<>'incomplete-snapshot' THEN RAISE; END IF;
  RAISE NOTICE 'Expected completeness rejection occurred before MERGE';
 END;
END
$completeness$;

SELECT
  pg_temp.check_stock ('[{"sku":"A","quantity":10,"source_version":1},{"sku":"B","quantity":3,"source_version":1},{"sku":"Z","quantity":5,"source_version":1}]', 'incomplete snapshot preserved original target');

DO $complete$
BEGIN
 IF (SELECT count(*) FROM w17_practice_feed)<>3 THEN RAISE EXCEPTION 'incomplete-snapshot'; END IF;
END
$complete$;

MERGE INTO w17_practice_stock AS t
  USING w17_practice_feed AS s ON t.sku = s.sku
  WHEN MATCHED AND s.source_version > t.source_version THEN
    UPDATE SET quantity = s.quantity, source_version = s.source_version
  WHEN NOT MATCHED BY SOURCE THEN
    DELETE
  WHEN NOT MATCHED THEN
    INSERT (sku, quantity, source_version) VALUES (s.sku, s.quantity, s.source_version);

SELECT
  pg_temp.check_stock ('[{"sku":"A","quantity":12,"source_version":2},{"sku":"B","quantity":3,"source_version":1},{"sku":"C","quantity":1,"source_version":1}]', 'complete snapshot passes same gate');

ROLLBACK TO SAVEPOINT exercise_6;

RELEASE SAVEPOINT exercise_6;

ROLLBACK;
