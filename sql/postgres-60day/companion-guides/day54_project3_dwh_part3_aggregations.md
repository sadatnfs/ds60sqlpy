# Day 54: Data Warehouse Project, Part 3: Aggregates

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** Review [Day 53; slowly changing dimensions](day53_project3_dwh_part2_scd.md)
  and retain the committed Day 52 warehouse in the same database. Day 54 does
  not depend on Day 53's rolled-back changes.
- **Artifacts:** [learner SQL](../day54_project3_dwh_part3_aggregations.sql) ·
  [solution reasoning](../solutions/day54_solutions.md) ·
  [executable solution](../solutions/day54_solutions.sql)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-54**. The
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
   `.learning/sql/sql-54/lesson/workspace/sql/postgres-60day/day54_project3_dwh_part3_aggregations.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-54
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Aggregate table, Idempotent refresh, Late-arriving fact. Its worked SQL reads or creates `agg_sales_category_month`, `agg_sales_customer_month`, `fact_sales`, `dim_date`, `dim_product`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: For one target year/month, delete category, customer, and product aggregate rows, rebuild each independently from facts, and commit or roll back the whole unit together. Reconcile each table's period revenue with a fact-only control before considering the refresh successful.
The first runnable example has a concrete contract: Example 1 must print the expected DDL command tag for `agg_sales_category_month`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state. Its final projection is the columns written in the final `SELECT`. Verify the command tag in `pg_catalog`/`information_schema`, run one accepted value and one value the declared rule rejects, and confirm the lesson rollback removes the course-owned object. Where this query can emit `NULL`, identify the exact source expression and explain whether the output preserves, classifies, or rejects it.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day54_project3_dwh_part3_aggregations.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TABLE agg_sales_category_month (
  year    INT NOT NULL,
  month   INT NOT NULL,
  category TEXT NOT NULL,
  revenue NUMERIC(14,2) NOT NULL,
  PRIMARY KEY (year, month, category)
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must print the expected DDL command tag for `agg_sales_category_month`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

### Example 2

```sql
CREATE TABLE agg_sales_customer_month (
  year     INT NOT NULL,
  month    INT NOT NULL,
  customer_sk INT NOT NULL,
  revenue  NUMERIC(14,2) NOT NULL,
  PRIMARY KEY (year, month, customer_sk)
);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 2 must print the expected DDL command tag for `agg_sales_customer_month`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

## Learning objectives

- Build aggregate tables with an enforced monthly grain.
- Refresh one period idempotently and reconcile it with warehouse facts.

## Vocabulary and concepts

- **Aggregate table:** persisted summaries at a coarser fact grain.
- **Idempotent refresh:** a rebuild whose repeated execution yields the same
  target-period rows.
- **Late-arriving fact:** a fact received after its reporting period was first
  built.

## Worked example / walkthrough

For one target year/month, delete category, customer, and product aggregate
rows, rebuild each independently from facts, and commit or roll back the whole
unit together. Reconcile each table's period revenue with a fact-only control
before considering the refresh successful.

## Exercises

Complete these in the
[learner SQL](../day54_project3_dwh_part3_aggregations.sql):

1. Add and validate `agg_sales_product_month`.
   **Inputs/evidence:** For sql-54 Exercise 1, read from `dim_product`, `agg_sales_product_month`, `fact_sales`, and `dim_date`. Build the answer toward `year`, `month`, and `product_sk`; keep `year`, `month`, and `product_sk` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-54 Exercise 1, expected output: one row per `year`, `month`, and `product_sk`. The final columns are `year`, `month`, and `product_sk`. The final order is `a.year, a.month`.
   **Verify:** For sql-54 Exercise 1, independently aggregate `dim_product`, `agg_sales_product_month`, `fact_sales`, and `dim_date` by `year`, `month`, and `product_sk`; require one output row for every distinct `year`, `month`, and `product_sk` tuple and compare `product_sk` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `row_count` for the existing `year`, and `month` tuple and verify the new tuple appears exactly once.
2. Refresh all aggregates for a supplied year/month.
   **Inputs/evidence:** For sql-54 Exercise 2, read from `agg_sales_category_month`, `agg_sales_customer_month`, `agg_sales_product_month`, `fact_sales`, and `dim_date`. Build the answer toward `year`, `month`, and `category`; keep `year`, `month`, and `product_sk` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-54 Exercise 2, expected output: one row per `year`, `month`, and `product_sk`. The final columns are `year`, `month`, and `category`. The final order is `dd.year DESC, dd.month DESC`.
   **Verify:** For sql-54 Exercise 2, assert no more than 1 rows, no duplicate `year`, `month`, and `product_sk`, and no adjacent pair that violates `dd.year DESC, dd.month DESC`. Rejoin the returned keys to `agg_sales_category_month`, `agg_sales_customer_month`, `agg_sales_product_month`, `fact_sales`, and `dim_date` to confirm `year`, `month`, and `category` came from the same source rows. Run with 1 minus one and 1 plus one eligible rows; require the output cap of 1 while retaining `dd.year DESC, dd.month DESC`.
