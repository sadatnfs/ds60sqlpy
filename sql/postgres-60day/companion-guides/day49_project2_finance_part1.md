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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-49/day49_project2_finance_part1.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
Backtest, Target leakage, MAPE. Its worked SQL reads or creates `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: At complete monthly grain, compute MA(6) with a frame ending at 1 PRECEDING, place it beside actual revenue, and score only months with a forecast and nonzero actual. Compare seasonal naive on that same scoring set and retain the number of evaluated months.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Produce a 50/50 seasonal/MA(6) forecast.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Explain and remove current-row leakage.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Build a complete monthly spine before lagging 12 months.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
5. Handle zero actuals and report excluded MAPE rows.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Compare MAE with MAPE on a low-revenue miss.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.

Score every model on a common observation window.

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

## Practice — match the learner prompts exactly

1. Build MA(6) and MA(12) one-step forecasts and compare their MAPEs with a
   12-month seasonal naive.
2. Produce a forecast equal to 50% seasonal naive plus 50% MA(6), and inspect it
   month by month.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day49_project2_finance_part1.md
- Answer-free learner SQL: sql/postgres-60day/day49_project2_finance_part1.sql

The lesson concepts include Backtest, Target leakage, MAPE. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: At complete monthly grain, compute MA(6) with a frame ending at 1 PRECEDING, place it beside actual revenue, and score only months with a forecast and nonzero actual. Compare seasonal naive on that same scoring set and retain the number of evaluated months.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-49/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
