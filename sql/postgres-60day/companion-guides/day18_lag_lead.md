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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-18/day18_lag_lead.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
Offset, Default value, Calendar spine. Its worked SQL reads or creates `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: At monthly grain, place revenue beside LAG(revenue) OVER (ORDER BY month). The first row has no predecessor and returns NULL. If a month is absent, the previous row is not necessarily the previous calendar month, so build a month spine before interpreting the difference as month-over-month.
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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per order; first customer order has NULL previous timestamp.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per order; first customer order has NULL previous timestamp.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected shape:** One row per order; first customer order has NULL previous timestamp.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. **Query writing:** Calculate days since each customer's previous order.
   **Progressive hint:** Compute lag in a CTE, subtract timestamps, and preserve NULL for first orders.
   **Expected shape:** One row per order with nullable interval/days.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Query writing:** Show each promotion with the next promotion start date for the same product.
   **Progressive hint:** Partition by product and define a stable chronological order.
   **Expected shape:** One row per promotion; last product promotion has NULL next date.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. **Prediction:** Identify first rows in each customer partition using a NULL lag without replacing it with a fake date.
   **Progressive hint:** NULL means there is no prior observation; preserve that semantic state.
   **Expected shape:** One row per customer's first order.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. **Debugging:** Compute month-over-month stored-revenue change after aggregating to month grain.
   **Progressive hint:** Aggregate first; applying lag to raw orders would compare adjacent orders rather than months.
   **Expected shape:** One row per month with nullable first change.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. **Extension:** Compare each product price with the next higher price in its category.
   **Progressive hint:** Use ascending price order and product ID to define adjacency; equal prices remain separate rows.
   **Expected shape:** One row per product with nullable next price.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day18_lag_lead.md
- Answer-free learner SQL: sql/postgres-60day/day18_lag_lead.sql

The lesson concepts include Offset, Default value, Calendar spine. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: At monthly grain, place revenue beside LAG(revenue) OVER (ORDER BY month). The first row has no predecessor and returns NULL. If a month is absent, the previous row is not necessarily the previous calendar month, so build a month spine before interpreting the difference as month-over-month.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-18/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
