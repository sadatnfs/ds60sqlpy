-- Day 8: Scalar & Inline Subqueries
-- BEGINNER WORKFLOW - sql-08: Scalar Inline Subqueries
-- Guide: sql/postgres-60day/companion-guides/day08_scalar_inline_subqueries.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-08.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items, customers, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.
-- Assumptions: A scalar subquery returning no rows becomes NULL; more than one row is an error. Order a `LIMIT 1` subquery deterministically.
-- Pitfall: Adding `LIMIT 1` to hide an unintended multi-row result creates arbitrary logic unless `ORDER BY` defines the chosen row.
-- Predict row grain and NULL/order behavior before executing each example.
-- Scalar subquery in SELECT: customer lifetime revenue
SELECT
  c.customer_id,
  c.full_name,
  (
    SELECT
      ROUND(COALESCE(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 0), 2)
    FROM
      orders o
      JOIN order_items oi ON oi.order_id = o.order_id
    WHERE
      o.customer_id = c.customer_id) AS lifetime_revenue
FROM
  customers c
ORDER BY
  lifetime_revenue DESC,
  c.customer_id
LIMIT 20;

-- Inline subquery in FROM
SELECT
  x.category,
  ROUND(AVG(x.order_total), 2) AS avg_order_total
FROM (
  SELECT
    p.category,
    o.order_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_total
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
  GROUP BY
    p.category,
    o.order_id) x
GROUP BY
  x.category
ORDER BY
  avg_order_total DESC,
  x.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return orders whose total exceeds the overall average order total.
