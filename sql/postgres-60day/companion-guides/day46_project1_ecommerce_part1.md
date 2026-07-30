# Day 46 — E-commerce Project, Part 1: LTV and Cohorts

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 45 — optimization project](day45_phase3_optimization_project.md)
- **Artifacts:** [learner SQL](../day46_project1_ecommerce_part1.sql) ·
  [solution reasoning](../solutions/day46_solutions.md) ·
  [executable solution](../solutions/day46_solutions.sql)

## Learning objectives

- Calculate customer lifetime value (LTV) at one row per customer.
- Assign policy-driven segments and measure cohort revenue over lifecycle
  months.

## Vocabulary and concepts

- **LTV:** lifetime value under a stated revenue, margin, and refund definition.
- **Signup cohort:** customers grouped by their creation month.
- **Lifecycle offset:** elapsed whole months from cohort start to activity.

## Worked example / walkthrough

Collapse line items to order value, then orders to one customer LTV row. Left
join from customers if zero-order customers belong in the population. Reconcile
summed LTV with the chosen source total before assigning thresholds; segmenting
at a duplicated order-line grain would bias both counts and value.

## Exercises

Complete these in the [learner SQL](../day46_project1_ecommerce_part1.sql):

1. Define fixed LTV segments and analyze them by country.
2. Calculate cohort revenue for offsets 0–12.
3. Predict how `NTILE` labels change when unrelated customers arrive.
4. Produce LTV, orders, AOV, and recency at customer grain.
5. Repair payment/item fanout in LTV.
6. Retain no-order customers with an explicit zero-LTV policy.

Add a zero-order-customer test and state its segment.

## Self-check

- Does every customer contribute at most once to segmentation input?
- Are threshold ownership, refund/margin scope, and multi-year month offsets
  explicit?

## Next step

Continue to [Day 47 — cohort retention](day47_project1_ecommerce_part2.md).

## Deep dive and reference

## Project focus

- Calculate lifetime value at one row per customer.
- Assign explicit gold, silver, and bronze value segments.
- Measure cohort revenue over lifecycle months 0–12.

## How the learner script uses the current schema

The starter first collapses `order_items` to order value, then sums orders to
customer LTV and assigns `NTILE(4)` for exploration. Signup cohort is
`date_trunc('month', customers.created_at)`.

`orders.total_amount` is already reconciled from line-item net revenue by setup,
so it is also valid for customer LTV when the metric definition is gross booked
order value. The schema does not model a separate refund fact.

## Practice — match the learner prompts exactly

1. Choose and state numeric thresholds for gold, silver, and bronze LTV. Assign
   every customer, then report customer count, average LTV, and total LTV by
   `(country, ltv_segment)`.
2. Calculate revenue by signup `cohort_month` and lifecycle `month_offset` from
   0 through 12.

## Grain and date reasoning

- One customer must contribute once to the LTV segmentation input.
- Customers with no orders need a deliberate policy; a left join can retain
  them with zero LTV.
- A multi-year month offset must combine years and months from `age`; extracting
  only the month component wraps after 11.
- A missing cohort/offset row means no represented orders, not necessarily a
  stored zero.

## Validation and limits

- Treat segment thresholds as business policy, not universal cutoffs.
- Reconcile summed customer LTV to `SUM(orders.total_amount)`.
- Signup month defines cohort membership; order month defines lifecycle revenue.
- Synthetic data demonstrates the method, not a real customer-value benchmark.
