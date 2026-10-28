-- SQL-QUALITY-01: executable solutions and fail-fast checks
BEGIN;
DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
END
$course_target$;

SET LOCAL TIME ZONE 'UTC';

SET LOCAL statement_timeout = '15s';

CREATE TEMP TABLE quality_source (
  invoice_id integer PRIMARY KEY,
  amount numeric
) ON COMMIT DROP;

CREATE TEMP TABLE quality_target (
  invoice_id integer PRIMARY KEY,
  amount numeric
) ON COMMIT DROP;

INSERT INTO quality_source
VALUES
  (1, 100),
  (2, 50),
  (3, 0),
  (4, 80);

INSERT INTO quality_target
VALUES
  (1, 100),
  (2, 40),
  (3, 0),
  (5, 90);

CREATE TEMP TABLE quality_sent (
  invoice_id integer,
  amount numeric
) ON COMMIT DROP;

CREATE TEMP TABLE quality_received (
  invoice_id integer,
  amount numeric
) ON COMMIT DROP;

INSERT INTO quality_sent
VALUES
  (1, 100),
  (1, 100),
  (2, 50);

INSERT INTO quality_received
VALUES
  (1, 100),
  (2, 50),
  (2, 50);

CREATE TEMP TABLE quality_orders (
  order_id integer PRIMARY KEY
) ON COMMIT DROP;

CREATE TEMP TABLE quality_lines (
  line_id integer PRIMARY KEY,
  order_id integer,
  amount numeric
) ON COMMIT DROP;

CREATE TEMP TABLE quality_attempts (
  attempt_id integer PRIMARY KEY,
  order_id integer,
  amount numeric
) ON COMMIT DROP;

INSERT INTO quality_orders
VALUES
  (1),
  (2),
  (3);

INSERT INTO quality_lines
VALUES
  (11, 1, 60),
  (12, 1, 40),
  (21, 2, 50);

INSERT INTO quality_attempts
VALUES
  (101, 1, 100),
  (102, 1, 100),
  (201, 2, 50);

CREATE FUNCTION pg_temp.assert_true (ok boolean, message text)
  RETURNS void
  LANGUAGE plpgsql
  AS $assert$
BEGIN
  IF ok IS DISTINCT FROM true THEN
    RAISE EXCEPTION 'Contract failed: %', message;
  END IF;
END
$assert$
;
-- Exercises: one isolated answer and verification per prompt.
-- 1. Disprove summary equality
SAVEPOINT exercise_1;

SELECT
  'source' AS origin,
  count(*) AS row_count,
  sum(amount) AS amount_total
FROM
  quality_source
UNION ALL
SELECT
  'target',
  count(*),
  sum(amount)
FROM
  quality_target
ORDER BY
  origin;

CREATE TEMP TABLE solution_answer_1 ON COMMIT DROP AS
SELECT
  'source' AS origin, count(*) AS row_count, sum(amount) AS amount_total
FROM
  quality_source
UNION ALL
SELECT
  'target', count(*), sum(amount)
FROM
  quality_target
ORDER BY
  origin;

SELECT
  pg_temp.assert_true ((
    SELECT
      count(*) = 2
    AND min(row_count) = 4
    AND max(row_count) = 4
    AND min(amount_total) = 230
    AND max(amount_total) = 230 FROM solution_answer_1), 'sql-quality-01 exercise 1');

ROLLBACK TO SAVEPOINT exercise_1;

RELEASE SAVEPOINT exercise_1;

-- 2. Report keyed mismatches in both directions
SAVEPOINT exercise_2;

SELECT
  COALESCE(s.invoice_id, t.invoice_id) AS invoice_id,
  s.amount AS source_amount,
  t.amount AS target_amount,
  CASE WHEN s.invoice_id IS NULL THEN
    'missing_source'
  WHEN t.invoice_id IS NULL THEN
    'missing_target'
  ELSE
    'changed'
  END AS difference_kind
FROM
  quality_source AS s
  FULL OUTER JOIN quality_target AS t USING (invoice_id)
WHERE
  s.invoice_id IS NULL
  OR t.invoice_id IS NULL
  OR s.amount IS DISTINCT FROM t.amount
ORDER BY
  invoice_id;

CREATE TEMP TABLE solution_answer_2 ON COMMIT DROP AS
SELECT
  COALESCE(s.invoice_id, t.invoice_id) AS invoice_id, s.amount AS source_amount, t.amount AS target_amount, CASE WHEN s.invoice_id IS NULL THEN
    'missing_source'
  WHEN t.invoice_id IS NULL THEN
    'missing_target'
  ELSE
    'changed'
  END AS difference_kind
FROM
  quality_source AS s
  FULL OUTER JOIN quality_target AS t USING (invoice_id)
WHERE
  s.invoice_id IS NULL
  OR t.invoice_id IS NULL
  OR s.amount IS DISTINCT FROM t.amount
ORDER BY
  invoice_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(invoice_id ORDER BY invoice_id) = ARRAY[2, 4, 5]
    AND array_agg(difference_kind ORDER BY invoice_id) = ARRAY['changed', 'missing_target', 'missing_source'] FROM solution_answer_2), 'sql-quality-01 exercise 2');

ROLLBACK TO SAVEPOINT exercise_2;

RELEASE SAVEPOINT exercise_2;

-- 3. Preserve duplicate multiplicity
SAVEPOINT exercise_3;

SELECT
  'sent_only' AS direction,
  invoice_id,
  amount
FROM (
  SELECT
    invoice_id,
    amount
  FROM
    quality_sent
  EXCEPT ALL
  SELECT
    invoice_id,
    amount
  FROM
    quality_received) AS missing
UNION ALL
SELECT
  'received_only',
  invoice_id,
  amount
