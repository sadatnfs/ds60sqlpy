# Day 26 — CTEs with Window Functions: Layered Analytics (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 25 — multiple CTEs and hierarchies](day25_multiple_ctes_hierarchies.md)
- **Artifacts:** [learner SQL](../day26_ctes_with_windows.sql) ·
  [solution reasoning](../solutions/day26_solutions.md) ·
  [executable solution](../solutions/day26_solutions.sql)

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

2. Open **SQL-26 — CTEs with Windows** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-26/lesson/workspace/sql/postgres-60day/day26_ctes_with_windows.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day26_ctes_with_windows.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day26_ctes_with_windows.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Layered analytics, Window input grain, QUALIFY alternative. Its worked SQL reads or creates `orders`, `order_items`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Create monthly totals in one CTE, add LAG(total) in the next, and calculate growth in the outer query with a guarded denominator. Keeping the ratio outside the LAG layer makes the prior value visible and lets you inspect both values before interpreting the percentage.
The expected contract is that One row per observed month. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day26_ctes_with_windows.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH line AS (
  SELECT o.order_id, o.customer_id, o.order_date,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id, o.order_date
), ranked AS (
  SELECT line.*,
         RANK() OVER (
           PARTITION BY customer_id
           ORDER BY order_total DESC
         ) AS rnk
  FROM line
)
SELECT customer_id, order_id, order_date, order_total, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY customer_id, rnk, order_total DESC, order_id;
```

**How to read it:** Example 1: Start with `orders`, and `order_items` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `customer_id`, `order_id`, `order_date`, `order_total`, and `rnk`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `customer_id`, and `order_id` with columns `customer_id`, `order_id`, `order_date`, `order_total`, and `rnk` from `orders`, and `order_items`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (COSTS OFF)
WITH line AS (
  SELECT o.order_id, o.customer_id, o.order_date,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id, o.order_date
), ranked AS (
  SELECT line.*,
         RANK() OVER (
           PARTITION BY customer_id
           ORDER BY order_total DESC
         ) AS rnk
  FROM line
)
SELECT customer_id, order_id, order_date, order_total, rnk
FROM ranked
WHERE rnk <= 3
ORDER BY customer_id, rnk, order_total DESC, order_id;
```

**How to read it:** Example 2 is executed by `psql` as part of the complete lesson. Expected notices are evidence; an unexpected error stops the script.

**Expected result/shape:** Example 2 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `customer_id`, and `order_id` key set and row count over `orders`, and `order_items`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

## Learning objectives

- Pre-aggregate to the correct grain before calculating ranks, shares, or
  changes.
- Filter a window result through an outer query in PostgreSQL.

## Vocabulary and concepts

- **Layered analytics:** successive relational stages with progressively richer
  measures.
- **Window input grain:** the meaning of one row before `OVER (...)` is applied.
- **QUALIFY alternative:** an outer `SELECT` that filters a computed window
  column.

## Worked example / walkthrough

Create monthly totals in one CTE, add `LAG(total)` in the next, and calculate
growth in the outer query with a guarded denominator. Keeping the ratio outside
the `LAG` layer makes the prior value visible and lets you inspect both values
before interpreting the percentage.

## Practice assumptions and review method

- **Focus:** Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.
- **Assumptions:** Monthly reporting uses UTC. Window order always includes chronological keys; revenue uses exact numeric and is rounded only in final output.
- **Failure to watch for:** Applying windows before aggregation compares detail rows, while filtering too early can remove the history a lag or moving frame needs.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Combine CTE grain control with window comparisons so time-series and ranking logic remain readable and reconcilable.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Calculate monthly stored revenue and its prior-month value/change.
   **Progressive hint:** Aggregate to month in a CTE, then lag the monthly measure.
   **Inputs/evidence:** For sql-26 Exercise 1, read from `orders`. Build the answer toward `month_start`, `revenue`, `previous_revenue`, and `change`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-26 Exercise 1, expected output: One row per observed month. The final columns are `month_start`, `revenue`, `previous_revenue`, and `change`. The final order is `month_start`.
   **Verify:** For sql-26 Exercise 1, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `month_start`, `revenue`, `previous_revenue`, and `change` against `orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
2. **Query writing:** Rank product categories by net revenue within each UTC order month.
   **Progressive hint:** Aggregate month/category first, then rank the stable aggregate.
   **Inputs/evidence:** For sql-26 Exercise 2, read from `orders`, `order_items`, and `products`. Build the answer toward `month_start`, `category`, `revenue`, and `revenue_rank`; keep `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-26 Exercise 2, expected output: One row per observed month/category. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
   **Verify:** For sql-26 Exercise 2, choose one complete partition from `orders`, `order_items`, and `products`; hand-calculate its first, middle, and final window values for `revenue`, and `revenue_rank`, then verify output keys remain `category`. Give two rows the same `month_start` value and different `category` values; verify `month_start, revenue_rank, category` produces the intended rank and display order.
