# Day 36: Materialized Views and Caching

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-36**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-36/lesson/workspace/sql/postgres-60day/day36_materialized_views.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-36
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 35; performance pitfalls](day35_avoiding_pitfalls.md)
- **Artifacts:** [learner SQL](../day36_materialized_views.sql) ·
  [solution reasoning](../solutions/day36_solutions.md) ·
  [executable solution](../solutions/day36_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Materialized view, Freshness, Concurrent refresh. Its worked SQL reads or creates `order_items`, `products`, `orders`, `mv_category_month_revenue`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Create the monthly-category materialized view inside the learner transaction, reconcile its total revenue and row-grain uniqueness with the source query, then refresh it. Query speed is only one dimension; record when the stored rows become stale and who would own refresh failures.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `category`, and `month` with columns `category`, `month`, and `revenue` from `order_items`, `products`, `orders`, and `mv_category_month_revenue`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `category`, `month`, and `revenue`. Verify the command tag in `pg_catalog`/`information_schema`, run one accepted value and one value the declared rule rejects, and confirm the lesson rollback removes the course-owned object.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day36_materialized_views.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

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

**Expected result/shape:** Example 1 returns one grouped row per `category`, and `month` with columns `category`, `month`, and `revenue` from `order_items`, `products`, `orders`, and `mv_category_month_revenue`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
SELECT * FROM mv_category_month_revenue ORDER BY month DESC, revenue DESC LIMIT 50;
```

**How to read it:** Example 2: Start with `mv_category_month_revenue` in `FROM`/`JOIN`. The final `SELECT` displays `*`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per the primary/business key of `mv_category_month_revenue`, capped at 50 rows from `mv_category_month_revenue`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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
   **Inputs/evidence:** For sql-36 Exercise 1, read from `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_solution`. Compute `week_start`, `country`, and `revenue` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-36 Exercise 1, expected output: one row per observed week-country pair. PostgreSQL weeks begin on Monday under `date_trunc('week',. The final columns are `week_start`, `country`, and `revenue`. The final order is `week_start DESC, revenue DESC`.
   **Verify:** For sql-36 Exercise 1, evaluate each of `revenue` in a separate control `SELECT` over `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_solution`; require one final row and compare every value. Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `country` tuple and verify the new tuple appears exactly once.
2. Compare source-query and materialized-query plans.
   **Inputs/evidence:** For sql-36 Exercise 2, run the underlying read-only query over `orders`, `customers`, `order_items`, and `mv_weekly_country_revenue_compare` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-36 Exercise 2, expected output: one row per `country`. The final columns are `week_start`, `country`, and `revenue`.
   **Verify:** For sql-36 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `country` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
3. Predict and verify stale results before refresh.
   **Inputs/evidence:** For sql-36 Exercise 3, read from `orders`, and `mv_weekly_country_revenue_solution`. Compute `live_total`, and `refreshed_mv_total` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-36 Exercise 3, expected output: exactly one aggregate summary row. The final columns are `live_total`, and `refreshed_mv_total`.
   **Verify:** For sql-36 Exercise 3, evaluate each of `live_total`, and `refreshed_mv_total` in a separate control `SELECT` over `orders`, and `mv_weekly_country_revenue_solution` using `(order_id = (SELECT MIN(order_id) FROM orders))`; require one final row and compare every value. Add one row for which `(order_id = (SELECT MIN(order_id) FROM orders))` is true and one for which it is false; verify only the matching `order_id` value is returned.
4. Design the unique index required by concurrent refresh.
   **Inputs/evidence:** For sql-36 Exercise 4, read from `pg_indexes`. Build the answer toward `indexdef`; keep `indexdef` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-36 Exercise 4, expected output: one row per `indexdef`. The final columns are `indexdef`.
   **Verify:** For sql-36 Exercise 4, run an anti-check that counts rows where NOT ((schemaname = 'training' AND tablename = 'mv_weekly_country_revenue_solution')); require unique `indexdef` where the expected grain is one row per key and confirm the projected `indexdef` against `pg_indexes`. Add duplicate source candidates for `indexdef`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
5. Reconcile line revenue with the chosen business definition.
   **Inputs/evidence:** For sql-36 Exercise 5, read from `orders`, and `order_items`. Compute `header_revenue`, and `line_revenue` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-36 Exercise 5, expected output: exactly one aggregate summary row. The final columns are `header_revenue`, and `line_revenue`.
   **Verify:** For sql-36 Exercise 5, evaluate each of `header_revenue`, and `line_revenue` in a separate control `SELECT` over `orders`, and `order_items`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
6. Explain absent dimension combinations versus explicit zeros.
   **Inputs/evidence:** For sql-36 Exercise 6, read from `orders`, `customers`, and `mv_weekly_country_revenue_solution`. Build the answer toward `week`, `country`, and `revenue`; keep `week`, and `country` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-36 Exercise 6, expected output: at most 20 rows keyed by `week`, and `country`. The final columns are `week`, `country`, and `revenue`. The final order is `m.week DESC, c.country`.
   **Verify:** For sql-36 Exercise 6, assert no more than 20 rows, no duplicate `week`, and `country`, and no adjacent pair that violates `m.week DESC, c.country`. Rejoin the returned keys to `orders`, `customers`, and `mv_weekly_country_revenue_solution` to confirm `week`, `country`, and `revenue` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `m.week DESC, c.country`.

Write a freshness expectation and validation query beside the refresh design.

## Self-check

- Does a declared key uniquely identify every materialized row?
- Can the consumer tolerate the documented refresh interval and failure mode?

## Next step

Continue to [Day 37; partitioning and sharding](day37_partitioning_sharding.md).

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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-36 — Materialized Views.

I have completed the direct catalog prerequisite: `sql-35`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day36_materialized_views.md
- Answer-free learner SQL: sql/postgres-60day/day36_materialized_views.sql

Key terms to teach in context: Materialized view, Freshness, Concurrent refresh. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Create the monthly-category materialized view inside the learner transaction, reconcile its total revenue and row-grain uniqueness with the source query, then refresh it. Query speed is only one dimension; record when the stored rows become stale and who would own refresh failures.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-36/ working copy. Never point setup, reset, DDL, or DML
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
