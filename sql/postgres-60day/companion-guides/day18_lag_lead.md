# Day 18 — LAG/LEAD and Intra-Row Comparisons (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 17 — ranking functions](day17_rank_functions.md)
- **Artifacts:** [learner SQL](../day18_lag_lead.sql) ·
  [solution reasoning](../solutions/day18_solutions.md) ·
  [executable solution](../solutions/day18_solutions.sql)

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

2. Open **SQL-18 — Lag Lead** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-18/lesson/workspace/sql/postgres-60day/day18_lag_lead.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day18_lag_lead.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day18_lag_lead.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Offset, Default value, Calendar spine. Its worked SQL reads or creates `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: At monthly grain, place revenue beside LAG(revenue) OVER (ORDER BY month). The first row has no predecessor and returns NULL. If a month is absent, the previous row is not necessarily the previous calendar month, so build a month spine before interpreting the difference as month-over-month.
The expected contract is that One row per order; first customer order has NULL previous timestamp. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day18_lag_lead.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH cust_orders AS (
  SELECT o.customer_id,
         o.order_id,
         o.order_date,
         o.total_amount
  FROM orders o
)
SELECT customer_id,
       order_id,
       order_date,
       total_amount,
       LAG(total_amount) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
       ) AS prev_order_amount,
       total_amount - LAG(total_amount) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
       ) AS delta_from_prev,
       LEAD(total_amount) OVER (
         PARTITION BY customer_id
         ORDER BY order_date, order_id
       ) AS next_order_amount
FROM cust_orders
ORDER BY customer_id, order_date, order_id
LIMIT 100;
```

**How to read it:** Example 1: Start with `orders` in `FROM`/`JOIN`; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `customer_id`, `order_id`, `order_date`, `total_amount`, `prev_order_amount`, `delta_from_prev`, and `next_order_amount`. `ORDER BY` determines presentation order and the final `LIMIT 100` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `customer_id`, and `order_id`, capped at 100 rows with columns `customer_id`, `order_id`, `order_date`, `total_amount`, `prev_order_amount`, and `delta_from_prev` from `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
WITH monthly AS (
  SELECT date_trunc('month', order_date AT TIME ZONE 'UTC')::date AS month_utc,
         SUM(total_amount) AS revenue
  FROM orders
  GROUP BY month_utc
), compared AS (
  SELECT month_utc,
         revenue,
         LAG(revenue, 12) OVER (ORDER BY month_utc) AS revenue_prev_year
  FROM monthly
)
SELECT month_utc,
       revenue,
       revenue_prev_year,
       ROUND(
         (revenue - revenue_prev_year)
         / NULLIF(revenue_prev_year, 0),
         4
       ) AS yoy_growth
FROM compared
ORDER BY month_utc DESC
LIMIT 36;
```

**How to read it:** Example 2: Start with `orders` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `month_utc`, `revenue`, `revenue_prev_year`, and `yoy_growth`. `ORDER BY` determines presentation order and the final `LIMIT 36` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `month_utc`, capped at 36 rows with columns `month_utc`, `revenue`, `revenue_prev_year`, and `yoy_growth` from `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Compare each row with an earlier or later row in the same ordered partition.
- Distinguish an offset in result rows from a duration in calendar time.

## Vocabulary and concepts

- **Offset:** the number of ordered rows traversed by `LAG` or `LEAD`.
- **Default value:** the value returned when the requested offset does not
  exist.
- **Calendar spine:** an explicit row for every required date or period.

## Worked example / walkthrough

At monthly grain, place `revenue` beside `LAG(revenue) OVER (ORDER BY month)`.
The first row has no predecessor and returns `NULL`. If a month is absent, the
previous row is not necessarily the previous calendar month, so build a month
spine before interpreting the difference as month-over-month.

## Practice assumptions and review method

- **Focus:** Use `LAG` and `LEAD` to compare adjacent rows only after defining partition, chronology, tie-breakers, and first/last-row behavior.
- **Assumptions:** Intervals are computed from `timestamptz` instants. The first/last row in a partition has no adjacent value and therefore returns NULL.
- **Failure to watch for:** Omitting a partition compares unrelated entities; ordering only by a nonunique timestamp makes adjacency ambiguous.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use `LAG` and `LEAD` to compare adjacent rows only after defining partition, chronology, tie-breakers, and first/last-row behavior.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Show each order with the previous order timestamp for that customer.
   **Progressive hint:** Partition by customer and order by timestamp plus ID.
   **Inputs/evidence:** For sql-18 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, and `previous_order_date`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-18 Exercise 1, expected output: One row per order; first customer order has NULL previous timestamp. The final columns are `order_id`, `customer_id`, `order_date`, and `previous_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
   **Verify:** For sql-18 Exercise 1, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `order_date`, and `previous_order_date`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
