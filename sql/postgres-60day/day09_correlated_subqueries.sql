-- Day 9: Correlated Subqueries, EXISTS/IN
-- BEGINNER WORKFLOW — sql-09: Correlated Subqueries
-- Guide: sql/postgres-60day/companion-guides/day09_correlated_subqueries.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-09/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, orders, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.
-- Assumptions: `EXISTS` tests whether at least one row qualifies and ignores selected values. `NOT EXISTS` remains safe when inner columns can be NULL.
-- Pitfall: A correlated subquery can run conceptually per outer row; do not use it when a join or pre-aggregation states the grain more clearly.
-- Predict row grain and NULL/order behavior before executing each example.

-- EXISTS: customers who purchased Electronics
SELECT c.*
FROM customers c
WHERE EXISTS (
  SELECT 1
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.customer_id = c.customer_id
    AND p.category = 'Electronics'
)
ORDER BY c.customer_id;

-- IN with correlated condition
SELECT p.product_id, p.name
FROM products p
WHERE p.product_id IN (
  SELECT DISTINCT oi.product_id
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  WHERE o.order_date >= now() - interval '30 days'
)
ORDER BY p.product_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return customers who have at least one delivered order.
--    Hint: `EXISTS` expresses the yes/no question without multiplying customer rows.
--    Inputs: For sql-09 Exercise 1, read from `customers`, and `orders`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-09 Exercise 1, expected output: One row per qualifying customer. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
--    Verify: For sql-09 Exercise 1, run an anti-check that counts rows where NOT ((EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND o.status = 'delivered' ))); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`, and `orders`. Add one row for which `(EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND o.status = 'delivered' ))` is true and one for which it is false; verify only the matching `customer_id` value is returned.
--    Hint ladder, rung 1: For sql-09 Exercise 1, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
-- 2. [Query writing] Return products that have never been sold.
--    Hint: `NOT EXISTS` correlates on product ID and is not confused by NULL membership.
--    Inputs: For sql-09 Exercise 2, read from `products`, and `order_items`. Build the answer toward `product_id`, `name`, and `category`; keep `product_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-09 Exercise 2, expected output: One row per unsold product. The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
--    Verify: For sql-09 Exercise 2, run an anti-check that counts rows where NOT ((NOT EXISTS ( SELECT 1 FROM order_items AS oi WHERE oi.product_id = p.product_id ))); require unique `product_id` where the expected grain is one row per key and confirm the projected `product_id`, `name`, and `category` against `products`, and `order_items`. Add one row for which `(NOT EXISTS ( SELECT 1 FROM order_items AS oi WHERE oi.product_id = p.product_id ))` is true and one for which it is false; verify only the matching `product_id` value is returned.
--    Hint ladder, rung 1: For sql-09 Exercise 2, inspect the source keys that survive `WHERE`; then check `p.product_id` before applying the row cap.
-- 3. [Query writing] Return each customer's orders that are above that customer's average order total.
--    Hint: Correlate the average to the current order's customer, not to the current order ID.
--    Inputs: For sql-09 Exercise 3, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-09 Exercise 3, expected output: Order rows above their own customer average. The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.customer_id, o.total_amount DESC, o.order_id`.
--    Verify: For sql-09 Exercise 3, run an anti-check that counts rows where NOT ((o.total_amount > ( SELECT AVG(peer.total_amount) FROM orders AS peer WHERE peer.customer_id = o.customer_id ))); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `total_amount` against `orders`. Add one row for which `(o.total_amount > ( SELECT AVG(peer.total_amount) FROM orders AS peer WHERE peer.customer_id = o.customer_id ))` is true and one for which it is false; verify only the matching `order_id` value is returned.
--    Hint ladder, rung 1: For sql-09 Exercise 3, inspect the source keys that survive `WHERE`; then check `o.customer_id, o.total_amount DESC, o.order_id` before applying the row cap.
-- 4. [Prediction] Explain and avoid the `NOT IN` plus NULL trap by finding customers without orders using `NOT EXISTS`.
--    Hint: Correlate on the customer key; a matching row alone determines exclusion.
--    Inputs: For sql-09 Exercise 4, read from `customers`, and `orders`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-09 Exercise 4, expected output: One row per customer with no order. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
--    Verify: For sql-09 Exercise 4, run an anti-check that counts rows where NOT ((NOT EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id ))); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`, and `orders`. Repeat with `NULL` in `customer_id`, and `full_name` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-09 Exercise 4, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
-- 5. [Debugging] Return only each customer's most recent order without an arbitrary `LIMIT 1`.
--    Hint: Compare to the correlated `MAX(order_date)` and break timestamp ties with the maximum ID at that timestamp.
--    Inputs: For sql-09 Exercise 5, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `order_date`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-09 Exercise 5, expected output: At most one deterministic order per customer. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `o.customer_id`.
--    Verify: For sql-09 Exercise 5, run an anti-check that counts rows where NOT ((o.order_id = ( SELECT candidate.order_id FROM orders AS candidate WHERE candidate.customer_id = o.customer_id ORDER BY candidate.order_date DESC, candidate.order_id DESC LIMIT 1 ))); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `order_date` against `orders`. Add one row for which `(o.order_id = ( SELECT candidate.order_id FROM orders AS candidate WHERE candidate.customer_id = o.customer_id ORDER BY candidate.order_date DESC, candidate.order_id DESC LIMIT 1 ))` is true and one for which it is false; verify only the matching `order_id` value is returned.
--    Hint ladder, rung 1: For sql-09 Exercise 5, inspect the source keys that survive `WHERE`; then check `o.customer_id` before applying the row cap.
-- 6. [Extension] Return customers for whom every order has at least one payment, excluding customers with no orders.
--    Hint: Require an order to exist, then prove no order lacks a payment using double `NOT EXISTS`.
--    Inputs: For sql-09 Exercise 6, read from `customers`, `orders`, and `payments`. Build the answer toward `customer_id`, and `full_name`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-09 Exercise 6, expected output: One row per customer satisfying the universal condition. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
--    Verify: For sql-09 Exercise 6, run an anti-check that counts rows where NOT ((EXISTS ( SELECT 1 FROM orders AS any_order WHERE any_order.customer_id = c.customer_id ) AND NOT EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND NOT EXISTS ( SELECT 1 FROM payments AS p WHERE p.order_id = o.order_)); require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, and `full_name` against `customers`, `orders`, and `payments`. Add one row for which `(EXISTS ( SELECT 1 FROM orders AS any_order WHERE any_order.customer_id = c.customer_id ) AND NOT EXISTS ( SELECT 1 FROM orders AS o WHERE o.customer_id = c.customer_id AND NOT EXISTS ( SELECT 1 FROM payments AS p WHERE p.order_id = o.order_)` is true and one for which it is false; verify only the matching `customer_id` value is returned.
--    Hint ladder, rung 1: For sql-09 Exercise 6, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.

ROLLBACK;
