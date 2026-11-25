# Day 57: Complex BI Project, Part 3: Trends and Anomalies

## How to run this lesson

Open **sql-57** from `./classroom` (PostgreSQL), choose **Whole SQL lesson
(psql)** and edit
`.learning/sql/sql-57/lesson/workspace/sql/postgres-60day/day57_project4_bi_part3.sql`.
The script reads `orders` in `advanced_sql_training` between `BEGIN` and
`ROLLBACK`. A `psql` run prints three tables, newest day first: 60 rows of a
rolling 14-day z-score, 60 rows of a whole-history MAD score and 30 rows of a
moving-average forecast with its absolute percentage error (`ape`). Order
dates are generated relative to load time, so the exact days shift with each
fresh load, and a load at another time of day moves a few orders across
midnight. Day-level figures below (observed days, daily revenue, scores and
error rates) come from one load checked on 2026-11-25, so yours may differ
slightly; the row counts, shapes and equalities hold on any load. Launcher steps are in the
[study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom), and the
optional notebook is described in its
[notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 56; percentiles and CUBE](day56_project4_bi_part2.md) Day 56's percentile work carries over: the MAD score in this lesson is a median of distances from a median, both taken with `percentile_cont(0.5)`.
- **Artifacts:** [learner SQL](../day57_project4_bi_part3.sql) ·
  [solution reasoning](../solutions/day57_solutions.md) ·
  [executable solution](../solutions/day57_solutions.sql)

## A beginner's mental model for this lesson

Every query here starts by collapsing `orders` into daily revenue. On the checked
load the orders cover 1,380 calendar days, but only 1,081 of them have any
orders; the other 299 empty days all fall before mid-December 2025. That gap
decides what "seven days ago" means. `LAG(revenue, 7)` over the 1,081 observed
rows looks back seven rows, which in the sparse early period can be weeks. Over
a full calendar spine with zeros it looks back seven days, which is what a
**seasonal naive** forecast (repeat last week's same weekday) needs.

The second idea is honesty about time. A forecast for a day may only use days
before it, so moving-average frames end at `1 PRECEDING`. Ending at
`CURRENT ROW` lets the day's own revenue into its forecast and makes the error
look roughly one seventh smaller than it really is.

The third idea is scoring unusual days. A z-score divides the distance from the
mean by the standard deviation; **MAD** (median absolute deviation) replaces
both with medians, so one day above 9,700 barely moves the baseline. A high score
makes a day an **anomaly candidate** to investigate, nothing more. Trace each
CTE in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order).

## Two worked SQL examples

Both excerpts are the first two queries of the learner script; neither uses a
calendar spine.

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

**How to read it:** `daily` sums `total_amount` per order date, giving one row per day that had
orders. `stats` attaches the mean and sample standard deviation of the 14
previous observed days to each day, so the baseline moves with the series.
The final `SELECT` divides the day's distance from that mean by the standard
deviation and labels the day `anomaly` when the result reaches 3 in either
direction.

**Expected result/shape:** 60 rows from the last order date backward, with columns `d`, `revenue`,
`rolling_avg14`, `rolling_sd14`, `z_score` and `flag`. None of the 60 recent
days is flagged; across all 1,081 days, 21 are. The very first two days have
no usable standard deviation, and the `CASE` prints their `z_score` as 0.

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

**How to read it:** `med` takes one median over every observed day since February 2023, `dev`
measures each day's absolute distance from it, and `mad` takes the median of
those distances. The modified score `0.6745 * (revenue - median) / MAD`
flags a day at 3.5 or more. The baseline is one global value, not a rolling
one.

