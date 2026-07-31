# Day 31 — EXPLAIN and EXPLAIN ANALYZE

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 30 — Phase 2 project](day30_phase2_project.md), with
  confidence in joins, aggregates, CTEs, and result reconciliation
- **Artifacts:** [learner SQL](../day31_explain_analyze.sql) ·
  [solution reasoning](../solutions/day31_solutions.md) ·
  [executable solution](../solutions/day31_solutions.sql)

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

2. Open **SQL-31 — Explain Analyze** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-31/lesson/workspace/sql/postgres-60day/day31_explain_analyze.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day31_explain_analyze.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day31_explain_analyze.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Plan node, Cost estimate, Loop count. Its worked SQL reads or creates `orders`, `customers`, `order_items`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Run the same safe filter first with EXPLAIN and then with EXPLAIN (ANALYZE, BUFFERS). Start at the scan leaf, compare estimated rows with actual rows × loops, note rows removed by the filter, and only then read the parent LIMIT or aggregate node.
The first runnable example has a concrete contract: Example 1 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `order_id` key set and row count over `orders`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan. Its final projection is `order_id`, and `total_amount`. Run the underlying query without `EXPLAIN` first; preserve its keys and row count, then compare estimates with actual rows × loops and read buffer/timing evidence without requiring one fixed node type.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day31_explain_analyze.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
EXPLAIN SELECT o.order_id, o.total_amount FROM orders o WHERE o.total_amount > 500;
```

**How to read it:** Example 1 returns plan rows rather than business rows. The node tree is evidence about one execution strategy; it does not replace a correctness check on the underlying query.

**Expected result/shape:** Example 1 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `order_id` key set and row count over `orders`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

### Example 2

```sql
EXPLAIN ANALYZE SELECT o.order_id, o.total_amount FROM orders o WHERE o.total_amount > 500 LIMIT 100;
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
   **Inputs/evidence:** For sql-31 Exercise 1, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-31 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`, and `total_amount`.
   **Verify:** For sql-31 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
2. Compare `EXPLAIN` with `EXPLAIN ANALYZE`, including estimated/actual rows.
   **Inputs/evidence:** For sql-31 Exercise 2, run the underlying read-only query over `orders`, `customers`, and `order_items` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-31 Exercise 2, expected output: one row per `country`. The final columns are `country`, and `units`.
   **Verify:** For sql-31 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `country` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
3. Predict and compare plans for `total_amount > 0` and `> 900`.
   **Inputs/evidence:** For sql-31 Exercise 3, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-31 Exercise 3, expected output: one row per `order_id`. The final columns are `order_id`.
   **Verify:** For sql-31 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
4. Explain a country-filtered customer/orders join with `VERBOSE`.
   **Inputs/evidence:** For sql-31 Exercise 4, run the underlying read-only query over `customers`, and `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-31 Exercise 4, expected output: one row per `country`. The final columns are `country`, and `order_count`.
   **Verify:** For sql-31 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `country` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
5. Safely inspect a no-op `UPDATE` with `ANALYZE` and a savepoint.
   **Inputs/evidence:** For sql-31 Exercise 5, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-31 Exercise 5, expected output: one row per `order_id`. The final columns are `update`, and `analyze`.
   **Verify:** For sql-31 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
6. Test a zero-row predicate and interpret its estimate.
   **Inputs/evidence:** For sql-31 Exercise 6, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-31 Exercise 6, expected output: one row per `order_id`. The final columns are `order_id`.
   **Verify:** For sql-31 Exercise 6, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

Save one plan and a result-control query as the baseline for Day 32.

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

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-31 — Explain Analyze.

I have completed the direct catalog prerequisite: `sql-30`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day31_explain_analyze.md
- Answer-free learner SQL: sql/postgres-60day/day31_explain_analyze.sql

Key terms to teach in context: Plan node, Cost estimate, Loop count. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Run the same safe filter first with EXPLAIN and then with EXPLAIN (ANALYZE, BUFFERS). Start at the scan leaf, compare estimated rows with actual rows × loops, note rows removed by the filter, and only then read the parent LIMIT or aggregate node.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
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
