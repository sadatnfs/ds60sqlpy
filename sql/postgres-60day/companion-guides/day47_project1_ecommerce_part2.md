# Day 47 — E-commerce Project, Part 2: Cohort Retention

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 46 — LTV and cohorts](day46_project1_ecommerce_part1.md)
- **Artifacts:** [learner SQL](../day47_project1_ecommerce_part2.sql) ·
  [solution reasoning](../solutions/day47_solutions.md) ·
  [executable solution](../solutions/day47_solutions.sql)

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

2. Open **SQL-47 — Project1 Ecommerce Part2** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-47/day47_project1_ecommerce_part2.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day47_project1_ecommerce_part2.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day47_project1_ecommerce_part2.sql
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
Cohort size, Active customer, Retention curve. Its worked SQL reads or creates `orders`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Deduplicate activity to (customerid, ordermonth), count active customers per cohort/offset, and join to cohort size calculated from all customers. Cast before division and build a cohort/offset spine when missing periods must appear as explicit zeros.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day47_project1_ecommerce_part2.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH orders_m AS (
  SELECT o.customer_id,
         date_trunc('month', o.order_date)::date AS order_month
  FROM orders o
  GROUP BY o.customer_id, date_trunc('month', o.order_date)
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month
  FROM customers c
), retention AS (
  SELECT co.cohort_month,
         om.order_month,
         (
           EXTRACT(YEAR FROM age(om.order_month, co.cohort_month)) * 12
           + EXTRACT(MONTH FROM age(om.order_month, co.cohort_month))
         )::int AS month_offset,
         COUNT(DISTINCT om.customer_id) AS active_customers
  FROM orders_m om
  JOIN cohorts co ON co.customer_id = om.customer_id
  GROUP BY co.cohort_month, om.order_month
)
SELECT cohort_month, month_offset, active_customers
FROM retention
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month DESC, month_offset;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (COSTS OFF)
WITH orders_m AS (
  SELECT o.customer_id,
         date_trunc('month', o.order_date)::date AS order_month
  FROM orders o
  GROUP BY o.customer_id, date_trunc('month', o.order_date)
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at)::date AS cohort_month
  FROM customers c
), retention AS (
  SELECT co.cohort_month,
         om.order_month,
         (
           EXTRACT(YEAR FROM age(om.order_month, co.cohort_month)) * 12
           + EXTRACT(MONTH FROM age(om.order_month, co.cohort_month))
         )::int AS month_offset,
         COUNT(DISTINCT om.customer_id) AS active_customers
  FROM orders_m om
  JOIN cohorts co ON co.customer_id = om.customer_id
  GROUP BY co.cohort_month, om.order_month
)
SELECT cohort_month, month_offset, active_customers
FROM retention
WHERE month_offset BETWEEN 0 AND 12
ORDER BY cohort_month DESC, month_offset;
```

**How to read it:** Example 2 is executed by `psql` as part of the complete lesson. Expected notices are evidence; an unexpected error stops the script.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Define cohort size independently from later activity.
- Produce a chart-ready retention table with explicit numerator, denominator,
  and lifecycle offset.

## Vocabulary and concepts

- **Cohort size:** all eligible signups in the cohort, including non-purchasers.
- **Active customer:** a distinct customer meeting the declared period rule.
- **Retention curve:** retention rate across lifecycle offsets for one cohort.

## Worked example / walkthrough

Deduplicate activity to `(customer_id, order_month)`, count active customers per
cohort/offset, and join to cohort size calculated from all customers. Cast
before division and build a cohort/offset spine when missing periods must appear
as explicit zeros.

## Exercises

Complete these in the [learner SQL](../day47_project1_ecommerce_part2.sql):

1. Convert active-customer counts to retention rates.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Return the latest six cohort curves in tidy form.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Compare signup-month and first-order-month cohort anchors.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Build a complete cohort/offset spine.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
5. Prevent negative offsets from inconsistent chronology.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Distinguish observed zero retention from future, unobservable offsets.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Retain numerator and denominator beside every rate.

## Self-check

- Is each customer counted once per activity month regardless of order count?
- Are rates bounded by zero and one, with missing rows distinguished from zero?

## Next step

Continue to [Day 48 — affinity and attribution](day48_project1_ecommerce_part3.md).

## Deep dive and reference

## Project focus

- Define signup cohort size.
- Count distinct active customers by lifecycle month.
- Produce six chart-ready retention curves.

## How the learner script uses the current schema

The starter deduplicates `orders` to one row per `(customer_id, order_month)`,
joins each customer to the signup month from `customers.created_at`, and counts
active customers at offsets 0–12.

This lesson is retention only. Funnel analysis belongs to the later
event/capstone work and is not a Day 47 deliverable.

## Practice — match the learner prompts exactly

1. Divide `active_customers` by total signup `cohort_size` to calculate
   `retention_rate`. Return numerator, denominator, and rate.
2. Restrict the tidy result to the six newest cohorts and chart
   `month_offset` on X, `retention_rate` on Y, and `cohort_month` as series.

The chart itself is outside SQL. The SQL deliverable is the narrow,
chart-ready table.

## Grain and denominator

- Cohort size includes every signup in the month, not only later purchasers.
- Multiple orders by the same customer in one month count as one active
  customer.
- Cast before division so PostgreSQL does not perform integer division.
- Combine year and month components when calculating lifecycle offset.

## Validation and limits

- A missing offset row and a present zero-rate row are different. Build a
  cohort-by-offset spine when a complete matrix is required.
- Do not count orders as retained customers.
- Restrict activity to order months on or after signup.
- The synthetic curves are technique demonstrations, not expected business
  retention shapes.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-47 — Project1 Ecommerce Part2.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day47_project1_ecommerce_part2.md
- Answer-free learner SQL: sql/postgres-60day/day47_project1_ecommerce_part2.sql

The lesson concepts include Cohort size, Active customer, Retention curve. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Deduplicate activity to (customerid, ordermonth), count active customers per cohort/offset, and join to cohort size calculated from all customers. Cast before division and build a cohort/offset spine when missing periods must appear as explicit zeros.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-47/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
