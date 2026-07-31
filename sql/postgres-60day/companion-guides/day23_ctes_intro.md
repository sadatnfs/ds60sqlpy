# Day 23 — Common Table Expressions (CTEs) Introduction (Companion Guide)

## Level and prerequisites

- **Level:** Intermediate
- **Prerequisites:** [Day 22 — advanced windows](day22_advanced_windows.md)
- **Artifacts:** [learner SQL](../day23_ctes_intro.sql) ·
  [solution reasoning](../solutions/day23_solutions.md) ·
  [executable solution](../solutions/day23_solutions.sql)

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

2. Open **SQL-23 — CTEs Intro** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-23/lesson/workspace/sql/postgres-60day/day23_ctes_intro.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day23_ctes_intro.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day23_ctes_intro.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is CTE, Inlining, Materialization. Its worked SQL reads or creates `orders`, `order_items`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Trace orderlines at one row per order, then topcustomers at one row per customer, then the final top-N presentation. Run each CTE body independently while developing and verify its key uniqueness before adding the next stage.
The expected contract is that One row per ordering customer. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day23_ctes_intro.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
WITH order_lines AS (
  SELECT o.order_id,
         o.customer_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id
), top_customers AS (
  SELECT customer_id,
         SUM(order_total) AS lifetime_revenue
  FROM order_lines
  GROUP BY customer_id
)
SELECT tc.customer_id, tc.lifetime_revenue
FROM top_customers tc
ORDER BY lifetime_revenue DESC, tc.customer_id
LIMIT 20;
```

**How to read it:** Example 1: Start with `orders`, and `order_items` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `customer_id`, and `lifetime_revenue`. `ORDER BY` determines presentation order and the final `LIMIT 20` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `customer_id`, capped at 20 rows with columns `customer_id`, and `lifetime_revenue` from `orders`, and `order_items`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
-- The same topic query shown as a plan instead of business rows.
EXPLAIN (COSTS OFF)
WITH order_lines AS (
  SELECT o.order_id,
         o.customer_id,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.order_id, o.customer_id
), top_customers AS (
  SELECT customer_id,
         SUM(order_total) AS lifetime_revenue
  FROM order_lines
  GROUP BY customer_id
)
SELECT tc.customer_id, tc.lifetime_revenue
FROM top_customers tc
ORDER BY lifetime_revenue DESC, tc.customer_id
LIMIT 20;
```

**How to read it:** Example 2 is executed by `psql` as part of the complete lesson. Expected notices are evidence; an unexpected error stops the script.

**Expected result/shape:** Example 2 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `customer_id` key set and row count over `orders`, and `order_items`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

## Learning objectives

- Decompose a query into named stages with an explicit grain at each stage.
- Explain when PostgreSQL may inline or materialize a non-recursive CTE.

## Vocabulary and concepts

- **CTE:** a statement-local named query introduced by `WITH`.
- **Inlining:** planner substitution of a CTE into the surrounding query.
- **Materialization:** evaluating and storing an intermediate relation before
  later use.

## Worked example / walkthrough

Trace `order_lines` at one row per order, then `top_customers` at one row per
customer, then the final top-N presentation. Run each CTE body independently
while developing and verify its key uniqueness before adding the next stage.

## Practice assumptions and review method

