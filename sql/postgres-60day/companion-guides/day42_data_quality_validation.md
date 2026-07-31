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
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-42/lesson/workspace/sql/postgres-60day/day42_data_quality_validation.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. The key vocabulary for this lesson is Invariant, Orphan, DQ result grain. Its worked SQL reads or creates `customers`, `order_items`, `orders`, `payments`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Normalize email with lower(trim(email)), group it, and return groups with COUNT() > 1. Keep the raw emails in a separate detail query: the summary counts duplicate groups, while remediation needs the member records.
The first runnable example has a concrete contract: Example 1 returns exactly one summary row with columns `rows`, `null_emails`, and `null_country` from `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `table`, `rows`, `null_emails`, and `null_country`. Recompute each displayed aggregate with a single-purpose query over `customers`; require the documented summary-row count. Where this query can emit `NULL`, identify the exact source expression and explain whether the output preserves, classifies, or rejects it.

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

**How to read it:** Example 1: Start with `customers` in `FROM`/`JOIN`. The final `SELECT` displays `table`, `rows`, `null_emails`, and `null_country`. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns exactly one summary row with columns `rows`, `null_emails`, and `null_country` from `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
SELECT email, COUNT(*) AS cnt
FROM customers
GROUP BY email
HAVING COUNT(*) > 1
ORDER BY cnt DESC;
```

**How to read it:** Example 2: Start with `customers` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `email`, and `cnt`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `email`, and `cnt` with columns `email`, and `cnt` from `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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
   **Inputs/evidence:** For sql-42 Exercise 1, read from `customers`, `orders`, `order_items`, `products`, and `payments`. Build the answer toward `check_name`, and `failing_rows`; keep `check_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-42 Exercise 1, expected output: seven rows with `check_name` and `failing_rows`. A nonzero result is evidence to investigate, not permission to delete data automatically. The final columns are `check_name`, and `failing_rows`. The final order is `check_name`.
   **Verify:** For sql-42 Exercise 1, project `check_name` plus the raw source columns from `customers`, `orders`, `order_items`, `products`, and `payments` at each join stage; record row count and distinct `check_name`, then assert the final `check_name`, and `failing_rows` values match those staged rows without unintended fanout or loss. Add one row for which `(email IS NULL) OR (total_amount < 0) OR (c.customer_id IS NULL)` is true and one for which it is false; verify only the matching `check_name` value is returned.
2. Detect invalid/null customer emails.
   **Inputs/evidence:** For sql-42 Exercise 2, read from `customers`. Build the answer toward `customer_id`, and `email`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-42 Exercise 2, expected output: one row per `customer_id`. The final columns are `customer_id`, and `email`. The final order is `customer_id`.
   **Verify:** For sql-42 Exercise 2, run an anti-check that counts rows where NOT ((email IS NULL OR email !~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `email` against `customers`. Repeat with `NULL` in `customer_id`, and `email` and state whether the row is kept, rejected, or classified.
3. Explain CHECK behavior for NULL without `NOT NULL`.
   **Inputs/evidence:** For sql-42 Exercise 3, read from `information_schema.columns`. Build the answer toward `table_name`, `column_name`, and `is_nullable`; keep `table_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-42 Exercise 3, expected output: one row per `table_name`. The final columns are `table_name`, `column_name`, and `is_nullable`. The final order is `table_name, column_name`.
   **Verify:** For sql-42 Exercise 3, run an anti-check that counts rows where NOT ((table_schema = 'training' AND table_name IN ('orders', 'payments') AND column_name IN ('total_amount', 'amount'))); require unique `table_name` where the expected grain is one row per key and confirm the projected `table_name`, `column_name`, and `is_nullable` against `information_schema.columns`. Repeat with `NULL` in `table_name`, and `column_name` and state whether the row is kept, rejected, or classified.
4. Reconcile order totals with calculated line revenue.
   **Inputs/evidence:** For sql-42 Exercise 4, read from `order_items`, and `orders`. Build the answer toward `order_id`, `total_amount`, `line_total`, and `difference`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-42 Exercise 4, expected output: one row per order before comparison. The final columns are `order_id`, `total_amount`, `line_total`, and `difference`. The final order is `o.order_id`.
   **Verify:** For sql-42 Exercise 4, project `order_id` plus the raw source columns from `order_items`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `total_amount`, `line_total`, and `difference` values match those staged rows without unintended fanout or loss. Add one row for which `(ABS(o.total_amount - c.line_total) > 0.01)` is true and one for which it is false; verify only the matching `order_id` value is returned.
5. Retain raw case variants in a normalized-email duplicate report.
   **Inputs/evidence:** For sql-42 Exercise 5, read from `customers`. Build the answer toward `normalized_email`, `raw_variants`, and `rows`; keep `normalized_email`, and `raw_variants` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-42 Exercise 5, expected output: one row per `normalized_email`, and `raw_variants`. The final columns are `normalized_email`, `raw_variants`, and `rows`. The final order is `normalized_email`.
   **Verify:** For sql-42 Exercise 5, independently aggregate `customers` by `normalized_email`, and `raw_variants`; require one output row for every distinct `normalized_email`, and `raw_variants` tuple satisfying `(email IS NOT NULL)` and compare `rows` tuple by tuple. Add duplicate source candidates for `normalized_email`, and `raw_variants`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
6. Detect overlapping inclusive promotion ranges.
   **Inputs/evidence:** For sql-42 Exercise 6, read from `promotions`. Build the answer toward `promotion_a`, `promotion_b`, and `product_id`; keep `product_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-42 Exercise 6, expected output: one row per `product_id`. The final columns are `promotion_a`, `promotion_b`, and `product_id`. The final order is `a.product_id, promotion_a, promotion_b`.
   **Verify:** For sql-42 Exercise 6, project `product_id` plus the raw source columns from `promotions` at each join stage; record row count and distinct `product_id`, then assert the final `promotion_a`, `promotion_b`, and `product_id` values match those staged rows without unintended fanout or loss. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.

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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

I have completed the direct catalog prerequisite: `sql-41`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day42_data_quality_validation.md
- Answer-free learner SQL: sql/postgres-60day/day42_data_quality_validation.sql

Key terms to teach in context: Invariant, Orphan, DQ result grain. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Normalize email with lower(trim(email)), group it, and return groups with COUNT() > 1. Keep the raw emails in a separate detail query: the summary counts duplicate groups, while remediation needs the member records.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-42/ working copy. Never point setup, reset, DDL, or DML
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
