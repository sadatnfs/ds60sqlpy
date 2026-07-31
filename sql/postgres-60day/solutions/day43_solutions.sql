-- Day 43 solutions: logical backup and recovery patterns
-- SOLUTION READING MAP — sql-43: Backup Recovery
-- Explanation: sql/postgres-60day/solutions/day43_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day43_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
BEGIN;
SET search_path TO training, public;

-- Exercise 1: emit a filtered CSV through the client connection.
-- In interactive psql, replace COPY ... TO STDOUT with:
-- \copy (SELECT * FROM training.customers WHERE country='US')
--   TO 'customers_us.csv' WITH (FORMAT csv, HEADER true)
COPY (
  SELECT customer_id, full_name, email, country, created_at, segment, attributes
  FROM customers
  WHERE country = 'US'
  ORDER BY customer_id
) TO STDOUT WITH (FORMAT csv, HEADER true);

-- A temporary staging table models the result of a later \copy ... FROM file.
CREATE TEMP TABLE customers_restore_stage AS
SELECT full_name, email, country, created_at, segment, attributes
FROM customers
WHERE country = 'US';

UPDATE customers_restore_stage
SET full_name = full_name || ' [restored]'
WHERE email = 'customer1@example.com';

-- Exercise 2: idempotent restore keyed by the schema's unique email.
INSERT INTO customers(full_name, email, country, created_at, segment, attributes)
SELECT full_name, email, country, created_at, segment, attributes
FROM customers_restore_stage
ON CONFLICT (email) DO UPDATE
SET full_name = EXCLUDED.full_name,
    country = EXCLUDED.country,
    segment = EXCLUDED.segment,
    attributes = EXCLUDED.attributes;

SELECT COUNT(*) AS staged_rows FROM customers_restore_stage;

-- Exercise 3: COPY above writes from the database backend to STDOUT; psql
-- \copy consumes that stream on the client. The latter is normally appropriate
-- when the learner controls the client filesystem but not the server host.

-- Exercise 4: a manifest makes export scope auditable. clock_timestamp is the
-- observation time; row/key fields are deterministic for this snapshot.
SELECT 'training.customers' AS table_name,
       COUNT(*) AS row_count,
       MIN(customer_id) AS min_key,
       MAX(customer_id) AS max_key,
       clock_timestamp() AS observed_at
FROM customers;

-- Exercise 5: ROW_NUMBER chooses one repeatable winner per normalized email.
WITH staged_duplicates AS (
  SELECT *, lower(trim(email)) AS normalized_email,
         ROW_NUMBER() OVER (
           PARTITION BY lower(trim(email))
           ORDER BY created_at DESC, full_name, email
         ) AS winner_rank
  FROM customers_restore_stage
)
SELECT full_name, email, country
FROM staged_duplicates
WHERE winner_rank = 1
ORDER BY email;

-- Exercise 6: IS DISTINCT FROM is NULL-safe and returns only actual column
-- differences between stage and target.
SELECT s.email,
       s.full_name AS staged_name,
       c.full_name AS restored_name
FROM customers_restore_stage s
JOIN customers c USING (email)
WHERE s.full_name IS DISTINCT FROM c.full_name
   OR s.country IS DISTINCT FROM c.country
   OR s.segment IS DISTINCT FROM c.segment
ORDER BY s.email;

ROLLBACK;
