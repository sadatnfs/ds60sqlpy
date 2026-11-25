# Day 31: EXPLAIN and EXPLAIN ANALYZE

## How to run this lesson

Open **sql-31** in `./classroom` and run **Whole SQL lesson (psql)** against
`advanced_sql_training`. The file prints three plans and no business rows:
two over `orders` alone and one that joins `orders`, `customers` and
`order_items`. Only the second plan executes its query, and the whole file
ends in `ROLLBACK`. Your editable copy is
`.learning/sql/sql-31/lesson/workspace/sql/postgres-60day/day31_explain_analyze.sql`.
The shared launch steps are in
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Plan text lines are long. Widen the transcript pane or scroll sideways
before deciding that a `Filter:` or `Buffers:` line is missing.

### Optional contributor notebook route

A notebook keeps each plan in its own cell, which makes it easy to rerun
one `EXPLAIN` after an `ANALYZE orders;`
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-31
```

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 30; Phase 2 project](day30_phase2_project.md), with
  confidence in joins, aggregates, CTEs, and result reconciliation
- **Artifacts:** [learner SQL](../day31_explain_analyze.sql) ·
  [solution reasoning](../solutions/day31_solutions.md) ·
  [executable solution](../solutions/day31_solutions.sql)

## A beginner's mental model for this lesson

`EXPLAIN` asks PostgreSQL how it would run a query; `EXPLAIN ANALYZE` runs
the query and reports what happened. Each output line with `->` is a plan
node, and indentation shows which node feeds which. Rows flow upward: the
most indented scans produce rows, and every parent consumes its children.

Three numbers on each node carry most of the meaning:

| On the node | What it tells you | In the first plan of this lesson |
|---|---|---|
| `cost=a..b` | planner units for first row and all rows | `0.00..119.53` |
| `rows=` (estimate) | how many rows the planner expects | `2410` |
| `actual ... rows= loops=` | what really came out, per loop | only with `ANALYZE` |

Costs are not milliseconds. They are relative units built from page reads
and per-row CPU charges, useful only for comparing plans of the same query.
In the first plan, 65 of the 119.53 units are the 65 pages of `orders`;
the rest is per-row CPU for 4,362 rows and their filter checks.

The trap to avoid is comparing a plan to a different query. Every
comparison in this lesson keeps the `SELECT`, the tables and the data fixed
and changes one thing: a predicate, `ANALYZE`, or `LIMIT`. When rows look
wrong, run the same `SELECT` without `EXPLAIN` and count; the plan never
replaces that check.

## Two worked SQL examples

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

**How to read it:** One node, `Seq Scan on orders o`, with a
`Filter: (total_amount > '500'::numeric)` line beneath it. PostgreSQL has no
index on `total_amount`, so reading all 65 pages is the only option. The
query itself does not run, so the plan shows estimates and nothing else.

**Expected result/shape:** A two-line plan with an estimate of
`rows=2410`. Running `SELECT COUNT(*) FROM orders WHERE total_amount > 500`
also returns 2,410 on a fresh load, so the statistics are accurate here. A
very different estimate usually means `orders` has not been analyzed yet.

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

**How to read it:** Now `Limit` sits above the scan, and
`ANALYZE` adds an `actual` section to each node. The scan's estimate still
says 2,410 rows, but its actual count is only 100, because `Limit` stops
asking for rows once it has enough.

**Expected result/shape:** About `actual ... rows=100` on both
nodes and `Rows Removed by Filter: 83` on the scan: PostgreSQL read 183
orders, kept the first 100 that passed the filter, and stopped. The plan
cost drops to about 4.96 for the same reason. Which 100 orders you get is
not defined, because there is no `ORDER BY`.

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

The six numbered prompts above are the full practice set, and the
solution walks through each one; the third plan in the learner file (the
90-day join) is a warm-up for the fourth.

## Pitfalls and validation

- Do not compare timings from different predicates or different result sets.
- Warm cache, background activity, and the compact seed can change timings.
- Never use `EXPLAIN ANALYZE` on destructive production DML merely to see a
  plan; it executes the statement.
- Prefer `EXPLAIN (ANALYZE, BUFFERS)` when you need I/O evidence.

## Expanded practice lab

Prompts 3-6 add prediction, construction, debugging, and an empty-result edge
case. Read a plan from the most deeply indented node upward: scans produce rows,
joins combine them, aggregates reduce their grain, and the root returns the
final result. For each plan, record estimated versus actual rows before timing;
a fast plan can still expose a serious cardinality error.

Use a savepoint for the no-op `UPDATE` demonstration because `ANALYZE` executes
the statement. A zero-row predicate is not itself evidence of stale statistics:
compare the estimate, then distinguish a rare but modeled value from genuinely
outdated table statistics.

## Ask an AI tutor about this lesson

If a plan confuses you, a tutor can walk through it one node at a
time while you keep the actual row counts in front of you
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

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
