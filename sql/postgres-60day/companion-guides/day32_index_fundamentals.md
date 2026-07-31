# Day 32 — Index Fundamentals

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 31 — EXPLAIN and EXPLAIN ANALYZE](day31_explain_analyze.md)
- **Artifacts:** [learner SQL](../day32_index_fundamentals.sql) ·
  [solution reasoning](../solutions/day32_solutions.md) ·
  [executable solution](../solutions/day32_solutions.sql)

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

2. Open **SQL-32 — Index Fundamentals** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-32/lesson/workspace/sql/postgres-60day/day32_index_fundamentals.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day32_index_fundamentals.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day32_index_fundamentals.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Selectivity, Index scan, Index-only scan. Its worked SQL reads or creates `orders`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Capture a category-filter plan before creating products(category), create the index inside the rollback-only transaction, and rerun the identical query. Record the plan even if PostgreSQL keeps the sequential scan: the compact seed can make reading the table cheaper than traversing an index.
The first runnable example has a concrete contract: Example 1 must print the expected DDL command tag for `idx_orders_total_amount`, and `orders`. Verify the object in `pg_catalog.pg_index`, and `pg_catalog.pg_indexes`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state. Its final projection is the columns written in the final `SELECT`. Verify the command tag in `pg_catalog`/`information_schema`, run one accepted value and one value the declared rule rejects, and confirm the lesson rollback removes the course-owned object.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day32_index_fundamentals.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE INDEX idx_orders_total_amount ON orders(total_amount);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must print the expected DDL command tag for `idx_orders_total_amount`, and `orders`. Verify the object in `pg_catalog.pg_index`, and `pg_catalog.pg_indexes`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

### Example 2

```sql
CREATE INDEX idx_orders_order_date ON orders(order_date);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 2 must print the expected DDL command tag for `idx_orders_order_date`, and `orders`. Verify the object in `pg_catalog.pg_index`, and `pg_catalog.pg_indexes`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

## Learning objectives

- Match a B-tree index to equality, range, and ordering requirements.
- Explain a planner choice using selectivity, table size, projection, and
  measured cost.

## Vocabulary and concepts

- **Selectivity:** the fraction of rows a predicate is expected to return.
- **Index scan:** an access path that uses index entries to locate heap rows.
- **Index-only scan:** a plan that can satisfy selected values from the index,
  subject to visibility checks.

## Worked example / walkthrough

Capture a category-filter plan before creating `products(category)`, create the
index inside the rollback-only transaction, and rerun the identical query.
Record the plan even if PostgreSQL keeps the sequential scan: the compact seed
can make reading the table cheaper than traversing an index.

## Exercises

Complete these in the [learner SQL](../day32_index_fundamentals.sql):

1. Create and test an index on `products(category)`.
   **Inputs/evidence:** For sql-32 Exercise 1, run the underlying read-only query over `products`, `training.idx_products_category_solution`, and `idx_products_category_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-32 Exercise 1, expected output: one row per `product_id`. The final columns are `product_id`, `name`, and `price`.
   **Verify:** For sql-32 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
2. Compare plans before and after dropping/recreating that index.
   **Inputs/evidence:** For sql-32 Exercise 2, run the underlying read-only query over `products`, `training.idx_products_category_compare`, and `idx_products_category_compare` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-32 Exercise 2, expected output: one row per `product_id`. The final columns are `product_id`.
   **Verify:** For sql-32 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
3. Predict the scan choice from category frequency, then measure it.
   **Inputs/evidence:** For sql-32 Exercise 3, run the underlying read-only query over `products` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-32 Exercise 3, expected output: one row per `category`. The final columns are `category`, and `products`. The final order is `products DESC, category`.
   **Verify:** For sql-32 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `category` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
4. Index `payments(payment_date)` and test a half-open date range.
   **Inputs/evidence:** For sql-32 Exercise 4, run the underlying read-only query over `payments`, and `idx_payments_date_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-32 Exercise 4, expected output: one row per `payment_id`. The final columns are `payment_id`, and `amount`.
   **Verify:** For sql-32 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `payment_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
