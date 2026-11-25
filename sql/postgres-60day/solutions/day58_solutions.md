# Day 58 Solutions: Staging, Cleaning, and Ingestion


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day58_solutions.sql
```

`psql` prints `BEGIN`, `SET`, `CREATE TABLE`, `INSERT 0 4`, `CREATE TABLE`,
`SET`, `CREATE FUNCTION` and `CREATE PROCEDURE`, then the `CALL` result: one
row with `upserted_rows` 3 and `invalid_rows` 1. The four-row cleaned detail
follows, then one result per remaining exercise (the replay check adds its own
`CREATE TABLE`, `INSERT 0 4` and `INSERT 0 0`), and the file ends with
`ROLLBACK`, which also discards the function, the procedure and the three
customers the `CALL` created. Stop at the first `ERROR`, because every later
result reads tables the failed statement was meant to fill. The
[solution reading notes](../../STUDY-GUIDE.md#read-a-solution) describe how to
compare your own attempt.

## Clause-by-clause reading map

Read the solution as one pipeline with three relations, each of which you can
query on its own.

- `stg_customer_ingest_solution` is the raw staging table: four rows, every
  value as text, plus an identity column `source_row_number` (1 to 4) so each
  row keeps an identity even when its email is garbage.
- `cleaned_customer_ingest_solution` holds one row per staged row. The
  procedure truncates it and refills it from a `normalized` CTE that trims and
  lowercases email, maps `USA` and `U S` to `US`, lowercases segment, parses
  `created_at` with the guarded function, strips the phone to digits and tests
  `attributes IS JSON`; the outer `SELECT` of that `INSERT` adds
  `phone_valid`, `email_valid` and `country_valid`. Four rows in, four rows
  out: cleaning never filters.
- The upsert reads only rows whose checks all pass, numbers each email's rows
  with `ROW_NUMBER()`, and inserts the rank-1 rows into `customers`.

Follow each query in
[logical order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).
Order matters most in the upsert: its `WHERE` removes invalid rows before the
window function runs, so an invalid but newer row can never outrank a valid
one, and `winner_rank = 1` is applied only after ranking. The counting queries
reread the cleaned table with `IS NOT TRUE`, so a `NULL` flag counts as a
rejection instead of disappearing.

The three capstone deliverables are additional timestamp parsing, phone
normalization/validation, and a stored procedure that cleans, validates,
upserts, and returns load counts. The full transaction-safe answer is
[`day58_solutions.sql`](day58_solutions.sql).

## Exercises 1 and 2: Dates and phone numbers

The staged answer supports these guarded timestamp formats:

| Input example | Guard | Parser |
|---|---|---|
| `2026/01/03 10:00` | `YYYY/MM/DD` regex | `to_timestamp(..., 'YYYY/MM/DD HH24:MI')` |
| `01/15/2026 08:30` | `MM/DD/YYYY` regex | `to_timestamp(..., 'MM/DD/YYYY HH24:MI')` |
| `15-Jan-2026 12:00` | textual month regex | `to_timestamp(..., 'DD-Mon-YYYY HH24:MI')` |
| ISO `YYYY-MM-DD...` | ISO prefix regex | cast to `timestamptz` |

Phone cleanup removes every non-digit character:

```sql
SELECT
  phone,
  regexp_replace(phone, '[^0-9]', '', 'g') AS phone_digits,
  regexp_replace(phone, '[^0-9]', '', 'g') ~ '^(1)?[0-9]{10}$' AS phone_valid
FROM (
  VALUES ('(415) 555-0101'),
    ('+1 415 555 0101'),
    ('123')) AS sample (phone);
```

Expected shape: one row per raw phone with normalized digits and a Boolean
validation flag. This regex is a simplified North American course rule, not a
global phone-number standard.

## Capstone implementation: Exercise 3 ingestion procedure

The procedure uses an `INOUT` pair because PostgreSQL procedures do not return a
query result like table-returning functions. `CALL` returns the final parameter
values as a one-row result.

```sql
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

INSERT INTO stg_customer_ingest_solution (full_name, email, country, segment, created_at, phone, attributes)
VALUES
  (' Customer 601 ', 'CUSTOMER601@EXAMPLE.COM ', 'USA', 'gold', '2026/01/03 10:00', '(415) 555-0101', '{"channel":"web"}'),
  ('Customer 602', 'customer602@example.com', 'GB', 'silver', '01/15/2026 08:30', '+44 20 7946 0958', '{"channel":"mobile"}'),
  ('Customer 603', 'customer603@example.com', 'DE', NULL, '15-Jan-2026 12:00', '030-1234567', '{"channel":"store"}'),
  ('Customer bad', 'not-an-email', 'XX', 'bronze', 'not-a-date', '123', 'not-json');

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

