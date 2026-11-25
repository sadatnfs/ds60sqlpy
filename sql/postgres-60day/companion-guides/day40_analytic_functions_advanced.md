# Day 40: Advanced Analytic Functions

## How to run this lesson

Start `./classroom`, pick **sql-40** and run **Whole SQL lesson (psql)**.
The learner file opens a transaction, prints three read-only result sets
(60 daily rolling-statistics rows, 12 monthly percentile rows and 6
category shares) and rolls back. Your editable copy is
`.learning/sql/sql-40/lesson/workspace/sql/postgres-60day/day40_analytic_functions_advanced.sql`,
and it runs against `advanced_sql_training`. Launch details are in
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

The dates you see depend on when your database was loaded, because the seed
places orders relative to the load time. The figures quoted below come from
a late-2026 load; compare shapes and relationships, not the exact dates.

### Optional contributor notebook route

A notebook is convenient here for plotting the z-score series next to the
raw daily revenue
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-40
```

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisite:** `sql-found-02`
- **Prerequisites:** Complete
  [SQL-FOUND-02; versioned schema migrations](../../professional/companion-guides/sql_found_02_versioned_migrations.md).
  That route already includes the window-function sequence from Days 16-22 and
  the transaction/locking sequence through SQL-39.
- **Artifacts:** [learner SQL](../day40_analytic_functions_advanced.sql) ·
  [solution reasoning](../solutions/day40_solutions.md) ·
  [executable solution](../solutions/day40_solutions.sql)

## A beginner's mental model for this lesson

The learner file asks three questions of the same order data, each at its
own grain. The first collapses the 4,362 orders into one revenue figure per
order day and slides a 15-row frame along that series. The second keeps
every order and groups them by month, so each percentile sees that month's
individual totals. The third sums line revenue per category and divides
each sum by the grand total from an empty `OVER ()`.

A **z-score** answers "how unusual is this day?" as
`(revenue - avg15) / sd15`, and it is only as good as its frame.
`ROWS BETWEEN 14 PRECEDING AND CURRENT ROW` counts the 14 previous *order
days*, not calendar days. Early in the series orders are sparse: on a
late-2026 load the first 15 order days stretch across 99 calendar days, so
a "15-day" window there really covers more than three months.
`STDDEV_SAMP` and `VAR_SAMP` divide by n - 1, so `var15` is `sd15` squared
up to rounding; `STDDEV_POP` and `VAR_POP` divide by n, and mixing the two
families makes the columns disagree.

An **ordered-set aggregate** such as
`PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY amt)` sorts a group's values
and reads a position from that order. The continuous version uses
**interpolation** between neighbors, so a median can be a value no order
has, while `PERCENTILE_DISC` always returns one that exists.

## Two worked SQL examples

### Example 1

```sql
WITH daily AS (
  SELECT
    date_trunc('day', o.order_date) AS d,
    SUM(o.total_amount) AS revenue
  FROM
    orders o
  GROUP BY
    1
)
SELECT
  d,
  revenue,
  ROUND(AVG(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW), 2) AS ma15,
  ROUND(STDDEV_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW), 2) AS sd15,
  ROUND(VAR_SAMP(revenue) OVER (ORDER BY d ROWS BETWEEN 14 PRECEDING AND CURRENT ROW), 2) AS var15
FROM
  daily
ORDER BY
  d DESC
LIMIT 60;
```

**How to read it:** `daily` turns the orders into one row per calendar
day that has orders. All three window calls share one frame, the current day
plus the 14 order days before it, so the mean, deviation and variance always
describe the same rows; a `WINDOW w AS (...)` clause could name that frame
once. The windows are computed over the whole ascending series before the
outer `ORDER BY d DESC LIMIT 60` keeps the newest 60 rows, so even the
oldest displayed day still has 14 predecessors in its frame.

**Expected result/shape:** 60 rows, newest first. On a late-2026 load
the top row is 2026-11-23 with `revenue` 742.14, `ma15` 3245.49 and `sd15`
1724.57. `d` prints as `2026-11-23 00:00:00+00` because `date_trunc` on a
`timestamptz` keeps that type. `var15` reads 2974133.16, a little off
1724.57 squared (2974141.68), because the two columns are rounded
separately from unrounded values. No statistic is NULL, since every
displayed date has a full 15-row frame. The newest date is the load day
itself, so its revenue may be partial.

### Example 2

```sql
WITH monthly AS (
  SELECT
    date_trunc('month', o.order_date) AS m,
    o.total_amount AS amt
  FROM
    orders o
)
SELECT
  m,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amt) AS p50,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY amt) AS p90,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY amt) AS p99
FROM
  monthly
GROUP BY
  m
ORDER BY
  m DESC
