# Day 14 — Numeric Types, Casting, and Precision (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 13 — date, time, and time zones](day13_date_time_functions.md)
- **Artifacts:** [learner SQL](../day14_numeric_and_casting.sql) ·
  [solution reasoning](../solutions/day14_solutions.md) ·
  [executable solution](../solutions/day14_solutions.sql)

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

2. Open **SQL-14 — Numeric and Casting** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-14/lesson/workspace/sql/postgres-60day/day14_numeric_and_casting.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day14_numeric_and_casting.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day14_numeric_and_casting.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Exact numeric, Scale, Type coercion. Its worked SQL reads or creates `orders`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Evaluate 1 / 3, 1::numeric / 3, and ROUND(1::numeric / NULLIF(3, 0), 2). Explain the result type at each step and why guarding the denominator belongs before rounding.
The expected contract is that One row per product. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day14_numeric_and_casting.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT order_id,
       total_amount,
       round(total_amount, 0) AS rounded,
       cast(total_amount AS int) AS as_int
FROM orders
ORDER BY total_amount DESC, order_id
LIMIT 50;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per product.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT p.category,
       SUM(oi.quantity) AS qty,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)) / NULLIF(SUM(oi.quantity),0), 2) AS avg_price
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY avg_price DESC, p.category;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per product.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Choose numeric types that preserve required precision.
- Cast deliberately and guard division, rounding, overflow, and malformed text.

## Vocabulary and concepts

- **Exact numeric:** `numeric`/`decimal`, which stores decimal values without
  binary floating-point approximation.
- **Scale:** digits to the right of the decimal point.
- **Type coercion:** PostgreSQL's conversion of values to a compatible type.

## Worked example / walkthrough

Evaluate `1 / 3`, `1::numeric / 3`, and
`ROUND(1::numeric / NULLIF(3, 0), 2)`. Explain the result type at each step and
why guarding the denominator belongs before rounding.

## Practice assumptions and review method

- **Focus:** Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.
- **Assumptions:** Money is exact `numeric`; division casts denominators to numeric where fractions matter. NULL/zero denominators return NULL through `NULLIF`.
- **Failure to watch for:** Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Calculate product gross margin amount and percentage, returning NULL percentage for zero price.
   **Progressive hint:** Keep exact numeric arithmetic and guard the denominator with `NULLIF`.
   **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: Calculate product gross margin amount and percentage, returning NULL percentage for zero price” at one row per product or product grouping requested. Named evidence columns/objects: `evidence`, `margin_amount`, `margin_rate`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 1, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
2. **Query writing:** Safely cast a set of text values to numeric only when they match a numeric grammar.
   **Progressive hint:** Validate with a regex before casting; otherwise return NULL.
   **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Safely cast a set of text values to numeric only when they match a numeric grammar” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `parsed_numeric`, `sample`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 2, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `order_items`, `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
3. **Query writing:** Show order-item net revenue rounded only after summing.
   **Progressive hint:** Aggregate exact line expressions first; round the final display value.
   **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: Show order-item net revenue rounded only after summing” at one summary row per grouping key explicitly named in the prompt. Named evidence columns/objects: `evidence`, `net_order_revenue`, `oi`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 3, prove uniqueness at one summary row per grouping key explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `order_items`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
4. **Prediction:** Compare integer division with numeric division for 1 divided by 4.
   **Progressive hint:** At least one operand must be numeric to preserve the fraction.
   **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Compare integer division with numeric division for 1 divided by 4”. Show both compared result shapes at one row at least one operand must be numeric to preserve the fraction grain, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `integer_division`, `numeric_division`.
   **Verify:** For Exercise 4, run the two forms over the identical rows in `orders`, `order_items`, `products`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
5. **Debugging:** Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders.
   **Progressive hint:** Aggregate payment amount and count distinct order IDs at one common scope.
   **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Debugging: Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders” at one row at one common scope grain. Named evidence columns/objects: `orders`, `evidence`, `average_paid_amount_per_order`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 5, prove uniqueness at one row at one common scope grain; reconcile the result's row count and any count/sum/amount with a simpler control over `payments`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
6. **Extension:** Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference.
   **Progressive hint:** This diagnostic makes the consequence of early rounding visible.
   **Expected result/shape:** Exercise 6 must make “Extension: Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference” observable through the exact DDL/DML command tag plus one summary row per grouping key explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `sum_of_rounded_lines`, `rounded_exact_total`, `rounding_difference`, `oi`.
   **Verify:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `sum_of_rounded_lines`, `rounded_exact_total`, `rounding_difference`, `oi`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
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

- Can you justify the type used for money-like values and ratios?
- Are division-by-zero and `NULL` behavior visible rather than silently
  misleading?

## Next step

Continue to [Day 15 — Phase 1 project](day15_phase1_project.md).

## Deep dive and reference

Learning objectives
- Use integer, numeric/decimal, and floating types appropriately
- Control rounding and formatting; avoid integer division pitfalls
- Cast safely between types; handle NULLs and invalid text

Core concepts and deep dive
- Types: integer (fast, bounded), numeric(p,s) (exact decimal), double precision (approximate). Use numeric for money.
- Division: integer/int division truncates; cast to numeric for fractional results.
- Rounding: ROUND(x,2), CEIL/FLOOR; formatting with to_char for presentation.
- Casting: CAST(text AS numeric) or ::numeric; use to_number(text, format) for messy text.

Examples
- Compute gross_margin_pct = (price-cost)/NULLIF(price,0) casting to numeric with scale.
- Parse '1,234.50' with to_number and compare to numeric cast behavior.

Pitfalls
- Silent rounding when casting to narrower numeric precision.
- Dividing by zero — use NULLIF(den,0) to avoid errors.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Numeric types: https://www.postgresql.org/docs/current/datatype-numeric.html

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-14 — Numeric and Casting.

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day14_numeric_and_casting.md
- Answer-free learner SQL: sql/postgres-60day/day14_numeric_and_casting.sql

Key terms to teach in context: Exact numeric, Scale, Type coercion. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Evaluate 1 / 3, 1::numeric / 3, and ROUND(1::numeric / NULLIF(3, 0), 2). Explain the result type at each step and why guarding the denominator belongs before rounding.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-14/ working copy. Never point setup, reset, DDL, or DML
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