**Expected result/shape:** 60 rows with columns `d`, `revenue`, `median_rev`, `modified_z` and `flag`.
Every row shows the same `median_rev`, 1,696.88 on the checked load, with a
MAD of 1,032.07. Seven of the 60 recent days are flagged, all of them busy
days between late September and early November 2026.

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
   **Expected result/shape:** For sql-57 Exercise 1, expected output: two model rows. Zero-revenue days are excluded from MAPE by `NULLIF`; disclose that choice. The final columns are `model` and `mape`. The final order is `model`.
   **Verify:** For sql-57 Exercise 1, require exactly two rows with model values `MA(7)` and `seasonal naive (lag 7)` and require unique `model`. Count the `forecasts` rows with `day >= CURRENT_DATE - 180` and a non-NULL forecast for each model (the same 179 days from 2026-05-29 on a run dated 2026-11-25, none with revenue 0) and recompute each `mape` as the average of `ABS(revenue - forecast) / revenue` over them (0.4289 and 0.5329 on the checked load). Then replace `CURRENT_DATE` with `date '2027-06-01'`: no day qualifies, and both model rows still print with `mape` NULL.
   **Data check:** On a run dated 2026-11-25, the window starts 2026-05-29 and each model scores 179 days: MA(7) gets 0.4289 and the seasonal naive 0.5329. No day in that window has zero revenue, so `NULLIF` drops nothing. The window start follows `CURRENT_DATE`, so the values drift a little from one day to the next.
2. Rank positive/negative anomalies with SD and MAD scores.
   **Inputs/evidence:** For sql-57 Exercise 2, read the `orders` placed since `CURRENT_TIMESTAMP - interval '6 months'`, sum `total_amount` per order day in `daily`, take one mean, sample SD, median and MAD over those days, and score each day with `sd_z` and `modified_z`; `direction` records the day's side of the mean and `anomaly_rank` numbers the days within it.
   **Expected result/shape:** For sql-57 Exercise 2, expected output: 20 rows, ten `positive` and ten `negative`, each side ranked 1 to 10 (a side with fewer than ten days would return fewer). The combined absolute score is a ranking heuristic; it is not a calibrated probability. The final columns are `direction`, `anomaly_rank`, `day`, `revenue`, `sd_z`, and `modified_z`. The final order is `direction DESC, anomaly_rank`.
   **Verify:** For sql-57 Exercise 2, confirm 20 rows and that `daily` holds 183 days (89 at or above the mean of 4,640.09 and 94 below on the checked load). Both scores are straight-line functions of revenue, so the `positive` list must equal the ten highest-revenue days and the `negative` list the ten lowest; check both with `ORDER BY revenue`. Then move the cutoff to `date_trunc('day', CURRENT_TIMESTAMP) - interval '6 months'`: the partial oldest day 2026-05-25 gets its full 3,758.33 instead of 1,446.62 and leaves the negative list.
   **Data check:** The six-month window holds 183 days: 89 at or above the mean of 4,640.09 and 94 below. Positive rank 1 is 2026-09-22, with 9,722.82 from 15 orders. Negative rank 1 is 2026-06-06 with 560.49 and rank 2 is 2026-08-15 with 650.99; ranks 3 to 5 are the fixture's last three days, which have only one or two orders each.
3. Predict how removing the date spine changes `LAG(..., 7)`.
   **Inputs/evidence:** For sql-57 Exercise 3, read `orders` twice: `observed_daily` sums revenue only for days that have orders, and `calendar_daily` left-joins those sums onto a `generate_series` spine from `bounds`, with 0 for empty days; apply `LAG(revenue, 7)` to each and join the two by `day`.
   **Expected result/shape:** For sql-57 Exercise 3, expected output: 30 rows, one per calendar `day`, newest first. The final columns are `day`, `revenue`, `observed_row_lag7`, and `calendar_day_lag7`. The final order is `c.day DESC`.
   **Verify:** For sql-57 Exercise 3, confirm 30 rows from the last order day back (2026-11-23 to 2026-10-25 on the checked load) with `observed_row_lag7` equal to `calendar_day_lag7` on every row, because no recent day is empty. Remove `LIMIT 30` and count the rows where the lags are `IS DISTINCT FROM` each other: on the checked load 728 of the 1,380 dates, the last on 2025-12-13, made of 435 observed days whose seventh earlier row is not seven days back and 293 empty spine days whose `observed_row_lag7` is NULL.
   **Data check:** All 30 rows show the same value in both lag columns, because every day since 2025-12-07 has orders. Drop the `LIMIT` and look before 2025-12-14 instead: 435 of the 1,081 observed days get a different seven-back value, and the 299 empty days appear only on the spine.
