# Day 30 — Phase 2 Project: Cohort Retention and CLV (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 29 — pattern matching](day29_pattern_matching.md) and
  the complete window/CTE sequence from Days 16–29
- **Artifacts:** [learner SQL](../day30_phase2_project.sql) ·
  [solution reasoning](../solutions/day30_solutions.md) ·
  [executable solution](../solutions/day30_solutions.sql)

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

2. Open **SQL-30 — Phase2 Project** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-30/day30_phase2_project.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day30_phase2_project.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day30_phase2_project.sql
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
Cohort, Retention denominator, Calendar spine. Its worked SQL reads or creates `orders`, `order_items`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Calculate cohort size directly from customers at one row per signup cohort. Separately deduplicate activity to one row per customer/order month, derive month offset, and count active customers. Join numerator to denominator only after both relations are stable, then guard and range-check the retention rate.
The expected contract is that One row per cohort month. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day30_phase2_project.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH orders_enriched AS (
  SELECT o.order_id,
         o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
           AS order_month_utc,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id,
           o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date
           AS cohort_month_utc
  FROM customers c
), cohort_sizes AS (
  -- The denominator includes customers who never place an order.
  SELECT cohort_month_utc,
         COUNT(*) AS original_customers
  FROM cohorts
  GROUP BY cohort_month_utc
), metrics AS (
  SELECT e.customer_id,
         c.cohort_month_utc,
         e.order_month_utc,
         SUM(e.order_value) AS revenue
  FROM orders_enriched e
  JOIN cohorts c ON c.customer_id = e.customer_id
  GROUP BY e.customer_id, c.cohort_month_utc, e.order_month_utc
), cohort_agg AS (
  SELECT cohort_month_utc,
         order_month_utc,
         (
           EXTRACT(YEAR FROM age(order_month_utc, cohort_month_utc)) * 12
           + EXTRACT(MONTH FROM age(order_month_utc, cohort_month_utc))
         )::int AS month_offset,
         SUM(revenue) AS cohort_revenue,
         COUNT(DISTINCT customer_id) AS active_customers
  FROM metrics
  GROUP BY cohort_month_utc, order_month_utc
)
-- This first pass contains observed activity months only. Exercise 4 creates
-- a dense offset spine so a missing month becomes an explicit zero.
SELECT agg.cohort_month_utc,
       agg.month_offset,
       sizes.original_customers,
       agg.active_customers,
       ROUND(
         agg.active_customers::numeric
         / NULLIF(sizes.original_customers, 0),
         4
       ) AS retention_rate,
       ROUND(agg.cohort_revenue, 2) AS revenue,
       ROUND(
         agg.cohort_revenue / NULLIF(agg.active_customers, 0),
         2
       ) AS revenue_per_active
FROM cohort_agg AS agg
JOIN cohort_sizes AS sizes
  ON sizes.cohort_month_utc = agg.cohort_month_utc
ORDER BY agg.cohort_month_utc DESC, agg.month_offset
LIMIT 200;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per cohort month.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (COSTS OFF)
WITH orders_enriched AS (
  SELECT o.order_id,
         o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
           AS order_month_utc,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_value
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id,
           o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
), cohorts AS (
  SELECT c.customer_id,
         date_trunc('month', c.created_at AT TIME ZONE 'UTC')::date
           AS cohort_month_utc
  FROM customers c
), cohort_sizes AS (
  -- The denominator includes customers who never place an order.
  SELECT cohort_month_utc,
         COUNT(*) AS original_customers
  FROM cohorts
  GROUP BY cohort_month_utc
), metrics AS (
  SELECT e.customer_id,
         c.cohort_month_utc,
         e.order_month_utc,
         SUM(e.order_value) AS revenue
  FROM orders_enriched e
  JOIN cohorts c ON c.customer_id = e.customer_id
  GROUP BY e.customer_id, c.cohort_month_utc, e.order_month_utc
), cohort_agg AS (
  SELECT cohort_month_utc,
         order_month_utc,
         (
           EXTRACT(YEAR FROM age(order_month_utc, cohort_month_utc)) * 12
           + EXTRACT(MONTH FROM age(order_month_utc, cohort_month_utc))
         )::int AS month_offset,
         SUM(revenue) AS cohort_revenue,
         COUNT(DISTINCT customer_id) AS active_customers
  FROM metrics
  GROUP BY cohort_month_utc, order_month_utc
)
-- This first pass contains observed activity months only. Exercise 4 creates
-- a dense offset spine so a missing month becomes an explicit zero.
SELECT agg.cohort_month_utc,
       agg.month_offset,
       sizes.original_customers,
       agg.active_customers,
       ROUND(
         agg.active_customers::numeric
         / NULLIF(sizes.original_customers, 0),
         4
       ) AS retention_rate,
       ROUND(agg.cohort_revenue, 2) AS revenue,
       ROUND(
         agg.cohort_revenue / NULLIF(agg.active_customers, 0),
         2
       ) AS revenue_per_active
