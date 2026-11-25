-- Day 33: Index Optimization Strategies (composite, covering, partial)
-- BEGINNER WORKFLOW - sql-33: Index Optimization Strategies
-- Guide: sql/postgres-60day/companion-guides/day33_index_optimization_strategies.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-33.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Composite index where predicates use (customer_id, order_date)
CREATE INDEX idx_orders_customer_date ON orders (customer_id, order_date);

-- Covering index (Postgres INCLUDE) for frequent query on order_items
CREATE INDEX idx_oi_order_product_inc ON order_items (order_id, product_id) INCLUDE (quantity, unit_price, discount);

-- Partial index for an active subset. Partial-index predicates must be
-- immutable, so a moving expression such as now() - interval '90 days' is
-- not valid in PostgreSQL.
CREATE INDEX idx_orders_open ON orders (order_date)
WHERE
  status IN ('placed', 'paid');

-- Test with EXPLAIN
EXPLAIN ANALYZE
SELECT
  o.order_id,
  o.order_date
FROM
  orders o
WHERE
  o.customer_id = 1
  AND o.order_date >= now() - interval '365 days';

EXPLAIN ANALYZE
SELECT
  oi.order_id,
  oi.product_id,
  oi.quantity
FROM
  order_items oi
WHERE
  oi.order_id IN (
    SELECT
      order_id
    FROM
      orders
    WHERE
      status IN ('placed', 'paid')
      AND order_date >= now() - interval '90 days');

