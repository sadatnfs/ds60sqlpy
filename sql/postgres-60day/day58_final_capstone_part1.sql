-- Day 58: Final Capstone - Integrated Data Challenge (Part 1)
-- BEGINNER WORKFLOW - sql-58: Final Capstone Part 1
-- Guide: sql/postgres-60day/companion-guides/day58_final_capstone_part1.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-58.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
  email TEXT,
  country TEXT,
  segment TEXT,
  created_at TEXT,
  attributes TEXT
);

INSERT INTO stg_customers_raw (full_name, email, country, segment, created_at, attributes)
VALUES
  ('  Customer 501  ', 'CUSTOMER501@EXAMPLE.COM ', ' us ', ' GOLD ', '2025/01/03 10:00', '{"channel":"Web","referrer":"SEO"}'),
  ('Customer 502', 'customer-502@example.com', 'GB', NULL, '03-01-2025', '{"channel":"mobile","referrer":"email"}'),
  ('Customer 503', 'invalid-email', 'DE', 'silver', '2025-01-05T12:34:56Z', '{"channel":"store"}');

-- 2. Clean and conform the staging data into canonical types
WITH cleaned AS (
  SELECT
    trim(full_name) AS full_name,
    lower(trim(email)) AS email,
    upper(trim(country)) AS country,
    nullif (trim(segment), '') AS segment,
    (
      -- attempt to parse multiple formats
      CASE WHEN created_at ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN
        created_at::timestamptz
      WHEN created_at ~ '^[0-9]{2}-[0-9]{2}-[0-9]{4}$' THEN
        to_timestamp(created_at, 'DD-MM-YYYY')
      WHEN created_at ~ '^\d{4}/\d{2}/\d{2}' THEN
        to_timestamp(created_at, 'YYYY/MM/DD HH24:MI')
      ELSE
        NULL
      END) AS created_at,
    COALESCE(NULLIF (trim(attributes), ''), '{}')::jsonb AS attributes
  FROM
    stg_customers_raw
),
validated AS (
  SELECT
    *,
    (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$') AS email_valid,
    (country IN ('US', 'CA', 'GB', 'DE', 'FR', 'IN', 'AU', 'BR')) AS country_valid
  FROM
    cleaned
)
SELECT
  *
FROM
  validated;

-- 3. Upsert valid rows into customers (demo only; rolled back)
--    Here we only insert valid emails and countries
INSERT INTO customers (full_name, email, country, segment, created_at, attributes)
SELECT
  v.full_name,
  v.email,
  v.country,
  v.segment,
  COALESCE(v.created_at, now()),
  v.attributes
FROM ( WITH cleaned AS (
    SELECT
      trim(full_name) AS full_name,
      lower(trim(email)) AS email,
      upper(trim(country)) AS country,
      nullif (trim(segment), '') AS segment,
      CASE WHEN created_at ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN
        created_at::timestamptz
      WHEN created_at ~ '^[0-9]{2}-[0-9]{2}-[0-9]{4}$' THEN
        to_timestamp(created_at, 'DD-MM-YYYY')
      WHEN created_at ~ '^\d{4}/\d{2}/\d{2}' THEN
        to_timestamp(created_at, 'YYYY/MM/DD HH24:MI')
      ELSE
        NULL
      END AS created_at,
      COALESCE(NULLIF (trim(attributes), ''), '{}')::jsonb AS attributes
    FROM
      stg_customers_raw
)
    SELECT
      *,
      (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$') AS email_valid,
      (country IN ('US', 'CA', 'GB', 'DE', 'FR', 'IN', 'AU', 'BR')) AS country_valid
    FROM
      cleaned) v
WHERE
  v.email_valid
  AND v.country_valid
ON CONFLICT (email)
  DO NOTHING;

-- avoid dup per our schema constraint
-- 4. Create a DQ report: invalid emails, invalid countries, null criticals
WITH dq AS (
  SELECT
    SUM(
      CASE WHEN NOT (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$') THEN
        1
      ELSE
        0
      END) AS invalid_email,
    SUM(
      CASE WHEN NOT (upper(country) IN ('US', 'CA', 'GB', 'DE', 'FR', 'IN', 'AU', 'BR')) THEN
        1
      ELSE
        0
      END) AS invalid_country,
    SUM(
      CASE WHEN trim(full_name) IS NULL
        OR trim(full_name) = '' THEN
        1
      ELSE
        0
      END) AS invalid_name
  FROM
    stg_customers_raw
)
SELECT
  *
FROM
  dq;

-- 5. Normalize country names (demo mapping table)
CREATE TEMP TABLE country_map (
  code TEXT PRIMARY KEY,
  normalized TEXT NOT NULL
);

INSERT INTO country_map
VALUES
  ('US', 'US'),
  (' U S ', 'US'),
  ('USA', 'US'),
  ('CA', 'CA'),
  ('GB', 'GB'),
  ('DE', 'DE'),
  ('FR', 'FR'),
  ('IN', 'IN'),
  ('AU', 'AU'),
  ('BR', 'BR');

SELECT
  src.country AS raw,
  COALESCE(cm.normalized, upper(trim(src.country))) AS normalized
FROM
  stg_customers_raw src
  LEFT JOIN country_map cm ON cm.code = src.country;

-- Exercises
-- 1. Extend the parser to handle additional datetime formats.
--    Inputs: For sql-58 Exercise 1, parse the four staged `created_at` strings in `stg_customer_ingest_solution` with the temporary function `pg_temp.try_parse_customer_timestamp`, which accepts `YYYY/MM/DD HH24:MI`, `MM/DD/YYYY HH24:MI`, `DD-Mon-YYYY HH24:MI`, and ISO `YYYY-MM-DD HH24:MI` text and returns NULL for anything else.
--    Expected result/shape: For sql-58 Exercise 1, expected output: in `cleaned_customer_ingest_solution`, `created_at` is 2026-01-03 10:00, 2026-01-15 08:30, and 2026-01-15 12:00 UTC for the first three staged rows and NULL for `not-a-date`.
--    Verify: For sql-58 Exercise 1, call the function directly with the session time zone set to UTC on `'2026/01/03 10:00'`, `'01/15/2026 08:30'`, `'15-Jan-2026 12:00'`, and `'not-a-date'` and expect the three timestamps above and NULL; an impossible date such as `'2026/02/30 10:00'` must also return NULL instead of rolling over into March.
--    Hint ladder, rung 1: For sql-58 Exercise 1, call `pg_temp.try_parse_customer_timestamp` on each staged string by itself before you run the cleaning step.
-- 2. Add phone number and normalize it using regex; flag invalid formats.
--    Inputs: For sql-58 Exercise 2, strip every non-digit from the staged `phone` with `regexp_replace(phone, '[^0-9]', '', 'g')` and flag the result valid when it has 10 to 15 digits (`phone_digits ~ '^[0-9]{10,15}$'`).
--    Expected result/shape: For sql-58 Exercise 2, expected output: `phone_digits` 4155550101, 442079460958, 0301234567, and 123, with `phone_valid` true, true, true, and false, stored in `cleaned_customer_ingest_solution`.
--    Verify: For sql-58 Exercise 2, confirm that `SELECT phone_digits, phone_valid FROM cleaned_customer_ingest_solution ORDER BY source_row_number` returns those four pairs and that only the `123` row is invalid; then test `'+1 (415) 555-0101 ext. 9'`, which becomes 141555501019 and still passes the length rule, so an extension needs its own handling.
--    Hint ladder, rung 1: For sql-58 Exercise 2, run the `regexp_replace` on the four staged phone strings in a plain `SELECT` before you add the validity flag.
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
--    Inputs: For sql-58 Exercise 6, group `cleaned_customer_ingest_solution`, whose `email` is already `lower(trim(...))`, by that normalized `email` and count the candidate rows per address.
--    Expected result/shape: For sql-58 Exercise 6, expected output: 4 rows, one per normalized `email`, each with `candidate_rows` 1 on the staged data. The final columns are `normalized_email` and `candidate_rows`. The final order is `email`.
--    Verify: For sql-58 Exercise 6, confirm that the staged `CUSTOMER601@EXAMPLE.COM ` (upper case with a trailing space) appears as `customer601@example.com`; on `VALUES ('A@x.com'), ('a@x.com ')`, `COUNT(DISTINCT e)` is 2 but `COUNT(DISTINCT lower(trim(e)))` is 1, which is the duplicate that normalization must catch before deduplication.
--    Hint ladder, rung 1: For sql-58 Exercise 6, compare `COUNT(DISTINCT email)` with `COUNT(DISTINCT lower(trim(email)))` on the staging table before you group the cleaned rows.
-- 7. Edge case: distinguish a missing country from an unrecognized country and
--    preserve the raw value for audit rather than coercing both to one default.
--    Inputs: For sql-58 Exercise 7, read from `stg_customer_ingest_solution`. Build the answer toward `raw_country`, `normalized_candidate`, and `country_status`; keep `raw_country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-58 Exercise 7, expected output: one row per `raw_country`. The final columns are `raw_country`, `normalized_candidate`, and `country_status`. The final order is `raw_country NULLS FIRST`.
--    Verify: For sql-58 Exercise 7, reselect the returned keys directly from the source; require unique `raw_country` where the expected grain is one row per key and confirm the projected `raw_country`, `normalized_candidate`, and `country_status` against `stg_customer_ingest_solution`. Add one source row with a new `raw_country`; verify the result gains exactly one row carrying that `raw_country` value.
--    Hint ladder, rung 1: For sql-58 Exercise 7, check `raw_country NULLS FIRST` before applying the row cap.
-- 8. Construction: make the staging load idempotent by assigning a source batch
--    ID and source row number, then reject repeated natural source records.
--    Inputs: For sql-58 Exercise 8, load the four staged rows into `staged_batch_identity`, keyed by (`batch_id`, `source_row_number`), twice with `INSERT ... ON CONFLICT (batch_id, source_row_number) DO NOTHING`, then count the stored rows.
--    Expected result/shape: For sql-58 Exercise 8, expected output: `INSERT 0 4` for the first load, `INSERT 0 0` for the replay, and one row with `replay_safe_rows` 4. The final columns are `replay_safe_rows`.
--    Verify: For sql-58 Exercise 8, confirm that the replay inserts nothing and that `SELECT COUNT(*) FROM staged_batch_identity` equals `SELECT COUNT(*) FROM stg_customer_ingest_solution` (4); load the same rows under a new `batch_id` and expect 8 rows, because the key identifies a batch and a source row, not a customer.
--    Hint ladder, rung 1: For sql-58 Exercise 8, run the `INSERT ... ON CONFLICT DO NOTHING` twice and read both command tags before you count.
-- 9. Debugging: prevent a single malformed JSON value from aborting the whole
--    batch; preserve the raw text and emit an invalid_json reason code.
--    Inputs: For sql-58 Exercise 9, read from `stg_customer_ingest_solution`. Build the answer toward `email`, `raw_attributes`, and `json_status`; keep `email` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-58 Exercise 9, expected output: one row per `email`. The final columns are `email`, `raw_attributes`, and `json_status`. The final order is `email`.
--    Verify: For sql-58 Exercise 9, reselect the returned keys directly from the source; require unique `email` where the expected grain is one row per key and confirm the projected `email`, `raw_attributes`, and `json_status` against `stg_customer_ingest_solution`. Add one source row with a new `email`; verify the result gains exactly one row carrying that `email` value.
--    Hint ladder, rung 1: For sql-58 Exercise 9, check `email` before applying the row cap.
-- 10. Explanation: reconcile staged, accepted, rejected, inserted, and updated
--     counts, and state why each row must end in exactly one outcome.
--    Inputs: For sql-58 Exercise 10, classify every row of `cleaned_customer_ingest_solution` as accepted only when its email, country, phone, JSON, timestamp, and name checks all pass, then count staged, accepted, and rejected rows and their reconciled sum.
--    Expected result/shape: For sql-58 Exercise 10, expected output: one row with `staged_rows` 4, `accepted_rows` 3, `rejected_rows` 1, and `reconciled_rows` 4. The final columns are `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows`.
--    Verify: For sql-58 Exercise 10, confirm `accepted_rows + rejected_rows = staged_rows` and that `staged_rows` equals `SELECT COUNT(*) FROM stg_customer_ingest_solution`; the rejected row is `Customer bad`, which fails the email, country, phone, JSON, and timestamp checks at once but is counted once.
--    Hint ladder, rung 1: For sql-58 Exercise 10, run `classified` alone and count the rows where `accepted` is true and false before you build the summary.
ROLLBACK;
