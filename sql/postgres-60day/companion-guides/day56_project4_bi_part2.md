# Day 56 — Complex BI Project, Part 2: Percentiles and CUBE

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 55 — BI drill-downs](day55_project4_bi_part1.md)
- **Artifacts:** [learner SQL](../day56_project4_bi_part2.sql) ·
  [solution reasoning](../solutions/day56_solutions.md) ·
  [executable solution](../solutions/day56_solutions.sql)

## Learning objectives

- Control order, payment, and line grain before multidimensional aggregation.
- Calculate percentiles over category-attributable order values.

## Vocabulary and concepts

- **Dimensional explosion:** rapid subtotal-row growth as a cube gains
  dimensions.
- **Primary payment method:** a reporting policy selecting one method per order.
- **Continuous percentile:** an interpolated ordered-set statistic from
  `PERCENTILE_CONT`.

## Worked example / walkthrough

Aggregate payments at `(order_id, method)`, select one method by greatest total
with a stable tie-breaker, and only then join line revenue. Separately aggregate
line value at `(month, category, order_id)` before computing p50/p90; whole
order totals would repeat across categories.

## Exercises

Complete these in the [learner SQL](../day56_project4_bi_part2.sql):

1. Add payment method to the cube and compare row counts.
2. Calculate category-month order-value P50/P90.
3. Predict raw payment/item join fanout.
4. Pre-aggregate payment methods and reconcile line revenue.
5. Repair line-grain percentiles when the metric is order value.
6. Compare continuous and discrete percentiles for an even population.

Retain cube and percentile observation counts.

## Self-check

- Does the cube grand total reconcile to source line revenue?
- Is the payment-method choice labeled as policy rather than an intrinsic order
  attribute?

## Next step

Continue to [Day 57 — trends and anomalies](day57_project4_bi_part3.md).

## Deep dive and reference

## Project focus

- Measure the dimensional growth caused by adding payment method to a cube.
- Calculate category-month p50 and p90 order-value distributions.
- Control join grain before multidimensional aggregation.

## How the learner script uses the current schema

The starter calculates order-value percentiles by `(country, month)`, ranks
products within country/category, and cubes line revenue across country and
category.

Orders can have multiple payment rows. For the exercise, the reference policy
defines one primary method per order as the method with the greatest total paid
amount, breaking ties by method name. Unpaid orders receive an `unpaid` label.

## Practice — match the learner prompts exactly

1. Add primary payment method to `CUBE(country, category)` and compare the
   two-dimension and three-dimension row counts.
2. At `(month, category, order_id)` grain, sum the net line value attributable
   to the category, then calculate category-month p50 and p90.

## BI and percentile reasoning

- Aggregate payments by `(order_id, method)` before choosing the greatest
  method; otherwise split rows can produce an arbitrary label.
- Reduce to one payment-method row before joining order items to prevent revenue
  multiplication.
- `PERCENTILE_CONT` interpolates and should be accompanied by observation count
  in a production report.
- Cast its result to numeric before two-argument `ROUND`.

## Validation and limits

- Three-dimensional cube row count should exceed the two-dimensional count on
  this seed.
- Reconcile cube grand-total revenue to source line revenue.
- Primary payment method is a declared reporting policy, not an intrinsic order
  attribute.
- Avoid repeating whole order totals once for every category.