4. Compare MAE, RMSE, MAPE, and scored-row counts on one window.
   **Inputs/evidence:** For sql-57 Exercise 4, derive `calendar_daily` (one row per date, 0 for days without orders) and `forecasts` from `orders`, keep the last 181 days on which both `ma7` and `seasonal_naive` exist, reshape the two forecasts with `LATERAL VALUES` into `common_scoring_rows` keyed by `day` and `model_name`, and build `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows` for each model.
   **Expected result/shape:** For sql-57 Exercise 4, expected output: one row per `model_name`. That gives 2 rows, `MA(7)` and `seasonal naive`, each with 181 `scored_rows` and 0 `zero_actual_rows`; on the checked load MA(7) has MAE 1,340.94, RMSE 1,695.59, and MAPE 0.4284 against 1,715.92, 2,157.43, and 0.5349 for seasonal naive. The final columns are `model_name`, `scored_rows`, `mae`, `rmse`, `mape`, and `zero_actual_rows`. The final order is `model_name`.
   **Verify:** For sql-57 Exercise 4, group `common_scoring_rows` by `model_name` yourself: it holds 362 rows, 181 per model over the same dates, so `scored_rows` and `zero_actual_rows` must match between the models; recompute `mae` as `ROUND(AVG(ABS(error)), 2)`, `rmse` as `ROUND(SQRT(AVG(POWER(error, 2))), 2)`, and `mape` with `NULLIF(actual, 0)`, and compare every value. In a rolled-back transaction delete the orders of the day 30 days before the last order day (15 orders on 2026-10-24 on the checked load): both models keep 181 `scored_rows`, `zero_actual_rows` becomes 1, and `mape` now averages only the 180 nonzero days (0.4268 and 0.5400).
   **Data check:** Expect 181 `scored_rows` for each model and `zero_actual_rows` 0. MA(7) wins on every measure: MAE 1,340.94 against 1,715.92, RMSE 1,695.59 against 2,157.43 and MAPE 0.4284 against 0.5349 on the checked load. This window ends at the last order date rather than today, so reruns on later days return the same numbers.
5. Detect and remove current-row forecast leakage.
   **Inputs/evidence:** For sql-57 Exercise 5, read `orders`, sum `total_amount` per observed order day in `daily` (no calendar spine), and compute two seven-row averages over `ORDER BY day`: `leaky_window` ends at `CURRENT ROW` and `forecast_window` ends at `1 PRECEDING`.
   **Expected result/shape:** For sql-57 Exercise 5, expected output: 20 rows, one per observed order `day`, newest first. The final columns are `day`, `revenue`, `leaky_window`, and `forecast_window`. The final order is `day DESC`.
   **Verify:** For sql-57 Exercise 5, confirm 20 rows ending at the last order day (2026-11-23 back to 2026-11-04 on the checked load) and that every `leaky_window` equals the `forecast_window` printed one row above it; recompute the newest `forecast_window` as the plain average of the seven previous days' revenue (2,300.43 on the checked load). Then, in a rolled-back transaction, add 700 to the `total_amount` of the newest day's only order: its `leaky_window` rises by exactly 100, from 2,079.31 to 2,179.31, while its `forecast_window` stays 2,300.43.
   **Data check:** The 20 rows run from 2026-11-23 back to 2026-11-04. Each `leaky_window` equals the `forecast_window` printed one row higher, which is the next day's honest forecast: 2,300.43 is the leaky value for 2026-11-22 and the honest forecast for 2026-11-23.
