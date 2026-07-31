# Day 35 — Avoiding Common Performance Pitfalls

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 34 — query optimization](day34_query_optimization.md)
- **Artifacts:** [learner SQL](../day35_avoiding_pitfalls.sql) ·
  [solution reasoning](../solutions/day35_solutions.md) ·
  [executable solution](../solutions/day35_solutions.sql)

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

2. Open **SQL-35 — Avoiding Pitfalls** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-35/lesson/workspace/sql/postgres-60day/day35_avoiding_pitfalls.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day35_avoiding_pitfalls.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day35_avoiding_pitfalls.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Sargability, Half-open range, Set-based rewrite. Its worked SQL reads or creates `orders`, `customers`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Compare datetrunc('day', orderdate) = targetday with orderdate >= targetday AND orderdate < targetday + interval '1 day'. Test timestamps at both boundaries, reconcile row IDs, and compare plans with a matching orderdate index.
The first runnable example has a concrete contract: Example 1 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its the primary/business key of `orders` key set and row count over `orders`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan. Its final projection is `*`. Run the underlying query without `EXPLAIN` first; preserve its keys and row count, then compare estimates with actual rows × loops and read buffer/timing evidence without requiring one fixed node type.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day35_avoiding_pitfalls.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE date_trunc('day', order_date) = date_trunc('day', now());
```

**How to read it:** Example 1 returns plan rows rather than business rows. The node tree is evidence about one execution strategy; it does not replace a correctness check on the underlying query.

**Expected result/shape:** Example 1 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its the primary/business key of `orders` key set and row count over `orders`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

### Example 2

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE order_date >= date_trunc('day', now()) AND order_date < date_trunc('day', now()) + interval '1 day';
```

**How to read it:** Example 2 returns plan rows rather than business rows. The node tree is evidence about one execution strategy; it does not replace a correctness check on the underlying query.

**Expected result/shape:** Example 2 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its the primary/business key of `orders` key set and row count over `orders`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

## Learning objectives

- Rewrite non-sargable temporal predicates as correct raw-column ranges.
- Replace repeated correlated work with one set-based aggregation.

## Vocabulary and concepts

- **Sargability:** whether a predicate can use an index's search ordering.
- **Half-open range:** `>= start AND < end`, suitable for adjacent periods.
- **Set-based rewrite:** compute a relation once rather than once per outer row.

## Worked example / walkthrough

Compare `date_trunc('day', order_date) = target_day` with
`order_date >= target_day AND order_date < target_day + interval '1 day'`.
Test timestamps at both boundaries, reconcile row IDs, and compare plans with a
matching `order_date` index.

## Exercises

Complete these in the [learner SQL](../day35_avoiding_pitfalls.sql):

1. Rewrite three non-sargable predicates.
   **Inputs/evidence:** For sql-35 Exercise 1, run the underlying read-only query over `orders`, `order_date`, and `CURRENT_DATE` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-35 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`.
   **Verify:** For sql-35 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
2. Replace correlated aggregates with one pre-aggregation and join.
   **Inputs/evidence:** For sql-35 Exercise 2, run the underlying read-only query over `orders`, and `customers` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-35 Exercise 2, expected output: one row per customer in both forms. The `LEFT JOIN` is required to retain customers with no orders; changing it to an inner join would alter the answer. The final columns are `customer_id`, and `lifetime_revenue`.
   **Verify:** For sql-35 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
3. Predict B-tree usefulness for prefix versus leading-wildcard patterns.
   **Inputs/evidence:** For sql-35 Exercise 3, run the underlying read-only query over `customers` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-35 Exercise 3, expected output: one row per `customer_id`. The final columns are `customer_id`.
   **Verify:** For sql-35 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
4. Replace `OFFSET` paging with deterministic keyset paging.
   **Inputs/evidence:** For sql-35 Exercise 4, read from `orders`. Build the answer toward `order_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-35 Exercise 4, expected output: at most 20 rows keyed by `order_id`. The final columns are `order_id`, and `order_date`. The final order is `o.order_date DESC, o.order_id DESC`.
   **Verify:** For sql-35 Exercise 4, assert no more than 20 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_date DESC, o.order_id DESC`. Rejoin the returned keys to `orders` to confirm `order_id`, and `order_date` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_date DESC, o.order_id DESC`.
