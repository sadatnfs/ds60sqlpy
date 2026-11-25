-- Day 34: Query Optimization Techniques
-- BEGINNER WORKFLOW - sql-34: Query Optimization
-- Guide: sql/postgres-60day/companion-guides/day34_query_optimization.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-34.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, customers, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Predicate pushdown by filtering early in CTE
WITH filtered_orders AS (
  SELECT
    order_id,
    customer_id
  FROM
    orders
  WHERE
    order_date >= now() - interval '30 days'
)
SELECT
  c.country,
  COUNT(*)
FROM
  filtered_orders fo
  JOIN customers c ON c.customer_id = fo.customer_id
GROUP BY
  c.country
ORDER BY
  COUNT(*) DESC;

-- Avoid SELECT * and unnecessary columns to reduce I/O
EXPLAIN ANALYZE
SELECT
  o.order_id,
  o.customer_id
FROM
  orders o
WHERE
  o.order_date >= now() - interval '7 days';

-- Join order rewrite (ensure correct join conditions, indexes)
EXPLAIN
SELECT
  p.category,
  SUM(oi.quantity) AS qty
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
  JOIN orders o ON o.order_id = oi.order_id
WHERE
  o.status IN ('paid', 'shipped', 'delivered')
GROUP BY
  p.category;

