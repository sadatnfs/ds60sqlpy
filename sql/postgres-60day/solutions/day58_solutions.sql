-- Day 58 solutions: robust staging, normalization, and ingestion
-- SOLUTION READING MAP — sql-58: Final Capstone Part1
-- Explanation: sql/postgres-60day/solutions/day58_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/solutions/day58_solutions.sql
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

CREATE TEMP TABLE stg_customer_ingest_solution (
  source_row_number bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name text,
  email text,
  country text,
  segment text,
  created_at text,
  phone text,
  attributes text
);

INSERT INTO stg_customer_ingest_solution(
  full_name, email, country, segment, created_at, phone, attributes
)
VALUES
  (' Customer 601 ', 'CUSTOMER601@EXAMPLE.COM ', 'USA', 'gold',
   '2026/01/03 10:00', '(415) 555-0101', '{"channel":"web"}'),
  ('Customer 602', 'customer602@example.com', 'GB', 'silver',
   '01/15/2026 08:30', '+44 20 7946 0958', '{"channel":"mobile"}'),
  ('Customer 603', 'customer603@example.com', 'DE', NULL,
   '15-Jan-2026 12:00', '030-1234567', '{"channel":"store"}'),
  ('Customer bad', 'not-an-email', 'XX', 'bronze',
   'not-a-date', '123', 'not-json');

CREATE TEMP TABLE cleaned_customer_ingest_solution (
  source_row_number bigint PRIMARY KEY,
  full_name text,
  email text,
  country text,
  segment text,
  created_at timestamptz,
  phone_digits text,
  phone_valid boolean,
  email_valid boolean,
  country_valid boolean,
  raw_attributes text,
  attributes jsonb,
  json_valid boolean
) ON COMMIT DROP;

-- Parse only the supported formats, in a declared source time zone, and turn
-- malformed-but-regex-shaped input into NULL rather than aborting the batch.
SET LOCAL TIME ZONE 'UTC';
CREATE OR REPLACE FUNCTION pg_temp.try_parse_customer_timestamp(raw_value text)
RETURNS timestamptz
LANGUAGE plpgsql
-- Parsing text as timestamptz depends on session time-zone/date settings even
-- though this lesson pins UTC above. STABLE is the honest volatility promise;
-- IMMUTABLE would let PostgreSQL cache a value across changed settings.
STABLE
AS $function$
DECLARE
  parsed_value timestamptz;
BEGIN
  IF raw_value ~ '^[0-9]{4}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}$' THEN
    parsed_value := to_timestamp(raw_value, 'FXYYYY/MM/DD HH24:MI');
    IF to_char(parsed_value AT TIME ZONE 'UTC', 'YYYY/MM/DD HH24:MI') <> raw_value THEN
      RETURN NULL;
    END IF;
  ELSIF raw_value ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4} [0-9]{2}:[0-9]{2}$' THEN
    parsed_value := to_timestamp(raw_value, 'FXMM/DD/YYYY HH24:MI');
    IF to_char(parsed_value AT TIME ZONE 'UTC', 'MM/DD/YYYY HH24:MI') <> raw_value THEN
      RETURN NULL;
    END IF;
  ELSIF raw_value ~ '^[0-9]{2}-[A-Za-z]{3}-[0-9]{4} [0-9]{2}:[0-9]{2}$' THEN
    parsed_value := to_timestamp(raw_value, 'FXDD-Mon-YYYY HH24:MI');
    IF lower(to_char(parsed_value AT TIME ZONE 'UTC', 'DD-Mon-YYYY HH24:MI'))
       <> lower(raw_value) THEN
      RETURN NULL;
    END IF;
  ELSIF raw_value ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}[ T][0-9]{2}:[0-9]{2}' THEN
    parsed_value := raw_value::timestamptz;
  ELSE
    RETURN NULL;
  END IF;
  RETURN parsed_value;
EXCEPTION
  WHEN datetime_field_overflow OR invalid_datetime_format THEN
    RETURN NULL;
END
$function$;

