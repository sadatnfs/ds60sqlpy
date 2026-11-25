# Day 10: DML with Subqueries: INSERT/UPDATE/DELETE/UPSERT (Companion Guide)

## How to run this lesson

Run `./classroom` from the repository root, pick PostgreSQL, open **sql-10** and choose **Whole SQL lesson (psql)**. The file opens a transaction on `advanced_sql_training`, builds a temporary table of net revenue per product category and prints its six rows, gives the 34 Sales and Engineering employees a 5% raise and prints them, then deletes the unpaid orders older than 365 days (362 on a freshly loaded database) and prints their IDs. The closing `ROLLBACK` undoes all three writes, so a second run starts from the same 100 employees and 4,362 orders.

Your editable copy is
`.learning/sql/sql-10/lesson/workspace/sql/postgres-60day/day10_dml_with_subqueries.sql`.
One experiment worth trying: change `e.department_id IN (SELECT ...)` in the salary update to `e.department_id = (SELECT ...)` and rerun. `psql` stops with `more than one row returned by a subquery used as an expression`, because the subquery returns two department IDs.

If the run does not start, the study guide has [the classroom's run instructions](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom); the [notebook option kept for contributors](../../STUDY-GUIDE.md#optional-contributor-notebook-route) is not needed for this course.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 09; correlated subqueries and EXISTS](day09_correlated_subqueries.md)
- **Artifacts:** [learner SQL](../day10_dml_with_subqueries.sql) ·
  [solution reasoning](../solutions/day10_solutions.md) ·
  [executable solution](../solutions/day10_solutions.sql)

## A beginner's mental model for this lesson

**DML** (data manipulation language) is the part of SQL that changes rows: `INSERT`, `UPDATE` and `DELETE`. In this lesson each of them gets its target rows from a query. The salary raise never lists employee IDs; it finds them through `department_id IN (SELECT d.department_id FROM departments AS d WHERE d.name IN ('Sales', 'Engineering'))`, which yields departments 1 and 2. The old-order delete removes an order only when `NOT EXISTS` finds no payment for it. Whatever the subquery returns decides which rows change, so run it on its own before trusting the write.

A write normally prints only a command tag such as `UPDATE 34`. Adding **RETURNING** makes it hand back the affected rows: new values after an `UPDATE`, the removed rows after a `DELETE`. Wrapping the statement in a CTE, as the learner file does with `WITH changed AS (UPDATE ... RETURNING ...)`, lets an outer `SELECT` sort those rows by `employee_id`.

An **upsert** is `INSERT ... ON CONFLICT (key) DO UPDATE`: insert the row, or, when a row with that key already exists, update it instead. PostgreSQL needs a primary key or unique index on the conflict columns to notice the clash. A load is **idempotent** when running it twice leaves the table exactly as running it once did. Exercise 4's upsert loads `source_a` twice and still holds one row, while a plain `INSERT` run twice fails with a duplicate-key error.

Every write here happens between `BEGIN` and `ROLLBACK`, and the solutions put a `SAVEPOINT` around each exercise, so nothing you change outlives the run.

## Two worked SQL examples

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

**How to read it:** `CREATE TEMP TABLE ... AS SELECT` creates the table and fills it from the query in one statement. The query joins every order line to its product, computes the line's net amount as price times quantity times `(1 - discount)`, and sums it per `p.category`. The new table takes its column names, `category` and `revenue`, from the select list. It would last until the session ends, but the file's final `ROLLBACK` removes it sooner, because the `CREATE` happened inside the transaction.

**Expected result/shape:** No result rows, only the tag `SELECT 6`: the number of rows the query stored, one per category. PostgreSQL reports `SELECT` rather than `CREATE TABLE` here because it counts what the query put in the new table.

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

**How to read it:** A plain read of the temporary table, sorted by `revenue DESC` with `category` as a tie-breaker in case two categories ever earn the same amount. Nothing is joined or grouped again; that work was done when the table was filled.

**Expected result/shape:** Six rows: Sports 397,427.70, Electronics 394,424.39, Home 393,760.42, Beauty 393,436.90, Apparel 390,404.94 and Books 386,192.77. The spread is only about 11,000, so the formula matters: sum without the discount and Beauty moves up to second while Electronics falls to fourth.

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

Preview the salary raise before running it: `SELECT COUNT(*) FROM employees e JOIN departments d ON d.department_id = e.department_id WHERE d.name IN ('Sales', 'Engineering')` returns 34, seventeen from each department. The update then returns 34 rows, starting with employee 1 in Sales, whose 40,079.19 becomes 42,083.15. Equal counts show the write touched exactly the previewed rows. The learner `UPDATE` has no `ROUND`, but `salary` is `numeric(10,2)`, so 42,083.1495 is stored as 42,083.15 anyway. After the closing `ROLLBACK`, employee 1 earns 40,079.19 again.

## Practice assumptions and review method

- **Focus:** Modify only reviewed row sets, inspect writes with `RETURNING`, and make repeat behavior explicit through constraints and rollback-safe tests.
- **Assumptions:** Every exercise runs inside the disposable course transaction. Savepoints isolate demonstrations so one answer does not change the next.
- **Failure to watch for:** Never run an unbounded `UPDATE` or `DELETE`; preview candidate keys and do not treat `ON CONFLICT` as safe without naming its unique key.
- **Review loop:** compare the preview count with the command tag (`UPDATE 34`, `DELETE 362`), read a few `RETURNING` rows, and after rolling back confirm that one changed row has its old value again, such as employee 1's 40,079.19.

## Exercises

Modify only reviewed row sets, inspect writes with `RETURNING`, and make repeat behavior explicit through constraints and rollback-safe tests.

Before each exercise, write down how many rows you expect the write to affect, then run a `SELECT COUNT(*)` with the same `WHERE` clause and compare. Put a `SAVEPOINT` before the write and `ROLLBACK TO SAVEPOINT` after it, so a mistake in one exercise cannot change the rows the next one starts from.

1. **Query writing:** Materialize category net revenue into a temporary table with `INSERT ... SELECT`.
   **Make a call:** what number does the `INSERT` command tag show?
   **Progressive hint:** Declare the temporary schema and aggregate source rows before inserting.
   **Inputs/evidence:** For sql-10 Exercise 1, aggregate net revenue, `unit_price * quantity * (1 - discount)`, from `order_items` joined to `products` by `p.category`, and load it with `INSERT ... SELECT` into the temporary table `exercise_category_revenue (category text PRIMARY KEY, revenue numeric NOT NULL)`.
   **Expected result/shape:** For sql-10 Exercise 1, expected output: the command tag `INSERT 0 6`, then six rows, one per product category, with columns `category` and `revenue` (rounded to 2 places), ordered by `revenue DESC, category`; `Sports` leads on the course seed.
   **Verify:** For sql-10 Exercise 1, rerun the aggregate as a plain `SELECT` and compare each category's revenue with the stored row; confirm that `SELECT COUNT(DISTINCT p.category) FROM order_items oi JOIN products p ON p.product_id = oi.product_id` returns 6, and that the savepoint rollback leaves no `exercise_category_revenue` table.
2. **Query writing:** Give Sales and Engineering employees a 5% demonstration raise and return affected rows.
   **Make a call:** how many employees get the raise, and what is employee 1's new salary?
   **Progressive hint:** Select departments by key, round exact numeric salary, and inspect `RETURNING`.
   **Inputs/evidence:** For sql-10 Exercise 2, raise `salary` by 5% (rounded to 2 places) for employees whose `department_id` belongs to the `departments` named `Sales` or `Engineering`, selected with an `IN (SELECT ...)` subquery, inside a savepoint.
   **Expected result/shape:** For sql-10 Exercise 2, expected output: the command tag `UPDATE 34` and 34 returned rows with columns `employee_id`, `full_name`, and `salary` (the new value); after `ROLLBACK TO SAVEPOINT`, no salary has changed.
   **Verify:** For sql-10 Exercise 2, before the update, count the targets with `SELECT COUNT(*) FROM employees e JOIN departments d ON d.department_id = e.department_id WHERE d.name IN ('Sales', 'Engineering')` (34) and compare with the command tag; after the rollback, compare one returned `employee_id`'s salary with its original value.
3. **Query writing:** Delete orders older than one year only when no payment exists, returning candidate keys.
   **Make a call:** while the deleted orders are gone, do their `order_items` rows still exist?
   **Progressive hint:** Use correlated `NOT EXISTS`; foreign-key cascades remain rollback-protected.
   **Inputs/evidence:** For sql-10 Exercise 3, delete orders with `order_date` older than one year that have no row in `payments`, using a correlated `NOT EXISTS`, inside a savepoint.
   **Expected result/shape:** For sql-10 Exercise 3, expected output: a `DELETE` command tag and returned rows with columns `order_id`, `customer_id`, and `order_date`, all older than one year (362 rows on a freshly seeded database); after `ROLLBACK TO SAVEPOINT`, every order and its cascaded `order_items` are restored.
   **Verify:** For sql-10 Exercise 3, count the candidates first with the same `WHERE` clause in a `SELECT COUNT(*)` and compare with the command tag; after the rollback, confirm that `SELECT COUNT(*) FROM orders` is back to 4,362 and that a deleted `order_id` exists again.
4. **Prediction:** Run an upsert twice against a temporary key-value table and prove only one row exists for the key.
   **Make a call:** how many rows does `exercise_feed` hold after the second statement, and with which value?
   **Progressive hint:** A primary key supplies the conflict target; the second statement updates rather than inserts.
   **Inputs/evidence:** For sql-10 Exercise 4, create the temporary table `exercise_feed (source_key text PRIMARY KEY, source_value numeric NOT NULL)` and run `INSERT ... ON CONFLICT (source_key) DO UPDATE SET source_value = EXCLUDED.source_value` twice for `source_a`, first with `10` and then with `12`.
   **Expected result/shape:** For sql-10 Exercise 4, expected output: both statements print `INSERT 0 1`, and the final `SELECT` returns one row ordered by `source_key` with columns `source_key` and `source_value`: `('source_a', 12)`.
   **Verify:** For sql-10 Exercise 4, confirm that `SELECT COUNT(*) FROM exercise_feed WHERE source_key = 'source_a'` returns 1 after the second run; add `RETURNING (xmax = 0) AS inserted` to each upsert to see `true` for the first run and `false` for the second.
5. **Debugging:** Preview and update a bounded product set while reconciling selected and returned key counts.
   **Make a call:** if one candidate product vanished before the update, which of the two counts would change?
   **Progressive hint:** Store candidate keys in a temporary table and update only through that reviewed set.
   **Inputs/evidence:** For sql-10 Exercise 5, store the first five `Books` product keys in the temporary table `exercise_product_candidates`, then lower those products' `price` by 1% through a data-modifying CTE that updates only keys in that table.
   **Expected result/shape:** For sql-10 Exercise 5, expected output: one summary row with columns `candidate_count` and `updated_count`, both `5`.
   **Verify:** For sql-10 Exercise 5, list the candidate `product_id` values before the update and compare them with the keys returned by the `UPDATE`'s `RETURNING` clause; after `ROLLBACK TO SAVEPOINT`, confirm that each candidate's `price` equals its original value.
6. **Extension:** Stage product prices and update only rows whose incoming price is nonnegative and actually differs.
   **Make a call:** when a staged price equals the product's current price, is that product returned?
   **Progressive hint:** Use `UPDATE ... FROM`, validate the stage predicate, and compare with `IS DISTINCT FROM`.
   **Inputs/evidence:** For sql-10 Exercise 6, stage new prices for the first three products in the temporary table `exercise_price_stage`, then run `UPDATE products ... FROM exercise_price_stage` only where `stage.new_price >= 0` and `p.price IS DISTINCT FROM stage.new_price`.
   **Expected result/shape:** For sql-10 Exercise 6, expected output: the command tag `UPDATE 3` and three returned rows ordered by `p.product_id` with columns `product_id` and `price`: `(1, 10.47)`, `(2, 10.85)`, and `(3, 11.22)` on the course seed.
   **Verify:** For sql-10 Exercise 6, add a staged row with a negative price and one whose price equals the current price, rerun the update after a savepoint, and confirm that neither key is returned; then confirm the original prices after `ROLLBACK TO SAVEPOINT`.

## Common mistakes and how to recover

- **An `UPDATE` whose filter does nothing:** drop the department condition from the raise and all 100 employees change, not 34. Run the matching `SELECT COUNT(*)` first and compare it with the tag.
- **`=` where the subquery returns several rows:** `department_id = (SELECT ... IN ('Sales', 'Engineering'))` stops with `more than one row returned by a subquery used as an expression`. Use `IN`.
- **A misspelled name inside the subquery:** `'Engineers'` matches no department, so the raise silently covers Sales alone and prints `UPDATE 17`. Only the 34-row preview reveals it.
- **Forgetting cascades:** `order_items` and `payments` reference `orders` with `ON DELETE CASCADE`, so deleting the 362 unpaid orders also removes 1,073 order lines (13,085 drops to 12,012). Count `order_items` before and after to see the hidden part of the delete.
- **`ON CONFLICT` without a unique key:** if `source_key` has no primary key or unique index, the upsert fails with `there is no unique or exclusion constraint matching the ON CONFLICT specification`.
- **Rerunning a plain `INSERT`:** a second `INSERT INTO exercise_feed VALUES ('source_a', 12)` fails with `duplicate key value violates unique constraint "exercise_feed_pkey"`.
- **Staging a negative price:** without the `stage.new_price >= 0` guard, a staged -5 reaches `products` and the whole update fails on `products_price_check`.

With `ON_ERROR_STOP`, `psql` stops at the first failure and the open transaction is discarded, so the partial run keeps nothing. Fix that statement and run the whole file again; the study guide explains [how to restart after an error](../../STUDY-GUIDE.md#recover-from-common-failures).

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
- Multi-row subqueries in scalar contexts: `department_id = (SELECT ... WHERE d.name IN ('Sales', 'Engineering'))` fails because two IDs come back. Use `IN`, or make sure the subquery can only return one row.
- Upserts racing under concurrency; consider locking or version columns.

Further reading
- INSERT: https://www.postgresql.org/docs/17/sql-insert.html
- UPDATE: https://www.postgresql.org/docs/17/sql-update.html
- UPSERT: https://www.postgresql.org/docs/17/sql-insert.html#SQL-ON-CONFLICT

## Ask an AI tutor about this lesson

You can finish this lesson without a tutor. If you use one, ask it to predict how many order lines disappear along with the 362 unpaid orders, then check the answer with a count in `psql`. The study guide has [ways to keep a tutor asking questions](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) rather than writing your `UPDATE` for you.

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