5. Repair payment/item fanout.
   **Inputs/evidence:** For sql-35 Exercise 5, read from `payments`, `order_items`, and `orders`. Build the answer toward `order_id`, `paid`, and `sold`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-35 Exercise 5, expected output: at most 20 rows keyed by `order_id`. The final columns are `order_id`, `paid`, and `sold`. The final order is `o.order_id`.
   **Verify:** For sql-35 Exercise 5, assert no more than 20 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_id`. Rejoin the returned keys to `payments`, `order_items`, and `orders` to confirm `order_id`, `paid`, and `sold` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_id`.
6. Explain `COUNT(*)` versus `COUNT(email)` with NULLs.
   **Inputs/evidence:** For sql-35 Exercise 6, read from `customers`. Build the answer toward `customer_rows`, `customers_with_email`, and `customers_without_email`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-35 Exercise 6, expected output: one row per `customer_id`. The final columns are `customer_rows`, `customers_with_email`, and `customers_without_email`.
   **Verify:** For sql-35 Exercise 6, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_rows`, `customers_with_email`, and `customers_without_email` against `customers`. Repeat with `NULL` in `customer_rows`, and `customers_with_email` and state whether the row is kept, rejected, or classified.

Add an edge-case result check before every performance comparison.

## Self-check

- Does the range preserve the intended time-zone and boundary semantics?
- Does a set-based rewrite retain outer entities with no matching facts when
  required?

## Next step

Continue to [Day 36 — materialized views](day36_materialized_views.md).

## Deep dive and reference

## What you will learn

- Recognize function-wrapped predicates that are hard to index.
- Replace per-row correlated aggregation with one set-based aggregation.
- Preserve correctness while reducing repeated work.

## How the learner script uses the current schema

The first pair compares `date_trunc('day', order_date) = ...` with a half-open
range on raw `orders.order_date`. The second pair compares a customer-by-customer
correlated sum with one grouped `orders` CTE joined to `customers`.

The half-open range is:

`order_date >= start_of_day AND order_date < start_of_next_day`

It handles every timestamp in the day and can match a normal B-tree index on
`order_date`.

## Why the set-based rewrite helps

The correlated form can execute an order scan once per customer. The grouped
form scans and aggregates orders once, then joins one row per customer. A
`LEFT JOIN` retains customers with no orders; decide whether the displayed
value should remain `NULL` or become zero.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Pitfalls and validation

- Do not rewrite a predicate unless time zone and inclusive/exclusive boundaries
  remain correct.
- Functions are not universally bad; a matching expression index can be valid
  when the expression is the real search key.
- Preserve outer-join behavior for entities with no facts.
- Compare result keys and totals before comparing timing.

## Expanded practice lab

Prompts 3–6 cover four common production surprises: leading-wildcard searches,
deep `OFFSET` pages, fanout, and nullable counts. Keyset pagination must use a
unique deterministic tuple such as `(order_date, order_id)` and repeat the same
ordering in the seek predicate.

Fix fanout at the grain boundary instead of hiding it with `DISTINCT`.
`COUNT(*)` counts rows; `COUNT(email)` counts only non-NULL emails. Neither is
universally “correct”—the metric definition decides.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-35 — Avoiding Pitfalls.

I have completed the direct catalog prerequisite: `sql-34`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day35_avoiding_pitfalls.md
- Answer-free learner SQL: sql/postgres-60day/day35_avoiding_pitfalls.sql

Key terms to teach in context: Sargability, Half-open range, Set-based rewrite. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Compare datetrunc('day', orderdate) = targetday with orderdate >= targetday AND orderdate < targetday + interval '1 day'. Test timestamps at both boundaries, reconcile row IDs, and compare plans with a matching orderdate index.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-35/ working copy. Never point setup, reset, DDL, or DML
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
