# Day 10: DML with Subqueries: INSERT/UPDATE/DELETE/UPSERT (Companion Guide)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-10**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. The **Course database** panel above the code shows whether the course
   training tables are loaded. Missing tables load automatically before your
   first run (or choose **Load course tables**) and stay loaded for later
   lessons. **Reset training data** restores the original rows only when your
   own changes made results differ; it keeps your saved code and notes.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-10/lesson/workspace/sql/postgres-60day/day10_dml_with_subqueries.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-10
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 09; correlated subqueries and EXISTS](day09_correlated_subqueries.md)
- **Artifacts:** [learner SQL](../day10_dml_with_subqueries.sql) ·
  [solution reasoning](../solutions/day10_solutions.md) ·
  [executable solution](../solutions/day10_solutions.sql)

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

The worked walkthrough's lesson-specific task is: Run the candidate-selection `SELECT` before the matching `UPDATE`. Compare its keys with `UPDATE ... RETURNING`, verify the affected count, and leave the course transaction at `ROLLBACK`. This preview/modify/reconcile pattern is safer than starting with an unbounded write.
Exercise 1 expects this result: one temporary row per product category. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day10_dml_with_subqueries.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
CREATE TEMP TABLE tmp_category_revenue AS
SELECT
  p.category,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
GROUP BY
  p.category;
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 returns one grouped row per `category` with columns `category`, and `revenue` from `order_items`, and `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT
  category,
  revenue
FROM
  tmp_category_revenue
ORDER BY
  revenue DESC,
  category;
```

**How to read it:** Example 2: Start with `tmp_category_revenue` in `FROM`/`JOIN`. The final `SELECT` displays `category`, and `revenue`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per `category` with columns `category`, and `revenue` from `tmp_category_revenue`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Modify a precisely selected row set and inspect affected rows with
  `RETURNING`.
- Make repeated loads safe with a declared conflict key and update policy.

## Vocabulary and concepts

- **DML:** data manipulation language, `INSERT`, `UPDATE`, and `DELETE`.
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
   **Inputs/evidence:** For sql-10 Exercise 1, aggregate net revenue, `unit_price * quantity * (1 - discount)`, from `order_items` joined to `products` by `p.category`, and load it with `INSERT ... SELECT` into the temporary table `exercise_category_revenue (category text PRIMARY KEY, revenue numeric NOT NULL)`.
   **Expected result/shape:** For sql-10 Exercise 1, expected output: the command tag `INSERT 0 6`, then six rows, one per product category, with columns `category` and `revenue` (rounded to 2 places), ordered by `revenue DESC, category`; `Sports` leads on the course seed.
   **Verify:** For sql-10 Exercise 1, rerun the aggregate as a plain `SELECT` and compare each category's revenue with the stored row; confirm that `SELECT COUNT(DISTINCT p.category) FROM order_items oi JOIN products p ON p.product_id = oi.product_id` returns 6, and that the savepoint rollback leaves no `exercise_category_revenue` table.
2. **Query writing:** Give Sales and Engineering employees a 5% demonstration raise and return affected rows.
   **Progressive hint:** Select departments by key, round exact numeric salary, and inspect `RETURNING`.
   **Inputs/evidence:** For sql-10 Exercise 2, raise `salary` by 5% (rounded to 2 places) for employees whose `department_id` belongs to the `departments` named `Sales` or `Engineering`, selected with an `IN (SELECT ...)` subquery, inside a savepoint.
   **Expected result/shape:** For sql-10 Exercise 2, expected output: the command tag `UPDATE 34` and 34 returned rows with columns `employee_id`, `full_name`, and `salary` (the new value); after `ROLLBACK TO SAVEPOINT`, no salary has changed.
   **Verify:** For sql-10 Exercise 2, before the update, count the targets with `SELECT COUNT(*) FROM employees e JOIN departments d ON d.department_id = e.department_id WHERE d.name IN ('Sales', 'Engineering')` (34) and compare with the command tag; after the rollback, compare one returned `employee_id`'s salary with its original value.
