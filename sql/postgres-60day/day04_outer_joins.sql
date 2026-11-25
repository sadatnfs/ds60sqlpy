-- Day 4: LEFT/RIGHT/FULL OUTER JOINs and NULL handling
-- BEGINNER WORKFLOW - sql-04: Outer Joins
-- Guide: sql/postgres-60day/companion-guides/day04_outer_joins.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-04.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, orders, order_items, products, payments.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.
-- Assumptions: Missing matches appear as NULL-extended columns. Decide whether absence means zero, unknown, or an exception before applying `COALESCE`.
-- Pitfall: A right-side predicate in `WHERE` can turn a left join into an inner join; put match-qualification predicates in `ON` when unmatched left rows must remain.
-- Predict row grain and NULL/order behavior before executing each example.
-- LEFT JOIN: customers without orders
SELECT
  c.customer_id,
  c.full_name,
  COUNT(o.order_id) AS orders
FROM
  customers c
  LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY
  c.customer_id,
  c.full_name
ORDER BY
  orders ASC,
  c.customer_id
LIMIT 25;

-- RIGHT JOIN: products that appear in orders (or not)
SELECT
  p.product_id,
  p.name,
  COALESCE(SUM(oi.quantity), 0) AS sold_qty
FROM
  order_items oi
  RIGHT JOIN products p ON p.product_id = oi.product_id
GROUP BY
  p.product_id,
  p.name
ORDER BY
  sold_qty ASC,
  p.product_id
LIMIT 25;

-- FULL OUTER JOIN: payments vs orders.
-- A payment foreign key prevents an orphan payment in this dataset, while an
-- order may legitimately have no payment. Keep both keys visible when auditing.
SELECT
  o.order_id,
  p.payment_id,
  p.order_id AS payment_order_id,
  o.total_amount,
  p.amount AS payment_amount
FROM
  orders o
  FULL OUTER JOIN payments p ON p.order_id = o.order_id
WHERE
  o.order_id IS NULL
  OR p.order_id IS NULL
ORDER BY
  COALESCE(o.order_id, p.order_id),
  p.payment_id;

