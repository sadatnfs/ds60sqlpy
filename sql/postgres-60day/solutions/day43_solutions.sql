-- Day 43 solutions: logical backup and recovery patterns
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

ROLLBACK;
