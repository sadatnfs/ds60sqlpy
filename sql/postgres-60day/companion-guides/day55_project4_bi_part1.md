# Day 55: Complex BI Project, Part 1: Drill-downs

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 54; warehouse aggregates](day54_project3_dwh_part3_aggregations.md)
- **Artifacts:** [learner SQL](../day55_project4_bi_part1.sql) ·
  [solution reasoning](../solutions/day55_solutions.md) ·
  [executable solution](../solutions/day55_solutions.sql)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-55**. The
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
   `.learning/sql/sql-55/lesson/workspace/sql/postgres-60day/day55_project4_bi_part1.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-55
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
on screen are not automatically stored. The key vocabulary for this lesson is ROLLUP, CUBE, GROUPING flag. Its worked SQL reads or creates `payments`, `orders`, `customers`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Compare ROLLUP(country, category) with CUBE(country, category). Both include detail, country subtotal, and grand total; CUBE also adds category-only subtotals. Use GROUPING(country) and GROUPING(category) to label each level, then reconcile the grand total with source line revenue.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `category`, `month`, and `g_country` with columns `category`, `payment_method`, `month`, `revenue`, `qty`, and `units` from `payments`, `orders`, `customers`, `order_items`, and `products`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `country`, `category`, `payment_method`, `month`, `revenue`, `units`, `g_country`, and `g_category`. Independently group `payments`, `payment_by_method`, `orders`, `customers`, and `order_items` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

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

**How to read it:** Example 1: Start with `payments`, `orders`, `customers`, and `order_items` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `country`, `category`, `payment_method`, `month`, `revenue`, `units`, and `g_country`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `category`, `month`, and `g_country` with columns `category`, `payment_method`, `month`, `revenue`, `qty`, and `units` from `payments`, `orders`, `customers`, `order_items`, and `products`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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

**How to read it:** Example 2: Start with `orders`, `customers`, `order_items`, and `products` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `*`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `country`, `category`, and `product_id` with columns `country`, `category`, `product_id`, `name`, `revenue`, and `rnk` from `orders`, `customers`, `order_items`, and `products`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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
   **Inputs/evidence:** For sql-55 Exercise 1, read from `orders`, `customers`, `order_items`, and `products`. Compute `rollup_row_count`, and `cube_row_count` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-55 Exercise 1, expected output: one comparison row. `CUBE(country, category)` adds category-only subtotals that the hierarchical `ROLLUP(country, category)` omits, so its count is greater on this seed. The final columns are `rollup_row_count`, and `cube_row_count`.
   **Verify:** For sql-55 Exercise 1, evaluate each of `rollup_row_count`, and `cube_row_count` in a separate control `SELECT` over `orders`, `customers`, `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
