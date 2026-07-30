# Day 07 — Week 1 Project: From Questions to Queries (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 06 — set operations](day06_set_operations.md) and the
  joins and aggregates from Days 01–05
- **Artifacts:** [learner SQL](../day07_week1_project.sql) ·
  [solution reasoning](../solutions/day07_solutions.md) ·
  [executable solution](../solutions/day07_solutions.sql)

## Learning objectives

- Translate a report request into grain, joins, filters, aggregates, and
  validation queries.
- Prevent payment-to-line fanout and document an allocation policy.

## Vocabulary and concepts

- **Report grain:** the dimensions represented by one output row.
- **Reconciliation:** comparing a complex result with an independent trusted
  total or count.
- **Allocation rule:** a declared policy for assigning a shared amount across
  multiple categories or methods.

## Worked example / walkthrough

Build the report in checkpoints: aggregate net line revenue to order/category,
reduce payments to the declared order/method grain, join those stable inputs,
and only then roll up country, category, and method. Reconcile revenue before
adding cohort month so a new dimension cannot hide fanout.

## Practice assumptions and review method

- **Focus:** Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.
- **Assumptions:** Revenue means exact net line revenue unless a prompt explicitly asks for stored order totals. Every ranked output has a deterministic tie-breaker.
- **Failure to watch for:** A polished result is not trustworthy until its grain, denominator, missing-row policy, and reconciliation are explicit.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Build an order KPI table by status with order count, revenue, average order value, and distinct customers.
   **Progressive hint:** Aggregate orders at status grain and round only displayed monetary values.
   **Expected shape:** One row per order status.
2. **Query writing:** Return the 20 products with the highest net line revenue.
   **Progressive hint:** Aggregate order items by product before ranking; use product ID as tie-breaker.
   **Expected shape:** At most 20 product rows.
3. **Query writing:** Create a customer summary that retains customers with no orders.
   **Progressive hint:** Left join from customers and count/order-sum nullable matches with `COALESCE` only where zero has clear meaning.
   **Expected shape:** One row per customer.
4. **Debugging:** Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows.
   **Progressive hint:** Aggregate each detail table to order grain first, then join the one-row-per-order relations.
   **Expected shape:** One row per order with signed differences.
5. **Prediction:** Build a monthly order trend and explain which months are absent rather than zero.
   **Progressive hint:** Grouping observed orders alone cannot create empty calendar months.
   **Expected shape:** One row per observed order month.
6. **Extension:** Create a compact one-row audit of customer, order, item, and payment coverage.
   **Progressive hint:** Use scalar subqueries for independent counts; this avoids accidental cross multiplication.
   **Expected shape:** Exactly one audit row.

## Self-check

- Can one order contribute to several payment-method rows, and if so, is its
  revenue allocation explicit?
- Are the 90-day boundary, unpaid-order policy, and report grain documented?

## Next step

Continue to [Day 08 — scalar and inline subqueries](day08_scalar_inline_subqueries.md).

## Deep dive and reference

Goal
- Extend the starter report of last-90-day revenue and buyers by country and
  category using the joins, aggregates, and set reasoning from Days 01–06.

Current practice map
- Use the six maintained prompts above as the project acceptance checklist.
  They now cover KPI grain, product and customer coverage, fanout-safe
  reconciliation, missing months, and a compact population audit.

Further extension: payment ambiguity
- `payments` can contain multiple rows per order. Joining raw payments to raw
  order lines can repeat revenue. Decide whether the report is payment revenue
  (`payments.amount`) or order-line revenue allocated to a method, and
  pre-aggregate to one row per order/method before joining.
- An order with split methods can legitimately appear in more than one method
  row. State the allocation rule rather than silently duplicating order revenue.

Checklist
1) Preserve the starter report's 90-day scope.
2) Validate each join and aggregation with order counts and revenue
   reconciliation.
3) Confirm how unpaid orders and split payments are represented.
4) Document cohort and payment-method assumptions beside the query.

Rubric
- Correct grain, no accidental payment fanout, reproducible date logic, clear
  assumptions, and readable SQL.
