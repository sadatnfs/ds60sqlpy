# Day 56 — Complex BI Project, Part 2: Percentiles and CUBE

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 55 — BI drill-downs](day55_project4_bi_part1.md)
- **Artifacts:** [learner SQL](../day56_project4_bi_part2.sql) ·
  [solution reasoning](../solutions/day56_solutions.md) ·
  [executable solution](../solutions/day56_solutions.sql)

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

2. Open **SQL-56 — Project4 BI Part2** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-56/day56_project4_bi_part2.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day56_project4_bi_part2.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day56_project4_bi_part2.sql
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
Dimensional explosion, Primary payment method, Continuous percentile. Its worked SQL reads or creates `orders`, `customers`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Aggregate payments at (orderid, method), select one method by greatest total with a stable tie-breaker, and only then join line revenue. Separately aggregate line value at (month, category, orderid) before computing p50/p90; whole order totals would repeat across categories.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day56_project4_bi_part2.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH orders_m AS (
  SELECT c.country,
         date_trunc('month', o.order_date)::date AS month,
         o.total_amount AS amt
  FROM orders o
  JOIN customers c ON c.customer_id = o.customer_id
)
SELECT country,
       month,
       PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY amt) AS p50,
       PERCENTILE_CONT(0.9)  WITHIN GROUP (ORDER BY amt) AS p90,
       PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM orders_m
GROUP BY country, month
ORDER BY month DESC, country
LIMIT 200;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
WITH prod_rev AS (
  SELECT c.country,
         p.category,
         p.product_id,
         p.name,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN customers c  ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p   ON p.product_id = oi.product_id
  GROUP BY c.country, p.category, p.product_id, p.name
), ranked AS (
  SELECT *, RANK() OVER (PARTITION BY country ORDER BY revenue DESC) AS rnk_country,
            RANK() OVER (PARTITION BY country, category ORDER BY revenue DESC) AS rnk_in_cat
  FROM prod_rev
)
SELECT * FROM ranked
WHERE rnk_in_cat <= 5
ORDER BY country, category, rnk_in_cat;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Control order, payment, and line grain before multidimensional aggregation.
- Calculate percentiles over category-attributable order values.

## Vocabulary and concepts

- **Dimensional explosion:** rapid subtotal-row growth as a cube gains
  dimensions.
- **Primary payment method:** a reporting policy selecting one method per order.
- **Continuous percentile:** an interpolated ordered-set statistic from
  `PERCENTILE_CONT`.

## Worked example / walkthrough

Aggregate payments at `(order_id, method)`, select one method by greatest total
with a stable tie-breaker, and only then join line revenue. Separately aggregate
line value at `(month, category, order_id)` before computing p50/p90; whole
order totals would repeat across categories.

## Exercises

Complete these in the [learner SQL](../day56_project4_bi_part2.sql):

1. Add payment method to the cube and compare row counts.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
2. Calculate category-month order-value P50/P90.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Predict raw payment/item join fanout.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Pre-aggregate payment methods and reconcile line revenue.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Repair line-grain percentiles when the metric is order value.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. Compare continuous and discrete percentiles for an even population.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.

Retain cube and percentile observation counts.

## Self-check

- Does the cube grand total reconcile to source line revenue?
- Is the payment-method choice labeled as policy rather than an intrinsic order
  attribute?

## Next step

Continue to [Day 57 — trends and anomalies](day57_project4_bi_part3.md).

## Deep dive and reference

## Project focus

- Measure the dimensional growth caused by adding payment method to a cube.
- Calculate category-month p50 and p90 order-value distributions.
- Control join grain before multidimensional aggregation.

## How the learner script uses the current schema

The starter calculates order-value percentiles by `(country, month)`, ranks
products within country/category, and cubes line revenue across country and
category.

Orders can have multiple payment rows. For the exercise, the reference policy
defines one primary method per order as the method with the greatest total paid
amount, breaking ties by method name. Unpaid orders receive an `unpaid` label.

## Practice — match the learner prompts exactly

1. Add primary payment method to `CUBE(country, category)` and compare the
   two-dimension and three-dimension row counts.
2. At `(month, category, order_id)` grain, sum the net line value attributable
   to the category, then calculate category-month p50 and p90.

## BI and percentile reasoning

- Aggregate payments by `(order_id, method)` before choosing the greatest
  method; otherwise split rows can produce an arbitrary label.
- Reduce to one payment-method row before joining order items to prevent revenue
  multiplication.
- `PERCENTILE_CONT` interpolates and should be accompanied by observation count
  in a production report.
- Cast its result to numeric before two-argument `ROUND`.

## Validation and limits

- Three-dimensional cube row count should exceed the two-dimensional count on
  this seed.
- Reconcile cube grand-total revenue to source line revenue.
- Primary payment method is a declared reporting policy, not an intrinsic order
  attribute.
- Avoid repeating whole order totals once for every category.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-56 — Project4 BI Part2.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day56_project4_bi_part2.md
- Answer-free learner SQL: sql/postgres-60day/day56_project4_bi_part2.sql

The lesson concepts include Dimensional explosion, Primary payment method, Continuous percentile. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate payments at (orderid, method), select one method by greatest total with a stable tie-breaker, and only then join line revenue. Separately aggregate line value at (month, category, orderid) before computing p50/p90; whole order totals would repeat across categories.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-56/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
