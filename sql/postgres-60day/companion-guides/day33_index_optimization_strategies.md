# Day 33: Composite, Covering, and Partial Indexes

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 32; index fundamentals](day32_index_fundamentals.md)
- **Artifacts:** [learner SQL](../day33_index_optimization_strategies.sql) ·
  [solution reasoning](../solutions/day33_solutions.md) ·
  [executable solution](../solutions/day33_solutions.sql)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-33**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-33/lesson/workspace/sql/postgres-60day/day33_index_optimization_strategies.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-33
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Leftmost prefix, Included column, Partial index. Its worked SQL reads or creates `orders`, `order_items`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: For a query filtering customerid and a date range, compare (customerid, orderdate) with the reversed key order. Then check whether the query predicate logically implies a partial-index predicate; mere overlap is not enough for PostgreSQL to use that index safely.
The first runnable example has a concrete contract: Example 1 must print the expected DDL command tag for `idx_orders_customer_date`, and `orders`. Verify the object in `pg_catalog.pg_index`, and `pg_catalog.pg_indexes`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state. Its final projection is the columns written in the final `SELECT`. Verify the command tag in `pg_catalog`/`information_schema`, run one accepted value and one value the declared rule rejects, and confirm the lesson rollback removes the course-owned object.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day33_index_optimization_strategies.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must print the expected DDL command tag for `idx_orders_customer_date`, and `orders`. Verify the object in `pg_catalog.pg_index`, and `pg_catalog.pg_indexes`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

### Example 2

```sql
CREATE INDEX idx_oi_order_product_inc ON order_items(order_id, product_id) INCLUDE (quantity, unit_price, discount);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 2 must print the expected DDL command tag for `idx_oi_order_product_inc`, and `order_items`. Verify the object in `pg_catalog.pg_index`, and `pg_catalog.pg_indexes`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

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
   **Inputs/evidence:** For sql-33 Exercise 1, run the underlying read-only query over `products`, `training.idx_products_category_created_solution`, and `idx_products_category_created_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-33 Exercise 1, expected output: one row per `product_id`. The final columns are `product_id`, `name`, and `created_at`. The final order is `created_at DESC`.
   **Verify:** For sql-33 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
2. Build/test a partial index for orders above 1000.
   **Inputs/evidence:** For sql-33 Exercise 2, run the underlying read-only query over `orders`, `training.idx_orders_high_value_solution`, and `idx_orders_high_value_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-33 Exercise 2, expected output: one row per `order_id`. The final columns are `order_id`, `total_amount`, and `order_date`. The final order is `total_amount DESC`.
   **Verify:** For sql-33 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
3. Predict how the product composite index behaves for `created_at` alone.
   **Inputs/evidence:** For sql-33 Exercise 3, run the underlying read-only query over `products` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-33 Exercise 3, expected output: one row per `product_id`. The final columns are `product_id`, and `created_at`.
   **Verify:** For sql-33 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `product_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
4. Design an `INCLUDE` index for customer order history.
   **Inputs/evidence:** For sql-33 Exercise 4, run the underlying read-only query over `orders`, and `idx_orders_history_cover_solution` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-33 Exercise 4, expected output: one row per `order_id`. The final columns are `order_id`, `order_date`, `status`, and `total_amount`. The final order is `order_date DESC`.
   **Verify:** For sql-33 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
5. Compare a query that implies a partial predicate with one that does not.
   **Inputs/evidence:** For sql-33 Exercise 5, run the underlying read-only query over `orders` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-33 Exercise 5, expected output: one row per `order_id`. The final columns are `order_id`.
   **Verify:** For sql-33 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `order_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
6. Evaluate a NULL-only partial index for `customers.segment`.
   **Inputs/evidence:** For sql-33 Exercise 6, run the underlying read-only query over `customers`, `idx_customers_null_segment_solution`, and `customers.segment` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
   **Expected result/shape:** For sql-33 Exercise 6, expected output: one row per `customer_id`. The final columns are `all_customers`, and `null_segments`.
   **Verify:** For sql-33 Exercise 6, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

For each candidate, name the exact query and maintenance tradeoff.

## Self-check

- Can you identify search, order, and return-only columns separately?
- Is every partial predicate immutable and logically implied by its target
  query?

## Next step

Continue to [Day 34; query optimization](day34_query_optimization.md).

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

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

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

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-33 — Index Optimization Strategies.

I have completed the direct catalog prerequisite: `sql-32`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day33_index_optimization_strategies.md
- Answer-free learner SQL: sql/postgres-60day/day33_index_optimization_strategies.sql

Key terms to teach in context: Leftmost prefix, Included column, Partial index. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For a query filtering customerid and a date range, compare (customerid, orderdate) with the reversed key order. Then check whether the query predicate logically implies a partial-index predicate; mere overlap is not enough for PostgreSQL to use that index safely.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-33/ working copy. Never point setup, reset, DDL, or DML
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
