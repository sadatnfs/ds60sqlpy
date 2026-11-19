# Day 37: Partitioning and Sharding

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-37**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. The **Course database** panel above the code shows whether the course
   training tables are loaded. Missing tables load automatically before your
   first run (or choose **Load course tables**) and stay loaded for later
   lessons. **Reset training data** restores the original rows only when your
   own changes made results differ; it keeps your saved code and notes.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-37/lesson/workspace/sql/postgres-60day/day37_partitioning_sharding.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-37
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 36; materialized views](day36_materialized_views.md)
- **Artifacts:** [learner SQL](../day37_partitioning_sharding.sql) ·
  [solution reasoning](../solutions/day37_solutions.md) ·
  [executable solution](../solutions/day37_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Partition bound, Partition pruning, Sharding. Its worked SQL reads or creates `big_events`, `big_events_2025_01`, `big_events_2025_02`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Map the January and February bounds on a timeline, then plan a January-15-to-February-15 query. Both partitions are required. Change the range to a January-only half-open interval and inspect `EXPLAIN` to prove February is pruned rather than assuming it.
The learner script loads 1,000 rows, 537 in January and 463 in February, then
plans two counts. The first worked example spans both months, so neither
partition can be pruned; the second stays inside January, so the plan reads
only the January partition.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day37_partitioning_sharding.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

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

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

Prompts 3–6 turn partition pruning into observable evidence. Compare plans with
and without the partition-key predicate and inspect `tableoid::regclass` to see
physical row placement. Add the DEFAULT partition only after observing the
helpful “no partition found” error for an uncovered date.

Range bounds are `[FROM, TO)`: midnight on February 1 belongs to the February
partition, not January. A DEFAULT partition improves ingest availability but
also needs monitoring so unexpected dates do not accumulate unnoticed.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

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
