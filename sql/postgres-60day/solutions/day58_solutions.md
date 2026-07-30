# Day 58 Solutions — Staging, Cleaning, and Ingestion

The three capstone deliverables are additional timestamp parsing, phone
normalization/validation, and a stored procedure that cleans, validates,
upserts, and returns load counts. The full transaction-safe answer is
[`day58_solutions.sql`](day58_solutions.sql).

## Exercises 1 and 2 — Dates and phone numbers

The staged answer supports these guarded timestamp formats:

| Input example | Guard | Parser |
|---|---|---|
| `2026/01/03 10:00` | `YYYY/MM/DD` regex | `to_timestamp(..., 'YYYY/MM/DD HH24:MI')` |
| `01/15/2026 08:30` | `MM/DD/YYYY` regex | `to_timestamp(..., 'MM/DD/YYYY HH24:MI')` |
| `15-Jan-2026 12:00` | textual month regex | `to_timestamp(..., 'DD-Mon-YYYY HH24:MI')` |
| ISO `YYYY-MM-DD...` | ISO prefix regex | cast to `timestamptz` |

Phone cleanup removes every non-digit character:

```sql
SELECT phone,
       regexp_replace(phone, '[^0-9]', '', 'g') AS phone_digits,
       regexp_replace(phone, '[^0-9]', '', 'g') ~ '^(1)?[0-9]{10}$'
         AS phone_valid
FROM (
  VALUES
    ('(415) 555-0101'),
    ('+1 415 555 0101'),
    ('123')
) AS sample(phone);
```

Expected shape: one row per raw phone with normalized digits and a Boolean
validation flag. This regex is a simplified North American course rule, not a
global phone-number standard.

## Exercise 3 — `INOUT` ingestion procedure

The procedure uses an `INOUT` pair because PostgreSQL procedures do not return a
query result like table-returning functions. `CALL` returns the final parameter
values as a one-row result.

```sql
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
         phone_digits ~ '^(1)?[0-9]{10}$' AS phone_valid,
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

SELECT *
FROM cleaned_customer_ingest_solution
ORDER BY email;

ROLLBACK;
```

Expected results: `CALL` returns `upserted_rows` and `invalid_rows`; the cleaned
table provides row-level evidence behind those counts. The whole demo rolls
back, including the procedure and customer changes.

## Reasoning, safety, and limits

- Regex guards prevent known malformed strings from reaching timestamp casts.
  Add formats deliberately; ambiguous dates such as `03/04/2026` require an
  explicit locale policy.
- Invalid JSON becomes `{}` in this exercise. A production pipeline should also
  retain the raw value and rejection reason.
- `ON CONFLICT (email)` makes repeat loads deterministic, but the procedure's
  `upserted_rows` counts rows affected, not inserts versus updates separately.
- The canonical `training.customers` table has no phone column. The solution
  validates phone in staging but does not discard the schema boundary by
  inventing a destination. Persisting phone requires a reviewed migration.
- The phone regex is intentionally narrow; use country-aware normalization for
  international data.

## Exercise 1 — Parse multiple datetime formats

Guard each cast with a pattern-specific CASE branch. Unrecognized text maps to
NULL and an invalid-datetime reason instead of aborting the batch.

## Exercise 2 — Normalize phone safely

The answer removes non-digits, then applies a deliberately narrow length check.
It retains the normalized staging value but does not invent a destination
column absent from `training.customers`.

## Exercise 4 — Choose duplicate winners deterministically

Normalize email before partitioning. Newest parsed timestamp wins, followed by
stable name/email tie-breakers; source input order never decides.

## Exercise 5 — Partition accepted and rejected outcomes

A CASE expression assigns one diagnostic outcome per cleaned row. Grouped counts
are useful for monitoring, while detail remains available for remediation.

## Exercise 6 — Normalize before conflict handling

The lowercased, trimmed email is both deduplication key and target conflict key.
Case-only variants therefore compete under one declared identity.

## Exercise 7 — Separate missing and unrecognized countries

Missing raw text, recognized codes/aliases, and unknown values receive distinct
states. Raw source text remains alongside its normalized candidate for audit.

## Exercise 8 — Make batch replay idempotent

`(batch_id, source_row_number)` is a stable source identity. Replaying the same
batch uses `ON CONFLICT DO NOTHING`; the count remains unchanged.

## Exercise 9 — Quarantine malformed JSON

PostgreSQL 16's `IS JSON` predicate checks text without raising. Invalid text is
kept with an `invalid_json` code instead of becoming an unexplained `{}` default.

## Exercise 10 — Reconcile every row outcome

Staged count must equal accepted plus rejected count. The procedure's affected
row count does not distinguish inserts from updates, so a production contract
needs explicit merge/audit evidence for those sub-outcomes.
