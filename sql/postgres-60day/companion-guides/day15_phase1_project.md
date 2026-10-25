# Day 15: Phase 1 Project: Multi-Dimensional Revenue Report (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 14; numeric types and casting](day14_numeric_and_casting.md)
  and the complete Day 01–14 foundation sequence
- **Artifacts:** [learner SQL](../day15_phase1_project.sql) ·
  [solution reasoning](../solutions/day15_solutions.md) ·
  [executable solution](../solutions/day15_solutions.sql)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-15**. The
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
   `.learning/sql/sql-15/lesson/workspace/sql/postgres-60day/day15_phase1_project.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-15
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
on screen are not automatically stored. The key vocabulary for this lesson is Metric contract, Dimensional report, Control total. Its worked SQL reads or creates `orders`, `order_items`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Build one stable orderlines relation first, with one row per intended line or order and a single net-revenue formula. Reconcile its total, then add dimension joins one at a time and compare the total after each join. Only after totals remain stable should you add grouping sets and display labels.
The expected contract is that One row per customer. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day15_phase1_project.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH line AS (
  SELECT o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
           AS month_utc,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
),
segment AS (
  SELECT c.customer_id, COALESCE(c.segment,'standard') AS segment, c.country
  FROM customers c
)
SELECT s.segment, s.country, l.month_utc,
       ROUND(SUM(l.revenue),2) AS revenue,
       COUNT(DISTINCT l.customer_id) AS actives,
       ROUND(SUM(l.revenue)/NULLIF(COUNT(DISTINCT l.customer_id),0),2) AS rev_per_active
FROM line l
JOIN segment s ON s.customer_id = l.customer_id
GROUP BY s.segment, s.country, l.month_utc
ORDER BY l.month_utc DESC, revenue DESC, s.segment, s.country
LIMIT 200;
```

**How to read it:** Example 1: Start with `orders`, `order_items`, and `customers` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `segment`, `country`, `month_utc`, `revenue`, `actives`, and `rev_per_active`. `ORDER BY` determines presentation order and the final `LIMIT 200` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `segment`, and `country`, capped at 200 rows with columns `segment`, `country`, `month_utc`, `revenue`, `actives`, and `rev_per_active` from `orders`, `order_items`, and `customers`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (COSTS OFF)
WITH line AS (
  SELECT o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
           AS month_utc,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
),
segment AS (
  SELECT c.customer_id, COALESCE(c.segment,'standard') AS segment, c.country
  FROM customers c
)
SELECT s.segment, s.country, l.month_utc,
       ROUND(SUM(l.revenue),2) AS revenue,
       COUNT(DISTINCT l.customer_id) AS actives,
       ROUND(SUM(l.revenue)/NULLIF(COUNT(DISTINCT l.customer_id),0),2) AS rev_per_active
FROM line l
JOIN segment s ON s.customer_id = l.customer_id
GROUP BY s.segment, s.country, l.month_utc
ORDER BY l.month_utc DESC, revenue DESC, s.segment, s.country
LIMIT 200;
```

**How to read it:** Example 2 is executed by `psql` as part of the complete lesson. Expected notices are evidence; an unexpected error stops the script.

**Expected result/shape:** Example 2 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `segment`, and `country` key set and row count over `orders`, `order_items`, and `customers`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

## Learning objectives

- Design a multi-dimensional revenue report from a written metric contract.
- Reconcile joins, conditional metrics, subtotals, and time calculations before
  presenting the result.

## Vocabulary and concepts

- **Metric contract:** a written definition of grain, formula, filters, and
  exclusions.
- **Dimensional report:** measures grouped by descriptive attributes such as
  country, category, and month.
- **Control total:** an independently calculated value used for reconciliation.

## Worked example / walkthrough

Build one stable `order_lines` relation first, with one row per intended line or
order and a single net-revenue formula. Reconcile its total, then add dimension
joins one at a time and compare the total after each join. Only after totals
remain stable should you add grouping sets and display labels.

## Practice assumptions and review method

- **Focus:** Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.
- **Assumptions:** All monetary summaries identify stored totals versus computed net line revenue. Reporting month uses UTC and empty populations remain visible where required.
- **Failure to watch for:** Combining fact tables before fixing their grain multiplies measures; every project output must state its row grain and acceptance checks.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Create a customer performance table with order count, stored revenue, and latest order date, retaining customers with no orders.
   **Progressive hint:** Left join from customers and aggregate at customer grain.
   **Inputs/evidence:** For sql-15 Exercise 1, read from `customers`, and `orders`. Build the answer toward `customer_id`, `full_name`, `country`, `order_count`, `stored_revenue`, and `latest_order_date`; keep `customer_id`, `full_name`, and `country` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-15 Exercise 1, expected output: One row per customer. The final columns are `customer_id`, `full_name`, `country`, `order_count`, `stored_revenue`, and `latest_order_date`. The final order is `stored_revenue DESC, c.customer_id`.
   **Verify:** For sql-15 Exercise 1, independently aggregate `customers`, and `orders` by `customer_id`, `full_name`, and `country`; require one output row for every distinct `customer_id`, `full_name`, and `country` tuple and compare `order_count`, `stored_revenue`, and `latest_order_date` tuple by tuple. Use one key absent from `orders`; then tie two candidates on `stored_revenue DESC` and verify `c.customer_id` selects the same row on every run.
2. **Query writing:** Create a product profitability table from net order-line revenue and catalog cost.
   **Progressive hint:** Calculate line revenue and line cost at item grain, then aggregate to product.
   **Inputs/evidence:** For sql-15 Exercise 2, read from `products`, and `order_items`. Build the answer toward `product_id`, `name`, `category`, `units_sold`, `net_revenue`, `catalog_cost`, and `gross_profit`; keep `product_id`, `name`, and `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-15 Exercise 2, expected output: One row per sold product. The final columns are `product_id`, `name`, `category`, `units_sold`, `net_revenue`, `catalog_cost`, and `gross_profit`. The final order is `gross_profit DESC, p.product_id`.
   **Verify:** For sql-15 Exercise 2, independently aggregate `products`, and `order_items` by `product_id`, `name`, and `category`; require one output row for every distinct `product_id`, `name`, and `category` tuple and compare `units_sold`, and `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `units_sold`, and `net_revenue` for the existing `product_id`, and `name` tuple and verify the new tuple appears exactly once.
3. **Query writing:** Build a UTC monthly order-status report with counts and stored revenue.
   **Progressive hint:** Derive one reporting month and group by month/status.
   **Inputs/evidence:** For sql-15 Exercise 3, read from `orders`. Build the answer toward `utc_month`, `status`, `order_count`, and `stored_revenue`; keep `status` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-15 Exercise 3, expected output: One row per observed month and status. The final columns are `utc_month`, `status`, `order_count`, and `stored_revenue`. The final order is `utc_month, o.status`.
   **Verify:** For sql-15 Exercise 3, independently aggregate `orders` by `status`; require one output row for every distinct `status` tuple and compare `order_count`, and `stored_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `stored_revenue` for the existing `status` tuple and verify the new tuple appears exactly once.