2. **Query writing:** Calculate days since each customer's previous order.
   **Progressive hint:** Compute lag in a CTE, subtract timestamps, and preserve NULL for first orders.
   **Inputs/evidence:** For sql-18 Exercise 2, read from `orders`. Build the answer toward `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-18 Exercise 2, expected output: One row per order with nullable interval/days. The final columns are `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous`. The final order is `customer_id, order_date, order_id`.
   **Verify:** For sql-18 Exercise 2, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, `order_date`, `previous_order_date`, and `days_since_previous` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
3. **Query writing:** Show each promotion with the next promotion start date for the same product.
   **Progressive hint:** Partition by product and define a stable chronological order.
   **Inputs/evidence:** For sql-18 Exercise 3, read from `promotions`. Build the answer toward `promotion_id`, `product_id`, `start_date`, and `next_promotion_start`; keep `promotion_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-18 Exercise 3, expected output: One row per promotion; last product promotion has NULL next date. The final columns are `promotion_id`, `product_id`, `start_date`, and `next_promotion_start`. The final order is `pr.product_id, pr.start_date, pr.promotion_id`.
   **Verify:** For sql-18 Exercise 3, choose one complete partition from `promotions`; hand-calculate its first, middle, and final window values for `product_id`, `start_date`, and `next_promotion_start`, then verify output keys remain `promotion_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
4. **Prediction:** Identify first rows in each customer partition using a NULL lag without replacing it with a fake date.
   **Progressive hint:** NULL means there is no prior observation; preserve that semantic state.
   **Inputs/evidence:** For sql-18 Exercise 4, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-18 Exercise 4, expected output: One row per customer's first order. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `customer_id`.
   **Verify:** For sql-18 Exercise 4, run an anti-check that counts rows where NOT ((previous_order_id IS NULL)); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `order_date` against `orders`. Repeat with `NULL` in `order_id`, and `customer_id` and state whether the row is kept, rejected, or classified.
5. **Debugging:** Compute month-over-month stored-revenue change after aggregating to month grain.
   **Progressive hint:** Aggregate first; applying lag to raw orders would compare adjacent orders rather than months.
   **Inputs/evidence:** For sql-18 Exercise 5, read from `orders`. Build the answer toward `month_start`, `revenue`, `previous_revenue`, and `revenue_change`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-18 Exercise 5, expected output: One row per month with nullable first change. The final columns are `month_start`, `revenue`, `previous_revenue`, and `revenue_change`. The final order is `month_start`.
   **Verify:** For sql-18 Exercise 5, reselect the returned keys directly from the source; require unique `month` where the expected grain is one row per key and confirm the projected `month_start`, `revenue`, `previous_revenue`, and `revenue_change` against `orders`. Add one source row with a new `month`; verify the result gains exactly one row carrying that `month` value.
6. **Extension:** Compare each product price with the next higher price in its category.
   **Progressive hint:** Use ascending price order and product ID to define adjacency; equal prices remain separate rows.
   **Inputs/evidence:** For sql-18 Exercise 6, read from `products`. Build the answer toward `product_id`, `category`, `price`, and `next_price`; keep `product_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-18 Exercise 6, expected output: One row per product with nullable next price. The final columns are `product_id`, `category`, `price`, and `next_price`. The final order is `p.category, p.price, p.product_id`.
   **Verify:** For sql-18 Exercise 6, choose one complete partition from `products`; hand-calculate its first, middle, and final window values for `category`, `price`, and `next_price`, then verify output keys remain `product_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Omitting a partition compares unrelated entities; ordering only by a nonunique timestamp makes adjacency ambiguous.
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

- Is each window ordered uniquely enough to define “previous” or “next”?
- Are missing first/last offsets and zero denominators handled explicitly?

## Next step

Continue to [Day 19 — running aggregates](day19_running_aggregates.md).

## Deep dive and reference

Learning objectives
- Use LAG/LEAD to access prior/next row values within partitions
- Compute deltas, growth rates, and interval gaps
- Handle nulls and defaults with the third LAG/LEAD argument

Why this matters
Many metrics are changes over time: day-over-day growth, time since last purchase, step detection. LAG/LEAD express these cleanly and efficiently.

Core concepts and deep dive
- LAG(expr, offset, default) OVER (PARTITION BY k ORDER BY t): returns value offset rows before current; default substitutes for missing (e.g., first row).
- LEAD symmetric; often used for next timestamp to compute session gaps.
- Differences: expr - LAG(expr) for numeric deltas; AGE(ts, LAG(ts)) for time deltas.

Patterns
- DoD/YoY growth: (x - LAG(x)) / NULLIF(LAG(x),0).
- Sessionization: gap = ts - LAG(ts); new session if gap > interval '30 min'.
- Churn signal: last_order_date per customer and days_since_last.

Pitfalls
- Sorting by a non-unique timestamp yields unpredictable row pairing; add tiebreakers.
- Large partitions without indexes increase sort cost; index on (k, t) helps.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- LAG/LEAD: https://www.postgresql.org/docs/current/functions-window.html#FUNCTIONS-WINDOW

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-18 — Lag Lead.

I have completed the direct catalog prerequisite: `sql-17`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day18_lag_lead.md
- Answer-free learner SQL: sql/postgres-60day/day18_lag_lead.sql

Key terms to teach in context: Offset, Default value, Calendar spine. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: At monthly grain, place revenue beside LAG(revenue) OVER (ORDER BY month). The first row has no predecessor and returns NULL. If a month is absent, the previous row is not necessarily the previous calendar month, so build a month spine before interpreting the difference as month-over-month.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-18/ working copy. Never point setup, reset, DDL, or DML
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
