# Day 04: OUTER JOINs: Preserving Unmatched Rows (Companion Guide)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-04**. The
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
   `.learning/sql/sql-04/lesson/workspace/sql/postgres-60day/day04_outer_joins.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-04
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 03; inner joins](day03_inner_joins.md)
- **Artifacts:** [learner SQL](../day04_outer_joins.sql) ·
  [solution reasoning](../solutions/day04_solutions.md) ·
  [executable solution](../solutions/day04_solutions.sql)

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Preserved side, NULL-extended row, Anti-join. Its worked SQL reads or creates `customers`, `orders`, `order_items`, `products`, `payments`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Start from products and left-join orderitems. A product with no line item still appears, with oi.productid IS NULL. Moving a right-side filter from ON into WHERE removes that row; run both shapes and explain the change.
The expected contract is that One row per customer; zero is visible. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These worked excerpts come from `sql/postgres-60day/day04_outer_joins.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

### Example 1

```sql
SELECT c.customer_id, c.full_name, COUNT(o.order_id) AS orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY orders ASC, c.customer_id
LIMIT 25;
```

**How to read it:** Example 1: Start with `customers`, and `orders` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `customer_id`, `full_name`, and `orders`. `ORDER BY` determines presentation order and the final `LIMIT 25` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one grouped row per `customer_id`, capped at 25 rows with columns `customer_id`, `full_name`, and `orders` from `customers`, and `orders`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT p.product_id, p.name, COALESCE(SUM(oi.quantity),0) AS sold_qty
FROM order_items oi
RIGHT JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY sold_qty ASC, p.product_id
LIMIT 25;
```

**How to read it:** Example 2: Start with `order_items`, and `products` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `product_id`, `name`, and `sold_qty`. `ORDER BY` determines presentation order and the final `LIMIT 25` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `product_id`, capped at 25 rows with columns `product_id`, `name`, and `sold_qty` from `order_items`, and `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Preserve unmatched dimension rows with an outer join.
- Place nullable-side predicates without accidentally converting a `LEFT JOIN`
  into an inner join.

## Vocabulary and concepts

- **Preserved side:** the side whose rows survive when no match exists.
- **NULL-extended row:** an unmatched outer-join row filled with `NULL` values
  for the other side.
- **Anti-join:** a query that returns rows for which no related row exists.

## Worked example / walkthrough

Start from `products` and left-join `order_items`. A product with no line item
still appears, with `oi.product_id IS NULL`. Moving a right-side filter from
`ON` into `WHERE` removes that row; run both shapes and explain the change.

## Practice assumptions and review method

- **Focus:** Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.
- **Assumptions:** Missing matches appear as NULL-extended columns. Decide whether absence means zero, unknown, or an exception before applying `COALESCE`.
- **Failure to watch for:** A right-side predicate in `WHERE` can turn a left join into an inner join; put match-qualification predicates in `ON` when unmatched left rows must remain.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** List every customer with order count, including customers with zero orders.
   **Progressive hint:** Start from customers, left join orders, and count the nullable order key rather than `COUNT(*)`.
   **Inputs/evidence:** For sql-04 Exercise 1, read from `customers`, and `orders`. Build the answer toward `customer_id`, `full_name`, and `order_count`; keep `customer_id`, and `full_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-04 Exercise 1, expected output: One row per customer; zero is visible. The final columns are `customer_id`, `full_name`, and `order_count`. The final order is `order_count DESC, c.customer_id`.
   **Verify:** For sql-04 Exercise 1, independently aggregate `customers`, and `orders` by `customer_id`, and `full_name`; require one output row for every distinct `customer_id`, and `full_name` tuple and compare `order_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count` for the existing `customer_id`, and `full_name` tuple and verify the new tuple appears exactly once.
2. **Query writing:** Find products that have never appeared in an order item.
   **Progressive hint:** Left join and retain rows where the right-side primary key is NULL.
   **Inputs/evidence:** For sql-04 Exercise 2, read from `products`, and `order_items`. Build the answer toward `product_id`, `name`, and `category`; keep `product_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-04 Exercise 2, expected output: One row per unsold product. The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
   **Verify:** For sql-04 Exercise 2, project `product_id` plus the raw source columns from `products`, and `order_items` at each join stage; record row count and distinct `product_id`, then assert the final `product_id`, `name`, and `category` values match those staged rows without unintended fanout or loss. Add one row for which `(oi.order_item_id IS NULL)` is true and one for which it is false; verify only the matching `product_id` value is returned.
3. **Query writing:** Compare monthly budgets and expenses by category with a full outer join.
   **Progressive hint:** Aggregate each side to the same category/month grain before joining; preserve keys from either side.
   **Inputs/evidence:** For sql-04 Exercise 3, read from `expenses`, and `budgets`. Build the answer toward `category`, `period`, `budget_amount`, and `actual_amount`; keep `category` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-04 Exercise 3, expected output: One row per category/month present in either source. The final columns are `category`, `period`, `budget_amount`, and `actual_amount`. The final order is `period, category`.
   **Verify:** For sql-04 Exercise 3, project `category` plus the raw source columns from `expenses`, and `budgets` at each join stage; record row count and distinct `category`, then assert the final `category`, `period`, `budget_amount`, and `actual_amount` values match those staged rows without unintended fanout or loss. Add one source row with a new `category`; verify the result gains exactly one row carrying that `category` value.
