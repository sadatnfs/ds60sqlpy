# Day 58 — Final Capstone, Part 1: Ingestion and Data Quality

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 57 — trends and anomalies](day57_project4_bi_part3.md)
- **Artifacts:** [learner SQL](../day58_final_capstone_part1.sql) ·
  [solution reasoning](../solutions/day58_solutions.md) ·
  [executable solution](../solutions/day58_solutions.sql)

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-58 — Final Capstone Part1** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-58/lesson/workspace/sql/postgres-60day/day58_final_capstone_part1.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day58_final_capstone_part1.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day58_final_capstone_part1.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Raw staging, Rejection reason, Upsert count. Its worked SQL reads or creates `stg_customers_raw`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: For each timestamp format, test a format-specific regular expression before casting. Keep raw text and parsed value together, collect explicit rejection reasons, and upsert only accepted rows inside the rollback-only transaction. Return staged, valid, invalid, and affected counts that reconcile.
The first runnable example has a concrete contract: Example 1 must complete through `psql` with its documented command tag or notice for the lesson evidence named below. Treat an unexpected error as failure, and prove the stated catalog/behavior invariant plus cleanup. Its final projection is the columns written in the final `SELECT`. Reselect the returned key columns from the columns written in the final `SELECT`, reject duplicate keys when the grain is one row per entity, and check the stated row cap and sort direction only when this example includes them.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day58_final_capstone_part1.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TEMP TABLE stg_customers_raw (
  full_name TEXT,
  email     TEXT,
  country   TEXT,
  segment   TEXT,
  created_at TEXT,
  attributes TEXT
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must complete through `psql` with its documented command tag or notice for the lesson evidence named below. Treat an unexpected error as failure, and prove the stated catalog/behavior invariant plus cleanup.

### Example 2

```sql
INSERT INTO stg_customers_raw(full_name, email, country, segment, created_at, attributes)
VALUES
  ('  Customer 501  ', 'CUSTOMER501@EXAMPLE.COM ', ' us ', ' GOLD ', '2025/01/03 10:00', '{"channel":"Web","referrer":"SEO"}'),
  ('Customer 502', 'customer-502@example.com', 'GB', NULL, '03-01-2025', '{"channel":"mobile","referrer":"email"}'),
  ('Customer 503', 'invalid-email', 'DE', 'silver', '2025-01-05T12:34:56Z', '{"channel":"store"}');
```

**How to read it:** Example 2 changes rows inside the lesson's declared transaction. The command tag reports affected rows, but a follow-up query must prove the intended before/after invariant.

**Expected result/shape:** Example 2 must complete through `psql` with its documented command tag or notice for `stg_customers_raw`. Treat an unexpected error as failure, and prove the stated catalog/behavior invariant plus cleanup.

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
   **Inputs/evidence:** For sql-58 Exercise 1, read from `stg_customers_raw`, `customers`, and `country_map`. Build the answer toward `parse_additional_datetime_formats_safely_answer`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-58 Exercise 1, expected output: one row per `customer_id`. The final columns are `parse_additional_datetime_formats_safely_answer`.
   **Verify:** For sql-58 Exercise 1, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `parse_additional_datetime_formats_safely_answer` against `stg_customers_raw`, `customers`, and `country_map`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
2. Normalize/validate staged phone values.
   **Inputs/evidence:** For sql-58 Exercise 2, read from `training.customers`. Build the answer toward `normalizevalidate_staged_phone_values_answer`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-58 Exercise 2, expected output: one row per `customer_id`. The final columns are `normalizevalidate_staged_phone_values_answer`.
   **Verify:** For sql-58 Exercise 2, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `normalizevalidate_staged_phone_values_answer` against `training.customers`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
3. Build a transactional ingest procedure with DQ counts.
   **Inputs/evidence:** For sql-58 Exercise 3, read from `stg_customer_ingest_solution`, `cleaned_customer_ingest_solution`, `customers`, and `ingest_customer_stage_solution`. Build the answer toward `full_name`, `email`, `country`, `segment`, `parsed_created_at`, `phone_digits`, `phone_valid`, `email_valid`, `country_valid`, and `attributes`; keep `country`, and `segment` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-58 Exercise 3, expected output: one row per `country`, and `segment`. The final columns are `full_name`, `email`, `country`, `segment`, `parsed_created_at`, `phone_digits`, `phone_valid`, `email_valid`, `country_valid`, and `attributes`. The final order is `email`.
   **Verify:** For sql-58 Exercise 3, run an anti-check that counts rows where NOT ((NOT email_valid OR NOT country_valid OR NOT phone_valid OR created_at IS NULL OR full_name IS NULL OR full_name = '') OR (email_valid AND country_valid AND phone_valid AND created_at IS NOT NULL AND full_name <> '' ON CONFLICT (email) DO UPDATE SET full_name = EXCLUDED.full_name, country = EXCLUDED.country, segment = EXCLUDED.segment, attributes = EXCLUDED.att)); require unique `country`, and `segment` where the expected grain is one row per key and confirm the projected `full_name`, `email`, `country`, `segment`, `parsed_created_at`, `phone_digits`, `phone_valid`, `email_valid`, `country_valid`, and `attributes` against `stg_customer_ingest_solution`, `cleaned_customer_ingest_solution`, `customers`, and `ingest_customer_stage_solution`. Add one row for which `(NOT email_valid OR NOT country_valid OR NOT phone_valid OR created_at IS NULL OR full_name IS NULL OR full_name = '') OR (email_valid AND country_valid AND phone_valid AND created_at IS NOT NULL AND full_name <> '' ON CONFLICT (email) DO UPDATE SET full_name = EXCLUDED.full_name, country = EXCLUDED.country, segment = EXCLUDED.segment, attributes = EXCLUDED.att)` is true and one for which it is false; verify only the matching `country`, and `segment` value is returned.
4. Make source-duplicate winner selection deterministic.
   **Inputs/evidence:** For sql-58 Exercise 4, read from `stg_customer_ingest_solution`. Build the answer toward `make_source_duplicate_winner_selection_determini`; keep `make_source_duplicate_winner_selection_determini` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-58 Exercise 4, expected output: one row per `make_source_duplicate_winner_selection_determini`. The final columns are `make_source_duplicate_winner_selection_determini`. The final order is `normalized_email`.
   **Verify:** For sql-58 Exercise 4, run an anti-check that counts rows where NOT ((winner_rank = 1)); require unique `make_source_duplicate_winner_selection_determini` where the expected grain is one row per key and confirm the projected `make_source_duplicate_winner_selection_determini` against `stg_customer_ingest_solution`. Add duplicate source candidates for `make_source_duplicate_winner_selection_determini`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
5. Split accepted/rejected rows with reason codes and reconcile counts.
   **Inputs/evidence:** For sql-58 Exercise 5, read from `cleaned_customer_ingest_solution`. Build the answer toward `outcome`, and `rows`; keep `outcome` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-58 Exercise 5, expected output: one row per `outcome`. The final columns are `outcome`, and `rows`. The final order is `outcome`.
   **Verify:** For sql-58 Exercise 5, independently aggregate `cleaned_customer_ingest_solution` by `outcome`; require one output row for every distinct `outcome` tuple and compare `rows` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `rows` for the existing `outcome` tuple and verify the new tuple appears exactly once.
6. Normalize email before deduplication.
   **Inputs/evidence:** For sql-58 Exercise 6, read from `cleaned_customer_ingest_solution`. Build the answer toward `normalized_email`, and `candidate_rows`; keep `email` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-58 Exercise 6, expected output: one row per `email`. The final columns are `normalized_email`, and `candidate_rows`. The final order is `email`.
   **Verify:** For sql-58 Exercise 6, independently aggregate `cleaned_customer_ingest_solution` by `email`; require one output row for every distinct `email` tuple and compare `candidate_rows` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `candidate_rows` for the existing `email` tuple and verify the new tuple appears exactly once.
7. Distinguish missing from unrecognized countries and retain raw values.
   **Inputs/evidence:** For sql-58 Exercise 7, read from `stg_customer_ingest_solution`. Build the answer toward `raw_country`, `normalized_candidate`, and `country_status`; keep `raw_country` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-58 Exercise 7, expected output: one row per `raw_country`. The final columns are `raw_country`, `normalized_candidate`, and `country_status`. The final order is `raw_country NULLS FIRST`.
   **Verify:** For sql-58 Exercise 7, reselect the returned keys directly from the source; require unique `raw_country` where the expected grain is one row per key and confirm the projected `raw_country`, `normalized_candidate`, and `country_status` against `stg_customer_ingest_solution`. Add one source row with a new `raw_country`; verify the result gains exactly one row carrying that `raw_country` value.
8. Add source batch/row identity and make replay idempotent.
   **Inputs/evidence:** For sql-58 Exercise 8, read from `staged_batch_identity`, and `stg_customer_ingest_solution`. Build the answer toward `email`; keep `email` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-58 Exercise 8, expected output: one row per `email`. The final columns are `email`.
   **Verify:** For sql-58 Exercise 8, choose one complete partition from `staged_batch_identity`, and `stg_customer_ingest_solution`; hand-calculate its first, middle, and final window values for `row_count`, then verify output keys remain `email`. Add duplicate source candidates for `email`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
9. Quarantine malformed JSON without aborting the batch.
   **Inputs/evidence:** For sql-58 Exercise 9, read from `stg_customer_ingest_solution`. Build the answer toward `email`, `raw_attributes`, and `json_status`; keep `email` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-58 Exercise 9, expected output: one row per `email`. The final columns are `email`, `raw_attributes`, and `json_status`. The final order is `email`.
   **Verify:** For sql-58 Exercise 9, reselect the returned keys directly from the source; require unique `email` where the expected grain is one row per key and confirm the projected `email`, `raw_attributes`, and `json_status` against `stg_customer_ingest_solution`. Add one source row with a new `email`; verify the result gains exactly one row carrying that `email` value.
10. Reconcile staged, accepted, rejected, inserted, and updated outcomes.
   **Inputs/evidence:** For sql-58 Exercise 10, read from `cleaned_customer_ingest_solution`, and `stg_customer_ingest_solution`. Build the answer toward `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows`; keep `staged_rows` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-58 Exercise 10, expected output: one row per `staged_rows`. The final columns are `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows`.
   **Verify:** For sql-58 Exercise 10, reselect the returned keys directly from the source; require unique `staged_rows` where the expected grain is one row per key and confirm the projected `staged_rows`, `accepted_rows`, `rejected_rows`, and `reconciled_rows` against `cleaned_customer_ingest_solution`, and `stg_customer_ingest_solution`. Add one source row with a new `staged_rows`; verify the result gains exactly one row carrying that `staged_rows` value.

Malformed inputs must become explained rejections.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: For each timestamp format, test a format-specific regular expression before casting. Keep raw text and parsed value together, collect explicit rejection reasons, and upsert only accepted rows inside the rollback-only transaction. Return staged, valid, invalid, and affected counts that reconcile.
- **Unexpected row count:** display keys before aggregates, count rows after
  each join/filter stage, and find the first stage whose grain differs from the
  contract. Do not hide fanout with `DISTINCT`.
- **Unexpected `NULL` or missing row:** decide whether the fact is unknown,
  inapplicable, zero, or absent before using `COALESCE`; inspect outer-join
  predicate placement and empty-input aggregate behavior.
- **Unstable top/first/last output:** add `ORDER BY` with a unique final
  tie-breaker before `LIMIT` or order-sensitive windows/aggregates.
- **`psql` stops on an error:** fix the first error shown by
  `ON_ERROR_STOP`, restore the declared transaction/setup state, and rerun the
  complete file. A later successful statement does not validate a partial run.

## Self-check

- Can every normalized value be traced to preserved raw input?
- Do count summaries reconcile, and are schema additions kept out of an
  unreviewed tutorial upsert?

## Next step

Continue to [Day 59 — stakeholder analytics](day59_final_capstone_part2.md).

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

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Pipeline reasoning

- Guard every timestamp cast with a format-specific regex; ambiguous dates need
  an explicit locale policy.
- Preserve rejection reasons and raw text in a real pipeline.
- Normalize before comparing unique email values.
- `ON CONFLICT (email)` counts affected inserts/updates but does not distinguish
  them without additional logic.
- Invalid JSON falling back to `{}` is a course choice; production should retain
  the error.

## Schema and safety limits

`training.customers` has no phone column. Validate phone in staging, but do not
invent a destination. Persisting phone requires a reviewed schema migration.
The sample phone regex is intentionally narrow and is not global normalization.

Keep the entire demonstration in a transaction and roll it back. A procedure is
appropriate for side effects and can expose `INOUT` counts; a table-returning
function would be a different interface.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-58 — Final Capstone Part1.

I have completed the direct catalog prerequisite: `sql-57`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day58_final_capstone_part1.md
- Answer-free learner SQL: sql/postgres-60day/day58_final_capstone_part1.sql

Key terms to teach in context: Raw staging, Rejection reason, Upsert count. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For each timestamp format, test a format-specific regular expression before casting. Keep raw text and parsed value together, collect explicit rejection reasons, and upsert only accepted rows inside the rollback-only transaction. Return staged, valid, invalid, and affected counts that reconcile.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
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
