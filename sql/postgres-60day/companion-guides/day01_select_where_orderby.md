# Day 01 — SELECT, WHERE, ORDER BY, LIMIT/OFFSET (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** Complete
  [SQL-FOUND-02 — versioned migrations](../../professional/companion-guides/sql_found_02_versioned_migrations.md)
  and the [SQL track setup](../README.md), reset the disposable
  `advanced_sql_training` database, and know how to run a `.sql` file with
  `psql`.
- **Artifacts:** [learner SQL](../day01_select_where_orderby.sql) ·
  [solution reasoning](../solutions/day01_solutions.md) ·
  [executable solution](../solutions/day01_solutions.sql)

## How to run this lesson

The rendered lesson page is a reading surface; PostgreSQL runs the real learner
file. The safest beginner route is the private course portal because it checks
the database target, creates an ignored working copy, and shows the complete
`psql` transcript in a Jupyter notebook.

1. Open a terminal **in the repository root**. On Windows, double-click
   `START_DS60.cmd` or run this in PowerShell:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. In the portal, open **SQL-01**, choose **Create/open guided SQL notebook**,
   and run the readiness cells from top to bottom. The notebook accepts only
   the local disposable `advanced_sql_training` database.
3. In the preparation cell, read the warning before changing
   `CONFIRM_COURSE_RESET` to `True`. Preparation drops and recreates only the
   course-owned `training` schema, loads deterministic seed rows, and verifies
   them. Never point this action at a shared or valuable database.
4. Open the notebook link to the editable
   `.learning/sql/sql-01/lesson/workspace/sql/postgres-60day/day01_select_where_orderby.sql` copy. Write predictions
   in comments, edit only that copy, save it, and run the notebook's full-script
   cell. It deliberately uses `psql -X -v ON_ERROR_STOP=1 -f`; this preserves
   the same behavior as the official `.sql` file.
5. Read output directly below the run cell. Each `SELECT` prints a
   table-shaped result with column headings and a row count. Success means the
   transcript has no `ERROR`, the runner reports exit code 0, and the final
   `ROLLBACK` leaves the seed data unchanged. The following verification cell
   should also pass.

If Jupyter is not available, run the official answer-free file directly:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day01_select_where_orderby.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day01_select_where_orderby.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL without
permanently changing `PATH`. If PostgreSQL reports that the database or a
`training` relation does not exist, return to the notebook preparation cell
and explicitly prepare the disposable database. For authentication errors,
rerun the setup/doctor flow—do not paste a password into a lesson, notebook, or
committed file. With `ON_ERROR_STOP`, fix the first reported error and rerun the
whole transactional script rather than continuing from partial state.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence of the
table's subject; in `training.customers`, one row represents one customer.
A **result set** is the temporary, table-shaped answer printed by a query. It
does not change stored rows. The **grain** says what one output row represents;
state it before writing a query.

For the opening query, imagine a pipeline:

1. `FROM training.customers` supplies candidate customer rows.
2. `WHERE country IN ('US', 'CA')` keeps only rows whose predicate is true.
   A predicate involving `NULL` can be unknown, so missing values need
   `IS NULL` or `IS NOT NULL`.
3. `SELECT` chooses the output columns. This is projection, not mutation.
4. `ORDER BY created_at DESC, customer_id DESC` creates a total order. The
   unique customer ID is the tie-breaker.
5. `LIMIT 10` keeps the first ten rows *after* sorting.

Before running, predict a result with the columns selected by the query, at
most ten rows, and one row per customer. After running, verify every country is
US or CA, timestamps never increase as you scan downward, and tied timestamps
have descending customer IDs. Without `ORDER BY`, PostgreSQL is free to return
rows in any convenient order; without a unique final sort key, tied rows may
swap places. `ROLLBACK` is the lesson's safety boundary even though today's
worked queries only read data.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day01_select_where_orderby.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT customer_id, full_name, country, created_at
FROM customers
WHERE country IN ('US','CA')
-- `customer_id` makes ties on the timestamp deterministic before LIMIT.
ORDER BY created_at DESC, customer_id
LIMIT 10;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; At most 20 rows; one row per order, newest first.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT 
  product_id,
  name,
  price,
  cost,
  (price - cost) AS gross_margin
