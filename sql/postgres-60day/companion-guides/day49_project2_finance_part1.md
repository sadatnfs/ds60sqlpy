# Day 49: Finance/Operations Project, Part 1: Revenue Forecasting

## How to run this lesson

Open **sql-49** in `./classroom`, pick PostgreSQL and run it as a
**Whole SQL lesson (psql)**. Your editable copy lives at
`.learning/sql/sql-49/lesson/workspace/sql/postgres-60day/day49_project2_finance_part1.sql`.
The file only reads `orders` in `advanced_sql_training`, wrapped in `BEGIN`
and `ROLLBACK`. `psql` prints four results: 24 months of revenue (newest
first), 36 months with year-over-year growth, three future months copied from
last year and a six-row trailing average. Order dates are generated relative
to the moment the fixture loaded, so the newest month is always a partial one.
Launcher details are in the
[study guide](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom), and the
notebook alternative is in its
[contributor notebook section](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 48; affinity and attribution](day48_project1_ecommerce_part3.md) Day 48 was mostly joins between purchases and touches; here the joins fade and window frames take over, so be ready to say which rows `ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING` covers before you run anything.
- **Artifacts:** [learner SQL](../day49_project2_finance_part1.sql) ·
  [solution reasoning](../solutions/day49_solutions.md) ·
  [executable solution](../solutions/day49_solutions.sql)

## A beginner's mental model for this lesson

Every query today first squeezes `orders` into one row per month. On a fresh
load the fixture has 46 months, February 2023 through November 2026, with no
empty month, and revenue climbs steeply: 1,203.26 in the first month and
170,179.13 in October 2026. The last month stops at the final order date, so
it shows only 85,364.67 and looks like a collapse that never happened.

A **backtest** replays history. For each past month, build the forecast you
could have made at the start of that month, then compare it with what came
in. Two rules keep it honest. The averaging frame must stop at `1 PRECEDING`,
because a frame reaching `CURRENT ROW` puts the month's own revenue into its
forecast, which is **target leakage**. And every model must be graded on the
same months: MA(12) and a 12-month seasonal naive need a year of warm-up that
MA(6) does not.

**MAPE** (mean absolute percentage error) averages
`|actual - forecast| / actual`. It reads as "off by 23% on average", but it
cannot divide by a zero month, and on a growing series it punishes any model
that looks far back. Read each CTE in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order)
and note its row count before moving on.

## Two worked SQL examples

Both excerpts are the opening queries of the learner script. They describe
the series; neither one forecasts or scores anything yet.

### Example 1

```sql
WITH monthly AS (
  SELECT
    date_trunc('month', o.order_date)::date AS month,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
)
SELECT
  *
FROM
  monthly
ORDER BY
  month DESC
LIMIT 24;
```

**How to read it:** `monthly` truncates each `order_date` to the first of its month and sums
`total_amount`, so 4,362 orders become 46 rows. The outer query only sorts
them newest first and keeps 24; `SELECT *` exposes exactly the two CTE
columns.

**Expected result/shape:** 24 rows of `month` and `revenue`, from 2026-11-01 (85,364.67, partial on a
fresh load) back to 2024-12-01 (35,551.24). October 2026, at 170,179.13, is
the real peak. No `NULL` can appear, because every month in the window has
orders.

### Example 2

```sql
WITH monthly AS (
  SELECT
    date_trunc('month', o.order_date)::date AS month,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
)
SELECT
  m.month,
  m.revenue,
  LAG(m.revenue, 12) OVER (ORDER BY m.month) AS prev_year,
  ROUND((m.revenue - COALESCE(LAG(m.revenue, 12) OVER (ORDER BY m.month), 0)) / NULLIF (LAG(m.revenue, 12) OVER (ORDER BY m.month), 0), 4) AS yoy_growth
FROM
  monthly m
ORDER BY
  m.month DESC
LIMIT 36;
```

**How to read it:** The same `monthly` CTE feeds a window. `LAG(m.revenue, 12) OVER (ORDER BY
m.month)` reads the row twelve positions earlier, which is the same calendar
month last year only because no month is missing. `yoy_growth` divides the
change by `NULLIF` of that lagged value; when the lag is `NULL` the ratio is
`NULL`, whatever the `COALESCE` in the numerator does.

**Expected result/shape:** 36 rows from 2026-11-01 back to 2023-12-01 with `month`, `revenue`,
`prev_year` and `yoy_growth`. The two oldest rows, December 2023 and January
2024, have no `prev_year` and so no growth. October 2026 grew 1.5790 over
October 2025, while the partial November shows just 0.0455: a truncation
artifact, not a slowdown.

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
   **Data check:** Expect 34 `scored_rows` per model, covering 2024-02 to 2026-11 on a fresh load, and `zero_actual_rows` 0. MAPE: MA(6) 0.2281, MA(12) 0.3636, the blend 0.4136 and seasonal naive 0.6027. Seasonal naive lands below the actual in all 34 months because revenue keeps climbing; it ranks last for being a year stale, not for being noisy.
