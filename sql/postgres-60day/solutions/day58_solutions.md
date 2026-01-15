# Day 58 — Solutions (Final Capstone, Part 1 — Staging, Cleaning, Validation)

We’ll extend the cleaning pipeline to support more datetime formats, add phone normalization and validation, and implement a stored procedure/function that ingests staging rows, cleans, validates, upserts, and returns a data‑quality (DQ) summary.

Reference from lesson (annotated: cleaning multiple timestamp formats)
```sql
WITH cleaned AS (
  SELECT trim(full_name)                           AS full_name,
         lower(trim(email))                        AS email,
         upper(trim(country))                      AS country,
         nullif(trim(segment), '')                 AS segment,
         (
           CASE
             WHEN created_at ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN created_at::timestamptz
             WHEN created_at ~ '^[0-9]{2}-[0-9]{2}-[0-9]{4}$' THEN to_timestamp(created_at, 'DD-MM-YYYY')
             WHEN created_at ~ '^\d{4}/\d{2}/\d{2}' THEN to_timestamp(created_at, 'YYYY/MM/DD HH24:MI')
             ELSE NULL
           END
         )                                          AS created_at,
         COALESCE(NULLIF(trim(attributes),''),'{}')::jsonb AS attributes
  FROM stg_customers_raw
)
SELECT * FROM cleaned;
```

Exercise 1 — Extend the parser to handle more datetime formats
Goal
- Support additional common formats: MM/DD/YYYY, RFC 2822 (Fri, 03 Jan 2025 10:00:00 +0000), and textual month (Jan 3, 2025 10:00).

Solution
```sql
WITH cleaned AS (
  SELECT trim(full_name) AS full_name,
         lower(trim(email)) AS email,
         upper(trim(country)) AS country,
         nullif(trim(segment),'') AS segment,
         COALESCE(NULLIF(trim(attributes),''),'{}')::jsonb AS attributes,
         trim(created_at) AS created_raw
  FROM stg_customers_raw
), parsed AS (
  SELECT *,
         CASE
           -- ISO 8601 / YYYY-MM-DD[THH:MI:SS[Z]]
           WHEN created_raw ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
             THEN created_raw::timestamptz
           -- DD-MM-YYYY
           WHEN created_raw ~ '^[0-9]{2}-[0-9]{2}-[0-9]{4}$'
             THEN to_timestamp(created_raw, 'DD-MM-YYYY')
           -- YYYY/MM/DD HH24:MI
           WHEN created_raw ~ '^\d{4}/\d{2}/\d{2}'
             THEN to_timestamp(created_raw, 'YYYY/MM/DD HH24:MI')
           -- MM/DD/YYYY [HH:MI[:SS]]
           WHEN created_raw ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}'
             THEN to_timestamp(created_raw, 'MM/DD/YYYY HH24:MI:SS')
           -- RFC 2822 like: Fri, 03 Jan 2025 10:00:00 +0000
           WHEN created_raw ~ '^[A-Za-z]{3},\s\d{2}\s[A-Za-z]{3}\s\d{4}'
             THEN to_timestamp(created_raw, 'Dy, DD Mon YYYY HH24:MI:SS TZH:TZM')
           -- Text month like: Jan 3, 2025 10:00
           WHEN created_raw ~ '^[A-Za-z]{3}\s\d{1,2},\s\d{4}'
             THEN to_timestamp(created_raw, 'Mon DD, YYYY HH24:MI')
           ELSE NULL
         END AS created_at
  FROM cleaned
)
SELECT * FROM parsed;
```
Line‑by‑line notes
- created_raw: cache the trimmed string once.
- Each WHEN branch: use a regex guard then an appropriate to_timestamp pattern.
- RFC 2822 branch expects timezone; adapt TZ pattern to your input if needed.

Exercise 2 — Add phone normalization and flag invalid formats
Goal
- Produce a normalized phone string. Example strategy: keep digits only, optionally prefix with a default country code (here just illustrate US +1 if 10 digits). Also compute phone_valid boolean.

Solution
```sql
-- Assume staging has a phone column (TEXT). If not, add it for the exercise.
ALTER TABLE IF EXISTS stg_customers_raw ADD COLUMN IF NOT EXISTS phone TEXT;

WITH cleaned AS (
  SELECT trim(full_name) AS full_name,
         lower(trim(email)) AS email,
         upper(trim(country)) AS country,
         nullif(trim(segment),'') AS segment,
         COALESCE(NULLIF(trim(attributes),''),'{}')::jsonb AS attributes,
         trim(phone) AS phone_raw
  FROM stg_customers_raw
), normalized AS (
  SELECT *,
         regexp_replace(COALESCE(phone_raw,''), '[^0-9]+', '', 'g') AS digits
  FROM cleaned
), mapped AS (
  SELECT *,
    CASE
      WHEN length(digits) = 10 THEN '+1' || digits          -- example default country
      WHEN length(digits) = 11 AND left(digits,1)='1' THEN '+' || digits
      WHEN length(digits) BETWEEN 8 AND 15 THEN '+' || digits -- generic E.164-ish fallback
      ELSE NULL
    END AS phone_norm
  FROM normalized
)
SELECT *, (phone_norm IS NOT NULL) AS phone_valid
FROM mapped;
```
Notes
- regexp_replace removes everything but digits.
- Adjust default country logic for your locale; real systems use a library or metadata.

