# Day 37: Partitioning and Sharding

## How to run this lesson

Start `./classroom`, pick **sql-37** and run **Whole SQL lesson (psql)**.
The learner file creates `big_events` with a January and a February 2025
partition, loads 1,000 rows, prints two plans and then rolls back, so no
partition survives the run. Your editable copy lives at
`.learning/sql/sql-37/lesson/workspace/sql/postgres-60day/day37_partitioning_sharding.sql`
and connects to `advanced_sql_training`. Launch details are in
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Nothing in this lesson reads the course tables; the fixture is built
inside the transaction. If `CREATE TABLE big_events` fails because the name
already exists, an earlier run committed by mistake, so drop that table
before trusting any plan.

### Optional contributor notebook route

A notebook is handy for editing one bound and replanning without rerunning
the load
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-37
```

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 36; materialized views](day36_materialized_views.md)
- **Artifacts:** [learner SQL](../day37_partitioning_sharding.sql) ·
  [solution reasoning](../solutions/day37_solutions.md) ·
  [executable solution](../solutions/day37_solutions.sql)

## A beginner's mental model for this lesson

A partitioned table such as `big_events` holds no rows itself. It is a
router: every insert is sent to the one child table whose bound contains
the row's `event_time`, and every query is answered by the children the
planner keeps. The children are ordinary tables, so you can count them
directly or ask any row where it lives with `tableoid::regclass`.

The learner load steps forward 83 minutes per row from midnight on
January 1, which places 537 rows in `big_events_2025_01` and 463 in
`big_events_2025_02`; the last one lands on February 27 at 15:20 UTC. The
two planned counts differ only in their upper bound. Mid-January to
mid-February crosses the partition line and returns 538. Stopping on
January 20 keeps the range inside one child and returns 87.

A **partition bound** decides placement, and **partition pruning** is the
planner reading those bounds against your `WHERE` clause. Pruning needs
the raw key: `WHERE date_trunc('month', event_time) = '2025-01-01'` still
scans both children, because the planner cannot invert the function to
compare it with a bound. Rewrite it as a half-open range on `event_time`
and February disappears from the plan.

## Two worked SQL examples

### Example 1: a range that needs both partitions

```sql
EXPLAIN ANALYZE
SELECT
  COUNT(*)
FROM
  big_events
WHERE
  event_time >= timestamptz '2025-01-15 00:00:00+00'
  AND event_time < timestamptz '2025-02-15 00:00:00+00';
```

**How to read it:** the half-open range `[2025-01-15, 2025-02-15)` overlaps the
January partition `[2025-01-01, 2025-02-01)` and the February partition
`[2025-02-01, 2025-03-01)`. The planner therefore keeps both partitions under
one `Append` node and applies the `Filter` inside each scan. The literals carry
an explicit `+00` offset, so the result does not depend on the session time
zone.

**Expected result/shape:** `EXPLAIN ANALYZE` prints one text column,
`QUERY PLAN`. On the course seed it shows an `Append` with two scans:
`big_events_2025_01` with `actual ... rows=295` and `big_events_2025_02` with
`actual ... rows=243`. Running the query without `EXPLAIN` returns one row whose
count is `538`.

### Example 2: a January-only range is pruned

```sql
EXPLAIN ANALYZE
SELECT
  COUNT(*)
FROM
  big_events
WHERE
  event_time >= timestamptz '2025-01-15 00:00:00+00'
  AND event_time < timestamptz '2025-01-20 00:00:00+00';
