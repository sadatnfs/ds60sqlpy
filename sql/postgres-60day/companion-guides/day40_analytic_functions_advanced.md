# Day 40 — Advanced Analytic Functions

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisite:** `sql-found-02`
- **Prerequisites:** Complete
  [SQL-FOUND-02 — versioned schema migrations](../../professional/companion-guides/sql_found_02_versioned_migrations.md).
  That route already includes the window-function sequence from Days 16–22 and
  the transaction/locking sequence through SQL-39.
- **Artifacts:** [learner SQL](../day40_analytic_functions_advanced.sql) ·
  [solution reasoning](../solutions/day40_solutions.md) ·
  [executable solution](../solutions/day40_solutions.sql)

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

2. Open **SQL-40 — Analytic Functions Advanced** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-40/lesson/workspace/sql/postgres-60day/day40_analytic_functions_advanced.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day40_analytic_functions_advanced.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day40_analytic_functions_advanced.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Ordered-set aggregate, Z-score, Interpolation. Its worked SQL reads or creates `orders`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Aggregate to one row per observed order date, calculate a 15-observation mean and standard deviation, then derive (revenue - avg15) / NULLIF(sd15, 0). Keep the observation count beside the score so early, undersized windows are visible.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `d`, `ma15`, and `sd15`, capped at 60 rows with columns `d`, `revenue`, `ma15`, `sd15`, and `var15` from `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `d`, `revenue`, `ma15`, `sd15`, and `var15`. Independently group `orders`, and `daily` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day40_analytic_functions_advanced.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH daily AS (
  SELECT date_trunc('day', o.order_date) AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT d,
       revenue,
       ROUND(AVG(revenue)  OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW),2) AS ma15,
       ROUND(STDDEV_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW),2) AS sd15,
       ROUND(VAR_POP(revenue)      OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW),2) AS var15
FROM daily
ORDER BY d DESC
LIMIT 60;
```

**How to read it:** Example 1: Start with `orders` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `d`, `revenue`, `ma15`, `sd15`, and `var15`. `ORDER BY` determines presentation order and the final `LIMIT 60` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `d`, `ma15`, and `sd15`, capped at 60 rows with columns `d`, `revenue`, `ma15`, `sd15`, and `var15` from `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date) AS m,
         o.total_amount AS amt
  FROM orders o
)
SELECT m,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amt) AS p50,
       PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY amt) AS p90,
       PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM monthly
GROUP BY m
ORDER BY m DESC
LIMIT 12;
```

**How to read it:** Example 2: Start with `orders` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `m`, `p50`, `p90`, and `p99`. `ORDER BY` determines presentation order and the final `LIMIT 12` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `m`, `amt`, and `p50`, capped at 12 rows with columns `m`, `amt`, `p50`, `p90`, and `p99` from `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

## Learning objectives

- Calculate rolling dispersion, ordered-set percentiles, shares, and z-scores at
  explicit grains.
- State the limits of small or sparse statistical windows.

## Vocabulary and concepts

- **Ordered-set aggregate:** an aggregate whose calculation uses
  `WITHIN GROUP (ORDER BY ...)`.
- **Z-score:** distance from a mean measured in standard deviations.
- **Interpolation:** estimating a percentile between observed values.

## Worked example / walkthrough

Aggregate to one row per observed order date, calculate a 15-observation mean
and standard deviation, then derive
`(revenue - avg15) / NULLIF(sd15, 0)`. Keep the observation count beside the
score so early, undersized windows are visible.

## Exercises

Complete these in the
[learner SQL](../day40_analytic_functions_advanced.sql):

1. Calculate a trailing daily-revenue z-score.
   **Inputs/evidence:** For sql-40 Exercise 1, read from `orders`. Compute `order_day`, `revenue`, `avg15`, `sd15`, and `z_score` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-40 Exercise 1, expected output: one row per day with orders. A positive z-score is above the rolling mean; a negative score is below it. The final columns are `order_day`, `revenue`, `avg15`, `sd15`, and `z_score`. The final order is `order_day`.
   **Verify:** For sql-40 Exercise 1, evaluate each of `order_day`, `revenue`, `sd15`, and `z_score` in a separate control `SELECT` over `orders`; require one final row and compare every value. Add one source row with a new `day`; verify the result gains exactly one row carrying that `day` value.
2. Calculate category order-total P50/P90.
   **Inputs/evidence:** For sql-40 Exercise 2, read from `order_items`, and `products`. Compute `category`, `p50_order_value`, `p90_order_value`, and `category_orders` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-40 Exercise 2, expected output: one row per sold category. `PERCENTILE_CONT` can interpolate between observed values, so a percentile need not equal an actual order value. The final columns are `category`, `p50_order_value`, `p90_order_value`, and `category_orders`. The final order is `category`.
   **Verify:** For sql-40 Exercise 2, evaluate each of `p50_order_value`, `p90_order_value`, and `category_orders` in a separate control `SELECT` over `order_items`, and `products`; require one final row and compare every value. Add one row to an existing group and one row for a new group; recompute `p50_order_value`, `p90_order_value`, and `category_orders` for the existing `category` tuple and verify the new tuple appears exactly once.
3. Predict `percentile_disc` versus `percentile_cont` on four values.
   **Inputs/evidence:** For sql-40 Exercise 3, read from the inline `VALUES` fixture. Build the answer toward `discrete_median`, and `continuous_median`; keep `discrete_median` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-40 Exercise 3, expected output: one row per `discrete_median`. The final columns are `discrete_median`, and `continuous_median`.
   **Verify:** For sql-40 Exercise 3, reselect the returned keys directly from the source; require unique `discrete_median` where the expected grain is one row per key and confirm the projected `discrete_median`, and `continuous_median` against the inline `VALUES` fixture. Add one source row with a new `discrete_median`; verify the result gains exactly one row carrying that `discrete_median` value.
4. Calculate monthly category revenue share and deterministic rank.
   **Inputs/evidence:** For sql-40 Exercise 4, read from `orders`, `order_items`, and `products`. Build the answer toward `month`, `category`, `revenue`, `month_share`, and `category_rank`; keep `month`, and `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-40 Exercise 4, expected output: one row per `month`, and `category`. The final columns are `month`, `category`, `revenue`, `month_share`, and `category_rank`. The final order is `month DESC, category_rank`.
   **Verify:** For sql-40 Exercise 4, choose one complete partition from `orders`, `order_items`, and `products`; hand-calculate its first, middle, and final window values for `revenue`, `month_share`, and `category_rank`, then verify output keys remain `month`, and `category`. Give two rows the same `month DESC` value and different `category_rank` values; verify `month DESC, category_rank` produces the intended rank and display order.
