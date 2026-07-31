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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-58/day58_final_capstone_part1.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
Raw staging, Rejection reason, Upsert count. Its worked SQL reads or creates `stg_customers_raw`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: For each timestamp format, test a format-specific regular expression before casting. Keep raw text and parsed value together, collect explicit rejection reasons, and upsert only accepted rows inside the rollback-only transaction. Return staged, valid, invalid, and affected counts that reconcile.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
INSERT INTO stg_customers_raw(full_name, email, country, segment, created_at, attributes)
VALUES
  ('  Customer 501  ', 'CUSTOMER501@EXAMPLE.COM ', ' us ', ' GOLD ', '2025/01/03 10:00', '{"channel":"Web","referrer":"SEO"}'),
  ('Customer 502', 'customer-502@example.com', 'GB', NULL, '03-01-2025', '{"channel":"mobile","referrer":"email"}'),
  ('Customer 503', 'invalid-email', 'DE', 'silver', '2025-01-05T12:34:56Z', '{"channel":"store"}');
```

**How to read it:** Example 2 changes rows inside the lesson's declared transaction. The command tag reports affected rows, but a follow-up query must prove the intended before/after invariant.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Normalize/validate staged phone values.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Build a transactional ingest procedure with DQ counts.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
4. Make source-duplicate winner selection deterministic.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Split accepted/rejected rows with reason codes and reconcile counts.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Normalize email before deduplication.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
7. Distinguish missing from unrecognized countries and retain raw values.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
8. Add source batch/row identity and make replay idempotent.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
9. Quarantine malformed JSON without aborting the batch.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
10. Reconcile staged, accepted, rejected, inserted, and updated outcomes.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Malformed inputs must become explained rejections.

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

## Practice — match the learner prompts exactly

1. Extend the guarded timestamp parser for additional explicit formats.
2. Add a staged phone value, strip non-digits with regex, and return a
   `phone_valid` flag under a clearly stated numbering policy.
3. Create a PostgreSQL stored procedure that truncates/rebuilds a cleaned stage,
   validates it, upserts accepted customers, and returns upserted/invalid counts
   through `INOUT` parameters.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day58_final_capstone_part1.md
- Answer-free learner SQL: sql/postgres-60day/day58_final_capstone_part1.sql

The lesson concepts include Raw staging, Rejection reason, Upsert count. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For each timestamp format, test a format-specific regular expression before casting. Keep raw text and parsed value together, collect explicit rejection reasons, and upsert only accepted rows inside the rollback-only transaction. Return staged, valid, invalid, and affected counts that reconcile.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-58/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