-- The complete executable defines pg_temp.try_parse_customer_timestamp before
-- the procedure. It uses exact-format guards, round-trip checks, exception
-- handling, and STABLE volatility after SET LOCAL TIME ZONE 'UTC'. STABLE is
-- required because parsing timestamptz can depend on session settings.
CREATE OR REPLACE PROCEDURE ingest_customer_stage_solution (INOUT upserted_rows integer, INOUT invalid_rows integer)
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
      -- Preserve the existing created_at as the first-seen/signup timestamp.
      attributes = EXCLUDED.attributes;

  GET DIAGNOSTICS upserted_rows = ROW_COUNT;
END
$procedure$
;
CALL ingest_customer_stage_solution (0, 0);

SELECT
  *
FROM
  cleaned_customer_ingest_solution
ORDER BY
  email;

ROLLBACK;
```

Expected seed results: `CALL` returns `upserted_rows = 3` and
`invalid_rows = 1`; the cleaned table retains four source rows, including the
raw malformed JSON. The accepted and rejected counts must sum to the staged
count. The whole demo rolls back, including the procedure and customer changes.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 3, stage every source row with `source_row_number` and raw text/JSON evidence; derive normalized name, email, country and segment, the parsed `created_at`, and the `phone_valid`, `email_valid`, `country_valid` and `json_valid` flags, then upsert exactly one validated winner per normalized email.
- **Expected result/shape:** For sql-58 Exercise 3, expected output: the procedure CALL returns one row with `upserted_rows` and `invalid_rows` (3 and 1 for the seed), while the cleaned detail remains one row per staged source row with raw evidence, normalized fields, and all four validity decisions.
- **Independent verification:** For sql-58 Exercise 3, confirm that `customers` goes from 500 to 503 rows after the first `CALL` and that `upserted_rows` 3 plus `invalid_rows` 1 equals the 4 staged rows; a second `CALL` in the same transaction prints 3 and 1 again and leaves 503 rows. Then stage a valid newer `customer601@example.com` row and `CALL` again: the pair stays 3 and 1 over 5 staged rows, `customers` still has 503 rows, and the stored name becomes the new row's, so the losing duplicate needs its own count.
- **Intermediate relation check:** Run the `normalized` CTE body as a plain `SELECT` against `stg_customer_ingest_solution` before wrapping it in the procedure: it returns 4 rows with `country` US, GB, DE and XX, `phone_digits` 4155550101, 442079460958, 0301234567 and 123, and `json_valid` false only for the `not-json` row. After one `CALL`, `cleaned_customer_ingest_solution` also holds 4 rows.
- **Clause check:** The procedure body runs three steps in a fixed order. `TRUNCATE` plus `INSERT ... WITH normalized` refills the cleaned table; `SELECT COUNT(*) INTO invalid_rows` counts rows where any flag `IS NOT TRUE` or the timestamp or name is missing; and `INSERT INTO customers ... ON CONFLICT (email) DO UPDATE` writes the winners, after which `GET DIAGNOSTICS upserted_rows = ROW_COUNT` captures how many rows that one statement touched. Because both `INOUT` parameters are assigned in the body, `CALL ingest_customer_stage_solution (0, 0)` prints them as a one-row result: 3 and 1 on the seed.
- **Alternative/trade-off:** A PostgreSQL function declared `RETURNS TABLE (upserted_rows int, invalid_rows int)` could do the same writes and be used inside a `SELECT`, but a procedure called with `CALL` makes it plain that this step changes tables. `MERGE` could replace the upsert, and on PostgreSQL 17 `RETURNING merge_action()` labels each affected row `INSERT` or `UPDATE`, which `ROW_COUNT` after `ON CONFLICT` cannot do: a second `CALL` in the same transaction reports 3 again, now meaning three updates.
- **Edge case:** Stage a second valid row for `customer601@example.com` and `CALL` again: `upserted_rows` stays 3 and `invalid_rows` stays 1, so with 5 staged rows the two outputs no longer add up to the staged count. The losing duplicate is valid but not loaded, and neither counter reports it; a full reconciliation needs a third number for rows removed by deduplication.

## Reasoning, safety, and limits

- Exact-format regex guards, round-trip formatting, and caught datetime
  exceptions prevent malformed strings from aborting the batch. The parser is
  `STABLE`, not `IMMUTABLE`, because `timestamptz` parsing is session-sensitive.
  Ambiguous dates such as `03/04/2026` still require an explicit locale policy.
- Invalid JSON remains visible in `raw_attributes`, produces
  `json_valid = false`, and keeps parsed `attributes` as SQL `NULL`; it never
  becomes an accepted unexplained empty object.
- Validation uses `IS TRUE` and rejection uses `IS NOT TRUE`, so an unknown
  Boolean cannot slip through either population.
- Valid rows are ranked by normalized email before `ON CONFLICT`; this avoids
  PostgreSQL trying to update the same target twice in one statement. The
  stable `source_row_number` breaks equal-timestamp ties.
- `ON CONFLICT (email)` makes repeat loads deterministic, but the procedure's
  `upserted_rows` counts rows affected, not inserts versus updates separately.
- The update preserves the existing `customers.created_at` as the immutable
  first-seen/signup timestamp; profile corrections update descriptive fields.
- The canonical `training.customers` table has no phone column. The solution
  validates phone in staging but does not discard the schema boundary by
  inventing a destination. Persisting phone requires a reviewed migration.
- The phone regex is intentionally narrow; use country-aware normalization for
  international data.

## Exercise 1: Parse multiple datetime formats

Guard each cast with a pattern-specific CASE branch. Unrecognized text maps to
NULL and an invalid-datetime reason instead of aborting the batch.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 1, parse the four staged `created_at` strings in `stg_customer_ingest_solution` with the temporary function `pg_temp.try_parse_customer_timestamp`, which accepts `YYYY/MM/DD HH24:MI`, `MM/DD/YYYY HH24:MI`, `DD-Mon-YYYY HH24:MI`, and ISO `YYYY-MM-DD HH24:MI` text and returns NULL for anything else.
- **Expected result/shape:** For sql-58 Exercise 1, expected output: in `cleaned_customer_ingest_solution`, `created_at` is 2026-01-03 10:00, 2026-01-15 08:30, and 2026-01-15 12:00 UTC for the first three staged rows and NULL for `not-a-date`.
- **Independent verification:** For sql-58 Exercise 1, call the function directly with the session time zone set to UTC on `'2026/01/03 10:00'`, `'01/15/2026 08:30'`, `'15-Jan-2026 12:00'`, and `'not-a-date'` and expect the three timestamps above and NULL; the impossible date `'2026/02/30 10:00'` must also return NULL, whereas a plain `to_timestamp('2026/02/30 10:00', 'YYYY/MM/DD HH24:MI')` raises `date/time field value out of range` and would abort the batch.
- **Intermediate relation check:** For sql-58 Exercise 1, call `pg_temp.try_parse_customer_timestamp` on each staged string by itself before you run the cleaning step.
- **Clause check:** For sql-58 Exercise 1, the solution defines `pg_temp.try_parse_customer_timestamp` as a `STABLE` PL/pgSQL function: each `IF`/`ELSIF` branch tests one anchored format with `~`, parses it with an `FX` `to_timestamp` template, rejects a value whose round trip through `to_char` differs, and an `EXCEPTION` block turns datetime errors into NULL.
- **Alternative/trade-off:** Plain `to_timestamp` with a template is shorter but is not a guard. On PostgreSQL 17 it raises `date/time field value out of range` for `'2026/02/30 10:00'`, so one such row stops the batch, and it quietly accepts `'2026/1/3 10:00'`, which the function's two-digit regex rejects. The function pays in length for a `NULL` in every bad case, which the cleaned table can then flag.
- **Edge case:** Text such as `01/02/2026` is January 2 under `MM/DD/YYYY` but February 1 under `DD/MM/YYYY`; the parser commits to one declared format per pattern instead of letting the session `DateStyle` decide.

## Exercise 2: Normalize phone safely

The answer removes non-digits, then applies a deliberately narrow length check.
It retains the normalized staging value but does not invent a destination
column absent from `training.customers`.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 2, strip every non-digit from the staged `phone` with `regexp_replace(phone, '[^0-9]', '', 'g')` and flag the result valid when it has 10 to 15 digits (`phone_digits ~ '^[0-9]{10,15}$'`).
- **Expected result/shape:** For sql-58 Exercise 2, expected output: `phone_digits` 4155550101, 442079460958, 0301234567, and 123, with `phone_valid` true, true, true, and false, stored in `cleaned_customer_ingest_solution`.
- **Independent verification:** For sql-58 Exercise 2, confirm that `SELECT phone_digits, phone_valid FROM cleaned_customer_ingest_solution ORDER BY source_row_number` returns those four pairs and that only the `123` row is invalid; then test `'+1 (415) 555-0101 ext. 9'`, which becomes 141555501019 and still passes the length rule, so an extension needs its own handling.
- **Intermediate relation check:** For sql-58 Exercise 2, run the `regexp_replace` on the four staged phone strings in a plain `SELECT` before you add the validity flag.
- **Clause check:** For sql-58 Exercise 2, the cleaning step computes `regexp_replace(phone, '[^0-9]', '', 'g') AS phone_digits` in one CTE and `phone_digits ~ '^[0-9]{10,15}$' AS phone_valid` in the next, so the flag reads the normalized digits, not the raw text.
- **Alternative/trade-off:** A stricter rule could demand a country-specific shape, such as 10 digits after an optional leading 1 for US numbers, but that pattern rejects the valid UK value `+44 20 7946 0958` (12 digits) unless the country is consulted too. The 10-to-15-digit rule accepts all three good seed phones and rejects `123`; its cost is that it cannot tell a US number from a German one of the same length, and it keeps no `+`.
- **Edge case:** Removing every non-digit also removes a leading `+`, so an international number and a domestic number with the same digits become indistinguishable; keep the raw value for audit.

## Exercise 3: Build the `INOUT` ingestion procedure

The complete transaction-safe procedure, its `CALL`, row-level evidence, and
reasoning appear in the
[capstone implementation above](#capstone-implementation--exercise-3-ingestion-procedure).
Use that runnable implementation to compare your attempt clause by clause,
including its validation rules, deterministic upsert, returned counts, and
rollback boundary.

## Exercise 4: Choose duplicate winners deterministically

Normalize email before partitioning. Newest parsed timestamp wins, and the
higher `source_row_number` breaks a tie; the order rows arrive in never decides.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 4, rank only cleaned rows whose email, country, phone, and JSON flags are all true and whose parsed timestamp and name are present; partition by normalized email and order by parsed creation time descending then `source_row_number` descending.
- **Expected result/shape:** For sql-58 Exercise 4, expected output: exactly one valid winner per `normalized_email`, with the normalized email, source row identity, parsed timestamp, and `winner_rank = 1`, ordered by normalized email.
- **Independent verification:** For sql-58 Exercise 4, assert every winner has all validity flags true, normalized emails are unique, an equal-timestamp duplicate chooses the higher `source_row_number`, an invalid newer duplicate never wins, and the winner set matches the rows used by the upsert.
- **Intermediate relation check:** Run the `candidates` CTE without the outer `winner_rank = 1` filter. On the seed it returns 3 rows, one each for customer601, customer602 and customer603 from source rows 1, 2 and 3, all ranked 1 because no email repeats. Source row 4 never appears, since the `WHERE` removes it before ranking.
- **Clause check:** The `WHERE` inside `candidates` keeps rows whose email, country, phone and JSON flags are all `IS TRUE` and whose `created_at` and `full_name` are present; only then does `ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at DESC NULLS LAST, source_row_number DESC)` number each email's rows, and the outer query keeps rank 1 ordered by `normalized_email`. `NULLS LAST` never matters here because `created_at IS NOT NULL` already removed the missing timestamps.
- **Alternative/trade-off:** `DISTINCT ON (email) ... ORDER BY email, created_at DESC, source_row_number DESC` returns the same three winners in a shorter query. `ROW_NUMBER()` is kept because the procedure needs exactly this ranking in front of the upsert, and the visible `winner_rank` lets you inspect the losers by dropping the outer filter. Breaking ties on `full_name` instead would make the winner depend on how a name is spelled, while `source_row_number` is unique within the batch, so the order is always total.
- **Edge case:** Stage `'Customer601@example.com'` with row 1's `'2026/01/03 10:00'` timestamp and a valid phone, then `CALL` again: it normalizes to the same email, ties on `created_at`, and beats row 1 because its higher `source_row_number` sorts first. A newer `customer601` row with phone `'12'` stays out entirely; the filter drops it before ranking, so it cannot win.

## Exercise 5: Partition accepted and rejected outcomes

A CASE expression assigns one diagnostic outcome per cleaned row. Grouped counts
are useful for monitoring, while detail remains available for remediation.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 5, label each row of `cleaned_customer_ingest_solution` with one `outcome` from a `CASE` that tests name, email, country, timestamp, phone and JSON in that order and otherwise returns `accepted`, then count the rows per `outcome`.
- **Expected result/shape:** For sql-58 Exercise 5, expected output: two rows on the seed, `accepted` 3 and `invalid_email` 1, whose `rows` sum to the 4 staged rows. The final columns are `outcome` and `rows`. The final order is `outcome`.
- **Independent verification:** For sql-58 Exercise 5, confirm the `rows` values sum to `SELECT COUNT(*) FROM stg_customer_ingest_solution` (4) and that source row 4, which fails the email, country, timestamp, phone and JSON checks, is counted once as `invalid_email`; then, inside a savepoint, set `email_valid = true` for source row 4 in the cleaned table and rerun: the result becomes `accepted` 3 and `invalid_country` 1.
- **Intermediate relation check:** Run `classified` alone with `source_row_number` and `outcome` side by side: rows 1 to 3 read `accepted` and row 4 reads `invalid_email`, even though row 4 also fails the country, timestamp, phone and JSON checks.
- **Clause check:** The `CASE` tests name, email, country, timestamp, phone and JSON in that order and stops at the first match, so each cleaned row receives exactly one `outcome`; `GROUP BY outcome` then counts them. On the seed the result is two rows, `accepted` 3 and `invalid_email` 1, in alphabetical order of `outcome`.
- **Alternative/trade-off:** To keep every failure, produce one row per staged row and failed check instead, for example by unnesting an array of failing check names; the bad row would then report five reasons and the counts would no longer sum to 4. The single-reason `CASE` keeps the total equal to the staged count at the cost of hiding secondary defects, so state the order of the checks wherever the report is shown.
- **Edge case:** Because country is tested third, a row with an unknown country and a bad email is reported as `invalid_email`, never `invalid_country`. Give row 4 a valid email and rerun the procedure: the same row moves to `invalid_country`, and the totals still sum to 4.

## Exercise 6: Normalize before conflict handling

The lowercased, trimmed email is both deduplication key and target conflict key.
Case-only variants therefore compete under one declared identity.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 6, group `cleaned_customer_ingest_solution`, whose `email` is already `lower(trim(...))`, by that normalized `email` and count the candidate rows per address.
- **Expected result/shape:** For sql-58 Exercise 6, expected output: 4 rows, one per normalized `email`, each with `candidate_rows` 1 on the staged data. The final columns are `normalized_email` and `candidate_rows`. The final order is `email`.
- **Independent verification:** For sql-58 Exercise 6, confirm that the staged `CUSTOMER601@EXAMPLE.COM ` (upper case with a trailing space) appears as `customer601@example.com`; on `VALUES ('A@x.com'), ('a@x.com ')`, `COUNT(DISTINCT e)` is 2 but `COUNT(DISTINCT lower(trim(e)))` is 1, which is the duplicate that normalization must catch before deduplication.
- **Intermediate relation check:** For sql-58 Exercise 6, compare `COUNT(DISTINCT email)` with `COUNT(DISTINCT lower(trim(email)))` on the staging table before you group the cleaned rows.
- **Clause check:** `GROUP BY email` over the cleaned table counts how many staged rows share each normalized address. The procedure has already applied `lower(trim(email))`, so the raw `'CUSTOMER601@EXAMPLE.COM '` is grouped as `customer601@example.com`. The four seed emails are distinct, so every `candidate_rows` value is 1, and the invalid `not-an-email` gets a group too because nothing here filters on validity.
- **Alternative/trade-off:** Normalizing inside this query, with `GROUP BY lower(trim(email))` on the staging table, gives the same groups without the procedure, but then the normalization rule lives in two places and can drift. Grouping the cleaned table means this check uses exactly the key that `ON CONFLICT (email)` will compare.
- **Edge case:** Lower-casing the whole address is a policy choice, because the part before `@` may be case-sensitive in principle; document the rule that the deduplication relies on.

## Exercise 7: Separate missing and unrecognized countries

Missing raw text, recognized codes/aliases, and unknown values receive distinct
states. Raw source text remains alongside its normalized candidate for audit.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 7, list every row of `stg_customer_ingest_solution` with its raw `country`, a normalized candidate (`USA` and `U S` become `US`, blank text becomes NULL) and a status that is `missing` for NULL or blank text, `recognized` for a known code or alias, and `unrecognized` otherwise.
- **Expected result/shape:** For sql-58 Exercise 7, expected output: 4 rows, one per staged row: `DE`/`DE`, `GB`/`GB` and `USA`/`US` are `recognized` and `XX`/`XX` is `unrecognized`. The final columns are `raw_country`, `normalized_candidate`, and `country_status`. The final order is `raw_country NULLS FIRST`.
- **Independent verification:** For sql-58 Exercise 7, confirm the 4 rows match `SELECT country FROM stg_customer_ingest_solution` and that no seed row is `missing`; then, inside a savepoint, stage one row with a NULL country and one with `' '` and expect 6 rows, the NULL row first and the blank row second, both `missing` with a NULL candidate, while `XX` stays `unrecognized`.
- **Intermediate relation check:** Before adding the status column, list `country` beside `upper(trim(country))` from the staging table: `USA`, `GB`, `DE` and `XX` on the seed. Only `XX` falls outside the known codes, and no row is `NULL` or blank, so the seed cannot show the `missing` state.
- **Clause check:** The first `CASE` builds `normalized_candidate`, mapping `USA` and `U S` to `US` and turning blank text into `NULL` with `NULLIF`; the second sets `country_status` from the raw value, testing `missing` first. The query reads all four staged rows without a filter and sorts by `raw_country NULLS FIRST`, so missing countries would print at the top; on the seed the rows are DE, GB, USA and XX.
- **Alternative/trade-off:** The learner file's `country_map` table is the alternative: a lookup join keeps aliases as data instead of code. It must join on the trimmed upper-case value, though; the learner joins on raw `src.country`, so its `' U S '` and `USA` keys match none of the three staged values and `' us '` becomes `US` only through the `upper(trim(...))` fallback. The two `CASE` expressions here also disagree: `' u s '` gets candidate `US` but status `unrecognized`, because the status list has no `U S`.
- **Edge case:** Stage one row with a `NULL` country and one with `'  '`: both print `missing` with a `NULL` candidate, sorted first. Staging `' u s '` exposes the disagreement above, and the procedure accepts that row with `country` `US`, so this report and the load reach different verdicts on it.

## Exercise 8: Make batch replay idempotent

`(batch_id, source_row_number)` is a stable source identity. Replaying the same
batch uses `ON CONFLICT DO NOTHING`; the count remains unchanged.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 8, load the four staged rows into `staged_batch_identity`, keyed by (`batch_id`, `source_row_number`), twice with `INSERT ... ON CONFLICT (batch_id, source_row_number) DO NOTHING`, then count the stored rows.
- **Expected result/shape:** For sql-58 Exercise 8, expected output: `INSERT 0 4` for the first load, `INSERT 0 0` for the replay, and one row with `replay_safe_rows` 4. The final columns are `replay_safe_rows`.
- **Independent verification:** For sql-58 Exercise 8, confirm that the replay inserts nothing and that `SELECT COUNT(*) FROM staged_batch_identity` equals `SELECT COUNT(*) FROM stg_customer_ingest_solution` (4); load the same rows under a new `batch_id` and expect 8 rows, because the key identifies a batch and a source row, not a customer.
- **Intermediate relation check:** For sql-58 Exercise 8, run the `INSERT ... ON CONFLICT DO NOTHING` twice and read both command tags before you count.
- **Clause check:** For sql-58 Exercise 8, the solution creates `staged_batch_identity` with the primary key (`batch_id`, `source_row_number`), runs the same `INSERT ... SELECT ... ON CONFLICT (batch_id, source_row_number) DO NOTHING` twice, and counts the stored rows.
- **Alternative/trade-off:** Keying on normalized email would also make a replay safe, but it would block a legitimate later batch that updates a customer's details, and it would build a key for the `not-an-email` row from bad data. The pair (`batch_id`, `source_row_number`) identifies the delivery, not the customer, so customer-level deduplication stays the upsert's job.
- **Edge case:** `ON CONFLICT DO NOTHING` makes a replay safe only for the declared key; a corrected resend under a new `batch_id` is a new load and needs its own reconciliation.

## Exercise 9: Quarantine malformed JSON

PostgreSQL 16's `IS JSON` predicate checks text without raising. Invalid text is
kept with an `invalid_json` code instead of becoming an unexplained `{}` default.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 9, read the raw `email` and `attributes` text of each `stg_customer_ingest_solution` row and label it `valid_json` when `attributes IS JSON` is true and `invalid_json` otherwise, without casting the text.
- **Expected result/shape:** For sql-58 Exercise 9, expected output: 4 rows, one per staged row, ordered by raw `email` from `'CUSTOMER601@EXAMPLE.COM '`: three `valid_json` rows and `not-an-email` with `raw_attributes` `not-json` and `invalid_json`. The final columns are `email`, `raw_attributes`, and `json_status`. The final order is `email`.
- **Independent verification:** For sql-58 Exercise 9, confirm that `SELECT 'not-json'::jsonb` raises `invalid input syntax for type json` inside a savepoint while this query returns all 4 rows; then stage a row with NULL attributes and expect `invalid_json`, because `NULL IS JSON` is NULL and falls to the `ELSE` branch.
- **Intermediate relation check:** Select `attributes` and `attributes IS JSON` from the staging table first: three seed rows give true and `'not-json'` gives false. A `NULL` attributes value gives `NULL`, not false, which matters in the next step.
- **Clause check:** The query reads `stg_customer_ingest_solution` directly, so `email` is raw text and `'CUSTOMER601@EXAMPLE.COM '` keeps its capitals and trailing space. The `CASE WHEN attributes IS JSON` sends both false and `NULL` to the `ELSE` branch, so missing attributes are labeled `invalid_json`; the procedure likewise rejects such a row because its `json_valid IS NOT TRUE`.
- **Alternative/trade-off:** `pg_input_is_valid(attributes, 'jsonb')` (PostgreSQL 16 and later) runs the same test without raising, and a PL/pgSQL `EXCEPTION` block could catch the cast error row by row at a higher cost. `IS JSON` also accepts scalars and arrays: `'42'` and `'[1,2]'` pass, so use `IS JSON OBJECT` if `attributes` must hold an object.
- **Edge case:** Stage a row whose attributes are `NULL`: it shows `invalid_json` here and the procedure counts it in `invalid_rows`, even though the `customers.attributes` default is `'{}'`. Whether missing attributes should reject a customer or default to an empty object is a policy decision this query makes without saying so.

## Exercise 10: Reconcile every row outcome

Staged count must equal accepted plus rejected count. The procedure's affected
row count does not distinguish inserts from updates, so a production contract
needs explicit merge/audit evidence for those sub-outcomes.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 10, classify every row of `cleaned_customer_ingest_solution` as accepted only when its email, country, phone, JSON, timestamp, and name checks all pass, then count staged, accepted, and rejected rows and their reconciled sum.
- **Expected result/shape:** For sql-58 Exercise 10, expected output: one row with `staged_rows` 4, `accepted_rows` 3, `rejected_rows` 1, and `reconciled_rows` 4. The final columns are `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows`.
- **Independent verification:** For sql-58 Exercise 10, confirm `accepted_rows + rejected_rows = staged_rows` and that `staged_rows` equals `SELECT COUNT(*) FROM stg_customer_ingest_solution`; the rejected row is `Customer bad`, which fails the email, country, phone, JSON, and timestamp checks at once but is counted once.
- **Intermediate relation check:** For sql-58 Exercise 10, run `classified` alone and count the rows where `accepted` is true and false before you build the summary.
- **Clause check:** `classified` adds one boolean, `accepted`, which is true only when all four flags are `IS TRUE` and the timestamp and name are present. The final `SELECT` has no `GROUP BY`, so it returns one row: a scalar subquery counts the staging table (4), `COUNT(*) FILTER (WHERE accepted IS TRUE)` gives 3, `FILTER (WHERE accepted IS NOT TRUE)` gives 1, and plain `COUNT(*)` gives 4.
- **Alternative/trade-off:** Counting the staging table in a scalar subquery makes `staged_rows` an independent control: had the procedure lost a row, `reconciled_rows` would fall below `staged_rows`. Splitting accepted rows into inserts and updates needs the write itself to report them, for example `MERGE ... RETURNING merge_action()` on PostgreSQL 17, which tags each affected row `INSERT` or `UPDATE`.
- **Edge case:** A row with several defects must still count once; adding up per-reason counts would report 5 rejections for the single bad row.
