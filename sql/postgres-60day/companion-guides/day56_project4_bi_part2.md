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
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-56/lesson/workspace/sql/postgres-60day/day56_project4_bi_part2.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. The key vocabulary for this lesson is Dimensional explosion, Primary payment method, Continuous percentile. Its worked SQL reads or creates `orders`, `customers`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Aggregate payments at (orderid, method), select one method by greatest total with a stable tie-breaker, and only then join line revenue. Separately aggregate line value at (month, category, orderid) before computing p50/p90; whole order totals would repeat across categories.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `country`, and `month`, capped at 200 rows with columns `country`, `month`, `amt`, `p50`, `p90`, and `p99` from `orders`, and `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `country`, `month`, `p50`, `p90`, and `p99`. Independently group `orders`, `customers`, and `orders_m` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

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

**How to read it:** Example 1: Start with `orders`, and `customers` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `country`, `month`, `p50`, `p90`, and `p99`. `ORDER BY` determines presentation order and the final `LIMIT 200` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `country`, and `month`, capped at 200 rows with columns `country`, `month`, `amt`, `p50`, `p90`, and `p99` from `orders`, and `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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

**How to read it:** Example 2: Start with `orders`, `customers`, `order_items`, and `products` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `*`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `country`, `category`, and `product_id` with columns `country`, `category`, `product_id`, `name`, `revenue`, and `rnk_country` from `orders`, `customers`, `order_items`, and `products`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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
   **Inputs/evidence:** For sql-56 Exercise 1, read from `payments`, `orders`, `customers`, `order_items`, and `products`. Compute `two_dimension_rows`, and `three_dimension_rows` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-56 Exercise 1, expected output: one row; `three_dimension_rows` should be larger. The final columns are `two_dimension_rows`, and `three_dimension_rows`.
   **Verify:** For sql-56 Exercise 1, evaluate each of `two_dimension_rows`, and `three_dimension_rows` in a separate control `SELECT` over `payments`, `orders`, `customers`, `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.
2. Calculate category-month order-value P50/P90.
   **Inputs/evidence:** For sql-56 Exercise 2, read from `orders`, `order_items`, and `products`. Build the answer toward `month`, `category`, `p50_order_value`, and `p90_order_value`; keep `month`, and `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-56 Exercise 2, expected output: one row per represented `(month, category)`. The final columns are `month`, `category`, `p50_order_value`, and `p90_order_value`. The final order is `month DESC, category`.
   **Verify:** For sql-56 Exercise 2, independently aggregate `orders`, `order_items`, and `products` by `month`, and `category`; require one output row for every distinct `month`, and `category` tuple and compare `p50_order_value`, and `p90_order_value` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `p50_order_value`, and `p90_order_value` for the existing `month`, and `category` tuple and verify the new tuple appears exactly once.
3. Predict raw payment/item join fanout.
   **Inputs/evidence:** For sql-56 Exercise 3, read from `orders`, `order_items`, and `payments`. Build the answer toward `raw_join_rows`, `distinct_items`, and `distinct_payments`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-56 Exercise 3, expected output: one row per `order_id`. The final columns are `raw_join_rows`, `distinct_items`, and `distinct_payments`.
   **Verify:** For sql-56 Exercise 3, project `order_id` plus the raw source columns from `orders`, `order_items`, and `payments` at each join stage; record row count and distinct `order_id`, then assert the final `raw_join_rows`, `distinct_items`, and `distinct_payments` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
4. Pre-aggregate payment methods and reconcile line revenue.
   **Inputs/evidence:** For sql-56 Exercise 4, read from `payments`, and `order_items`. Build the answer toward `reporting_method`, `revenue`, and `reconciled_total`; keep `payment_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-56 Exercise 4, expected output: one row per `payment_id`. The final columns are `reporting_method`, `revenue`, and `reconciled_total`. The final order is `reporting_method`.
   **Verify:** For sql-56 Exercise 4, choose one complete partition from `payments`, and `order_items`; hand-calculate its first, middle, and final window values for `revenue`, and `reconciled_total`, then verify output keys remain `payment_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
5. Repair line-grain percentiles when the metric is order value.
   **Inputs/evidence:** For sql-56 Exercise 5, read from `orders`, `order_items`, and `products`. Build the answer toward `category`, `observations`, and `p50`; keep `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-56 Exercise 5, expected output: one row per `category`. The final columns are `category`, `observations`, and `p50`. The final order is `category`.
   **Verify:** For sql-56 Exercise 5, independently aggregate `orders`, `order_items`, and `products` by `category`; require one output row for every distinct `category` tuple and compare `p50` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `p50` for the existing `category` tuple and verify the new tuple appears exactly once.
6. Compare continuous and discrete percentiles for an even population.
   **Inputs/evidence:** For sql-56 Exercise 6, read from `orders`, `order_items`, and `products`. Build the answer toward `category`, `observations`, `continuous_p50`, and `discrete_p50`; keep `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-56 Exercise 6, expected output: one row per `category`. The final columns are `category`, `observations`, `continuous_p50`, and `discrete_p50`. The final order is `category`.
   **Verify:** For sql-56 Exercise 6, independently aggregate `orders`, `order_items`, and `products` by `category`; require one output row for every distinct `category` tuple and compare `continuous_p50`, and `discrete_p50` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `continuous_p50`, and `discrete_p50` for the existing `category` tuple and verify the new tuple appears exactly once.

Retain cube and percentile observation counts.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Three-dimensional cube row count should exceed the two-dimensional count on
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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

I have completed the direct catalog prerequisite: `sql-55`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day56_project4_bi_part2.md
- Answer-free learner SQL: sql/postgres-60day/day56_project4_bi_part2.sql

Key terms to teach in context: Dimensional explosion, Primary payment method, Continuous percentile. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate payments at (orderid, method), select one method by greatest total with a stable tie-breaker, and only then join line revenue. Separately aggregate line value at (month, category, orderid) before computing p50/p90; whole order totals would repeat across categories.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-56/ working copy. Never point setup, reset, DDL, or DML
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