2. Add status to an exact top-five drill-down.
   **Inputs/evidence:** For sql-55 Exercise 2, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `country`, `category`, `status`, `product_id`, `name`, `revenue`, and `product_rank`; keep `product_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-55 Exercise 2, expected output: up to five rows per `(country, category, status)`. The final columns are `country`, `category`, `status`, `product_id`, `name`, `revenue`, and `product_rank`. The final order is `country, category, status, product_rank`.
   **Verify:** For sql-55 Exercise 2, project `product_id` plus the raw source columns from `orders`, `customers`, `order_items`, and `products` at each join stage; record row count and distinct `product_id`, then assert the final `country`, `category`, `status`, `product_id`, `name`, `revenue`, and `product_rank` values match those staged rows without unintended fanout or loss. Give two rows the same `country` value and different `product_rank` values; verify `country, category, status, product_rank` produces the intended rank and display order.
3. Predict `ROLLUP(country, category, month)` grouping sets.
   **Inputs/evidence:** For sql-55 Exercise 3, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `country`, `category`, `revenue`, and `grouping_mask`; keep `country`, and `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-55 Exercise 3, expected output: one row per `country`, and `category`. The final columns are `country`, `category`, `revenue`, and `grouping_mask`. The final order is `grouping_mask, country, category`.
   **Verify:** For sql-55 Exercise 3, independently aggregate `orders`, `customers`, `order_items`, and `products` by `country`, and `category`; require one output row for every distinct `country`, and `category` tuple and compare `revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `country`, and `category` tuple and verify the new tuple appears exactly once.
4. Label levels with PostgreSQL's `GROUPING(country, category)` bit mask.
   **Inputs/evidence:** For sql-55 Exercise 4, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `level_id`, `level_name`, `country`, `category`, and `revenue`; keep `level_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-55 Exercise 4, expected output: one row per `level_id`. The final columns are `level_id`, `level_name`, `country`, `category`, and `revenue`. The final order is `level_id, country, category`.
   **Verify:** For sql-55 Exercise 4, independently aggregate `orders`, `customers`, `order_items`, and `products` by `level_id`; require one output row for every distinct `level_id` tuple and compare `revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `level_id` tuple and verify the new tuple appears exactly once.
5. Use deterministic `ROW_NUMBER` for exactly five results.
   **Inputs/evidence:** For sql-55 Exercise 5, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-55 Exercise 5, expected output: one row per `order_id`. The final columns are `order_id`, `customer_id`, `order_date`, `status`, and `total_amount`. The final order is `country, position`.
   **Verify:** For sql-55 Exercise 5, project `order_id` plus the raw source columns from `orders`, `customers`, `order_items`, and `products` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `customer_id`, `order_date`, `status`, and `total_amount` values match those staged rows without unintended fanout or loss. Add one row for which `(position <= 5)` is true and one for which it is false; verify only the matching `order_id` value is returned.
6. Separate real unknown members from generated subtotals.
   **Inputs/evidence:** For sql-55 Exercise 6, read from `customers`. Build the answer toward `display_country`, `is_generated_total`, and `customers`; keep `display_country` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-55 Exercise 6, expected output: one row per `display_country`. The final columns are `display_country`, `is_generated_total`, and `customers`. The final order is `is_generated_total, display_country`.
   **Verify:** For sql-55 Exercise 6, independently aggregate `customers` by `display_country`; require one output row for every distinct `display_country` tuple and compare `is_generated_total`, and `customers` tuple by tuple. Repeat with `NULL` in `display_country`, and `is_generated_total` and state whether the row is kept, rejected, or classified.

Test one real NULL/unknown dimension value.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** A raw payment join fans out split-payment orders. Keep the declared primary
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

- Is payment method reduced to one declared row per order before joining lines?
- Does top-five ranking partition by every requested dimension and break ties
  deterministically?

## Next step

Continue to [Day 56; percentiles and CUBE](day56_project4_bi_part2.md).

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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## BI reasoning

- `ROLLUP(a, b)` returns `(a,b)`, `(a)`, and grand total.
- `CUBE(a, b)` also returns the `(b)` subtotal.
- Use `GROUPING` flags when real dimension nulls are possible.
- Aggregate revenue before ranking; use `ROW_NUMBER` plus `product_id` for
  exactly five deterministic results.

## Validation and limits

- A raw payment join fans out split-payment orders. Keep the declared primary
  method policy, or document a different allocation, before using that dimension.
- Cube row counts grow rapidly with dimensions and distinct values.
- Reconcile grand-total cube revenue to source line revenue.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-55 — Project4 BI Part1.

I have completed the direct catalog prerequisite: `sql-54`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day55_project4_bi_part1.md
- Answer-free learner SQL: sql/postgres-60day/day55_project4_bi_part1.sql

Key terms to teach in context: ROLLUP, CUBE, GROUPING flag. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Compare ROLLUP(country, category) with CUBE(country, category). Both include detail, country subtotal, and grand total; CUBE also adds category-only subtotals. Use GROUPING(country) and GROUPING(category) to label each level, then reconcile the grand total with source line revenue.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-55/ working copy. Never point setup, reset, DDL, or DML
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