-- mismatches
-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List every customer with order count, including customers with zero orders.
--    Hint: Start from customers, left join orders, and count the nullable order key rather than `COUNT(*)`.
--    Inputs: For sql-04 Exercise 1, start from all 500 `customers` and `LEFT JOIN` the 4,362 `orders`; 62 customers have no orders. Return `customer_id`, `full_name`, and `order_count`.
--    Expected result/shape: For sql-04 Exercise 1, return 500 rows, one per customer: 33 customers tie at the maximum of 16 orders, starting with customer 12, and the 62 customers without orders show 0 at the bottom. The final columns are `customer_id`, `full_name`, and `order_count`. The final order is `order_count DESC, c.customer_id`.
--    Verify: For sql-04 Exercise 1, confirm 500 distinct `customer_id` values and that `order_count` sums to 4,362, the size of `orders`. Count rows with `order_count = 0` and expect 62; changing `COUNT(o.order_id)` to `COUNT(*)` would turn each of those zeros into 1.
--    Hint ladder, rung 1: For sql-04 Exercise 1, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, and `full_name` so the exact fanout or loss is visible.
-- 2. [Query writing] Find products that have never appeared in an order item.
--    Hint: Left join and retain rows where the right-side primary key is NULL.
--    Inputs: For sql-04 Exercise 2, `LEFT JOIN` all 300 `products` to the 13,085 `order_items` and keep only rows where `oi.order_item_id IS NULL`; the items use 275 distinct products.
--    Expected result/shape: For sql-04 Exercise 2, return 25 rows, one per product that has never been sold: products 276 through 300. The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
--    Verify: For sql-04 Exercise 2, confirm 300 products minus 275 sold products leaves the 25 returned rows, and that `SELECT COUNT(*) FROM products p WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.product_id)` also returns 25. Inside a rolled-back transaction, add one `order_items` row for product 300; the result must drop to 24 rows, ending at product 299.
--    Hint ladder, rung 1: For sql-04 Exercise 2, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id` so the exact fanout or loss is visible.
-- 3. [Query writing] Compare monthly budgets and expenses by category with a full outer join.
--    Hint: Aggregate each side to the same category/month grain before joining; preserve keys from either side.
--    Inputs: For sql-04 Exercise 3, aggregate `budgets` (125 rows) and `expenses` (10,000 rows) separately to one row per category and month, then `FULL JOIN` the two; each side has 125 category-month keys over 25 months and 5 categories.
--    Expected result/shape: For sql-04 Exercise 3, return 125 rows, one per category and month, from the oldest budget month to the current month; on the fixture every key exists on both sides, so no amount is `NULL`. The final columns are `category`, `period`, `budget_amount`, and `actual_amount`. The final order is `period, category`.
--    Verify: For sql-04 Exercise 3, confirm 125 distinct `(category, period)` pairs and zero `NULL` values in either amount column. Inside a rolled-back transaction, delete the `COGS` expenses for the oldest month; the result must still have 125 rows, now with one `NULL` `actual_amount`, while an inner join would drop to 124.
--    Hint ladder, rung 1: For sql-04 Exercise 3, run `expense_months`, and `budget_months` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 4. [Prediction] Preserve every customer while counting only delivered orders; compare a status predicate in `ON` with the same predicate in `WHERE`.
--    Hint: Place `o.status = 'delivered'` in `ON`; `WHERE` would remove NULL-extended customers.
--    Inputs: For sql-04 Exercise 4, start from all 500 `customers` and `LEFT JOIN` `orders` with `o.status = 'delivered'` inside the `ON` clause; 872 orders are delivered.
--    Expected result/shape: For sql-04 Exercise 4, return 500 rows, one per customer: 7 customers lead with 4 delivered orders, starting with customer 38, and 69 customers show 0. The final columns are `customer_id`, `full_name`, and `delivered_orders`. The final order is `delivered_orders DESC, c.customer_id`.
--    Verify: For sql-04 Exercise 4, confirm 500 rows and that `delivered_orders` sums to 872, matching `SELECT COUNT(*) FROM orders WHERE status = 'delivered'`. Move the status test from `ON` to `WHERE` and the result must shrink to 431 customers, because the 69 zero rows are filtered out.
--    Hint ladder, rung 1: For sql-04 Exercise 4, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, and `full_name` so the exact fanout or loss is visible.
-- 5. [Debugging] Repair `COUNT(*)` in a left-join order count so customers without orders report zero rather than one.
--    Hint: Count a non-nullable right-side key that becomes NULL for an unmatched row.
--    Inputs: For sql-04 Exercise 5, start from all 500 `customers` and `LEFT JOIN` `orders`, counting `o.order_id` rather than `*`; 62 customers have no orders.
--    Expected result/shape: For sql-04 Exercise 5, return 500 rows in `customer_id` order; customer 1 has 5 orders, customer 8 has 0, and customer 500 has 10. The final columns are `customer_id`, and `order_count`. The final order is `c.customer_id`.
--    Verify: For sql-04 Exercise 5, confirm `order_count` sums to 4,362 across 438 nonzero rows and 62 zero rows. The buggy `COUNT(*)` version sums to 4,424 instead, because each of the 62 unmatched customers contributes one all-`NULL` joined row.
--    Hint ladder, rung 1: For sql-04 Exercise 5, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id` so the exact fanout or loss is visible.
-- 6. [Extension] Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys.
--    Hint: Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero.
--    Inputs: For sql-04 Exercise 6, `FULL JOIN` all 300 `products` to the 13,085 `order_items` on `product_id`, which produces 13,110 joined rows, and count distinct product keys by match state.
--    Expected result/shape: For sql-04 Exercise 6, return exactly one row: `matched_products` 275, `unsold_products` 25, and `orphan_item_product_ids` 0. The final columns are `matched_products`, `unsold_products`, and `orphan_item_product_ids`.
--    Verify: For sql-04 Exercise 6, confirm 275 + 25 equals `SELECT COUNT(*) FROM products` and that 13,110 joined rows equal 13,085 items plus the 25 unsold products. The orphan count must be 0, because `order_items.product_id` is a foreign key to `products` and cannot point at a missing product.
--    Hint ladder, rung 1: For sql-04 Exercise 6, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id` so the exact fanout or loss is visible.
ROLLBACK;
