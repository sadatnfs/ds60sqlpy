# Day 03: INNER JOINs: Relational Linking and Predicate Placement (Companion Guide)

## Level and prerequisites

- **Level:** Foundation (beginner)
- **Prerequisites:** [Day 02; aggregations and grouping](day02_aggregates_groupby_having.md)
- **Artifacts:** [learner SQL](../day03_inner_joins.sql) ·
  [solution reasoning](../solutions/day03_solutions.md) ·
  [executable solution](../solutions/day03_solutions.sql)

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-03**. The
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
   `.learning/sql/sql-03/lesson/workspace/sql/postgres-60day/day03_inner_joins.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-03
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## A beginner's mental model for this lesson

A **table** is stored data with named columns. A **row** is one occurrence of
the table's subject. A query produces a temporary **result set**; seeing rows
on screen does not mean the stored tables changed. The **grain** is what one
result row represents. Here the inputs are training.customers, training.orders, training.order_items, and training.products, and the intended
grain is one row per matched key combination before any final aggregation.

Read the main query as a pipeline: FROM chooses a starting relation; each INNER JOIN matches declared keys in its ON condition; WHERE then filters the joined rows; GROUP BY can collapse the resulting detail to the requested report grain. For ordinary analytical
queries, the useful logical reading order is `FROM/JOIN` → `WHERE` →
`GROUP BY`/aggregates → `HAVING` → window calculations → `SELECT` →
`ORDER BY` → `LIMIT`. This is a reasoning model, not a promise about the
physical plan PostgreSQL chooses.

Before running, write the expected column names and row grain in a comment.
After running, display both join keys while debugging; compare joined row counts and monetary totals with simple controls before hiding keys. an INNER JOIN discards unmatched rows; one-to-many joins duplicate parent values by design; qualify columns and add a deterministic ORDER BY. A blank cell, SQL `NULL`, zero,
and an absent row have different meanings; never substitute one for another
without a stated rule.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day03_inner_joins.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT o.order_id, o.order_date, c.full_name, p.name AS product, oi.quantity, oi.unit_price
FROM orders o
JOIN customers c   ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p    ON p.product_id = oi.product_id
ORDER BY o.order_date DESC, o.order_id DESC, p.product_id
LIMIT 50;
```

**How to read it:** Example 1: Start with `orders`, `customers`, `order_items`, and `products` in `FROM`/`JOIN`. The final `SELECT` displays `order_id`, `order_date`, `full_name`, `product`, `quantity`, and `unit_price`. `ORDER BY` determines presentation order and the final `LIMIT 50` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `order_id`, capped at 50 rows with columns `order_id`, `order_date`, `full_name`, `product`, `quantity`, and `unit_price` from `orders`, `customers`, `order_items`, and `products`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

### Example 2

```sql
SELECT o.order_id, c.country, SUM(oi.quantity) AS total_items
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, c.country
ORDER BY total_items DESC, o.order_id
LIMIT 20;
```

**How to read it:** Example 2: Start with `orders`, `customers`, and `order_items` in `FROM`/`JOIN`; let `GROUP BY` collapse rows to its grouping keys. The final `SELECT` displays `order_id`, `country`, and `total_items`. `ORDER BY` determines presentation order and the final `LIMIT 20` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 2 returns one grouped row per `order_id`, and `country`, capped at 20 rows with columns `order_id`, `country`, and `total_items` from `orders`, `customers`, and `order_items`. Use a direct count or grouped aggregate over those same source relations as the control; check ordering only when this query has an `ORDER BY`, and inspect `NULL` only for columns this example can produce.

## Learning objectives

- Join related tables with explicit keys and qualified column names.
- Predict one-to-many fanout and validate the intended output grain.

## Vocabulary and concepts

- **Join key:** columns that define how rows from two relations correspond.
- **Cardinality:** whether a relationship is one-to-one, one-to-many, or
  many-to-many.
- **Fanout:** row multiplication caused by matching one row to several rows.