- **Focus:** Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability—not forced materialization—is the default goal.
- **Assumptions:** Each CTE declares its output grain. PostgreSQL 16 may inline a side-effect-free single-use CTE unless `MATERIALIZED` is requested.
- **Failure to watch for:** A CTE does not automatically improve performance; duplicated rows or ambiguous names remain logical bugs even when split into stages.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability—not forced materialization—is the default goal.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** Build order-level net value in one CTE and summarize it by customer in the outer query.
   **Progressive hint:** Name the one-row-per-order grain before changing to customer grain.
   **Inputs/evidence:** For sql-23 Exercise 1, read from `orders`, and `order_items`. Build the answer toward `customer_id`, `order_count`, and `net_revenue`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-23 Exercise 1, expected output: One row per ordering customer. The final columns are `customer_id`, `order_count`, and `net_revenue`. The final order is `net_revenue DESC, ov.customer_id`.
   **Verify:** For sql-23 Exercise 1, independently aggregate `orders`, and `order_items` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `order_count`, and `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `net_revenue` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
2. **Query writing:** Use one category-revenue CTE twice to return the highest category and total revenue.
   **Progressive hint:** A named aggregate can support multiple scalar reads without repeating the business formula.
   **Inputs/evidence:** For sql-23 Exercise 2, read from `order_items`, and `products`. Compute `top_category`, and `all_revenue` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
   **Expected result/shape:** For sql-23 Exercise 2, expected output: One summary row. The final columns are `top_category`, and `all_revenue`.
   **Verify:** For sql-23 Exercise 2, evaluate each of `all_revenue` in a separate control `SELECT` over `order_items`, and `products`; require one final row and compare every value. Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.
3. **Query writing:** Create staged payment reconciliation CTEs at order grain.
   **Progressive hint:** Aggregate payment detail before joining to orders and preserve unpaid orders with a left join.
   **Inputs/evidence:** For sql-23 Exercise 3, read from `payments`, and `orders`. Build the answer toward `order_id`, `order_total`, `paid_amount`, and `unpaid_balance`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-23 Exercise 3, expected output: One row per order. The final columns are `order_id`, `order_total`, `paid_amount`, and `unpaid_balance`. The final order is `ABS(total_amount - paid_amount) DESC, order_id`.
   **Verify:** For sql-23 Exercise 3, project `order_id` plus the raw source columns from `payments`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `order_total`, `paid_amount`, and `unpaid_balance` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
4. **Prediction:** Compare `MATERIALIZED` and `NOT MATERIALIZED` syntax on a side-effect-free filtered order CTE without claiming one is universally faster.
   **Progressive hint:** Both return the same rows; planning effects require `EXPLAIN` evidence in a representative environment.
   **Inputs/evidence:** For sql-23 Exercise 4, read from `orders`, `materialized_orders`, and `inline_orders`. Build the answer toward `variant`, and `row_count`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-23 Exercise 4, expected output: Two count rows with equal values. The final columns are `variant`, and `row_count`. The final order is `variant`.
   **Verify:** For sql-23 Exercise 4, reselect the returned keys directly from the source; require unique `order_id` where the expected grain is one row per key and confirm the projected `variant`, and `row_count` against `orders`, `materialized_orders`, and `inline_orders`. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
5. **Debugging:** Repair a multi-stage query whose repeated `total` column names are ambiguous by assigning grain-specific aliases.
   **Progressive hint:** Name measures `order_value`, `customer_revenue`, and similar rather than carrying generic `total`.
   **Inputs/evidence:** For sql-23 Exercise 5, read from `orders`, `order_items`, and `customers`. Build the answer toward `country`, and `country_revenue`; keep `country` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-23 Exercise 5, expected output: One row per country. The final columns are `country`, and `country_revenue`. The final order is `country_revenue DESC, c.country`.
   **Verify:** For sql-23 Exercise 5, independently aggregate `orders`, `order_items`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `country_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `country_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.
6. **Extension:** Use a data-modifying CTE to demonstrate an update and inspect its returned rows without persistence.
   **Progressive hint:** The outer lesson transaction rolls back; the CTE exposes changed rows as a relation.
   **Inputs/evidence:** For sql-23 Exercise 6, read the target keys from `products` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-23 Exercise 6, expected output: One summary row for a bounded three-product update. The final columns are `updated_rows`, `first_updated_product`, and `last_updated_product`.
   **Verify:** For sql-23 Exercise 6, materialize the intended `product_id` target set first; require the command tag/`RETURNING` set to match it, then query `products` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `product_id` values in both cases.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** A CTE does not automatically improve performance; duplicated rows or ambiguous names remain logical bugs even when split into stages.
- **Unexpected row count:** display keys before aggregates, count rows after
  each join/filter stage, and find the first stage whose grain differs from the
  contract. Do not hide fanout with `DISTINCT`.
- **Unexpected `NULL` or missing row:** decide whether the fact is unknown,
  inapplicable, zero, or absent before using `COALESCE`; inspect outer-join
  predicate placement and empty-input aggregate behavior.
- **Unstable top/first/last output:** add `ORDER BY` with a unique final
  tie-breaker before `LIMIT` or order-sensitive windows/aggregates.
- **`psql` stops on an error:** fix the first error shown by
  `ON_ERROR_STOP`, restore the declared transaction/setup state, and rerun the
  complete file. A later successful statement does not validate a partial run.

## Self-check

- Can later stages reference only columns deliberately exposed by earlier ones?
- Is `MATERIALIZED` or `NOT MATERIALIZED` used only for a measured reason?

## Next step

Continue to [Day 24 — recursive CTEs](day24_recursive_ctes.md).

## Deep dive and reference

Learning objectives
- Rewrite subqueries as CTEs (WITH ...) to improve readability and reuse
- Understand evaluation order and CTE inlining/materialization in Postgres
- Structure multi-step analytical pipelines with clean, named stages

Why this matters
CTEs make complex queries understandable. By naming intermediate results, you reduce cognitive load and avoid repeating logic. Postgres can inline non-recursive CTEs (since v12), so you often get both clarity and performance.

Core concepts and deep dive
- Syntax: WITH name AS (subquery) SELECT ... FROM name ...; Multiple CTEs are comma-separated.
- Visibility: CTEs are visible only to the main query and to subsequent CTEs defined after them.
- Evaluation (Postgres specifics):
  - Pre-v12: non-recursive CTEs were optimization fences (always materialized). v12+ can inline them; the planner may treat them as simple subqueries.
  - Use MATERIALIZED/NOT MATERIALIZED hints (v12+) to force/forbid materialization if needed.
- Reuse: you can reference a CTE multiple times to avoid recomputing complex expressions. Be mindful: if inlined, the planner may duplicate work; consider MATERIALIZED.

Walkthrough of the day’s script
- order_lines CTE aggregates order-level revenue by joining orders and order_items, producing one row per order_id and customer_id.
- top_customers CTE rolls order_lines up to lifetime_revenue per customer.
- The final SELECT orders customers by lifetime revenue and returns the top 20. This expresses a clear two-stage pipeline: lines → customers.

Design patterns
- “Stage and refine”: build granular CTEs (lines), then roll-ups (customers), then selections (top-N).
- “Filter early”: push selective WHERE predicates into earlier CTEs to reduce data volume in later stages.
- Parameterization with psql variables: WHERE order_date >= :'since'.

Pitfalls
- Overusing CTEs for tiny subqueries can hurt readability and prevent predicate pushdown if forced materialization.
- Reusing a heavy CTE many times without MATERIALIZED can multiply work if the planner inlines it.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- WITH queries: https://www.postgresql.org/docs/current/queries-with.html
- MATERIALIZED/NOT MATERIALIZED: https://www.postgresql.org/docs/current/queries-with.html#QUERIES-WITH-MATERIALIZED

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-23 — CTEs Intro.

I have completed the direct catalog prerequisite: `sql-22`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day23_ctes_intro.md
- Answer-free learner SQL: sql/postgres-60day/day23_ctes_intro.sql

Key terms to teach in context: CTE, Inlining, Materialization. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Trace orderlines at one row per order, then topcustomers at one row per customer, then the final top-N presentation. Run each CTE body independently while developing and verify its key uniqueness before adding the next stage.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-23/ working copy. Never point setup, reset, DDL, or DML
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
