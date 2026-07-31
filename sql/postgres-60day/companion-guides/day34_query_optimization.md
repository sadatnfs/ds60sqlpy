# Day 34 — Query Optimization Techniques

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 33 — composite, covering, and partial indexes](day33_index_optimization_strategies.md)
- **Artifacts:** [learner SQL](../day34_query_optimization.sql) ·
  [solution reasoning](../solutions/day34_solutions.md) ·
  [executable solution](../solutions/day34_solutions.sql)

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

2. Open **SQL-34 — Query Optimization** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-34/lesson/workspace/sql/postgres-60day/day34_query_optimization.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day34_query_optimization.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day34_query_optimization.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Baseline, Predicate pushdown, Semantic equivalence. Its worked SQL reads or creates `orders`, `customers`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Capture a baseline and control totals, replace a repeated scalar aggregate with one grouped relation, and join it back. Recheck keys and totals before comparing plans; a faster query that silently drops zero-order customers is not an optimization of the same requirement.
The first runnable example has a concrete contract: Example 1 returns one grouped row per `order_id`, `customer_id`, and `country` with columns `order_id`, `customer_id`, and `country` from `orders`, and `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `country`. Independently group `orders`, `filtered_orders`, and `customers` by the shown grouping expressions and compare every displayed aggregate at that exact grain. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day34_query_optimization.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH filtered_orders AS (
  SELECT order_id, customer_id FROM orders WHERE order_date >= now() - interval '30 days'
)
SELECT c.country, COUNT(*)
FROM filtered_orders fo
JOIN customers c ON c.customer_id = fo.customer_id
GROUP BY c.country
ORDER BY COUNT(*) DESC;
```

**How to read it:** Example 1: Start with `orders`, and `customers` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `country`. `ORDER BY` determines presentation order. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `order_id`, `customer_id`, and `country` with columns `order_id`, `customer_id`, and `country` from `orders`, and `customers`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
EXPLAIN ANALYZE
SELECT o.order_id, o.customer_id
FROM orders o
WHERE o.order_date >= now() - interval '7 days';
```

**How to read it:** Example 2 returns plan rows rather than business rows. The node tree is evidence about one execution strategy; it does not replace a correctness check on the underlying query.

**Expected result/shape:** Example 2 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `order_id`, and `customer_id` key set and row count over `orders`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

## Learning objectives

- Optimize one measured bottleneck while preserving result semantics.
- Reduce repeated work through early safe filtering, narrower projection, or
  pre-aggregation.

## Vocabulary and concepts

- **Baseline:** the controlled query, data, plan, and result used for comparison.
- **Predicate pushdown:** evaluating a safe filter closer to its source.
- **Semantic equivalence:** two queries returning the same defined result.

## Worked example / walkthrough

Capture a baseline and control totals, replace a repeated scalar aggregate with
one grouped relation, and join it back. Recheck keys and totals before comparing
plans; a faster query that silently drops zero-order customers is not an
optimization of the same requirement.

## Exercises

Complete these in the [learner SQL](../day34_query_optimization.sql):

1. Replace a scalar/correlated subquery with a join and compare plans.
   **Inputs/evidence:** For sql-34 Exercise 1, run the underlying read-only query over `orders`, `order_items`, and `products` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-34 Exercise 1, expected output: one row per `order_id`. The final columns are `order_id`, and `order_date`.
   **Verify:** For sql-34 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
2. Limit rows early without changing the result.
   **Inputs/evidence:** For sql-34 Exercise 2, run the underlying read-only query over `orders`, `customers`, and `top_orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-34 Exercise 2, expected output: at most 100 rows keyed by `order_id`. The final columns are `order_id`, `order_date`, and `country`. The final order is `t.order_date DESC, t.order_id DESC`.
   **Verify:** For sql-34 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
3. Predict `MATERIALIZED` versus `NOT MATERIALIZED` planner freedom.
   **Inputs/evidence:** For sql-34 Exercise 3, run the underlying read-only query over `orders`, `recent`, and `customers` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-34 Exercise 3, expected output: one row per `order_id`. The final columns are `materialized`.
   **Verify:** For sql-34 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