## Worked example / walkthrough

Follow one `orders` row through the `order_items` join. It becomes one row per
line item, so summing `orders.total_amount` at that point repeats the order
total. The learner query instead calculates value from each line and aggregates
at the requested customer or category grain.

## Practice assumptions and review method

- **Focus:** Use inner joins only when unmatched rows should disappear, and verify key cardinality before aggregating.
- **Assumptions:** Foreign keys define expected many-to-one relationships. Net line revenue is `unit_price * quantity * (1 - discount)`.
- **Failure to watch for:** A missing or incomplete `ON` condition creates row multiplication; joining two detail tables before aggregation can multiply measures.
- **Review loop:** predict the row grain and NULL/order behavior, run the
  query, inspect a bounded sample, and reconcile counts or totals before
  accepting the result.

## Exercises

Use inner joins only when unmatched rows should disappear, and verify key cardinality before aggregating.

Attempt each prompt in a scratch SQL file before opening the solution.
For every result, write its row grain and expected shape first.

1. **Query writing:** List orders with customer names and countries.
   **Progressive hint:** Join the order foreign key to the customer primary key and qualify every selected column.
   **Inputs/evidence:** For sql-03 Exercise 1, read from `orders`, and `customers`. Build the answer toward `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-03 Exercise 1, expected output: One row per order. The final columns are `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`. The final order is `o.order_date DESC, o.order_id DESC`.
   **Verify:** For sql-03 Exercise 1, project `order_id` plus the raw source columns from `orders`, and `customers` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
2. **Query writing:** Calculate each order item's net line revenue with the product name and category.
   **Progressive hint:** Remain at one row per order item; do not aggregate until the desired grain changes.
   **Inputs/evidence:** For sql-03 Exercise 2, read from `order_items`, and `products`. Build the answer toward `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`; keep `order_item_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-03 Exercise 2, expected output: One row per order item. The final columns are `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`. The final order is `oi.order_id, oi.order_item_id`.
   **Verify:** For sql-03 Exercise 2, project `order_item_id` plus the raw source columns from `order_items`, and `products` at each join stage; record row count and distinct `order_item_id`, then assert the final `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.
3. **Query writing:** List payments with order status and customer name.
   **Progressive hint:** Follow payments → orders → customers using each declared foreign key.
   **Inputs/evidence:** For sql-03 Exercise 3, read from `payments`, `orders`, and `customers`. Build the answer toward `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`; keep `payment_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-03 Exercise 3, expected output: One row per payment. The final columns are `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`. The final order is `p.payment_date DESC, p.payment_id DESC`.
   **Verify:** For sql-03 Exercise 3, project `payment_id` plus the raw source columns from `payments`, `orders`, and `customers` at each join stage; record row count and distinct `payment_id`, then assert the final `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name` values match those staged rows without unintended fanout or loss. Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.
4. **Prediction:** Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation.
   **Progressive hint:** Aggregate items and payments separately to one row per order before joining those aggregates.
   **Inputs/evidence:** For sql-03 Exercise 4, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `item_total`, and `paid_total`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-03 Exercise 4, expected output: One row per order; no six-row multiplication. The final columns are `order_id`, `item_total`, and `paid_total`. The final order is `o.order_id`.
   **Verify:** For sql-03 Exercise 4, project `order_id` plus the raw source columns from `order_items`, `payments`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `item_total`, and `paid_total` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
5. **Debugging:** Repair a customer/order join whose `ON` clause compares unrelated IDs.
   **Progressive hint:** Join `orders.customer_id` to `customers.customer_id`; verify output cannot exceed the order count for an inner many-to-one join.
   **Inputs/evidence:** For sql-03 Exercise 5, read from `orders`, and `customers`. Build the answer toward `joined_rows`, and `distinct_orders`; keep `order_id` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-03 Exercise 5, expected output: Exactly one customer match per order. The final columns are `joined_rows`, and `distinct_orders`.
   **Verify:** For sql-03 Exercise 5, project `order_id` plus the raw source columns from `orders`, and `customers` at each join stage; record row count and distinct `order_id`, then assert the final `joined_rows`, and `distinct_orders` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
