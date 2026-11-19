# Day 16: Window Functions Fundamentals: OVER, PARTITION BY, ORDER BY, Frames (Companion Guide)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-16**. The
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
   `.learning/sql/sql-16/lesson/workspace/sql/postgres-60day/day16_window_functions_fundamentals.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-16
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Intermediate
- **Direct prerequisite:** [SQL-FOUND-01; Relational design, DDL, and integrity
  constraints](../../professional/companion-guides/sql_found_01_relational_design.md).
  That module follows [Day 15; Phase 1 project](day15_phase1_project.md), so
  you should already be comfortable with grouped aggregates and declared
  result grain.
- **Artifacts:** [learner SQL](../day16_window_functions_fundamentals.sql) ·
  [solution reasoning](../solutions/day16_solutions.md) ·
  [executable solution](../solutions/day16_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Window, Partition, Frame. Its worked SQL reads or creates `order_items`, `products`, `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Pre-aggregate net revenue to one row per category, then calculate `SUM(revenue) OVER ()` beside each category. The ordinary aggregate establishes the category grain; the window exposes the grand total without removing those category rows.
Exercise 1 expects this result: one row per order. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day16_window_functions_fundamentals.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
WITH category_totals AS (
  SELECT
    p.category,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    order_items oi
    JOIN products p ON p.product_id = oi.product_id
  GROUP BY
    p.category
)
SELECT
  category,
  ROUND(revenue, 2) AS category_revenue,
  ROUND(SUM(revenue) OVER (), 2) AS total_revenue,
  ROUND(revenue / NULLIF (SUM(revenue) OVER (), 0), 4) AS category_share
FROM
  category_totals
ORDER BY
  category_revenue DESC,
  category;
```

**How to read it:** Example 1: Start with `order_items`, and `products` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `category`, `category_revenue`, `total_revenue`, and `category_share`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `category` with columns `category`, `category_revenue`, `total_revenue`, and `category_share` from `order_items`, and `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT
  o.order_id,
  o.customer_id,
  o.order_date,
  o.total_amount,
  ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id), 2) AS avg_customer_order,
  COUNT(*) OVER (PARTITION BY o.customer_id) AS orders_per_customer
FROM
  orders o
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id
LIMIT 100;
```

**How to read it:** Example 2: Start with `orders` in `FROM`/`JOIN`; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `order_id`, `customer_id`, `order_date`, `total_amount`, `avg_customer_order`, and `orders_per_customer`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns exactly one summary row, capped at 100 rows with columns `order_id`, `customer_id`, `order_date`, `total_amount`, `avg_customer_order`, and `orders_per_customer` from `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Add partition-level and running metrics without collapsing detail rows.
- Choose an explicit `ROWS` frame when peer-aware `RANGE` behavior is not
  intended.

## Vocabulary and concepts

- **Window:** the related rows visible to a window function for one result row.
- **Partition:** an independent window group created by `PARTITION BY`.
- **Frame:** the ordered subset of a partition used for the current row.

## Worked example / walkthrough

Pre-aggregate net revenue to one row per category, then calculate
`SUM(revenue) OVER ()` beside each category. The ordinary aggregate establishes
the category grain; the window exposes the grand total without removing those
category rows.

## Practice assumptions and review method