3. Explain late-fact effects on closed months.
   **Inputs/evidence:** For sql-54 Exercise 3, read from `fact_sales`, and `dim_date`. Build the answer toward `year`, `month`, `fact_rows`, and `latest_fact_date`; keep `year`, and `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-54 Exercise 3, expected output: one row per `year`, and `month`. The final columns are `year`, `month`, `fact_rows`, and `latest_fact_date`. The final order is `dd.year DESC, dd.month DESC`.
   **Verify:** For sql-54 Exercise 3, independently aggregate `fact_sales`, and `dim_date` by `year`, and `month`; require one output row for every distinct `year`, and `month` tuple and compare `fact_rows` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `fact_rows` for the existing `year`, and `month` tuple and verify the new tuple appears exactly once.
4. Implement transactional delete/insert for one month.
   **Inputs/evidence:** For sql-54 Exercise 4, read the target keys from `agg_sales_category_month` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-54 Exercise 4, expected output: the command tag and an independently counted set of affected `year`, and `month` values. The final columns are `year`, `month`, `category_rows`, and `revenue`. The final order is `year DESC, month DESC`.
   **Verify:** For sql-54 Exercise 4, materialize the intended `year`, and `month` target set first; require the command tag/`RETURNING` set to match it, then query `agg_sales_category_month` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `year`, and `month` values in both cases.
5. Make missing-side reconciliation NULL-safe.
   **Inputs/evidence:** For sql-54 Exercise 5, read from `agg_sales_category_month`, `fact_sales`, `dim_date`, and `f.revenue`. Build the answer toward `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`; keep `year`, and `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-54 Exercise 5, expected output: one row per `year`, and `month`. The final columns are `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference`. The final order is `year, month`.
   **Verify:** For sql-54 Exercise 5, project `year`, and `month` plus the raw source columns from `agg_sales_category_month`, `fact_sales`, `dim_date`, and `f.revenue` at each join stage; record row count and distinct `year`, and `month`, then assert the final `year`, `month`, `aggregate_revenue`, `fact_revenue`, and `difference` values match those staged rows without unintended fanout or loss. Repeat with `NULL` in `year`, and `month` and state whether the row is kept, rejected, or classified.
6. Prove the refresh is idempotent.
   **Inputs/evidence:** For sql-54 Exercise 6, read from `agg_sales_category_month`, `fact_sales`, `dim_date`, and `aggregate_snapshot_before`. Build the answer toward `except`; keep `except` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-54 Exercise 6, expected output: at most one row keyed by `except`. The final columns are `except`. The final order is `dd.year DESC, dd.month DESC`.
   **Verify:** For sql-54 Exercise 6, assert no more than 1 rows, no duplicate `except`, and no adjacent pair that violates `dd.year DESC, dd.month DESC`. Rejoin the returned keys to `agg_sales_category_month`, `fact_sales`, `dim_date`, and `aggregate_snapshot_before` to confirm `except` came from the same source rows. Add duplicate source candidates for `except`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

Refresh twice and compare row counts and totals.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Every refreshed month's aggregate revenue must equal fact revenue.
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

- Does each primary key exactly match the documented aggregate grain?
- Can a late fact be incorporated through a deliberate period backfill?

## Next step

Continue to [Day 55; BI drill-downs](day55_project4_bi_part1.md).

## Deep dive and reference

## Project focus

- Build monthly category and customer aggregate tables.
- Add a monthly product aggregate with a declared primary-key grain.
- Refresh one period idempotently and reconcile it to facts.

## Preconditions and state

Run Day 52 first in the same database. The learner creates its aggregate tables,
loads them, performs data-quality checks, and rolls the entire Day 54 transaction
back.

The starter grains are `(year, month, category)` and
`(year, month, customer_sk)`. Revenue is summed from `fact_sales.amount`; date
attributes come from `dim_date`.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Refresh design

- Delete and insert all related aggregates in one transaction.
- A period rebuild is idempotent when the primary-key grain is correct.
- Filter facts through `dim_date.year` and `dim_date.month`.
- Aggregate each side independently before reconciliation to prevent fanout.

## Validation and limits

- Every refreshed month's aggregate revenue must equal fact revenue.
- Orphan surrogate keys must be zero.
- Late facts require rerunning affected periods or a deliberate backfill window.
- The compact seed does not need aggregates for speed; this is a warehouse
  serving-pattern exercise.
- Day 54 does not require rolled-back Day 53 audit/SCD changes.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-54 — Project3 DWH Part3 Aggregations.

I have completed the direct catalog prerequisite: `sql-53`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day54_project3_dwh_part3_aggregations.md
- Answer-free learner SQL: sql/postgres-60day/day54_project3_dwh_part3_aggregations.sql

Key terms to teach in context: Aggregate table, Idempotent refresh, Late-arriving fact. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For one target year/month, delete category, customer, and product aggregate rows, rebuild each independently from facts, and commit or roll back the whole unit together. Reconcile each table's period revenue with a fact-only control before considering the refresh successful.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-54/ working copy. Never point setup, reset, DDL, or DML
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