-- Exercises
-- 1. Add a composite index for (category, created_at) on products and test.
--    Inputs: For sql-33 Exercise 1, read `products` (300 rows, 50 per category), create `idx_products_category_created_solution` on `(category, created_at)`, and plan `SELECT product_id, name, created_at ... WHERE category = 'Home' AND created_at >= CURRENT_TIMESTAMP - interval '1 year' ORDER BY created_at` with `EXPLAIN (ANALYZE, BUFFERS)`.
--    Expected result/shape: For sql-33 Exercise 1, expected output: 4 Home rows on this load, oldest first, from a `Sort` on `created_at` above a `Bitmap Heap Scan` whose `Bitmap Index Scan on idx_products_category_created_solution` holds both predicates in its `Index Cond`. The final columns are `product_id`, `name`, and `created_at`. The final order is `created_at`.
--    Verify: For sql-33 Exercise 1, confirm `COUNT(*)` with the same `WHERE` clause and no `EXPLAIN` returns 4, the plan's actual rows, and that the rows come back as `product_id` 279, 297, 291, and 285; then, inside `BEGIN ... ROLLBACK`, set the oldest Home product's (201, created 2020-12-07) `created_at` to `CURRENT_TIMESTAMP - interval '1 day'` and confirm the query returns 5 rows with 201 last.
--    Hint ladder, rung 1: For sql-33 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
-- 2. Create a partial index for high-value orders (total_amount > 1000) and test.
--    Inputs: For sql-33 Exercise 2, read `orders` (4,362 rows, 334 above 1,000), create the partial index `idx_orders_high_value_solution` on `(total_amount, order_date) WHERE total_amount > 1000`, and plan `SELECT order_id, order_date, total_amount` for `total_amount > 1000` and an `order_date` lower bound of 90 days, sorted by `total_amount DESC`.
--    Expected result/shape: For sql-33 Exercise 2, expected output: a `Sort` on `total_amount DESC` above a `Bitmap Index Scan on idx_orders_high_value_solution` whose `Index Cond` holds only the `order_date` bound, returning 65 rows on this load led by order 2304 at 1432.49. The final columns are `order_id`, `order_date`, and `total_amount`. The final order is `total_amount DESC`.
--    Verify: For sql-33 Exercise 2, confirm `COUNT(*) FILTER (WHERE total_amount > 1000 AND order_date >= CURRENT_TIMESTAMP - interval '90 days')` returns 65, the plan's actual rows, and note that orders 39, 864, 3064, and 3339 tie at 1322.97, so `total_amount DESC` alone does not fix their relative order; then, inside `BEGIN ... ROLLBACK`, set order 2304 to exactly 1000 and confirm the 90-day result drops to 64 rows and now starts with the 1322.97 tie.
--    Hint ladder, rung 1: For sql-33 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 3. Prediction: test the composite product index with created_at alone. Explain
--    why the leftmost category column affects how useful the index can be.
--    Inputs: For sql-33 Exercise 3, read `products` with only `created_at >= CURRENT_TIMESTAMP - interval '1 year'`, while the composite index on `(category, created_at)` from the first answer still exists in the transaction.
--    Expected result/shape: For sql-33 Exercise 3, expected output: a `Seq Scan on products` with 25 actual rows on this load, `Rows Removed by Filter: 275`, and about 4 shared buffers; the composite index is not chosen because `created_at` is not its leading key. The final columns are `product_id`, and `created_at`.
--    Verify: For sql-33 Exercise 3, confirm `SELECT COUNT(*) FROM products WHERE created_at >= CURRENT_TIMESTAMP - interval '1 year'` returns 25 and that actual plus removed rows equal 300; then, inside `BEGIN ... ROLLBACK`, create an index on `products (created_at)` alone and confirm the same query switches to a `Bitmap Index Scan` on that new index.
--    Hint ladder, rung 1: For sql-33 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `product_id` rows.
-- 4. Construction: build an INCLUDE index for a customer order-history query
--    that returns order_id, order_date, status, and total_amount.
--    Inputs: For sql-33 Exercise 4, read `orders`, create `idx_orders_history_cover_solution` on `(customer_id, order_date DESC) INCLUDE (status, total_amount)`, and plan the order history of `customer_id = 1`.
--    Expected result/shape: For sql-33 Exercise 4, expected output: an `Index Scan using idx_orders_history_cover_solution` with `Index Cond: (customer_id = 1)`, no `Sort` node, and 5 actual rows, orders 5, 4, 3, 2, and 1 from newest to oldest. The final columns are `order_id`, `order_date`, `status`, and `total_amount`. The final order is `order_date DESC`.
--    Verify: For sql-33 Exercise 4, confirm `SELECT COUNT(*) FROM orders WHERE customer_id = 1` returns 5 and that the returned `order_date` values strictly decrease; then plan `customer_id = -1` and confirm the same `Index Scan` with 0 actual rows, the empty case for a customer with no orders (62 real customers have none).
--    Hint ladder, rung 1: For sql-33 Exercise 4, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 5. Debugging: write a query whose WHERE clause does not imply the partial
--    index predicate. Compare it with a query that does and explain eligibility
--    separately from the planner's final cost choice.
--    Inputs: For sql-33 Exercise 5, read `orders` with the partial index on `total_amount > 1000` still present, and plan `SELECT order_id` twice with plain `EXPLAIN`: once for `total_amount > 1200` and once for `total_amount > 500`.
--    Expected result/shape: For sql-33 Exercise 5, expected output: for `> 1200`, a `Bitmap Index Scan on idx_orders_high_value_solution` estimated at 144 rows; for `> 500`, a `Seq Scan on orders` estimated at 2,410 rows, because `> 500` does not imply the index predicate. The final columns are `order_id`.
--    Verify: For sql-33 Exercise 5, confirm the actual counts with `COUNT(*) FILTER (WHERE total_amount > 1200)` and `COUNT(*) FILTER (WHERE total_amount > 500)`, which return 142 and 2,410; then plan `total_amount > 1000.01`, which implies the predicate and uses the partial index, and `total_amount >= 1000`, which does not and falls back to a `Seq Scan`.
--    Hint ladder, rung 1: For sql-33 Exercise 5, run the underlying query without `EXPLAIN` and preserve its `order_id` rows.
-- 6. Edge case: query a nullable column (customers.segment) with IS NULL and
--    discuss whether a partial index for only NULL rows would be worthwhile.
--    Inputs: For sql-33 Exercise 6, count all customers and those with `segment IS NULL`, create the partial index `idx_customers_null_segment_solution ON customers (customer_id) WHERE segment IS NULL`, and read the plan of `SELECT customer_id FROM customers WHERE segment IS NULL`.
--    Expected result/shape: For sql-33 Exercise 6, expected output: one row with `all_customers` 500 and `null_segments` 0, then a plan for the `IS NULL` query that can use the partial index (a `Bitmap Index Scan on idx_customers_null_segment_solution` on the course data). The final columns of the count are `all_customers` and `null_segments`.
--    Verify: For sql-33 Exercise 6, confirm that the `IS NULL` query returns 0 rows, matching `null_segments`, whatever plan it uses; then confirm that `SELECT indexdef FROM pg_indexes WHERE indexname = 'idx_customers_null_segment_solution'` ends with `WHERE (segment IS NULL)`, because only a query whose `WHERE` implies that predicate can use the index.
--    Hint ladder, rung 1: For sql-33 Exercise 6, run the count first; a partial index on `segment IS NULL` stores only those rows, so an empty count means an empty index.
ROLLBACK;
