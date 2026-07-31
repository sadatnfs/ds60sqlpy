# Day 11 — CASE Expressions and Conditional Logic (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 10 — data modification with subqueries](day10_dml_with_subqueries.md)
- **Artifacts:** [learner SQL](../day11_case_expressions.sql) ·
  [solution reasoning](../solutions/day11_solutions.md) ·
  [executable solution](../solutions/day11_solutions.sql)

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

2. Open **SQL-11 — Case Expressions** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-11/lesson/workspace/sql/postgres-60day/day11_case_expressions.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day11_case_expressions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day11_case_expressions.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Searched CASE, Simple CASE, Short-circuit ordering. Its worked SQL reads or creates `orders`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Take a three-tier amount classification and test values just below, exactly at, and just above each boundary. Because CASE stops at the first match, place the most specific or highest-threshold conditions before broader ones.
The expected contract is that One row per order with exactly one size label. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day11_case_expressions.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT o.order_id, o.total_amount,
  CASE
    WHEN o.total_amount >= 1000 THEN 'XL'
    WHEN o.total_amount >= 300 THEN 'L'
    WHEN o.total_amount >= 100 THEN 'M'
    ELSE 'S'
  END AS order_size
FROM orders o
ORDER BY o.total_amount DESC, o.order_id
LIMIT 50;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per order with exactly one size label.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT p.category,
  SUM(CASE WHEN o.order_date >= now() - interval '30 days' THEN oi.quantity ELSE 0 END) AS qty_30d,
  SUM(CASE WHEN o.order_date >= now() - interval '90 days' THEN oi.quantity ELSE 0 END) AS qty_90d
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY qty_30d DESC, p.category;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per order with exactly one size label.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Classify rows with ordered, mutually understandable `CASE` branches.
- Use conditional aggregation without losing unmatched categories.

## Vocabulary and concepts

- **Searched CASE:** evaluates Boolean conditions in order.
- **Simple CASE:** compares one expression with several values.
- **Short-circuit ordering:** the first matching branch supplies the result.

## Worked example / walkthrough

Take a three-tier amount classification and test values just below, exactly at,
and just above each boundary. Because `CASE` stops at the first match, place the
most specific or highest-threshold conditions before broader ones.

## Practice assumptions and review method

- **Focus:** Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.
- **Assumptions:** Searched `CASE` uses first-match wins. Status/category labels are illustrative course rules, not universal business definitions.
- **Failure to watch for:** Overlapping broad conditions placed first make later branches unreachable; an omitted `ELSE` produces NULL.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Classify orders as small, medium, or large by total amount.
   **Progressive hint:** Validate boundaries and place the highest threshold first.
   **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: Classify orders as small, medium, or large by total amount” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `small`, `evidence`, `order_size`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 1, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
2. **Query writing:** Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation.
   **Progressive hint:** Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator.
   **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation” at one summary row per grouping key explicitly named in the prompt. Named evidence columns/objects: `evidence`, `paid_like`, `open_orders`, `returned_orders`, `all_orders`, `o`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 2, prove uniqueness at one summary row per grouping key explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
3. **Query writing:** Label missing customer segments separately from known segment values.
   **Progressive hint:** Test `IS NULL` before comparing text values.
   **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: Label missing customer segments separately from known segment values” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `segment_group`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
4. **Prediction:** Predict the label for 500 when `>= 100` appears before `>= 500`, then repair the branch order.
   **Progressive hint:** First-match wins, so specific/high thresholds must precede broader/lower ones.
   **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Predict the label for 500 when >= 100 appears before >= 500, then repair the branch order”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `corrected_label`, `sample`.
   **Verify:** For Exercise 4, run the two forms over the identical rows in `orders`, `order_items`, `products`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
5. **Debugging:** Replace a CASE expression that returns mixed numeric and text types with one consistent output type.
   **Progressive hint:** All result branches must resolve to a compatible PostgreSQL type.
   **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Debugging: Replace a CASE expression that returns mixed numeric and text types with one consistent output type” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `value_state`, `sample`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 5, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `order_items`, `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
6. **Extension:** Create payment-method display labels and preserve unknown future methods with an explicit fallback.
   **Progressive hint:** A simple CASE fits equality mapping; `ELSE` prevents silent NULL labels.
   **Expected result/shape:** Exercise 6 must make “Extension: Create payment-method display labels and preserve unknown future methods with an explicit fallback” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `method_label`, `payment_count`, `p`.
   **Verify:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `method_label`, `payment_count`, `p`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Overlapping broad conditions placed first make later branches unreachable; an omitted ELSE produces NULL.
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

- Are branch boundaries exhaustive and non-overlapping?
- Do all branches, including `ELSE`, resolve to compatible data types?

## Next step

Continue to [Day 12 — string functions](day12_string_functions.md).

## Deep dive and reference

Learning objectives
- Write simple and searched CASE expressions in SELECT and ORDER BY
- Use CASE within aggregates for conditional sums/counts
- Understand evaluation order and NULL handling in CASE

Core concepts and deep dive
- Simple CASE: CASE expr WHEN val1 THEN ... WHEN val2 THEN ... ELSE ... END
- Searched CASE: CASE WHEN cond1 THEN ... WHEN cond2 THEN ... ELSE ... END — more flexible; prefer for predicates.
- CASE is an expression; can be nested and used anywhere expressions are allowed.
- Use CASE to implement bucketing, flags, and conditional aggregation without extra joins.

Examples
- Segment labels: CASE WHEN ltv>=1000 THEN 'gold' WHEN ltv>=300 THEN 'silver' ELSE 'bronze' END.
- Conditional aggregate: `SUM(CASE WHEN status='returned' THEN total_amount
  ELSE 0 END)` over `orders`.

Pitfalls
- Overlapping conditions in searched CASE; first match wins. Order matters.
- Returning mixed types; ensure consistent result types across branches.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- CASE: https://www.postgresql.org/docs/current/functions-conditional.html

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-11 — Case Expressions.

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day11_case_expressions.md
- Answer-free learner SQL: sql/postgres-60day/day11_case_expressions.sql

Key terms to teach in context: Searched CASE, Simple CASE, Short-circuit ordering. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Take a three-tier amount classification and test values just below, exactly at, and just above each boundary. Because CASE stops at the first match, place the most specific or highest-threshold conditions before broader ones.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-11/ working copy. Never point setup, reset, DDL, or DML
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
