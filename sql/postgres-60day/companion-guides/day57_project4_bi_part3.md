# Day 57 — Complex BI Project, Part 3: Trends and Anomalies

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 56 — percentiles and CUBE](day56_project4_bi_part2.md)
- **Artifacts:** [learner SQL](../day57_project4_bi_part3.sql) ·
  [solution reasoning](../solutions/day57_solutions.md) ·
  [executable solution](../solutions/day57_solutions.sql)

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

2. Open **SQL-57 — Project4 BI Part3** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-57/lesson/workspace/sql/postgres-60day/day57_project4_bi_part3.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day57_project4_bi_part3.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day57_project4_bi_part3.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Seasonal naive, MAD, Anomaly candidate. Its worked SQL reads or creates `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Build a complete daily spine before LAG(revenue, 7) so the offset means seven calendar days. Calculate a trailing forecast that excludes the current actual, then score the same six-month rows. For anomaly output, retain raw revenue, center, dispersion, and both scores beside the rank.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day57_project4_bi_part3.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), stats AS (
  -- Rolling 14-day window to compute z-score style anomaly score
  SELECT d,
         revenue,
         AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS avg14,
         STDDEV_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS sd14
  FROM daily
)
SELECT d,
       ROUND(revenue,2) AS revenue,
       ROUND(avg14,2)   AS rolling_avg14,
       ROUND(sd14,2)    AS rolling_sd14,
       CASE WHEN sd14 IS NULL OR sd14 = 0 THEN 0 ELSE ROUND((revenue - avg14)/sd14, 2) END AS z_score,
       CASE WHEN sd14 IS NOT NULL AND sd14 > 0 AND ABS((revenue-avg14)/sd14) >= 3 THEN 'anomaly' ELSE 'normal' END AS flag
FROM stats
ORDER BY d DESC
LIMIT 60;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
WITH daily AS (
  SELECT date_trunc('day', o.order_date)::date AS d,
         SUM(o.total_amount) AS revenue
  FROM orders o
  GROUP BY 1
), med AS (
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY revenue) AS median_rev FROM daily
), dev AS (
  SELECT d.revenue, d.d,
         ABS(d.revenue - m.median_rev) AS abs_dev,
         m.median_rev
  FROM daily d CROSS JOIN med m
), mad AS (
  SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY abs_dev) AS mad
  FROM dev
)
SELECT dev.d,
       ROUND(dev.revenue, 2) AS revenue,
       ROUND(dev.median_rev::numeric, 2) AS median_rev,
       CASE
         WHEN mad.mad = 0 THEN 0
         ELSE ROUND(
           (0.6745 * (dev.revenue - dev.median_rev) / mad.mad)::numeric,
           2
         )
       END AS modified_z,
       CASE
         WHEN mad.mad > 0
          AND ABS(0.6745 * (dev.revenue - dev.median_rev) / mad.mad) >= 3.5
         THEN 'anomaly'
         ELSE 'normal'
       END AS flag
FROM dev
CROSS JOIN mad
ORDER BY dev.d DESC
LIMIT 60;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Backtest observation-based moving average and calendar-week seasonal naive
  without leakage.
- Compare standard-deviation and median-absolute-deviation anomaly scores.

## Vocabulary and concepts

- **Seasonal naive:** forecast equal to the observation from a fixed seasonal
  lag.
- **MAD:** median absolute deviation, a robust dispersion statistic.
- **Anomaly candidate:** an observation prioritized for investigation, not
  proof of an incident.

## Worked example / walkthrough

Build a complete daily spine before `LAG(revenue, 7)` so the offset means seven
calendar days. Calculate a trailing forecast that excludes the current actual,
then score the same six-month rows. For anomaly output, retain raw revenue,
center, dispersion, and both scores beside the rank.

## Exercises

Complete these in the [learner SQL](../day57_project4_bi_part3.sql):

1. Compare MA(7) with calendar-week seasonal naive using MAPE.
   **Expected result/shape:** Exercise 1 requires a written prediction and the observed result for “Compare MA(7) with calendar-week seasonal naive using MAPE”. Show both compared result shapes at one row per requested calendar/cohort bucket and grouping key, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `day`, `revenue`, `ma7_forecast`, `seasonal_naive`, `model`, `mape`, `ma`.
   **Verify:** For Exercise 1, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
2. Rank positive/negative anomalies with SD and MAD scores.
   **Expected result/shape:** Exercise 2 returns a table-shaped answer to “Rank positive/negative anomalies with SD and MAD scores” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `absolute_deviation`, `mad`, `sd_z`, `modified_z`, `direction`, `anomaly_rank`, `sd`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 2, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
3. Predict how removing the date spine changes `LAG(..., 7)`.
   **Expected result/shape:** Exercise 3 requires a written prediction and the observed result for “Predict how removing the date spine changes LAG(..., 7)”. Show both compared result shapes at one row per requested calendar/cohort bucket and grouping key, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `max_day`, `day`, `revenue`, `observed_row_lag7`, `calendar`, `calendar_day_lag7`, `lag`.
   **Verify:** For Exercise 3, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
4. Compare MAE, RMSE, MAPE, and scored-row counts on one window.
   **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Compare MAE, RMSE, MAPE, and scored-row counts on one window”. Show both compared result shapes at one summary row per grouping key explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `error`, `model`, `scored_rows`, `mae`, `rmse`, `mape`, `zero_actual_rows`.
   **Verify:** For Exercise 4, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
5. Detect and remove current-row forecast leakage.
   **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Detect and remove current-row forecast leakage” at one row per requested calendar/cohort bucket and grouping key. Named evidence columns/objects: `day`, `revenue`, `leaky_window`, `forecast_window`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
   **Verify:** For Exercise 5, prove uniqueness at one row per requested calendar/cohort bucket and grouping key; reconcile the result's row count and any count/sum/amount with a simpler control over `orders`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
6. Preserve undefined scores for a constant series.
   **Expected result/shape:** Exercise 6 requires a written prediction and the observed result for “Preserve undefined scores for a constant series. Compare absent no-order days with explicit zero-revenue days”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `median_revenue`, `mean_revenue`, `sd_revenue`, `absolute_deviation`, `mad`, `sd_z`, `modified_mad_z`.
   **Verify:** For Exercise 6, run the two forms over the identical rows in `orders`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.

Compare absent no-order days with explicit zero-revenue days.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Guard zero standard deviation and zero MAD with NULLIF.
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

- Do forecast windows end before the current actual and use a common scoring
  set?
- Are zero dispersion, rank ties, and synthetic-data limitations explicit?

## Next step

Continue to [Day 58 — capstone ingestion and data quality](day58_final_capstone_part1.md).

## Deep dive and reference

## Project focus

- Compare a seven-observation moving average with a weekly seasonal naive.
- Calculate standard-deviation and median-absolute-deviation scores.
- Rank the strongest recent positive and negative anomaly candidates.

## How the learner script uses the current schema

Daily revenue is `SUM(orders.total_amount)` by order date. The starter shows a
14-prior-observation rolling mean/standard deviation, a global MAD score, and a
seven-prior-observation moving-average forecast with APE.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Time-series reasoning

- Build a complete date spine before `LAG(..., 7)` when “seven days ago” must
  mean calendar days; otherwise it means seven observed rows.
- Moving-average windows must exclude the current actual to prevent leakage.
- MAPE excludes zero actuals unless another error definition is chosen.
- MAD is robust to outliers; SD is more sensitive. They are complementary, not
  interchangeable proof of an incident.

## Validation and limits

- Guard zero standard deviation and zero MAD with `NULLIF`.
- State whether no-order days are absent or represented as zero.
- Rank anomaly candidates deterministically and retain both score types.
- Synthetic anomalies are investigation examples, not operational alerts or
  calibrated probabilities.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-57 — Project4 BI Part3.

I am a complete beginner. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day57_project4_bi_part3.md
- Answer-free learner SQL: sql/postgres-60day/day57_project4_bi_part3.sql

Key terms to teach in context: Seasonal naive, MAD, Anomaly candidate. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Build a complete daily spine before LAG(revenue, 7) so the offset means seven calendar days. Calculate a trailing forecast that excludes the current actual, then score the same six-month rows. For anomaly output, retain raw revenue, center, dispersion, and both scores beside the rank.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-57/ working copy. Never point setup, reset, DDL, or DML
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