FROM cohort_agg AS agg
JOIN cohort_sizes AS sizes
  ON sizes.cohort_month_utc = agg.cohort_month_utc
ORDER BY agg.cohort_month_utc DESC, agg.month_offset
LIMIT 200;
```

**How to read it:** Example 2 is executed by `psql` as part of the complete lesson. Expected notices are evidence; an unexpected error stops the script.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Build cohort-size, activity, retention, and revenue measures at compatible
  grains.
- Present an illustrative projection with explicit model limitations.

## Vocabulary and concepts

- **Cohort:** entities grouped by a shared starting period or event.
- **Retention denominator:** the original eligible population for a cohort.
- **Calendar spine:** explicit cohort/period combinations, including periods
  with no observed activity.

## Worked example / walkthrough

Calculate cohort size directly from customers at one row per signup cohort.
Separately deduplicate activity to one row per customer/order month, derive
month offset, and count active customers. Join numerator to denominator only
after both relations are stable, then guard and range-check the retention rate.

## Practice assumptions and review method

- **Focus:** Build a cohort-retention analysis through explicit grains, a stable denominator, a dense calendar, reconciled revenue, and clearly limited projections.
- **Assumptions:** Cohort month is customer creation month in UTC. Active means at least one order in the order month. Net revenue is computed from line items.
- **Failure to watch for:** Observed rows are not a complete calendar; active customers must not exceed original cohort size, and a moving average is not a production CLV model.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Build a cohort-retention analysis through explicit grains, a stable denominator, a dense calendar, reconciled revenue, and clearly limited projections.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Calculate original customer count for each UTC signup cohort month.
   **Progressive hint:** Build the denominator from customers, including customers who never order.
   **Expected shape:** One row per cohort month.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. **Query writing:** Calculate active customers and net line revenue for each cohort/order month.
   **Progressive hint:** Aggregate line items to order grain before cohort joins, then count distinct active customers.
   **Expected shape:** One row per observed cohort/order month.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Query writing:** Calculate cohort month offset and retention using original cohort size.
   **Progressive hint:** Use year-plus-month age components and guard the denominator.
   **Expected shape:** Observed cohort/offset rows with retention from 0 to 1.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. **Prediction:** Create a dense cohort/offset spine from offset 0 through 12 and show missing activity as zero.
   **Progressive hint:** Cross join cohort months with generate_series, then left join observed activity at the same offset grain.
   **Expected shape:** Thirteen rows per cohort.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
5. **Debugging:** Calculate revenue per active customer and a trailing three-observation annualized teaching projection.
   **Progressive hint:** Compute stable cohort metrics before applying the window; disclose that observed rows may have month gaps.
   **Expected shape:** One row per observed cohort/month with nullable guarded measures.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. **Extension:** Audit cohort constraints and reconcile cohort revenue to net line revenue for offsets 0–12.
   **Progressive hint:** Calculate violations and compare totals at the same scoped population.
   **Expected shape:** One row with zero retention violations and zero revenue difference.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.

## Self-check

- Is `active_customers <= cohort_size` for every row and is retention in
  `[0, 1]`?
- Does the projection exclude current-period leakage and disclose sparse-month,
  margin, churn, and uncertainty limits?

## Next step

Continue to [Day 31 — EXPLAIN and EXPLAIN ANALYZE](day31_explain_analyze.md).

## Deep dive and reference

Goal
- Extend the starter customer-cohort analysis with retention rates and an
  illustrative customer-lifetime-value projection.

Current practice map
- The six maintained prompts above are the complete deliverable: denominator,
  activity and revenue, retention, a dense offset spine, a limited teaching
  projection, and a reconciliation/constraint audit.

Guidance
1) Aggregate net order-line value to one row per order before cohort joins.
2) Calculate month offsets with year and month components from `age`; extracting
   only the month component wraps after 12 months.
3) Use the original cohort size as the retention denominator, including
   customers who never order.
4) Apply the moving window after revenue per active customer is computed.
5) Reconcile order-value totals to the underlying line-item formula.

Explicit limitations
- The maintained projection annualizes a trailing three-observation average of
  revenue per active customer. It is a teaching heuristic, not a production CLV
  model.
- Observed order months are not a dense calendar. A three-row frame may span
  missing month offsets unless you add a cohort calendar.
- The model does not incorporate margin, churn probability, discount rate,
  acquisition cost, or uncertainty.

Quality checklist
- `active_customers <= cohort_size` and retention remains between 0 and 1.
- Revenue is not multiplied by line or cohort joins.
- Cohort definition, active-customer rule, missing-month treatment, and
  projection horizon are stated beside the query.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-30 — Phase2 Project.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day30_phase2_project.md
- Answer-free learner SQL: sql/postgres-60day/day30_phase2_project.sql

The lesson concepts include Cohort, Retention denominator, Calendar spine. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Calculate cohort size directly from customers at one row per signup cohort. Separately deduplicate activity to one row per customer/order month, derive month offset, and count active customers. Join numerator to denominator only after both relations are stable, then guard and range-check the retention rate.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-30/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
