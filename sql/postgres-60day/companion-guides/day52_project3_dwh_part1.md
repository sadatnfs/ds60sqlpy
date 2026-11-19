# Day 52: Data Warehouse Project, Part 1: Star Schema

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-52**. The
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
   `.learning/sql/sql-52/lesson/workspace/sql/postgres-60day/day52_project3_dwh_part1.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-52
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
- **Prerequisites:** [Day 51; cash flow](day51_project2_finance_part3.md).
  Use only the course-owned disposable `dwh` schema; Day 52 resets and commits
  it for Days 53 and 54.
- **Artifacts:** [learner SQL](../day52_project3_dwh_part1.sql) ·
  [solution reasoning](../solutions/day52_solutions.md) ·
  [executable solution](../solutions/day52_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Fact table, Dimension, Surrogate key. Its worked SQL reads or creates `dim_date`, `dim_customer`, `dim_product`, `fact_sales`, `training.orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Write the grain beside every table before loading it. Load `dim_date` and the customer/product dimensions, then map each source order item to exactly one date, customer, and product key in `fact_sales`. Compare fact row count with source `order_items` and check every key resolves once before committing Day 52.
The first runnable example has a concrete contract: Example 1 must print the expected DDL command tag for `dim_date`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day52_project3_dwh_part1.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
CREATE TABLE dim_date (
  date_key INT PRIMARY KEY, -- yyyymmdd
  date_actual DATE NOT NULL,
  year INT NOT NULL,
  quarter INT NOT NULL,
  month INT NOT NULL,
  day INT NOT NULL,
  day_name TEXT NOT NULL,
  is_weekend BOOLEAN NOT NULL
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must print the expected DDL command tag for `dim_date`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

### Example 2

```sql
CREATE TABLE dim_customer (
  customer_sk INT PRIMARY KEY DEFAULT nextval('dim_customer_sk_seq'),
  customer_id INT NOT NULL, -- business key
  full_name TEXT,
  country TEXT,
  segment TEXT,
  valid_from DATE NOT NULL,
  valid_to DATE,
  is_current BOOLEAN NOT NULL DEFAULT TRUE
);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 2 must print the expected DDL command tag for `dim_customer`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

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
   **Inputs/evidence:** For sql-52 Exercise 1, create `dim_country(country_sk, country_code)` with one row per distinct `training.customers.country`, add `country_sk` to `dim_customer` as a foreign key to it, backfill it from the text `country`, and make it `NOT NULL` before the final `COMMIT`.
   **Expected result/shape:** For sql-52 Exercise 1, expected output: `INSERT 0 8` for the country codes, `UPDATE 500` for the backfill, and `ALTER TABLE` for the `NOT NULL` change, so every customer-dimension version has exactly one `country_sk`. Days 53 and 54 run against this committed state, and Day 53's SCD2 inserts must keep it.
   **Verify:** For sql-52 Exercise 1, right after the backfill, confirm that `SELECT COUNT(*) FROM dim_country` is 8, that no `dim_customer` row has a NULL `country_sk`, and that joining `dim_customer` to `dim_country` on `country_sk` gives `country_code = country` on every row; after a savepoint, an `INSERT` into `dim_customer` without `country_sk` must fail with SQLSTATE `23502`, then roll back to the savepoint.
2. Build `fact_payments` at payment grain.
   **Inputs/evidence:** For sql-52 Exercise 2, create `fact_payments` with one row per `training.payments` row, keyed by `payment_id`, and load it by joining each payment to its order, to `dim_date` on the payment date, and to the `dim_customer` version valid on that date.
   **Expected result/shape:** For sql-52 Exercise 2, expected output: `INSERT 0 3836`, one fact row per source payment, then a check row with `countries` 8, `fact_payment_rows` 3836, and `source_payment_rows` 3836. The fact columns are `payment_id`, `order_id`, `date_key`, `customer_sk`, `amount`, and `method`.
   **Verify:** For sql-52 Exercise 2, confirm that `fact_payment_rows` equals `source_payment_rows` (3836) and that `SELECT SUM(amount) FROM fact_payments` equals `SELECT SUM(amount) FROM training.payments` (1831900.81); a join that lost payments would lower the count, and a join to every customer version would raise it.
3. State/prove the `fact_sales` grain.
   **Inputs/evidence:** For sql-52 Exercise 3, read from `fact_sales` and count its rows, its distinct `order_id` values, and its distinct `order_item_id` values.
   **Expected result/shape:** For sql-52 Exercise 3, expected output: one row with `fact_rows` 13085, `orders` 4362, and `distinct_order_items` 13085, which shows that `fact_sales` has one row per order line and that `order_id` alone does not identify a row. The final columns are `fact_rows`, `orders`, and `distinct_order_items`.
   **Verify:** For sql-52 Exercise 3, confirm that `fact_rows` and `distinct_order_items` both equal `SELECT COUNT(*) FROM training.order_items` (13085) while `orders` is only 4362; `SELECT order_id FROM fact_sales GROUP BY order_id HAVING COUNT(*) > 1` returns 3490 orders, which proves that `order_id` repeats.
4. Add and test unknown dimension members.
   **Inputs/evidence:** For sql-52 Exercise 4, add an unknown member with surrogate key -1 to `dim_country`, `dim_customer`, and `dim_product`, then route a source row whose `customer_id` (-999) has no dimension match to that member with `COALESCE(dc.customer_sk, -1)` after a `LEFT JOIN`.
   **Expected result/shape:** For sql-52 Exercise 4, expected output: three `INSERT 0 1` commands and one row whose `routed_customer_sk` is -1. The final columns are `routed_customer_sk`.
   **Verify:** For sql-52 Exercise 4, confirm that `SELECT customer_sk FROM dim_customer WHERE customer_sk = -1` returns one row and that the routing query returns -1 for `customer_id` -999; replace -999 with 1 and confirm that it returns that customer's real `customer_sk` (1) instead.
5. Reconcile fact rows and amount to source.
   **Inputs/evidence:** For sql-52 Exercise 5, compare `fact_sales` with `training.order_items`: the two row counts, the total fact `amount`, and the source line total `ROUND(SUM(quantity * unit_price * (1 - discount)), 2)`.
   **Expected result/shape:** For sql-52 Exercise 5, expected output: one row with `fact_rows` and `source_rows` both 13085, `fact_amount` 2355648.13, and `source_amount` 2355647.12; the 1.01 gap comes from rounding each fact line to cents. The final columns are `fact_rows`, `source_rows`, `fact_amount`, and `source_amount`.
   **Verify:** For sql-52 Exercise 5, confirm equal row counts, then recompute the source with the fact's rounding rule, `SELECT SUM(ROUND(quantity * unit_price * (1 - discount), 2)) FROM training.order_items`, and expect 2355648.13, exactly `fact_amount`; a gap that remains after that would be a real load error.
6. Define a late-arriving date policy.
   **Inputs/evidence:** For sql-52 Exercise 6, read from `training.payments`, and `dim_date`. Build the answer toward `payment_id`, and `date`; keep `payment_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-52 Exercise 6, expected output: one row per `payment_id`. The final columns are `payment_id`, and `date`. The final order is `p.payment_id`.
   **Verify:** For sql-52 Exercise 6, project `payment_id` plus the raw source columns from `training.payments`, and `dim_date` at each join stage; record row count and distinct `payment_id`, then assert the final `payment_id`, and `date` values match those staged rows without unintended fanout or loss. Add one row for which `(d.date_key IS NULL)` is true and one for which it is false; verify only the matching `payment_id` value is returned.

Run from a reset and save checks for Days 53 and 54.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** `fact_sales` rows must equal source `order_items` rows.
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

- Does every fact table have a documented, enforced source grain?
- Did the script complete with `COMMIT`, and do all source/fact counts and key
  resolution checks pass?

## Next step

Continue in the same database to
[Day 53; slowly changing dimensions](day53_project3_dwh_part2_scd.md).

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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Required Days 52 to 54 sequence

1. Run Day 52 once, either this learner file or `day52_solutions.sql`; it
   commits the base warehouse.
2. Run Day 53 in the same database. It first checks the Exercise 1 country
   link (a `NOT NULL` `country_sk` that points at `dim_country`), adds it only
   if your Day 52 run did not, keeps it in every new SCD2 version, and rolls all
   its changes back.
3. Run Day 54 in the same database; its aggregate/procedure changes roll back.

Day 54 depends on committed Day 52 state, not on Day 53 changes persisting.
Either Day 52 file is a valid starting point for the learner and solution files
of Days 53 and 54.

## Validation and limits

- `fact_sales` rows must equal source `order_items` rows.
- `fact_payments` rows must equal source `payments` rows.
- Every fact date and dimension key must resolve exactly once.
- Use `psql -v ON_ERROR_STOP=1`; a partial warehouse is not a passing load.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-52: Data Warehouse Project, Part 1: Star Schema.

I have completed the direct catalog prerequisite: `sql-51`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day52_project3_dwh_part1.md
- Answer-free learner SQL: sql/postgres-60day/day52_project3_dwh_part1.sql

Key terms to teach in context: Fact table, Dimension, Surrogate key. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Write the grain beside every table before loading it. Load `dim_date` and the customer/product dimensions, then map each source order item to exactly one date, customer, and product key in `fact_sales`. Compare fact row count with source `order_items` and check every key resolves once before committing Day 52.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-52/ working copy. Never point setup, reset, DDL, or DML
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
