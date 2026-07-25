# Day 35 — Avoiding Common Performance Pitfalls

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 34 — query optimization](day34_query_optimization.md)
- **Artifacts:** [learner SQL](../day35_avoiding_pitfalls.sql) ·
  [solution reasoning](../solutions/day35_solutions.md) ·
  [executable solution](../solutions/day35_solutions.sql)

## Learning objectives

- Rewrite non-sargable temporal predicates as correct raw-column ranges.
- Replace repeated correlated work with one set-based aggregation.

## Vocabulary and concepts

- **Sargability:** whether a predicate can use an index's search ordering.
- **Half-open range:** `>= start AND < end`, suitable for adjacent periods.
- **Set-based rewrite:** compute a relation once rather than once per outer row.

## Worked example / walkthrough

Compare `date_trunc('day', order_date) = target_day` with
`order_date >= target_day AND order_date < target_day + interval '1 day'`.
Test timestamps at both boundaries, reconcile row IDs, and compare plans with a
matching `order_date` index.

## Exercises

Complete the prompts in the [learner SQL](../day35_avoiding_pitfalls.sql).
For each rewrite, add an edge-case result check before the performance
comparison.

## Self-check

- Does the range preserve the intended time-zone and boundary semantics?
- Does a set-based rewrite retain outer entities with no matching facts when
  required?

## Next step

Continue to [Day 36 — materialized views](day36_materialized_views.md).

## Deep dive and reference

## What you will learn

- Recognize function-wrapped predicates that are hard to index.
- Replace per-row correlated aggregation with one set-based aggregation.
- Preserve correctness while reducing repeated work.

## How the learner script uses the current schema

The first pair compares `date_trunc('day', order_date) = ...` with a half-open
range on raw `orders.order_date`. The second pair compares a customer-by-customer
correlated sum with one grouped `orders` CTE joined to `customers`.

The half-open range is:

`order_date >= start_of_day AND order_date < start_of_next_day`

It handles every timestamp in the day and can match a normal B-tree index on
`order_date`.

## Why the set-based rewrite helps

The correlated form can execute an order scan once per customer. The grouped
form scans and aggregates orders once, then joins one row per customer. A
`LEFT JOIN` retains customers with no orders; decide whether the displayed
value should remain `NULL` or become zero.

## Practice — match the learner prompts exactly

1. Find and rewrite three queries that apply a function to an indexed column.
   Use equivalent raw-column ranges and prove their boundary behavior.
2. Replace correlated subqueries with joins to grouped CTEs or derived tables,
   then compare plans and reconcile results.

## Pitfalls and validation

- Do not rewrite a predicate unless time zone and inclusive/exclusive boundaries
  remain correct.
- Functions are not universally bad; a matching expression index can be valid
  when the expression is the real search key.
- Preserve outer-join behavior for entities with no facts.
- Compare result keys and totals before comparing timing.
