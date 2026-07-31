# Day 41 — Complex Aggregations

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 40 — advanced analytic functions](day40_analytic_functions_advanced.md)
- **Artifacts:** [learner SQL](../day41_complex_aggregations.sql) ·
  [solution reasoning](../solutions/day41_solutions.md) ·
  [executable solution](../solutions/day41_solutions.sql)

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

2. Open **SQL-41 — Complex Aggregations** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-41/day41_complex_aggregations.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day41_complex_aggregations.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day41_complex_aggregations.sql
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
on screen are not automatically stored. This lesson introduces or reinforces
FILTER clause, Conditional aggregate, Ordered aggregation. Its worked SQL reads or creates `order_items`, `products`, `orders`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Establish one order-line relation, then calculate 30-day revenue, 90-day revenue, order count, and customer count in one category group using FILTER. Reconcile each measure with a simpler single-purpose query before trusting the combined dashboard.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day41_complex_aggregations.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT p.category,
       SUM(oi.quantity)                                                   AS total_qty,
       SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '30 days') AS qty_30d,
       SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '90 days') AS qty_90d,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),2)           AS revenue,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount))
             FILTER (WHERE o.order_date >= now() - interval '30 days'),2) AS revenue_30d
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o   ON o.order_id = oi.order_id
GROUP BY p.category
ORDER BY revenue DESC;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT c.country,
       SUM(CASE WHEN o.status IN ('paid','shipped','delivered') THEN 1 ELSE 0 END) AS successful_orders,
       SUM(CASE WHEN o.status = 'returned' THEN 1 ELSE 0 END)                      AS returned_orders,
       ROUND(SUM(CASE WHEN o.status <> 'returned' THEN o.total_amount ELSE 0 END),2) AS net_revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY net_revenue DESC;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Produce several conditional measures from one controlled fact grain.
- Build deterministic ordered labels after ranking within a partition.

## Vocabulary and concepts

- **FILTER clause:** a per-aggregate condition written after the aggregate.
- **Conditional aggregate:** a measure calculated only for qualifying rows.
- **Ordered aggregation:** concatenation or collection under a specified order.

## Worked example / walkthrough

Establish one order-line relation, then calculate 30-day revenue, 90-day
revenue, order count, and customer count in one category group using `FILTER`.
Reconcile each measure with a simpler single-purpose query before trusting the
combined dashboard.

## Exercises

Complete these in the [learner SQL](../day41_complex_aggregations.sql):

1. Build six category metrics with `FILTER`.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
2. List each country's top five products with `string_agg`.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Predict explicit grouping sets versus a two-column `CUBE`.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Build country status/revenue/customer metrics with `FILTER`.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
5. Distinguish stored NULLs from subtotal NULLs with `GROUPING`.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Return a typed empty array for an empty aggregate input.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Decide explicitly when an absent measure should be `NULL` or zero.

## Self-check

- Are order and customer counts protected from line-level fanout?
- Is the top-five label order stable under metric ties?

## Next step

Continue to [Day 42 — data quality and validation](day42_data_quality_validation.md).

## Deep dive and reference

## What you will learn

- Calculate several conditional metrics in one grouped query with `FILTER`.
- Express equivalent conditional aggregates with `CASE`.
- Build ordered labels with `string_agg`.

## How the learner script uses the current schema

The starter calculates category units and revenue over all history, 30 days, and
90 days by joining `orders`, `order_items`, and `products`. It also reports
successful/returned orders by `customers.country`, then demonstrates
`string_agg(DISTINCT products.name, ...)` by category.

The valid successful status set used by the script is `paid`, `shipped`, and
`delivered`; `returned` is reported separately. Use only the statuses supplied
by the course setup.

## Multi-metric design

- Establish line-item grain before summing net revenue.
- Use `COUNT(DISTINCT order_id)` and `COUNT(DISTINCT customer_id)` when a join
  has expanded each order to multiple item rows.
- Guard every denominator with `NULLIF`.
- Conditional sums can be `NULL` when no row qualifies; decide whether display
  policy should use `COALESCE`.

## Practice — match the learner prompts exactly

1. Build a six-metric dashboard by category with `FILTER`: 30-day revenue,
   90-day revenue, 30-day orders, 30-day units, 90-day customers, and 30-day
   revenue per order.
2. For each country, rank products by net line revenue, keep the top five, then
   `string_agg` their names in revenue-rank order.

## Pitfalls and validation

- Applying a global `LIMIT 5` does not produce five products per country; rank
  within country first.
- Do not sum `orders.total_amount` after joining to item rows.
- Add a deterministic tie-break such as `product_id`.
- Validate dashboard totals against a simpler single-metric query before
  trusting the combined report.

## Expanded practice lab

Prompts 3–6 make aggregate grain and subtotal identity explicit. A two-column
`CUBE` emits detail, both one-dimensional subtotals, and a grand total; the
listed `GROUPING SETS` intentionally omits detail. Use `GROUPING(column)` rather
than `column IS NULL` to detect a subtotal.

`FILTER` keeps several metric definitions readable in one grouped query.
Aggregates over no input rows often return NULL, so `COALESCE(array_agg(...),
'{}'::text[])` needs an explicit type matching the aggregate result.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-41 — Complex Aggregations.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day41_complex_aggregations.md
- Answer-free learner SQL: sql/postgres-60day/day41_complex_aggregations.sql

The lesson concepts include FILTER clause, Conditional aggregate, Ordered aggregation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Establish one order-line relation, then calculate 30-day revenue, 90-day revenue, order count, and customer count in one category group using FILTER. Reconcile each measure with a simpler single-purpose query before trusting the combined dashboard.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-41/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
