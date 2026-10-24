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
--    Inputs: For sql-58 Exercise 1, read from `stg_customers_raw`, `customers`, and `country_map`. Build the answer toward `parse_additional_datetime_formats_safely_answer`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-58 Exercise 1, expected output: one row per `customer_id`. The final columns are `parse_additional_datetime_formats_safely_answer`.
--    Verify: For sql-58 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `parse_additional_datetime_formats_safely_answer` against `stg_customers_raw`, `customers`, and `country_map`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-58 Exercise 1, select `customer_id` from `stg_customers_raw`, `customers`, and `country_map` before adding derived columns.
-- 2. Add phone number and normalize it using regex; flag invalid formats.
--    Inputs: For sql-58 Exercise 2, read from `training.customers`. Build the answer toward `normalizevalidate_staged_phone_values_answer`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-58 Exercise 2, expected output: one row per `customer_id`. The final columns are `normalizevalidate_staged_phone_values_answer`.
--    Verify: For sql-58 Exercise 2, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `normalizevalidate_staged_phone_values_answer` against `training.customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-58 Exercise 2, select `customer_id` from `training.customers` before adding derived columns.
-- 3. Write a stored procedure that ingests stg_ rows, cleans, validates, and upserts, returning a DQ summary.
--    Inputs: For sql-58 Exercise 3, stage every source row with `source_row_number` and raw text/JSON evidence; derive normalized fields plus timestamp, phone, email, and country validity flags, then upsert exactly one validated winner per normalized email.
--    Expected result/shape: For sql-58 Exercise 3, expected output: the procedure CALL returns one row with `upserted_rows` and `invalid_rows` (3 and 1 for the seed), while the cleaned detail remains one row per staged source row with raw evidence, normalized fields, and all four validity decisions.
--    Verify: For sql-58 Exercise 3, require `staged_rows = accepted_rows + rejected_rows`, every accepted row has all validity flags true, every rejection preserves `source_row_number` and raw attributes, malformed JSON never aborts the batch, valid winners reconcile to customer upserts, and rerun reaches the same final state.
--    Hint ladder, rung 1: For sql-58 Exercise 3, run `normalized` one at a time. Record each CTE's row count and `country`, and `segment` uniqueness before the next stage uses it.
-- 4. Prediction: identify which source duplicates survive ON CONFLICT DO
--    NOTHING and explain why input order must not decide production outcomes.
--    Inputs: For sql-58 Exercise 4, rank only cleaned rows whose timestamp, phone, email, and country flags are all true; partition by normalized email and order by parsed creation time descending then `source_row_number` descending.
--    Expected result/shape: For sql-58 Exercise 4, expected output: exactly one valid winner per `normalized_email`, with the normalized email, source row identity, parsed timestamp, and `winner_rank = 1`, ordered by normalized email.
--    Verify: For sql-58 Exercise 4, assert every winner has all validity flags true, normalized emails are unique, an equal-timestamp duplicate chooses the higher `source_row_number`, an invalid newer duplicate never wins, and the winner set matches the rows used by the upsert.
--    Hint ladder, rung 1: For sql-58 Exercise 4, run `candidates` one at a time. Record each CTE's row count and `make_source_duplicate_winner_selection_determini` uniqueness before the next stage uses it.
-- 5. Construction: create accepted and rejected result sets with a reason code
--    for every rejected row; reconcile both counts to the staging count.
--    Inputs: For sql-58 Exercise 5, read from `cleaned_customer_ingest_solution`. Build the answer toward `outcome`, and `rows`; keep `outcome` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-58 Exercise 5, expected output: one row per `outcome`. The final columns are `outcome`, and `rows`. The final order is `outcome`.
--    Verify: For sql-58 Exercise 5, independently aggregate `cleaned_customer_ingest_solution` by `outcome`; require one output row for every distinct `outcome` tuple and compare `rows` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `rows` for the existing `outcome` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-58 Exercise 5, run `classified` one at a time. Record each CTE's row count and `outcome` uniqueness before the next stage uses it.
-- 6. Debugging: normalize email before deduplication so case-only variants do
--    not become two competing records.
--    Inputs: For sql-58 Exercise 6, read from `cleaned_customer_ingest_solution`. Build the answer toward `normalized_email`, and `candidate_rows`; keep `email` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-58 Exercise 6, expected output: one row per `email`. The final columns are `normalized_email`, and `candidate_rows`. The final order is `email`.
--    Verify: For sql-58 Exercise 6, independently aggregate `cleaned_customer_ingest_solution` by `email`; require one output row for every distinct `email` tuple and compare `candidate_rows` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `candidate_rows` for the existing `email` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-58 Exercise 6, confirm the groups are `email`; then check `email` before applying the row cap.
-- 7. Edge case: distinguish a missing country from an unrecognized country and
--    preserve the raw value for audit rather than coercing both to one default.
--    Inputs: For sql-58 Exercise 7, read from `stg_customer_ingest_solution`. Build the answer toward `raw_country`, `normalized_candidate`, and `country_status`; keep `raw_country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-58 Exercise 7, expected output: one row per `raw_country`. The final columns are `raw_country`, `normalized_candidate`, and `country_status`. The final order is `raw_country NULLS FIRST`.
--    Verify: For sql-58 Exercise 7, reselect the returned keys directly from the source; require unique `raw_country` where the expected grain is one row per key and confirm the projected `raw_country`, `normalized_candidate`, and `country_status` against `stg_customer_ingest_solution`. Add one source row with a new `raw_country`; verify the result gains exactly one row carrying that `raw_country` value.
--    Hint ladder, rung 1: For sql-58 Exercise 7, check `raw_country NULLS FIRST` before applying the row cap.
-- 8. Construction: make the staging load idempotent by assigning a source batch
--    ID and source row number, then reject repeated natural source records.
--    Inputs: For sql-58 Exercise 8, read from `staged_batch_identity`, and `stg_customer_ingest_solution`. Build the answer toward `email`; keep `email` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-58 Exercise 8, expected output: one row per `email`. The final columns are `email`.
--    Verify: For sql-58 Exercise 8, choose one complete partition from `staged_batch_identity`, and `stg_customer_ingest_solution`; hand-calculate its first, middle, and final window values for `row_count`, then verify output keys remain `email`. Add duplicate source candidates for `email`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
--    Hint ladder, rung 1: For sql-58 Exercise 8, inspect one window partition before projecting.
-- 9. Debugging: prevent a single malformed JSON value from aborting the whole
--    batch; preserve the raw text and emit an invalid_json reason code.
--    Inputs: For sql-58 Exercise 9, read from `stg_customer_ingest_solution`. Build the answer toward `email`, `raw_attributes`, and `json_status`; keep `email` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-58 Exercise 9, expected output: one row per `email`. The final columns are `email`, `raw_attributes`, and `json_status`. The final order is `email`.
--    Verify: For sql-58 Exercise 9, reselect the returned keys directly from the source; require unique `email` where the expected grain is one row per key and confirm the projected `email`, `raw_attributes`, and `json_status` against `stg_customer_ingest_solution`. Add one source row with a new `email`; verify the result gains exactly one row carrying that `email` value.
--    Hint ladder, rung 1: For sql-58 Exercise 9, check `email` before applying the row cap.
-- 10. Explanation: reconcile staged, accepted, rejected, inserted, and updated
--     counts, and state why each row must end in exactly one outcome.
--    Inputs: For sql-58 Exercise 10, read from `cleaned_customer_ingest_solution`, and `stg_customer_ingest_solution`. Build the answer toward `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows`; keep `staged_rows` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-58 Exercise 10, expected output: one row per `staged_rows`. The final columns are `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows`.
--    Verify: For sql-58 Exercise 10, reselect the returned keys directly from the source; require unique `staged_rows` where the expected grain is one row per key and confirm the projected `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows` against `cleaned_customer_ingest_solution`, and `stg_customer_ingest_solution`. Add one source row with a new `staged_rows`; verify the result gains exactly one row carrying that `staged_rows` value.
--    Hint ladder, rung 1: For sql-58 Exercise 10, run `classified` one at a time. Record each CTE's row count and `staged_rows` uniqueness before the next stage uses it.

ROLLBACK;