4. **Debugging:** Reconcile stored order total, computed line total, and paid total without multiplying details.
   **Progressive hint:** Aggregate items and payments independently to order grain before joining.
   **Inputs/evidence:** For sql-15 Exercise 4, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-15 Exercise 4, expected output: One row per order with differences. The final columns are `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance`. The final order is `ABS(o.total_amount - lt.line_total) DESC, o.order_id`.
   **Verify:** For sql-15 Exercise 4, project `order_id` plus the raw source columns from `order_items`, `payments`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
5. **Prediction:** Compare monthly budgets with actual expenses and preserve missing sides.
   **Progressive hint:** Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero.
   **Inputs/evidence:** For sql-15 Exercise 5, read from `expenses`, and `budgets`. Build the answer toward `category`, `period`, `budget_amount`, `actual_amount`, and `variance`; keep `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-15 Exercise 5, expected output: One row per category/month in either source. The final columns are `category`, `period`, `budget_amount`, `actual_amount`, and `variance`. The final order is `period, category`.
   **Verify:** For sql-15 Exercise 5, project `category` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `category`, then assert the final `category`, `period`, `budget_amount`, `actual_amount`, and `variance` values match those staged rows without unintended fanout or loss. Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.
6. **Extension:** Produce one executive summary row with population, activity, stored revenue, computed revenue, and payments.
   **Progressive hint:** Compute independent one-row aggregates, then cross join them to avoid detail multiplication.
   **Inputs/evidence:** For sql-15 Exercise 6, read from `customers`, `orders`, `order_items`, and `payments`. Build the answer toward `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-15 Exercise 6, expected output: Exactly one summary row. The final columns are `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments`.
   **Verify:** For sql-15 Exercise 6, project `customer_id` plus the raw source columns from `customers`, `orders`, `order_items`, and `payments` at each join stage; record row count and distinct `customer_id`, then assert the final `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments` values match those staged rows without unintended fanout or loss. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Combining fact tables before fixing their grain multiplies measures; every project output must state its row grain and acceptance checks.
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

- Does the grand total equal the independent net-line-revenue control?
- Are date window, payment handling, zero-activity entities, and subtotal
  `NULL`s documented?

## Next step

Continue to [Day 16; window-function fundamentals](day16_window_functions_fundamentals.md).

## Deep dive and reference

Goal
- Produce a robust monthly revenue report segmented by customer attributes and product categories using techniques from Days 01–14.

What you’ll build
- Extend the supplied monthly segment-country report while retaining its
  revenue, active-customer, and revenue-per-active metrics.
- Add at least two dimensions. The learner script suggests payment method and
  product category.

Guidance
1) Keep product category at line grain before aggregating; it cannot be
   recovered after all lines have been collapsed to one order total.
2) Pre-aggregate payments to the order-method grain before joining to lines.
3) Aggregate by month, segment, country, and the two chosen dimensions.
4) Validate totals against net line revenue and inspect split-payment orders.
5) Document whether all order statuses are included; the starter query does not
   exclude `placed`, `returned`, or any other status.

Quality checklist
- Correct join cardinality (no double counting)
- Handling of NULL/unknown categories and segments
- Performance: indices on join keys; avoid unnecessary DISTINCT

Current practice map
- The authoritative six prompts above replace the older single deliverable.
  Complete all six outputs and document grain, missing-side behavior, UTC
  boundaries, money definitions, and reconciliation evidence.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-15 — Phase1 Project.

I have completed the direct catalog prerequisite: `sql-14`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day15_phase1_project.md
- Answer-free learner SQL: sql/postgres-60day/day15_phase1_project.sql

Key terms to teach in context: Metric contract, Dimensional report, Control total. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Build one stable orderlines relation first, with one row per intended line or order and a single net-revenue formula. Reconcile its total, then add dimension joins one at a time and compare the total after each join. Only after totals remain stable should you add grouping sets and display labels.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-15/ working copy. Never point setup, reset, DDL, or DML
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
