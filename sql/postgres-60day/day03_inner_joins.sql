-- Day 3: INNER JOIN deep dive
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
-- 2. [Query writing] Calculate each order item's net line revenue with the product name and category.
--    Hint: Remain at one row per order item; do not aggregate until the desired grain changes.
-- 3. [Query writing] List payments with order status and customer name.
--    Hint: Follow payments → orders → customers using each declared foreign key.
-- 4. [Prediction] Predict the row count from joining one order with three items and two payments directly, then write a safe per-order reconciliation.
--    Hint: Aggregate items and payments separately to one row per order before joining those aggregates.
-- 5. [Debugging] Repair a customer/order join whose `ON` clause compares unrelated IDs.
--    Hint: Join `orders.customer_id` to `customers.customer_id`; verify output cannot exceed the order count for an inner many-to-one join.
-- 6. [Extension] Calculate net line revenue by customer country without double-counting order totals.
--    Hint: Start from line items, join through orders and customers, then aggregate at country grain.

ROLLBACK;
