# Day 15 — Phase 1 Project: Multi-Dimensional Revenue Report (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 14 — numeric types and casting](day14_numeric_and_casting.md)
  and the complete Day 01–14 foundation sequence
- **Artifacts:** [learner SQL](../day15_phase1_project.sql) ·
  [solution reasoning](../solutions/day15_solutions.md) ·
  [executable solution](../solutions/day15_solutions.sql)

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

2. Open **SQL-15 — Phase1 Project** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-15/day15_phase1_project.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day15_phase1_project.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day15_phase1_project.sql
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
Metric contract, Dimensional report, Control total. Its worked SQL reads or creates `orders`, `order_items`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Build one stable orderlines relation first, with one row per intended line or order and a single net-revenue formula. Reconcile its total, then add dimension joins one at a time and compare the total after each join. Only after totals remain stable should you add grouping sets and display labels.
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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per customer.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected shape:** One row per customer.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
2. **Query writing:** Create a product profitability table from net order-line revenue and catalog cost.
   **Progressive hint:** Calculate line revenue and line cost at item grain, then aggregate to product.
   **Expected shape:** One row per sold product.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
3. **Query writing:** Build a UTC monthly order-status report with counts and stored revenue.
   **Progressive hint:** Derive one reporting month and group by month/status.
   **Expected shape:** One row per observed month and status.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
4. **Debugging:** Reconcile stored order total, computed line total, and paid total without multiplying details.
   **Progressive hint:** Aggregate items and payments independently to order grain before joining.
   **Expected shape:** One row per order with differences.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
5. **Prediction:** Compare monthly budgets with actual expenses and preserve missing sides.
   **Progressive hint:** Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero.
   **Expected shape:** One row per category/month in either source.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
6. **Extension:** Produce one executive summary row with population, activity, stored revenue, computed revenue, and payments.
   **Progressive hint:** Compute independent one-row aggregates, then cross join them to avoid detail multiplication.
   **Expected shape:** Exactly one summary row.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

## Self-check

- Does the grand total equal the independent net-line-revenue control?
- Are date window, payment handling, zero-activity entities, and subtotal
  `NULL`s documented?

## Next step

Continue to [Day 16 — window-function fundamentals](day16_window_functions_fundamentals.md).

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

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-15 — Phase1 Project.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day15_phase1_project.md
- Answer-free learner SQL: sql/postgres-60day/day15_phase1_project.sql

The lesson concepts include Metric contract, Dimensional report, Control total. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Build one stable orderlines relation first, with one row per intended line or order and a single net-revenue formula. Reconcile its total, then add dimension joins one at a time and compare the total after each join. Only after totals remain stable should you add grouping sets and display labels.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-15/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
