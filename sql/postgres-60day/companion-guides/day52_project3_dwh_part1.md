# Day 52 — Data Warehouse Project, Part 1: Star Schema

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 51 — cash flow](day51_project2_finance_part3.md).
  Use only the course-owned disposable `dwh` schema; Day 52 resets and commits
  it for Days 53–54.
- **Artifacts:** [learner SQL](../day52_project3_dwh_part1.sql) ·
  [solution reasoning](../solutions/day52_solutions.md) ·
  [executable solution](../solutions/day52_solutions.sql)

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

2. Open **SQL-52 — Project3 DWH Part1** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-52/day52_project3_dwh_part1.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final `COMMIT` intentionally preserves the course-owned `dwh` schema, and the following verification cell passes.

This is the intentional stateful exception: Day 52 replaces only the course-owned `dwh` schema and **commits** it for Days 53–54. Review the target and the `dwh` warning before running. Do not substitute a schema that contains personal or shared work.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day52_project3_dwh_part1.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day52_project3_dwh_part1.sql
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
Fact table, Dimension, Surrogate key. Its worked SQL reads or creates `dim_date`, `dim_customer`, `dim_product`, `fact_sales`, `training.orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Write the grain beside every table before loading it. Load dimdate and the customer/product dimensions, then map each source order item to exactly one date, customer, and product key in factsales. Compare fact row count with source orderitems and check every key resolves once before committing Day 52.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day52_project3_dwh_part1.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TABLE dim_date (
  date_key       INT PRIMARY KEY,      -- yyyymmdd
  date_actual    DATE NOT NULL,
  year           INT NOT NULL,
  quarter        INT NOT NULL,
  month          INT NOT NULL,
  day            INT NOT NULL,
  day_name       TEXT NOT NULL,
  is_weekend     BOOLEAN NOT NULL
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
CREATE TABLE dim_customer (
  customer_sk    INT PRIMARY KEY DEFAULT nextval('dim_customer_sk_seq'),
  customer_id    INT NOT NULL,   -- business key
  full_name      TEXT,
  country        TEXT,
  segment        TEXT,
  valid_from     DATE NOT NULL,
  valid_to       DATE,
  is_current     BOOLEAN NOT NULL DEFAULT TRUE
);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Declare fact and dimension grains before creating a star schema.
- Load surrogate keys and validate every fact-to-dimension relationship.

## Vocabulary and concepts

- **Fact table:** measurements/events at a declared business grain.
- **Dimension:** descriptive attributes joined to facts through keys.
- **Surrogate key:** warehouse-owned identifier for a dimension row or version.

## Worked example / walkthrough

Write the grain beside every table before loading it. Load `dim_date` and the
customer/product dimensions, then map each source order item to exactly one date,
customer, and product key in `fact_sales`. Compare fact row count with source
`order_items` and check every key resolves once before committing Day 52.

## Exercises

Complete these in the [learner SQL](../day52_project3_dwh_part1.sql):

1. Add `dim_country` and connect it to customers.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Build `fact_payments` at payment grain.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
3. State/prove the `fact_sales` grain.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. Add and test unknown dimension members.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Reconcile fact rows and amount to source.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Define a late-arriving date policy.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.

Run from a reset and save checks for Days 53–54.

## Self-check

- Does every fact table have a documented, enforced source grain?
- Did the script complete with `COMMIT`, and do all source/fact counts and key
  resolution checks pass?

## Next step

Continue in the same database to
[Day 53 — slowly changing dimensions](day53_project3_dwh_part2_scd.md).

## Deep dive and reference

## Project focus

- Define fact and dimension grain with surrogate keys.
- Load date, customer, product, and sales facts from `training`.
- Add a conformed country dimension and a payment fact.

## Stateful behavior

Day 52 is intentionally different from most lessons. It drops and recreates
only the course-owned `dwh` schema, builds its base warehouse, and commits it for
Days 53 and 54. Do not run it against a `dwh` schema containing unrelated work.

The base grains are:

- `dim_date`: one row per calendar date;
- `dim_customer`: Type-2-ready versions keyed by `customer_sk`;
- `dim_product`: Type-2-ready versions keyed by `product_sk`; and
- `fact_sales`: one row per source `order_item_id`.

## Practice — match the learner prompts exactly

1. Create `dim_country`, load one row per customer country code, add
   `country_sk` to `dim_customer`, backfill it, and enforce the relationship.
2. Create `fact_payments` at one row per source payment, linked to payment-day
   `dim_date` and the customer version valid on that date.

## Required Days 52–54 sequence

1. Run Day 52 once; it commits the base warehouse.
2. Run Day 53 in the same database; its exercise changes roll back.
3. Run Day 54 in the same database; its aggregate/procedure changes roll back.

Day 54 depends on committed Day 52 state, not on Day 53 changes persisting.

## Validation and limits

- `fact_sales` rows must equal source `order_items` rows.
- `fact_payments` rows must equal source `payments` rows.
- Every fact date and dimension key must resolve exactly once.
- Use `psql -v ON_ERROR_STOP=1`; a partial warehouse is not a passing load.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-52 — Project3 DWH Part1.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day52_project3_dwh_part1.md
- Answer-free learner SQL: sql/postgres-60day/day52_project3_dwh_part1.sql

The lesson concepts include Fact table, Dimension, Surrogate key. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Write the grain beside every table before loading it. Load dimdate and the customer/product dimensions, then map each source order item to exactly one date, customer, and product key in factsales. Compare fact row count with source orderitems and check every key resolves once before committing Day 52.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-52/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
