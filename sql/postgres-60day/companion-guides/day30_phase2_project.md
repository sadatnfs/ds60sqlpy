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
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-30/lesson/workspace/sql/postgres-60day/day30_phase2_project.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. The key vocabulary for this lesson is Cohort, Retention denominator, Calendar spine. Its worked SQL reads or creates `orders`, `order_items`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Calculate cohort size directly from customers at one row per signup cohort. Separately deduplicate activity to one row per customer/order month, derive month offset, and count active customers. Join numerator to denominator only after both relations are stable, then guard and range-check the retention rate.
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

**How to read it:** Example 1: Start with `orders`, `order_items`, `customers`, and `age` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `cohort_month_utc`, `month_offset`, `original_customers`, `active_customers`, `retention_rate`, `revenue`, and `revenue_per_active`. `ORDER BY` determines presentation order and the final `LIMIT 200` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `cohort_month_utc`, capped at 200 rows with columns `cohort_month_utc`, `month_offset`, `original_customers`, `active_customers`, `retention_rate`, and `revenue` from `orders`, `order_items`, `customers`, and `age`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

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

**Expected result/shape:** Example 2 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `cohort_month_utc` key set and row count over `orders`, `order_items`, `customers`, and `age`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

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
   **Inputs/evidence:** For sql-30 Exercise 1, read from `customers`. Build the answer toward `cohort_month`, and `cohort_size`; keep `cohort_month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-30 Exercise 1, expected output: One row per cohort month. The final columns are `cohort_month`, and `cohort_size`. The final order is `cohort_month`.
   **Verify:** For sql-30 Exercise 1, independently aggregate `customers` by `cohort_month`; require one output row for every distinct `cohort_month` tuple and compare `cohort_size` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `cohort_size` for the existing `cohort_month` tuple and verify the new tuple appears exactly once.
2. **Query writing:** Calculate active customers and net line revenue for each cohort/order month.
   **Progressive hint:** Aggregate line items to order grain before cohort joins, then count distinct active customers.
   **Inputs/evidence:** For sql-30 Exercise 2, read from `orders`, `order_items`, and `customers`. Build the answer toward `cohort_month`, `order_month`, `active_customers`, and `net_revenue`; keep `cohort_month`, and `order_month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-30 Exercise 2, expected output: One row per observed cohort/order month. The final columns are `cohort_month`, `order_month`, `active_customers`, and `net_revenue`. The final order is `c.cohort_month, ov.order_month`.
   **Verify:** For sql-30 Exercise 2, independently aggregate `orders`, `order_items`, and `customers` by `cohort_month`, and `order_month`; require one output row for every distinct `cohort_month`, and `order_month` tuple and compare `order_month`, `active_customers`, and `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `active_customers`, and `net_revenue` for the existing `cohort_month`, and `order_month` tuple and verify the new tuple appears exactly once.
3. **Query writing:** Calculate cohort month offset and retention using original cohort size.
   **Progressive hint:** Use year-plus-month age components and guard the denominator.
   **Inputs/evidence:** For sql-30 Exercise 3, read from `customers`, and `orders`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`; keep `cohort_month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-30 Exercise 3, expected output: Observed cohort/offset rows with retention from 0 to 1. The final columns are `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate`. The final order is `a.cohort_month, month_offset`.
   **Verify:** For sql-30 Exercise 3, project `cohort_month` plus the raw source columns from `customers`, and `orders` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, `active_customers`, and `retention_rate` values match those staged rows without unintended fanout or loss. Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.
4. **Prediction:** Create a dense cohort/offset spine from offset 0 through 12 and show missing activity as zero.
   **Progressive hint:** Cross join cohort months with generate_series, then left join observed activity at the same offset grain.
   **Inputs/evidence:** For sql-30 Exercise 4, read from `customers`, `orders`, and `generate_series`. Build the answer toward `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`; keep `cohort_month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-30 Exercise 4, expected output: Thirteen rows per cohort. The final columns are `cohort_month`, `month_offset`, `cohort_size`, and `active_customers`. The final order is `s.cohort_month, s.month_offset`.
   **Verify:** For sql-30 Exercise 4, project `cohort_month` plus the raw source columns from `customers`, `orders`, and `generate_series` at each join stage; record row count and distinct `cohort_month`, then assert the final `cohort_month`, `month_offset`, `cohort_size`, and `active_customers` values match those staged rows without unintended fanout or loss. Add one source row with a new `cohort_month`; verify the result gains exactly one row carrying that `cohort_month` value.
5. **Debugging:** Calculate revenue per active customer and a trailing three-observation annualized teaching projection.
   **Progressive hint:** Compute stable cohort metrics before applying the window; disclose that observed rows may have month gaps.
   **Inputs/evidence:** For sql-30 Exercise 5, read from `orders`, `order_items`, and `customers`. Build the answer toward `cohort_month`, `order_month`, `month_offset`, `active_customers`, `revenue`, `revenue_per_active`, and `illustrative_annualized_clv`; keep `cohort_month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-30 Exercise 5, expected output: One row per observed cohort/month with nullable guarded measures. The final columns are `cohort_month`, `order_month`, `month_offset`, `active_customers`, `revenue`, `revenue_per_active`, and `illustrative_annualized_clv`. The final order is `cohort_month, month_offset`.
   **Verify:** For sql-30 Exercise 5, choose one complete partition from `orders`, `order_items`, and `customers`; hand-calculate its first, middle, and final window values for `order_month`, `active_customers`, `revenue`, and `revenue_per_active`, then verify output keys remain `cohort_month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
6. **Extension:** Audit cohort constraints and reconcile cohort revenue to net line revenue for offsets 0–12.
   **Progressive hint:** Calculate violations and compare totals at the same scoped population.
   **Inputs/evidence:** For sql-30 Exercise 6, read from `orders`, `order_items`, and `customers`. Build the answer toward `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-30 Exercise 6, expected output: One row with zero retention violations and zero revenue difference. The final columns are `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference`.
   **Verify:** For sql-30 Exercise 6, project `order_id` plus the raw source columns from `orders`, `order_items`, and `customers` at each join stage; record row count and distinct `order_id`, then assert the final `active_exceeds_cohort_violations`, `cohort_revenue`, `independent_revenue`, and `revenue_difference` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Observed rows are not a complete calendar; active customers must not exceed original cohort size, and a moving average is not a production CLV model.
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

I have completed the direct catalog prerequisite: `sql-29`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day30_phase2_project.md
- Answer-free learner SQL: sql/postgres-60day/day30_phase2_project.sql

Key terms to teach in context: Cohort, Retention denominator, Calendar spine. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Calculate cohort size directly from customers at one row per signup cohort. Separately deduplicate activity to one row per customer/order month, derive month offset, and count active customers. Join numerator to denominator only after both relations are stable, then guard and range-check the retention rate.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-30/ working copy. Never point setup, reset, DDL, or DML
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