```

**How to read it:** the only change is the upper bound. No February timestamp
can satisfy `event_time < '2025-01-20'`, so the planner removes
`big_events_2025_02` before execution. This is partition pruning: the evidence
is the partition name that is missing from the plan, not a faster timing.

**Expected result/shape:** the plan has no `Append` node and one scan,
`Seq Scan on big_events_2025_01`, with `actual ... rows=87`. Running the query
without `EXPLAIN` returns one row whose count is `87`.

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

Complete these in the [learner SQL](../day37_partitioning_sharding.sql):

1. Add partitions and test pruning.
   **Inputs/evidence:** For sql-37 Exercise 1, extend `solution_events` (January and February partitions) with March and April partitions, load the 5,000 deterministic rows spread from 2025-01-01 to 2025-04-30, then run `EXPLAIN (ANALYZE, BUFFERS)` on a March-only `COUNT(*)` with constant `timestamptz` bounds.
   **Expected result/shape:** For sql-37 Exercise 1, expected output: a plan whose only scan node reads `solution_events_2025_03`, with `actual ... rows=950`; January, February, and April are pruned at planning time. `EXPLAIN` prints one text column named `QUERY PLAN`, not business rows.
   **Verify:** For sql-37 Exercise 1, run the same `SELECT COUNT(*)` without `EXPLAIN` and confirm it returns `950`, the scan node's actual rows; then plan a count with no `WHERE` clause and confirm that all four monthly partitions appear under one `Append` node.
2. Add local indexes and compare plans.
   **Inputs/evidence:** For sql-37 Exercise 2, create one index on the partitioned parent, `solution_events (customer_id, event_time)`, then run `EXPLAIN (ANALYZE, BUFFERS)` on `SELECT *` for `customer_id = 42` in March.
   **Expected result/shape:** For sql-37 Exercise 2, expected output: `pg_indexes` lists the parent index plus one `(customer_id, event_time)` index for each of the four monthly partitions, and the plan reads only `solution_events_2025_03`, returning `rows=2`. On this seed the scan uses `solution_events_2025_03_customer_id_event_time_idx`; another access path is acceptable when statistics differ.
   **Verify:** For sql-37 Exercise 2, query `SELECT tablename, indexname FROM pg_indexes WHERE tablename LIKE 'solution_events%' ORDER BY tablename` and confirm five rows; then run the query without `EXPLAIN` and confirm it returns the same two rows that the plan reports.
3. Predict partition scans with and without a time predicate.
   **Inputs/evidence:** For sql-37 Exercise 3, run plain `EXPLAIN` (without `ANALYZE`) on `SELECT COUNT(*) FROM solution_events` with no predicate, then on the same count restricted to the March half-open range.
   **Expected result/shape:** For sql-37 Exercise 3, expected output: the unfiltered plan lists four scans, one per monthly partition, under one `Append`; the March plan lists only `solution_events_2025_03` and has no `Append` node.
   **Verify:** For sql-37 Exercise 3, write the predicted number of scanned partitions (4 and 1) before running both plans, then count the `Seq Scan on solution_events_...` lines in each plan and compare them with the prediction.
4. Add a DEFAULT partition and inspect row placement via `tableoid`.
   **Inputs/evidence:** For sql-37 Exercise 4, add `solution_events_default` as the DEFAULT partition and insert one event dated `2025-06-15 00:00:00+00`, which no monthly partition covers.
   **Expected result/shape:** For sql-37 Exercise 4, expected output: one row, `physical_partition` = `solution_events_default` and `event_time` = `2025-06-15 00:00:00+00`.
   **Verify:** For sql-37 Exercise 4, before the DEFAULT partition exists, the same insert fails with SQLSTATE `23514` (`no partition of relation "solution_events" found for row`); after it exists, `SELECT COUNT(*) FROM solution_events_default` returns `1`.
5. Diagnose an insert into an uncovered range.
   **Inputs/evidence:** For sql-37 Exercise 5, list the leaf partitions of `solution_events` and their bounds from `pg_partition_tree('solution_events')` joined to `pg_class`, after Exercises 1 to 4 created four monthly partitions and the DEFAULT partition.
   **Expected result/shape:** For sql-37 Exercise 5, expected output: five rows ordered by `c.relname`, with columns `partition_name` and `partition_bound`: four `FOR VALUES FROM (...) TO (...)` rows for January to April and one `DEFAULT` row for `solution_events_default`.
   **Verify:** For sql-37 Exercise 5, compare the bound text with the dates you wrote in Exercise 1; then, in a scratch transaction before any DEFAULT partition exists, insert a `2025-07-01 00:00:00+00` row and confirm SQLSTATE `23514`, which this catalog query explains because no listed bound covers July.
6. Test the inclusive-FROM/exclusive-TO boundary at February 1.
   **Inputs/evidence:** For sql-37 Exercise 6, insert one row at exactly `2025-02-01 00:00:00+00` with `payload` `{"source":"boundary"}`, then read it back by that payload value.
   **Expected result/shape:** For sql-37 Exercise 6, expected output: one row, `physical_partition` = `solution_events_2025_02` and `event_time` = `2025-02-01 00:00:00+00`, because `FROM` bounds are inclusive and `TO` bounds are exclusive.
   **Verify:** For sql-37 Exercise 6, insert a second row at `2025-01-31 23:59:59.999999+00` and confirm that `tableoid::regclass` reports `solution_events_2025_01` for it, so the two instants one microsecond apart land in different partitions.

Test every boundary and one value without a matching named partition.

## Self-check

- Are bounds complete and non-overlapping for the intended data?
- Does the plan show pruning, and is “sharding” kept as an architecture topic
  rather than claimed as implemented?

## Next step

Continue to [Day 38; transactions and isolation](day38_transactions_isolation.md).

## Deep dive and reference

## What you will learn

- Create range partitions and verify partition pruning.
- Add partition-local indexes and compare access plans.
- Distinguish in-database partitioning from cross-database sharding.

## How the learner script works

The rollback-only demo creates `big_events` partitioned by `event_time`, with
January and February 2025 partitions. It inserts 1,000 deterministic rows, one
every 83 minutes (537 in January and 463 in February), then plans a
January-15-to-February-15 count that needs both partitions and a January-only
count that prunes February.

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

## Practice map

The exercises switch to a second table, `solution_events`, so your
answers never collide with the demo. Its loader steps 47 minutes per row
over a 120-day window and wraps once after about row 3,676, so January ends
up with 1,899 rows while March has 950 and April 919. Expect lopsided
months, and use the March count of 950 as your anchor across the first
three prompts.

## Pitfalls and validation

- PostgreSQL range bounds are lower-inclusive and upper-exclusive.
- An inserted row with no matching partition fails unless a default partition
  exists.
- Too many tiny partitions increase planning and maintenance overhead.
- An index created on the partitioned parent is created on every partition,
  including partitions attached later; each partition stores its own physical
  index. `CREATE INDEX CONCURRENTLY` cannot target the parent, so large online
  builds use `CREATE INDEX ... ON ONLY` plus `ALTER INDEX ... ATTACH PARTITION`.
- All demo tables and indexes disappear at the learner script's `ROLLBACK`.

## Expanded practice lab

Prompts 3-6 turn partition pruning into observable evidence. Compare plans with
and without the partition-key predicate and inspect `tableoid::regclass` to see
physical row placement. Add the DEFAULT partition only after observing the
helpful “no partition found” error for an uncovered date.

Range bounds are `[FROM, TO)`: midnight on February 1 belongs to the February
partition, not January. A DEFAULT partition improves ingest availability but
also needs monitoring so unexpected dates do not accumulate unnoticed.

## Ask an AI tutor about this lesson

A tutor can hand you a date range and ask which partitions it needs
before you plan it, or pose a bound such as midnight on March 1 and ask
which child gets it. Set one up with the
[AI tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional) and paste
this prompt:

```text
Tutor me through sql-37: Partitioning and Sharding.

I have completed the direct catalog prerequisite: `sql-36`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day37_partitioning_sharding.md
- Answer-free learner SQL: sql/postgres-60day/day37_partitioning_sharding.sql

Key terms to teach in context: Partition bound, Partition pruning, Sharding. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Map the January and February bounds on a timeline, then plan a January-15-to-February-15 query. Both partitions are required. Change the range to a January-only half-open interval and inspect `EXPLAIN` to prove February is pruned rather than assuming it.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-37/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
