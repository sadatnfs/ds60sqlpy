# Day 47 — E-commerce Project, Part 2: Cohort Retention

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 46 — LTV and cohorts](day46_project1_ecommerce_part1.md)
- **Artifacts:** [learner SQL](../day47_project1_ecommerce_part2.sql) ·
  [solution reasoning](../solutions/day47_solutions.md) ·
  [executable solution](../solutions/day47_solutions.sql)

## Learning objectives

- Define cohort size independently from later activity.
- Produce a chart-ready retention table with explicit numerator, denominator,
  and lifecycle offset.

## Vocabulary and concepts

- **Cohort size:** all eligible signups in the cohort, including non-purchasers.
- **Active customer:** a distinct customer meeting the declared period rule.
- **Retention curve:** retention rate across lifecycle offsets for one cohort.

## Worked example / walkthrough

Deduplicate activity to `(customer_id, order_month)`, count active customers per
cohort/offset, and join to cohort size calculated from all customers. Cast
before division and build a cohort/offset spine when missing periods must appear
as explicit zeros.

## Exercises

Complete the prompts in the [learner SQL](../day47_project1_ecommerce_part2.sql).
Return a tidy six-cohort result with numerator and denominator retained beside
the rate.

## Self-check

- Is each customer counted once per activity month regardless of order count?
- Are rates bounded by zero and one, with missing rows distinguished from zero?

## Next step

Continue to [Day 48 — affinity and attribution](day48_project1_ecommerce_part3.md).

## Deep dive and reference

## Project focus

- Define signup cohort size.
- Count distinct active customers by lifecycle month.
- Produce six chart-ready retention curves.

## How the learner script uses the current schema

The starter deduplicates `orders` to one row per `(customer_id, order_month)`,
joins each customer to the signup month from `customers.created_at`, and counts
active customers at offsets 0–12.

This lesson is retention only. Funnel analysis belongs to the later
event/capstone work and is not a Day 47 deliverable.

## Practice — match the learner prompts exactly

1. Divide `active_customers` by total signup `cohort_size` to calculate
   `retention_rate`. Return numerator, denominator, and rate.
2. Restrict the tidy result to the six newest cohorts and chart
   `month_offset` on X, `retention_rate` on Y, and `cohort_month` as series.

The chart itself is outside SQL. The SQL deliverable is the narrow,
chart-ready table.

## Grain and denominator

- Cohort size includes every signup in the month, not only later purchasers.
- Multiple orders by the same customer in one month count as one active
  customer.
- Cast before division so PostgreSQL does not perform integer division.
- Combine year and month components when calculating lifecycle offset.

## Validation and limits

- A missing offset row and a present zero-rate row are different. Build a
  cohort-by-offset spine when a complete matrix is required.
- Do not count orders as retained customers.
- Restrict activity to order months on or after signup.
- The synthetic curves are technique demonstrations, not expected business
  retention shapes.
