-- Day 9: Correlated Subqueries, EXISTS/IN
-- BEGINNER WORKFLOW - sql-09: Correlated Subqueries
-- Guide: sql/postgres-60day/companion-guides/day09_correlated_subqueries.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-09.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
SELECT
  c.*
FROM
  customers c
WHERE
  EXISTS (
    SELECT
      1
    FROM
      orders o
      JOIN order_items oi ON oi.order_id = o.order_id
      JOIN products p ON p.product_id = oi.product_id
    WHERE
      o.customer_id = c.customer_id
      AND p.category = 'Electronics')
ORDER BY
  c.customer_id;

-- IN with correlated condition
SELECT
  p.product_id,
  p.name
FROM
  products p
WHERE
  p.product_id IN ( SELECT DISTINCT
      oi.product_id
    FROM
      order_items oi
      JOIN orders o ON o.order_id = oi.order_id
    WHERE
      o.order_date >= now() - interval '30 days')
ORDER BY
  p.product_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return customers who have at least one delivered order.
--    Hint: `EXISTS` expresses the yes/no question without multiplying customer rows.
--    Inputs: For sql-09 Exercise 1, keep each of the 500 `customers` rows for which a correlated `EXISTS` finds at least one `orders` row with `status = 'delivered'`; 872 orders are delivered.
--    Expected result/shape: For sql-09 Exercise 1, return 431 rows, one per customer with a delivered order, from customer 1 to customer 500; the 62 customers without orders and 7 buyers with no delivered order (39, 169, 234, 299, 364, 429, 494) are missing. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
--    Verify: For sql-09 Exercise 1, confirm 431 equals `SELECT COUNT(DISTINCT customer_id) FROM orders WHERE status = 'delivered'`; a plain `JOIN` on the same condition returns 872 rows because it repeats customers. Inside a rolled-back transaction, set customer 38's 4 delivered orders to `shipped`; the result must drop to 430 rows.
--    Hint ladder, rung 1: For sql-09 Exercise 1, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
-- 2. [Query writing] Return products that have never been sold.
--    Hint: `NOT EXISTS` correlates on product ID and is not confused by NULL membership.
--    Inputs: For sql-09 Exercise 2, keep each of the 300 `products` rows for which `NOT EXISTS` finds no `order_items` row with the same `product_id`.
--    Expected result/shape: For sql-09 Exercise 2, return 25 rows, one per never-sold product, products 276 through 300, from Product 276 (Books) to Product 300 (Books). The final columns are `product_id`, `name`, and `category`. The final order is `p.product_id`.
--    Verify: For sql-09 Exercise 2, confirm `NOT IN (SELECT product_id FROM order_items)` and a `LEFT JOIN ... WHERE oi.product_id IS NULL` both return the same 25 products, which is safe here because `order_items.product_id` is `NOT NULL`. Inside a rolled-back transaction, insert one `order_items` row for product 276; the result must drop to 24 rows.
--    Hint ladder, rung 1: For sql-09 Exercise 2, inspect the source keys that survive `WHERE`; then check `p.product_id` before applying the row cap.
-- 3. [Query writing] Return each customer's orders that are above that customer's average order total.
--    Hint: Correlate the average to the current order's customer, not to the current order ID.
--    Inputs: For sql-09 Exercise 3, compare each of the 4,362 `orders` rows with a correlated subquery that averages `total_amount` over the same customer's orders.
--    Expected result/shape: For sql-09 Exercise 3, return 2,249 rows, one per order above its own customer's average, covering all 438 buyers; customer 1 contributes orders 4 (1155.92) and 3 (601.73). The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.customer_id, o.total_amount DESC, o.order_id`.
--    Verify: For sql-09 Exercise 3, confirm 2,249 distinct `order_id` values and that filtering on `total_amount > AVG(total_amount) OVER (PARTITION BY customer_id)` returns the same 2,249 orders. Comparing with the global average instead, as in sql-08, returns 2,269 rows, so a correlation mistake changes the count.
--    Hint ladder, rung 1: For sql-09 Exercise 3, inspect the source keys that survive `WHERE`; then check `o.customer_id, o.total_amount DESC, o.order_id` before applying the row cap.
-- 4. [Prediction] Explain and avoid the `NOT IN` plus NULL trap by finding customers without orders using `NOT EXISTS`.
--    Hint: Correlate on the customer key; a matching row alone determines exclusion.
--    Inputs: For sql-09 Exercise 4, keep each of the 500 `customers` rows for which `NOT EXISTS` finds no matching `orders` row.
--    Expected result/shape: For sql-09 Exercise 4, return 62 rows, one per customer with no orders, from customer 8 to customer 496 in steps of 8. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
--    Verify: For sql-09 Exercise 4, confirm the same 62 customers as the sql-06 `EXCEPT` result. Rewrite the filter as `customer_id NOT IN (SELECT customer_id FROM orders UNION ALL SELECT NULL)` and it must return 0 rows, which is why `NOT EXISTS` is used instead of `NOT IN` against a column that can contain `NULL`.
--    Hint ladder, rung 1: For sql-09 Exercise 4, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
-- 5. [Debugging] Return only each customer's most recent order without an arbitrary `LIMIT 1`.
--    Hint: Compare to the correlated `MAX(order_date)` and break timestamp ties with the maximum ID at that timestamp.
--    Inputs: For sql-09 Exercise 5, keep each `orders` row whose `order_id` equals a correlated subquery that picks the same customer's order by `order_date DESC, order_id DESC` with `LIMIT 1`.
--    Expected result/shape: For sql-09 Exercise 5, return 438 rows, one latest order per buyer, starting with order 5 for customer 1 and ending with order 4362 for customer 500. The final columns are `order_id`, `customer_id`, and `order_date`. The final order is `o.customer_id`.
--    Verify: For sql-09 Exercise 5, confirm 438 distinct `customer_id` values and that `DISTINCT ON (customer_id)` with the same ordering returns the same 438 orders. Inside a rolled-back transaction, insert a new order for customer 1 with the default `order_date` of `now()`; customer 1's row must switch from order 5 to the new order.
--    Hint ladder, rung 1: For sql-09 Exercise 5, inspect the source keys that survive `WHERE`; then check `o.customer_id` before applying the row cap.
-- 6. [Extension] Return customers for whom every order has at least one payment, excluding customers with no orders.
--    Hint: Require an order to exist, then prove no order lacks a payment using double `NOT EXISTS`.
--    Inputs: For sql-09 Exercise 6, keep each `customers` row that has at least one order and no order lacking a `payments` row, using `EXISTS` plus a doubly nested `NOT EXISTS`; 873 of the 4,362 orders have no payment.
--    Expected result/shape: For sql-09 Exercise 6, return 7 rows, one per customer whose every order is paid: customers 26, 91, 156, 221, 286, 351, and 481, each with 4 orders. The final columns are `customer_id`, and `full_name`. The final order is `c.customer_id`.
--    Verify: For sql-09 Exercise 6, confirm each of the 7 customers has 0 orders without a payment. Dropping the `EXISTS` guard must return 69 rows, because the 62 customers with no orders satisfy the universal condition vacuously. Inside a rolled-back transaction, delete the payments for order 223; customer 26 must leave the result, leaving 6 rows.
--    Hint ladder, rung 1: For sql-09 Exercise 6, inspect the source keys that survive `WHERE`; then check `c.customer_id` before applying the row cap.
ROLLBACK;
