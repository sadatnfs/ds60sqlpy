# Day 42 — Data Quality and Validation

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 41 — complex aggregations](day41_complex_aggregations.md)
- **Artifacts:** [learner SQL](../day42_data_quality_validation.sql) ·
  [solution reasoning](../solutions/day42_solutions.md) ·
  [executable solution](../solutions/day42_solutions.sql)

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

2. Open **SQL-42 — Data Quality Validation** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-42/day42_data_quality_validation.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day42_data_quality_validation.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day42_data_quality_validation.sql
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
Invariant, Orphan, DQ result grain. Its worked SQL reads or creates `customers`, `order_items`, `orders`, `payments`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Normalize email with lower(trim(email)), group it, and return groups with COUNT() > 1. Keep the raw emails in a separate detail query: the summary counts duplicate groups, while remediation needs the member records.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day42_data_quality_validation.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT 'customers' AS table,
       COUNT(*) AS rows,
       SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) AS null_emails,
       SUM(CASE WHEN country IS NULL THEN 1 ELSE 0 END) AS null_country
FROM customers;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT email, COUNT(*) AS cnt
FROM customers
GROUP BY email
HAVING COUNT(*) > 1
ORDER BY cnt DESC;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Encode repeatable quality rules with stable names, grains, and failure counts.
- Separate observed failures from remediation policy.

## Vocabulary and concepts

- **Invariant:** a condition expected to remain true for valid data.
- **Orphan:** a foreign-key-like value with no matching parent.
- **DQ result grain:** whether a check counts failing rows, keys, or duplicate
  groups.

## Worked example / walkthrough

Normalize email with `lower(trim(email))`, group it, and return groups with
`COUNT(*) > 1`. Keep the raw emails in a separate detail query: the summary
counts duplicate groups, while remediation needs the member records.

## Exercises

Complete these in the [learner SQL](../day42_data_quality_validation.sql):

1. Build a named core-table validation report.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
2. Detect invalid/null customer emails.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
3. Explain CHECK behavior for NULL without `NOT NULL`.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Reconcile order totals with calculated line revenue.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Retain raw case variants in a normalized-email duplicate report.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Detect overlapping inclusive promotion ranges.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.

For one rule, return both a summary and failing-record detail.

## Self-check

- Does every check expose its name, result grain, expected result, and observed
  failure count?
- Can a zero result be rerun on future data without implying a permanent
  guarantee?

## Next step

Continue to [Day 43 — logical backup and recovery](day43_backup_recovery.md).

## Deep dive and reference

## What you will learn

- Profile nulls and normalized duplicates.
- Check referential, range, quantity, and discount invariants.
- Return repeatable validation results with named checks and failure counts.

## How the learner script uses the current schema

The starter profiles `customers.email` and `customers.country`, searches for
duplicate emails, checks `order_items` and `payments` for orphan orders, and
looks for negative order/payment amounts. Foreign keys and checks should keep
many failures at zero, but the queries protect future imports and schema
changes.

## Validation design

- Give each rule a stable `check_name` and `failing_rows`.
- Normalize email with `lower(trim(email))` before duplicate grouping.
- Use anti-joins to test relationships even when foreign keys exist.
- Keep observed failures separate from remediation policy.
- Report the grain: duplicate groups, failing records, and orphan keys are
  different counts.

## Practice — match the learner prompts exactly

1. Build one validation report for core tables that summarizes null emails,
   normalized duplicate emails, negative totals, orphan references, invalid
   quantities, and discounts outside 0–1.
2. Return `customer_id` and `email` for null or regex-invalid email values.

## Pitfalls and validation

- The course email regex is a pragmatic check, not the full email RFC.
- A zero count means the checked rule passed on this snapshot, not that future
  loads are guaranteed clean.
- Do not auto-delete failed rows from a validation query.
- The deterministic seed should return zero for every core failure check and no
  invalid emails.

## Expanded practice lab

Prompts 3–6 progress from constraint semantics to reconciliations and diagnostic
evidence. SQL CHECK constraints pass both TRUE and UNKNOWN, so nullable fields
need a separate `NOT NULL` rule when NULL is invalid.

Reconcile stored totals to line revenue at order grain and use a one-cent
tolerance deliberately. A duplicate report should retain raw email variants.
For inclusive promotion dates, ranges overlap when each start is less than or
equal to the other range's end; compare each pair only once.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-42 — Data Quality Validation.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day42_data_quality_validation.md
- Answer-free learner SQL: sql/postgres-60day/day42_data_quality_validation.sql

The lesson concepts include Invariant, Orphan, DQ result grain. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Normalize email with lower(trim(email)), group it, and return groups with COUNT() > 1. Keep the raw emails in a separate detail query: the summary counts duplicate groups, while remediation needs the member records.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-42/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
