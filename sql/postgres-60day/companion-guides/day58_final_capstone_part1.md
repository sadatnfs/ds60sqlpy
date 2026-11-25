# Day 58: Final Capstone, Part 1: Ingestion and Data Quality

## How to run this lesson

In `./classroom`, choose PostgreSQL, open **sql-58** and run it with
**Whole SQL lesson (psql)**. The learner file is rollback-only: it opens
`BEGIN` in `advanced_sql_training`, sets `search_path` to `training, public`,
lands three messy customer rows in a temporary staging table, cleans and
validates them, upserts the good ones into `customers` and ends with
`ROLLBACK`, so `customers` still holds its 500 fixture rows afterward. Your
editable copy is
`.learning/sql/sql-58/lesson/workspace/sql/postgres-60day/day58_final_capstone_part1.sql`
in the Docker learning volume. A clean run prints `BEGIN`, `SET`,
`CREATE TABLE`, `INSERT 0 3`, a three-row cleaned grid, `INSERT 0 2` from the
upsert, a one-row data-quality count, `CREATE TABLE` and `INSERT 0 10` for the
country map, a three-row mapping grid and `ROLLBACK`. Run the file as a whole:
pasting the upsert on its own, outside the `BEGIN`, would commit customers 501
and 502 for real, and every later run would then insert nothing because
`ON CONFLICT (email) DO NOTHING` finds them. `psql` stops at the first error and
the open transaction dies with it. Launch and reset steps are in the
[classroom section of the study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom);
a JupyterLab alternative is described under the
[contributor notebook route](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 57; trends and anomalies](day57_project4_bi_part3.md) Day 57 finished the BI project on clean warehouse tables; Day 58 starts one step earlier, with customer text nobody has cleaned yet.
- **Artifacts:** [learner SQL](../day58_final_capstone_part1.sql) ·
  [solution reasoning](../solutions/day58_solutions.md) ·
  [executable solution](../solutions/day58_solutions.sql)

## A beginner's mental model for this lesson

Every value in a real feed arrives as text, and some of it is wrong. Day 58's
learner file lands three customers whose problems are visible on sight:
`'  Customer 501  '` is padded, `'CUSTOMER501@EXAMPLE.COM '` is upper case with
a trailing space, `' us '` is a padded lowercase country, `'03-01-2025'` is a
date whose day and month could be read either way, and `'invalid-email'` is
not an address at all.

**Raw staging** means landing that text exactly as received, in a table whose
six columns are all `TEXT`, so the load itself cannot fail on a bad date or
broken JSON. Cleaning then happens in queries that read the staging table and
leave it untouched, so a reviewer can always set `' us '` beside the `US` it
became.

A **rejection reason** names why a row was not accepted. The learner file only
computes two flags, `email_valid` and `country_valid`; customer 503 gets
`email_valid` false and the upsert skips it without a word. The solution goes
further and labels each staged row with one outcome such as `invalid_email` or
`accepted`, so a rejected row can be explained and repaired instead of
vanishing.

The **upsert count** is the number `INSERT ... ON CONFLICT` reports. The
learner upsert prints `INSERT 0 2`: the emails of customers 501 and 502 are new,
and 503 never reaches the insert because the `WHERE` drops it. With
`DO NOTHING`, repeating that statement inside the same transaction would print
`INSERT 0 0`. The solution's `DO UPDATE` reports 3 on every repeat instead,
because an updated row counts the same as an inserted one.

Read the cleaning query in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order):
`FROM stg_customers_raw` supplies three rows, the `cleaned` CTE rewrites each
column without changing the count, and `validated` adds two boolean columns.
The grid statement never filters. The upsert repeats both CTEs inside a
derived table `v` and filters only at `WHERE v.email_valid AND v.country_valid`.
Three rows in, three rows on screen, two rows written.

## Two worked SQL examples

Both excerpts are the first two statements after
`SET search_path TO training, public` in `day58_final_capstone_part1.sql`.
They run inside the file's `BEGIN`, and the staging table is `TEMP`, so it
would disappear at the end of the session even without the closing `ROLLBACK`.

### Example 1

```sql
CREATE TEMP TABLE stg_customers_raw (
  full_name TEXT,
  email TEXT,
  country TEXT,
  segment TEXT,
  created_at TEXT,
  attributes TEXT
);
```