-- Exercise 1: guarded CASE branches parse each supported datetime format and
-- leave unrecognized input NULL instead of raising.
-- Exercise 2: phone text is normalized to digits and validated in staging;
-- there is deliberately no destination column in training.customers.
-- Exercise 3: an INOUT procedure returns a two-column DQ/load summary.
CREATE OR REPLACE PROCEDURE ingest_customer_stage_solution(
  INOUT upserted_rows integer,
  INOUT invalid_rows integer
)
LANGUAGE plpgsql
AS $procedure$
BEGIN
  TRUNCATE cleaned_customer_ingest_solution;

  INSERT INTO cleaned_customer_ingest_solution
  WITH normalized AS (
    SELECT source_row_number,
           trim(full_name) AS full_name,
           lower(trim(email)) AS email,
           CASE upper(trim(country))
             WHEN 'USA' THEN 'US'
             WHEN 'U S' THEN 'US'
             ELSE upper(trim(country))
           END AS country,
           lower(NULLIF(trim(segment), '')) AS segment,
           pg_temp.try_parse_customer_timestamp(created_at) AS parsed_created_at,
           regexp_replace(phone, '[^0-9]', '', 'g') AS phone_digits,
           attributes AS raw_attributes,
           CASE WHEN attributes IS JSON THEN attributes::jsonb END AS attributes,
           attributes IS JSON AS json_valid
    FROM stg_customer_ingest_solution
  )
  SELECT source_row_number,
         full_name,
         email,
         country,
         segment,
         parsed_created_at,
         phone_digits,
         phone_digits ~ '^[0-9]{10,15}$' AS phone_valid,
         email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$' AS email_valid,
         country IN ('US','CA','GB','DE','FR','IN','AU','BR') AS country_valid,
         raw_attributes,
         attributes,
         json_valid
  FROM normalized;

  SELECT COUNT(*)
  INTO invalid_rows
  FROM cleaned_customer_ingest_solution
  WHERE email_valid IS NOT TRUE
     OR country_valid IS NOT TRUE
     OR phone_valid IS NOT TRUE
     OR json_valid IS NOT TRUE
     OR created_at IS NULL
     OR full_name IS NULL
     OR full_name = '';

  -- PostgreSQL cannot update the same conflict target twice in one
  -- INSERT ... ON CONFLICT statement. Rank validated normalized rows first,
  -- then send exactly one winner per email to the upsert.
  WITH valid_rows AS (
    SELECT *
    FROM cleaned_customer_ingest_solution
    WHERE email_valid IS TRUE
      AND country_valid IS TRUE
      AND phone_valid IS TRUE
      AND json_valid IS TRUE
      AND created_at IS NOT NULL
      AND full_name <> ''
  ), deduped AS (
    SELECT valid_rows.*,
           ROW_NUMBER() OVER (
             PARTITION BY email
             ORDER BY created_at DESC, source_row_number DESC
           ) AS winner_rank
    FROM valid_rows
  )
  INSERT INTO customers(full_name, email, country, created_at, segment, attributes)
  SELECT full_name,
         email,
         country,
         created_at,
         segment,
         attributes
  FROM deduped
  WHERE winner_rank = 1
  ON CONFLICT (email) DO UPDATE
  SET full_name = EXCLUDED.full_name,
      country = EXCLUDED.country,
      segment = EXCLUDED.segment,
      -- `created_at` is the immutable first-seen/signup timestamp; a replay or
      -- profile correction must not rewrite it.
      attributes = EXCLUDED.attributes;

  GET DIAGNOSTICS upserted_rows = ROW_COUNT;
END
$procedure$;

CALL ingest_customer_stage_solution(0, 0);

-- Exercises 1 and 2 are visible in the parsed datetime and normalized phone
-- columns. Phone is not loaded because the canonical customers table has no
-- phone column; changing that model is a separate migration decision.
SELECT *
FROM cleaned_customer_ingest_solution
ORDER BY email;

-- Exercise 4: deterministic winner selection happens after normalization and
-- before upsert. Newest valid timestamp wins; email/full_name break any ties.
WITH candidates AS (
  SELECT email AS normalized_email,
         full_name,
         created_at,
         source_row_number,
         ROW_NUMBER() OVER (
           PARTITION BY email
           ORDER BY created_at DESC NULLS LAST, source_row_number DESC
         ) AS winner_rank
  FROM cleaned_customer_ingest_solution
  WHERE email_valid IS TRUE
    AND country_valid IS TRUE
    AND phone_valid IS TRUE
    AND json_valid IS TRUE
    AND created_at IS NOT NULL
    AND full_name IS NOT NULL
    AND full_name <> ''
)
SELECT * FROM candidates WHERE winner_rank = 1 ORDER BY normalized_email;