5. Repair a forecasting frame that includes the current row.
   **Inputs/evidence:** For sql-40 Exercise 5, read from `orders`. Build the answer toward `day`, `revenue`, and `prior_seven_forecast`; keep `day` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-40 Exercise 5, expected output: at most 20 rows keyed by `day`. The final columns are `day`, `revenue`, and `prior_seven_forecast`. The final order is `day DESC`.
   **Verify:** For sql-40 Exercise 5, assert no more than 20 rows, no duplicate `day`, and no adjacent pair that violates `day DESC`. Rejoin the returned keys to `orders` to confirm `day`, `revenue`, and `prior_seven_forecast` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `day DESC`.
6. Preserve NULL z-scores for a constant series.
   **Inputs/evidence:** For sql-40 Exercise 6, read from `constant`. Build the answer toward `value`, and `z_score`; keep `value` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-40 Exercise 6, expected output: one row per `value`. The final columns are `value`, and `z_score`.
   **Verify:** For sql-40 Exercise 6, reselect the returned keys directly from the source; require unique `value` where the expected grain is one row per key and confirm the projected `value`, and `z_score` against `constant`. Repeat with `NULL` in `value`, and `z_score` and state whether the row is kept, rejected, or classified.

Verify that the undefined constant-series z-score remains `NULL`.

## Self-check

- Is the named “day” window actually calendar-dense or only observation-based?
- Do percentile and share inputs use one stable, non-duplicated grain?

## Next step

Continue to [Day 41 — complex aggregations](day41_complex_aggregations.md).

## Deep dive and reference

## What you will learn

- Compute rolling mean, standard deviation, and variance with explicit frames.
- Use ordered-set aggregates for percentiles.
- Calculate a ratio to a window total and a rolling z-score.

## How the learner script uses the current schema

The script aggregates `orders.total_amount` by order day, then applies a
15-observation window (`14 PRECEDING` plus the current row). It calculates
monthly p50/p90/p99 order totals and category revenue share from
`order_items` and `products`.

`ROWS` counts result rows, not elapsed calendar days. Because the daily series
does not build a calendar spine, the “15-day” names in the script are more
precisely 15 observed order dates.

## Statistical concepts

- A rolling z-score is `(revenue - avg15) / sd15`; use `NULLIF(sd15, 0)`.
- `PERCENTILE_CONT` interpolates between ordered values and may return a value
  not present in the data.
- A share is `value / SUM(value) OVER (...)`; calculate at one stable grain.
- Small windows make tail percentiles and standard deviation noisy.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Pitfalls and validation

- Do not repeat the whole `orders.total_amount` once per category in a
  multi-category order; use category-attributable line revenue.
- Cast ordered-set results to numeric before PostgreSQL's two-argument `ROUND`.
- Undefined zero-dispersion z-scores should remain `NULL`, not be asserted as
  normal.
- Validate that category revenue shares sum to one, allowing for rounding.

## Expanded practice lab

Prompts 3–6 distinguish continuous interpolation, observed-value percentiles,
partitioned shares, leakage-free windows, and undefined dispersion. For
`(10,20,100,200)`, `percentile_disc(0.5)` returns an observed middle choice,
while `percentile_cont(0.5)` interpolates between the two central values.

Monthly category share partitions by month; ranking should add a stable category
tie-break. A forecasting window ends at `1 PRECEDING`, and a constant series
uses `NULLIF(sd, 0)` so “undefined” is not mislabeled as a score of zero.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-40 — Analytic Functions Advanced.

I have completed the direct catalog prerequisite: `sql-found-02`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day40_analytic_functions_advanced.md
- Answer-free learner SQL: sql/postgres-60day/day40_analytic_functions_advanced.sql

Key terms to teach in context: Ordered-set aggregate, Z-score, Interpolation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate to one row per observed order date, calculate a 15-observation mean and standard deviation, then derive (revenue - avg15) / NULLIF(sd15, 0). Keep the observation count beside the score so early, undersized windows are visible.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-40/ working copy. Never point setup, reset, DDL, or DML
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
