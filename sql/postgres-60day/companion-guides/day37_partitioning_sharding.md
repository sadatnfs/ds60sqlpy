# Day 37 — Partitioning and Sharding

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 36 — materialized views](day36_materialized_views.md)
- **Artifacts:** [learner SQL](../day37_partitioning_sharding.sql) ·
  [solution reasoning](../solutions/day37_solutions.md) ·
  [executable solution](../solutions/day37_solutions.sql)

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-37 — Partitioning Sharding** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-37/day37_partitioning_sharding.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day37_partitioning_sharding.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day37_partitioning_sharding.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. This lesson introduces or reinforces
Partition bound, Partition pruning, Sharding. Its worked SQL reads or creates `big_events`, `big_events_2025_01`, `big_events_2025_02`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Map the January and February bounds on a timeline, then plan a January-15-to-February-15 query. Both partitions are required. Change the range to a January-only half-open interval and inspect EXPLAIN to prove February is pruned rather than assuming it.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day37_partitioning_sharding.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TABLE big_events (
  id BIGSERIAL,
  event_time TIMESTAMPTZ NOT NULL,
  customer_id INT,
  payload JSONB
) PARTITION BY RANGE (event_time);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
CREATE TABLE big_events_2025_01 PARTITION OF big_events
  FOR VALUES FROM ('2025-01-01 00:00:00+00') TO ('2025-02-01 00:00:00+00');
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Add local indexes and compare plans.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
3. Predict partition scans with and without a time predicate.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Add a DEFAULT partition and inspect row placement via `tableoid`.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
5. Diagnose an insert into an uncovered range.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
6. Test the inclusive-FROM/exclusive-TO boundary at February 1.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

Test every boundary and one value without a matching named partition.

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

## Expanded practice lab

Prompts 3–6 turn partition pruning into observable evidence. Compare plans with
and without the partition-key predicate and inspect `tableoid::regclass` to see
physical row placement. Add the DEFAULT partition only after observing the
helpful “no partition found” error for an uncovered date.

Range bounds are `[FROM, TO)`: midnight on February 1 belongs to the February
partition, not January. A DEFAULT partition improves ingest availability but
also needs monitoring so unexpected dates do not accumulate unnoticed.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-37 — Partitioning Sharding.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day37_partitioning_sharding.md
- Answer-free learner SQL: sql/postgres-60day/day37_partitioning_sharding.sql

The lesson concepts include Partition bound, Partition pruning, Sharding. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Map the January and February bounds on a timeline, then plan a January-15-to-February-15 query. Both partitions are required. Change the range to a January-only half-open interval and inspect EXPLAIN to prove February is pruned rather than assuming it.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-37/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
