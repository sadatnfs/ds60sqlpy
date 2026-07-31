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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; Order rows above the global average.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; Order rows above the global average.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** Exercise 1 returns a table-shaped answer to “Query writing: Return orders whose total exceeds the overall average order total” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `evidence`, `o`, `all_orders`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 1, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
2. **Query writing:** Add the total customer count as a scalar column beside each country-level customer count.
   **Progressive hint:** An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.
   **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Query writing: Add the total customer count as a scalar column beside each country-level customer count” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `country_customers`, `all_customers`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 2, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
3. **Query writing:** Show each customer with their latest order timestamp using a scalar correlated subquery.
   **Progressive hint:** Use `MAX` to guarantee one result and let customers without orders receive NULL.
   **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Query writing: Show each customer with their latest order timestamp using a scalar correlated subquery” at one row per customer or the customer grouping key named by the prompt. Named evidence columns/objects: `evidence`, `o`, `latest_order_date`, `c`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 3, prove uniqueness at one row per customer or the customer grouping key named by the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, `customers`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
4. **Prediction:** Demonstrate that a scalar subquery with no matching rows returns NULL.
   **Progressive hint:** Use a deliberately impossible product key and test the scalar result with `IS NULL`.
   **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Prediction: Demonstrate that a scalar subquery with no matching rows returns NULL”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `evidence`, `p`, `no_row_becomes_null`.
   **Verify:** For Exercise 4, run the two forms over the identical rows in `products`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
5. **Debugging:** Repair a scalar subquery that returns many product prices by aggregating to the intended single value.
   **Progressive hint:** Choose the business reduction explicitly; this answer uses maximum price.
   **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Debugging: Repair a scalar subquery that returns many product prices by aggregating to the intended single value” at one row per product or product grouping requested. Named evidence columns/objects: `evidence`, `category_max_price`, `all_products`, `global_max_price`, `p`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 5, prove uniqueness at one row per product or product grouping requested; reconcile the result's row count and any count/sum/amount with a simpler control over `products`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
6. **Extension:** Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report.
   **Progressive hint:** Compute the global total once, then cross join the guaranteed one-row relation.
   **Expected result/shape:** Exercise 6 must make “Extension: Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report” observable through the exact DDL/DML command tag plus one row per customer or the customer grouping key named by the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `evidence`, `customer_count`, `country_customers`, `customer_share`, `c`, `cte`.
   **Verify:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `evidence`, `customer_count`, `country_customers`, `customer_share`, `c`, `cte`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.

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

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
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
