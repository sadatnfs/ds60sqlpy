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

## Exercises

Implement both deliverables in the [learner SQL](../day07_week1_project.sql).
Save a one-row revenue control query and compare it with the sum of the detailed
report.

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

Deliverables from the learner script
1) Add payment method and show revenue by country, category, and method.
2) Add customer cohort month (`date_trunc('month', customers.created_at)`) and
   rerun the report.

Payment ambiguity
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
