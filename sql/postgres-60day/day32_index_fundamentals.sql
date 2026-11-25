-- Day 32: Index Fundamentals (B-tree, hash, basics)
-- BEGINNER WORKFLOW - sql-32: Index Fundamentals
-- Guide: sql/postgres-60day/companion-guides/day32_index_fundamentals.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-32.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Create simple indexes (demonstration; rolled back)
CREATE INDEX idx_orders_total_amount ON orders (total_amount);

CREATE INDEX idx_orders_order_date ON orders (order_date);

CREATE INDEX idx_customers_country ON customers (country);

-- Observe plan changes
EXPLAIN ANALYZE
SELECT
  order_id
FROM
  orders
WHERE
  total_amount > 500
LIMIT 100;

EXPLAIN ANALYZE
SELECT
  *
FROM
  orders
WHERE
  order_date >= now() - interval '30 days';

EXPLAIN ANALYZE
SELECT
  *
FROM
  customers
WHERE
  country = 'US';

-- Hash index example (not commonly needed; Postgres B-tree supports = well)
-- CREATE INDEX idx_customers_email_hash ON customers USING hash(email);
-- Exercises
-- 1. Create an index on products(category) and test a category filter.
--    Inputs: For sql-32 Exercise 1, read `products` (300 rows on 3 pages, six categories of 50), create `idx_products_category_solution` on `category`, and plan `SELECT product_id, name, price ... WHERE category = 'Electronics'` with `EXPLAIN (ANALYZE, BUFFERS)`.
--    Expected result/shape: For sql-32 Exercise 1, expected output: a `Seq Scan on products` plan with estimated and actual `rows=50`, `Rows Removed by Filter: 250`, and `Buffers: shared hit=3`; the index exists but is not chosen. The final columns are `product_id`, `name`, and `price`.
--    Verify: For sql-32 Exercise 1, confirm `SELECT COUNT(*) FROM products WHERE category = 'Electronics'` returns 50, the plan's actual rows, and that actual plus removed rows equal 300; then, in the same transaction, `SET LOCAL enable_seqscan = off` and confirm the plan becomes a `Bitmap Index Scan on idx_products_category_solution` with the same 50 rows, and that `category = 'Toys'` keeps the `Seq Scan` with 0 actual rows and 300 removed.
--    Hint ladder, rung 1: For sql-32 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
-- 2. Drop vs create index and observe planner differences.
--    Inputs: For sql-32 Exercise 2, drop `idx_products_category_solution` with `DROP INDEX IF EXISTS`, plan `SELECT product_id, name, price FROM products WHERE category = 'Electronics'` with `EXPLAIN (ANALYZE, BUFFERS)`, re-create the index on `products (category)`, and plan the same query again.
--    Expected result/shape: For sql-32 Exercise 2, expected output: two plans that are both `Seq Scan on products` with 50 actual rows, `Rows Removed by Filter: 250`, and `Buffers: shared hit=3`; re-creating the index changes nothing on this 3-page table. The final columns are `product_id`, `name`, and `price`.
--    Verify: For sql-32 Exercise 2, confirm `SELECT COUNT(*) FROM pg_indexes WHERE indexname = 'idx_products_category_solution'` returns 0 after the `DROP` and 1 after the `CREATE`; then run the query once without `EXPLAIN` and confirm it returns the same 50 products as both plans, `product_id` 2 through 296.
--    Hint ladder, rung 1: For sql-32 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
-- 3. Prediction: inspect category frequency first, then predict whether the
--    planner will prefer a sequential scan or the category index on this small
--    seed. Verify with EXPLAIN (ANALYZE, BUFFERS).
--    Inputs: For sql-32 Exercise 3, read `products`, count rows per `category` with `GROUP BY category`, then plan `SELECT product_id FROM products WHERE category = 'Electronics'` while the category index from the previous answer still exists.
--    Expected result/shape: For sql-32 Exercise 3, expected output: exactly 6 frequency rows, `Apparel`, `Beauty`, `Books`, `Electronics`, `Home`, and `Sports`, each with 50 products and listed alphabetically because every count ties; the plan is a `Seq Scan` with 50 actual rows. The final columns are `category`, and `products`. The final order is `products DESC, category`.
--    Verify: For sql-32 Exercise 3, confirm the counts sum to 300 and that `pg_stats.most_common_freqs` for `products.category` shows 0.16666667 for all six values; then, inside `BEGIN ... ROLLBACK`, move 49 `Electronics` rows to `Home`, run `ANALYZE products`, and confirm the frequency query now starts with `Home` at 99 and ends with `Electronics` at 1, while the plan stays a `Seq Scan` with 1 actual row because 3 pages are still cheaper than an index probe.
--    Hint ladder, rung 1: For sql-32 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `category` rows.
-- 4. Construction: create a B-tree index on payments(payment_date), query a
--    bounded half-open date range, and identify its scan node.
--    Inputs: For sql-32 Exercise 4, read `payments` (3,836 rows on 29 pages), create `idx_payments_date_solution` on `payment_date`, and plan `SELECT payment_id, amount` for the half-open window `payment_date >= CURRENT_TIMESTAMP - interval '180 days' AND payment_date < CURRENT_TIMESTAMP`.
--    Expected result/shape: For sql-32 Exercise 4, expected output: a `Bitmap Heap Scan on payments` over a `Bitmap Index Scan on idx_payments_date_solution` with both bounds in the `Index Cond`, 1,340 actual rows on this load, and `Heap Blocks: exact=29`. The final columns are `payment_id`, and `amount`.
--    Verify: For sql-32 Exercise 4, confirm the same window counted without `EXPLAIN` matches the plan's actual rows (1,340 on this load), and that the two adjacent half-open windows of 180 to 90 days and 90 to 0 days ago add up to it (632 + 708); then on `VALUES (timestamp '2026-01-01 00:00:00')` confirm `BETWEEN` places that instant in both one-day windows that meet at midnight, while `>= start AND < end` places it only in the later one.
--    Hint ladder, rung 1: For sql-32 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `payment_id` rows.
-- 5. Debugging: run a filter with lower(country) = 'us'. Explain why the plain
--    country index may not match it, then create and test an expression index.
--    Inputs: For sql-32 Exercise 5, read `customers` (500 rows, country codes stored in uppercase), create `idx_customers_lower_country_solution` on the expression `lower(country)`, and plan `SELECT customer_id FROM customers WHERE lower(country) = 'us'`.
--    Expected result/shape: For sql-32 Exercise 5, expected output: a `Bitmap Heap Scan on customers` over a `Bitmap Index Scan on idx_customers_lower_country_solution` with `Index Cond: (lower(country) = 'us'::text)`, an estimate of `rows=2`, and 63 actual rows. The final columns are `customer_id`.
--    Verify: For sql-32 Exercise 5, confirm `COUNT(*)` with `lower(country) = 'us'` and with `country = 'US'` both return 63; then, inside `BEGIN ... ROLLBACK`, show that a plain index on `customers (country)` alone leaves the plan as `Seq Scan on customers` with `Filter: (lower(country) = 'us'::text)`, and that running `ANALYZE customers` after creating the expression index raises its estimate from `rows=2` to `rows=63`.
--    Hint ladder, rung 1: For sql-32 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `customer_id` rows.
-- 6. Edge case: prove that an index does not provide a guaranteed output order
--    by contrasting a query without ORDER BY with one ordered explicitly.
--    Inputs: For sql-32 Exercise 6, read `customers` twice with `LIMIT 10`: once with no `ORDER BY`, as a control, and once with `ORDER BY country, customer_id`; no index is created for this answer.
--    Expected result/shape: For sql-32 Exercise 6, expected output: 10 rows from each query; the unordered control happens to return customers 1 to 10 cycling through `US`, `CA`, `GB`, `DE`, `FR`, `IN`, `AU`, and `BR`, while the ordered query returns the first ten of the 62 `AU` customers, ids 7, 15, 23, 31, 39, 47, 55, 63, 71, and 79. The final columns are `customer_id`, and `country`. The final order is `country, customer_id`.
--    Verify: For sql-32 Exercise 6, confirm the ordered ids match `SELECT customer_id FROM customers WHERE country = 'AU' ORDER BY customer_id LIMIT 10`; then, inside `BEGIN ... ROLLBACK`, run `UPDATE customers SET country = country WHERE customer_id = 1` and confirm the unordered control now returns ids 2 to 11 while the ordered query still returns 7 through 79.
--    Hint ladder, rung 1: For sql-32 Exercise 6, check `country, customer_id` before applying the row cap.
ROLLBACK;
