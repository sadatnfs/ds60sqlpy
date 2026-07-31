-- Day 3: INNER JOIN deep dive
-- BEGINNER WORKFLOW — sql-03: Inner Joins
-- Guide: sql/postgres-60day/companion-guides/day03_inner_joins.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-03/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
SELECT o.order_id, o.order_date, c.full_name, p.name AS product, oi.quantity, oi.unit_price
FROM orders o
JOIN customers c   ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN products p    ON p.product_id = oi.product_id
ORDER BY o.order_date DESC, o.order_id DESC, p.product_id
LIMIT 50;

-- Multiple joins with filters
SELECT o.order_id, c.country, SUM(oi.quantity) AS total_items
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, c.country
ORDER BY total_items DESC, o.order_id
LIMIT 20;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List orders with customer names and countries.
--    Hint: Join the order foreign key to the customer primary key and qualify every selected column.
--    Inputs: For sql-03 Exercise 1, read from `orders`, and `customers`. Build the answer toward `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-03 Exercise 1, expected output: One row per order. The final columns are `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country`. The final order is `o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-03 Exercise 1, project `order_id` plus the raw source columns from `orders`, and `customers` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `order_date`, `total_amount`, `customer_id`, `full_name`, and `country` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-03 Exercise 1, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 2. [Query writing] Calculate each order item's net line revenue with the product name and category.
--    Hint: Remain at one row per order item; do not aggregate until the desired grain changes.
--    Inputs: For sql-03 Exercise 2, read from `order_items`, and `products`. Build the answer toward `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`; keep `order_item_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-03 Exercise 2, expected output: One row per order item. The final columns are `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue`. The final order is `oi.order_id, oi.order_item_id`.
--    Verify: For sql-03 Exercise 2, project `order_item_id` plus the raw source columns from `order_items`, and `products` at each join stage; record row count and distinct `order_item_id`, then assert the final `order_item_id`, `order_id`, `product_id`, `name`, `category`, `quantity`, and `line_revenue` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_item_id`; verify the result gains exactly one row carrying that `order_item_id` value.
--    Hint ladder, rung 1: For sql-03 Exercise 2, start with the first relation in `order_items`, and `products`; after each join, record total rows and distinct `order_item_id` so the exact fanout or loss is visible.
-- 3. [Query writing] List payments with order status and customer name.
--    Hint: Follow payments → orders → customers using each declared foreign key.
--    Inputs: For sql-03 Exercise 3, read from `payments`, `orders`, and `customers`. Build the answer toward `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`; keep `payment_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-03 Exercise 3, expected output: One row per payment. The final columns are `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name`. The final order is `p.payment_date DESC, p.payment_id DESC`.
--    Verify: For sql-03 Exercise 3, project `payment_id` plus the raw source columns from `payments`, `orders`, and `customers` at each join stage; record row count and distinct `payment_id`, then assert the final `payment_id`, `payment_date`, `amount`, `method`, `order_id`, `status`, and `full_name` values match those staged rows without unintended fanout or loss. Add one source row with a new `payment_id`; verify the result gains exactly one row carrying that `payment_id` value.
--    Hint ladder, rung 1: For sql-03 Exercise 3, start with the first relation in `payments`, `orders`, and `customers`; after each join, record total rows and distinct `payment_id` so the exact fanout or loss is visible.
-- 4. [Prediction] Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation.
--    Hint: Aggregate items and payments separately to one row per order before joining those aggregates.
--    Inputs: For sql-03 Exercise 4, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `item_total`, and `paid_total`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-03 Exercise 4, expected output: One row per order; no six-row multiplication. The final columns are `order_id`, `item_total`, and `paid_total`. The final order is `o.order_id`.
--    Verify: For sql-03 Exercise 4, project `order_id` plus the raw source columns from `order_items`, `payments`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `item_total`, and `paid_total` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-03 Exercise 4, run `item_totals`, and `payment_totals` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. [Debugging] Repair a customer/order join whose `ON` clause compares unrelated IDs.
--    Hint: Join `orders.customer_id` to `customers.customer_id`; verify output cannot exceed the order count for an inner many-to-one join.
--    Inputs: For sql-03 Exercise 5, read from `orders`, and `customers`. Build the answer toward `joined_rows`, and `distinct_orders`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-03 Exercise 5, expected output: Exactly one customer match per order. The final columns are `joined_rows`, and `distinct_orders`.
--    Verify: For sql-03 Exercise 5, project `order_id` plus the raw source columns from `orders`, and `customers` at each join stage; record row count and distinct `order_id`, then assert the final `joined_rows`, and `distinct_orders` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-03 Exercise 5, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
-- 6. [Extension] Calculate net line revenue by customer country without double-counting order totals.
--    Hint: Start from line items, join through orders and customers, then aggregate at country grain.
--    Inputs: For sql-03 Exercise 6, read from `order_items`, `orders`, and `customers`. Build the answer toward `country`, and `net_revenue`; keep `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-03 Exercise 6, expected output: One row per country represented by an order. The final columns are `country`, and `net_revenue`. The final order is `net_revenue DESC, c.country`.
--    Verify: For sql-03 Exercise 6, independently aggregate `order_items`, `orders`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `net_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `net_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-03 Exercise 6, start with the first relation in `order_items`, `orders`, and `customers`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.

ROLLBACK;