**How to read it:** `CREATE TEMP TABLE` builds a session-only table. Every column, including
`created_at` and `attributes`, is `TEXT` on purpose: a `timestamptz` column
would interpret `'03-01-2025'` under the session `DateStyle` at load time (as
1 March 2025 in an `ISO, MDY` session), and a `jsonb` column would refuse a
malformed document before anyone could record why. Typing waits for the
cleaning query, where each conversion is guarded.

**Expected result/shape:** `psql` prints `CREATE TABLE` and no grid. Running `\d stg_customers_raw` right
after it lists six nullable `text` columns with no key and no constraint, so
nothing about this table can turn an input row away.

### Example 2

```sql
INSERT INTO stg_customers_raw (full_name, email, country, segment, created_at, attributes)
VALUES
  ('  Customer 501  ', 'CUSTOMER501@EXAMPLE.COM ', ' us ', ' GOLD ', '2025/01/03 10:00', '{"channel":"Web","referrer":"SEO"}'),
  ('Customer 502', 'customer-502@example.com', 'GB', NULL, '03-01-2025', '{"channel":"mobile","referrer":"email"}'),
  ('Customer 503', 'invalid-email', 'DE', 'silver', '2025-01-05T12:34:56Z', '{"channel":"store"}');
```

**How to read it:** The three `VALUES` rows are the test cases for everything after them. Row 1
has padding or case problems in its name, email, country and segment; row 2
has a `NULL` segment and the ambiguous date; row 3 has a well-formed ISO
timestamp ending in `Z` but an email with no `@`. Each attributes string is
valid JSON, so the learner's `::jsonb` cast succeeds. Put `'not-json'` in that
column and the cast would stop the whole file.

**Expected result/shape:** `psql` prints `INSERT 0 3`. The cleaned grid that follows shows what those rows
become in a UTC session: 501 as `customer501@example.com`, `US`, segment
`GOLD` (trimmed but still upper case) and 2025-01-03 10:00; 502 with segment
`NULL` and `created_at` 2025-01-03 00:00, because the `DD-MM-YYYY` branch
reads `'03-01-2025'` as 3 January; 503 with 2025-01-05 12:34:56 and
`email_valid` false. All three rows have `country_valid` true.

## Learning objectives

- Preserve raw staged input while deriving validated, normalized fields.
- Package a repeatable stage/validate/upsert flow with observable counts.

## Vocabulary and concepts

- **Raw staging:** an input-preserving landing area before typed transformation.
- **Rejection reason:** a stable explanation for why a record was not accepted.
- **Upsert count:** affected rows under the interface's defined insert/update
  semantics.

## Worked example / walkthrough

For each timestamp format, test a format-specific regular expression before
casting. Keep raw text and parsed value together, collect explicit rejection
reasons, and upsert only accepted rows inside the rollback-only transaction.
Return staged, valid, invalid, and affected counts that reconcile.

## Exercises

Complete these in the [learner SQL](../day58_final_capstone_part1.sql):

1. Parse additional datetime formats safely.
   **Inputs/evidence:** For sql-58 Exercise 1, parse the four staged `created_at` strings in `stg_customer_ingest_solution` with the temporary function `pg_temp.try_parse_customer_timestamp`, which accepts `YYYY/MM/DD HH24:MI`, `MM/DD/YYYY HH24:MI`, `DD-Mon-YYYY HH24:MI`, and ISO `YYYY-MM-DD HH24:MI` text and returns NULL for anything else.
   **Expected result/shape:** For sql-58 Exercise 1, expected output: in `cleaned_customer_ingest_solution`, `created_at` is 2026-01-03 10:00, 2026-01-15 08:30, and 2026-01-15 12:00 UTC for the first three staged rows and NULL for `not-a-date`.
   **Verify:** For sql-58 Exercise 1, call the function directly with the session time zone set to UTC on `'2026/01/03 10:00'`, `'01/15/2026 08:30'`, `'15-Jan-2026 12:00'`, and `'not-a-date'` and expect the three timestamps above and NULL; the impossible date `'2026/02/30 10:00'` must also return NULL, whereas a plain `to_timestamp('2026/02/30 10:00', 'YYYY/MM/DD HH24:MI')` raises `date/time field value out of range` and would abort the batch.
   **Data check:** In a UTC session the function returns `NULL` for `'2026/02/30 10:00'`, `'2026/13/01 10:00'`, `'2026/01/03 25:00'` and `'2026/1/3 10:00'` (its regex wants two-digit months and days), while `'15-JAN-2026 12:00'` parses because the month comparison ignores case. Outside the function, PostgreSQL 17's plain `to_timestamp('2026/02/30 10:00', 'YYYY/MM/DD HH24:MI')` raises `date/time field value out of range` rather than rolling into March, so the unguarded risk is an aborted batch.
