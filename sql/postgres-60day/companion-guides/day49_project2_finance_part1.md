# Day 49 — Finance/Operations Project, Part 1: Revenue Forecasting

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 48 — affinity and attribution](day48_project1_ecommerce_part3.md)
- **Artifacts:** [learner SQL](../day49_project2_finance_part1.sql) ·
  [solution reasoning](../solutions/day49_solutions.md) ·
  [executable solution](../solutions/day49_solutions.sql)

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

2. Open **SQL-49 — Project2 Finance Part1** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-49/lesson/workspace/sql/postgres-60day/day49_project2_finance_part1.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day49_project2_finance_part1.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day49_project2_finance_part1.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Backtest, Target leakage, MAPE. Its worked SQL reads or creates `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: At complete monthly grain, compute MA(6) with a frame ending at 1 PRECEDING, place it beside actual revenue, and score only months with a forecast and nonzero actual. Compare seasonal naive on that same scoring set and retain the number of evaluated months.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `month`, capped at 24 rows with columns `month`, and `revenue` from `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `*`. Independently group `orders`, and `monthly` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day49_project2_finance_part1.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT * FROM monthly ORDER BY month DESC LIMIT 24;
```

**How to read it:** Example 1: Start with `orders` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `*`. `ORDER BY` determines presentation order and the final `LIMIT 24` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `month`, capped at 24 rows with columns `month`, and `revenue` from `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
WITH monthly AS (
  SELECT date_trunc('month', o.order_date)::date AS month,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
)
SELECT m.month,
       m.revenue,
       LAG(m.revenue, 12) OVER (ORDER BY m.month) AS prev_year,
       ROUND((m.revenue - COALESCE(LAG(m.revenue,12) OVER (ORDER BY m.month),0))
             / NULLIF(LAG(m.revenue,12) OVER (ORDER BY m.month),0), 4) AS yoy_growth
FROM monthly m
ORDER BY m.month DESC
LIMIT 36;
```

**How to read it:** Example 2: Start with `orders` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `month`, `revenue`, `prev_year`, and `yoy_growth`. `ORDER BY` determines presentation order and the final `LIMIT 36` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `month`, and `prev_year`, capped at 36 rows with columns `month`, `revenue`, `prev_year`, and `yoy_growth` from `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

## Learning objectives

- Backtest moving-average and seasonal-naive forecasts without target leakage.
- Compare errors on a common scoring population and disclose sparse history.

## Vocabulary and concepts

- **Backtest:** evaluate a forecast using only information available before each
  historical target.
- **Target leakage:** using the actual target or future information in its
  prediction.
- **MAPE:** mean absolute percentage error, undefined for zero actuals.

## Worked example / walkthrough

At complete monthly grain, compute MA(6) with a frame ending at
`1 PRECEDING`, place it beside actual revenue, and score only months with a
forecast and nonzero actual. Compare seasonal naive on that same scoring set and
retain the number of evaluated months.

## Exercises

Complete these in the [learner SQL](../day49_project2_finance_part1.sql):

1. Backtest MA(6), MA(12), and seasonal naive with MAPE.
   **Inputs/evidence:** For sql-49 Exercise 1, aggregate `orders` by observed month, left-join to `month_spine`, compute full-window history counts, and reshape four forecasts over `common_scoring_rows`.
   **Expected result/shape:** For sql-49 Exercise 1, expected output: exactly four rows keyed by `model`, with `scored_rows`, `zero_actual_rows`, and `mape`, ordered by `model`.
   **Verify:** For sql-49 Exercise 1, require `ma6_history_rows = 6`, `ma12_history_rows = 12`, and a non-NULL twelve-month seasonal value before any model is scored. All four models must have identical eligible months and equal `scored_rows`; independently recompute each MAPE.
