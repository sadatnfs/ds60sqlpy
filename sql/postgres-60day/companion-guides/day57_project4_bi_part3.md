# Day 57: Complex BI Project, Part 3: Trends and Anomalies

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-57**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-57/lesson/workspace/sql/postgres-60day/day57_project4_bi_part3.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-57
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 56; percentiles and CUBE](day56_project4_bi_part2.md)
- **Artifacts:** [learner SQL](../day57_project4_bi_part3.sql) ·
  [solution reasoning](../solutions/day57_solutions.md) ·
  [executable solution](../solutions/day57_solutions.sql)

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
The first runnable example has a concrete contract: Example 1 returns one grouped row per `d`, `avg14`, and `sd14`, capped at 60 rows with columns `d`, `revenue`, `avg14`, `sd14`, `rolling_avg14`, and `rolling_sd14` from `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `d`, `revenue`, `rolling_avg14`, `rolling_sd14`, `z_score`, and `flag`. Independently group `orders`, `daily`, and `stats` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day57_project4_bi_part3.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
WITH daily AS (
  SELECT
    date_trunc('day', o.order_date)::date AS d,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
),
stats AS (
  -- Rolling 14-day window to compute z-score style anomaly score
  SELECT
    d,
    revenue,
    AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS avg14,
    STDDEV_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING) AS sd14
  FROM
    daily
)
SELECT
  d,
  ROUND(revenue, 2) AS revenue,
  ROUND(avg14, 2) AS rolling_avg14,
  ROUND(sd14, 2) AS rolling_sd14,
  CASE WHEN sd14 IS NULL
    OR sd14 = 0 THEN
    0
  ELSE
    ROUND((revenue - avg14) / sd14, 2)
  END AS z_score,
  CASE WHEN sd14 IS NOT NULL
    AND sd14 > 0
    AND ABS((revenue - avg14) / sd14) >= 3 THEN
    'anomaly'
  ELSE
    'normal'
  END AS flag
FROM
  stats
ORDER BY
  d DESC
LIMIT 60;
```

**How to read it:** Example 1: Start with `orders` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys; let each `OVER` expression calculate across related rows without collapsing them. The final `SELECT` displays `d`, `revenue`, `rolling_avg14`, `rolling_sd14`, `z_score`, and `flag`. `ORDER BY` determines presentation order and the final `LIMIT 60` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `d`, `avg14`, and `sd14`, capped at 60 rows with columns `d`, `revenue`, `avg14`, `sd14`, `rolling_avg14`, and `rolling_sd14` from `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
WITH daily AS (
  SELECT
    date_trunc('day', o.order_date)::date AS d,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
),
med AS (
  SELECT
    percentile_cont(0.5) WITHIN GROUP (ORDER BY revenue) AS median_rev
  FROM
    daily
),
dev AS (
  SELECT
    d.revenue,
    d.d,
    ABS(d.revenue - m.median_rev) AS abs_dev,
    m.median_rev
  FROM
    daily d
    CROSS JOIN med m
),
mad AS (
  SELECT
    percentile_cont(0.5) WITHIN GROUP (ORDER BY abs_dev) AS mad
  FROM
    dev
)
SELECT
  dev.d,
  ROUND(dev.revenue, 2) AS revenue,
  ROUND(dev.median_rev::numeric, 2) AS median_rev,
  CASE WHEN mad.mad = 0 THEN
    0
  ELSE
    ROUND((0.6745 * (dev.revenue - dev.median_rev) / mad.mad)::numeric, 2)
  END AS modified_z,
  CASE WHEN mad.mad > 0
    AND ABS(0.6745 * (dev.revenue - dev.median_rev) / mad.mad) >= 3.5 THEN
    'anomaly'
  ELSE
    'normal'
  END AS flag
FROM
  dev
  CROSS JOIN mad
ORDER BY
  dev.d DESC
LIMIT 60;
```

**How to read it:** Example 2: Start with `orders` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `d`, `revenue`, `median_rev`, `modified_z`, and `flag`. `ORDER BY` determines presentation order and the final `LIMIT 60` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `d`, `abs_dev`, and `mad`, capped at 60 rows with columns `d`, `revenue`, `median_rev`, `abs_dev`, `mad`, and `modified_z` from `orders`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

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
   **Inputs/evidence:** For sql-57 Exercise 1, read `orders` into a one-row-per-day calendar spine, calculate `ma7_forecast` and `seasonal_naive` in `forecasts`, and aggregate the final `model` and `mape`; the output grain is model, not order.
   **Expected result/shape:** For sql-57 Exercise 1, expected output: two model rows. Zero-revenue days are excluded from MAPE by `NULLIF`; disclose that choice. The final columns are `model`, and `mape`. The final order is `model`.
   **Verify:** For sql-57 Exercise 1, require exactly two rows with model values `MA(7)` and `seasonal naive (lag 7)` and require unique `model`. From the same `forecasts` rows and 180-day evaluation window, independently recompute each model's absolute percentage-error numerator and eligible denominator, compare the resulting `mape`, and disclose that zero-revenue days and NULL forecasts are excluded.