- **Focus:** Use window functions to add partition-level context while preserving row grain, with explicit partition and ordering semantics.
- **Assumptions:** Window aggregates do not collapse rows. When order matters, use a unique tie-breaker and declare the frame in later cumulative lessons.
- **Failure to watch for:** Filtering a window result in the same query level is invalid; compute it in a subquery or CTE first.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use window functions to add partition-level context while preserving row grain, with explicit partition and ordering semantics.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Show each order with the customer's average order total.
   **Progressive hint:** Partition by customer ID and keep one output row per order.
   **Inputs/evidence:** For sql-16 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `customer_average`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-16 Exercise 1, expected output: One row per order. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_average`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-16 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `total_amount`, and `customer_average`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
2. **Query writing:** Show each employee salary with department average, minimum, and maximum.
   **Progressive hint:** Partition all three window aggregates by department.
   **Inputs/evidence:** For sql-16 Exercise 2, read from `employees`. Build the answer toward `employee_id`, `department_id`, `salary`, `department_average`, `department_minimum`, and `department_maximum`; keep `employee_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-16 Exercise 2, expected output: One row per employee. The final columns are `employee_id`, `department_id`, `salary`, `department_average`, `department_minimum`, and `department_maximum`. The final order is `e.department_id, e.employee_id`.
   **Verify:** For sql-16 Exercise 2, choose one complete partition from `employees`; hand-calculate its first, middle, and final window values for `department_average`, then verify output keys remain `employee_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
3. **Query writing:** Calculate every order's share of its customer's stored revenue.
   **Progressive hint:** Use a partition total denominator and guard it with `NULLIF`.
   **Inputs/evidence:** For sql-16 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `customer_revenue_share`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-16 Exercise 3, expected output: One row per order with shares summing near one per customer. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_revenue_share`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-16 Exercise 3, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `total_amount`, and `customer_revenue_share`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
4. **Prediction:** Compare `GROUP BY customer_id` with `AVG(...) OVER (PARTITION BY customer_id)` and report their row counts.
   **Progressive hint:** Grouping collapses to one row per customer; a window preserves every order row.
   **Inputs/evidence:** For sql-16 Exercise 4, compare a `grouped` CTE (`AVG(o.total_amount) ... GROUP BY o.customer_id`) with a `windowed` CTE (`AVG(o.total_amount) OVER (PARTITION BY o.customer_id)`) over `orders`, then count the rows of each.
   **Expected result/shape:** For sql-16 Exercise 4, expected output: two rows ordered by `method`, with columns `method` and `row_count`: `('grouped', 438)` and `('windowed', 4362)` on the course seed.
   **Verify:** For sql-16 Exercise 4, confirm that the `grouped` count equals `SELECT COUNT(DISTINCT customer_id) FROM orders` and the `windowed` count equals `SELECT COUNT(*) FROM orders`; grouping keeps one row per ordering customer, while the window keeps every order row.
5. **Debugging:** Return orders above their customer average without placing a window function in `WHERE`.
   **Progressive hint:** Compute the window value in a CTE, then filter the named column outside.
   **Inputs/evidence:** For sql-16 Exercise 5, compute `AVG(o.total_amount) OVER (PARTITION BY o.customer_id)` as `customer_average` in a `scored` CTE over `orders`, then filter `total_amount > customer_average` in the outer query.
   **Expected result/shape:** For sql-16 Exercise 5, expected output: one row per `order_id` whose `total_amount` is strictly above its customer's mean (2,249 rows on the course seed), with columns `order_id`, `customer_id`, `total_amount`, and `customer_average` (rounded to 2 places), ordered by `customer_id, total_amount DESC, order_id`.
   **Verify:** For sql-16 Exercise 5, compare the row count with `SELECT COUNT(*) FROM orders o WHERE o.total_amount > (SELECT AVG(i.total_amount) FROM orders i WHERE i.customer_id = o.customer_id)` (2,249), require unique `order_id`, and confirm that moving the window expression into `WHERE` fails with `window functions are not allowed in WHERE`.