2. Normalize/validate staged phone values.
   **Inputs/evidence:** For sql-58 Exercise 2, strip every non-digit from the staged `phone` with `regexp_replace(phone, '[^0-9]', '', 'g')` and flag the result valid when it has 10 to 15 digits (`phone_digits ~ '^[0-9]{10,15}$'`).
   **Expected result/shape:** For sql-58 Exercise 2, expected output: `phone_digits` 4155550101, 442079460958, 0301234567, and 123, with `phone_valid` true, true, true, and false, stored in `cleaned_customer_ingest_solution`.
   **Verify:** For sql-58 Exercise 2, confirm that `SELECT phone_digits, phone_valid FROM cleaned_customer_ingest_solution ORDER BY source_row_number` returns those four pairs and that only the `123` row is invalid; then test `'+1 (415) 555-0101 ext. 9'`, which becomes 141555501019 and still passes the length rule, so an extension needs its own handling.
   **Data check:** The leading zero of `030-1234567` survives as `0301234567` because `phone_digits` is text, and `+44 20 7946 0958` keeps its 12 digits but loses the `+`. Only `123`, with 3 digits, fails.
3. Build a transactional ingest procedure with DQ counts.
   **Inputs/evidence:** For sql-58 Exercise 3, stage every source row with `source_row_number` and raw text/JSON evidence; derive normalized name, email, country and segment, the parsed `created_at`, and the `phone_valid`, `email_valid`, `country_valid` and `json_valid` flags, then upsert exactly one validated winner per normalized email.
   **Expected result/shape:** For sql-58 Exercise 3, expected output: the procedure CALL returns one row with `upserted_rows` and `invalid_rows` (3 and 1 for the seed), while the cleaned detail remains one row per staged source row with raw evidence, normalized fields, and all four validity decisions.
   **Verify:** For sql-58 Exercise 3, confirm that `customers` goes from 500 to 503 rows after the first `CALL` and that `upserted_rows` 3 plus `invalid_rows` 1 equals the 4 staged rows; a second `CALL` in the same transaction prints 3 and 1 again and leaves 503 rows. Then stage a valid newer `customer601@example.com` row and `CALL` again: the pair stays 3 and 1 over 5 staged rows, `customers` still has 503 rows, and the stored name becomes the new row's, so the losing duplicate needs its own count.
   **Data check:** Each `CALL` prints one row, `upserted_rows` 3 and `invalid_rows` 1. A second `CALL` in the same transaction prints the same pair, but now all three are updates of the rows the first call inserted, and `customers` still holds 503 rows. Stage a valid duplicate of `customer601` and the pair stays 3 and 1 over 5 staged rows: the duplicate that loses the ranking is counted nowhere.
4. Make source-duplicate winner selection deterministic.
   **Inputs/evidence:** For sql-58 Exercise 4, rank only cleaned rows whose email, country, phone, and JSON flags are all true and whose parsed timestamp and name are present; partition by normalized email and order by parsed creation time descending then `source_row_number` descending.
   **Expected result/shape:** For sql-58 Exercise 4, expected output: exactly one valid winner per `normalized_email`, with the normalized email, source row identity, parsed timestamp, and `winner_rank = 1`, ordered by normalized email.
   **Verify:** For sql-58 Exercise 4, assert every winner has all validity flags true, normalized emails are unique, an equal-timestamp duplicate chooses the higher `source_row_number`, an invalid newer duplicate never wins, and the winner set matches the rows used by the upsert.
   **Data check:** On the seed every email is distinct, so the result is 3 winners: customer601, customer602 and customer603 from source rows 1, 2 and 3, each with `winner_rank` 1. Staging `'Customer601@example.com'` with row 1's timestamp makes the new row the winner on its higher `source_row_number`; staging a newer `customer601` row with phone `'12'` changes nothing, because the filter removes it before ranking.
