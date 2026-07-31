# Day 08 — Scalar and Inline Subqueries (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 07 — Week 1 project](day07_week1_project.md)
- **Artifacts:** [learner SQL](../day08_scalar_inline_subqueries.sql) ·
  [solution reasoning](../solutions/day08_solutions.md) ·
  [executable solution](../solutions/day08_solutions.sql)

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

2. Open **SQL-08 — Scalar Inline Subqueries** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-08/lesson/workspace/sql/postgres-60day/day08_scalar_inline_subqueries.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day08_scalar_inline_subqueries.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day08_scalar_inline_subqueries.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Scalar subquery, Inline view, Uncorrelated subquery. Its worked SQL reads or creates `orders`, `order_items`, `customers`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: For each customer, the learner needs one first-order date. MIN(orderdate) returns exactly one value, including NULL when no order exists. Contrast that with selecting raw order dates, which can raise “more than one row returned by a subquery used as an expression.”
The expected contract is that Order rows above the global average. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day08_scalar_inline_subqueries.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT c.customer_id, c.full_name,
  (
    SELECT ROUND(COALESCE(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),0),2)
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id = c.customer_id
  ) AS lifetime_revenue
FROM customers c
ORDER BY lifetime_revenue DESC, c.customer_id
LIMIT 20;
```

**How to read it:** Example 1: Start with `orders`, `order_items`, and `customers` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows. The final `SELECT` displays the columns written in the final `SELECT`. `ORDER BY` determines presentation order and the final `LIMIT 20` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns exactly one summary row, capped at 20 rows from `orders`, `order_items`, and `customers`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT x.category, ROUND(AVG(x.order_total),2) AS avg_order_total
FROM (
  SELECT p.category, o.order_id, SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, o.order_id
) x
GROUP BY x.category
ORDER BY avg_order_total DESC, x.category;
```

**How to read it:** Example 2: Start with `orders`, `order_items`, and `products` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `category`, `order_id`, and `order_total`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `category`, and `order_id` with columns `category`, `order_id`, and `order_total` from `orders`, `order_items`, and `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Use a scalar subquery only where zero or one value is guaranteed.
- Compare subquery forms with equivalent joins for correctness and work done.

## Vocabulary and concepts

- **Scalar subquery:** a nested query used where one value is expected.
- **Inline view:** a subquery in `FROM` that behaves like a temporary relation.
- **Uncorrelated subquery:** a nested query that does not reference the outer
  row.

## Worked example / walkthrough

For each customer, the learner needs one first-order date. `MIN(order_date)`
returns exactly one value, including `NULL` when no order exists. Contrast that
with selecting raw order dates, which can raise “more than one row returned by a
subquery used as an expression.”

## Practice assumptions and review method

- **Focus:** Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.
- **Assumptions:** A scalar subquery returning no rows becomes NULL; more than one row is an error. Order a `LIMIT 1` subquery deterministically.
- **Failure to watch for:** Adding `LIMIT 1` to hide an unintended multi-row result creates arbitrary logic unless `ORDER BY` defines the chosen row.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Return orders whose total exceeds the overall average order total.
   **Progressive hint:** The aggregate subquery is guaranteed to return exactly one value.
   **Inputs/evidence:** For sql-08 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-08 Exercise 1, expected output: Order rows above the global average. The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.total_amount DESC, o.order_id`.
   **Verify:** For sql-08 Exercise 1, run an anti-check that counts rows where NOT ((o.total_amount > ( SELECT AVG(all_orders.total_amount) FROM orders AS all_orders ))); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `total_amount` against `orders`. Add one row for which `(o.total_amount > ( SELECT AVG(all_orders.total_amount) FROM orders AS all_orders ))` is true and one for which it is false; verify only the matching `order_id` value is returned.
