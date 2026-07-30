# Day 15 — Phase 1 Project: Multi-Dimensional Revenue Report (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 14 — numeric types and casting](day14_numeric_and_casting.md)
  and the complete Day 01–14 foundation sequence
- **Artifacts:** [learner SQL](../day15_phase1_project.sql) ·
  [solution reasoning](../solutions/day15_solutions.md) ·
  [executable solution](../solutions/day15_solutions.sql)

## Learning objectives

- Design a multi-dimensional revenue report from a written metric contract.
- Reconcile joins, conditional metrics, subtotals, and time calculations before
  presenting the result.

## Vocabulary and concepts

- **Metric contract:** a written definition of grain, formula, filters, and
  exclusions.
- **Dimensional report:** measures grouped by descriptive attributes such as
  country, category, and month.
- **Control total:** an independently calculated value used for reconciliation.

## Worked example / walkthrough

Build one stable `order_lines` relation first, with one row per intended line or
order and a single net-revenue formula. Reconcile its total, then add dimension
joins one at a time and compare the total after each join. Only after totals
remain stable should you add grouping sets and display labels.

## Practice assumptions and review method

- **Focus:** Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.
- **Assumptions:** All monetary summaries identify stored totals versus computed net line revenue. Reporting month uses UTC and empty populations remain visible where required.
- **Failure to watch for:** Combining fact tables before fixing their grain multiplies measures; every project output must state its row grain and acceptance checks.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Create a customer performance table with order count, stored revenue, and latest order date, retaining customers with no orders.
   **Progressive hint:** Left join from customers and aggregate at customer grain.
   **Expected shape:** One row per customer.
2. **Query writing:** Create a product profitability table from net order-line revenue and catalog cost.
   **Progressive hint:** Calculate line revenue and line cost at item grain, then aggregate to product.
   **Expected shape:** One row per sold product.
3. **Query writing:** Build a UTC monthly order-status report with counts and stored revenue.
   **Progressive hint:** Derive one reporting month and group by month/status.
   **Expected shape:** One row per observed month and status.
4. **Debugging:** Reconcile stored order total, computed line total, and paid total without multiplying details.
   **Progressive hint:** Aggregate items and payments independently to order grain before joining.
   **Expected shape:** One row per order with differences.
5. **Prediction:** Compare monthly budgets with actual expenses and preserve missing sides.
   **Progressive hint:** Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero.
   **Expected shape:** One row per category/month in either source.
6. **Extension:** Produce one executive summary row with population, activity, stored revenue, computed revenue, and payments.
   **Progressive hint:** Compute independent one-row aggregates, then cross join them to avoid detail multiplication.
   **Expected shape:** Exactly one summary row.

## Self-check

- Does the grand total equal the independent net-line-revenue control?
- Are date window, payment handling, zero-activity entities, and subtotal
  `NULL`s documented?

## Next step

Continue to [Day 16 — window-function fundamentals](day16_window_functions_fundamentals.md).

## Deep dive and reference

Goal
- Produce a robust monthly revenue report segmented by customer attributes and product categories using techniques from Days 01–14.

What you’ll build
- Extend the supplied monthly segment-country report while retaining its
  revenue, active-customer, and revenue-per-active metrics.
- Add at least two dimensions. The learner script suggests payment method and
  product category.

Guidance
1) Keep product category at line grain before aggregating; it cannot be
   recovered after all lines have been collapsed to one order total.
2) Pre-aggregate payments to the order-method grain before joining to lines.
3) Aggregate by month, segment, country, and the two chosen dimensions.
4) Validate totals against net line revenue and inspect split-payment orders.
5) Document whether all order statuses are included; the starter query does not
   exclude `placed`, `returned`, or any other status.

Quality checklist
- Correct join cardinality (no double counting)
- Handling of NULL/unknown categories and segments
- Performance: indices on join keys; avoid unnecessary DISTINCT

Current practice map
- The authoritative six prompts above replace the older single deliverable.
  Complete all six outputs and document grain, missing-side behavior, UTC
  boundaries, money definitions, and reconciliation evidence.