5. Split accepted/rejected rows with reason codes and reconcile counts.
   **Inputs/evidence:** For sql-58 Exercise 5, label each row of `cleaned_customer_ingest_solution` with one `outcome` from a `CASE` that tests name, email, country, timestamp, phone and JSON in that order and otherwise returns `accepted`, then count the rows per `outcome`.
   **Expected result/shape:** For sql-58 Exercise 5, expected output: two rows on the seed, `accepted` 3 and `invalid_email` 1, whose `rows` sum to the 4 staged rows. The final columns are `outcome` and `rows`. The final order is `outcome`.
   **Verify:** For sql-58 Exercise 5, confirm the `rows` values sum to `SELECT COUNT(*) FROM stg_customer_ingest_solution` (4) and that source row 4, which fails the email, country, timestamp, phone and JSON checks, is counted once as `invalid_email`; then, inside a savepoint, set `email_valid = true` for source row 4 in the cleaned table and rerun: the result becomes `accepted` 3 and `invalid_country` 1.
   **Data check:** The seed gives two outcome rows, `accepted` 3 and `invalid_email` 1. `Customer bad` fails five checks, but the `CASE` reports only the first one it reaches after the name test, which is email.
6. Normalize email before deduplication.
   **Inputs/evidence:** For sql-58 Exercise 6, group `cleaned_customer_ingest_solution`, whose `email` is already `lower(trim(...))`, by that normalized `email` and count the candidate rows per address.
   **Expected result/shape:** For sql-58 Exercise 6, expected output: 4 rows, one per normalized `email`, each with `candidate_rows` 1 on the staged data. The final columns are `normalized_email` and `candidate_rows`. The final order is `email`.
   **Verify:** For sql-58 Exercise 6, confirm that the staged `CUSTOMER601@EXAMPLE.COM ` (upper case with a trailing space) appears as `customer601@example.com`; on `VALUES ('A@x.com'), ('a@x.com ')`, `COUNT(DISTINCT e)` is 2 but `COUNT(DISTINCT lower(trim(e)))` is 1, which is the duplicate that normalization must catch before deduplication.
   **Data check:** All four normalized emails, `not-an-email` included, appear once with `candidate_rows` 1, because this grouping does not filter on validity.
7. Distinguish missing from unrecognized countries and retain raw values.
   **Inputs/evidence:** For sql-58 Exercise 7, list every row of `stg_customer_ingest_solution` with its raw `country`, a normalized candidate (`USA` and `U S` become `US`, blank text becomes NULL) and a status that is `missing` for NULL or blank text, `recognized` for a known code or alias, and `unrecognized` otherwise.
   **Expected result/shape:** For sql-58 Exercise 7, expected output: 4 rows, one per staged row: `DE`/`DE`, `GB`/`GB` and `USA`/`US` are `recognized` and `XX`/`XX` is `unrecognized`. The final columns are `raw_country`, `normalized_candidate`, and `country_status`. The final order is `raw_country NULLS FIRST`.
   **Verify:** For sql-58 Exercise 7, confirm the 4 rows match `SELECT country FROM stg_customer_ingest_solution` and that no seed row is `missing`; then, inside a savepoint, stage one row with a NULL country and one with `' '` and expect 6 rows, the NULL row first and the blank row second, both `missing` with a NULL candidate, while `XX` stays `unrecognized`.
   **Data check:** The seed prints four rows: `DE`/`DE`, `GB`/`GB`, `USA`/`US` and `XX`/`XX`, the first three `recognized` and `XX` `unrecognized`. No seed country is missing; staging a `NULL` or `' '` country adds a `missing` row with a `NULL` candidate at the top.
