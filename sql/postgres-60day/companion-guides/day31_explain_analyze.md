# Day 31: EXPLAIN and EXPLAIN ANALYZE

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-31**. The
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
   `.learning/sql/sql-31/lesson/workspace/sql/postgres-60day/day31_explain_analyze.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-31
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
- **Prerequisites:** [Day 30; Phase 2 project](day30_phase2_project.md), with
  confidence in joins, aggregates, CTEs, and result reconciliation
- **Artifacts:** [learner SQL](../day31_explain_analyze.sql) ·
  [solution reasoning](../solutions/day31_solutions.md) ·
  [executable solution](../solutions/day31_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Plan node, Cost estimate, Loop count. Its worked SQL reads or creates `orders`, `customers`, `order_items`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Run the same safe filter first with `EXPLAIN` and then with `EXPLAIN (ANALYZE, BUFFERS)`. Start at the scan leaf, compare estimated rows with `actual rows × loops`, note rows removed by the filter, and only then read the parent `LIMIT` or aggregate node.
The first runnable example has a concrete contract: Example 1 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `order_id` key set and row count over `orders`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan. Its final projection is `order_id`, and `total_amount`. Run the underlying query without `EXPLAIN` first; preserve its keys and row count, then compare estimates with actual rows × loops and read buffer/timing evidence without requiring one fixed node type.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day31_explain_analyze.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
EXPLAIN
SELECT
  o.order_id,
  o.total_amount
FROM
  orders o
WHERE
  o.total_amount > 500;
```

**How to read it:** Example 1 returns plan rows rather than business rows. The node tree is evidence about one execution strategy; it does not replace a correctness check on the underlying query.

**Expected result/shape:** Example 1 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `order_id` key set and row count over `orders`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

### Example 2

```sql
EXPLAIN ANALYZE
SELECT
  o.order_id,
  o.total_amount
FROM
  orders o
WHERE
  o.total_amount > 500
LIMIT 100;
```

**How to read it:** Example 2 returns plan rows rather than business rows. The node tree is evidence about one execution strategy; it does not replace a correctness check on the underlying query.

**Expected result/shape:** Example 2 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `order_id` key set and row count over `orders`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

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

Complete these in the [learner SQL](../day31_explain_analyze.sql):

1. Add predicates and observe selectivity effects.
   **Inputs/evidence:** For sql-31 Exercise 1, plan `SELECT * FROM orders` twice with `EXPLAIN (ANALYZE, BUFFERS)`: once with the broad filter `order_date >= CURRENT_TIMESTAMP - interval '3 years'`, and once with a selective filter that adds `status = 'returned'` and `total_amount >= 1000` to a 7-day window.
   **Expected result/shape:** For sql-31 Exercise 1, expected output: two plans, each a `Seq Scan on orders` with a `Filter` line; the broad plan reports thousands of actual rows (4,247 of 4,362 on a freshly seeded database) and the selective plan reports `actual ... rows=0`. Both read the same `Buffers: shared hit=` count, because a sequential scan reads every page whatever the filter keeps.
   **Verify:** For sql-31 Exercise 1, run `SELECT COUNT(*)` with each `WHERE` clause and no `EXPLAIN`, and confirm it equals the plan's actual rows; for each plan, actual rows plus `Rows Removed by Filter` must equal `SELECT COUNT(*) FROM orders` (4,362).
2. Compare `EXPLAIN` with `EXPLAIN ANALYZE`, including estimated/actual rows.
   **Inputs/evidence:** For sql-31 Exercise 2, plan the same revenue query, `SELECT c.country, SUM(o.total_amount) AS revenue FROM customers c JOIN orders o ON o.customer_id = c.customer_id GROUP BY c.country`, first with plain `EXPLAIN` and then with `EXPLAIN (ANALYZE, BUFFERS)`.
   **Expected result/shape:** For sql-31 Exercise 2, expected output: the same plan tree twice (on the course seed a `HashAggregate` above a `Hash Join`); only the second adds `actual time=... rows=... loops=...`, `Buffers:` lines, `Planning Time`, and `Execution Time`. The aggregate's actual rows are `7`, one per customer country, against an estimate of `8`.
   **Verify:** For sql-31 Exercise 2, run the query without `EXPLAIN` and confirm it returns 7 rows with columns `country` and `revenue`, matching the aggregate node's actual rows; then compare each node's estimated `rows=` with its actual rows multiplied by `loops`.
3. Predict and compare plans for `total_amount > 0` and `> 900`.
   **Inputs/evidence:** For sql-31 Exercise 3, predict which predicate has the smaller row estimate, then run `EXPLAIN (ANALYZE, BUFFERS) SELECT order_id FROM orders WHERE total_amount > 0` and the same query with `total_amount > 900`.
   **Expected result/shape:** For sql-31 Exercise 3, expected output: with current statistics, `total_amount > 0` is estimated at `rows=4362` and returns 4,362 actual rows, while `total_amount > 900` is estimated near `rows=593` and returns 605; both plans report the same `shared hit` count because both are sequential scans.
   **Verify:** For sql-31 Exercise 3, confirm the actual counts with `SELECT COUNT(*) FILTER (WHERE total_amount > 0), COUNT(*) FILTER (WHERE total_amount > 900) FROM orders` (4,362 and 605); if both estimates are identical (for example `rows=1454`), the table has no statistics yet, so run `ANALYZE orders;` and plan again.