LIMIT 12;
```

**How to read it:** `monthly` does no aggregation; it only labels each
order with the first day of its month. `GROUP BY m` then hands each month's
`amt` values to three ordered-set aggregates, each of which sorts them with
`WITHIN GROUP (ORDER BY amt)` and reads the 50th, 90th and 99th percentile
positions. There is no `OVER` here: unlike Example 1's windows, these
aggregates collapse a month to a single row.

**Expected result/shape:** 12 rows, one per month, newest first, with
columns `m`, `p50`, `p90` and `p99`. On a late-2026 load they run from
November 2026, a partial month of 151 orders, back to December 2025. Some
values print with float noise, such as October's `p90` of
944.6360000000001, because `PERCENTILE_CONT` returns `double precision`;
the exercises cast to `numeric` before `ROUND` for that reason. Every row
should satisfy `p50 <= p90 <= p99`.

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
   **Inputs/evidence:** For sql-40 Exercise 1, read from `orders`, sum `total_amount` per UTC day in the CTE `daily`, then compute a trailing 15-row mean and sample standard deviation (`ROWS BETWEEN 14 PRECEDING AND CURRENT ROW`) in `rolling` and the z-score `(revenue - avg15) / NULLIF(sd15, 0)`.
   **Expected result/shape:** For sql-40 Exercise 1, expected output: 1,080 rows on this load, one per UTC day with orders from 2023-02-13 to 2026-11-23; the second row, 2023-03-07, has `revenue` 1,034.00 against `avg15` 1,118.63 and `z_score` -0.7071. A positive z-score is above the rolling mean; a negative score is below it. The final columns are `order_day`, `revenue`, `avg15`, `sd15`, and `z_score`. The final order is `order_day`.
   **Verify:** For sql-40 Exercise 1, confirm one row per `order_day`, so the row count equals `SELECT COUNT(DISTINCT date_trunc('day', order_date)) FROM orders`; the first row has NULL `sd15` and `z_score` because a one-row sample has no standard deviation, and for one later day recompute `avg15` as the mean of that day's and the 14 previous days' `revenue` in `daily`.
2. Calculate category order-total P50/P90.
   **Inputs/evidence:** For sql-40 Exercise 2, read from `order_items` joined to `products`, sum each order's net lines per category in `category_order_values`, then compute `PERCENTILE_CONT(0.5)` and `PERCENTILE_CONT(0.9)` of those per-order category values and count them per category.
   **Expected result/shape:** For sql-40 Exercise 2, expected output: 6 rows, one per category, whose `category_orders` run from 2,145 for Books to 2,192 for Apparel and sum to 13,085, more than the 4,362 orders because an order with lines in several categories counts once in each; `p50_order_value` runs from 146.54 for Home to 150.24 for Electronics on this load. `PERCENTILE_CONT` can interpolate between observed values, so a percentile need not equal an actual order value. The final columns are `category`, `p50_order_value`, `p90_order_value`, and `category_orders`. The final order is `category`.
   **Verify:** For sql-40 Exercise 2, confirm 6 rows, one per category, and that `category_orders` equals `SELECT COUNT(DISTINCT oi.order_id) FROM order_items oi JOIN products p USING (product_id) WHERE p.category = <that category>` (for example 2192 for `Apparel`); `p90_order_value` must be at least `p50_order_value` in every row.
3. Predict `percentile_disc` versus `percentile_cont` on four values.
   **Inputs/evidence:** For sql-40 Exercise 3, use the inline `VALUES` fixture 10, 20, 100, 200 and compute `percentile_disc(0.5)` and `percentile_cont(0.5)` over it.
   **Expected result/shape:** For sql-40 Exercise 3, expected output: one row with `discrete_median` 20 and `continuous_median` 60. The final columns are `discrete_median` and `continuous_median`.
   **Verify:** For sql-40 Exercise 3, confirm by hand that `percentile_disc(0.5)` returns the first value whose cumulative share reaches 0.5, the second of four values (20), while `percentile_cont(0.5)` interpolates halfway between 20 and 100 (60); add the value 300 and expect both medians to become 100.
4. Calculate monthly category revenue share and deterministic rank.
   **Inputs/evidence:** For sql-40 Exercise 4, read `orders` for the month, `order_items` for net line revenue `quantity * unit_price * (1 - discount)`, and `products` for `category`; the CTE `category_month` sums revenue per month and category, `SUM(revenue) OVER (PARTITION BY month)` supplies the share denominator, and `ROW_NUMBER() OVER (PARTITION BY month ORDER BY revenue DESC, category)` supplies the rank.
   **Expected result/shape:** For sql-40 Exercise 4, expected output: 276 rows on this load, 46 months from 2023-02-01 to 2026-11-01 times all 6 categories, with `category_rank` 1 to 6 in every month; the newest month starts with Sports at 16,427.31 and a `month_share` of 0.1924 and ends with Home at rank 6. The final columns are `month`, `category`, `revenue`, `month_share`, and `category_rank`. The final order is `month DESC, category_rank`.
   **Verify:** For sql-40 Exercise 4, confirm 276 distinct `(month, category)` pairs, that the unrounded shares sum to exactly 1 in each of the 46 months while the rounded `month_share` values sum to between 0.9998 and 1.0002, and that `SUM(revenue)` over all rows is 2,355,647.1235, the `order_items` line total; this load has no revenue ties, so `RANK()` matches `ROW_NUMBER()` in every row, but on `VALUES ('Books', 100.00), ('Apparel', 100.00), ('Home', 90.00)` the `category` tiebreaker ranks Apparel 1 and Books 2 where `RANK()` gives both 1.
5. Repair a forecasting frame that includes the current row.
   **Inputs/evidence:** For sql-40 Exercise 5, read `orders`, sum `total_amount` per `order_date::date` in the CTE `daily`, then average the seven previous order days with `AVG(revenue) OVER (ORDER BY day ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING)`, so a day's own revenue never feeds its forecast.
   **Expected result/shape:** For sql-40 Exercise 5, expected output: exactly 20 rows on this load, the consecutive days from 2026-11-23 back to 2026-11-04, each with a non-NULL forecast; the top row is 2026-11-23 with `revenue` 742.14 and `prior_seven_forecast` 2,300.43. The final columns are `day`, `revenue`, and `prior_seven_forecast`. The final order is `day DESC`.
   **Verify:** For sql-40 Exercise 5, confirm 2,300.43 by averaging the seven `daily` rows before 2026-11-23 (`ORDER BY day DESC LIMIT 7`), and that the leaky frame `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` reports 2,079.31 for that day; then, inside `BEGIN ... ROLLBACK`, insert a 500.00 order on 2026-11-24 and confirm it becomes the top row with forecast 2,079.31, the leaky value shifted one day, while the 20-row window now starts at 2026-11-05.
6. Preserve NULL z-scores for a constant series.
   **Inputs/evidence:** For sql-40 Exercise 6, use the inline `VALUES` fixture `constant`, three rows of 5; `moments` adds `AVG(value) OVER ()` and `STDDEV_SAMP(value) OVER ()` to every row, and the outer query divides `value - mean_value` by `NULLIF(sd_value, 0)`.
   **Expected result/shape:** For sql-40 Exercise 6, expected output: three rows, each with `value` 5 and a NULL `z_score`, because the sample standard deviation is 0 and `NULLIF` turns that 0 into NULL. The final columns are `value`, and `z_score`.
   **Verify:** For sql-40 Exercise 6, confirm that dividing by `sd_value` without `NULLIF` fails with `division by zero`, that the fixture 5, 5, 6 gives `z_score` values -0.5774, -0.5774, and 1.1547, and that adding a `NULL` row returns four rows with every `z_score` NULL: `STDDEV_SAMP` skips the NULL, so the 5s still have zero spread, and the NULL row's own difference is NULL.

Verify that the undefined constant-series z-score remains `NULL`.

## Self-check

- Is the named “day” window actually calendar-dense or only observation-based?
- Do percentile and share inputs use one stable, non-duplicated grain?

## Next step

Continue to [Day 41; complex aggregations](day41_complex_aggregations.md).

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

The six prompts move between grains, so name the grain before writing
each query. The first and fifth work on one row per order day, the second on
one row per category and order, and the fourth on one row per month and
category. The third and sixth use tiny inline fixtures, four values and three
identical fives, so you can work out the answer with pencil and paper first
and then check that PostgreSQL agrees.

## Pitfalls and validation

- Do not repeat the whole `orders.total_amount` once per category in a
  multi-category order; use category-attributable line revenue.
- Cast ordered-set results to numeric before PostgreSQL's two-argument `ROUND`.
- Undefined zero-dispersion z-scores should remain `NULL`, not be asserted as
  normal.
- Validate that category revenue shares sum to one, allowing for rounding.

## Expanded practice lab

Prompts 3-6 distinguish continuous interpolation, observed-value percentiles,
partitioned shares, leakage-free windows, and undefined dispersion. For
`(10,20,100,200)`, `percentile_disc(0.5)` returns an observed middle choice,
while `percentile_cont(0.5)` interpolates between the two central values.

Monthly category share partitions by month; ranking should add a stable category
tie-break. A forecasting window ends at `1 PRECEDING`, and a constant series
uses `NULLIF(sd, 0)` so “undefined” is not mislabeled as a score of zero.

## Ask an AI tutor about this lesson

A tutor is handy for the hand calculations: ask it to quiz you on what
`percentile_disc` and `percentile_cont` return for a short list, or on why a
two-day frame always scores plus or minus 0.7071. Setup is in the
[AI tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional); start
with this prompt:

```text
Tutor me through sql-40: Advanced Analytic Functions.

I have completed the direct catalog prerequisite: `sql-found-02`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day40_analytic_functions_advanced.md
- Answer-free learner SQL: sql/postgres-60day/day40_analytic_functions_advanced.sql

Key terms to teach in context: Ordered-set aggregate, Z-score, Interpolation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Aggregate to one row per observed order date, calculate a 15-observation mean and standard deviation, then derive `(revenue - avg15) / NULLIF(sd15, 0)`. Keep the observation count beside the score so early, undersized windows are visible.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
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
