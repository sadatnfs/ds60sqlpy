# Day 37 — Partitioning and Sharding

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 36 — materialized views](day36_materialized_views.md)
- **Artifacts:** [learner SQL](../day37_partitioning_sharding.sql) ·
  [solution reasoning](../solutions/day37_solutions.md) ·
  [executable solution](../solutions/day37_solutions.sql)

## Learning objectives

- Define non-overlapping range partitions and prove pruning.
- Separate local partitioning mechanics from distributed sharding design.

## Vocabulary and concepts

- **Partition bound:** the lower-inclusive, upper-exclusive range accepted by a
  partition.
- **Partition pruning:** planner or executor removal of irrelevant partitions.
- **Sharding:** routing data across separate databases or servers.

## Worked example / walkthrough

Map the January and February bounds on a timeline, then plan a
January-15-to-February-15 query. Both partitions are required. Change the range
to a January-only half-open interval and inspect `EXPLAIN` to prove February is
pruned rather than assuming it.

## Exercises

Complete the prompts in the [learner SQL](../day37_partitioning_sharding.sql).
Test values exactly on every partition boundary and one value with no matching
partition.

## Self-check

- Are bounds complete and non-overlapping for the intended data?
- Does the plan show pruning, and is “sharding” kept as an architecture topic
  rather than claimed as implemented?

## Next step

Continue to [Day 38 — transactions and isolation](day38_transactions_isolation.md).

## Deep dive and reference

## What you will learn

- Create range partitions and verify partition pruning.
- Add partition-local indexes and compare access plans.
- Distinguish in-database partitioning from cross-database sharding.

## How the learner script works

The rollback-only demo creates `big_events` partitioned by `event_time`, with
January and February 2025 partitions. It inserts 1,000 deterministic rows across
those two months and plans a half-open January-15-to-February-15 count.

Partition pruning removes partitions whose bounds cannot satisfy a predicate.
Use the raw partition key in sargable ranges. Partitioning is primarily a data
management and scale technique; it does not guarantee a faster small-table
query.

## Partitioning versus sharding

- Partitioning divides one logical table inside one PostgreSQL database.
- Sharding routes data across databases or servers and changes joins,
  transactions, failure handling, and operations.
- The learner script demonstrates partitioning only. “Sharding” remains an
  architecture discussion, not a runnable course setup.

## Practice — match the learner prompts exactly

1. Add one or more new `big_events` partitions, insert matching rows, and use
   `EXPLAIN` to prove pruning for single- and multi-partition date ranges.
2. Create indexes on the relevant partitions and compare query plans for a
   selective event/customer lookup.

## Pitfalls and validation

- PostgreSQL range bounds are lower-inclusive and upper-exclusive.
- An inserted row with no matching partition fails unless a default partition
  exists.
- Too many tiny partitions increase planning and maintenance overhead.
- PostgreSQL indexes are implemented per partition; plan index creation for new
  partitions.
- All demo tables and indexes disappear at the learner script's `ROLLBACK`.
