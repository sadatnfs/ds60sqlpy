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

ROLLBACK;