FROM products
WHERE price > 50
ORDER BY gross_margin DESC, price DESC, product_id
LIMIT 15;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; At most 20 rows; one row per order, newest first.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Project named columns, filter rows, sort deterministically, and limit a result.
- Explain why `NULL` comparisons and an omitted `ORDER BY` can produce
  surprising results.

## Vocabulary and concepts

- **Projection:** the columns or expressions returned by `SELECT`.
- **Predicate:** a true/false/unknown condition used to filter rows.
- **Deterministic ordering:** an `ORDER BY` whose final tie-breaker uniquely
  orders the result.

## Worked example / walkthrough

Trace the first learner query in logical order: `FROM training.customers`
produces candidate rows, `WHERE country IN ('US', 'CA')` filters them,
`ORDER BY created_at DESC, customer_id DESC` fixes their order, and `LIMIT 10`
keeps the first ten. Remove the `customer_id` tie-breaker and explain why rows
with equal timestamps no longer have a guaranteed relative order.

## Practice assumptions and review method

- **Focus:** Build a result deliberately from projection, filtering, deterministic ordering, and a bounded row count.
- **Assumptions:** Timestamps are `timestamptz`; relative-date exercises use the database clock. A result is stable only when its final sort key breaks ties.
- **Failure to watch for:** Never use `= NULL`, depend on implicit row order, or apply `LIMIT` without first defining which rows are first.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Build a result deliberately from projection, filtering, deterministic ordering, and a bounded row count.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** List the 20 newest orders with customer ID and total amount.
   **Progressive hint:** Sort by `order_date DESC` and add `order_id DESC` as a unique tie-breaker before applying `LIMIT`.
   **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: List the 20 newest orders with customer ID and total amount” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `id`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 1, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
2. **Query writing:** Find the 10 most expensive products created in the last 90 days.
   **Progressive hint:** Filter the timestamp directly, then sort by price and a stable product key.
   **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Find the 10 most expensive products created in the last 90 days” at one row per product or product grouping requested. Named evidence columns/objects: `evidence`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 2, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
3. **Query writing:** Show customers from GB or DE created in the last year, newest first.
   **Progressive hint:** Use `IN` for the country set, combine the time condition with `AND`, and break timestamp ties.
   **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: Show customers from GB or DE created in the last year, newest first” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `c`, `gb`, `de`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
4. **Prediction:** Predict which rows survive `email = NULL`, then write a query that counts missing and present emails correctly.
   **Progressive hint:** Comparisons with `NULL` are unknown; use `IS NULL` and `IS NOT NULL`.
   **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Predict which rows survive email = NULL, then write a query that counts missing and present emails correctly”. Show both compared result shapes at one summary row per grouping key explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `missing_email_count`, `present_email_count`, `customer_count`, `c`.
   **Verify:** For Exercise 4, run the two forms over the identical rows in `customers`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
5. **Debugging:** Repair a top-price query that uses `LIMIT 10` without `ORDER BY` and explain why the original is nondeterministic.
   **Progressive hint:** Define the business ranking first; use a unique final key for tied prices.
   **Expected result/shape:** Exercise 5 needs the plan evidence for “Debugging: Repair a top-price query that uses LIMIT 10 without ORDER BY and explain why the original is nondeterministic”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `p`, `limit`.
   **Verify:** For Exercise 5, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `products` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers.
6. **Extension:** Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than `OFFSET`.
   **Progressive hint:** Use the last `(order_date, order_id)` pair from page one and compare row values in the same descending order.
   **Expected result/shape:** Exercise 6 must make “Extension: Return the second page of 10 newest orders using a keyset cursor derived from the first page rather than OFFSET” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `o`, `fp`, `cursor`, `offset`.
   **Verify:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `o`, `fp`, `cursor`, `offset`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Never use = NULL, depend on implicit row order, or apply LIMIT without first defining which rows are first.
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

