-- Day 58: Final Capstone - Integrated Data Challenge (Part 1)
-- BEGINNER WORKFLOW — sql-58: Final Capstone Part1
-- Guide: sql/postgres-60day/companion-guides/day58_final_capstone_part1.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-58/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: stg_customers_raw, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
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
--    Inputs: Use only the declared lesson objects (stg_customers_raw, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Add phone number and normalize it using regex; flag invalid formats.
--    Inputs: Use only the declared lesson objects (stg_customers_raw, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. Write a stored procedure that ingests stg_ rows, cleans, validates, and upserts, returning a DQ summary.
--    Inputs: Use only the declared lesson objects (stg_customers_raw, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 4. Prediction: identify which source duplicates survive ON CONFLICT DO
--    NOTHING and explain why input order must not decide production outcomes.
--    Inputs: Use only the declared lesson objects (stg_customers_raw, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 5. Construction: create accepted and rejected result sets with a reason code
--    for every rejected row; reconcile both counts to the staging count.
--    Inputs: Use only the declared lesson objects (stg_customers_raw, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 6. Debugging: normalize email before deduplication so case-only variants do
--    not become two competing records.
--    Inputs: Use only the declared lesson objects (stg_customers_raw, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 7. Edge case: distinguish a missing country from an unrecognized country and
--    preserve the raw value for audit rather than coercing both to one default.
--    Inputs: Use only the declared lesson objects (stg_customers_raw, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 8. Construction: make the staging load idempotent by assigning a source batch
--    ID and source row number, then reject repeated natural source records.
--    Inputs: Use only the declared lesson objects (stg_customers_raw, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 9. Debugging: prevent a single malformed JSON value from aborting the whole
--    batch; preserve the raw text and emit an invalid_json reason code.
--    Inputs: Use only the declared lesson objects (stg_customers_raw, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Show the incorrect/failing behavior and then a corrected result with the violated invariant, keys, and row grain visible.
--    Verify: Keep a minimal failing case and reconcile corrected counts/totals against an independent control rather than checking syntax alone.
--    Hint ladder, rung 1: Reproduce the smallest wrong result first, then inspect the earliest relation or clause where its grain/count stops matching the contract.
-- 10. Explanation: reconcile staged, accepted, rejected, inserted, and updated
--     counts, and state why each row must end in exactly one outcome.
--    Inputs: Use only the declared lesson objects (stg_customers_raw, customers) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
