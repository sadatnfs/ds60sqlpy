# Day 10 — DML with Subqueries: INSERT/UPDATE/DELETE/UPSERT (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 09 — correlated subqueries and EXISTS](day09_correlated_subqueries.md)
- **Artifacts:** [learner SQL](../day10_dml_with_subqueries.sql) ·
  [solution reasoning](../solutions/day10_solutions.md) ·
  [executable solution](../solutions/day10_solutions.sql)

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

2. Open **SQL-10 — DML with Subqueries** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-10/lesson/workspace/sql/postgres-60day/day10_dml_with_subqueries.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day10_dml_with_subqueries.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day10_dml_with_subqueries.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is DML, Upsert, Idempotent. Its worked SQL reads or creates `tmp_category_revenue`, `order_items`, `products`, `employees`, `departments`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Run the candidate-selection SELECT before the matching UPDATE. Compare its keys with UPDATE ... RETURNING, verify the affected count, and leave the course transaction at ROLLBACK. This preview/modify/reconcile pattern is safer than starting with an unbounded write.
The expected contract is that One temporary row per product category. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day10_dml_with_subqueries.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TEMP TABLE tmp_category_revenue AS
SELECT p.category, ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category;
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 returns one grouped row per `category` with columns `category`, and `revenue` from `order_items`, and `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT category, revenue
FROM tmp_category_revenue
ORDER BY revenue DESC, category;
```

**How to read it:** Example 2: Start with `tmp_category_revenue` in `FROM`/`JOIN`. The final `SELECT` displays `category`, and `revenue`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per `category` with columns `category`, and `revenue` from `tmp_category_revenue`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Modify a precisely selected row set and inspect affected rows with
  `RETURNING`.
- Make repeated loads safe with a declared conflict key and update policy.

## Vocabulary and concepts

- **DML:** data manipulation language—`INSERT`, `UPDATE`, and `DELETE`.
- **Upsert:** insert a row or resolve a uniqueness conflict through a declared
  alternative action.
- **Idempotent:** safe to repeat without accumulating unintended changes.

## Worked example / walkthrough

Run the candidate-selection `SELECT` before the matching `UPDATE`. Compare its
keys with `UPDATE ... RETURNING`, verify the affected count, and leave the
course transaction at `ROLLBACK`. This preview/modify/reconcile pattern is safer
than starting with an unbounded write.

## Practice assumptions and review method

- **Focus:** Modify only reviewed row sets, inspect writes with `RETURNING`, and make repeat behavior explicit through constraints and rollback-safe tests.
- **Assumptions:** Every exercise runs inside the disposable course transaction. Savepoints isolate demonstrations so one answer does not change the next.
- **Failure to watch for:** Never run an unbounded `UPDATE` or `DELETE`; preview candidate keys and do not treat `ON CONFLICT` as safe without naming its unique key.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Modify only reviewed row sets, inspect writes with `RETURNING`, and make repeat behavior explicit through constraints and rollback-safe tests.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Materialize category net revenue into a temporary table with `INSERT ... SELECT`.
   **Progressive hint:** Declare the temporary schema and aggregate source rows before inserting.
   **Inputs/evidence:** For sql-10 Exercise 1, read the target keys from `exercise_category_revenue`, `order_items`, and `products` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-10 Exercise 1, expected output: One temporary row per product category. The final columns are `category`. The final order is `revenue DESC, category`.
   **Verify:** For sql-10 Exercise 1, materialize the intended `category` target set first; require the command tag/`RETURNING` set to match it, then query `exercise_category_revenue`, `order_items`, and `products` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `category` values in both cases.
2. **Query writing:** Give Sales and Engineering employees a 5% demonstration raise and return affected rows.
   **Progressive hint:** Select departments by key, round exact numeric salary, and inspect `RETURNING`.
   **Inputs/evidence:** For sql-10 Exercise 2, read the target keys from `employees`, and `departments` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-10 Exercise 2, expected output: Affected employee rows only; no change persists. The final columns are `returning`, `update`, `from`, and `where`.
   **Verify:** For sql-10 Exercise 2, materialize the intended `employee_id` target set first; require the command tag/`RETURNING` set to match it, then query `employees`, and `departments` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `employee_id` values in both cases.
3. **Query writing:** Delete orders older than one year only when no payment exists, returning candidate keys.
   **Progressive hint:** Use correlated `NOT EXISTS`; foreign-key cascades remain rollback-protected.
   **Inputs/evidence:** For sql-10 Exercise 3, read the target keys from `orders`, and `payments` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-10 Exercise 3, expected output: Deleted-candidate order rows, then fully restored state. The final columns are `from`, `where`, and `returning`.
   **Verify:** For sql-10 Exercise 3, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `orders`, and `payments` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
