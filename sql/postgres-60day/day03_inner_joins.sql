-- Day 3: INNER JOIN deep dive
-- BEGINNER WORKFLOW - sql-03: Inner Joins
-- Guide: sql/postgres-60day/companion-guides/day03_inner_joins.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-03.
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

-- Study contract
-- Focus: Use inner joins only when unmatched rows should disappear, and verify key cardinality before aggregating.
-- Assumptions: Foreign keys define expected many-to-one relationships. Net line revenue is `unit_price * quantity * (1 - discount)`.
-- Pitfall: A missing or incomplete `ON` condition creates row multiplication; joining two detail tables before aggregation can multiply measures.
-- Predict row grain and NULL/order behavior before executing each example.
-- Example: Orders with customer and items (3-table join)
SELECT
  o.order_id,
  o.order_date,
  c.full_name,
  p.name AS product,
  oi.quantity,
  oi.unit_price
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
ORDER BY
  o.order_date DESC,
  o.order_id DESC,
  p.product_id
LIMIT 50;

-- Multiple joins with filters
SELECT
  o.order_id,
  c.country,
  SUM(oi.quantity) AS total_items
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
  JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY
  o.order_id,
  c.country
ORDER BY
  total_items DESC,
  o.order_id
LIMIT 20;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List orders with customer names and countries.
--    Hint: Join the order foreign key to the customer primary key and qualify every selected column.
--    Inputs: For sql-03 Exercise 1, join the 4,362 `orders` rows to `customers` on the `customer_id` foreign key, which references the `customers` primary key, so each order finds exactly one customer. Return `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`.
--    Expected result/shape: For sql-03 Exercise 1, return 4,362 rows, one per order, newest first; order 2258 for customer 258 (`CA`) leads. The 62 customers with no orders, all of them in `BR`, do not appear. The final columns are `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`. The final order is `o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-03 Exercise 1, confirm 4,362 rows and 4,362 distinct `order_id` values, matching `SELECT COUNT(*) FROM orders`, so the inner join neither lost nor repeated an order. Count `country = 'BR'` in the output: it must be 0, because all 62 `BR` customers have no orders.
--    Hint ladder, rung 1: For sql-03 Exercise 1, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 2. [Query writing] Calculate each order item's net line revenue with the product name and category.
--    Hint: Remain at one row per order item; do not aggregate until the desired grain changes.
--    Inputs: For sql-03 Exercise 2, join the 13,085 `order_items` rows to `products` on `product_id`; the items use 275 of the 300 products and every item finds its product. Return `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`.
--    Expected result/shape: For sql-03 Exercise 2, return 13,085 rows, one per order item, starting with item 1 (order 1, product 48, `Books`, quantity 3, `line_revenue` 83.28). The final columns are `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`. The final order is `oi.order_id, oi.order_item_id`.
--    Verify: For sql-03 Exercise 2, confirm 13,085 rows and 13,085 distinct `order_item_id` values, and that the `line_revenue` column sums to 2355648.13, 1.01 above the unrounded 2355647.12 because each line is rounded before the sum. Item 1 has `unit_price` 27.76, `quantity` 3, and `discount` 0.00, so 27.76 * 3 must equal its 83.28.
--    Hint ladder, rung 1: For sql-03 Exercise 2, start with the first relation in `order_items`, and `products`; after each join, record total rows and distinct `order_item_id` so the exact fanout or loss is visible.
-- 3. [Query writing] List payments with order status and customer name.
--    Hint: Follow payments → orders → customers using each declared foreign key.
--    Inputs: For sql-03 Exercise 3, join the 3,836 `payments` rows to `orders` and then to `customers`; the payments cover 3,489 orders, 347 of which have two payments. Return `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`.
--    Expected result/shape: For sql-03 Exercise 3, return 3,836 rows, one per payment, newest first; payment 654 (order 745, `paypal`, 54.04) leads. The final columns are `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`. The final order is `p.payment_date DESC, p.payment_id DESC`.
--    Verify: For sql-03 Exercise 3, confirm 3,836 rows and 3,836 distinct `payment_id` values, matching `SELECT COUNT(*) FROM payments`, and that `COUNT(DISTINCT order_id)` in the output is 3,489. Order 10 must appear twice, once per payment, which is the expected grain here rather than fan-out.
--    Hint ladder, rung 1: For sql-03 Exercise 3, start with the first relation in `payments`, `orders`, and `customers`; after each join, record total rows and distinct `payment_id` so the exact fanout or loss is visible.
-- 4. [Prediction] Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation.
--    Hint: Aggregate items and payments separately to one row per order before joining those aggregates.
--    Inputs: For sql-03 Exercise 4, aggregate the 13,085 `order_items` rows and the 3,836 `payments` rows to one row per `order_id` each, then join both to `orders`; 873 orders have no payment and 347 have two.
--    Expected result/shape: For sql-03 Exercise 4, return 4,362 rows, one per order, with `paid_total` 0.00 for the 873 unpaid orders and no doubled item totals for the 347 two-payment orders. The final columns are `order_id`, `item_total`, and `paid_total`. The final order is `o.order_id`.
--    Verify: For sql-03 Exercise 4, confirm 4,362 distinct `order_id` values; 3,290 orders show equal totals, 199 differ, and 873 show `paid_total` 0.00. Order 10 has one item and two payments: its `item_total` must be 143.43, while joining raw `order_items` to raw `payments` before summing reports 286.86.
--    Hint ladder, rung 1: For sql-03 Exercise 4, run `item_totals`, and `payment_totals` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. [Debugging] Repair a customer/order join whose `ON` clause compares unrelated IDs.
--    Hint: Join `orders.customer_id` to `customers.customer_id`; verify output cannot exceed the order count for an inner many-to-one join.
--    Inputs: For sql-03 Exercise 5, join the 4,362 `orders` rows to `customers` on `customer_id` and count the joined rows and the distinct orders; no row-level key is returned.
--    Expected result/shape: For sql-03 Exercise 5, return exactly one row with `joined_rows` 4,362 and `distinct_orders` 4,362, which shows every order matched exactly one customer. The final columns are `joined_rows`, and `distinct_orders`.
--    Verify: For sql-03 Exercise 5, confirm both values equal `SELECT COUNT(*) FROM orders`. Reverse the join into `customers LEFT JOIN orders` and the row count must become 4,424, because the 62 customers without orders each add one unmatched row.
--    Hint ladder, rung 1: For sql-03 Exercise 5, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 6. [Extension] Calculate net line revenue by customer country without double-counting order totals.
--    Hint: Start from line items, join through orders and customers, then aggregate at country grain.
--    Inputs: For sql-03 Exercise 6, join the 13,085 `order_items` rows to `orders` and then to `customers`, and total net revenue by `country`; `BR` customers have no orders.
--    Expected result/shape: For sql-03 Exercise 6, return 7 rows, one per country with orders: `FR` first at 343290.13 and `IN` last at 329081.73, with no `BR` row. The final columns are `country`, and `net_revenue`. The final order is `net_revenue DESC, c.country`.
--    Verify: For sql-03 Exercise 6, confirm the 7 totals sum to 2355647.12, the same as `SUM(unit_price * quantity * (1 - discount))` over all of `order_items`. Starting the join from `customers` with `LEFT JOIN` must add an eighth `BR` row whose `net_revenue` is `NULL`.
--    Hint ladder, rung 1: For sql-03 Exercise 6, start with the first relation in `order_items`, `orders`, and `customers`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
ROLLBACK;