2. Produce a 50/50 seasonal/MA(6) forecast.
   **Inputs/evidence:** For sql-49 Exercise 2, aggregate `orders` into 46 calendar months in `monthly`, then in `forecasted` add `LAG(revenue, 12)` as `seasonal_naive` and `AVG(revenue)` over `ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING` as `ma6_forecast`, and blend them 50/50 for every month that has a value a year earlier.
   **Expected result/shape:** For sql-49 Exercise 2, expected output: 34 rows, one per `month` from 2024-02-01 to 2026-11-01, with columns `month`, `actual`, `seasonal_naive`, `ma6_forecast`, and `blended_forecast`, ordered by `month DESC`, so the partial current month comes first.
   **Verify:** For sql-49 Exercise 2, confirm 34 distinct months and that `forecasted` holds exactly 12 rows with a `NULL` `seasonal_naive` (2023-02 to 2024-01), which the `WHERE` removes. Recompute the oldest row by hand: 2024-02 has `actual` 14,823.22, `seasonal_naive` 1,203.26 from 2023-02, `ma6_forecast` 11,859.69 (the mean of 2023-08 to 2024-01), and `blended_forecast` 6,531.47, their average. Then, in a transaction, delete the 91 orders from 2025-03, rerun, and confirm 33 rows and that 2026-03 now takes 33,302.51 from 2025-02 as its "seasonal" value, a 13-month lag; `ROLLBACK`.
   **Data check:** `forecasted` holds 46 months and the query returns 34; the 12 oldest months (2023-02 to 2024-01) have a `NULL` `seasonal_naive` and drop out because nothing exists a year before them. The oldest row is the easiest to check by hand: 2024-02-01 has actual 14,823.22, seasonal 1,203.26, MA(6) 11,859.69 and blend 6,531.47. For October 2026 the blend gives about 97,200 against an actual of 170,179.13; the late months shift slightly between loads.
3. Explain and remove current-row leakage.
   **Inputs/evidence:** For sql-49 Exercise 3, aggregate `orders` into 46 calendar months in `monthly` and compute two six-month averages over the same `ORDER BY month` window: `leaky_ma6` with `ROWS BETWEEN 5 PRECEDING AND CURRENT ROW`, and `honest_ma6` with `ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING`.
   **Expected result/shape:** For sql-49 Exercise 3, expected output: 46 rows, one per `month` from 2023-02-01 to 2026-11-01, with columns `month`, `revenue`, `leaky_ma6`, and `honest_ma6`, ordered by `month`; only the first row has a `NULL` `honest_ma6`.
   **Verify:** For sql-49 Exercise 3, recompute the first three months by hand: 2023-02 has `leaky_ma6` 1,203.26 (its own revenue) and `honest_ma6` `NULL`; 2023-03 has 1,503.345 and 1,203.26; 2023-04 has 2,197.18 and 1,503.345. Then confirm with `LAG(leaky_ma6) OVER (ORDER BY month)` that every row's `honest_ma6` equals the previous row's `leaky_ma6` (0 mismatches over 46 rows), which shows the leaky forecast for a month is the honest one shifted to include the month being forecast. There is no `PARTITION BY`, so there is no partition reset to test; the frame first holds six rows at 2023-07 (leaky) and 2023-08 (honest).
   **Data check:** 46 rows. In the first row (2023-02-01) `leaky_ma6` equals the revenue, 1,203.26, and `honest_ma6` is `NULL`. After that, each month's `leaky_ma6` reappears as the next month's `honest_ma6`: 1,503.345 is leaky for March 2023 and honest for April. Graded on the 34 common months, the leaky frame scores a MAPE of 0.1696 against the honest 0.2281.
4. Build a complete monthly spine before lagging 12 months.
   **Inputs/evidence:** For sql-49 Exercise 4, take the first and last order months from `orders` in `bounds`, build every calendar month between them with `generate_series` in `spine`, `LEFT JOIN` the monthly revenue in `actual` to it in `complete`, and apply `LAG(revenue, 12)` to the spine rather than to the observed months.
   **Expected result/shape:** For sql-49 Exercise 4, expected output: 46 rows, one per calendar `month` from 2023-02-01 to 2026-11-01, with columns `month`, `revenue`, `had_source_rows`, and `seasonal_forecast`, ordered by `month`; `seasonal_forecast` is `NULL` for the first 12 months.
   **Verify:** For sql-49 Exercise 4, confirm `had_source_rows` is true on all 46 rows today and that 2024-02 takes 1,203.26 from 2023-02. Then, in a transaction, delete the 91 orders from 2025-03 and rerun: the spine still has 46 rows, 2025-03 shows `revenue` `NULL` and `had_source_rows` false, 2026-03 gets a `NULL` `seasonal_forecast` instead of February's 33,302.51, and `ROLLBACK`. Repeat with `UPDATE ... SET total_amount = 0` for those orders instead: 2025-03 shows `revenue` 0.00 with `had_source_rows` true, and 2026-03 gets 0.00.
   **Data check:** 46 rows, and `had_source_rows` is true on every one because the fixture has orders in every month; the spine changes nothing today but protects the lag once a month goes missing. `seasonal_forecast` is `NULL` for the first 12 months, then 2024-02 receives 1,203.26 from 2023-02 and the last row receives 81,650.05.