- Can you predict which clause runs logically before `SELECT` and which runs
  after it?
- Does the learner file complete under `psql -X -v ON_ERROR_STOP=1` and finish
  with `ROLLBACK`?

## Next step

Continue to [Day 02 — aggregations and grouping](day02_aggregates_groupby_having.md).

## Deep dive and reference

Learning objectives
- Understand logical vs physical query execution order (FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT)
- Select specific columns; create derived columns with aliases
- Filter with comparison, IN, BETWEEN, LIKE/ILIKE; handle NULL semantics
- Sort by multiple keys, descending/ascending; apply LIMIT/OFFSET for pagination

Why this matters
These primitives underpin every SQL query you will write. Knowing evaluation order and NULL behavior prevents subtle bugs and makes queries predictable and performant.

Core concepts and deep dive
- Projection (SELECT): Choose only the columns you need; use column aliases for readability. Derived columns (expressions) compute values on the fly, e.g., (price - cost) AS gross_margin.
- Filtering (WHERE): Removes rows before projection and ordering. Remember three-valued logic: comparisons with NULL yield UNKNOWN and therefore fail the predicate.
- Pattern matching: LIKE is case-sensitive; ILIKE is case-insensitive (Postgres). Use % for any-length wildcard, _ for single-character. Escape literal %/_ via ESCAPE clause if necessary.
- Sorting (ORDER BY): Occurs after SELECT; you can sort by aliases. Ties are stable only by explicit secondary keys. NULLS FIRST/NULLS LAST gives control of null ordering.
- Pagination (LIMIT/OFFSET): LIMIT n returns at most n rows; OFFSET skips rows first. For large tables, prefer keyset pagination (WHERE value < last_value ORDER BY value DESC) over OFFSET for performance.

Walkthrough of the day’s script
- Customers by country with newest first: Filters by IN ('US','CA'), sorts by created_at DESC, limits to 10. Emphasizes how WHERE reduces the set before ORDER BY runs.
- Derived gross_margin for products: Computes price - cost as gross_margin, then orders by gross_margin DESC, price DESC. This shows sorting by computed aliases and multi-key ordering.
- Pattern filters: ILIKE/LIKE on email and full_name highlight pattern matching and case-insensitive search.

Postgres-specific notes
- ILIKE is a Postgres extension. For case-insensitive comparisons at scale, consider citext extension (case-insensitive text type) or full-text search for complex text queries.
- text pattern ops on leading wildcard ('%foo') cannot use btree indexes; consider trigram indexes (pg_trgm) or rewrite predicates.

Anti-patterns and pitfalls
- Selecting * in production queries; fetch only needed columns to reduce I/O.
- Assuming WHERE matches NULLs; use IS NULL/IS NOT NULL explicitly.
- Depending on implicit order without ORDER BY; SQL does not guarantee row order otherwise.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Check your understanding
- In what order are WHERE and ORDER BY evaluated, and why does that matter for derived columns?
- How does SQL treat comparisons with NULL? Provide an example that filters out NULL values.

Further reading
- Postgres pattern matching: https://www.postgresql.org/docs/current/functions-matching.html
- NULLs and three-valued logic: https://www.postgresql.org/docs/current/functions-comparison.html

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-01 — Select Where Orderby.

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day01_select_where_orderby.md
- Answer-free learner SQL: sql/postgres-60day/day01_select_where_orderby.sql

Key terms to teach in context: Projection, Predicate, Deterministic ordering. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Trace the first learner query in logical order: FROM training.customers produces candidate rows, WHERE country IN ('US', 'CA') filters them, ORDER BY createdat DESC, customerid DESC fixes their order, and LIMIT 10 keeps the first ten. Remove the customerid tie-breaker and explain why rows with equal timestamps no longer have a guaranteed relative order.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-01/ working copy. Never point setup, reset, DDL, or DML
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