2. **Query writing:** Add the total customer count as a scalar column beside each country-level customer count.
   **Progressive hint:** An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.
   **Inputs/evidence:** For sql-08 Exercise 2, read from `customers`. Build the answer toward `country`, `country_customers`, and `all_customers`; keep `country` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-08 Exercise 2, expected output: One row per country with a common global total. The final columns are `country`, `country_customers`, and `all_customers`. The final order is `country_customers DESC, c.country`.
   **Verify:** For sql-08 Exercise 2, independently aggregate `customers` by `country`; require one output row for every distinct `country` tuple and compare `country_customers`, and `all_customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `country_customers`, and `all_customers` for the existing `country` tuple and verify the new tuple appears exactly once.
3. **Query writing:** Show each customer with their latest order timestamp using a scalar correlated subquery.
   **Progressive hint:** Use `MAX` to guarantee one result and let customers without orders receive NULL.
   **Inputs/evidence:** For sql-08 Exercise 3, read from `orders`, and `customers`. Build the answer toward `customer_id`, `full_name`, and `latest_order_date`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-08 Exercise 3, expected output: One row per customer. The final columns are `customer_id`, `full_name`, and `latest_order_date`. The final order is `latest_order_date DESC NULLS LAST, c.customer_id`.
   **Verify:** For sql-08 Exercise 3, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `full_name`, and `latest_order_date` against `orders`, and `customers`. Tie two rows on `latest_order_date DESC NULLS LAST` and give them different `c.customer_id` values; verify `latest_order_date DESC NULLS LAST, c.customer_id` chooses a stable first/last row.
4. **Prediction:** Demonstrate that a scalar subquery with no matching rows returns NULL.
   **Progressive hint:** Use a deliberately impossible product key and test the scalar result with `IS NULL`.
   **Inputs/evidence:** For sql-08 Exercise 4, read from `products`. Compute `no_row_becomes_null` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-08 Exercise 4, expected output: One row whose boolean result is true. The final columns are `no_row_becomes_null`.
   **Verify:** For sql-08 Exercise 4, evaluate each of `no_row_becomes_null` in a separate control `SELECT` over `products`; require one final row and compare every value. Repeat with `NULL` in `no_row_becomes_null` and state whether the row is kept, rejected, or classified.
5. **Debugging:** Repair a scalar subquery that returns many product prices by aggregating to the intended single value.
   **Progressive hint:** Choose the business reduction explicitly; this answer uses maximum price.
   **Inputs/evidence:** For sql-08 Exercise 5, read from `products`. Build the answer toward `category`, `category_max_price`, and `global_max_price`; keep `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-08 Exercise 5, expected output: One row per category with a scalar global maximum for comparison. The final columns are `category`, `category_max_price`, and `global_max_price`. The final order is `p.category`.
   **Verify:** For sql-08 Exercise 5, independently aggregate `products` by `category`; require one output row for every distinct `category` tuple and compare `category_max_price`, and `global_max_price` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `category_max_price`, and `global_max_price` for the existing `category` tuple and verify the new tuple appears exactly once.
6. **Extension:** Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report.
   **Progressive hint:** Compute the global total once, then cross join the guaranteed one-row relation.
   **Inputs/evidence:** For sql-08 Exercise 6, read from `customers`. Build the answer toward `country`, `country_customers`, and `customer_share`; keep `country`, and `customer_count` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-08 Exercise 6, expected output: One row per country with country share. The final columns are `country`, `country_customers`, and `customer_share`. The final order is `customer_share DESC, c.country`.
   **Verify:** For sql-08 Exercise 6, independently aggregate `customers` by `country`, and `customer_count`; require one output row for every distinct `country`, and `customer_count` tuple and compare `country_customers`, and `customer_share` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `country_customers`, and `customer_share` for the existing `country`, and `customer_count` tuple and verify the new tuple appears exactly once.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Adding LIMIT 1 to hide an unintended multi-row result creates arbitrary logic unless ORDER BY defines the chosen row.
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

- Can every scalar subquery prove its one-value contract without an arbitrary
  `LIMIT 1`?
- Are customers with no matching orders handled deliberately?

## Next step

Continue to [Day 09 — correlated subqueries and EXISTS](day09_correlated_subqueries.md).

## Deep dive and reference

Learning objectives
- Use scalar subqueries in SELECT/WHERE for per-row lookups
- Use IN/ANY/ALL with subqueries and understand semantics
- Replace subqueries with joins where appropriate for performance

Core concepts and deep dive
- Scalar subquery returns a single value; errors on >1 row. Use LIMIT 1 with ORDER BY to guarantee determinism.
- IN subquery builds a set; ANY/ALL compare a value against a subquery-produced set with an operator.
- Correlated vs uncorrelated inline subqueries: prefer uncorrelated when possible.

Examples
- SELECT customer_id, (SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.customer_id) AS order_cnt FROM customers c.
- `WHERE product_id IN (SELECT product_id FROM promotions WHERE CURRENT_DATE
  BETWEEN start_date AND end_date)`.

Pitfalls
- Scalar subqueries in SELECT executed per row; may be slow. Consider pre-aggregating and joining.
- IN with large sets can be slow; join instead or use EXISTS.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Subqueries: https://www.postgresql.org/docs/current/sql-select.html#SQL-SELECT-SUBQUERIES

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-08 — Scalar Inline Subqueries.

I have completed the direct catalog prerequisite: `sql-07`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day08_scalar_inline_subqueries.md
- Answer-free learner SQL: sql/postgres-60day/day08_scalar_inline_subqueries.sql

Key terms to teach in context: Scalar subquery, Inline view, Uncorrelated subquery. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For each customer, the learner needs one first-order date. MIN(orderdate) returns exactly one value, including NULL when no order exists. Contrast that with selecting raw order dates, which can raise “more than one row returned by a subquery used as an expression.”

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-08/ working copy. Never point setup, reset, DDL, or DML
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