3. **Query writing:** Delete orders older than one year only when no payment exists, returning candidate keys.
   **Progressive hint:** Use correlated `NOT EXISTS`; foreign-key cascades remain rollback-protected.
   **Inputs/evidence:** For sql-10 Exercise 3, delete orders with `order_date` older than one year that have no row in `payments`, using a correlated `NOT EXISTS`, inside a savepoint.
   **Expected result/shape:** For sql-10 Exercise 3, expected output: a `DELETE` command tag and returned rows with columns `order_id`, `customer_id`, and `order_date`, all older than one year (362 rows on a freshly seeded database); after `ROLLBACK TO SAVEPOINT`, every order and its cascaded `order_items` are restored.
   **Verify:** For sql-10 Exercise 3, count the candidates first with the same `WHERE` clause in a `SELECT COUNT(*)` and compare with the command tag; after the rollback, confirm that `SELECT COUNT(*) FROM orders` is back to 4,362 and that a deleted `order_id` exists again.
4. **Prediction:** Run an upsert twice against a temporary key-value table and prove only one row exists for the key.
   **Progressive hint:** A primary key supplies the conflict target; the second statement updates rather than inserts.
   **Inputs/evidence:** For sql-10 Exercise 4, create the temporary table `exercise_feed (source_key text PRIMARY KEY, source_value numeric NOT NULL)` and run `INSERT ... ON CONFLICT (source_key) DO UPDATE SET source_value = EXCLUDED.source_value` twice for `source_a`, first with `10` and then with `12`.
   **Expected result/shape:** For sql-10 Exercise 4, expected output: both statements print `INSERT 0 1`, and the final `SELECT` returns one row ordered by `source_key` with columns `source_key` and `source_value`: `('source_a', 12)`.
   **Verify:** For sql-10 Exercise 4, confirm that `SELECT COUNT(*) FROM exercise_feed WHERE source_key = 'source_a'` returns 1 after the second run; add `RETURNING (xmax = 0) AS inserted` to each upsert to see `true` for the first run and `false` for the second.
5. **Debugging:** Preview and update a bounded product set while reconciling selected and returned key counts.
   **Progressive hint:** Store candidate keys in a temporary table and update only through that reviewed set.
   **Inputs/evidence:** For sql-10 Exercise 5, store the first five `Books` product keys in the temporary table `exercise_product_candidates`, then lower those products' `price` by 1% through a data-modifying CTE that updates only keys in that table.
   **Expected result/shape:** For sql-10 Exercise 5, expected output: one summary row with columns `candidate_count` and `updated_count`, both `5`.
   **Verify:** For sql-10 Exercise 5, list the candidate `product_id` values before the update and compare them with the keys returned by the `UPDATE`'s `RETURNING` clause; after `ROLLBACK TO SAVEPOINT`, confirm that each candidate's `price` equals its original value.
6. **Extension:** Stage product prices and update only rows whose incoming price is nonnegative and actually differs.
   **Progressive hint:** Use `UPDATE ... FROM`, validate the stage predicate, and compare with `IS DISTINCT FROM`.
   **Inputs/evidence:** For sql-10 Exercise 6, stage new prices for the first three products in the temporary table `exercise_price_stage`, then run `UPDATE products ... FROM exercise_price_stage` only where `stage.new_price >= 0` and `p.price IS DISTINCT FROM stage.new_price`.
   **Expected result/shape:** For sql-10 Exercise 6, expected output: the command tag `UPDATE 3` and three returned rows ordered by `p.product_id` with columns `product_id` and `price`: `(1, 10.47)`, `(2, 10.85)`, and `(3, 11.22)` on the course seed.
   **Verify:** For sql-10 Exercise 6, add a staged row with a negative price and one whose price equals the current price, rerun the update after a savepoint, and confirm that neither key is returned; then confirm the original prices after `ROLLBACK TO SAVEPOINT`.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Never run an unbounded `UPDATE` or `DELETE`; preview candidate keys and do not treat `ON CONFLICT` as safe without naming its unique key.
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

Continue to [Day 11; CASE expressions](day11_case_expressions.md).

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

Further reading
- INSERT: https://www.postgresql.org/docs/17/sql-insert.html
- UPDATE: https://www.postgresql.org/docs/17/sql-update.html
- UPSERT: https://www.postgresql.org/docs/17/sql-insert.html#SQL-ON-CONFLICT

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-10: Changing Data with Subqueries: INSERT, UPDATE, DELETE, and Upsert.

I have completed the direct catalog prerequisite: `sql-09`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day10_dml_with_subqueries.md
- Answer-free learner SQL: sql/postgres-60day/day10_dml_with_subqueries.sql

Key terms to teach in context: DML, Upsert, Idempotent. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Run the candidate-selection `SELECT` before the matching `UPDATE`. Compare its keys with `UPDATE ... RETURNING`, verify the affected count, and leave the course transaction at `ROLLBACK`. This preview/modify/reconcile pattern is safer than starting with an unbounded write.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
