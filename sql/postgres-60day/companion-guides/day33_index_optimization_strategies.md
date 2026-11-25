# Day 33: Composite, Covering, and Partial Indexes

## How to run this lesson

Open `./classroom`, select **sql-33** and run **Whole SQL lesson (psql)**.
The learner file builds a composite index, a covering index and a partial
index, plans two queries against them, and rolls everything back. Your copy
lives at
`.learning/sql/sql-33/lesson/workspace/sql/postgres-60day/day33_index_optimization_strategies.sql`
and runs against `advanced_sql_training`. General launch help is in
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Day 32's indexes were rolled back, so none of them are present here. If
`\di training.idx_*` lists anything before you start, an earlier experiment
was committed; drop it so it cannot compete with this lesson's indexes.

### Optional contributor notebook route

A notebook helps for the fifth prompt, where you plan two predicates side by
side against one partial index
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-33
```

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 32; index fundamentals](day32_index_fundamentals.md)
- **Artifacts:** [learner SQL](../day33_index_optimization_strategies.sql) ·
  [solution reasoning](../solutions/day33_solutions.md) ·
  [executable solution](../solutions/day33_solutions.sql)

## A beginner's mental model for this lesson

A composite index sorts its entries by the first key, then by the second key
inside each value of the first. In `(customer_id, order_date)`, all orders
for customer 1 sit next to each other in date order, so "customer 1 in the
last year" is one short slice of the index. Reverse the keys to
`(order_date, customer_id)` and the same five orders are scattered across a
year of dates, mixed with every other customer's.

Two more tools change what the index stores rather than its order. An
`INCLUDE` list adds payload columns to each entry without sorting by them,
so a query can read them from the index. A `WHERE` clause on the index
keeps only some rows, which makes it a partial index. The three learner
indexes show the size effect:

| Index | Table pages | Index pages | Rows indexed |
|---|---|---|---|
| `idx_orders_customer_date` | 65 | 19 | all 4,362 orders |
| `idx_oi_order_product_inc` | 97 | 67 | all 13,085 items |
| `idx_orders_open` | 65 | 7 | 1,745 placed or paid orders |

The covering index is two thirds the size of `order_items` itself, because
it repeats five of its columns. The partial index holds only the 873 placed
and 872 paid orders, so it is the smallest of the three.

## Two worked SQL examples

### Example 1

```sql
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);
```

**How to read it:** The composite index puts `customer_id`
first because the query that follows filters it by equality, and
`order_date` second because the same query bounds it by a range. A range
key in first place would stop the seek from narrowing on the
customer.

**Expected result/shape:** The `CREATE INDEX` tag, then a plan
for customer 1's last 365 days that reads `Index Scan using
idx_orders_customer_date` with both conditions in one `Index Cond`. It
returns 5 rows, all of customer 1's orders.

### Example 2

```sql
CREATE INDEX idx_oi_order_product_inc ON order_items (order_id, product_id) INCLUDE (quantity, unit_price, discount);
```

**How to read it:** The covering index searches `order_items`
by `(order_id, product_id)` and carries `quantity`, `unit_price` and
`discount` as payload. The learner query that follows asks for items of
open orders from the last 90 days through an `IN` subquery.

**Expected result/shape:** The tag, then a plan that does not
use the covering index at all: a `Hash Join` over a `Seq Scan on
order_items` (13,085 rows) and a hash of 322 orders. Those 322 orders come
from a `Bitmap Index Scan on idx_orders_open`, so the partial index is the
one doing the work. The join returns 962 item rows.

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
   **Inputs/evidence:** For sql-33 Exercise 1, read `products` (300 rows, 50 per category), create `idx_products_category_created_solution` on `(category, created_at)`, and plan `SELECT product_id, name, created_at ... WHERE category = 'Home' AND created_at >= CURRENT_TIMESTAMP - interval '1 year' ORDER BY created_at` with `EXPLAIN (ANALYZE, BUFFERS)`.
   **Expected result/shape:** For sql-33 Exercise 1, expected output: 4 Home rows on this load, oldest first, from a `Sort` on `created_at` above a `Bitmap Heap Scan` whose `Bitmap Index Scan on idx_products_category_created_solution` holds both predicates in its `Index Cond`. The final columns are `product_id`, `name`, and `created_at`. The final order is `created_at`.
   **Verify:** For sql-33 Exercise 1, confirm `COUNT(*)` with the same `WHERE` clause and no `EXPLAIN` returns 4, the plan's actual rows, and that the rows come back as `product_id` 279, 297, 291, and 285; then, inside `BEGIN ... ROLLBACK`, set the oldest Home product's (201, created 2020-12-07) `created_at` to `CURRENT_TIMESTAMP - interval '1 day'` and confirm the query returns 5 rows with 201 last.
2. Build/test a partial index for orders above 1000.
   **Inputs/evidence:** For sql-33 Exercise 2, read `orders` (4,362 rows, 334 above 1,000), create the partial index `idx_orders_high_value_solution` on `(total_amount, order_date) WHERE total_amount > 1000`, and plan `SELECT order_id, order_date, total_amount` for `total_amount > 1000` and an `order_date` lower bound of 90 days, sorted by `total_amount DESC`.
   **Expected result/shape:** For sql-33 Exercise 2, expected output: a `Sort` on `total_amount DESC` above a `Bitmap Index Scan on idx_orders_high_value_solution` whose `Index Cond` holds only the `order_date` bound, returning 65 rows on this load led by order 2304 at 1432.49. The final columns are `order_id`, `order_date`, and `total_amount`. The final order is `total_amount DESC`.
   **Verify:** For sql-33 Exercise 2, confirm `COUNT(*) FILTER (WHERE total_amount > 1000 AND order_date >= CURRENT_TIMESTAMP - interval '90 days')` returns 65, the plan's actual rows, and note that orders 39, 864, 3064, and 3339 tie at 1322.97, so `total_amount DESC` alone does not fix their relative order; then, inside `BEGIN ... ROLLBACK`, set order 2304 to exactly 1000 and confirm the 90-day result drops to 64 rows and now starts with the 1322.97 tie.
3. Predict how the product composite index behaves for `created_at` alone.
   **Inputs/evidence:** For sql-33 Exercise 3, read `products` with only `created_at >= CURRENT_TIMESTAMP - interval '1 year'`, while the composite index on `(category, created_at)` from the first answer still exists in the transaction.
   **Expected result/shape:** For sql-33 Exercise 3, expected output: a `Seq Scan on products` with 25 actual rows on this load, `Rows Removed by Filter: 275`, and about 4 shared buffers; the composite index is not chosen because `created_at` is not its leading key. The final columns are `product_id`, and `created_at`.
   **Verify:** For sql-33 Exercise 3, confirm `SELECT COUNT(*) FROM products WHERE created_at >= CURRENT_TIMESTAMP - interval '1 year'` returns 25 and that actual plus removed rows equal 300; then, inside `BEGIN ... ROLLBACK`, create an index on `products (created_at)` alone and confirm the same query switches to a `Bitmap Index Scan` on that new index.
4. Design an `INCLUDE` index for customer order history.
   **Inputs/evidence:** For sql-33 Exercise 4, read `orders`, create `idx_orders_history_cover_solution` on `(customer_id, order_date DESC) INCLUDE (status, total_amount)`, and plan the order history of `customer_id = 1`.
   **Expected result/shape:** For sql-33 Exercise 4, expected output: an `Index Scan using idx_orders_history_cover_solution` with `Index Cond: (customer_id = 1)`, no `Sort` node, and 5 actual rows, orders 5, 4, 3, 2, and 1 from newest to oldest. The final columns are `order_id`, `order_date`, `status`, and `total_amount`. The final order is `order_date DESC`.
   **Verify:** For sql-33 Exercise 4, confirm `SELECT COUNT(*) FROM orders WHERE customer_id = 1` returns 5 and that the returned `order_date` values strictly decrease; then plan `customer_id = -1` and confirm the same `Index Scan` with 0 actual rows, the empty case for a customer with no orders (62 real customers have none).
5. Compare a query that implies a partial predicate with one that does not.
   **Inputs/evidence:** For sql-33 Exercise 5, read `orders` with the partial index on `total_amount > 1000` still present, and plan `SELECT order_id` twice with plain `EXPLAIN`: once for `total_amount > 1200` and once for `total_amount > 500`.
   **Expected result/shape:** For sql-33 Exercise 5, expected output: for `> 1200`, a `Bitmap Index Scan on idx_orders_high_value_solution` estimated at 144 rows; for `> 500`, a `Seq Scan on orders` estimated at 2,410 rows, because `> 500` does not imply the index predicate. The final columns are `order_id`.
   **Verify:** For sql-33 Exercise 5, confirm the actual counts with `COUNT(*) FILTER (WHERE total_amount > 1200)` and `COUNT(*) FILTER (WHERE total_amount > 500)`, which return 142 and 2,410; then plan `total_amount > 1000.01`, which implies the predicate and uses the partial index, and `total_amount >= 1000`, which does not and falls back to a `Seq Scan`.
6. Evaluate a NULL-only partial index for `customers.segment`.
   **Inputs/evidence:** For sql-33 Exercise 6, count all customers and those with `segment IS NULL`, create the partial index `idx_customers_null_segment_solution ON customers (customer_id) WHERE segment IS NULL`, and read the plan of `SELECT customer_id FROM customers WHERE segment IS NULL`.
   **Expected result/shape:** For sql-33 Exercise 6, expected output: one row with `all_customers` 500 and `null_segments` 0, then a plan for the `IS NULL` query that can use the partial index (a `Bitmap Index Scan on idx_customers_null_segment_solution` on the course data). The final columns of the count are `all_customers` and `null_segments`.
   **Verify:** For sql-33 Exercise 6, confirm that the `IS NULL` query returns 0 rows, matching `null_segments`, whatever plan it uses; then confirm that `SELECT indexdef FROM pg_indexes WHERE indexname = 'idx_customers_null_segment_solution'` ends with `WHERE (segment IS NULL)`, because only a query whose `WHERE` implies that predicate can use the index.

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

## Why the second learner plan skips the covering index

It looks like a failure that `idx_oi_order_product_inc` goes unused, but
the numbers explain it. The subquery finds 322 recent open orders, and
those orders own 962 of the 13,085 order items. Using the covering index
would mean 322 separate descents into a 67-page B-tree. Reading all 97
pages of `order_items` once and keeping the matches through a hash table
is cheaper, so the planner picks the hash join.

The partial index earns its place in the same plan. Its `Index Cond`
mentions only `order_date`; the status test is already guaranteed by the
index's own `WHERE` clause, so the 7-page index is searched by date alone.
Notice also that the learner query selects `oi.quantity` but not
`unit_price`; a covering index helps only when every selected column is a
key or included column, and even then only if the planner chooses an
index path.

## Practice map

The six prompts above pair one index with one query each. For every
prompt, write down the index definition, the query and the plan line that
shows whether that index was used; the solution notes list what the course
seed produces.

## Pitfalls and validation

- `products` has no `active` column. Do not import an “active products” example
  from another schema.
- A query for `total_amount > 500` cannot generally use an index containing
  only rows greater than 1000.
- The compact seed may prefer a sequential scan; correctness and measured cost
  come before forcing a plan.
- All exercise indexes roll back with the learner transaction.

## Expanded practice lab

Prompts 3-6 test the contracts behind composite, covering, and partial indexes.
For `(category, created_at)`, queries anchored on the leftmost equality have a
more useful search prefix than `created_at` alone. `INCLUDE` columns can satisfy
the output list without changing the index's search key.

A partial index is eligible only when PostgreSQL can prove the query predicate
implies its stored predicate; eligibility does not guarantee selection. For
nullable segments, measure the NULL subset before deciding whether a tiny
partial index earns its write and maintenance cost.

## Ask an AI tutor about this lesson

A tutor is most useful for testing your partial-index reasoning: give it an
index predicate and several query predicates, and ask it to make you say
which ones imply the index condition
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-33: Composite, Covering, and Partial Indexes.

I have completed the direct catalog prerequisite: `sql-32`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day33_index_optimization_strategies.md
- Answer-free learner SQL: sql/postgres-60day/day33_index_optimization_strategies.sql

Key terms to teach in context: Leftmost prefix, Included column, Partial index. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: For a query filtering `customer_id` and a date range, compare `(customer_id, order_date)` with the reversed key order. Then check whether the query predicate logically implies a partial-index predicate; mere overlap is not enough for PostgreSQL to use that index safely.

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
