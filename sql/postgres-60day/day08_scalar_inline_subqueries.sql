-- Day 8: Scalar & Inline Subqueries
-- BEGINNER WORKFLOW — sql-08: Scalar Inline Subqueries
-- Guide: sql/postgres-60day/companion-guides/day08_scalar_inline_subqueries.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-08/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
SELECT c.customer_id, c.full_name,
  (
    SELECT ROUND(COALESCE(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),0),2)
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id = c.customer_id
  ) AS lifetime_revenue
FROM customers c
ORDER BY lifetime_revenue DESC, c.customer_id
LIMIT 20;

-- Inline subquery in FROM
SELECT x.category, ROUND(AVG(x.order_total),2) AS avg_order_total
FROM (
  SELECT p.category, o.order_id, SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, o.order_id
) x
GROUP BY x.category
ORDER BY avg_order_total DESC, x.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return orders whose total exceeds the overall average order total.
--    Hint: The aggregate subquery is guaranteed to return exactly one value.
--    Inputs: For sql-08 Exercise 1, read from `orders`. Build the answer toward `order_id`, `customer_id`, and `total_amount`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-08 Exercise 1, expected output: Order rows above the global average. The final columns are `order_id`, `customer_id`, and `total_amount`. The final order is `o.total_amount DESC, o.order_id`.
--    Verify: For sql-08 Exercise 1, run an anti-check that counts rows where NOT ((o.total_amount > ( SELECT AVG(all_orders.total_amount) FROM orders AS all_orders ))); require unique `order_id` where the expected grain is one row per key and confirm the projected `order_id`, `customer_id`, and `total_amount` against `orders`. Add one row for which `(o.total_amount > ( SELECT AVG(all_orders.total_amount) FROM orders AS all_orders ))` is true and one for which it is false; verify only the matching `order_id` value is returned.
--    Hint ladder, rung 1: For sql-08 Exercise 1, inspect the source keys that survive `WHERE`; then check `o.total_amount DESC, o.order_id` before applying the row cap.
-- 2. [Query writing] Add the total customer count as a scalar column beside each country-level customer count.
--    Hint: An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.
--    Inputs: For sql-08 Exercise 2, read from `customers`. Build the answer toward `country`, `country_customers`, and `all_customers`; keep `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-08 Exercise 2, expected output: One row per country with a common global total. The final columns are `country`, `country_customers`, and `all_customers`. The final order is `country_customers DESC, c.country`.
--    Verify: For sql-08 Exercise 2, independently aggregate `customers` by `country`; require one output row for every distinct `country` tuple and compare `country_customers`, and `all_customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `country_customers`, and `all_customers` for the existing `country` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-08 Exercise 2, confirm the groups are `country`; then check `country_customers DESC, c.country` before applying the row cap.
-- 3. [Query writing] Show each customer with their latest order timestamp using a scalar correlated subquery.
--    Hint: Use `MAX` to guarantee one result and let customers without orders receive NULL.
--    Inputs: For sql-08 Exercise 3, read from `orders`, and `customers`. Build the answer toward `customer_id`, `full_name`, and `latest_order_date`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-08 Exercise 3, expected output: One row per customer. The final columns are `customer_id`, `full_name`, and `latest_order_date`. The final order is `latest_order_date DESC NULLS LAST, c.customer_id`.
--    Verify: For sql-08 Exercise 3, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `customer_id`, `full_name`, and `latest_order_date` against `orders`, and `customers`. Tie two rows on `latest_order_date DESC NULLS LAST` and give them different `c.customer_id` values; verify `latest_order_date DESC NULLS LAST, c.customer_id` chooses a stable first/last row.
--    Hint ladder, rung 1: For sql-08 Exercise 3, inspect the source keys that survive `WHERE`; then check `latest_order_date DESC NULLS LAST, c.customer_id` before applying the row cap.
-- 4. [Prediction] Demonstrate that a scalar subquery with no matching rows returns NULL.
--    Hint: Use a deliberately impossible product key and test the scalar result with `IS NULL`.
--    Inputs: For sql-08 Exercise 4, read from `products`. Compute `no_row_becomes_null` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-08 Exercise 4, expected output: One row whose boolean result is true. The final columns are `no_row_becomes_null`.
--    Verify: For sql-08 Exercise 4, evaluate each of `no_row_becomes_null` in a separate control `SELECT` over `products`; require one final row and compare every value. Repeat with `NULL` in `no_row_becomes_null` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-08 Exercise 4, inspect the source keys that survive `WHERE`.
-- 5. [Debugging] Repair a scalar subquery that returns many product prices by aggregating to the intended single value.
--    Hint: Choose the business reduction explicitly; this answer uses maximum price.
--    Inputs: For sql-08 Exercise 5, read from `products`. Build the answer toward `category`, `category_max_price`, and `global_max_price`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-08 Exercise 5, expected output: One row per category with a scalar global maximum for comparison. The final columns are `category`, `category_max_price`, and `global_max_price`. The final order is `p.category`.
--    Verify: For sql-08 Exercise 5, independently aggregate `products` by `category`; require one output row for every distinct `category` tuple and compare `category_max_price`, and `global_max_price` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `category_max_price`, and `global_max_price` for the existing `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-08 Exercise 5, confirm the groups are `category`; then check `p.category` before applying the row cap.
-- 6. [Extension] Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report.
--    Hint: Compute the global total once, then cross join the guaranteed one-row relation.
--    Inputs: For sql-08 Exercise 6, read from `customers`. Build the answer toward `country`, `country_customers`, and `customer_share`; keep `country`, and `customer_count` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-08 Exercise 6, expected output: One row per country with country share. The final columns are `country`, `country_customers`, and `customer_share`. The final order is `customer_share DESC, c.country`.
--    Verify: For sql-08 Exercise 6, independently aggregate `customers` by `country`, and `customer_count`; require one output row for every distinct `country`, and `customer_count` tuple and compare `country_customers`, and `customer_share` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `country_customers`, and `customer_share` for the existing `country`, and `customer_count` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-08 Exercise 6, run `global` one at a time. Record each CTE's row count and `country`, and `customer_count` uniqueness before the next stage uses it.

ROLLBACK;