6. **Extension:** Calculate net line revenue by customer country without double-counting order totals.
   **Progressive hint:** Start from line items, join through orders and customers, then aggregate at country grain.
   **Inputs/evidence:** For sql-03 Exercise 6, read from `order_items`, `orders`, and `customers`. Build the answer toward `country`, and `net_revenue`; keep `country` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-03 Exercise 6, expected output: One row per country represented by an order. The final columns are `country`, and `net_revenue`. The final order is `net_revenue DESC, c.country`.
   **Verify:** For sql-03 Exercise 6, independently aggregate `order_items`, `orders`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `net_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** A missing or incomplete ON condition creates row multiplication; joining two detail tables before aggregation can multiply measures.
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

- Can you diagram every join as one-to-one or one-to-many before running it?
- Does each relationship predicate live in `ON`, with business filters placed
  deliberately?

## Next step

Continue to [Day 04; outer joins](day04_outer_joins.md).

## Deep dive and reference

Learning objectives
- Join multiple tables with explicit INNER JOIN ... ON syntax
- Place join predicates vs row filters correctly (ON vs WHERE)
- Avoid fanout and duplicate rows; validate cardinalities
- Use table aliases and qualified names for clarity

Why this matters
Most analytical questions span multiple entities. Correct join logic preserves row counts, avoids duplicate multiplication, and keeps queries maintainable.

Core concepts and deep dive
- INNER JOIN returns rows where the join condition matches in both tables. Rows without matches are dropped.
- Predicate placement:
  - ON defines how rows from left and right relate. Keep relationship conditions here (keys, equality).
  - WHERE filters the result after joins. Put row-level filters here (time windows, status).
- Cardinality awareness: 1:1, 1:N, N:M. Validate with COUNT(*) vs COUNT(DISTINCT key) to detect accidental fanout.
- Joining chains: Join dimension tables (customers, products) to fact tables (orders, order_items) along keys. Prefer explicit column lists to avoid ambiguous names.

Walkthrough mapping to your schema
- orders o JOIN customers c ON c.customer_id=o.customer_id; adds customer context to orders.
- `order_items oi JOIN products p ON p.product_id=oi.product_id` brings product
  name, category, catalog price, and cost to lines.
- Multi-join: orders→order_items→products to compute revenue: SUM(oi.quantity*oi.unit_price*(1-oi.discount)).

Validation patterns
- Compare: SELECT COUNT(*) FROM orders vs SELECT COUNT(DISTINCT order_id) after joining order_items; counts should match if grouping by order_id.
- Check join selectivity: how many rows drop when adding additional ON predicates.

Anti-patterns and pitfalls
- Old-style comma joins with predicates in WHERE; easy to miss a condition and create cross joins; use explicit JOIN ... ON.
- Using LIKE to join keys; always use exact key equality unless justified.
- Ambiguity in column names after join; qualify columns to avoid surprises.

Current practice map
- The authoritative six prompts, progressive hints, and expected shapes
  are maintained in **Exercises** above. They map
  one-for-one to both solution companions; older short exercise lists
  were removed to prevent prompt drift.

Further reading
- Joins: https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-JOINS

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

```text
Tutor me through sql-03 — Inner Joins.

I have completed the direct catalog prerequisite: `sql-02`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day03_inner_joins.md
- Answer-free learner SQL: sql/postgres-60day/day03_inner_joins.sql

Key terms to teach in context: Join key, Cardinality, Fanout. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Follow one orders row through the orderitems join. It becomes one row per line item, so summing orders.totalamount at that point repeats the order total. The learner query instead calculates value from each line and aggregates at the requested customer or category grain.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-03/ working copy. Never point setup, reset, DDL, or DML
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