2. Rank positive/negative anomalies with SD and MAD scores.
   **Inputs/evidence:** For sql-57 Exercise 2, read from `orders`. Build the answer toward `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z`; keep `day` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-57 Exercise 2, expected output: up to ten positive and ten negative rows. The combined absolute score is a ranking heuristic; it is not a calibrated probability. The final columns are `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z`. The final order is `direction DESC, anomaly_rank`.
   **Verify:** For sql-57 Exercise 2, project `day` plus the raw source columns from `orders` at each join stage; record row count and distinct `day`, then assert the final `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z` values match those staged rows without unintended fanout or loss. Give two rows the same `direction DESC` value and different `anomaly_rank` values; verify `direction DESC, anomaly_rank` produces the intended rank and display order.
3. Predict how removing the date spine changes `LAG(..., 7)`.
   **Inputs/evidence:** For sql-57 Exercise 3, read from `orders`. Build the answer toward `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7`; keep `day` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-57 Exercise 3, expected output: at most 30 rows keyed by `day`. The final columns are `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7`. The final order is `c.day DESC`.
   **Verify:** For sql-57 Exercise 3, assert no more than 30 rows, no duplicate `day`, and no adjacent pair that violates `c.day DESC`. Rejoin the returned keys to `orders` to confirm `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7` came from the same source rows. Run with 30 minus one and 30 plus one eligible rows; require the output cap of 30 while retaining `c.day DESC`.
4. Compare MAE, RMSE, MAPE, and scored-row counts on one window.
   **Inputs/evidence:** For sql-57 Exercise 4, derive `common_scoring_rows` from `orders`, reshape both forecasts to `model_name` rows, and build `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows`; keep `model_name` as the final grouping key.
   **Expected result/shape:** For sql-57 Exercise 4, expected output: one row per `model_name`. The final columns are `model_name`, `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows`. The final order is `model_name`.
   **Verify:** For sql-57 Exercise 4, independently aggregate `common_scoring_rows` by `model_name` and require exactly two unique `model_name` rows. Require both models to have the same `scored_rows` and `zero_actual_rows` because they share one evaluation population; recompute `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows` for each model and compare every value, preserving NULL `mape` when the eligible percentage-error denominator is zero.
5. Detect and remove current-row forecast leakage.
   **Inputs/evidence:** For sql-57 Exercise 5, read from `orders`. Build the answer toward `day`, `revenue`, `leaky_window`, and `forecast_window`; keep `day` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-57 Exercise 5, expected output: at most 20 rows keyed by `day`. The final columns are `day`, `revenue`, `leaky_window`, and `forecast_window`. The final order is `day DESC`.
   **Verify:** For sql-57 Exercise 5, assert no more than 20 rows, no duplicate `day`, and no adjacent pair that violates `day DESC`. Rejoin the returned keys to `orders` to confirm `day`, `revenue`, `leaky_window`, and `forecast_window` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `day DESC`.
6. Preserve undefined scores for a constant series.
   **Inputs/evidence:** For sql-57 Exercise 6, read from `constant`. Build the answer toward `day`, `revenue`, `sd_z`, and `modified_mad_z`; keep `day` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-57 Exercise 6, expected output: one row per `day`. The final columns are `day`, `revenue`, `sd_z`, and `modified_mad_z`. The final order is `d.day`.
   **Verify:** For sql-57 Exercise 6, project `day` plus the raw source columns from `constant` at each join stage; record row count and distinct `day`, then assert the final `day`, `revenue`, `sd_z`, and `modified_mad_z` values match those staged rows without unintended fanout or loss. Add one source row with a new `day`; verify the result gains exactly one row carrying that `day` value.

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

Continue to [Day 58; capstone ingestion and data quality](day58_final_capstone_part1.md).

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

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-57 — Project4 BI Part3.

I have completed the direct catalog prerequisite: `sql-56`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day57_project4_bi_part3.md
- Answer-free learner SQL: sql/postgres-60day/day57_project4_bi_part3.sql

Key terms to teach in context: Seasonal naive, MAD, Anomaly candidate. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Build a complete daily spine before LAG(revenue, 7) so the offset means seven calendar days. Calculate a trailing forecast that excludes the current actual, then score the same six-month rows. For anomaly output, retain raw revenue, center, dispersion, and both scores beside the rank.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
