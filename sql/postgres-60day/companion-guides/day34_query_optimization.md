# Day 34 — Query Optimization Techniques

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 33 — composite, covering, and partial indexes](day33_index_optimization_strategies.md)
- **Artifacts:** [learner SQL](../day34_query_optimization.sql) ·
  [solution reasoning](../solutions/day34_solutions.md) ·
  [executable solution](../solutions/day34_solutions.sql)

## Learning objectives

- Optimize one measured bottleneck while preserving result semantics.
- Reduce repeated work through early safe filtering, narrower projection, or
  pre-aggregation.

## Vocabulary and concepts

- **Baseline:** the controlled query, data, plan, and result used for comparison.
- **Predicate pushdown:** evaluating a safe filter closer to its source.
- **Semantic equivalence:** two queries returning the same defined result.

## Worked example / walkthrough

Capture a baseline and control totals, replace a repeated scalar aggregate with
one grouped relation, and join it back. Recheck keys and totals before comparing
plans; a faster query that silently drops zero-order customers is not an
optimization of the same requirement.

## Exercises

Complete the prompts in the [learner SQL](../day34_query_optimization.sql).
Change one thing per experiment and record plan, buffers, result reconciliation,
and observed tradeoff.

## Self-check

- Are compared queries semantically identical at edge cases as well as typical
  rows?
- Does the evidence identify work removed rather than relying only on elapsed
  time?

## Next step

Continue to [Day 35 — performance pitfalls](day35_avoiding_pitfalls.md).

## Deep dive and reference

## What you will learn

- Reduce rows and columns before expensive joins or aggregates.
- Replace repeated subquery work with set-based joins when semantics allow.
- Measure a rewrite rather than assuming it is faster.

## How the learner script uses the current schema

The script filters recent `orders` in a CTE before joining to `customers`,
projects only `order_id` and `customer_id` in a seven-day plan, and aggregates
`order_items.quantity` by `products.category` for successful order statuses.

PostgreSQL can inline many non-materialized CTEs, so writing a filter in a CTE
does not itself guarantee a faster plan. The value is a clear, correct query
shape that the optimizer can transform.

## Optimization loop

1. Capture `EXPLAIN (ANALYZE, BUFFERS)` for a safe baseline.
2. Identify excess rows, repeated loops, large sorts, or poor estimates.
3. Make one targeted change.
4. Reconcile keys, counts, and totals.
5. Compare plans under the same data and predicate.

## Practice — match the learner prompts exactly

1. Replace a scalar or correlated subquery with a join to a pre-aggregated
   relation, then compare the two plans and outputs.
2. Limit rows as early as the business semantics permit and compare performance.
   Do not move `LIMIT` before an aggregate or ordering if that changes which
   rows are eligible.

## Pitfalls and validation

- The optimizer chooses physical join order; SQL text order is not a reliable
  tuning lever.
- Pushing a filter from `WHERE` into the nullable side of an outer join can
  change results.
- `DISTINCT` can hide join fanout. Fix grain instead of masking duplicates.
- A faster query that changes counts or totals is incorrect.