6. Preserve undefined scores for a constant series.
   **Inputs/evidence:** For sql-57 Exercise 6, read only the three-row `VALUES` fixture `constant` (revenue 100 on 2026-01-01, 2026-01-02 and 2026-01-03); `center` takes its median, mean and sample SD, `deviations` measures each day's distance from the median, and `dispersion` takes the MAD.
   **Expected result/shape:** For sql-57 Exercise 6, expected output: three rows, one per fixture `day`, each with revenue 100 and both scores NULL. The final columns are `day`, `revenue`, `sd_z`, and `modified_mad_z`. The final order is `d.day`.
   **Verify:** For sql-57 Exercise 6, confirm 3 rows with NULL `sd_z` and `modified_mad_z`, `center` showing SD 0 and `dispersion` showing MAD 0. Append `(date '2026-01-04', 101)`: `sd_z` becomes -0.5 for the three old days and 1.5 for the new one, while `modified_mad_z` stays NULL because three of the four deviations are 0. Make the values 100, 100, 101 and 101 and both scores are defined: `sd_z` is -0.8660 or 0.8660 and `modified_mad_z` -0.6745 or 0.6745.
   **Data check:** Three rows dated 2026-01-01 to 2026-01-03, each with revenue 100 and both scores `NULL`. Append a fourth value of 101 and `sd_z` becomes defined (-0.5 for the old rows, 1.5 for the new one), while `modified_mad_z` stays `NULL`: three of four deviations are still 0, so their median is 0 too.

Compare absent no-order days with explicit zero-revenue days.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Guard zero standard deviation and zero MAD with `NULLIF`.
  The learner examples use a `CASE` that prints 0 instead, which reads as
  "perfectly normal" for the first two days of Example 1; Exercise 6 keeps the
  score `NULL`.
- **A forecast that knows the answer:** a frame ending at `CURRENT ROW` cuts
  MA(7)'s MAPE from 0.4284 to 0.3696 on the 181-day window. Every forecast
  frame should end at `1 PRECEDING`.
- **Lag over gaps:** before mid-December 2025, `LAG(revenue, 7)` over observed
  days can reach back weeks. Build the `generate_series` spine first.
- **A global baseline over a growing series:** monthly revenue rose from about
  1,200 in early 2023 to 170,179 in October 2026, so Example 2's all-history
  median flags only recent busy days. All 20 of its flags on the checked load are
  high days from 2025-11-28 onward.
- **Different rows per model:** score both models on dates where both
  forecasts exist, as Exercise 4 does, or their errors are not comparable.
- The study guide has general
  [recovery steps](../../STUDY-GUIDE.md#recover-from-common-failures).

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

Exercises 1, 4 and 5 measure forecast error and how a frame can cheat it, Exercise 3 shows what the calendar spine changes, and Exercises 2 and 6 deal
with anomaly scores, including the case where no score can be computed. The
learner file repeats each numbered prompt verbatim.

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

For this lesson a tutor is most useful as a questioner: have it ask why the
`0.6745` factor appears or which rows `1 PRECEDING` excludes, and answer from
your own output. Your MAPE values and anomaly dates should come from `psql`,
not the chat. The
[tutor section of the study guide](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)
lists what to share. The prompt:

```text
Tutor me through sql-57: BI Project, Part 3: Trends and Anomalies.

I have completed the direct catalog prerequisite: `sql-56`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day57_project4_bi_part3.md
- Answer-free learner SQL: sql/postgres-60day/day57_project4_bi_part3.sql

Key terms to teach in context: Seasonal naive, MAD, Anomaly candidate. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Build a complete daily spine before `LAG(revenue, 7)` so the offset means seven calendar days. Calculate a trailing forecast that excludes the current actual, then score the same six-month rows. For anomaly output, retain raw revenue, center, dispersion, and both scores beside the rank.

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
