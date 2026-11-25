-- Day 20: FIRST_VALUE and LAST_VALUE
-- BEGINNER WORKFLOW - sql-20: FIRST_VALUE and LAST_VALUE
-- Guide: sql/postgres-60day/companion-guides/day20_first_last_value.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-20.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use `FIRST_VALUE` and `LAST_VALUE` only with an ordering and frame that covers the intended partition.
-- Assumptions: First/last refer to ordered rows, not minimum/maximum values unless ordering states that. Ties need unique keys for deterministic row identity.
-- Pitfall: The default `LAST_VALUE` frame ends at the current row/peer group, often making it return the current value rather than the partition's final value.
-- Predict row grain and NULL/order behavior before executing each example.
-- First and last order amount per customer
SELECT
  o.customer_id,
  o.order_id,
  o.order_date,
  o.total_amount,
  FIRST_VALUE(o.total_amount) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_order_amount,
  LAST_VALUE(o.total_amount) OVER (PARTITION BY o.customer_id ORDER BY o.order_date, o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_order_amount
FROM
  orders o
ORDER BY
  o.customer_id,
  o.order_date,
  o.order_id
LIMIT 100;

-- Compare current to first/last
WITH per_cust AS (
  SELECT
    o.customer_id,
    o.order_id,
    o.order_date,
    o.total_amount,
    FIRST_VALUE(o.total_amount) OVER (PARTITION BY o.customer_id ORDER BY o.order_date,
      o.order_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_amt
  FROM
    orders o
)
SELECT
  *,
  ROUND(total_amount - first_amt, 2) AS delta_from_first
FROM
  per_cust
ORDER BY
  customer_id,
  order_date,
  order_id
LIMIT 100;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Show every order with the customer's first and last order timestamps.
--    Hint: Use one full-partition frame from unbounded preceding through unbounded following.
--    Inputs: For sql-20 Exercise 1, read from `orders` and return, for every order, its customer's first and last `order_date` with `FIRST_VALUE` and `LAST_VALUE` over a named window partitioned by `customer_id`, ordered by `order_date, order_id`, with the frame `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.
--    Expected result/shape: For sql-20 Exercise 1, return 4,362 rows, one per order, where both dates stay constant within each of the 438 customers; customer 1's five rows all show order 1's date as `first_order_date` and order 5's date as `last_order_date`. The final columns are `order_id`, `customer_id`, `order_date`, `first_order_date`, and `last_order_date`. The final order is `o.customer_id, o.order_date, o.order_id`.
--    Verify: For sql-20 Exercise 1, confirm 4362 rows and compare them with `SELECT customer_id, MIN(order_date), MAX(order_date) FROM orders GROUP BY customer_id` (438 customers): no row may differ. With the default frame instead, `LAST_VALUE` returns each row's own `order_date` on all 4362 rows.
--    Hint ladder, rung 1: For sql-20 Exercise 1, write the window with an explicit full frame first, then remove the frame clause once and watch `LAST_VALUE` change.
-- 2. [Query writing] Show each product with the cheapest and most expensive price in its category.
--    Hint: Order by price and use a full frame; values tie without needing row identity.
--    Inputs: For sql-20 Exercise 2, read from `products` and show each product with the lowest and highest `price` in its `category`, using `FIRST_VALUE` and `LAST_VALUE` over a window ordered by `price, product_id` with a full frame.
--    Expected result/shape: For sql-20 Exercise 2, return 300 rows, one per product, with two values per category; `Apparel` rows all show 10.37 and 119.15, `Books` rows show 12.22 and 121.00, and `Sports` rows show 11.85 and 120.63. The final columns are `product_id`, `category`, `price`, `category_min_price`, and `category_max_price`. The final order is `p.category, p.price, p.product_id`.
--    Verify: For sql-20 Exercise 2, confirm 300 rows and compare the two window columns with `SELECT category, MIN(price), MAX(price) FROM products GROUP BY category`; for example, every `Apparel` row must show 10.37 and 119.15.
--    Hint ladder, rung 1: For sql-20 Exercise 2, compute `MIN(price)` and `MAX(price)` per category with `GROUP BY` first; the window columns must repeat those values on every product row.
-- 3. [Query writing] Compare every payment with the first and last payment amount for its order.
--    Hint: Partition by order, order by timestamp/payment ID, and keep the full frame.
--    Inputs: For sql-20 Exercise 3, read from `payments` and compare every payment with the first and last payment `amount` of its order, using a window partitioned by `order_id`, ordered by `payment_date, payment_id`, with a full frame.
--    Expected result/shape: For sql-20 Exercise 3, return 3,836 rows, one per payment; on the 3,142 single-payment orders both window columns repeat the payment's own `amount`, while order 10's two payments show a first amount of 71.72 and a last of 71.71. The final columns are `payment_id`, `order_id`, `payment_date`, `amount`, `first_payment_amount`, and `last_payment_amount`. The final order is `p.order_id, p.payment_date, p.payment_id`.
--    Verify: For sql-20 Exercise 3, confirm 3836 rows, one per `payment_id`; 3489 orders have payments, 347 of them have two payments, and only 20 orders have a first amount that differs from the last, so check one of those 20 orders by hand.
--    Hint ladder, rung 1: For sql-20 Exercise 3, count payments per `order_id` first; only orders with two payments can show different first and last amounts.
-- 4. [Prediction] Demonstrate the default `LAST_VALUE` result versus a full-partition frame on values 10, 20, 30.
--    Hint: The default ends at the current row; explicit following reaches the true last row.
--    Inputs: For sql-20 Exercise 4, apply `LAST_VALUE(value)` to the three-row `VALUES` fixture `(10), (20), (30)` twice: once over `ORDER BY value` with the default frame, and once with `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.
--    Expected result/shape: For sql-20 Exercise 4, return three rows: values 10, 20, and 30 with `default_last_value` 10, 20, and 30 and `partition_last_value` 30 on every row. The final columns are `value`, `default_last_value`, and `partition_last_value`. The final order is `value`.
--    Verify: For sql-20 Exercise 4, check by hand that the default frame stops at the current row, so `default_last_value` repeats `value`, while the full frame reaches 30. Add `(NULL::int)` to the fixture; ascending order puts `NULL` last, so all four rows must then show `NULL` as `partition_last_value`, while the first three keep `default_last_value` 10, 20, and 30.
--    Hint ladder, rung 1: For sql-20 Exercise 4, inspect one window partition before projecting; then check `value` before applying the row cap.
-- 5. [Debugging] Return one first and one last order per customer without using window output as an accidental duplicate report.
--    Hint: Compute first/last IDs with full-frame windows, then select distinct customer-level output.
--    Inputs: For sql-20 Exercise 5, read from `orders`, compute each customer's first and last `order_id` with full-frame `FIRST_VALUE` and `LAST_VALUE` windows ordered by `order_date, order_id` in the CTE `annotated`, then return one row per customer with `SELECT DISTINCT`.
--    Expected result/shape: For sql-20 Exercise 5, return 438 rows, one per customer with orders; customer 1 shows orders 1 and 5, customer 2 shows 6 and 11, and customer 500 shows 4353 and 4362. The final columns are `customer_id`, `first_order_id`, and `last_order_id`. The final order is `customer_id`.
--    Verify: For sql-20 Exercise 5, confirm 438 rows, one per customer with orders, equal to `SELECT COUNT(DISTINCT customer_id) FROM orders`; without `DISTINCT`, the same query returns 4362 rows, one per order, with each customer's values repeated.
--    Hint ladder, rung 1: For sql-20 Exercise 5, run `annotated` alone and count its rows (4362) before you collapse it to one row per `customer_id`.
-- 6. [Extension] Solve latest order per customer with PostgreSQL `DISTINCT ON` and compare its ordering contract with row number.
--    Hint: `DISTINCT ON` keeps the first row under its mandatory leading order keys.
--    Inputs: For sql-20 Exercise 6, keep one row per customer from the 4,362 `orders` rows with `SELECT DISTINCT ON (o.customer_id)`, where `ORDER BY o.order_date DESC, o.order_id DESC` decides which row survives.
--    Expected result/shape: For sql-20 Exercise 6, return 438 rows, one latest order per customer with orders; customer 1 returns order 5 for 105.84, customer 2 returns order 11 for 680.50, and customer 500 returns order 4362 for 951.76. The final columns are `customer_id`, `order_id`, `order_date`, and `total_amount`. The final order is `o.customer_id, o.order_date DESC, o.order_id DESC`.
--    Verify: For sql-20 Exercise 6, confirm 438 distinct `customer_id` values, that every `order_id` equals the `last_order_id` from Exercise 5, and that the kept `total_amount` values add up to 252375.44. Inside a rolled-back transaction, set order 5's `order_date` to order 4's; customer 1 must still return order 5 because `o.order_id DESC` breaks the tie, and changing that key to `o.order_id ASC` must return order 4 for 1155.92.
--    Hint ladder, rung 1: For sql-20 Exercise 6, check `o.customer_id, o.order_date DESC, o.order_id DESC` before applying the row cap.
ROLLBACK;
