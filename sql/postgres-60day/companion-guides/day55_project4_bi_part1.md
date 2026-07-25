# Day 55 — Complex BI Project, Part 1: Drill-downs

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 54 — warehouse aggregates](day54_project3_dwh_part3_aggregations.md)
- **Artifacts:** [learner SQL](../day55_project4_bi_part1.sql) ·
  [solution reasoning](../solutions/day55_solutions.md) ·
  [executable solution](../solutions/day55_solutions.sql)

## Learning objectives

- Generate hierarchical subtotal levels with `ROLLUP` and distinguish them from
  all-combination `CUBE` output.
- Rank deterministic top products within several dimensions.

## Vocabulary and concepts

- **ROLLUP:** hierarchical grouping sets from detail through grand total.
- **CUBE:** every grouping-key subset for the supplied dimensions.
- **GROUPING flag:** an indicator separating generated subtotal `NULL`s from
  data `NULL`s.

## Worked example / walkthrough

Compare `ROLLUP(country, category)` with `CUBE(country, category)`. Both include
detail, country subtotal, and grand total; `CUBE` also adds category-only
subtotals. Use `GROUPING(country)` and `GROUPING(category)` to label each level,
then reconcile the grand total with source line revenue.

## Exercises

Complete the prompts in the [learner SQL](../day55_project4_bi_part1.sql). Add
one real `NULL` dimension value and prove labels still distinguish it from a
generated subtotal.

## Self-check

- Is payment method reduced to one declared row per order before joining lines?
- Does top-five ranking partition by every requested dimension and break ties
  deterministically?

## Next step

Continue to [Day 56 — percentiles and CUBE](day56_project4_bi_part2.md).

## Deep dive and reference

## Project focus

- Generate hierarchical subtotals with `ROLLUP`.
- Compare hierarchical subtotal rows with all-combination `CUBE`.
- Rank top products within country, category, and order status.

## How the learner script uses the current schema

The starter builds line revenue from `orders`, `customers`, `order_items`, and
`products`, chooses one primary payment method per order by greatest paid
amount (method name breaks ties), and rolls up country, category, payment
method, and month. Unpaid orders receive the `unpaid` label.
`GROUPING(column)` distinguishes subtotal nulls from detail values.

It separately ranks product revenue within `(country, category)`.

## Practice — match the learner prompts exactly

1. Replace a two-dimension `ROLLUP(country, category)` with
   `CUBE(country, category)` and compare row counts. Explain the category-only
   subtotal added by `CUBE`.
2. Add `orders.status`, aggregate product revenue at
   `(country, category, status, product_id)`, and return the top five products
   within every such group.

## BI reasoning

- `ROLLUP(a, b)` returns `(a,b)`, `(a)`, and grand total.
- `CUBE(a, b)` also returns the `(b)` subtotal.
- Use `GROUPING` flags when real dimension nulls are possible.
- Aggregate revenue before ranking; use `ROW_NUMBER` plus `product_id` for
  exactly five deterministic results.

## Validation and limits

- A raw payment join fans out split-payment orders. Keep the declared primary
  method policy—or document a different allocation—before using that dimension.
- Cube row counts grow rapidly with dimensions and distinct values.
- Reconcile grand-total cube revenue to source line revenue.
