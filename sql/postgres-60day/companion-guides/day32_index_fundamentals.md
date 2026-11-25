# Day 32: Index Fundamentals

## How to run this lesson

Choose **sql-32** in `./classroom`, then **Whole SQL lesson (psql)**. The
learner file creates three indexes inside one transaction, plans three
filters with `EXPLAIN ANALYZE`, and ends with `ROLLBACK`, so no index
outlives the run. That also means each run starts from a table with only its
primary key and unique constraints. Work in
`.learning/sql/sql-32/lesson/workspace/sql/postgres-60day/day32_index_fundamentals.sql`
against `advanced_sql_training`. The shared launch steps are in
[Run a lesson in the classroom](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

If a `CREATE INDEX` fails with "relation already exists", an earlier
experiment committed an index by mistake. Drop that index by name rather
than renaming yours.

### Optional contributor notebook route

In a notebook you can keep the transaction open across cells and plan the
same filter before and after each `CREATE INDEX`
([notebook setup](../../STUDY-GUIDE.md#optional-contributor-notebook-route)):

```sh
uv run --no-sync python scripts/course.py sql notebook sql-32
```

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 31; EXPLAIN and EXPLAIN ANALYZE](day31_explain_analyze.md)
- **Artifacts:** [learner SQL](../day32_index_fundamentals.sql) ·
  [solution reasoning](../solutions/day32_solutions.md) ·
  [executable solution](../solutions/day32_solutions.sql)

## A beginner's mental model for this lesson

A B-tree index is a sorted copy of one or more column values, each entry
pointing at a row in the table (the heap). Looking up `country = 'US'` in
the index is fast, but every match still needs a trip to the heap for the
other columns. An index pays off when it lets PostgreSQL skip most pages of
the table; when the matching rows are spread over every page anyway, a
plain sequential scan is cheaper.

The tables in this lesson are small, and that makes the trade-off visible:

| Table | Rows | Pages | Filter used here | Rows matched |
|---|---|---|---|---|
| `products` | 300 | 3 | `category = 'Electronics'` | 50 (1 in 6) |
| `customers` | 500 | 9 | `country = 'US'` | 63 (1 in 8) |
| `orders` | 4,362 | 65 | last 30 days | about 209 |
| `payments` | 3,836 | 29 | last 180 days | about 1,340 |

On a three-page table no index can save much, so `products` keeps its
sequential scan. On `orders`, a 30-day window touches 16 of 65 pages through
a bitmap scan, which is a real saving. PostgreSQL makes this choice from
**selectivity**, the fraction of rows it expects a predicate to keep, and
from the table's size. Your job is to read its choice, not to force it.

## Two worked SQL examples

### Example 1

```sql
CREATE INDEX idx_orders_total_amount ON orders (total_amount);
```

**How to read it:** `CREATE INDEX` builds a B-tree over
`orders.total_amount` and prints `CREATE INDEX`. That tag proves only that
the index exists. The learner file then plans `total_amount > 500 LIMIT
100`, and the plan ignores the new index: 2,410 of 4,362 orders match, so
the first 100 are found after reading about 183 rows from the heap.

**Expected result/shape:** The command tag, then a `Limit` over a
`Seq Scan on orders` with `Rows Removed by Filter: 83`. To see the index
itself, query `pg_indexes WHERE indexname = 'idx_orders_total_amount'`
before the `ROLLBACK`; it is about 112 kB, nearly twice the 65-page table
footprint of each column it covers.

### Example 2

```sql
CREATE INDEX idx_orders_order_date ON orders (order_date);
```

**How to read it:** The second index is on `order_date`, and
its filter, the last 30 days, keeps only about 209 orders. This time the
planner uses the index: a `Bitmap Index Scan` collects matching row
locations, and a `Bitmap Heap Scan` visits only the pages that hold
them.

**Expected result/shape:** `Bitmap Heap Scan on orders` above
`Bitmap Index Scan on idx_orders_order_date`, with an `Index Cond` on
`order_date` and `Heap Blocks: exact=16`, about a quarter of the table. The
third plan, `country = 'US'` on `customers`, also uses a bitmap scan but
visits all 9 heap pages, so the index saves nothing there.

## Learning objectives

- Match a B-tree index to equality, range, and ordering requirements.
- Explain a planner choice using selectivity, table size, projection, and
  measured cost.

## Vocabulary and concepts

- **Selectivity:** the fraction of rows a predicate is expected to return.
- **Index scan:** an access path that uses index entries to locate heap rows.
- **Index-only scan:** a plan that can satisfy selected values from the index,
  subject to visibility checks.

## Worked example / walkthrough

Capture a category-filter plan before creating `products(category)`, create the
index inside the rollback-only transaction, and rerun the identical query.
Record the plan even if PostgreSQL keeps the sequential scan: the compact seed
can make reading the table cheaper than traversing an index.

## Exercises

Complete these in the [learner SQL](../day32_index_fundamentals.sql):

1. Create and test an index on `products(category)`.
   **Inputs/evidence:** For sql-32 Exercise 1, read `products` (300 rows on 3 pages, six categories of 50), create `idx_products_category_solution` on `category`, and plan `SELECT product_id, name, price ... WHERE category = 'Electronics'` with `EXPLAIN (ANALYZE, BUFFERS)`.
   **Expected result/shape:** For sql-32 Exercise 1, expected output: a `Seq Scan on products` plan with estimated and actual `rows=50`, `Rows Removed by Filter: 250`, and `Buffers: shared hit=3`; the index exists but is not chosen. The final columns are `product_id`, `name`, and `price`.
   **Verify:** For sql-32 Exercise 1, confirm `SELECT COUNT(*) FROM products WHERE category = 'Electronics'` returns 50, the plan's actual rows, and that actual plus removed rows equal 300; then, in the same transaction, `SET LOCAL enable_seqscan = off` and confirm the plan becomes a `Bitmap Index Scan on idx_products_category_solution` with the same 50 rows, and that `category = 'Toys'` keeps the `Seq Scan` with 0 actual rows and 300 removed.
2. Compare plans before and after dropping/recreating that index.
   **Inputs/evidence:** For sql-32 Exercise 2, drop `idx_products_category_solution` with `DROP INDEX IF EXISTS`, plan `SELECT product_id, name, price FROM products WHERE category = 'Electronics'` with `EXPLAIN (ANALYZE, BUFFERS)`, re-create the index on `products (category)`, and plan the same query again.
   **Expected result/shape:** For sql-32 Exercise 2, expected output: two plans that are both `Seq Scan on products` with 50 actual rows, `Rows Removed by Filter: 250`, and `Buffers: shared hit=3`; re-creating the index changes nothing on this 3-page table. The final columns are `product_id`, `name`, and `price`.
   **Verify:** For sql-32 Exercise 2, confirm `SELECT COUNT(*) FROM pg_indexes WHERE indexname = 'idx_products_category_solution'` returns 0 after the `DROP` and 1 after the `CREATE`; then run the query once without `EXPLAIN` and confirm it returns the same 50 products as both plans, `product_id` 2 through 296.
3. Predict the scan choice from category frequency, then measure it.
   **Inputs/evidence:** For sql-32 Exercise 3, read `products`, count rows per `category` with `GROUP BY category`, then plan `SELECT product_id FROM products WHERE category = 'Electronics'` while the category index from the previous answer still exists.
   **Expected result/shape:** For sql-32 Exercise 3, expected output: exactly 6 frequency rows, `Apparel`, `Beauty`, `Books`, `Electronics`, `Home`, and `Sports`, each with 50 products and listed alphabetically because every count ties; the plan is a `Seq Scan` with 50 actual rows. The final columns are `category`, and `products`. The final order is `products DESC, category`.
   **Verify:** For sql-32 Exercise 3, confirm the counts sum to 300 and that `pg_stats.most_common_freqs` for `products.category` shows 0.16666667 for all six values; then, inside `BEGIN ... ROLLBACK`, move 49 `Electronics` rows to `Home`, run `ANALYZE products`, and confirm the frequency query now starts with `Home` at 99 and ends with `Electronics` at 1, while the plan stays a `Seq Scan` with 1 actual row because 3 pages are still cheaper than an index probe.
4. Index `payments(payment_date)` and test a half-open date range.
   **Inputs/evidence:** For sql-32 Exercise 4, read `payments` (3,836 rows on 29 pages), create `idx_payments_date_solution` on `payment_date`, and plan `SELECT payment_id, amount` for the half-open window `payment_date >= CURRENT_TIMESTAMP - interval '180 days' AND payment_date < CURRENT_TIMESTAMP`.
   **Expected result/shape:** For sql-32 Exercise 4, expected output: a `Bitmap Heap Scan on payments` over a `Bitmap Index Scan on idx_payments_date_solution` with both bounds in the `Index Cond`, 1,340 actual rows on this load, and `Heap Blocks: exact=29`. The final columns are `payment_id`, and `amount`.
   **Verify:** For sql-32 Exercise 4, confirm the same window counted without `EXPLAIN` matches the plan's actual rows (1,340 on this load), and that the two adjacent half-open windows of 180 to 90 days and 90 to 0 days ago add up to it (632 + 708); then on `VALUES (timestamp '2026-01-01 00:00:00')` confirm `BETWEEN` places that instant in both one-day windows that meet at midnight, while `>= start AND < end` places it only in the later one.
5. Diagnose `lower(country)` and test a matching expression index.
   **Inputs/evidence:** For sql-32 Exercise 5, read `customers` (500 rows, country codes stored in uppercase), create `idx_customers_lower_country_solution` on the expression `lower(country)`, and plan `SELECT customer_id FROM customers WHERE lower(country) = 'us'`.
   **Expected result/shape:** For sql-32 Exercise 5, expected output: a `Bitmap Heap Scan on customers` over a `Bitmap Index Scan on idx_customers_lower_country_solution` with `Index Cond: (lower(country) = 'us'::text)`, an estimate of `rows=2`, and 63 actual rows. The final columns are `customer_id`.
   **Verify:** For sql-32 Exercise 5, confirm `COUNT(*)` with `lower(country) = 'us'` and with `country = 'US'` both return 63; then, inside `BEGIN ... ROLLBACK`, show that a plain index on `customers (country)` alone leaves the plan as `Seq Scan on customers` with `Filter: (lower(country) = 'us'::text)`, and that running `ANALYZE customers` after creating the expression index raises its estimate from `rows=2` to `rows=63`.
6. Prove that index order does not replace an explicit `ORDER BY`.
   **Inputs/evidence:** For sql-32 Exercise 6, read `customers` twice with `LIMIT 10`: once with no `ORDER BY`, as a control, and once with `ORDER BY country, customer_id`; no index is created for this answer.
   **Expected result/shape:** For sql-32 Exercise 6, expected output: 10 rows from each query; the unordered control happens to return customers 1 to 10 cycling through `US`, `CA`, `GB`, `DE`, `FR`, `IN`, `AU`, and `BR`, while the ordered query returns the first ten of the 62 `AU` customers, ids 7, 15, 23, 31, 39, 47, 55, 63, 71, and 79. The final columns are `customer_id`, and `country`. The final order is `country, customer_id`.
   **Verify:** For sql-32 Exercise 6, confirm the ordered ids match `SELECT customer_id FROM customers WHERE country = 'AU' ORDER BY customer_id LIMIT 10`; then, inside `BEGIN ... ROLLBACK`, run `UPDATE customers SET country = country WHERE customer_id = 1` and confirm the unordered control now returns ids 2 to 11 while the ordered query still returns 7 through 79.

Compare selective and unselective predicates against the same indexed column.

## Self-check

- Are the before/after SQL, parameters, and returned rows identical?
- Can you explain index write/storage cost as well as possible read benefit?

## Next step

Continue to [Day 33; composite, covering, and partial indexes](day33_index_optimization_strategies.md).

## Deep dive and reference

## What you will learn

- Create B-tree indexes for equality and range predicates.
- Observe planner choices before and after an index exists.
- Explain why a valid index can remain unused on a small or unselective query.

## How the learner script uses the current schema

Inside a rollback-only transaction, the script creates indexes on
`orders.total_amount`, `orders.order_date`, and `customers.country`. It then
executes matching filters with `EXPLAIN ANALYZE`. No course index persists after
the final `ROLLBACK`.

B-tree is PostgreSQL's default and supports equality, ranges, ordering, `IN`
and `IS NULL`. It serves an anchored pattern such as `LIKE 'abc%'` only in the
`C` collation or through a `text_pattern_ops` index. The classroom's
`advanced_sql_training` database uses the `en_US.utf8` collation (check with
`SELECT datcollate FROM pg_database WHERE datname = current_database();`), so a
default B-tree on a text column does not help that predicate. A hash index is
mentioned only as a contrast; B-tree already handles the equality lookup on
`customers.email`.

## Planner and index concepts

- Selective predicates benefit most because they fetch a small fraction of the
  table.
- Every index adds storage and write/vacuum work. “Index every column” is not a
  sound policy.
- An index-only scan also depends on selected columns and visibility-map state.
- `SELECT *` can make heap access necessary even when a filter uses an index.
- On the compact seed, a sequential scan may correctly be cheaper.

## What the three learner indexes cost and buy

Before the `ROLLBACK`, measure the indexes with
`pg_relation_size`. The two `orders` indexes are 114,688 bytes each, 14
pages of 8 kB, beside a 65-page table. The `customers(country)` index is 2
pages beside a 9-page table. Every `INSERT` into `orders` now writes three
B-trees instead of one heap page and a primary key, and every `UPDATE` that
changes an indexed column writes a new index entry as well.

```sql
SELECT
  indexrelid::regclass AS index_name,
  pg_relation_size(indexrelid) / 8192 AS pages
FROM
  pg_index
WHERE
  indexrelid::regclass::text LIKE 'idx_%';
```

The plans show what that cost buys. A bitmap scan works in two passes: the
`Bitmap Index Scan` walks the B-tree and marks every page that holds a
match, then the `Bitmap Heap Scan` reads those pages once each in physical
order. `Recheck Cond` is printed because a bitmap can become lossy under
memory pressure; with `Heap Blocks: exact=...` no recheck was needed.

The two bitmap plans in the learner file differ in what they save. The 209
recent orders sit on 16 of the 65 `orders` pages, so the index lets
PostgreSQL skip three quarters of the table. The 63 US customers are
`customer_id` 1, 9, 17 and so on, one in every eight rows, so they appear
on all 9 `customers` pages. That plan reads the index and then the whole
table, and a sequential scan would have cost about the same.
`pg_stats.correlation` for `customers.country`
is 0.12, close to zero: the physical order of rows says almost nothing
about the country order.

## Practice map

The six numbered prompts above are the full practice set. Each solution
answer names the plan it saw on the course seed; your node types may differ
after a fresh `ANALYZE`, but the row counts should not.

## Pitfalls and validation

- Use only the setup's valid order statuses: `placed`, `paid`, `shipped`,
  `delivered`, and `returned`.
- Do not disable sequential scans as proof that an index is beneficial.
- Index names are schema-local; use exercise-specific names to avoid collisions.
- The learner transaction rolls all index experiments back safely.

## Expanded practice lab

Prompts 3-6 separate index *eligibility* from a planner's cost decision. First
measure category frequency: on a compact table, reading every page can be
cheaper than bouncing through an index. Use a half-open timestamp range for the
payment-date index so boundary semantics are explicit.

`lower(country)` is a different indexed expression from `country`; an
expression index must match the query expression. Finally, remember that an
index's physical order never replaces `ORDER BY` in the SQL result contract.

## Ask an AI tutor about this lesson

A tutor is useful here for one question: "why did the planner ignore my
index?" Bring the plan and the row counts with you
([optional tutor notes](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)).

```text
Tutor me through sql-32: B-Tree Index Fundamentals.

I have completed the direct catalog prerequisite: `sql-31`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day32_index_fundamentals.md
- Answer-free learner SQL: sql/postgres-60day/day32_index_fundamentals.sql

Key terms to teach in context: Selectivity, Index scan, Index-only scan. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Capture a category-filter plan before creating `products(category)`, create the index inside the rollback-only transaction, and rerun the identical query. Record the plan even if PostgreSQL keeps the sequential scan: the compact seed can make reading the table cheaper than traversing an index.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-32/ working copy. Never point setup, reset, DDL, or DML
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
