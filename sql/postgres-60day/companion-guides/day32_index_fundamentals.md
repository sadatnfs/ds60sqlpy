# Day 32 — Index Fundamentals

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 31 — EXPLAIN and EXPLAIN ANALYZE](day31_explain_analyze.md)
- **Artifacts:** [learner SQL](../day32_index_fundamentals.sql) ·
  [solution reasoning](../solutions/day32_solutions.md) ·
  [executable solution](../solutions/day32_solutions.sql)

## Learning objectives

- Match a B-tree index to equality, range, and ordering requirements.
- Explain a planner choice using selectivity, table size, projection, and
  measured cost.

## Vocabulary and concepts

- **Selectivity:** the fraction of rows a predicate is expected to return.
- **Index scan:** an access path that uses index entries to locate heap rows.
- **Index-only scan:** a plan that can satisfy selected values from the index,
  subject to visibility checks.

## Worked example / walkthrough

Capture a category-filter plan before creating `products(category)`, create the
index inside the rollback-only transaction, and rerun the identical query.
Record the plan even if PostgreSQL keeps the sequential scan: the compact seed
can make reading the table cheaper than traversing an index.

## Exercises

Complete the prompts in the [learner SQL](../day32_index_fundamentals.sql).
Compare selective and unselective predicates against the same indexed column.

## Self-check

- Are the before/after SQL, parameters, and returned rows identical?
- Can you explain index write/storage cost as well as possible read benefit?

## Next step

Continue to [Day 33 — composite, covering, and partial indexes](day33_index_optimization_strategies.md).

## Deep dive and reference

## What you will learn

- Create B-tree indexes for equality and range predicates.
- Observe planner choices before and after an index exists.
- Explain why a valid index can remain unused on a small or unselective query.

## How the learner script uses the current schema

Inside a rollback-only transaction, the script creates indexes on
`orders.total_amount`, `orders.order_date`, and `customers.country`. It then
executes matching filters with `EXPLAIN ANALYZE`. No course index persists after
the final `ROLLBACK`.

B-tree is PostgreSQL's default and supports equality, ranges, ordering, `IN`,
and prefix pattern searches. A hash index is mentioned only as a contrast;
B-tree already handles the equality lookup on `customers.email`.

## Planner and index concepts

- Selective predicates benefit most because they fetch a small fraction of the
  table.
- Every index adds storage and write/vacuum work. “Index every column” is not a
  sound policy.
- An index-only scan also depends on selected columns and visibility-map state.
- `SELECT *` can make heap access necessary even when a filter uses an index.
- On the compact seed, a sequential scan may correctly be cheaper.

## Practice — match the learner prompts exactly

1. Create an index on `products(category)` and run a category filter with
   `EXPLAIN ANALYZE`.
2. Compare the same category query with the index absent and present. Record
   scan type, estimated/actual rows, execution time, and buffers if requested.

Run both comparisons in one controlled session and keep predicate and projection
the same.

## Pitfalls and validation

- Use only the setup's valid order statuses: `placed`, `paid`, `shipped`,
  `delivered`, and `returned`.
- Do not disable sequential scans as proof that an index is beneficial.
- Index names are schema-local; use exercise-specific names to avoid collisions.
- The learner transaction rolls all index experiments back safely.
