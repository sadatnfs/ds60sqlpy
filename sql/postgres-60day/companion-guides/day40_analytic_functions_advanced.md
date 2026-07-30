# Day 40 — Advanced Analytic Functions

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 39 — locks and deadlocks](day39_locks_deadlocks.md)
  plus the window-function sequence from Days 16–22
- **Artifacts:** [learner SQL](../day40_analytic_functions_advanced.sql) ·
  [solution reasoning](../solutions/day40_solutions.md) ·
  [executable solution](../solutions/day40_solutions.sql)

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
2. Calculate category order-total P50/P90.
3. Predict `percentile_disc` versus `percentile_cont` on four values.
4. Calculate monthly category revenue share and deterministic rank.
5. Repair a forecasting frame that includes the current row.
6. Preserve NULL z-scores for a constant series.

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
