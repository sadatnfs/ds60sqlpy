# Day 36 — Materialized Views and Caching

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 35 — performance pitfalls](day35_avoiding_pitfalls.md)
- **Artifacts:** [learner SQL](../day36_materialized_views.sql) ·
  [solution reasoning](../solutions/day36_solutions.md) ·
  [executable solution](../solutions/day36_solutions.sql)

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

2. Open **SQL-36 — Materialized Views** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-36/day36_materialized_views.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day36_materialized_views.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day36_materialized_views.sql
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
Materialized view, Freshness, Concurrent refresh. Its worked SQL reads or creates `order_items`, `products`, `orders`, `mv_category_month_revenue`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Create the monthly-category materialized view inside the learner transaction, reconcile its total revenue and row-grain uniqueness with the source query, then refresh it. Query speed is only one dimension; record when the stored rows become stale and who would own refresh failures.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day36_materialized_views.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE MATERIALIZED VIEW mv_category_month_revenue AS
SELECT p.category,
       date_trunc('month', o.order_date)::date AS month,
       SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
GROUP BY p.category, date_trunc('month', o.order_date);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT * FROM mv_category_month_revenue ORDER BY month DESC, revenue DESC LIMIT 50;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Materialize a query at a declared grain and reconcile it with source data.
- Design refresh, freshness, ownership, and failure expectations.

## Vocabulary and concepts

- **Materialized view:** stored rows produced by a query and refreshed
  explicitly.
- **Freshness:** how current cached output is relative to its sources.
- **Concurrent refresh:** a read-preserving refresh mode with unique-index and
  transaction restrictions.

## Worked example / walkthrough

Create the monthly-category materialized view inside the learner transaction,
reconcile its total revenue and row-grain uniqueness with the source query,
then refresh it. Query speed is only one dimension; record when the stored rows
become stale and who would own refresh failures.

## Exercises

Complete these in the [learner SQL](../day36_materialized_views.sql):

1. Create weekly country revenue materialization.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
2. Compare source-query and materialized-query plans.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
3. Predict and verify stale results before refresh.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Design the unique index required by concurrent refresh.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
5. Reconcile line revenue with the chosen business definition.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Explain absent dimension combinations versus explicit zeros.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.

Write a freshness expectation and validation query beside the refresh design.

## Self-check

- Does a declared key uniquely identify every materialized row?
- Can the consumer tolerate the documented refresh interval and failure mode?

## Next step

Continue to [Day 37 — partitioning and sharding](day37_partitioning_sharding.md).

## Deep dive and reference

## What you will learn

- Store the result of an expensive query in a materialized view (MV).
- Refresh cached results when source tables change.
- Compare freshness, storage, and query cost with querying base tables.

## How the learner script uses the current schema

The script creates `mv_category_month_revenue` from `orders`, `order_items`, and
`products`. Its grain is one row per `(category, month)`, and revenue is line
price times quantity after discount. It queries and refreshes the MV, then rolls
the object back.

A normal view stores only SQL and executes it on every read. A materialized view
stores rows and can be indexed, but those rows are stale until refreshed.

## Refresh behavior

- `REFRESH MATERIALIZED VIEW` replaces the stored contents and blocks reads of
  that MV during refresh.
- `REFRESH ... CONCURRENTLY` permits reads but requires a qualifying unique
  index and cannot run inside an explicit transaction block.
- PostgreSQL does not provide general native incremental MV refresh; selective
  rollup tables are a separate design.

## Practice — match the learner prompts exactly

1. Create an MV for weekly revenue by `customers.country`. Use a clear grain of
   `(week, country)` and line-item net revenue.
2. Compare the same weekly-country query over base tables with a query over the
   MV. Capture actual plans, buffers, row counts, and freshness assumptions.

## Pitfalls and validation

- Reconcile the MV's total revenue to the source query before measuring speed.
- A fast stale result can be wrong for the consumer's freshness requirement.
- The compact seed may make the raw query as fast as or faster than the MV.
- Document refresh ownership and failure behavior before relying on an MV.
- The learner transaction safely removes the demonstration MV at rollback.

## Expanded practice lab

Prompts 3–6 focus on the materialized view's data contract. A new base row is
invisible until refresh, so record both data time and refresh time. Concurrent
refresh requires a qualifying unique index and cannot be demonstrated as a
first population inside this rollback-only lesson.

Reconcile the view to the exact line-revenue definition it materializes; stored
order totals are a separate measure. Grouped aggregates emit no row for an
absent dimension combination, so any displayed zero must come from an explicit
dimension/date spine and outer join.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-36 — Materialized Views.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day36_materialized_views.md
- Answer-free learner SQL: sql/postgres-60day/day36_materialized_views.sql

The lesson concepts include Materialized view, Freshness, Concurrent refresh. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Create the monthly-category materialized view inside the learner transaction, reconcile its total revenue and row-grain uniqueness with the source query, then refresh it. Query speed is only one dimension; record when the stored rows become stale and who would own refresh failures.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-36/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
