# Day 31 — EXPLAIN and EXPLAIN ANALYZE

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 30 — Phase 2 project](day30_phase2_project.md), with
  confidence in joins, aggregates, CTEs, and result reconciliation
- **Artifacts:** [learner SQL](../day31_explain_analyze.sql) ·
  [solution reasoning](../solutions/day31_solutions.md) ·
  [executable solution](../solutions/day31_solutions.sql)

## Learning objectives

- Read a plan tree from its leaf nodes through the final output.
- Compare estimates with actual rows, loops, timing, and buffers without
  treating one timing as universal evidence.

## Vocabulary and concepts

- **Plan node:** one physical operation in a PostgreSQL execution plan.
- **Cost estimate:** a planner-relative estimate, not elapsed milliseconds.
- **Loop count:** the number of times a node executes under its parent.

## Worked example / walkthrough

Run the same safe filter first with `EXPLAIN` and then with
`EXPLAIN (ANALYZE, BUFFERS)`. Start at the scan leaf, compare estimated rows
with `actual rows × loops`, note rows removed by the filter, and only then read
the parent `LIMIT` or aggregate node.

## Exercises

Complete the prompts in the [learner SQL](../day31_explain_analyze.sql). Save one
plan and a result-control query as the baseline for Day 32.

## Self-check

- Can you distinguish estimated cost from measured time?
- Have you verified that every `EXPLAIN ANALYZE` statement is safe to execute?

## Next step

Continue to [Day 32 — index fundamentals](day32_index_fundamentals.md).

## Deep dive and reference

## What you will learn

- Read planned operations, estimated costs, row counts, and widths.
- Add actual timing, rows, and loop counts with `EXPLAIN ANALYZE`.
- Compare scan, join, aggregate, and sort nodes without guessing about speed.

## How the learner script uses the current schema

The first plan filters `training.orders.total_amount > 500`. The second plan
executes that filter with `LIMIT 100`. The join plan combines `orders`,
`customers`, and `order_items`, filters the last 90 days, and aggregates units
by `customers.country`.

`EXPLAIN` does not execute the statement. `EXPLAIN ANALYZE` does, so use it with
care around writes. The day is wrapped in a transaction and contains only
read-only statements.

## Reading a plan

- Start at the most indented nodes: they produce rows for their parents.
- Compare estimated `rows` with `actual rows × loops`; large gaps can signal
  stale statistics, skew, or a misunderstood predicate.
- Inspect filters and “Rows Removed by Filter” to understand selectivity.
- A sequential scan is not automatically bad. It is often cheapest for a small
  table or a predicate returning much of the table.
- The highest individual node time is not the whole story. Loops multiply work,
  and sort or aggregate nodes can spill when memory is insufficient.

## Practice — match the learner prompts exactly

1. Add different `WHERE` predicates to the existing order queries and record
   how selectivity changes estimates, actual rows, and scan choice.
2. Run the same safe query with `EXPLAIN` and `EXPLAIN ANALYZE`; note which
   actual timing, row, and loop fields appear only after execution.

Keep the query result logically identical when comparing plans. Day 32 adds
indexes, so save one Day 31 plan as a before-index baseline.

## Pitfalls and validation

- Do not compare timings from different predicates or different result sets.
- Warm cache, background activity, and the compact seed can change timings.
- Never use `EXPLAIN ANALYZE` on destructive production DML merely to see a
  plan; it executes the statement.
- Prefer `EXPLAIN (ANALYZE, BUFFERS)` when you need I/O evidence.
