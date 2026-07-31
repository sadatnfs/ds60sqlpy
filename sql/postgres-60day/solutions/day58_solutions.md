# Day 58 Solutions — Staging, Cleaning, and Ingestion


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day58_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day58_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Raw staging, Rejection reason, Upsert count. Its worked-model focus is:
For each timestamp format, test a format-specific regular expression before casting. Keep raw text and parsed value together, collect explicit rejection reasons, and upsert only accepted rows inside the rollback-only transaction. Return staged, valid, invalid, and affected counts that reconcile.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

## Capstone implementation — Exercise 3 ingestion procedure

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

-- The complete executable defines pg_temp.try_parse_customer_timestamp before
-- the procedure. It uses exact-format guards, round-trip checks, exception
-- handling, and STABLE volatility after SET LOCAL TIME ZONE 'UTC'. STABLE is
-- required because parsing timestamptz can depend on session settings.

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
$procedure$;

CALL ingest_customer_stage_solution(0, 0);

SELECT *
FROM cleaned_customer_ingest_solution
ORDER BY email;

ROLLBACK;
```

Expected seed results: `CALL` returns `upserted_rows = 3` and
`invalid_rows = 1`; the cleaned table retains four source rows, including the
raw malformed JSON. The accepted and rejected counts must sum to the staged
count. The whole demo rolls back, including the procedure and customer changes.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 3, stage every source row with `source_row_number` and raw text/JSON evidence; derive normalized fields plus timestamp, phone, email, and country validity flags, then upsert exactly one validated winner per normalized email.
- **Expected result/shape:** For sql-58 Exercise 3, expected output: the procedure CALL returns one row with `upserted_rows` and `invalid_rows` (3 and 1 for the seed), while the cleaned detail remains one row per staged source row with raw evidence, normalized fields, and all four validity decisions.
- **Independent verification:** For sql-58 Exercise 3, require `staged_rows = accepted_rows + rejected_rows`, every accepted row has all validity flags true, every rejection preserves `source_row_number` and raw attributes, malformed JSON never aborts the batch, valid winners reconcile to customer upserts, and rerun reaches the same final state.
- **Intermediate relation check:** For sql-58 Exercise 3, run `normalized` one at a time. Record each CTE's row count and `country`, and `segment` uniqueness before the next stage uses it.
- **Clause check:** For sql-58 Exercise 3, the solution actually uses `WITH`, `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `stg_customer_ingest_solution`, `cleaned_customer_ingest_solution`, `customers`, and `ingest_customer_stage_solution`, preserve one row per `country`, and `segment`, and finish with `full_name`, `email`, `country`, `segment`, `parsed_created_at`, `phone_digits`, `phone_valid`, `email_valid`, `country_valid`, and `attributes` ordered by `email`.
- **Alternative/trade-off:** For sql-58 Exercise 3, the chosen form is justified by this lesson-specific rationale: The procedure uses an `INOUT` pair because PostgreSQL procedures do not return a query result like table-returning functions. Evaluate another form against the concrete expected result (one row per `country`, and `segment`) and the verification above.
- **Edge case:** Add one row for which `(NOT email_valid OR NOT country_valid OR NOT phone_valid OR created_at IS NULL OR full_name IS NULL OR full_name = '') OR (email_valid AND country_valid AND phone_valid AND created_at IS NOT NULL AND full_name <> '' ON CONFLICT (email) DO UPDATE SET full_name = EXCLUDED.full_name, country = EXCLUDED.country, segment = EXCLUDED.segment, attributes = EXCLUDED.att)` is true and one for which it is false; verify only the matching `country`, and `segment` value is returned.

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

## Exercise 1 — Parse multiple datetime formats

