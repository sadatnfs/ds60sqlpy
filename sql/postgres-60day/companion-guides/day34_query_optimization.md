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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-34/day34_query_optimization.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
Baseline, Predicate pushdown, Semantic equivalence. Its worked SQL reads or creates `orders`, `customers`, `order_items`, `products`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Capture a baseline and control totals, replace a repeated scalar aggregate with one grouped relation, and join it back. Recheck keys and totals before comparing plans; a faster query that silently drops zero-order customers is not an optimization of the same requirement.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
EXPLAIN ANALYZE
SELECT o.order_id, o.customer_id
FROM orders o
WHERE o.order_date >= now() - interval '7 days';
```

**How to read it:** Example 2 returns plan rows rather than business rows. The node tree is evidence about one execution strategy; it does not replace a correctness check on the underlying query.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
2. Limit rows early without changing the result.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Predict `MATERIALIZED` versus `NOT MATERIALIZED` planner freedom.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Pre-aggregate items at order grain and verify totals.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Repair payment/item fanout.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. Replace nullable `NOT IN` logic with `NOT EXISTS`.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

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

## Practice — match the learner prompts exactly

1. Replace a scalar or correlated subquery with a join to a pre-aggregated
   relation, then compare the two plans and outputs.
2. Limit rows as early as the business semantics permit and compare performance.
   Do not move `LIMIT` before an aggregate or ordering if that changes which
   rows are eligible.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day34_query_optimization.md
- Answer-free learner SQL: sql/postgres-60day/day34_query_optimization.sql

The lesson concepts include Baseline, Predicate pushdown, Semantic equivalence. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Capture a baseline and control totals, replace a repeated scalar aggregate with one grouped relation, and join it back. Recheck keys and totals before comparing plans; a faster query that silently drops zero-order customers is not an optimization of the same requirement.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-34/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
