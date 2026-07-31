# Day 09 — Correlated Subqueries and EXISTS (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 08 — scalar and inline subqueries](day08_scalar_inline_subqueries.md)
- **Artifacts:** [learner SQL](../day09_correlated_subqueries.sql) ·
  [solution reasoning](../solutions/day09_solutions.md) ·
  [executable solution](../solutions/day09_solutions.sql)

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

2. Open **SQL-09 — Correlated Subqueries** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-09/lesson/workspace/sql/postgres-60day/day09_correlated_subqueries.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day09_correlated_subqueries.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day09_correlated_subqueries.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Correlation, Semi-join, Anti-join. Its worked SQL reads or creates `customers`, `orders`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Read WHERE EXISTS (...) as a yes/no question for one outer customer. The subquery may stop after its first qualifying order, and it never adds order columns or duplicates the customer. Replace it temporarily with a join to see why DISTINCT may become necessary in the join form.
The expected contract is that One row per qualifying customer. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day09_correlated_subqueries.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT c.*
FROM customers c
WHERE EXISTS (
  SELECT 1
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.customer_id = c.customer_id
    AND p.category = 'Electronics'
)
ORDER BY c.customer_id;
```

**How to read it:** Example 1: Start with `customers`, `orders`, `order_items`, and `products` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows. The final `SELECT` displays the columns written in the final `SELECT`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per the primary/business key of `customers` from `customers`, `orders`, `order_items`, and `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT p.product_id, p.name
FROM products p
WHERE p.product_id IN (
  SELECT DISTINCT oi.product_id
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  WHERE o.order_date >= now() - interval '30 days'
)
ORDER BY p.product_id;
```

**How to read it:** Example 2: Start with `products`, `order_items`, and `orders` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows. The final `SELECT` displays `product_id`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one row per `product_id` with columns `product_id` from `products`, `order_items`, and `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Express existence and non-existence without multiplying outer rows.
- Recognize when a correlated subquery repeats work for each candidate row.

## Vocabulary and concepts

- **Correlation:** a nested query's reference to a column from its outer query.
- **Semi-join:** return an outer row when at least one match exists.
- **Anti-join:** return an outer row only when no match exists.

## Worked example / walkthrough

Read `WHERE EXISTS (...)` as a yes/no question for one outer customer. The
subquery may stop after its first qualifying order, and it never adds order
columns or duplicates the customer. Replace it temporarily with a join to see
why `DISTINCT` may become necessary in the join form.

## Practice assumptions and review method

- **Focus:** Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.
- **Assumptions:** `EXISTS` tests whether at least one row qualifies and ignores selected values. `NOT EXISTS` remains safe when inner columns can be NULL.
- **Failure to watch for:** A correlated subquery can run conceptually per outer row; do not use it when a join or pre-aggregation states the grain more clearly.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Return customers who have at least one delivered order.
   **Progressive hint:** `EXISTS` expresses the yes/no question without multiplying customer rows.
   **Inputs/evidence:** For sql-09 Exercise 1, read from `customers`, and `orders`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-09 Exercise 1, expected output: One row per qualifying customer. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
   **Verify:** For sql-09 Exercise 1, run an anti-check that counts rows where NOT ((EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND o.status = 'delivered' ))); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`, and `orders`. Add one row for which `(EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND o.status = 'delivered' ))` is true and one for which it is false; verify only the matching `customer_id` value is returned.
2. **Query writing:** Return products that have never been sold.
   **Progressive hint:** `NOT EXISTS` correlates on product ID and is not confused by NULL membership.
   **Inputs/evidence:** For sql-09 Exercise 2, read from `products`, and `order_items`. Build the answer toward `product_id`, `name`, and `category`; keep `product_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-09 Exercise 2, expected output: One row per unsold product. The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
   **Verify:** For sql-09 Exercise 2, run an anti-check that counts rows where NOT ((NOT EXISTS ( SELECT 1 FROM order_items AS oi WHERE oi.product_id = p.product_id ))); require unique `product_id` where the expected grain is one row per key and confirm the projected `product_id`, `name`, and `category` against `products`, and `order_items`. Add one row for which `(NOT EXISTS ( SELECT 1 FROM order_items AS oi WHERE oi.product_id = p.product_id ))` is true and one for which it is false; verify only the matching `product_id` value is returned.
