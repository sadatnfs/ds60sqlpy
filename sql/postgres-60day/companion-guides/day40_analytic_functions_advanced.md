# Day 40 — Advanced Analytic Functions

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 39 — locks and deadlocks](day39_locks_deadlocks.md)
  plus the window-function sequence from Days 16–22
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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-40/day40_analytic_functions_advanced.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
Ordered-set aggregate, Z-score, Interpolation. Its worked SQL reads or creates `orders`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Aggregate to one row per observed order date, calculate a 15-observation mean and standard deviation, then derive (revenue - avg15) / NULLIF(sd15, 0). Keep the observation count beside the score so early, undersized windows are visible.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Calculate category order-total P50/P90.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Predict `percentile_disc` versus `percentile_cont` on four values.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Calculate monthly category revenue share and deterministic rank.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Repair a forecasting frame that includes the current row.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. Preserve NULL z-scores for a constant series.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

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

## Practice — match the learner prompts exactly

1. Add the daily-revenue z-score using the same trailing 15-observation mean and
   sample standard deviation.
2. For every product category, compute p50 and p90 of the order value
   attributable to that category: first aggregate net line revenue at
   `(category, order_id)` grain, then calculate category percentiles.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day40_analytic_functions_advanced.md
- Answer-free learner SQL: sql/postgres-60day/day40_analytic_functions_advanced.sql

The lesson concepts include Ordered-set aggregate, Z-score, Interpolation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate to one row per observed order date, calculate a 15-observation mean and standard deviation, then derive (revenue - avg15) / NULLIF(sd15, 0). Keep the observation count beside the score so early, undersized windows are visible.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-40/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
