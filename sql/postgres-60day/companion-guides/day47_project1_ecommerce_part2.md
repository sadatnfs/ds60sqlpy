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
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-47/lesson/workspace/sql/postgres-60day/day47_project1_ecommerce_part2.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. The key vocabulary for this lesson is Cohort size, Active customer, Retention curve. Its worked SQL reads or creates `orders`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Deduplicate activity to (customerid, ordermonth), count active customers per cohort/offset, and join to cohort size calculated from all customers. Cast before division and build a cohort/offset spine when missing periods must appear as explicit zeros.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `customer_id`, `order_month`, and `cohort_month` with columns `customer_id`, `order_month`, `cohort_month`, `month_offset`, and `active_customers` from `orders`, `customers`, and `age`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `cohort_month`, `month_offset`, and `active_customers`. Independently group `orders`, `customers`, `age`, `orders_m`, and `cohorts` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

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

**How to read it:** Example 1: Start with `orders`, `customers`, and `age` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `cohort_month`, `month_offset`, and `active_customers`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `customer_id`, `order_month`, and `cohort_month` with columns `customer_id`, `order_month`, `cohort_month`, `month_offset`, and `active_customers` from `orders`, `customers`, and `age`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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

**Expected result/shape:** Example 2 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `customer_id`, `order_month`, and `cohort_month` key set and row count over `orders`, `customers`, and `age`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

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
   **Inputs/evidence:** For sql-47 Exercise 1, read from `orders`, `customers`, and `age`. Build the answer toward `cohort_sizes`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-47 Exercise 1, expected output: one row per `order_id`. The final columns are `cohort_sizes`.
   **Verify:** For sql-47 Exercise 1, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `cohort_sizes` against `orders`, `customers`, and `age`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
2. Return the latest six cohort curves in tidy form.
   **Inputs/evidence:** For sql-47 Exercise 2, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`; keep `cohort_month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-47 Exercise 2, expected output: one row per `cohort_month`. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`. The final order is `cohort_month DESC, month_offset`.
   **Verify:** For sql-47 Exercise 2, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate` values match those staged rows without unintended fanout or loss. Tie two rows on `cohort_month DESC` and give them different `month_offset` values; verify `cohort_month DESC, month_offset` chooses a stable first/last row.
3. Compare signup-month and first-order-month cohort anchors.
   **Inputs/evidence:** For sql-47 Exercise 3, read from `customers`, and `orders`. Build the answer toward `customer_id`, `signup_cohort`, and `first_order_cohort`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-47 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`, `signup_cohort`, and `first_order_cohort`. The final order is `c.customer_id`.
   **Verify:** For sql-47 Exercise 3, independently aggregate `customers`, and `orders` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `first_order_cohort` tuple by tuple. Use one key absent from `orders`; then tie two candidates on `c.customer_id` and verify `c.customer_id` selects the same row on every run.
4. Build a complete cohort/offset spine.
   **Inputs/evidence:** For sql-47 Exercise 4, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`; keep `cohort_month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-47 Exercise 4, expected output: one row per `cohort_month`. The final columns are `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`. The final order is `s.cohort_month DESC, x.month_offset`.
   **Verify:** For sql-47 Exercise 4, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, and `active_customers` values match those staged rows without unintended fanout or loss. Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.
5. Prevent negative offsets from inconsistent chronology.
   **Inputs/evidence:** For sql-47 Exercise 5, read from `customers`, and `orders`. Build the answer toward `customer_id`, `created_at`, and `first_order_at`; keep `customer_id`, and `created_at` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-47 Exercise 5, expected output: one row per `customer_id`, and `created_at`. The final columns are `customer_id`, `created_at`, and `first_order_at`. The final order is `c.customer_id`.
   **Verify:** For sql-47 Exercise 5, independently aggregate `customers`, and `orders` by `customer_id`, and `created_at`; require one output row for every distinct `customer_id`, and `created_at` tuple and compare `first_order_at` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `first_order_at` for the existing `customer_id`, and `created_at` tuple and verify the new tuple appears exactly once.
6. Distinguish observed zero retention from future, unobservable offsets.
   **Inputs/evidence:** For sql-47 Exercise 6, read from `orders`, and `sample`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-47 Exercise 6, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`.
   **Verify:** For sql-47 Exercise 6, project `order_id` plus the raw source columns from `orders`, and `sample` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

Retain numerator and denominator beside every rate.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** A missing offset row and a present zero-rate row are different. Build a
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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

I have completed the direct catalog prerequisite: `sql-46`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day47_project1_ecommerce_part2.md
- Answer-free learner SQL: sql/postgres-60day/day47_project1_ecommerce_part2.sql

Key terms to teach in context: Cohort size, Active customer, Retention curve. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Deduplicate activity to (customerid, ordermonth), count active customers per cohort/offset, and join to cohort size calculated from all customers. Cast before division and build a cohort/offset spine when missing periods must appear as explicit zeros.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-47/ working copy. Never point setup, reset, DDL, or DML
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
