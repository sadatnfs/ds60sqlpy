# Day 16 — Window Functions Fundamentals: OVER, PARTITION BY, ORDER BY, Frames (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Direct prerequisite:** [SQL-FOUND-01 — Relational design, DDL, and integrity
  constraints](../../professional/companion-guides/sql_found_01_relational_design.md).
  That module follows [Day 15 — Phase 1 project](day15_phase1_project.md), so
  you should already be comfortable with grouped aggregates and declared
  result grain.
- **Artifacts:** [learner SQL](../day16_window_functions_fundamentals.sql) ·
  [solution reasoning](../solutions/day16_solutions.md) ·
  [executable solution](../solutions/day16_solutions.sql)

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

2. Open **SQL-16 — Window Functions Fundamentals** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-16/lesson/workspace/sql/postgres-60day/day16_window_functions_fundamentals.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day16_window_functions_fundamentals.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day16_window_functions_fundamentals.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Window, Partition, Frame. Its worked SQL reads or creates `order_items`, `products`, `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Pre-aggregate net revenue to one row per category, then calculate SUM(revenue) OVER () beside each category. The ordinary aggregate establishes the category grain; the window exposes the grand total without removing those category rows.
The expected contract is that One row per order. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day16_window_functions_fundamentals.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH category_totals AS (
  SELECT p.category,
         SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM order_items oi
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category
)
SELECT category,
       ROUND(revenue, 2) AS category_revenue,
       ROUND(SUM(revenue) OVER (), 2) AS total_revenue,
       ROUND(revenue / NULLIF(SUM(revenue) OVER (), 0), 4) AS category_share
FROM category_totals
ORDER BY category_revenue DESC, category;
```

**How to read it:** Example 1: Start with `order_items`, and `products` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `category`, `category_revenue`, `total_revenue`, and `category_share`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `category` with columns `category`, `category_revenue`, `total_revenue`, and `category_share` from `order_items`, and `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       o.total_amount,
       ROUND(AVG(o.total_amount) OVER (PARTITION BY o.customer_id),2) AS avg_customer_order,
       COUNT(*) OVER (PARTITION BY o.customer_id) AS orders_per_customer
FROM orders o
ORDER BY o.customer_id, o.order_date, o.order_id
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
   **Inputs/evidence:** For sql-16 Exercise 4, read from `orders`. Build the answer toward `method`, and `row_count`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-16 Exercise 4, expected output: Two labeled count rows. The final columns are `method`, and `row_count`. The final order is `method`.
   **Verify:** For sql-16 Exercise 4, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `method`, and `row_count` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
5. **Debugging:** Return orders above their customer average without placing a window function in `WHERE`.
   **Progressive hint:** Compute the window value in a CTE, then filter the named column outside.
   **Inputs/evidence:** For sql-16 Exercise 5, read from `orders`. Build the answer toward `order_id`, `customer_id`, `total_amount`, and `customer_average`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-16 Exercise 5, expected output: Order rows above their customer mean. The final columns are `order_id`, `customer_id`, `total_amount`, and `customer_average`. The final order is `customer_id, total_amount DESC, order_id`.
   **Verify:** For sql-16 Exercise 5, run an anti-check that counts rows where NOT ((total_amount > customer_average)); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `total_amount`, and `customer_average` against `orders`. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
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

Continue to [Day 17 — ranking functions](day17_rank_functions.md).

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
- Rolling window: SUM(revenue) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) computes a 7-day moving total. Note the explicit ROWS frame to avoid RANGE pitfalls.

Patterns to master
- Running total: SUM(x) OVER (PARTITION BY k ORDER BY t ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
- Percent of partition: x / NULLIF(SUM(x) OVER (PARTITION BY k),0)
- Windowed average/stddev for anomaly detection

Pitfalls
- Mixing RANGE with non-unique ORDER BY can include ties; use ROWS for exact counts.
- Window functions run after WHERE but before ORDER BY LIMIT at the outermost level; to filter on a windowed value, wrap in a subquery.
- Performance: Heavy windows over millions of rows may spill; ensure indexes on partition/order keys.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Postgres windows: https://www.postgresql.org/docs/current/tutorial-window.html
- Frames: https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-16 — Window Functions Fundamentals.

I have completed the direct catalog prerequisite: `sql-found-01`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day16_window_functions_fundamentals.md
- Answer-free learner SQL: sql/postgres-60day/day16_window_functions_fundamentals.sql

Key terms to teach in context: Window, Partition, Frame. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Pre-aggregate net revenue to one row per category, then calculate SUM(revenue) OVER () beside each category. The ordinary aggregate establishes the category grain; the window exposes the grand total without removing those category rows.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
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