-- Exercise 5: every cleaned row receives one acceptance state and a diagnostic
-- reason. Keeping detail permits remediation; grouped counts alone would not.
WITH classified AS (
  SELECT *,
         CASE
           WHEN full_name IS NULL OR full_name = '' THEN 'invalid_name'
           WHEN email_valid IS NOT TRUE THEN 'invalid_email'
           WHEN country_valid IS NOT TRUE THEN 'invalid_country'
           WHEN created_at IS NULL THEN 'invalid_datetime'
           WHEN phone_valid IS NOT TRUE THEN 'invalid_phone'
           WHEN json_valid IS NOT TRUE THEN 'invalid_json'
           ELSE 'accepted'
         END AS outcome
  FROM cleaned_customer_ingest_solution
)
SELECT outcome, COUNT(*) AS rows
FROM classified
GROUP BY outcome
ORDER BY outcome;

-- Exercise 6: normalized email is the deduplication/conflict key, so case and
-- surrounding whitespace cannot create competing logical customers.
SELECT email AS normalized_email, COUNT(*) AS candidate_rows
FROM cleaned_customer_ingest_solution
GROUP BY email
ORDER BY email;

-- Exercise 7: missing and unknown are different quality states. Preserve the
-- raw input beside its normalized candidate.
SELECT country AS raw_country,
       CASE upper(trim(country))
         WHEN 'USA' THEN 'US'
         WHEN 'U S' THEN 'US'
         ELSE NULLIF(upper(trim(country)), '')
       END AS normalized_candidate,
       CASE WHEN country IS NULL OR trim(country) = '' THEN 'missing'
            WHEN upper(trim(country)) IN ('US','USA','CA','GB','DE','FR','IN','AU','BR')
              THEN 'recognized'
            ELSE 'unrecognized' END AS country_status
FROM stg_customer_ingest_solution
ORDER BY raw_country NULLS FIRST;

-- Exercise 8: source identity makes replay detection independent of row values.
CREATE TEMP TABLE staged_batch_identity (
  batch_id text NOT NULL,
  source_row_number int NOT NULL,
  email text,
  PRIMARY KEY (batch_id, source_row_number)
);
INSERT INTO staged_batch_identity
SELECT 'day58-demo', source_row_number, email
FROM stg_customer_ingest_solution
ON CONFLICT (batch_id, source_row_number) DO NOTHING;
INSERT INTO staged_batch_identity
SELECT 'day58-demo', source_row_number, email
FROM stg_customer_ingest_solution
ON CONFLICT (batch_id, source_row_number) DO NOTHING;
SELECT COUNT(*) AS replay_safe_rows FROM staged_batch_identity;

-- Exercise 9: PostgreSQL 16's IS JSON predicate validates text without raising.
-- Invalid raw text remains available for quarantine and diagnosis.
SELECT email, attributes AS raw_attributes,
       CASE WHEN attributes IS JSON THEN 'valid_json'
            ELSE 'invalid_json' END AS json_status
FROM stg_customer_ingest_solution
ORDER BY email;

-- Exercise 10: each staged row is accepted or rejected exactly once. Upserted
-- rows can be inserts or updates; production code would return those two counts
-- separately using an explicit merge/audit strategy.
WITH classified AS (
  SELECT *,
         email_valid IS TRUE
           AND country_valid IS TRUE
           AND phone_valid IS TRUE
           AND json_valid IS TRUE
           AND created_at IS NOT NULL
           AND full_name IS NOT NULL
           AND full_name <> '' AS accepted
  FROM cleaned_customer_ingest_solution
)
SELECT (SELECT COUNT(*) FROM stg_customer_ingest_solution) AS staged_rows,
       COUNT(*) FILTER (WHERE accepted IS TRUE) AS accepted_rows,
       COUNT(*) FILTER (WHERE accepted IS NOT TRUE) AS rejected_rows,
       COUNT(*) AS reconciled_rows
FROM classified;

ROLLBACK;