-- Exercises
-- 1. Replace subqueries with joins and compare plans.
--    Inputs: For sql-34 Exercise 1, read `orders`, `order_items`, and `products` (50 `Electronics` products) and plan two forms of 'orders with an Electronics line' with `EXPLAIN (ANALYZE, BUFFERS)`: an `EXISTS` subquery and a `SELECT DISTINCT` join through `order_items` and `products`.
--    Expected result/shape: For sql-34 Exercise 1, expected output: both forms return 2,187 orders, one per `order_id`; the `EXISTS` plan is a `Hash Semi Join`, and the join plan is a `Hash Join` under a `HashAggregate` for the `DISTINCT`. The final columns are `order_id`, and `order_date`.
--    Verify: For sql-34 Exercise 1, confirm both forms return 2,187 rows without `EXPLAIN` and that the join without `DISTINCT` also returns 2,187, because no order has two Electronics lines; then, inside `BEGIN ... ROLLBACK`, insert a second Electronics line (product 116) into order 5 and confirm the plain join grows to 2,188 rows while the `EXISTS` and `DISTINCT` forms stay at 2,187.
--    Hint ladder, rung 1: For sql-34 Exercise 1, start with the first relation in `orders`, `order_items`, and `products`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 2. Limit rows as early as possible and compare performance.
--    Inputs: For sql-34 Exercise 2, read `orders` (4,362 rows) and `customers`, and plan two forms of the latest 100 orders with country: a join followed by `ORDER BY ... LIMIT 100`, and a `top_orders` CTE `AS MATERIALIZED` that limits `orders` to 100 rows before joining `customers`.
--    Expected result/shape: For sql-34 Exercise 2, expected output: exactly 100 rows from each form on this load, newest first, starting with order 2258 and ending with order 2269; the plain plan joins all 4,362 orders before a `top-N heapsort`, while the CTE plan joins only the 100 kept orders. The final columns are `order_id`, `order_date`, and `country`. The final order is `t.order_date DESC, t.order_id DESC`.
--    Verify: For sql-34 Exercise 2, confirm the plain query `EXCEPT` the CTE query returns no rows, and that the 100 rows have 100 distinct `order_id` values; then, inside `BEGIN ... ROLLBACK`, move order 2258 to `order_date = '2000-01-01'` and confirm the CTE form now starts with order 745 and ends with order 910, the former 101st row.
--    Hint ladder, rung 1: For sql-34 Exercise 2, start with the first relation in `orders`, `customers`, and `top_orders`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 3. Prediction: compare a MATERIALIZED CTE with NOT MATERIALIZED for a recent
--    orders query. Predict which version permits more planner reordering.
--    Inputs: For sql-34 Exercise 3, run `EXPLAIN` on the same recent-orders count twice, once with `WITH recent AS MATERIALIZED (...)` and once with `AS NOT MATERIALIZED`, where `recent` keeps orders from the last 30 days and is joined to `customers`.
--    Expected result/shape: For sql-34 Exercise 3, expected output: two plans. The `MATERIALIZED` plan computes `CTE recent` separately and reads it through a `CTE Scan on recent`; the `NOT MATERIALIZED` plan folds the date filter into a `Seq Scan on orders` under the join. Both queries return the same count.
--    Verify: For sql-34 Exercise 3, run both queries without `EXPLAIN` and confirm that they return the same `count`; then confirm that only the `MATERIALIZED` plan contains a `CTE recent` node, and treat the estimated costs as plan evidence, not as a universal speed ranking.
--    Hint ladder, rung 1: For sql-34 Exercise 3, run the CTE's `SELECT` alone and count its rows before you compare the two plans.
-- 4. Construction: pre-aggregate order_items to one row per order before
--    joining orders and customers; verify that totals match the direct join.
--    Inputs: For sql-34 Exercise 4, read `order_items` (13,085 lines, 39,257 units), sum `quantity` per order in the `item_totals` CTE (4,362 rows), then join `orders` and `customers` and group by `country`.
--    Expected result/shape: For sql-34 Exercise 4, expected output: exactly 7 country rows, from IN with 5,479 units to FR with 5,711, with AU 5,529, CA 5,683, DE 5,687, GB 5,558, and US 5,610; BR is absent because its customers have no orders. The final columns are `country`, and `units`. The final order is `c.country`.
--    Verify: For sql-34 Exercise 4, confirm the seven `units` add up to 39,257, the result of `SELECT SUM(quantity) FROM order_items`, and that summing `oi.quantity` straight through the three-way join gives the same seven rows; then, inside `BEGIN ... ROLLBACK`, insert a 3-unit line into order 1 (a US customer) and confirm only US changes, from 5,610 to 5,613.
--    Hint ladder, rung 1: For sql-34 Exercise 4, run `item_totals` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
-- 5. Debugging: repair a query that joins orders and payments before
--    order_items and therefore multiplies both payment and line-item amounts.
--    Inputs: For sql-34 Exercise 5, read `payments` (3,836 rows) into `paid`, one `SUM(amount)` per order, and `order_items` into `sold`, one discounted line revenue per order, then `LEFT JOIN` both to `orders` and keep the first 20 orders.
--    Expected result/shape: For sql-34 Exercise 5, expected output: exactly 20 rows, orders 1 to 20; orders 5, 9, 14, and 20 have no payment and show `NULL` `paid_amount`, order 10 shows its two payments as 143.43, and order 17 shows 172.16 paid against 344.3105 of line revenue. The final columns are `order_id`, `paid_amount`, and `line_revenue`. The final order is `o.order_id`.
--    Verify: For sql-34 Exercise 5, confirm order 4 shows 1155.92 paid and 1155.9185 of revenue, while joining `payments` and `order_items` directly to `orders` inflates its `paid_amount` five times, to 5,779.60, because it has five item lines; then, inside `BEGIN ... ROLLBACK`, insert a second 240.20 payment for order 1 and confirm its `paid_amount` doubles to 480.40 while `line_revenue` stays 240.2000.
--    Hint ladder, rung 1: For sql-34 Exercise 5, run `paid`, and `sold` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 6. Edge case: replace NOT IN with NOT EXISTS for an anti-join and explain how
--    a NULL in the subquery changes NOT IN semantics.
--    Inputs: For sql-34 Exercise 6, read `customers` (500 rows) and test each `customer_id` against `orders` (438 distinct customers) with a correlated `NOT EXISTS`.
--    Expected result/shape: For sql-34 Exercise 6, expected output: exactly 62 rows, customers 8, 16, 24, and every eighth id up to 496, all of them in `BR`. The final columns are `customer_id`. The final order is `c.customer_id`.
--    Verify: For sql-34 Exercise 6, confirm 500 customers minus 438 distinct ordering customers equals the 62 returned rows; then append a `NULL` to the inner list with `UNION ALL SELECT NULL` and confirm `customer_id NOT IN (...)` now returns 0 rows while `NOT EXISTS` over the same list still returns 62.
--    Hint ladder, rung 1: For sql-34 Exercise 6, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
ROLLBACK;
