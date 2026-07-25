# Day 41 — Complex Aggregations

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 40 — advanced analytic functions](day40_analytic_functions_advanced.md)
- **Artifacts:** [learner SQL](../day41_complex_aggregations.sql) ·
  [solution reasoning](../solutions/day41_solutions.md) ·
  [executable solution](../solutions/day41_solutions.sql)

## Learning objectives

- Produce several conditional measures from one controlled fact grain.
- Build deterministic ordered labels after ranking within a partition.

## Vocabulary and concepts

- **FILTER clause:** a per-aggregate condition written after the aggregate.
- **Conditional aggregate:** a measure calculated only for qualifying rows.
- **Ordered aggregation:** concatenation or collection under a specified order.

## Worked example / walkthrough

Establish one order-line relation, then calculate 30-day revenue, 90-day
revenue, order count, and customer count in one category group using `FILTER`.
Reconcile each measure with a simpler single-purpose query before trusting the
combined dashboard.

## Exercises

Complete the prompts in the [learner SQL](../day41_complex_aggregations.sql).
Add a category with no qualifying recent rows and decide whether its measures
should be `NULL` or zero.

## Self-check

- Are order and customer counts protected from line-level fanout?
- Is the top-five label order stable under metric ties?

## Next step

Continue to [Day 42 — data quality and validation](day42_data_quality_validation.md).

## Deep dive and reference

## What you will learn

- Calculate several conditional metrics in one grouped query with `FILTER`.
- Express equivalent conditional aggregates with `CASE`.
- Build ordered labels with `string_agg`.

## How the learner script uses the current schema

The starter calculates category units and revenue over all history, 30 days, and
90 days by joining `orders`, `order_items`, and `products`. It also reports
successful/returned orders by `customers.country`, then demonstrates
`string_agg(DISTINCT products.name, ...)` by category.

The valid successful status set used by the script is `paid`, `shipped`, and
`delivered`; `returned` is reported separately. Use only the statuses supplied
by the course setup.

## Multi-metric design

- Establish line-item grain before summing net revenue.
- Use `COUNT(DISTINCT order_id)` and `COUNT(DISTINCT customer_id)` when a join
  has expanded each order to multiple item rows.
- Guard every denominator with `NULLIF`.
- Conditional sums can be `NULL` when no row qualifies; decide whether display
  policy should use `COALESCE`.

## Practice — match the learner prompts exactly

1. Build a six-metric dashboard by category with `FILTER`: 30-day revenue,
   90-day revenue, 30-day orders, 30-day units, 90-day customers, and 30-day
   revenue per order.
2. For each country, rank products by net line revenue, keep the top five, then
   `string_agg` their names in revenue-rank order.

## Pitfalls and validation

- Applying a global `LIMIT 5` does not produce five products per country; rank
  within country first.
- Do not sum `orders.total_amount` after joining to item rows.
- Add a deterministic tie-break such as `product_id`.
- Validate dashboard totals against a simpler single-metric query before
  trusting the combined report.
