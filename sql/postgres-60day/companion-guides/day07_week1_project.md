# Day 07 — Week 1 Project: From Questions to Queries (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 06 — set operations](day06_set_operations.md) and the
  joins and aggregates from Days 01–05
- **Artifacts:** [learner SQL](../day07_week1_project.sql) ·
  [solution reasoning](../solutions/day07_solutions.md) ·
  [executable solution](../solutions/day07_solutions.sql)

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

2. Open **SQL-07 — Week1 Project** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-07/lesson/workspace/sql/postgres-60day/day07_week1_project.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day07_week1_project.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day07_week1_project.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Report grain, Reconciliation, Allocation rule. Its worked SQL reads or creates `orders`, `customers`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Build the report in checkpoints: aggregate net line revenue to order/category, reduce payments to the declared order/method grain, join those stable inputs, and only then roll up country, category, and method. Reconcile revenue before adding cohort month so a new dimension cannot hide fanout.
The expected contract is that One row per order status. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day07_week1_project.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH recent_orders AS (
  SELECT * FROM orders WHERE order_date >= now() - interval '90 days'
), line AS (
  SELECT ro.order_id, ro.customer_id, c.country, p.category,
         (oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_revenue
  FROM recent_orders ro
  JOIN customers c ON c.customer_id = ro.customer_id
  JOIN order_items oi ON oi.order_id = ro.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT country, category,
       ROUND(SUM(line_revenue),2) AS revenue,
       COUNT(DISTINCT customer_id) AS buyers,
       ROUND(SUM(line_revenue)/NULLIF(COUNT(DISTINCT customer_id),0),2) AS rev_per_buyer
FROM line
GROUP BY country, category
ORDER BY revenue DESC, country, category
LIMIT 50;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per order status.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (COSTS OFF)
WITH recent_orders AS (
  SELECT * FROM orders WHERE order_date >= now() - interval '90 days'
), line AS (
  SELECT ro.order_id, ro.customer_id, c.country, p.category,
         (oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_revenue
  FROM recent_orders ro
  JOIN customers c ON c.customer_id = ro.customer_id
  JOIN order_items oi ON oi.order_id = ro.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT country, category,
       ROUND(SUM(line_revenue),2) AS revenue,
       COUNT(DISTINCT customer_id) AS buyers,
       ROUND(SUM(line_revenue)/NULLIF(COUNT(DISTINCT customer_id),0),2) AS rev_per_buyer
FROM line
GROUP BY country, category
ORDER BY revenue DESC, country, category
LIMIT 50;
```

**How to read it:** Example 2 is executed by `psql` as part of the complete lesson. Expected notices are evidence; an unexpected error stops the script.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Translate a report request into grain, joins, filters, aggregates, and
  validation queries.
- Prevent payment-to-line fanout and document an allocation policy.

## Vocabulary and concepts

- **Report grain:** the dimensions represented by one output row.
- **Reconciliation:** comparing a complex result with an independent trusted
  total or count.
- **Allocation rule:** a declared policy for assigning a shared amount across
  multiple categories or methods.

## Worked example / walkthrough

Build the report in checkpoints: aggregate net line revenue to order/category,
reduce payments to the declared order/method grain, join those stable inputs,
and only then roll up country, category, and method. Reconcile revenue before
adding cohort month so a new dimension cannot hide fanout.

## Practice assumptions and review method

- **Focus:** Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.
- **Assumptions:** Revenue means exact net line revenue unless a prompt explicitly asks for stored order totals. Every ranked output has a deterministic tie-breaker.
- **Failure to watch for:** A polished result is not trustworthy until its grain, denominator, missing-row policy, and reconciliation are explicit.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Build an order KPI table by status with order count, revenue, average order value, and distinct customers.
   **Progressive hint:** Aggregate orders at status grain and round only displayed monetary values.
   **Expected result/shape:** Exercise 1 must make “Query writing: Build an order KPI table by status with order count, revenue, average order value, and distinct customers” observable through the exact DDL/DML command tag plus one row at status grain; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `order_count`, `customer_count`, `revenue`, `average_order_value`, `o`, `kpi`.
   **Verify:** For Exercise 1, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `order_count`, `customer_count`, `revenue`, `average_order_value`, `o`, `kpi`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
2. **Query writing:** Return the 20 products with the highest net line revenue.
   **Progressive hint:** Aggregate order items by product before ranking; use product ID as tie-breaker.
   **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Return the 20 products with the highest net line revenue” at one row per product or product grouping requested. Named evidence columns/objects: `tie`, `evidence`, `net_revenue`, `p`, `oi`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 2, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, `order_items`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
3. **Query writing:** Create a customer summary that retains customers with no orders.
   **Progressive hint:** Left join from customers and count/order-sum nullable matches with `COALESCE` only where zero has clear meaning.
   **Expected result/shape:** Exercise 3 must make “Query writing: Create a customer summary that retains customers with no orders” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `order_count`, `stored_order_total`, `c`, `o`.
   **Verify:** For Exercise 3, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `order_count`, `stored_order_total`, `c`, `o`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
4. **Debugging:** Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows.
   **Progressive hint:** Aggregate each detail table to order grain first, then join the one-row-per-order relations.
   **Expected result/shape:** Exercise 4 returns a table-shaped answer to “Debugging: Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows” at one summary row per grouping key explicitly named in the prompt. Named evidence columns/objects: `p`, `stored_total`, `storage_difference`, `unpaid_balance`, `o`, `it`, `pt`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 4, prove uniqueness at one summary row per grouping key explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `order_items`, `payments`, `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
5. **Prediction:** Build a monthly order trend and explain which months are absent rather than zero.
   **Progressive hint:** Grouping observed orders alone cannot create empty calendar months.
   **Expected result/shape:** Exercise 5 needs the plan evidence for “Prediction: Build a monthly order trend and explain which months are absent rather than zero”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `evidence`, `order_month`, `order_count`, `stored_revenue`, `o`.
   **Verify:** For Exercise 5, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `orders` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers.
6. **Extension:** Create a compact one-row audit of customer, order, item, and payment coverage.
   **Progressive hint:** Use scalar subqueries for independent counts; this avoids accidental cross multiplication.
   **Expected result/shape:** Exercise 6 must make “Extension: Create a compact one-row audit of customer, order, item, and payment coverage” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, `c`, `o`, `customers_without_orders`.
   **Verify:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, `c`, `o`, `customers_without_orders`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** A polished result is not trustworthy until its grain, denominator, missing-row policy, and reconciliation are explicit.
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

- Can one order contribute to several payment-method rows, and if so, is its
  revenue allocation explicit?
- Are the 90-day boundary, unpaid-order policy, and report grain documented?

## Next step

Continue to [Day 08 — scalar and inline subqueries](day08_scalar_inline_subqueries.md).

## Deep dive and reference

Goal
- Extend the starter report of last-90-day revenue and buyers by country and
  category using the joins, aggregates, and set reasoning from Days 01–06.

Current practice map
- Use the six maintained prompts above as the project acceptance checklist.
  They now cover KPI grain, product and customer coverage, fanout-safe
  reconciliation, missing months, and a compact population audit.

Further extension: payment ambiguity
- `payments` can contain multiple rows per order. Joining raw payments to raw
  order lines can repeat revenue. Decide whether the report is payment revenue
  (`payments.amount`) or order-line revenue allocated to a method, and
  pre-aggregate to one row per order/method before joining.
- An order with split methods can legitimately appear in more than one method
  row. State the allocation rule rather than silently duplicating order revenue.

Checklist
1) Preserve the starter report's 90-day scope.
2) Validate each join and aggregation with order counts and revenue
   reconciliation.
3) Confirm how unpaid orders and split payments are represented.
4) Document cohort and payment-method assumptions beside the query.

Rubric
- Correct grain, no accidental payment fanout, reproducible date logic, clear
  assumptions, and readable SQL.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-07 — Week1 Project.

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day07_week1_project.md
- Answer-free learner SQL: sql/postgres-60day/day07_week1_project.sql

Key terms to teach in context: Report grain, Reconciliation, Allocation rule. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Build the report in checkpoints: aggregate net line revenue to order/category, reduce payments to the declared order/method grain, join those stable inputs, and only then roll up country, category, and method. Reconcile revenue before adding cohort month so a new dimension cannot hide fanout.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-07/ working copy. Never point setup, reset, DDL, or DML
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