8. Add source batch/row identity and make replay idempotent.
   **Inputs/evidence:** For sql-58 Exercise 8, load the four staged rows into `staged_batch_identity`, keyed by (`batch_id`, `source_row_number`), twice with `INSERT ... ON CONFLICT (batch_id, source_row_number) DO NOTHING`, then count the stored rows.
   **Expected result/shape:** For sql-58 Exercise 8, expected output: `INSERT 0 4` for the first load, `INSERT 0 0` for the replay, and one row with `replay_safe_rows` 4. The final columns are `replay_safe_rows`.
   **Verify:** For sql-58 Exercise 8, confirm that the replay inserts nothing and that `SELECT COUNT(*) FROM staged_batch_identity` equals `SELECT COUNT(*) FROM stg_customer_ingest_solution` (4); load the same rows under a new `batch_id` and expect 8 rows, because the key identifies a batch and a source row, not a customer.
   **Data check:** The first load prints `INSERT 0 4`, the replay `INSERT 0 0`, and `replay_safe_rows` is 4. The stored `email` is the raw staged text, so the identity row for source row 1 still reads `'CUSTOMER601@EXAMPLE.COM '`.
9. Quarantine malformed JSON without aborting the batch.
   **Inputs/evidence:** For sql-58 Exercise 9, read the raw `email` and `attributes` text of each `stg_customer_ingest_solution` row and label it `valid_json` when `attributes IS JSON` is true and `invalid_json` otherwise, without casting the text.
   **Expected result/shape:** For sql-58 Exercise 9, expected output: 4 rows, one per staged row, ordered by raw `email` from `'CUSTOMER601@EXAMPLE.COM '`: three `valid_json` rows and `not-an-email` with `raw_attributes` `not-json` and `invalid_json`. The final columns are `email`, `raw_attributes`, and `json_status`. The final order is `email`.
   **Verify:** For sql-58 Exercise 9, confirm that `SELECT 'not-json'::jsonb` raises `invalid input syntax for type json` inside a savepoint while this query returns all 4 rows; then stage a row with NULL attributes and expect `invalid_json`, because `NULL IS JSON` is NULL and falls to the `ELSE` branch.
   **Data check:** The four rows come back ordered by raw email, starting with `'CUSTOMER601@EXAMPLE.COM '`; three read `valid_json` and the `not-json` row reads `invalid_json` with its raw text still visible, which is the quarantine evidence.
10. Reconcile staged, accepted, rejected, inserted, and updated outcomes.
   **Inputs/evidence:** For sql-58 Exercise 10, classify every row of `cleaned_customer_ingest_solution` as accepted only when its email, country, phone, JSON, timestamp, and name checks all pass, then count staged, accepted, and rejected rows and their reconciled sum.
   **Expected result/shape:** For sql-58 Exercise 10, expected output: one row with `staged_rows` 4, `accepted_rows` 3, `rejected_rows` 1, and `reconciled_rows` 4. The final columns are `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows`.
   **Verify:** For sql-58 Exercise 10, confirm `accepted_rows + rejected_rows = staged_rows` and that `staged_rows` equals `SELECT COUNT(*) FROM stg_customer_ingest_solution`; the rejected row is `Customer bad`, which fails the email, country, phone, JSON, and timestamp checks at once but is counted once.
   **Data check:** The single row reads 4, 3, 1 and 4. `Customer bad` fails five checks yet adds only 1 to `rejected_rows`, because acceptance is one boolean per row.

Malformed inputs must become explained rejections.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** checking quality on raw text while
  loading cleaned text. The learner's data-quality query reads
  `stg_customers_raw` directly and reports `invalid_email` 2 and
  `invalid_country` 1, yet the upsert has just accepted customer 501. The raw
  `'CUSTOMER501@EXAMPLE.COM '` fails the regex only because of its trailing
  space, and `upper(' us ')` is `' US '`, which is not in the country list.
  Count rejections from the same cleaned relation the load reads.
- **A date that parses to the wrong day:** the learner's `DD-MM-YYYY` branch
  turns `'03-01-2025'` into 3 January, while a plain cast in an `ISO, MDY`
  session gives 1 March 2025. Neither raises an error, so only a declared
  format per source protects you.
- **One bad JSON string ends the run:** the learner's
  `COALESCE(NULLIF(trim(attributes), ''), '{}')::jsonb` replaces only `NULL`
  or blank text. `'not-json'` raises `invalid input syntax for type json`
  (SQLSTATE 22P02), and under `ON_ERROR_STOP` the transaction is gone. Test
  with `attributes IS JSON` first, as the solution does.
