# Day 33 — Composite, Covering, and Partial Indexes

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 32 — index fundamentals](day32_index_fundamentals.md)
- **Artifacts:** [learner SQL](../day33_index_optimization_strategies.sql) ·
  [solution reasoning](../solutions/day33_solutions.md) ·
  [executable solution](../solutions/day33_solutions.sql)

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

2. Open **SQL-33 — Index Optimization Strategies** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-33/day33_index_optimization_strategies.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day33_index_optimization_strategies.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day33_index_optimization_strategies.sql
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
Leftmost prefix, Included column, Partial index. Its worked SQL reads or creates `orders`, `order_items`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: For a query filtering customerid and a date range, compare (customerid, orderdate) with the reversed key order. Then check whether the query predicate logically implies a partial-index predicate; mere overlap is not enough for PostgreSQL to use that index safely.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day33_index_optimization_strategies.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
CREATE INDEX idx_oi_order_product_inc ON order_items(order_id, product_id) INCLUDE (quantity, unit_price, discount);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Order composite search keys from real predicate and ordering requirements.
- Separate search keys, included payload columns, and a partial-index predicate.

## Vocabulary and concepts

- **Leftmost prefix:** the leading composite-index keys usable by a query.
- **Included column:** payload stored with an index but not part of its search
  ordering.
- **Partial index:** an index containing only rows satisfying a fixed predicate.

## Worked example / walkthrough

For a query filtering `customer_id` and a date range, compare
`(customer_id, order_date)` with the reversed key order. Then check whether the
query predicate logically implies a partial-index predicate; mere overlap is
not enough for PostgreSQL to use that index safely.

## Exercises

Complete these in the
[learner SQL](../day33_index_optimization_strategies.sql):

1. Test `(category, created_at)` on products.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Build/test a partial index for orders above 1000.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
3. Predict how the product composite index behaves for `created_at` alone.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
4. Design an `INCLUDE` index for customer order history.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
5. Compare a query that implies a partial predicate with one that does not.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
6. Evaluate a NULL-only partial index for `customers.segment`.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.

For each candidate, name the exact query and maintenance tradeoff.

## Self-check

- Can you identify search, order, and return-only columns separately?
- Is every partial predicate immutable and logically implied by its target
  query?

## Next step

Continue to [Day 34 — query optimization](day34_query_optimization.md).

## Deep dive and reference

## What you will learn

- Match composite-index order to filters and ordering.
- Use `INCLUDE` for covering columns that are not search keys.
- Use a partial index for a stable, explicitly defined subset.

## How the learner script uses the current schema

The script creates:

- `(customer_id, order_date)` on `orders`;
- `(order_id, product_id) INCLUDE (quantity, unit_price, discount)` on
  `order_items`; and
- a partial `orders(order_date)` index for statuses `placed` and `paid`.

The partial predicate is deliberately status-based. PostgreSQL index predicates
must be immutable, so a moving boundary such as `now() - interval '90 days'`
cannot appear in a partial-index definition.

## Design reasoning

- A composite B-tree is most useful from its leftmost key onward.
- `INCLUDE` columns can support index-only reads but do not participate in
  search ordering.
- A partial index is used only when the query predicate logically implies its
  stored predicate.
- Index-only scans are possible, not guaranteed; visibility and cost still
  matter.

## Practice — match the learner prompts exactly

1. Add a composite index on `products(category, created_at)` and test a query
   that filters category and a created-at range.
2. Add a partial index for `orders.total_amount > 1000` and test a query whose
   predicate implies that exact high-value subset.

For each exercise, compare the same query before and after the index and record
plan, row estimate, timing, and index size if useful.

## Pitfalls and validation

- `products` has no `active` column. Do not import an “active products” example
  from another schema.
- A query for `total_amount > 500` cannot generally use an index containing
  only rows greater than 1000.
- The compact seed may prefer a sequential scan; correctness and measured cost
  come before forcing a plan.
- All exercise indexes roll back with the learner transaction.

## Expanded practice lab

Prompts 3–6 test the contracts behind composite, covering, and partial indexes.
For `(category, created_at)`, queries anchored on the leftmost equality have a
more useful search prefix than `created_at` alone. `INCLUDE` columns can satisfy
the output list without changing the index's search key.

A partial index is eligible only when PostgreSQL can prove the query predicate
implies its stored predicate; eligibility does not guarantee selection. For
nullable segments, measure the NULL subset before deciding whether a tiny
partial index earns its write and maintenance cost.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-33 — Index Optimization Strategies.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day33_index_optimization_strategies.md
- Answer-free learner SQL: sql/postgres-60day/day33_index_optimization_strategies.sql

The lesson concepts include Leftmost prefix, Included column, Partial index. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For a query filtering customerid and a date range, compare (customerid, orderdate) with the reversed key order. Then check whether the query predicate logically implies a partial-index predicate; mere overlap is not enough for PostgreSQL to use that index safely.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-33/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
