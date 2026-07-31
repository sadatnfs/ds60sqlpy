# Day 54 — Data Warehouse Project, Part 3: Aggregates

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** Review [Day 53 — slowly changing dimensions](day53_project3_dwh_part2_scd.md)
  and retain the committed Day 52 warehouse in the same database. Day 54 does
  not depend on Day 53's rolled-back changes.
- **Artifacts:** [learner SQL](../day54_project3_dwh_part3_aggregations.sql) ·
  [solution reasoning](../solutions/day54_solutions.md) ·
  [executable solution](../solutions/day54_solutions.sql)

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

2. Open **SQL-54 — Project3 DWH Part3 Aggregations** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-54/day54_project3_dwh_part3_aggregations.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

This lesson requires the committed Day 52 warehouse. The guided preparation cell resolves that cataloged predecessor. For a direct terminal run, execute Day 52 successfully first; do not assume a rolled-back Day 53 exercise persists into Day 54.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day54_project3_dwh_part3_aggregations.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day54_project3_dwh_part3_aggregations.sql
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
Aggregate table, Idempotent refresh, Late-arriving fact. Its worked SQL reads or creates `agg_sales_category_month`, `agg_sales_customer_month`, `fact_sales`, `dim_date`, `dim_product`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: For one target year/month, delete category, customer, and product aggregate rows, rebuild each independently from facts, and commit or roll back the whole unit together. Reconcile each table's period revenue with a fact-only control before considering the refresh successful.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Refresh all aggregates for a supplied year/month.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Explain late-fact effects on closed months.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Implement transactional delete/insert for one month.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Make missing-side reconciliation NULL-safe.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Prove the refresh is idempotent.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Refresh twice and compare row counts and totals.

## Self-check

- Does each primary key exactly match the documented aggregate grain?
- Can a late fact be incorporated through a deliberate period backfill?

## Next step

Continue to [Day 55 — BI drill-downs](day55_project4_bi_part1.md).

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

## Practice — match the learner prompts exactly

1. Create `agg_sales_product_month` at
   `(year, month, product_sk)` grain with revenue, units, and distinct orders,
   then validate it against `fact_sales`.
2. Create a stored procedure accepting year and month that deletes and rebuilds
   category, customer, and product aggregates for that target period.

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

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-54 — Project3 DWH Part3 Aggregations.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day54_project3_dwh_part3_aggregations.md
- Answer-free learner SQL: sql/postgres-60day/day54_project3_dwh_part3_aggregations.sql

The lesson concepts include Aggregate table, Idempotent refresh, Late-arriving fact. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For one target year/month, delete category, customer, and product aggregate rows, rebuild each independently from facts, and commit or roll back the whole unit together. Reconcile each table's period revenue with a fact-only control before considering the refresh successful.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-54/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