2. Produce a 50/50 seasonal/MA(6) forecast.
   **Inputs/evidence:** For sql-49 Exercise 2, read from `orders`. Build the answer toward `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-49 Exercise 2, expected output: one row per `month`. The final columns are `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast`. The final order is `month DESC`.
   **Verify:** For sql-49 Exercise 2, run an anti-check that counts rows where NOT ((seasonal_naive IS NOT NULL)); require unique `month` where the expected grain is one row per key and confirm the projected `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast` against `orders`. Add one row for which `(seasonal_naive IS NOT NULL)` is true and one for which it is false; verify only the matching `month` value is returned.
3. Explain and remove current-row leakage.
   **Inputs/evidence:** For sql-49 Exercise 3, read from `orders`. Build the answer toward `month`, `revenue`, `leaky_ma6`, and `honest_ma6`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-49 Exercise 3, expected output: one row per `month`. The final columns are `month`, `revenue`, `leaky_ma6`, and `honest_ma6`. The final order is `month`.
   **Verify:** For sql-49 Exercise 3, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `revenue`, `leaky_ma6`, and `honest_ma6`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
4. Build a complete monthly spine before lagging 12 months.
   **Inputs/evidence:** For sql-49 Exercise 4, read from `orders`. Build the answer toward `month`, `revenue`, `had_source_rows`, and `seasonal_forecast`; keep `month` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-49 Exercise 4, expected output: one row per calendar month before the 12-row lag. The final columns are `month`, `revenue`, `had_source_rows`, and `seasonal_forecast`. The final order is `month`.
   **Verify:** For sql-49 Exercise 4, choose one complete partition from `orders`; hand-calculate its first, middle, and final window values for `revenue`, and `had_source_rows`, then verify output keys remain `month`. Test a one-row partition and a partition with at least three rows; verify the frame boundary and partition reset explicitly.
5. Handle zero actuals and report excluded MAPE rows.
   **Inputs/evidence:** For sql-49 Exercise 5, read from `toy`. Build the answer toward `mape`, `scored_rows`, and `excluded_zero_actuals`; keep `mape` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-49 Exercise 5, expected output: one row per `mape`. The final columns are `mape`, `scored_rows`, and `excluded_zero_actuals`.
   **Verify:** For sql-49 Exercise 5, reselect the returned keys directly from the source; require unique `mape` where the expected grain is one row per key and confirm the projected `mape`, `scored_rows`, and `excluded_zero_actuals` against `toy`. Add one source row with a new `mape`; verify the result gains exactly one row carrying that `mape` value.
6. Compare MAE with MAPE on a low-revenue miss.
   **Inputs/evidence:** For sql-49 Exercise 6, read from `toy`. Build the answer toward `mae`, and `mape`; keep `mae` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-49 Exercise 6, expected output: one row per `mae`. The final columns are `mae`, and `mape`.
   **Verify:** For sql-49 Exercise 6, reselect the returned keys directly from the source; require unique `mae` where the expected grain is one row per key and confirm the projected `mae`, and `mape` against `toy`. Add one source row with a new `mae`; verify the result gains exactly one row carrying that `mae` value.

Score every model on a common observation window.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Return forecast and actual side by side.
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

- Does every forecast exclude its current actual?
- Are model errors compared over the same months, with excluded zero actuals
  and warm-up periods reported?

## Next step

Continue to [Day 50 — budget variance](day50_project2_finance_part2.md).

## Deep dive and reference

## Project focus

- Build one monthly order-revenue series.
- Backtest moving-average and seasonal-naive forecasts.
- Compare MAPE and inspect a 50/50 blended forecast.

## How the learner script uses the current schema

The starter aggregates `orders.total_amount` by order month, calculates
year-over-year growth with `LAG(..., 12)`, projects future months from last
year's matching month, and shows a trailing three-month average.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Backtesting reasoning

- Moving windows must end at `1 PRECEDING`; including the current actual leaks
  the answer into its forecast.
- `LAG(revenue, 12)` means the previous 12 result rows. Build a complete month
  calendar first if months can be absent.
- MAPE is undefined when actual revenue is zero; disclose excluded periods and
  consider MAE as a companion metric.
- Compare models over a common scoring window when warm-up history differs.

## Validation and limits

- Return forecast and actual side by side.
- Record the number of scored months for each model.
- The deterministic seed has only a few years of history, so model ranking is a
  learning result, not evidence of forecast reliability.
- A historical backtest does not create a production forecast pipeline.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-49 — Project2 Finance Part1.

I have completed the direct catalog prerequisite: `sql-48`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day49_project2_finance_part1.md
- Answer-free learner SQL: sql/postgres-60day/day49_project2_finance_part1.sql

Key terms to teach in context: Backtest, Target leakage, MAPE. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: At complete monthly grain, compute MA(6) with a frame ending at 1 PRECEDING, place it beside actual revenue, and score only months with a forecast and nonzero actual. Compare seasonal naive on that same scoring set and retain the number of evaluated months.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-49/ working copy. Never point setup, reset, DDL, or DML
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