3. **Query writing:** Return the top three category revenue levels per month.
   **Progressive hint:** Rank in one CTE and filter the window result outside.
   **Inputs/evidence:** For sql-26 Exercise 3, read from `orders`, `order_items`, and `products`. Build the answer toward `month_start`, `category`, `revenue`, and `revenue_rank`; keep `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-26 Exercise 3, expected output: Top three revenue ranks for each observed month. The final columns are `month_start`, `category`, `revenue`, and `revenue_rank`. The final order is `month_start, revenue_rank, category`.
   **Verify:** For sql-26 Exercise 3, project `category` plus the raw source columns from `orders`, `order_items`, and `products` at each join stage; record row count and distinct `category`, then assert the final `month_start`, `category`, `revenue`, and `revenue_rank` values match those staged rows without unintended fanout or loss. Give two rows the same `month_start` value and different `category` values; verify `month_start, revenue_rank, category` produces the intended rank and display order.
4. **Prediction:** Calculate each category's cumulative share of monthly revenue in descending contribution order.
   **Progressive hint:** Divide running category revenue by the full monthly total; use explicit frames.
   **Inputs/evidence:** For sql-26 Exercise 4, read from `orders`, `order_items`, and `products`. Build the answer toward `month_start`, `category`, `revenue`, and `cumulative_revenue_share`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-26 Exercise 4, expected output: One row per month/category with final share equal to one. The final columns are `month_start`, `category`, `revenue`, and `cumulative_revenue_share`. The final order is `month_start, revenue DESC, category`.
   **Verify:** For sql-26 Exercise 4, choose one complete partition from `orders`, `order_items`, and `products`; hand-calculate its first, middle, and final window values for `revenue`, and `cumulative_revenue_share`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
5. **Debugging:** Calculate a three-month moving average after building a dense month calendar.
   **Progressive hint:** Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way.
   **Inputs/evidence:** For sql-26 Exercise 5, read from `orders`. Build the answer toward `month_start`, `revenue`, and `moving_3_month_average`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-26 Exercise 5, expected output: A continuous chronological month series. The final columns are `month_start`, `revenue`, and `moving_3_month_average`. The final order is `month_start`.
   **Verify:** For sql-26 Exercise 5, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `revenue`, and `moving_3_month_average`, then verify output keys remain `order_id`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
6. **Extension:** Reconcile the final cumulative monthly revenue with the independent order total.
   **Progressive hint:** Compare at the end of the CTE/window chain instead of assuming transformations preserved totals.
   **Inputs/evidence:** For sql-26 Exercise 6, read from `orders`. Build the answer toward `final_cumulative`, `independent_total`, and `difference`; keep `cumulative_revenue` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-26 Exercise 6, expected output: One row with zero difference. The final columns are `final_cumulative`, `independent_total`, and `difference`.
   **Verify:** For sql-26 Exercise 6, independently aggregate `orders` by `cumulative_revenue`; require one output row for every distinct `cumulative_revenue` tuple and compare `independent_total` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `independent_total` for the existing `cumulative_revenue` tuple and verify the new tuple appears exactly once.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Applying windows before aggregation compares detail rows, while filtering too early can remove the history a lag or moving frame needs.
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

- Does every window operate over the intended pre-aggregated relation?
- Is window filtering performed in an outer query rather than an invalid
  same-level `WHERE`?

## Next step

Continue to [Day 27 — pivoting and unpivoting](day27_pivot_unpivot.md).

## Deep dive and reference

Learning objectives
- Combine CTE staging with window calculations for clarity and speed
- Decide which grain to aggregate at before applying windows
- Build multi-stage pipelines for advanced KPIs (shares, ranks, rolling metrics)

Why this matters
Complex analytics often need a staging step (pre-aggregations) before windowing. Getting the grain right avoids wrong answers and large sorts, and it yields maintainable queries.

Core concepts and deep dive
- Pre-aggregate, then window: compute daily/category totals in a CTE, then run windows over that smaller set.
- Windows across aggregates: once at daily grain, you can apply running totals, moving averages, and shares cheaply.
- Multiple windows: define named window specs to compute per-partition and global metrics in the same SELECT.

Patterns
- WITH daily AS (... GROUP BY day, key) SELECT day, key, SUM(x) OVER (PARTITION BY key ORDER BY day) ... FROM daily.
- Shares of total: x / NULLIF(SUM(x) OVER (PARTITION BY key),0) and x / NULLIF(SUM(x) OVER(),0).

Pitfalls
- Windowing raw rows creates noisy and heavy computations; pre-aggregate first.
- Filtering on windowed values in the same SELECT; wrap in another SELECT to filter.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- CTEs: https://www.postgresql.org/docs/current/queries-with.html
- Windows: https://www.postgresql.org/docs/current/tutorial-window.html

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-26 — CTEs with Windows.

I have completed the direct catalog prerequisite: `sql-25`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day26_ctes_with_windows.md
- Answer-free learner SQL: sql/postgres-60day/day26_ctes_with_windows.sql

Key terms to teach in context: Layered analytics, Window input grain, QUALIFY alternative. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Create monthly totals in one CTE, add LAG(total) in the next, and calculate growth in the outer query with a guarded denominator. Keeping the ratio outside the LAG layer makes the prior value visible and lets you inspect both values before interpreting the percentage.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-26/ working copy. Never point setup, reset, DDL, or DML
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
