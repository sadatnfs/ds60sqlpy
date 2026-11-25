# Day 33: Solutions: Composite and Partial Indexes


<!-- beginner-solution-enrichment -->
## How to study and run this solution

All six answers run in a single transaction that ends with `ROLLBACK`, so
none of their indexes survive. Plans show shape and row counts that should
match the notes below; timings will not. General advice is in
[Read a solution](../../STUDY-GUIDE.md#read-a-solution).

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day33_solutions.sql
```

## How these answers fit together

The first and third answers share one composite index,
`products(category, created_at)`: the first query leads with `category` and
can seek, the third filters `created_at` alone and cannot. The second and
fifth answers share one partial index on orders above 1,000. The second
repeats the index predicate; the fifth asks whether `> 1200` and `> 500`
imply it. The fourth answer builds a covering index for one customer's
order history, and the sixth measures a `NULL` subset before indexing it.

The first two blocks each open their own transaction and start with
`DROP INDEX IF EXISTS`, so either can be pasted into `psql` on its own. The
first asks for `'Home'` products created in the last year, and the second
for high-value orders in the last 90 days. The learner file is
[day33_index_optimization_strategies.sql](../day33_index_optimization_strategies.sql).

## Exercise 1: Composite index on `(category, created_at)`

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_products_category_created_solution;

CREATE INDEX idx_products_category_created_solution ON products (category, created_at);

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  product_id,
  name,
  created_at
FROM
  products
WHERE
  category = 'Home'
  AND created_at >= CURRENT_TIMESTAMP - interval '1 year'
ORDER BY
  created_at;

ROLLBACK;
```

The equality condition on the leading `category` column lets the B-tree narrow
the search before applying the `created_at` range and can also support the
`ORDER BY created_at`. A predicate on `created_at` alone cannot use the
leftmost `category` key as efficiently.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 1, read `products` (300 rows, 50 per category), create `idx_products_category_created_solution` on `(category, created_at)`, and plan `SELECT product_id, name, created_at ... WHERE category = 'Home' AND created_at >= CURRENT_TIMESTAMP - interval '1 year' ORDER BY created_at` with `EXPLAIN (ANALYZE, BUFFERS)`.
- **Expected result/shape:** For sql-33 Exercise 1, expected output: 4 Home rows on this load, oldest first, from a `Sort` on `created_at` above a `Bitmap Heap Scan` whose `Bitmap Index Scan on idx_products_category_created_solution` holds both predicates in its `Index Cond`. The final columns are `product_id`, `name`, and `created_at`. The final order is `created_at`.
- **Independent verification:** For sql-33 Exercise 1, confirm `COUNT(*)` with the same `WHERE` clause and no `EXPLAIN` returns 4, the plan's actual rows, and that the rows come back as `product_id` 279, 297, 291, and 285; then, inside `BEGIN ... ROLLBACK`, set the oldest Home product's (201, created 2020-12-07) `created_at` to `CURRENT_TIMESTAMP - interval '1 day'` and confirm the query returns 5 rows with 201 last.

- **Intermediate relation check:** Without `EXPLAIN`, the query returns 4 of the 50 Home products on this load: 279, 297, 291, and 285, created between 2026-09-19 and 2026-11-09. The oldest Home product, 201, dates from 2020-12-07, so the one-year range removes 46 rows.
- **Clause check:** Both predicates appear in the `Index Cond` of a `Bitmap Index Scan on idx_products_category_created_solution`. A `Sort` on `created_at` sits on top, because a bitmap scan hands rows over in page order, not index order.
- **Alternative/trade-off:** With `enable_seqscan` and `enable_bitmapscan` set off for the transaction, the planner switches to an `Index Scan using idx_products_category_created_solution` with no `Sort` node, because equality on `category` leaves the rows in `created_at` order. For 4 rows on one heap page the planner judges the bitmap scan plus a quicksort cheaper; both are correct.
- **Edge case:** If the range kept every Home row, the second key would do no filtering. Here it removes 46 rows, and moving product 201's `created_at` into the window inside a rolled-back transaction raises the result to 5 rows.

## Exercise 2: Partial index for high-value orders

```sql
BEGIN;
SET LOCAL search_path TO training, public;

DROP INDEX IF EXISTS training.idx_orders_high_value_solution;

CREATE INDEX idx_orders_high_value_solution ON orders (total_amount, order_date)
WHERE
  total_amount > 1000;

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  order_id,
  order_date,
  total_amount
FROM
  orders
WHERE
  total_amount > 1000
  AND order_date >= CURRENT_TIMESTAMP - interval '90 days'
ORDER BY
  total_amount DESC;

ROLLBACK;
```

The query repeats the partial predicate in a form the planner can prove implies
the index condition. The index excludes lower-value orders, reducing its size.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 2, read `orders` (4,362 rows, 334 above 1,000), create the partial index `idx_orders_high_value_solution` on `(total_amount, order_date) WHERE total_amount > 1000`, and plan `SELECT order_id, order_date, total_amount` for `total_amount > 1000` and an `order_date` lower bound of 90 days, sorted by `total_amount DESC`.
- **Expected result/shape:** For sql-33 Exercise 2, expected output: a `Sort` on `total_amount DESC` above a `Bitmap Index Scan on idx_orders_high_value_solution` whose `Index Cond` holds only the `order_date` bound, returning 65 rows on this load led by order 2304 at 1432.49. The final columns are `order_id`, `order_date`, and `total_amount`. The final order is `total_amount DESC`.
- **Independent verification:** For sql-33 Exercise 2, confirm `COUNT(*) FILTER (WHERE total_amount > 1000 AND order_date >= CURRENT_TIMESTAMP - interval '90 days')` returns 65, the plan's actual rows, and note that orders 39, 864, 3064, and 3339 tie at 1322.97, so `total_amount DESC` alone does not fix their relative order; then, inside `BEGIN ... ROLLBACK`, set order 2304 to exactly 1000 and confirm the 90-day result drops to 64 rows and now starts with the 1322.97 tie.

- **Intermediate relation check:** 334 orders exceed 1,000, and 65 of them fall in the last 90 days on this load; order 2304 at 1432.49 is the largest of them.
- **Clause check:** The plan is a `Bitmap Index Scan on idx_orders_high_value_solution` whose `Index Cond` holds only the `order_date` bound. `total_amount > 1000` is guaranteed by the index predicate, so it is not searched again. A `Sort` on `total_amount DESC` follows.
- **Alternative/trade-off:** A full index on `(total_amount, order_date)` would hold all 4,362 orders; the partial one holds 334 and is 4 pages. It serves only queries that repeat or imply `total_amount > 1000`.
- **Edge case:** An `UPDATE` that lowers an order from 1,050 to 950 removes it from the index, and one that raises an order past 1,000 adds it. Changes to `total_amount` now carry that maintenance cost.

## Pitfalls

- Partial-index predicates cannot contain volatile or merely stable expressions
  such as `CURRENT_TIMESTAMP - interval '90 days'`. A fixed business condition
  such as `total_amount > 1000` is valid.
- A logically similar parameterized predicate may not be provably compatible
  with a partial index at planning time.
- Column order matters in a composite B-tree. Design it for real query shapes,
  not simply for every column mentioned by a query.
- Small course tables may still receive sequential scans. Judge the design and
  inspect the plan; do not force a node type.

## Exercise 3: Test the leftmost-prefix limitation

Filtering only `created_at` omits the composite index's first search column.
PostgreSQL may still inspect the index in some conditions, but the query cannot
seek through a known category prefix.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 3, read `products` with only `created_at >= CURRENT_TIMESTAMP - interval '1 year'`, while the composite index on `(category, created_at)` from the first answer still exists in the transaction.
- **Expected result/shape:** For sql-33 Exercise 3, expected output: a `Seq Scan on products` with 25 actual rows on this load, `Rows Removed by Filter: 275`, and about 4 shared buffers; the composite index is not chosen because `created_at` is not its leading key. The final columns are `product_id`, and `created_at`.
- **Independent verification:** For sql-33 Exercise 3, confirm `SELECT COUNT(*) FROM products WHERE created_at >= CURRENT_TIMESTAMP - interval '1 year'` returns 25 and that actual plus removed rows equal 300; then, inside `BEGIN ... ROLLBACK`, create an index on `products (created_at)` alone and confirm the same query switches to a `Bitmap Index Scan` on that new index.

- **Intermediate relation check:** 25 of the 300 products were created in the last year.
- **Clause check:** The plan is a `Seq Scan on products` with `Rows Removed by Filter: 275` and 3 buffers; the composite index is not chosen.
- **Alternative/trade-off:** With `SET LOCAL enable_seqscan = off`, PostgreSQL will scan the composite index with `created_at` as its condition, at an estimated cost of 18.53 against 8.25 for the table scan. The index can test a non-leading key, but with no `category` to seek on it must read every category's entries.
- **Edge case:** An index that leads with `created_at` would serve this query, but it is another structure that every `INSERT` into `products` has to update. Add it only if date-only lookups are common.

## Exercise 4: Cover customer order history

`customer_id, order_date` are search/order keys. `status` and `total_amount` are
included payload, which can support an index-only scan without widening the
search key.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 4, read `orders`, create `idx_orders_history_cover_solution` on `(customer_id, order_date DESC) INCLUDE (status, total_amount)`, and plan the order history of `customer_id = 1`.
- **Expected result/shape:** For sql-33 Exercise 4, expected output: an `Index Scan using idx_orders_history_cover_solution` with `Index Cond: (customer_id = 1)`, no `Sort` node, and 5 actual rows, orders 5, 4, 3, 2, and 1 from newest to oldest. The final columns are `order_id`, `order_date`, `status`, and `total_amount`. The final order is `order_date DESC`.
- **Independent verification:** For sql-33 Exercise 4, confirm `SELECT COUNT(*) FROM orders WHERE customer_id = 1` returns 5 and that the returned `order_date` values strictly decrease; then plan `customer_id = -1` and confirm the same `Index Scan` with 0 actual rows, the empty case for a customer with no orders (62 real customers have none).

- **Intermediate relation check:** Customer 1 has 5 orders, and the query returns all of them, newest first.
- **Clause check:** The plan is `Index Scan using idx_orders_history_cover_solution` with `Index Cond: (customer_id = 1)` and no `Sort` node; the `order_date DESC` key already returns newest first.
- **Alternative/trade-off:** The plan is an `Index Scan`, not an `Index Only Scan`, because `order_id` is selected but is neither a key nor an included column. Adding `order_id` to the `INCLUDE` list turns the plan into an `Index Only Scan`.
- **Edge case:** Even an index-only plan visits the heap for pages that `VACUUM` has not yet marked all-visible; `EXPLAIN ANALYZE` reports those visits as `Heap Fetches`.

## Exercise 5: Prove partial-index eligibility

`total_amount > 1200` implies the stored `> 1000` predicate; `> 500` does not.
Eligibility and final selection are separate planner decisions.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 5, read `orders` with the partial index on `total_amount > 1000` still present, and plan `SELECT order_id` twice with plain `EXPLAIN`: once for `total_amount > 1200` and once for `total_amount > 500`.
- **Expected result/shape:** For sql-33 Exercise 5, expected output: for `> 1200`, a `Bitmap Index Scan on idx_orders_high_value_solution` estimated at 144 rows; for `> 500`, a `Seq Scan on orders` estimated at 2,410 rows, because `> 500` does not imply the index predicate. The final columns are `order_id`.
- **Independent verification:** For sql-33 Exercise 5, confirm the actual counts with `COUNT(*) FILTER (WHERE total_amount > 1200)` and `COUNT(*) FILTER (WHERE total_amount > 500)`, which return 142 and 2,410; then plan `total_amount > 1000.01`, which implies the predicate and uses the partial index, and `total_amount >= 1000`, which does not and falls back to a `Seq Scan`.

- **Intermediate relation check:** 142 orders exceed 1,200 and 2,410 exceed 500.
- **Clause check:** For `> 1200` the plan is a `Bitmap Index Scan on idx_orders_high_value_solution` with an estimate of 144 rows. For `> 500` it is a `Seq Scan on orders`, because orders between 500 and 1,000 are not in the index.
- **Alternative/trade-off:** The proof works for comparisons against constants. A prepared statement with a parameter such as `total_amount > $1` gives the planner nothing to prove with, so a generic plan cannot use the partial index.
- **Edge case:** `total_amount >= 1000` does not imply `> 1000`: an order of exactly 1,000.00 would be missing from the index, so the planner rejects that predicate too.

## Exercise 6: Evaluate the NULL subset

The answer first measures NULL prevalence, then builds a NULL-only index.
Whether it is worthwhile depends on query frequency, subset size, and added
write/storage cost, not on syntax alone.

### Reasoning and verification

- **Inputs/evidence:** For sql-33 Exercise 6, count all customers and those with `segment IS NULL`, create the partial index `idx_customers_null_segment_solution ON customers (customer_id) WHERE segment IS NULL`, and read the plan of `SELECT customer_id FROM customers WHERE segment IS NULL`.
- **Expected result/shape:** For sql-33 Exercise 6, expected output: one row with `all_customers` 500 and `null_segments` 0, then a plan for the `IS NULL` query that can use the partial index (a `Bitmap Index Scan on idx_customers_null_segment_solution` on the course data). The final columns of the count are `all_customers` and `null_segments`.
- **Independent verification:** For sql-33 Exercise 6, confirm that the `IS NULL` query returns 0 rows, matching `null_segments`, whatever plan it uses; then confirm that `SELECT indexdef FROM pg_indexes WHERE indexname = 'idx_customers_null_segment_solution'` ends with `WHERE (segment IS NULL)`, because only a query whose `WHERE` implies that predicate can use the index.

- **Intermediate relation check:** The count returns 500 customers and 0 with a `NULL` segment; the four segments hold 125 customers each.
- **Clause check:** The partial index is created empty, a single 8 kB metapage, and the `EXPLAIN` shows an `Index Only Scan using idx_customers_null_segment_solution` with an estimate of 1 row.
- **Alternative/trade-off:** With no `NULL` segments today, the index protects nothing yet. If every customer must have a segment, a `NOT NULL` constraint states that rule directly and needs no index.
- **Edge case:** B-tree indexes store `NULL` keys, so a full index on `segment` could serve `IS NULL` as well. The partial index stays far smaller as long as `NULL` segments are rare.

## Final self-check

1. Why can `products(category, created_at)` seek for Home products from
   the last year but not for every product from the last year?
2. In the second answer, why does the `Index Cond` mention only
   `order_date`?
3. What one change turns the fourth answer's `Index Scan` into an
   `Index Only Scan`?
4. Which of `> 1200`, `> 500` and `>= 1000` can use an index built with
   `WHERE total_amount > 1000`, and why?