4. Pre-aggregate items at order grain and verify totals.
   **Inputs/evidence:** For sql-34 Exercise 4, read from `order_items`, `orders`, and `customers`. Build the answer toward `country`, and `units`; keep `country` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-34 Exercise 4, expected output: one row per order before customer/country joins. The final columns are `country`, and `units`. The final order is `c.country`.
   **Verify:** For sql-34 Exercise 4, independently aggregate `order_items`, `orders`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `units` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `units` for the existing `country` tuple and verify the new tuple appears exactly once.
5. Repair payment/item fanout.
   **Inputs/evidence:** For sql-34 Exercise 5, read from `payments`, `order_items`, and `orders`. Build the answer toward `order_id`, `paid_amount`, and `line_revenue`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-34 Exercise 5, expected output: at most 20 rows keyed by `order_id`. The final columns are `order_id`, `paid_amount`, and `line_revenue`. The final order is `o.order_id`.
   **Verify:** For sql-34 Exercise 5, assert no more than 20 rows, no duplicate `order_id`, and no adjacent pair that violates `o.order_id`. Rejoin the returned keys to `payments`, `order_items`, and `orders` to confirm `order_id`, `paid_amount`, and `line_revenue` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `o.order_id`.
6. Replace nullable `NOT IN` logic with `NOT EXISTS`.
   **Inputs/evidence:** For sql-34 Exercise 6, read from `customers`, and `orders`. Build the answer toward `customer_id`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-34 Exercise 6, expected output: one row per `customer_id`. The final columns are `customer_id`. The final order is `c.customer_id`.
   **Verify:** For sql-34 Exercise 6, run an anti-check that counts rows where NOT ((NOT EXISTS ( SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id ))); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id` against `customers`, and `orders`. Repeat with `NULL` in `customer_id` and state whether the row is kept, rejected, or classified.

Change one thing per experiment and reconcile results before timing.

## Self-check

- Are compared queries semantically identical at edge cases as well as typical
  rows?
- Does the evidence identify work removed rather than relying only on elapsed
  time?

## Next step

Continue to [Day 35 — performance pitfalls](day35_avoiding_pitfalls.md).

## Deep dive and reference

## What you will learn

- Reduce rows and columns before expensive joins or aggregates.
- Replace repeated subquery work with set-based joins when semantics allow.
- Measure a rewrite rather than assuming it is faster.

## How the learner script uses the current schema

The script filters recent `orders` in a CTE before joining to `customers`,
projects only `order_id` and `customer_id` in a seven-day plan, and aggregates
`order_items.quantity` by `products.category` for successful order statuses.

PostgreSQL can inline many non-materialized CTEs, so writing a filter in a CTE
does not itself guarantee a faster plan. The value is a clear, correct query
shape that the optimizer can transform.

## Optimization loop

1. Capture `EXPLAIN (ANALYZE, BUFFERS)` for a safe baseline.
2. Identify excess rows, repeated loops, large sorts, or poor estimates.
3. Make one targeted change.
4. Reconcile keys, counts, and totals.
5. Compare plans under the same data and predicate.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Pitfalls and validation

- The optimizer chooses physical join order; SQL text order is not a reliable
  tuning lever.
- Pushing a filter from `WHERE` into the nullable side of an outer join can
  change results.
- `DISTINCT` can hide join fanout. Fix grain instead of masking duplicates.
- A faster query that changes counts or totals is incorrect.

## Expanded practice lab

Prompts 3–6 make semantic equivalence the first optimization gate. Compare
`MATERIALIZED` and `NOT MATERIALIZED` as planner boundaries, then verify a
one-row-per-order pre-aggregation against the direct join with `EXCEPT` in both
directions.

When payments and line items are both many-to-one with orders, aggregate each
to order grain before combining them. Use `NOT EXISTS` for a NULL-safe anti-join;
`NOT IN` becomes unknown for every candidate if its subquery can return NULL.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-34 — Query Optimization.

I have completed the direct catalog prerequisite: `sql-33`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day34_query_optimization.md
- Answer-free learner SQL: sql/postgres-60day/day34_query_optimization.sql

Key terms to teach in context: Baseline, Predicate pushdown, Semantic equivalence. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Capture a baseline and control totals, replace a repeated scalar aggregate with one grouped relation, and join it back. Recheck keys and totals before comparing plans; a faster query that silently drops zero-order customers is not an optimization of the same requirement.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-34/ working copy. Never point setup, reset, DDL, or DML
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