4. **Prediction:** Preserve every customer while counting only delivered orders; compare a status predicate in `ON` with the same predicate in `WHERE`.
   **Progressive hint:** Place `o.status = 'delivered'` in `ON`; `WHERE` would remove NULL-extended customers.
   **Inputs/evidence:** For sql-04 Exercise 4, read from `customers`, and `orders`. Build the answer toward `customer_id`, `full_name`, and `delivered_orders`; keep `customer_id`, and `full_name` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-04 Exercise 4, expected output: One row per customer, including zero delivered orders. The final columns are `customer_id`, `full_name`, and `delivered_orders`. The final order is `delivered_orders DESC, c.customer_id`.
   **Verify:** For sql-04 Exercise 4, independently aggregate `customers`, and `orders` by `customer_id`, and `full_name`; require one output row for every distinct `customer_id`, and `full_name` tuple and compare `delivered_orders` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `delivered_orders` for the existing `customer_id`, and `full_name` tuple and verify the new tuple appears exactly once.
5. **Debugging:** Repair `COUNT(*)` in a left-join order count so customers without orders report zero rather than one.
   **Progressive hint:** Count a non-nullable right-side key that becomes NULL for an unmatched row.
   **Inputs/evidence:** For sql-04 Exercise 5, read from `customers`, and `orders`. Build the answer toward `customer_id`, and `order_count`; keep `customer_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-04 Exercise 5, expected output: One row per customer with correct zero counts. The final columns are `customer_id`, and `order_count`. The final order is `c.customer_id`.
   **Verify:** For sql-04 Exercise 5, independently aggregate `customers`, and `orders` by `customer_id`; require one output row for every distinct `customer_id` tuple and compare `order_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count` for the existing `customer_id` tuple and verify the new tuple appears exactly once.
6. **Extension:** Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys.
   **Progressive hint:** Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero.
   **Inputs/evidence:** For sql-04 Exercise 6, read from `products`, and `order_items`. Build the answer toward `matched_products`, `unsold_products`, and `orphan_item_product_ids`; keep `product_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-04 Exercise 6, expected output: One summary row with three mutually interpretable counts. The final columns are `matched_products`, `unsold_products`, and `orphan_item_product_ids`.
   **Verify:** For sql-04 Exercise 6, project `product_id` plus the raw source columns from `products`, and `order_items` at each join stage; record row count and distinct `product_id`, then assert the final `matched_products`, `unsold_products`, and `orphan_item_product_ids` values match those staged rows without unintended fanout or loss. Add one source row with a new `product_id`; verify the result gains exactly one row carrying that `product_id` value.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** A right-side predicate in WHERE can turn a left join into an inner join; put match-qualification predicates in ON when unmatched left rows must remain.
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

- Do entities with zero matching facts remain visible when the question
  requires complete coverage?
- Can you explain why `COUNT(*)` and `COUNT(right_table.id)` differ after a
  left join?

## Next step

Continue to [Day 05; cross and self joins](day05_cross_self_joins.md).

## Deep dive and reference

Learning objectives
- Use LEFT/RIGHT/FULL OUTER JOIN to retain non-matching rows
- Write NULL-aware filters; COALESCE and IS NULL checks
- Identify when to prefer LEFT JOIN vs INNER JOIN

Why this matters
Real data is messy. Outer joins let you keep entities that currently lack related rows (e.g., products with no sales), which is essential for completeness and auditing.

Core concepts and deep dive
- LEFT OUTER JOIN: keeps all rows from the left table, with NULLs for missing right-side columns.
- RIGHT OUTER JOIN: mirror of LEFT; prefer LEFT by flipping table order for readability.
- FULL OUTER JOIN: keeps rows from both sides even when no match exists; useful for reconciliation.
- NULL-aware filtering: Put right-table predicates in `ON` to avoid turning the
  `LEFT JOIN` into an inner join by accident.
  - Example: `LEFT JOIN payments p ON p.order_id=o.order_id AND p.method='card'`
  - `WHERE p.method='card'` would filter out NULL-extended rows and collapse the
    result to matched card payments.

Walkthrough mapping to your schema
- Products with zero sales: products p LEFT JOIN order_items oi ON oi.product_id=p.product_id; filter WHERE oi.product_id IS NULL to find non-sellers.
- Customer coverage: customers c LEFT JOIN orders o ON o.customer_id=c.customer_id to count actives vs inactives by segment.
- Reconciliation: FULL JOIN of two extracts to find missing keys on either side.

Pitfalls
- Filtering on right-side columns in WHERE after LEFT JOIN removes the NULL-extended rows.
- Aggregations with NULLs: COUNT(oi.*) counts only non-null matches; use COUNT(*) with CASE WHEN to count zeroes explicitly.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Outer joins: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-FROM

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-04 — Outer Joins.

I have completed the direct catalog prerequisite: `sql-03`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day04_outer_joins.md
- Answer-free learner SQL: sql/postgres-60day/day04_outer_joins.sql

Key terms to teach in context: Preserved side, NULL-extended row, Anti-join. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Start from products and left-join orderitems. A product with no line item still appears, with oi.productid IS NULL. Moving a right-side filter from ON into WHERE removes that row; run both shapes and explain the change.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-04/ working copy. Never point setup, reset, DDL, or DML
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