FROM (
  SELECT
    invoice_id,
    amount
  FROM
    quality_received
  EXCEPT ALL
  SELECT
    invoice_id,
    amount
  FROM
    quality_sent) AS extra
ORDER BY
  direction,
  invoice_id,
  amount;

CREATE TEMP TABLE solution_answer_3 ON COMMIT DROP AS
SELECT
  'sent_only' AS direction, invoice_id, amount
FROM (
  SELECT
    invoice_id, amount
  FROM
    quality_sent
  EXCEPT ALL
  SELECT
    invoice_id, amount
  FROM
    quality_received) AS missing
UNION ALL
SELECT
  'received_only', invoice_id, amount
FROM (
  SELECT
    invoice_id, amount
  FROM
    quality_received
  EXCEPT ALL
  SELECT
    invoice_id, amount
  FROM
    quality_sent) AS extra
ORDER BY
  direction, invoice_id, amount;

SELECT
  pg_temp.assert_true ((
    SELECT
      count(*)
    FROM solution_answer_3) = 2
  AND (
    SELECT
      count(*)
    FROM solution_answer_3
    WHERE
      direction = 'sent_only'
      AND invoice_id = 1
      AND amount = 100) = 1
    AND (
      SELECT
        count(*)
      FROM solution_answer_3
    WHERE
      direction = 'received_only'
      AND invoice_id = 2
      AND amount = 50) = 1, 'sql-quality-01 exercise 3');

ROLLBACK TO SAVEPOINT exercise_3;

RELEASE SAVEPOINT exercise_3;

-- 4. Repair independent-child fanout
SAVEPOINT exercise_4;

WITH lines AS (
  SELECT
    order_id,
    sum(amount) AS line_total
  FROM
    quality_lines
  GROUP BY
    order_id
),
attempts AS (
  SELECT
    order_id,
    sum(amount) AS attempted_total
  FROM
    quality_attempts
  GROUP BY
    order_id
)
SELECT
  o.order_id,
  COALESCE(l.line_total, 0) AS line_total,
  COALESCE(a.attempted_total, 0) AS attempted_total
FROM
  quality_orders AS o
  LEFT JOIN lines AS l USING (order_id)
  LEFT JOIN attempts AS a USING (order_id)
ORDER BY
  o.order_id;

CREATE TEMP TABLE solution_answer_4 ON COMMIT DROP AS
WITH lines AS (
  SELECT
    order_id,
    sum(amount) AS line_total
  FROM
    quality_lines
  GROUP BY
    order_id
),
attempts AS (
  SELECT
    order_id,
    sum(amount) AS attempted_total
  FROM
    quality_attempts
  GROUP BY
    order_id
)
SELECT
  o.order_id, COALESCE(l.line_total, 0) AS line_total, COALESCE(a.attempted_total, 0) AS attempted_total
FROM
  quality_orders AS o
  LEFT JOIN lines AS l USING (order_id)
  LEFT JOIN attempts AS a USING (order_id)
ORDER BY
  o.order_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      array_agg(order_id ORDER BY order_id) = ARRAY[1, 2, 3]
    AND array_agg(line_total ORDER BY order_id) = ARRAY[100, 50, 0]::numeric[]
    AND array_agg(attempted_total ORDER BY order_id) = ARRAY[200, 50, 0]::numeric[] FROM solution_answer_4), 'sql-quality-01 exercise 4');

ROLLBACK TO SAVEPOINT exercise_4;

RELEASE SAVEPOINT exercise_4;

-- 5. Detect a missingness transition
SAVEPOINT exercise_5;

WITH s (
  invoice_id,
  amount
) AS (
  VALUES (6, NULL::numeric)
),
t (
  invoice_id, amount
) AS (
  VALUES (6, 0::numeric))
SELECT
  s.invoice_id,
  s.amount AS source_amount,
  t.amount AS target_amount
FROM
  s
  JOIN t USING (invoice_id)
WHERE
  s.amount IS DISTINCT FROM t.amount
ORDER BY
  s.invoice_id;

CREATE TEMP TABLE solution_answer_5 ON COMMIT DROP AS
WITH s (
  invoice_id,
  amount
) AS (
  VALUES (6, NULL::numeric)
),
t (
  invoice_id, amount
) AS (
  VALUES (6, 0::numeric))
SELECT
  s.invoice_id, s.amount AS source_amount, t.amount AS target_amount
FROM
  s
  JOIN t USING (invoice_id)
WHERE
  s.amount IS DISTINCT FROM t.amount
ORDER BY
  s.invoice_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      count(*) = 1
    AND min(invoice_id) = 6
    AND bool_and(source_amount IS NULL
      AND target_amount = 0)
    FROM solution_answer_5), 'sql-quality-01 exercise 5');

ROLLBACK TO SAVEPOINT exercise_5;

RELEASE SAVEPOINT exercise_5;

-- 6. Gate a keyed comparison on valid identity
SAVEPOINT exercise_6;

SELECT
  invoice_id,
  count(*) AS occurrences
FROM
  quality_sent
GROUP BY
  invoice_id
HAVING
  count(*) > 1
ORDER BY
  invoice_id;

CREATE TEMP TABLE solution_answer_6 ON COMMIT DROP AS
SELECT
  invoice_id, count(*) AS occurrences
FROM
  quality_sent
GROUP BY
  invoice_id
HAVING
  count(*) > 1
ORDER BY
  invoice_id;

SELECT
  pg_temp.assert_true ((
    SELECT
      count(*) = 1
    AND min(invoice_id) = 1
    AND min(occurrences) = 2 FROM solution_answer_6), 'sql-quality-01 exercise 6');

ROLLBACK TO SAVEPOINT exercise_6;

RELEASE SAVEPOINT exercise_6;

ROLLBACK;