Exercise 3 — Write a stored routine to ingest, clean, validate, upsert, and return a DQ summary
Goal
- Implement a stored FUNCTION (returns a summary table) that:
  1) Cleans/validates emails, countries, phones, and timestamps
  2) Upserts valid rows into training.customers (by unique email)
  3) Returns counts for total, inserted, updated, invalid

Solution (PL/pgSQL)
```sql
CREATE OR REPLACE FUNCTION training.ingest_customers_from_staging()
RETURNS TABLE(total_rows int, inserted int, updated int, invalid_rows int)
LANGUAGE plpgsql
AS $$
DECLARE
  v_total int := 0;
  v_inserted int := 0;
  v_updated int := 0;
  v_invalid int := 0;
BEGIN
  -- 1) Clean + validate into a temp table ---------------------------------
  CREATE TEMP TABLE tmp_customers_clean AS
  WITH cleaned AS (
    SELECT trim(full_name) AS full_name,
           lower(trim(email)) AS email,
           upper(trim(country)) AS country,
           nullif(trim(segment),'') AS segment,
           trim(created_at) AS created_raw,
           COALESCE(NULLIF(trim(attributes),''),'{}')::jsonb AS attributes,
           trim(phone) AS phone_raw
    FROM stg_customers_raw
  ), parsed AS (
    SELECT *,
           CASE
             WHEN created_raw ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN created_raw::timestamptz
             WHEN created_raw ~ '^[0-9]{2}-[0-9]{2}-[0-9]{4}$' THEN to_timestamp(created_raw, 'DD-MM-YYYY')
             WHEN created_raw ~ '^\d{4}/\d{2}/\d{2}' THEN to_timestamp(created_raw, 'YYYY/MM/DD HH24:MI')
             WHEN created_raw ~ '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}' THEN to_timestamp(created_raw, 'MM/DD/YYYY HH24:MI:SS')
             WHEN created_raw ~ '^[A-Za-z]{3},\s\d{2}\s[A-Za-z]{3}\s\d{4}' THEN to_timestamp(created_raw, 'Dy, DD Mon YYYY HH24:MI:SS TZH:TZM')
             WHEN created_raw ~ '^[A-Za-z]{3}\s\d{1,2},\s\d{4}' THEN to_timestamp(created_raw, 'Mon DD, YYYY HH24:MI')
             ELSE NULL
           END AS created_at
    FROM cleaned
  ), phone_norm AS (
    SELECT *, regexp_replace(COALESCE(phone_raw,''), '[^0-9]+', '', 'g') AS digits
    FROM parsed
  ), with_phone AS (
    SELECT *,
      CASE
        WHEN length(digits) = 10 THEN '+1' || digits
        WHEN length(digits) = 11 AND left(digits,1)='1' THEN '+' || digits
        WHEN length(digits) BETWEEN 8 AND 15 THEN '+' || digits
        ELSE NULL
      END AS phone_norm
    FROM phone_norm
  ), validated AS (
    SELECT *,
           (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$') AS email_valid,
           (country IN ('US','CA','GB','DE','FR','IN','AU','BR')) AS country_valid,
           (phone_norm IS NOT NULL) AS phone_valid
    FROM with_phone
  )
  SELECT * FROM validated;

  SELECT COUNT(*) INTO v_total FROM tmp_customers_clean;

  -- 2) Split valid/invalid -----------------------------------------------
  CREATE TEMP TABLE tmp_valid AS
    SELECT * FROM tmp_customers_clean
    WHERE email_valid AND country_valid;  -- phone_valid optional for acceptance

  CREATE TEMP TABLE tmp_invalid AS
    SELECT * FROM tmp_customers_clean
    WHERE NOT (email_valid AND country_valid);

  SELECT COUNT(*) INTO v_invalid FROM tmp_invalid;

  -- 3) Upsert by email ----------------------------------------------------
  -- 3a) UPDATE existing rows
  WITH u AS (
    UPDATE training.customers c
    SET full_name = v.full_name,
        country   = v.country,
        segment   = v.segment,
        created_at= COALESCE(v.created_at, c.created_at),
        attributes= v.attributes
    FROM tmp_valid v
    WHERE c.email = v.email
    RETURNING 1
  ) SELECT COUNT(*) INTO v_updated FROM u;

  -- 3b) INSERT new rows
  WITH ins AS (
    INSERT INTO training.customers(full_name, email, country, segment, created_at, attributes)
    SELECT v.full_name, v.email, v.country, v.segment,
           COALESCE(v.created_at, now()), v.attributes
    FROM tmp_valid v
    WHERE NOT EXISTS (SELECT 1 FROM training.customers c WHERE c.email = v.email)
    RETURNING 1
  ) SELECT COUNT(*) INTO v_inserted FROM ins;

  -- 4) Return summary -----------------------------------------------------
  total_rows := v_total; inserted := v_inserted; updated := v_updated; invalid_rows := v_invalid;
  RETURN NEXT;
END;
$$;
```
How to run and interpret
```sql
SELECT * FROM training.ingest_customers_from_staging();
-- Expect a single row with counts. Inspect tmp_invalid (in same session) if you want details.
```
Notes
- We chose a FUNCTION to return a summary row; a PROCEDURE cannot RETURN rows directly. In Postgres 11+, procedures are for side effects; functions return data.
- For production, consider persisting invalid rows in an error table with reasons per row.

Going further
- Add strict country normalization via a country_map table before validation.
- Track audit columns (created_at/updated_at/by) on training.customers.
- Wrap the ingestion in a transaction; add exception handling with GET STACKED DIAGNOSTICS.
