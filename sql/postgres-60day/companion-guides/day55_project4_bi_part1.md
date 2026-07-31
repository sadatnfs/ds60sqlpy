# Day 55 — Complex BI Project, Part 1: Drill-downs

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 54 — warehouse aggregates](day54_project3_dwh_part3_aggregations.md)
- **Artifacts:** [learner SQL](../day55_project4_bi_part1.sql) ·
  [solution reasoning](../solutions/day55_solutions.md) ·
  [executable solution](../solutions/day55_solutions.sql)

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

2. Open **SQL-55 — Project4 BI Part1** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-55/day55_project4_bi_part1.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day55_project4_bi_part1.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day55_project4_bi_part1.sql
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
ROLLUP, CUBE, GROUPING flag. Its worked SQL reads or creates `payments`, `orders`, `customers`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Compare ROLLUP(country, category) with CUBE(country, category). Both include detail, country subtotal, and grand total; CUBE also adds category-only subtotals. Use GROUPING(country) and GROUPING(category) to label each level, then reconcile the grand total with source line revenue.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day55_project4_bi_part1.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH payment_by_method AS (
  SELECT order_id, method, SUM(amount) AS method_amount
  FROM payments
  GROUP BY order_id, method
), primary_payment_method AS (
  SELECT order_id, method
  FROM (
    SELECT order_id,
           method,
           ROW_NUMBER() OVER (
             PARTITION BY order_id
             ORDER BY method_amount DESC, method
           ) AS method_rank
    FROM payment_by_method
  ) ranked_methods
  WHERE method_rank = 1
), line AS (
  SELECT c.country,
         p.category,
         COALESCE(pm.method, 'unpaid') AS payment_method,
         date_trunc('month', o.order_date)::date AS month,
         (oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue,
         oi.quantity AS qty
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  LEFT JOIN primary_payment_method pm ON pm.order_id = o.order_id
)
SELECT country,
       category,
       payment_method,
       month,
       ROUND(SUM(revenue),2) AS revenue,
       SUM(qty) AS units,
       GROUPING(country)        AS g_country,
       GROUPING(category)       AS g_category,
       GROUPING(payment_method) AS g_method,
       GROUPING(month)          AS g_month
FROM line
GROUP BY ROLLUP (country, category, payment_method, month)
ORDER BY country NULLS FIRST, category NULLS FIRST, payment_method NULLS FIRST, month NULLS FIRST;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
WITH prod_rev AS (
  SELECT c.country, p.category, p.product_id, p.name,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  GROUP BY c.country, p.category, p.product_id, p.name
), ranked AS (
  SELECT *,
         RANK() OVER (PARTITION BY country, category ORDER BY revenue DESC) AS rnk
  FROM prod_rev
)
SELECT * FROM ranked WHERE rnk <= 5
ORDER BY country, category, rnk;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Generate hierarchical subtotal levels with `ROLLUP` and distinguish them from
  all-combination `CUBE` output.
- Rank deterministic top products within several dimensions.

## Vocabulary and concepts

- **ROLLUP:** hierarchical grouping sets from detail through grand total.
- **CUBE:** every grouping-key subset for the supplied dimensions.
- **GROUPING flag:** an indicator separating generated subtotal `NULL`s from
  data `NULL`s.

## Worked example / walkthrough

Compare `ROLLUP(country, category)` with `CUBE(country, category)`. Both include
detail, country subtotal, and grand total; `CUBE` also adds category-only
subtotals. Use `GROUPING(country)` and `GROUPING(category)` to label each level,
then reconcile the grand total with source line revenue.

## Exercises

Complete these in the [learner SQL](../day55_project4_bi_part1.sql):

1. Replace `ROLLUP` with `CUBE` and compare row counts.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
2. Add status to an exact top-five drill-down.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Predict `ROLLUP(country, category, month)` grouping sets.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Label levels with PostgreSQL's `GROUPING(country, category)` bit mask.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Use deterministic `ROW_NUMBER` for exactly five results.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Separate real unknown members from generated subtotals.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Test one real NULL/unknown dimension value.

## Self-check

- Is payment method reduced to one declared row per order before joining lines?
- Does top-five ranking partition by every requested dimension and break ties
  deterministically?

## Next step

Continue to [Day 56 — percentiles and CUBE](day56_project4_bi_part2.md).

## Deep dive and reference

## Project focus

- Generate hierarchical subtotals with `ROLLUP`.
- Compare hierarchical subtotal rows with all-combination `CUBE`.
- Rank top products within country, category, and order status.

## How the learner script uses the current schema

The starter builds line revenue from `orders`, `customers`, `order_items`, and
`products`, chooses one primary payment method per order by greatest paid
amount (method name breaks ties), and rolls up country, category, payment
method, and month. Unpaid orders receive the `unpaid` label.
`GROUPING(column)` distinguishes subtotal nulls from detail values.

It separately ranks product revenue within `(country, category)`.

## Practice — match the learner prompts exactly

1. Replace a two-dimension `ROLLUP(country, category)` with
   `CUBE(country, category)` and compare row counts. Explain the category-only
   subtotal added by `CUBE`.
2. Add `orders.status`, aggregate product revenue at
   `(country, category, status, product_id)`, and return the top five products
   within every such group.

## BI reasoning

- `ROLLUP(a, b)` returns `(a,b)`, `(a)`, and grand total.
- `CUBE(a, b)` also returns the `(b)` subtotal.
- Use `GROUPING` flags when real dimension nulls are possible.
- Aggregate revenue before ranking; use `ROW_NUMBER` plus `product_id` for
  exactly five deterministic results.

## Validation and limits

- A raw payment join fans out split-payment orders. Keep the declared primary
  method policy—or document a different allocation—before using that dimension.
- Cube row counts grow rapidly with dimensions and distinct values.
- Reconcile grand-total cube revenue to source line revenue.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-55 — Project4 BI Part1.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day55_project4_bi_part1.md
- Answer-free learner SQL: sql/postgres-60day/day55_project4_bi_part1.sql

The lesson concepts include ROLLUP, CUBE, GROUPING flag. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Compare ROLLUP(country, category) with CUBE(country, category). Both include detail, country subtotal, and grand total; CUBE also adds category-only subtotals. Use GROUPING(country) and GROUPING(category) to label each level, then reconcile the grand total with source line revenue.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-55/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