4. **Prediction:** Run an upsert twice against a temporary key-value table and prove only one row exists for the key.
   **Progressive hint:** A primary key supplies the conflict target; the second statement updates rather than inserts.
   **Inputs/evidence:** For sql-10 Exercise 4, read the target keys from `exercise_feed` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-10 Exercise 4, expected output: One row for `source_a` with the second value. The final columns are `source_key`, and `source_value`. The final order is `source_key`.
   **Verify:** For sql-10 Exercise 4, materialize the intended `source_key` target set first; require the command tag/`RETURNING` set to match it, then query `exercise_feed` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `source_key` values in both cases.
5. **Debugging:** Preview and update a bounded product set while reconciling selected and returned key counts.
   **Progressive hint:** Store candidate keys in a temporary table and update only through that reviewed set.
   **Inputs/evidence:** For sql-10 Exercise 5, read the target keys from `products`, and `exercise_product_candidates` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-10 Exercise 5, expected output: One summary row with equal candidate and updated counts. The final columns are `product_id`. The final order is `p.product_id`.
   **Verify:** For sql-10 Exercise 5, materialize the intended `product_id` target set first; require the command tag/`RETURNING` set to match it, then query `products`, and `exercise_product_candidates` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `product_id` values in both cases.
6. **Extension:** Stage product prices and update only rows whose incoming price is nonnegative and actually differs.
   **Progressive hint:** Use `UPDATE ... FROM`, validate the stage predicate, and compare with `IS DISTINCT FROM`.
   **Inputs/evidence:** For sql-10 Exercise 6, read the target keys from `exercise_price_stage`, `products`, and `stage.new_price` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-10 Exercise 6, expected output: Returned rows only for valid changed products. The final columns are `product_id`. The final order is `p.product_id`.
   **Verify:** For sql-10 Exercise 6, materialize the intended `product_id` target set first; require the command tag/`RETURNING` set to match it, then query `exercise_price_stage`, `products`, and `stage.new_price` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `product_id` values in both cases.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Never run an unbounded UPDATE or DELETE; preview candidate keys and do not treat ON CONFLICT as safe without naming its unique key.
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

- Is every write bounded by reviewed keys or a deliberate predicate?
- Can you name the unique constraint that makes each `ON CONFLICT` clause valid?

## Next step

Continue to [Day 11 — CASE expressions](day11_case_expressions.md).

## Deep dive and reference

Learning objectives
- INSERT ... SELECT to populate tables from queries
- UPDATE ... FROM and DELETE using subqueries
- Use ON CONFLICT for idempotent upserts

Core concepts and deep dive
- INSERT INTO table(cols) SELECT ... FROM ... WHERE ...; carry all required columns, handle default values.
- UPDATE t SET col=expr FROM other WHERE t.id=other.id; mind ambiguity with JOINs.
- DELETE FROM t USING other WHERE t.id=other.id; or use WHERE EXISTS (...) pattern.
- Upsert: INSERT ... ON CONFLICT (key) DO UPDATE SET ...; choose conflict target (PK/unique) and update columns carefully.

Walkthrough of the learner script
- `CREATE TEMP TABLE ... AS SELECT` materializes category revenue for the
  current session.
- `UPDATE employees` gives a demonstration raise to Sales and Engineering,
  with `RETURNING` exposing affected rows.
- `DELETE FROM orders` removes only old orders for which no payment exists.
- The enclosing `BEGIN`/`ROLLBACK` makes all demonstrations non-persistent.

Pitfalls
- Multi-row subqueries in scalar contexts; ensure uniqueness or add LIMIT 1.
- Upserts racing under concurrency; consider locking or version columns.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- INSERT: https://www.postgresql.org/docs/current/sql-insert.html
- UPDATE: https://www.postgresql.org/docs/current/sql-update.html
- UPSERT: https://www.postgresql.org/docs/current/sql-insert.html#SQL-ON-CONFLICT

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-10 — DML with Subqueries.

I have completed the direct catalog prerequisite: `sql-09`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day10_dml_with_subqueries.md
- Answer-free learner SQL: sql/postgres-60day/day10_dml_with_subqueries.sql

Key terms to teach in context: DML, Upsert, Idempotent. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Run the candidate-selection SELECT before the matching UPDATE. Compare its keys with UPDATE ... RETURNING, verify the affected count, and leave the course transaction at ROLLBACK. This preview/modify/reconcile pattern is safer than starting with an unbounded write.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-10/ working copy. Never point setup, reset, DDL, or DML
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