--    Hint: The aggregate subquery is guaranteed to return exactly one value.
--    Inputs: For sql-08 Exercise 1, compare each of the 4,362 `orders` rows with one scalar subquery, `SELECT AVG(total_amount) FROM orders`, which evaluates to about 540.0383.
--    Expected result/shape: For sql-08 Exercise 1, return 2,269 rows, one per order above the average, from 16 orders tied at 1432.49 (order 104 first) down to 540.27. The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.total_amount DESC, o.order_id`.
--    Verify: For sql-08 Exercise 1, confirm 2,269 distinct `order_id` values and that the complementary filter `total_amount <= (SELECT AVG(total_amount) FROM orders)` returns the other 2,093 orders, topping out at 538.05. Replace `AVG(all_orders.total_amount)` with the bare column and the query must fail with `more than one row returned by a subquery used as an expression`.
--    Hint ladder, rung 1: For sql-08 Exercise 1, inspect the source keys that survive `WHERE`; then check `o.total_amount DESC, o.order_id` before applying the row cap.
-- 2. [Query writing] Add the total customer count as a scalar column beside each country-level customer count.
--    Hint: An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.
--    Inputs: For sql-08 Exercise 2, group the 500 `customers` rows by `country` and add an uncorrelated scalar subquery, `SELECT COUNT(*) FROM customers`, as a constant column.
--    Expected result/shape: For sql-08 Exercise 2, return 8 rows, one per country: CA, DE, GB, and US with 63 customers, then AU, BR, FR, and IN with 62, each showing `all_customers` = 500. The final columns are `country`, `country_customers`, and `all_customers`. The final order is `country_customers DESC, c.country`.
--    Verify: For sql-08 Exercise 2, confirm the `country_customers` values sum to 500, the value repeated in every `all_customers` cell. Inside a rolled-back transaction, insert one customer from `MX`; the result must grow to 9 rows, with `MX` at 1 and every `all_customers` value at 501.
--    Hint ladder, rung 1: For sql-08 Exercise 2, confirm the groups are `country`; then check `country_customers DESC, c.country` before applying the row cap.
-- 3. [Query writing] Show each customer with their latest order timestamp using a scalar correlated subquery.
--    Hint: Use `MAX` to guarantee one result and let customers without orders receive NULL.
--    Inputs: For sql-08 Exercise 3, list all 500 `customers` and fill `latest_order_date` with a correlated subquery that takes `MAX(order_date)` over that customer's `orders`.
--    Expected result/shape: For sql-08 Exercise 3, return 500 rows, one per customer: 438 dated rows, newest first and led by customer 258 on a freshly loaded fixture, then the 62 customers without orders with a `NULL` date. The final columns are `customer_id`, `full_name`, and `latest_order_date`. The final order is `latest_order_date DESC NULLS LAST, c.customer_id`.
--    Verify: For sql-08 Exercise 3, confirm 438 non-`NULL` dates, all distinct, so the `c.customer_id` tiebreaker only orders the 62 `NULL` rows. A `LEFT JOIN` to `orders` grouped by customer must return the same 500 `(customer_id, latest_order_date)` pairs; removing `NULLS LAST` must move customers 8 through 496 to the top.
--    Hint ladder, rung 1: For sql-08 Exercise 3, inspect the source keys that survive `WHERE`; then check `latest_order_date DESC NULLS LAST, c.customer_id` before applying the row cap.
-- 4. [Prediction] Demonstrate that a scalar subquery with no matching rows returns NULL.
--    Hint: Use a deliberately impossible product key and test the scalar result with `IS NULL`.
--    Inputs: For sql-08 Exercise 4, wrap a scalar subquery that selects `price` for `product_id = -1`, an ID no `products` row has, and test the result with `IS NULL`.
--    Expected result/shape: For sql-08 Exercise 4, return one row with `no_row_becomes_null` = `true`. The final columns are `no_row_becomes_null`.
--    Verify: For sql-08 Exercise 4, confirm `SELECT COUNT(*) FROM products WHERE product_id = -1` returns 0, so the scalar subquery has no row and yields `NULL`. Point the subquery at product 300 instead and the column must become `false`, because that row exists with a price of 121.00.
--    Hint ladder, rung 1: For sql-08 Exercise 4, inspect the source keys that survive `WHERE`.
-- 5. [Debugging] Repair a scalar subquery that returns many product prices by aggregating to the intended single value.
--    Hint: Choose the business reduction explicitly; this answer uses maximum price.
--    Inputs: For sql-08 Exercise 5, group the 300 `products` rows (50 per category) by `category` for `MAX(price)`, and add the uncorrelated subquery `SELECT MAX(price) FROM products` as a constant column.
--    Expected result/shape: For sql-08 Exercise 5, return 6 rows, one per category from Apparel (119.15) to Sports (120.63); every row shows `global_max_price` = 121.00, which only Books reaches, through product 300. The final columns are `category`, `category_max_price`, and `global_max_price`. The final order is `p.category`.
--    Verify: For sql-08 Exercise 5, confirm `global_max_price` equals the largest `category_max_price` (121.00 for Books). Inside a rolled-back transaction, set product 1's price to 130.00; Apparel's maximum and every `global_max_price` value must become 130.00, while the other five category maximums stay the same.
--    Hint ladder, rung 1: For sql-08 Exercise 5, confirm the groups are `category`; then check `p.category` before applying the row cap.
-- 6. [Extension] Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report.
--    Hint: Compute the global total once, then cross join the guaranteed one-row relation.
--    Inputs: For sql-08 Exercise 6, read from `customers`; compute the overall customer count once in a one-row CTE named `global`, then return each `country` with `country_customers` and `customer_share`, its fraction of all customers rounded to 4 places.
--    Expected result/shape: For sql-08 Exercise 6, return 8 rows, one per country, with the four 63-customer countries (CA, DE, GB, US) first at 0.1260 and the four 62-customer countries (AU, BR, FR, IN) after them at 0.1240. The final columns are `country`, `country_customers`, and `customer_share`. The final order is `customer_share DESC, c.country`.
--    Verify: For sql-08 Exercise 6, confirm 8 rows whose `country_customers` add up to `SELECT COUNT(*) FROM customers` (500) and whose `customer_share` values add up to 1.0000; on the seed, CA, DE, GB, and US have 63 customers (0.1260) and AU, BR, FR, and IN have 62 (0.1240).
--    Hint ladder, rung 1: For sql-08 Exercise 6, run `global` alone and confirm it returns one row; cross joining a one-row relation does not multiply the grouped rows.
ROLLBACK;
