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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-26/day26_ctes_with_windows.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
Layered analytics, Window input grain, QUALIFY alternative. Its worked SQL reads or creates `orders`, `order_items`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Create monthly totals in one CTE, add LAG(total) in the next, and calculate growth in the outer query with a guarded denominator. Keeping the ratio outside the LAG layer makes the prior value visible and lets you inspect both values before interpreting the percentage.
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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; One row per observed month.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected shape:** One row per observed month.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. **Query writing:** Rank product categories by net revenue within each UTC order month.
   **Progressive hint:** Aggregate month/category first, then rank the stable aggregate.
   **Expected shape:** One row per observed month/category.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Query writing:** Return the top three category revenue levels per month.
   **Progressive hint:** Rank in one CTE and filter the window result outside.
   **Expected shape:** Top three revenue ranks for each observed month.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. **Prediction:** Calculate each category's cumulative share of monthly revenue in descending contribution order.
   **Progressive hint:** Divide running category revenue by the full monthly total; use explicit frames.
   **Expected shape:** One row per month/category with final share equal to one.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
5. **Debugging:** Calculate a three-month moving average after building a dense month calendar.
   **Progressive hint:** Join observed monthly revenue onto the calendar and treat absent observed revenue as zero only because the report defines it that way.
   **Expected shape:** A continuous chronological month series.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. **Extension:** Reconcile the final cumulative monthly revenue with the independent order total.
   **Progressive hint:** Compare at the end of the CTE/window chain instead of assuming transformations preserved totals.
   **Expected shape:** One row with zero difference.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day26_ctes_with_windows.md
- Answer-free learner SQL: sql/postgres-60day/day26_ctes_with_windows.sql

The lesson concepts include Layered analytics, Window input grain, QUALIFY alternative. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Create monthly totals in one CTE, add LAG(total) in the next, and calculate growth in the outer query with a guarded denominator. Keeping the ratio outside the LAG layer makes the prior value visible and lets you inspect both values before interpreting the percentage.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-26/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