5. Handle zero actuals and report excluded MAPE rows.
   **Inputs/evidence:** For sql-49 Exercise 5, use the `toy` `VALUES` fixture `(100, 90), (0, 10), (50, 60)` of `actual` and `forecast` and compute MAPE as `AVG(ABS(actual - forecast) / NULLIF(actual, 0))`, counting scored rows and excluded zero actuals.
   **Expected result/shape:** For sql-49 Exercise 5, expected output: one row with `mape` 0.1500, `scored_rows` 2, and `excluded_zero_actuals` 1. The final columns are `mape`, `scored_rows`, and `excluded_zero_actuals`.
   **Verify:** For sql-49 Exercise 5, confirm by hand that the two scored errors are 10/100 = 0.10 and 10/50 = 0.20, whose mean is 0.15, and that the zero-actual row adds nothing because `NULLIF(actual, 0)` makes its ratio NULL, which `AVG` skips.
   **Data check:** Listed per row, the ratios are 0.10, `NULL` and 0.20. Change the middle row to `(1, 10)` and it becomes a scored row with an error ratio of 9.00, pushing MAPE to 3.1000: a tiny actual is almost as hazardous as a zero one, and no `NULLIF` protects you from it.
6. Compare MAE with MAPE on a low-revenue miss.
   **Inputs/evidence:** For sql-49 Exercise 6, use the `toy` fixture `(1000, 900), (10, 20)` and compute MAE, `AVG(ABS(actual - forecast))`, and MAPE, `AVG(ABS(actual - forecast) / NULLIF(actual, 0))`.
   **Expected result/shape:** For sql-49 Exercise 6, expected output: one row with `mae` 55 and `mape` 0.55. The final columns are `mae` and `mape`.
   **Verify:** For sql-49 Exercise 6, confirm by hand that the absolute errors are 100 and 10 (mean 55) and the percentage errors are 0.10 and 1.00 (mean 0.55); the output shows that the small month's modest miss dominates MAPE, while the large month dominates MAE.
   **Data check:** Swap the small row to `(10, 15)`: MAE falls to 52.5 and MAPE to 0.30, although the large month's 100-unit miss is unchanged. One 5-unit improvement moved MAPE by almost half, which is the sensitivity Exercise 1's early, low-revenue months bring into its scores.

Score every model on a common observation window.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Return forecast and actual side by side.
  A MAPE alone hides direction. Exercise 2's columns show seasonal naive under
  the actual in every scored month, which a single 0.6027 never reveals.
- **Reading a partial month as a drop:** on a fresh load November 2026 ends at
  the last order date. That month alone gives MA(6) an error of 0.6555, and
  leaving it out moves MA(6)'s MAPE from 0.2281 to 0.2151. Decide which months
  are complete before grading them.
- **A frame that contains the target:** `ROWS BETWEEN 5 PRECEDING AND CURRENT
  ROW` still spans six months, but one of them is the answer. Its 0.1696 is
  not an improvement.
- **Grading models on different months:** score MA(6) wherever it has six
  months of history and it covers 40 months at 0.2519; on the common 34 it
  is 0.2281. Only the second can sit beside MA(12).
- **Lagging over gaps:** `LAG(revenue, 12)` counts rows. Build the month
  spine first, as Exercise 4 does, or one missing month shifts a whole year of
  seasonal forecasts.
- Generic diagnosis steps live in the study guide's
  [recovery section](../../STUDY-GUIDE.md#recover-from-common-failures).

## Self-check

- Does every forecast exclude its current actual?
- Are model errors compared over the same months, with excluded zero actuals
  and warm-up periods reported?

## Next step

Continue to [Day 50; budget variance](day50_project2_finance_part2.md).

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

Exercise 1 is the full backtest and Exercise 2 its month-by-month view.
Exercises 3 and 4 isolate the two rules that backtest depends on (no leakage,
a complete calendar), and Exercises 5 and 6 use tiny `VALUES` sets to show
where MAPE misleads. The learner file carries the same numbered prompts, each
with a first hint.

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

## Ask an AI tutor about this lesson

A tutor helps most here when it checks your reasoning instead of producing
numbers. Explain to it why the leaky frame scores better, or why seasonal
naive loses on this fixture, and ask it to find the gap in your explanation.
Keep every MAPE and row count from your own `psql` run; the
[tutor notes in the study guide](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)
say what to paste. Start from this prompt:

```text
Tutor me through sql-49: Finance Project, Part 1: Revenue Forecasting.

I have completed the direct catalog prerequisite: `sql-48`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day49_project2_finance_part1.md
- Answer-free learner SQL: sql/postgres-60day/day49_project2_finance_part1.sql

Key terms to teach in context: Backtest, Target leakage, MAPE. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: At complete monthly grain, compute MA(6) with a frame ending at `1 PRECEDING`, place it beside actual revenue, and score only months with a forecast and nonzero actual. Compare seasonal naive on that same scoring set and retain the number of evaluated months.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
