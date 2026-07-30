-- Day 58: Final Capstone - Integrated Data Challenge (Part 1)
-- Focus: Real-world messy data, data quality fixes, staging, and normalization
BEGIN;
SET search_path TO training, public;

-- 1. Simulate messy incoming data (staging)
CREATE TEMP TABLE stg_customers_raw (
  full_name TEXT,
  email     TEXT,
  country   TEXT,
  segment   TEXT,
  created_at TEXT,
  attributes TEXT
);

INSERT INTO stg_customers_raw(full_name, email, country, segment, created_at, attributes)
VALUES
  ('  Customer 501  ', 'CUSTOMER501@EXAMPLE.COM ', ' us ', ' GOLD ', '2025/01/03 10:00', '{"channel":"Web","referrer":"SEO"}'),
  ('Customer 502', 'customer-502@example.com', 'GB', NULL, '03-01-2025', '{"channel":"mobile","referrer":"email"}'),
  ('Customer 503', 'invalid-email', 'DE', 'silver', '2025-01-05T12:34:56Z', '{"channel":"store"}');

-- 2. Clean and conform the staging data into canonical types
WITH cleaned AS (
  SELECT trim(full_name)                           AS full_name,
         lower(trim(email))                        AS email,
         upper(trim(country))                      AS country,
         nullif(trim(segment), '')                 AS segment,
         (
           -- attempt to parse multiple formats
           CASE
             WHEN created_at ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN created_at::timestamptz
             WHEN created_at ~ '^[0-9]{2}-[0-9]{2}-[0-9]{4}$' THEN to_timestamp(created_at, 'DD-MM-YYYY')
             WHEN created_at ~ '^\d{4}/\d{2}/\d{2}' THEN to_timestamp(created_at, 'YYYY/MM/DD HH24:MI')
             ELSE NULL
           END
         )                                          AS created_at,
         COALESCE(NULLIF(trim(attributes),''),'{}')::jsonb AS attributes
  FROM stg_customers_raw
), validated AS (
  SELECT *,
         (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$') AS email_valid,
         (country IN ('US','CA','GB','DE','FR','IN','AU','BR')) AS country_valid
  FROM cleaned
)
SELECT * FROM validated;

-- 3. Upsert valid rows into customers (demo only; rolled back)
--    Here we only insert valid emails and countries
INSERT INTO customers(full_name, email, country, segment, created_at, attributes)
SELECT v.full_name, v.email, v.country, v.segment, COALESCE(v.created_at, now()), v.attributes
FROM (
  WITH cleaned AS (
    SELECT trim(full_name) AS full_name,
           lower(trim(email)) AS email,
           upper(trim(country)) AS country,
           nullif(trim(segment),'') AS segment,
           CASE
             WHEN created_at ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN created_at::timestamptz
             WHEN created_at ~ '^[0-9]{2}-[0-9]{2}-[0-9]{4}$' THEN to_timestamp(created_at, 'DD-MM-YYYY')
             WHEN created_at ~ '^\d{4}/\d{2}/\d{2}' THEN to_timestamp(created_at, 'YYYY/MM/DD HH24:MI')
             ELSE NULL
           END AS created_at,
           COALESCE(NULLIF(trim(attributes),''),'{}')::jsonb AS attributes
    FROM stg_customers_raw
  )
  SELECT *,
         (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$') AS email_valid,
         (country IN ('US','CA','GB','DE','FR','IN','AU','BR')) AS country_valid
  FROM cleaned
) v
WHERE v.email_valid AND v.country_valid
ON CONFLICT (email) DO NOTHING;  -- avoid dup per our schema constraint

-- 4. Create a DQ report: invalid emails, invalid countries, null criticals
WITH dq AS (
  SELECT 
    SUM(CASE WHEN NOT (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$') THEN 1 ELSE 0 END) AS invalid_email,
    SUM(CASE WHEN NOT (upper(country) IN ('US','CA','GB','DE','FR','IN','AU','BR')) THEN 1 ELSE 0 END) AS invalid_country,
    SUM(CASE WHEN trim(full_name) IS NULL OR trim(full_name) = '' THEN 1 ELSE 0 END) AS invalid_name
  FROM stg_customers_raw
)
SELECT * FROM dq;

-- 5. Normalize country names (demo mapping table)
CREATE TEMP TABLE country_map (code TEXT PRIMARY KEY, normalized TEXT NOT NULL);
INSERT INTO country_map VALUES
  ('US','US'),(' U S ','US'),('USA','US'),('CA','CA'),('GB','GB'),('DE','DE'),('FR','FR'),('IN','IN'),('AU','AU'),('BR','BR');

SELECT src.country AS raw, COALESCE(cm.normalized, upper(trim(src.country))) AS normalized
FROM stg_customers_raw src
LEFT JOIN country_map cm ON cm.code = src.country;

-- Exercises
-- 1. Extend the parser to handle additional datetime formats.
-- 2. Add phone number and normalize it using regex; flag invalid formats.
-- 3. Write a stored procedure that ingests stg_ rows, cleans, validates, and upserts, returning a DQ summary.
-- 4. Prediction: identify which source duplicates survive ON CONFLICT DO
--    NOTHING and explain why input order must not decide production outcomes.
-- 5. Construction: create accepted and rejected result sets with a reason code
--    for every rejected row; reconcile both counts to the staging count.
-- 6. Debugging: normalize email before deduplication so case-only variants do
--    not become two competing records.
-- 7. Edge case: distinguish a missing country from an unrecognized country and
--    preserve the raw value for audit rather than coercing both to one default.
-- 8. Construction: make the staging load idempotent by assigning a source batch
--    ID and source row number, then reject repeated natural source records.
-- 9. Debugging: prevent a single malformed JSON value from aborting the whole
--    batch; preserve the raw text and emit an invalid_json reason code.
-- 10. Explanation: reconcile staged, accepted, rejected, inserted, and updated
--     counts, and state why each row must end in exactly one outcome.

ROLLBACK;