- **Two staged rows for one email:** `ON CONFLICT (email) DO UPDATE` fails with
  `ON CONFLICT DO UPDATE command cannot affect row a second time`, while
  `DO NOTHING` succeeds and keeps whichever duplicate the insert reaches first.
  Rank the rows and send one winner per email.
- **A `NULL` flag that is neither accepted nor rejected:** in the learner file a
  `NULL` email gives a `NULL` `email_valid`, the upsert's `WHERE` drops the
  row, and the data-quality `CASE WHEN NOT (...)` counts it as 0. The solution
  writes `IS TRUE` for acceptance and `IS NOT TRUE` for rejection, so every row
  lands in exactly one bucket.
- **`psql` stopped partway:** read the first error, rerun the whole file from
  `BEGIN`, and use the
  [failure recovery checklist](../../STUDY-GUIDE.md#recover-from-common-failures)
  for container or path problems.

## Self-check

- Can every normalized value be traced to preserved raw input?
- Do count summaries reconcile, and are schema additions kept out of an
  unreviewed tutorial upsert?

## Next step

Continue to [Day 59; stakeholder analytics](day59_final_capstone_part2.md).

## Deep dive and reference

## Capstone focus

- Stage messy customer text without losing the raw input.
- Normalize names, email, country, segment, timestamps, JSON, and phone.
- Validate records, upsert accepted customers, and return a DQ summary.

## How the learner script works

The rollback-only starter creates `stg_customers_raw`, inserts three varied
records, parses three timestamp patterns, validates email/country, upserts valid
rows by unique email, reports invalid counts, and demonstrates a country map.

## Practice map

The ten numbered exercises above are the practice set. The first three are the
capstone deliverables and build on each other: the parser and the phone rule
feed the cleaned table that the ingestion procedure fills. Exercises 4 to 10
then read that cleaned table, or the staging table behind it, after one `CALL`,
so build and call the procedure before attempting them. A workable order after
the procedure is 6 then 4 (normalize, then rank), 7 and 9 (keep the evidence
for quarantined values), 5 and 10 (count outcomes), and 8 (replay) last. The
data checks quote numbers from the solution's four seed rows, so load those
rows when you want to compare.

## Pipeline reasoning

- Guard every timestamp cast with a format-specific regex; ambiguous dates need
  an explicit locale policy.
- Preserve rejection reasons and raw text in a real pipeline.
- Normalize before comparing unique email values.
- `ON CONFLICT (email)` counts affected inserts/updates but does not distinguish
  them without additional logic.
- The learner file defaults only `NULL` or blank attributes to `{}`; invalid
  text such as `'not-json'` makes its `::jsonb` cast fail. The solution keeps
  the raw string, stores `NULL` and sets `json_valid` false instead.

## Schema and safety limits

`training.customers` has no phone column. Validate phone in staging, but do not
invent a destination. Persisting phone requires a reviewed schema migration.
The sample phone regex is intentionally narrow and is not global normalization.

Keep the entire demonstration in a transaction and roll it back. A procedure is
appropriate for side effects and can expose `INOUT` counts; a table-returning
function would be a different interface.

## Ask an AI tutor about this lesson

Working with an AI tutor is optional; this guide, the learner file and
PostgreSQL cover the whole lesson. The
[tutor section of the study guide](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)
lists what to share. The most useful drill here is prediction: have the tutor
invent a messy staged row and tell it which flag, outcome and counter the row
will land in before you run anything. Send it this once the four seed rows make
sense to you:

```text
Tutor me through sql-58: Final Capstone, Part 1: Ingestion and Data Quality.

I have completed the direct catalog prerequisite: `sql-57`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day58_final_capstone_part1.md
- Answer-free learner SQL: sql/postgres-60day/day58_final_capstone_part1.sql

Key terms to teach in context: Raw staging, Rejection reason, Upsert count. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For each timestamp format, test a format-specific regular expression before casting. Keep raw text and parsed value together, collect explicit rejection reasons, and upsert only accepted rows inside the rollback-only transaction. Return staged, valid, invalid, and affected counts that reconcile.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-58/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