5. Diagnose `lower(country)` and test a matching expression index.
   **Inputs/evidence:** For sql-32 Exercise 5, run the underlying read-only query over `customers`, and `idx_customers_lower_country_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-32 Exercise 5, expected output: one row per `customer_id`. The final columns are `customer_id`.
   **Verify:** For sql-32 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
6. Prove that index order does not replace an explicit `ORDER BY`.
   **Inputs/evidence:** For sql-32 Exercise 6, read from `customers`. Build the answer toward `customer_id`, and `country`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-32 Exercise 6, expected output: at most 10 rows keyed by `customer_id`. The final columns are `customer_id`, and `country`. The final order is `country, customer_id`.
   **Verify:** For sql-32 Exercise 6, assert no more than 10 rows, no duplicate `customer_id`, and no adjacent pair that violates `country, customer_id`. Rejoin the returned keys to `customers` to confirm `customer_id`, and `country` came from the same source rows. Run with 10 minus one and 10 plus one eligible rows; require the output cap of 10 while retaining `country, customer_id`.

Compare selective and unselective predicates against the same indexed column.

## Self-check

- Are the before/after SQL, parameters, and returned rows identical?
- Can you explain index write/storage cost as well as possible read benefit?

## Next step

Continue to [Day 33 — composite, covering, and partial indexes](day33_index_optimization_strategies.md).

## Deep dive and reference

## What you will learn

- Create B-tree indexes for equality and range predicates.
- Observe planner choices before and after an index exists.
- Explain why a valid index can remain unused on a small or unselective query.

## How the learner script uses the current schema

Inside a rollback-only transaction, the script creates indexes on
`orders.total_amount`, `orders.order_date`, and `customers.country`. It then
executes matching filters with `EXPLAIN ANALYZE`. No course index persists after
the final `ROLLBACK`.

B-tree is PostgreSQL's default and supports equality, ranges, ordering, `IN`,
and prefix pattern searches. A hash index is mentioned only as a contrast;
B-tree already handles the equality lookup on `customers.email`.

## Planner and index concepts

- Selective predicates benefit most because they fetch a small fraction of the
  table.
- Every index adds storage and write/vacuum work. “Index every column” is not a
  sound policy.
- An index-only scan also depends on selected columns and visibility-map state.
- `SELECT *` can make heap access necessary even when a filter uses an index.
- On the compact seed, a sequential scan may correctly be cheaper.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Pitfalls and validation

- Use only the setup's valid order statuses: `placed`, `paid`, `shipped`,
  `delivered`, and `returned`.
- Do not disable sequential scans as proof that an index is beneficial.
- Index names are schema-local; use exercise-specific names to avoid collisions.
- The learner transaction rolls all index experiments back safely.

## Expanded practice lab

Prompts 3–6 separate index *eligibility* from a planner's cost decision. First
measure category frequency: on a compact table, reading every page can be
cheaper than bouncing through an index. Use a half-open timestamp range for the
payment-date index so boundary semantics are explicit.

`lower(country)` is a different indexed expression from `country`; an
expression index must match the query expression. Finally, remember that an
index's physical order never replaces `ORDER BY` in the SQL result contract.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-32 — Index Fundamentals.

I have completed the direct catalog prerequisite: `sql-31`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day32_index_fundamentals.md
- Answer-free learner SQL: sql/postgres-60day/day32_index_fundamentals.sql

Key terms to teach in context: Selectivity, Index scan, Index-only scan. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Capture a category-filter plan before creating products(category), create the index inside the rollback-only transaction, and rerun the identical query. Record the plan even if PostgreSQL keeps the sequential scan: the compact seed can make reading the table cheaper than traversing an index.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-32/ working copy. Never point setup, reset, DDL, or DML
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