6. **Extension:** Show order count and revenue context at both customer and country levels in the same row.
   **Progressive hint:** Use different partitions for independent analytical contexts.
   **Inputs/evidence:** For sql-16 Exercise 6, read from `orders`, and `customers`. Build the answer toward `order_id`, `customer_id`, `country`, `customer_order_count`, `customer_revenue`, and `country_revenue`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-16 Exercise 6, expected output: One row per order with customer and country totals. The final columns are `order_id`, `customer_id`, `country`, `customer_order_count`, `customer_revenue`, and `country_revenue`. The final order is `c.country, o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-16 Exercise 6, choose one complete partition from `orders`, and `customers`; hand-calculate its first, middle, and final window values for `customer_order_count`, `customer_revenue`, and `country_revenue`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Filtering a window result in the same query level is invalid; compute it in a subquery or CTE first.
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

- Does the result retain the intended number of detail rows?
- Can you state the partition, ordering, and frame for every window expression?

## Next step

Continue to [Day 17; ranking functions](day17_rank_functions.md).

## Deep dive and reference

Learning objectives
- Understand what a window is and how window functions differ from aggregates
- Use OVER() with PARTITION BY and ORDER BY to compute per-row metrics without collapsing rows
- Control frames with ROWS/RANGE; grasp default frames and their impact
- Combine multiple window functions in the same SELECT

Why this matters
Window functions unlock powerful analytics: running totals, per-customer averages alongside each row, shares of totals, and rank-based features, all without subqueries that collapse results.

Core concepts and deep dive
- Window vs aggregate
  - Aggregates (SUM, AVG, COUNT) collapse groups into a single row.
  - Window functions compute values across a set of rows related to the current row, but keep one row per input row.
- OVER() clause
  - PARTITION BY defines independent windows (e.g., per customer or per category).
  - ORDER BY defines an order within each partition enabling running/lagged calculations.
  - You can define named windows via WINDOW w AS (PARTITION BY ... ORDER BY ...).
- Default frame
  - If you specify ORDER BY without an explicit frame, the default is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW.
  - RANGE groups peers with equal ORDER BY values; SUM(RANGE ...) may include more rows than expected when there are ties.
  - Prefer ROWS BETWEEN ... for precise row-count frames: ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW for cumulative sums, or ROWS BETWEEN 6 PRECEDING AND CURRENT ROW for 7-row rolling.
- Mixing GROUP BY and window functions
  - You may compute aggregates in a subquery/CTE then apply window functions to the aggregated rows, or vice versa. Know which level is appropriate for your metric.

Walkthrough of the day’s script
- Category share of total revenue: a CTE first produces one row per category,
  then `SUM(revenue) OVER ()` exposes the grand total without collapsing those
  category rows.
- Customer-level windows: AVG(total_amount) OVER (PARTITION BY customer_id) and COUNT(*) OVER (PARTITION BY customer_id) produce lifetime averages and counts joined to each order without GROUP BY.
- Rolling window: `SUM(revenue) OVER (ORDER BY d_utc ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` totals the current and six previous observed dates; dates without orders are skipped. For seven calendar days use `RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW` or a date spine.

Patterns to master
- Running total: SUM(x) OVER (PARTITION BY k ORDER BY t ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
- Percent of partition: x / NULLIF(SUM(x) OVER (PARTITION BY k),0)
- Windowed average/stddev for anomaly detection

Pitfalls
- Mixing RANGE with non-unique ORDER BY can include ties; use ROWS for exact counts.
- Window functions run after WHERE but before ORDER BY LIMIT at the outermost level; to filter on a windowed value, wrap in a subquery.
- Performance: Heavy windows over millions of rows may spill; ensure indexes on partition/order keys.

Further reading
- Postgres windows: https://www.postgresql.org/docs/17/tutorial-window.html
- Frames: https://www.postgresql.org/docs/17/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-16: Window Function Fundamentals: OVER, PARTITION BY, and Frames.

I have completed the direct catalog prerequisite: `sql-found-01`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day16_window_functions_fundamentals.md
- Answer-free learner SQL: sql/postgres-60day/day16_window_functions_fundamentals.sql

Key terms to teach in context: Window, Partition, Frame. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Pre-aggregate net revenue to one row per category, then calculate `SUM(revenue) OVER ()` beside each category. The ordinary aggregate establishes the category grain; the window exposes the grand total without removing those category rows.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-16/ working copy. Never point setup, reset, DDL, or DML
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