3. **Query writing:** Return each customer's orders that are above that customer's average order total.
   **Progressive hint:** Correlate the average to the current order's customer, not to the current order ID.
   **Inputs/evidence:** For sql-09 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-09 Exercise 3, expected output: Order rows above their own customer average. The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.customer_id, o.total_amount DESC, o.order_id`.
   **Verify:** For sql-09 Exercise 3, run an anti-check that counts rows where NOT ((o.total_amount > ( SELECT AVG(peer.total_amount) FROM orders AS peer WHERE peer.customer_id = o.customer_id ))); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `total_amount` against `orders`. Add one row for which `(o.total_amount > ( SELECT AVG(peer.total_amount) FROM orders AS peer WHERE peer.customer_id = o.customer_id ))` is true and one for which it is false; verify only the matching `order_id` value is returned.
4. **Prediction:** Explain and avoid the `NOT IN` plus NULL trap by finding customers without orders using `NOT EXISTS`.
   **Progressive hint:** Correlate on the customer key; a matching row alone determines exclusion.
   **Inputs/evidence:** For sql-09 Exercise 4, read from `customers`, and `orders`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-09 Exercise 4, expected output: One row per customer with no order. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
   **Verify:** For sql-09 Exercise 4, run an anti-check that counts rows where NOT ((NOT EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id ))); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`, and `orders`. Repeat with `NULL` in `customer_id`, and `full_name` and state whether the row is kept, rejected, or classified.
5. **Debugging:** Return only each customer's most recent order without an arbitrary `LIMIT 1`.
   **Progressive hint:** Compare to the correlated `MAX(order_date)` and break timestamp ties with the maximum ID at that timestamp.
   **Inputs/evidence:** For sql-09 Exercise 5, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-09 Exercise 5, expected output: At most one deterministic order per customer. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `o.customer_id`.
   **Verify:** For sql-09 Exercise 5, run an anti-check that counts rows where NOT ((o.order_id = ( SELECT candidate.order_id FROM orders AS candidate WHERE candidate.customer_id = o.customer_id ORDER BY candidate.order_date DESC, candidate.order_id DESC LIMIT 1 ))); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `order_date` against `orders`. Add one row for which `(o.order_id = ( SELECT candidate.order_id FROM orders AS candidate WHERE candidate.customer_id = o.customer_id ORDER BY candidate.order_date DESC, candidate.order_id DESC LIMIT 1 ))` is true and one for which it is false; verify only the matching `order_id` value is returned.
6. **Extension:** Return customers for whom every order has at least one payment, excluding customers with no orders.
   **Progressive hint:** Require an order to exist, then prove no order lacks a payment using double `NOT EXISTS`.
   **Inputs/evidence:** For sql-09 Exercise 6, read from `customers`, `orders`, and `payments`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-09 Exercise 6, expected output: One row per customer satisfying the universal condition. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
   **Verify:** For sql-09 Exercise 6, run an anti-check that counts rows where NOT ((EXISTS ( SELECT 1 FROM orders AS any_order WHERE any_order.customer_id = c.customer_id ) AND NOT EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND NOT EXISTS ( SELECT 1 FROM payments AS p WHERE p.order_id = o.order_)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`, `orders`, and `payments`. Add one row for which `(EXISTS ( SELECT 1 FROM orders AS any_order WHERE any_order.customer_id = c.customer_id ) AND NOT EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND NOT EXISTS ( SELECT 1 FROM payments AS p WHERE p.order_id = o.order_)` is true and one for which it is false; verify only the matching `customer_id` value is returned.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** A correlated subquery can run conceptually per outer row; do not use it when a join or pre-aggregation states the grain more clearly.
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

- Does the outer result retain one row per intended entity?
- Can you explain the `NULL` hazard of `NOT IN` and why `NOT EXISTS` avoids it?

## Next step

Continue to [Day 10 — data modification with subqueries](day10_dml_with_subqueries.md).

## Deep dive and reference

Learning objectives
- Write correlated subqueries that reference outer query rows
- Use EXISTS/NOT EXISTS efficiently for semi/anti-joins
- Decide between EXISTS vs IN vs JOIN for correctness and performance

Core concepts and deep dive
- Correlated subquery runs per outer row; use with EXISTS to short-circuit on the first match.
- EXISTS returns true if subquery returns any row; NOT EXISTS is a robust anti-join that handles NULLs well.
- IN vs EXISTS: IN materializes a set; EXISTS stops early. Prefer EXISTS for large or non-indexed right sides.

Examples
- Customers with at least one order: WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id=c.customer_id).
- Products never sold: WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id=p.product_id).

Pitfalls
- Correlated subqueries in SELECT list scale poorly; precompute and join.
- NOT IN with NULLs can drop all rows unexpectedly; prefer NOT EXISTS with correlated subquery.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- EXISTS: https://www.postgresql.org/docs/current/functions-subquery.html

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-09 — Correlated Subqueries.

I have completed the direct catalog prerequisite: `sql-08`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day09_correlated_subqueries.md
- Answer-free learner SQL: sql/postgres-60day/day09_correlated_subqueries.sql

Key terms to teach in context: Correlation, Semi-join, Anti-join. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Read WHERE EXISTS (...) as a yes/no question for one outer customer. The subquery may stop after its first qualifying order, and it never adds order columns or duplicates the customer. Replace it temporarily with a join to see why DISTINCT may become necessary in the join form.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-09/ working copy. Never point setup, reset, DDL, or DML
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
