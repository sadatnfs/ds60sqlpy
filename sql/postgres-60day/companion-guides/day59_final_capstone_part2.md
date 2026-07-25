# Day 59 — Final Capstone, Part 2: Stakeholder Analytics

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 58 — capstone ingestion and data quality](day58_final_capstone_part1.md)
- **Artifacts:** [learner SQL](../day59_final_capstone_part2.sql) ·
  [solution reasoning](../solutions/day59_solutions.md) ·
  [executable solution](../solutions/day59_solutions.sql)

## Learning objectives

- Deliver stakeholder-specific metrics with documented grain, denominator,
  scope, and reconciliation.
- Pair performance recommendations with representative evidence and operational
  ownership.

## Vocabulary and concepts

- **KPI contract:** metric name, formula, grain, population, window, exclusions,
  and owner.
- **Funnel denominator:** the eligible population used at each conversion step.
- **Scale hypothesis:** a design expected to help at larger volume but still
  requiring representative validation.

## Worked example / walkthrough

Choose one KPI and write its contract before SQL. Build its lowest stable grain,
add dimensions only after reconciliation, and return numerator/denominator
beside any rate. Present the stakeholder table together with its control total
and a limitation; repeat that evidence pattern for Finance and Marketing.

## Exercises

Complete all four deliverables in the [learner SQL](../day59_final_capstone_part2.sql).
Add a one-page metric dictionary and a before/after performance evidence table.

## Self-check

- Can another analyst reproduce every KPI from its written contract?
- Are campaign counts, pair counts, and funnel rates prevented from being
  summed across non-additive rows?

## Next step

Continue to [Day 60 — end-to-end sign-off](day60_final_capstone_part3.md).

## Deep dive and reference

Day 59 is a capstone checkpoint, not a pair of discrete exercises. It combines
KPI definitions, performance evidence, stakeholder outputs, and scale planning.

## Deliverable 1 — KPI suite

- LTV by signup cohort and customer segment, with customer count, average LTV,
  and total LTV.
- A 90-day customer-grain funnel for page view, add to cart, checkout, and
  purchase/order conversion, with explicit denominators.
- The top 20 distinct product pairs from order baskets, ranked by co-occurrence
  count (`together`), not by attributed pair revenue.

## Deliverable 2 — Performance evidence

Create candidate indexes only inside the rollback-only experiment, then capture
`EXPLAIN (ANALYZE, BUFFERS)` for the recent customer-revenue query. Save result
reconciliation, timing, buffers, row estimates, and plan choice. The compact
seed may correctly use a sequential scan.

## Deliverable 3 — Stakeholder outputs

- Finance: current-year budget, actual expense, and variance by category.
- Marketing: campaign touches within seven days before each customer's first
  order, counted as distinct assisted customers.

The marketing definition differs from Day 48's all-purchase event attribution.
Multiple campaigns can assist one customer, so campaign rows are not additive.

## Deliverable 4 — Large-scale design note

For a hypothetical 100M-row workload, identify candidate time partitions for
orders/events, prove partition-key filters for pruning, describe local/partial
indexes, and assign retention/maintenance ownership. Do not claim a benefit
without a representative plan.

## Sign-off limits

Record metric grain, time window, exclusions, reconciliation, and consumer for
every KPI. All candidate DDL rolls back; production changes require a separate
reviewed migration.
