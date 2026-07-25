# Day 36 — Materialized Views and Caching

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 35 — performance pitfalls](day35_avoiding_pitfalls.md)
- **Artifacts:** [learner SQL](../day36_materialized_views.sql) ·
  [solution reasoning](../solutions/day36_solutions.md) ·
  [executable solution](../solutions/day36_solutions.sql)

## Learning objectives

- Materialize a query at a declared grain and reconcile it with source data.
- Design refresh, freshness, ownership, and failure expectations.

## Vocabulary and concepts

- **Materialized view:** stored rows produced by a query and refreshed
  explicitly.
- **Freshness:** how current cached output is relative to its sources.
- **Concurrent refresh:** a read-preserving refresh mode with unique-index and
  transaction restrictions.

## Worked example / walkthrough

Create the monthly-category materialized view inside the learner transaction,
reconcile its total revenue and row-grain uniqueness with the source query,
then refresh it. Query speed is only one dimension; record when the stored rows
become stale and who would own refresh failures.

## Exercises

Complete the prompts in the [learner SQL](../day36_materialized_views.sql).
Write a freshness service-level expectation and a validation query beside the
refresh design.

## Self-check

- Does a declared key uniquely identify every materialized row?
- Can the consumer tolerate the documented refresh interval and failure mode?

## Next step

Continue to [Day 37 — partitioning and sharding](day37_partitioning_sharding.md).

## Deep dive and reference

## What you will learn

- Store the result of an expensive query in a materialized view (MV).
- Refresh cached results when source tables change.
- Compare freshness, storage, and query cost with querying base tables.

## How the learner script uses the current schema

The script creates `mv_category_month_revenue` from `orders`, `order_items`, and
`products`. Its grain is one row per `(category, month)`, and revenue is line
price times quantity after discount. It queries and refreshes the MV, then rolls
the object back.

A normal view stores only SQL and executes it on every read. A materialized view
stores rows and can be indexed, but those rows are stale until refreshed.

## Refresh behavior

- `REFRESH MATERIALIZED VIEW` replaces the stored contents and blocks reads of
  that MV during refresh.
- `REFRESH ... CONCURRENTLY` permits reads but requires a qualifying unique
  index and cannot run inside an explicit transaction block.
- PostgreSQL does not provide general native incremental MV refresh; selective
  rollup tables are a separate design.

## Practice — match the learner prompts exactly

1. Create an MV for weekly revenue by `customers.country`. Use a clear grain of
   `(week, country)` and line-item net revenue.
2. Compare the same weekly-country query over base tables with a query over the
   MV. Capture actual plans, buffers, row counts, and freshness assumptions.

## Pitfalls and validation

- Reconcile the MV's total revenue to the source query before measuring speed.
- A fast stale result can be wrong for the consumer's freshness requirement.
- The compact seed may make the raw query as fast as or faster than the MV.
- Document refresh ownership and failure behavior before relying on an MV.
- The learner transaction safely removes the demonstration MV at rollback.