4. Explain a country-filtered customer/orders join with `VERBOSE`.
   **Inputs/evidence:** For sql-31 Exercise 4, run `EXPLAIN (ANALYZE, BUFFERS, VERBOSE)` on `SELECT c.country, COUNT(*) AS order_count FROM customers c JOIN orders o ON o.customer_id = c.customer_id WHERE c.country = 'US' GROUP BY c.country`.
   **Expected result/shape:** For sql-31 Exercise 4, expected output: on the course seed, a `GroupAggregate` root with 1 actual row, a `Hash Join` with 625 actual rows, a filtered `Seq Scan on training.customers` with 63 actual rows, and a `Seq Scan on training.orders` with 4,362 rows; `VERBOSE` adds `Output:` lines and schema-qualified relation names.
   **Verify:** For sql-31 Exercise 4, run the query without `EXPLAIN` and confirm one row, `('US', 625)`; then confirm that `SELECT COUNT(*) FROM customers WHERE country = 'US'` returns 63, the actual rows of the `customers` scan.
5. Safely inspect a no-op `UPDATE` with `ANALYZE` and a savepoint.
   **Inputs/evidence:** For sql-31 Exercise 5, inside the lesson transaction, set a savepoint, run `EXPLAIN (ANALYZE, BUFFERS) UPDATE orders SET status = status WHERE order_id = -1`, then roll back to the savepoint and release it.
   **Expected result/shape:** For sql-31 Exercise 5, expected output: an `Update on orders` node above an `Index Scan using orders_pkey`, whose actual rows are `0` because no order has `order_id = -1`. The `UPDATE` really executed; only the impossible key and the savepoint keep it harmless.
   **Verify:** For sql-31 Exercise 5, confirm that `SELECT COUNT(*) FROM orders` returns 4,362 before and after the rollback; in a scratch transaction, compare `SELECT xmin FROM orders WHERE order_id = 1` before and after `EXPLAIN ANALYZE UPDATE orders SET status = status WHERE order_id = 1`: the `xmin` changes, which proves that `ANALYZE` wrote a new row version, then roll back.
6. Test a zero-row predicate and interpret its estimate.
   **Inputs/evidence:** For sql-31 Exercise 6, plan `SELECT order_id FROM orders WHERE total_amount < 0` with `EXPLAIN (ANALYZE, BUFFERS)`.
   **Expected result/shape:** For sql-31 Exercise 6, expected output: `actual ... rows=0` with `Rows Removed by Filter: 4362`, and an estimate of `rows=1` when statistics exist, because the planner never estimates fewer than one row. The seed simply contains no negative totals; `orders.total_amount` has no `CHECK` constraint.
   **Verify:** For sql-31 Exercise 6, confirm that `SELECT MIN(total_amount) FROM orders` is positive (20.74 on the course seed) and that `SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid = 'orders'::regclass` lists only the primary key and the foreign key; then compare the estimate with and without statistics to separate missing statistics from rare data.

Save one plan and a result-control query as the baseline for Day 32.

## Self-check

- Can you distinguish estimated cost from measured time?
- Have you verified that every `EXPLAIN ANALYZE` statement is safe to execute?

## Next step

Continue to [Day 32; index fundamentals](day32_index_fundamentals.md).

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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Pitfalls and validation

- Do not compare timings from different predicates or different result sets.
- Warm cache, background activity, and the compact seed can change timings.
- Never use `EXPLAIN ANALYZE` on destructive production DML merely to see a
  plan; it executes the statement.
- Prefer `EXPLAIN (ANALYZE, BUFFERS)` when you need I/O evidence.

## Expanded practice lab

Prompts 3–6 add prediction, construction, debugging, and an empty-result edge
case. Read a plan from the most deeply indented node upward: scans produce rows,
joins combine them, aggregates reduce their grain, and the root returns the
final result. For each plan, record estimated versus actual rows before timing;
a fast plan can still expose a serious cardinality error.

Use a savepoint for the no-op `UPDATE` demonstration because `ANALYZE` executes
the statement. A zero-row predicate is not itself evidence of stale statistics:
compare the estimate, then distinguish a rare but modeled value from genuinely
outdated table statistics.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-31: Reading Plans with EXPLAIN and EXPLAIN ANALYZE.

I have completed the direct catalog prerequisite: `sql-30`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day31_explain_analyze.md
- Answer-free learner SQL: sql/postgres-60day/day31_explain_analyze.sql

Key terms to teach in context: Plan node, Cost estimate, Loop count. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Run the same safe filter first with `EXPLAIN` and then with `EXPLAIN (ANALYZE, BUFFERS)`. Start at the scan leaf, compare estimated rows with `actual rows × loops`, note rows removed by the filter, and only then read the parent `LIMIT` or aggregate node.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-31/ working copy. Never point setup, reset, DDL, or DML
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
