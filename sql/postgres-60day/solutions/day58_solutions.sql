-- Day 58 solutions: robust staging, normalization, and ingestion
BEGIN;
SET search_path TO training, public;

CREATE TEMP TABLE stg_customer_ingest_solution (
  full_name text,
  email text,
  country text,
  segment text,
  created_at text,
  phone text,
  attributes text
);

INSERT INTO stg_customer_ingest_solution
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
  full_name text,
  email text,
  country text,
  segment text,
  created_at timestamptz,
  phone_digits text,
  phone_valid boolean,
  email_valid boolean,
  country_valid boolean,
  attributes jsonb
) ON COMMIT DROP;

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
    SELECT trim(full_name) AS full_name,
           lower(trim(email)) AS email,
           CASE upper(trim(country))
             WHEN 'USA' THEN 'US'
             WHEN 'U S' THEN 'US'
             ELSE upper(trim(country))
           END AS country,
           lower(NULLIF(trim(segment), '')) AS segment,
           CASE
             WHEN created_at ~ '^[0-9]{4}/[0-9]{2}/[0-9]{2} '
               THEN to_timestamp(created_at, 'YYYY/MM/DD HH24:MI')
             WHEN created_at ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4} '
               THEN to_timestamp(created_at, 'MM/DD/YYYY HH24:MI')
             WHEN created_at ~ '^[0-9]{2}-[A-Za-z]{3}-[0-9]{4} '
               THEN to_timestamp(created_at, 'DD-Mon-YYYY HH24:MI')
             WHEN created_at ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
               THEN created_at::timestamptz
             ELSE NULL
           END AS parsed_created_at,
           regexp_replace(phone, '[^0-9]', '', 'g') AS phone_digits,
           CASE
             WHEN attributes IS JSON THEN attributes::jsonb
             ELSE '{}'::jsonb
           END AS attributes
    FROM stg_customer_ingest_solution
  )
  SELECT full_name,
         email,
         country,
         segment,
         parsed_created_at,
         phone_digits,
         phone_digits ~ '^[0-9]{10,15}$' AS phone_valid,
         email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$' AS email_valid,
         country IN ('US','CA','GB','DE','FR','IN','AU','BR') AS country_valid,
         attributes
  FROM normalized;

  SELECT COUNT(*)
  INTO invalid_rows
  FROM cleaned_customer_ingest_solution
  WHERE NOT email_valid
     OR NOT country_valid
     OR NOT phone_valid
     OR created_at IS NULL
     OR full_name IS NULL
     OR full_name = '';

  INSERT INTO customers(full_name, email, country, created_at, segment, attributes)
  SELECT full_name,
         email,
         country,
         created_at,
         segment,
         attributes
  FROM cleaned_customer_ingest_solution
  WHERE email_valid
    AND country_valid
    AND phone_valid
    AND created_at IS NOT NULL
    AND full_name <> ''
  ON CONFLICT (email) DO UPDATE
  SET full_name = EXCLUDED.full_name,
      country = EXCLUDED.country,
      segment = EXCLUDED.segment,
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
  SELECT lower(trim(email)) AS normalized_email,
         full_name,
         created_at,
         ROW_NUMBER() OVER (
           PARTITION BY lower(trim(email))
           ORDER BY created_at DESC NULLS LAST, trim(full_name), email
         ) AS winner_rank
  FROM stg_customer_ingest_solution
)
SELECT * FROM candidates WHERE winner_rank = 1 ORDER BY normalized_email;

-- Exercise 5: every cleaned row receives one acceptance state and a diagnostic
-- reason. Keeping detail permits remediation; grouped counts alone would not.
WITH classified AS (
  SELECT *,
         CASE
           WHEN full_name IS NULL OR full_name = '' THEN 'invalid_name'
           WHEN NOT email_valid THEN 'invalid_email'
           WHEN NOT country_valid THEN 'invalid_country'
           WHEN created_at IS NULL THEN 'invalid_datetime'
           WHEN NOT phone_valid THEN 'invalid_phone'
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
       NULLIF(upper(trim(country)), '') AS normalized_candidate,
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
SELECT 'day58-demo', row_number() OVER (ORDER BY email), email
FROM stg_customer_ingest_solution
ON CONFLICT (batch_id, source_row_number) DO NOTHING;
INSERT INTO staged_batch_identity
SELECT 'day58-demo', row_number() OVER (ORDER BY email), email
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
         email_valid AND country_valid AND phone_valid
           AND created_at IS NOT NULL
           AND full_name IS NOT NULL AND full_name <> '' AS accepted
  FROM cleaned_customer_ingest_solution
)
SELECT (SELECT COUNT(*) FROM stg_customer_ingest_solution) AS staged_rows,
       COUNT(*) FILTER (WHERE accepted) AS accepted_rows,
       COUNT(*) FILTER (WHERE NOT accepted) AS rejected_rows,
       COUNT(*) AS reconciled_rows
FROM classified;

ROLLBACK;