Guard each cast with a pattern-specific CASE branch. Unrecognized text maps to
NULL and an invalid-datetime reason instead of aborting the batch.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 1, read from `stg_customers_raw`, `customers`, and `country_map`. Build the answer toward `parse_additional_datetime_formats_safely_answer`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-58 Exercise 1, expected output: one row per `customer_id`. The final columns are `parse_additional_datetime_formats_safely_answer`.
- **Independent verification:** For sql-58 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `parse_additional_datetime_formats_safely_answer` against `stg_customers_raw`, `customers`, and `country_map`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-58 Exercise 1, select `customer_id` from `stg_customers_raw`, `customers`, and `country_map` before adding derived columns.
- **Clause check:** For sql-58 Exercise 1, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `stg_customers_raw`, `customers`, and `country_map` or label it as proposed policy.
- **Alternative/trade-off:** For sql-58 Exercise 1, the chosen form is justified by this lesson-specific rationale: Guard each cast with a pattern-specific CASE branch. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Exercise 2 — Normalize phone safely

The answer removes non-digits, then applies a deliberately narrow length check.
It retains the normalized staging value but does not invent a destination
column absent from `training.customers`.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 2, read from `training.customers`. Build the answer toward `normalizevalidate_staged_phone_values_answer`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-58 Exercise 2, expected output: one row per `customer_id`. The final columns are `normalizevalidate_staged_phone_values_answer`.
- **Independent verification:** For sql-58 Exercise 2, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `normalizevalidate_staged_phone_values_answer` against `training.customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-58 Exercise 2, select `customer_id` from `training.customers` before adding derived columns.
- **Clause check:** For sql-58 Exercise 2, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `training.customers` or label it as proposed policy.
- **Alternative/trade-off:** For sql-58 Exercise 2, the chosen form is justified by this lesson-specific rationale: The answer removes non-digits, then applies a deliberately narrow length check. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Exercise 3 — Build the `INOUT` ingestion procedure

The complete transaction-safe procedure, its `CALL`, row-level evidence, and
reasoning appear in the
[capstone implementation above](#capstone-implementation--exercise-3-ingestion-procedure).
Use that runnable implementation to compare your attempt clause by clause,
including its validation rules, deterministic upsert, returned counts, and
rollback boundary.

## Exercise 4 — Choose duplicate winners deterministically

Normalize email before partitioning. Newest parsed timestamp wins, followed by
stable name/email tie-breakers; source input order never decides.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 4, rank only cleaned rows whose timestamp, phone, email, and country flags are all true; partition by normalized email and order by parsed creation time descending then `source_row_number` descending.
- **Expected result/shape:** For sql-58 Exercise 4, expected output: exactly one valid winner per `normalized_email`, with the normalized email, source row identity, parsed timestamp, and `winner_rank = 1`, ordered by normalized email.
- **Independent verification:** For sql-58 Exercise 4, assert every winner has all validity flags true, normalized emails are unique, an equal-timestamp duplicate chooses the higher `source_row_number`, an invalid newer duplicate never wins, and the winner set matches the rows used by the upsert.
- **Intermediate relation check:** For sql-58 Exercise 4, run `candidates` one at a time. Record each CTE's row count and `make_source_duplicate_winner_selection_determini` uniqueness before the next stage uses it.
- **Clause check:** For sql-58 Exercise 4, the solution actually uses `WITH`, `FROM`, `WHERE`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `stg_customer_ingest_solution`, preserve one row per `make_source_duplicate_winner_selection_determini`, and finish with `make_source_duplicate_winner_selection_determini` ordered by `normalized_email`.
- **Alternative/trade-off:** For sql-58 Exercise 4, the chosen form is justified by this lesson-specific rationale: Normalize email before partitioning. Evaluate another form against the concrete expected result (one row per `make_source_duplicate_winner_selection_determini`) and the verification above.
- **Edge case:** Add duplicate source candidates for `make_source_duplicate_winner_selection_determini`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Exercise 5 — Partition accepted and rejected outcomes

A CASE expression assigns one diagnostic outcome per cleaned row. Grouped counts
are useful for monitoring, while detail remains available for remediation.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 5, read from `cleaned_customer_ingest_solution`. Build the answer toward `outcome`, and `rows`; keep `outcome` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-58 Exercise 5, expected output: one row per `outcome`. The final columns are `outcome`, and `rows`. The final order is `outcome`.
- **Independent verification:** For sql-58 Exercise 5, independently aggregate `cleaned_customer_ingest_solution` by `outcome`; require one output row for every distinct `outcome` tuple and compare `rows` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `rows` for the existing `outcome` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-58 Exercise 5, run `classified` one at a time. Record each CTE's row count and `outcome` uniqueness before the next stage uses it.
- **Clause check:** For sql-58 Exercise 5, the solution actually uses `WITH`, `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `cleaned_customer_ingest_solution`, preserve one row per `outcome`, and finish with `outcome`, and `rows` ordered by `outcome`.
- **Alternative/trade-off:** For sql-58 Exercise 5, the chosen form is justified by this lesson-specific rationale: A CASE expression assigns one diagnostic outcome per cleaned row. Evaluate another form against the concrete expected result (one row per `outcome`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `rows` for the existing `outcome` tuple and verify the new tuple appears exactly once.

## Exercise 6 — Normalize before conflict handling

The lowercased, trimmed email is both deduplication key and target conflict key.
Case-only variants therefore compete under one declared identity.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 6, read from `cleaned_customer_ingest_solution`. Build the answer toward `normalized_email`, and `candidate_rows`; keep `email` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-58 Exercise 6, expected output: one row per `email`. The final columns are `normalized_email`, and `candidate_rows`. The final order is `email`.
- **Independent verification:** For sql-58 Exercise 6, independently aggregate `cleaned_customer_ingest_solution` by `email`; require one output row for every distinct `email` tuple and compare `candidate_rows` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `candidate_rows` for the existing `email` tuple and verify the new tuple appears exactly once.
- **Intermediate relation check:** For sql-58 Exercise 6, confirm the groups are `email`; then check `email` before applying the row cap.
- **Clause check:** For sql-58 Exercise 6, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `cleaned_customer_ingest_solution`, preserve one row per `email`, and finish with `normalized_email`, and `candidate_rows` ordered by `email`.
- **Alternative/trade-off:** For sql-58 Exercise 6, the chosen form is justified by this lesson-specific rationale: The lowercased, trimmed email is both deduplication key and target conflict key. Evaluate another form against the concrete expected result (one row per `email`) and the verification above.
- **Edge case:** Add one row to an existing group and one row for a new group; recompute `candidate_rows` for the existing `email` tuple and verify the new tuple appears exactly once.

## Exercise 7 — Separate missing and unrecognized countries

Missing raw text, recognized codes/aliases, and unknown values receive distinct
states. Raw source text remains alongside its normalized candidate for audit.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 7, read from `stg_customer_ingest_solution`. Build the answer toward `raw_country`, `normalized_candidate`, and `country_status`; keep `raw_country` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-58 Exercise 7, expected output: one row per `raw_country`. The final columns are `raw_country`, `normalized_candidate`, and `country_status`. The final order is `raw_country NULLS FIRST`.
- **Independent verification:** For sql-58 Exercise 7, reselect the returned keys directly from the source; require unique `raw_country` where the expected grain is one row per key and confirm the projected `raw_country`, `normalized_candidate`, and `country_status` against `stg_customer_ingest_solution`. Add one source row with a new `raw_country`; verify the result gains exactly one row carrying that `raw_country` value.
- **Intermediate relation check:** For sql-58 Exercise 7, check `raw_country NULLS FIRST` before applying the row cap.
- **Clause check:** For sql-58 Exercise 7, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `stg_customer_ingest_solution`, preserve one row per `raw_country`, and finish with `raw_country`, `normalized_candidate`, and `country_status` ordered by `raw_country NULLS FIRST`.
- **Alternative/trade-off:** For sql-58 Exercise 7, the chosen form is justified by this lesson-specific rationale: Missing raw text, recognized codes/aliases, and unknown values receive distinct states. Evaluate another form against the concrete expected result (one row per `raw_country`) and the verification above.
- **Edge case:** Add one source row with a new `raw_country`; verify the result gains exactly one row carrying that `raw_country` value.

## Exercise 8 — Make batch replay idempotent

`(batch_id, source_row_number)` is a stable source identity. Replaying the same
batch uses `ON CONFLICT DO NOTHING`; the count remains unchanged.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 8, read from `staged_batch_identity`, and `stg_customer_ingest_solution`. Build the answer toward `email`; keep `email` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-58 Exercise 8, expected output: one row per `email`. The final columns are `email`.
- **Independent verification:** For sql-58 Exercise 8, choose one complete partition from `staged_batch_identity`, and `stg_customer_ingest_solution`; hand-calculate its first, middle, and final window values for `row_count`, then verify output keys remain `email`. Add duplicate source candidates for `email`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-58 Exercise 8, inspect one window partition before projecting.
- **Clause check:** For sql-58 Exercise 8, the solution actually uses `FROM`, window `OVER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `staged_batch_identity`, and `stg_customer_ingest_solution`, preserve one row per `email`, and finish with `email`.
- **Alternative/trade-off:** For sql-58 Exercise 8, the chosen form is justified by this lesson-specific rationale: `(batch_id, source_row_number)` is a stable source identity. Evaluate another form against the concrete expected result (one row per `email`) and the verification above.
- **Edge case:** Add duplicate source candidates for `email`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Exercise 9 — Quarantine malformed JSON

PostgreSQL 16's `IS JSON` predicate checks text without raising. Invalid text is
kept with an `invalid_json` code instead of becoming an unexplained `{}` default.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 9, read from `stg_customer_ingest_solution`. Build the answer toward `email`, `raw_attributes`, and `json_status`; keep `email` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-58 Exercise 9, expected output: one row per `email`. The final columns are `email`, `raw_attributes`, and `json_status`. The final order is `email`.
- **Independent verification:** For sql-58 Exercise 9, reselect the returned keys directly from the source; require unique `email` where the expected grain is one row per key and confirm the projected `email`, `raw_attributes`, and `json_status` against `stg_customer_ingest_solution`. Add one source row with a new `email`; verify the result gains exactly one row carrying that `email` value.
- **Intermediate relation check:** For sql-58 Exercise 9, check `email` before applying the row cap.
- **Clause check:** For sql-58 Exercise 9, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `stg_customer_ingest_solution`, preserve one row per `email`, and finish with `email`, `raw_attributes`, and `json_status` ordered by `email`.
- **Alternative/trade-off:** For sql-58 Exercise 9, the chosen form is justified by this lesson-specific rationale: PostgreSQL 16's `IS JSON` predicate checks text without raising. Evaluate another form against the concrete expected result (one row per `email`) and the verification above.
- **Edge case:** Add one source row with a new `email`; verify the result gains exactly one row carrying that `email` value.

## Exercise 10 — Reconcile every row outcome

Staged count must equal accepted plus rejected count. The procedure's affected
row count does not distinguish inserts from updates, so a production contract
needs explicit merge/audit evidence for those sub-outcomes.

### Reasoning and verification

- **Inputs/evidence:** For sql-58 Exercise 10, read from `cleaned_customer_ingest_solution`, and `stg_customer_ingest_solution`. Build the answer toward `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows`; keep `staged_rows` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-58 Exercise 10, expected output: one row per `staged_rows`. The final columns are `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows`.
- **Independent verification:** For sql-58 Exercise 10, reselect the returned keys directly from the source; require unique `staged_rows` where the expected grain is one row per key and confirm the projected `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows` against `cleaned_customer_ingest_solution`, and `stg_customer_ingest_solution`. Add one source row with a new `staged_rows`; verify the result gains exactly one row carrying that `staged_rows` value.
- **Intermediate relation check:** For sql-58 Exercise 10, run `classified` one at a time. Record each CTE's row count and `staged_rows` uniqueness before the next stage uses it.
- **Clause check:** For sql-58 Exercise 10, the solution actually uses `WITH`, `FROM`, `WHERE`, aggregate `FILTER`, and `SELECT`. Read only those operations: begin at `cleaned_customer_ingest_solution`, and `stg_customer_ingest_solution`, preserve one row per `staged_rows`, and finish with `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows`.
- **Alternative/trade-off:** For sql-58 Exercise 10, the chosen form is justified by this lesson-specific rationale: Staged count must equal accepted plus rejected count. Evaluate another form against the concrete expected result (one row per `staged_rows`) and the verification above.
- **Edge case:** Add one source row with a new `staged_rows`; verify the result gains exactly one row carrying that `staged_rows` value.
