-- Day 7: Week 1 Mini-Project
-- BEGINNER WORKFLOW — sql-07: Week1 Project
-- Guide: sql/postgres-60day/companion-guides/day07_week1_project.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-07/ copy, and prints the full
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
-- Build a comprehensive report combining joins, aggregates, set ops
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Integrate foundational SELECT, aggregation, joins, NULL handling, and set reasoning into reconciled business outputs.
-- Assumptions: Revenue means exact net line revenue unless a prompt explicitly asks for stored order totals. Every ranked output has a deterministic tie-breaker.
-- Pitfall: A polished result is not trustworthy until its grain, denominator, missing-row policy, and reconciliation are explicit.
-- Predict row grain and NULL/order behavior before executing each example.

-- Customer revenue by country and category (last 90 days)
WITH recent_orders AS (
  SELECT * FROM orders WHERE order_date >= now() - interval '90 days'
), line AS (
  SELECT ro.order_id, ro.customer_id, c.country, p.category,
         (oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_revenue
  FROM recent_orders ro
  JOIN customers c ON c.customer_id = ro.customer_id
  JOIN order_items oi ON oi.order_id = ro.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT country, category,
       ROUND(SUM(line_revenue),2) AS revenue,
       COUNT(DISTINCT customer_id) AS buyers,
       ROUND(SUM(line_revenue)/NULLIF(COUNT(DISTINCT customer_id),0),2) AS rev_per_buyer
FROM line
GROUP BY country, category
ORDER BY revenue DESC, country, category
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Build an order KPI table by status with order count, revenue, average order value, and distinct customers.
--    Hint: Aggregate orders at status grain and round only displayed monetary values.
--    Inputs: For sql-07 Exercise 1, read from `orders`. Build the answer toward `status`, `order_count`, `customer_count`, `revenue`, and `average_order_value`; keep `status` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-07 Exercise 1, expected output: One row per order status. The final columns are `status`, `order_count`, `customer_count`, `revenue`, and `average_order_value`. The final order is `revenue DESC, o.status`.
--    Verify: For sql-07 Exercise 1, independently aggregate `orders` by `status`; require one output row for every distinct `status` tuple and compare `order_count`, `customer_count`, `revenue`, and `average_order_value` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, `customer_count`, and `revenue` for the existing `status` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-07 Exercise 1, confirm the groups are `status`; then check `revenue DESC, o.status` before applying the row cap.
-- 2. [Query writing] Return the 20 products with the highest net line revenue.
--    Hint: Aggregate order items by product before ranking; use product ID as tie-breaker.
--    Inputs: For sql-07 Exercise 2, read from `products`, and `order_items`. Build the answer toward `product_id`, `name`, `category`, and `net_revenue`; keep `product_id`, `name`, and `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-07 Exercise 2, expected output: At most 20 product rows. The final columns are `product_id`, `name`, `category`, and `net_revenue`. The final order is `net_revenue DESC, p.product_id`.
--    Verify: For sql-07 Exercise 2, assert no more than 20 rows, no duplicate `product_id`, `name`, and `category`, and no adjacent pair that violates `net_revenue DESC, p.product_id`. Rejoin the returned keys to `products`, and `order_items` to confirm `product_id`, `name`, `category`, and `net_revenue` came from the same source rows. Run with 20 minus one and 20 plus one eligible rows; require the output cap of 20 while retaining `net_revenue DESC, p.product_id`.
--    Hint ladder, rung 1: For sql-07 Exercise 2, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id`, `name`, and `category` so the exact fanout or loss is visible.
-- 3. [Query writing] Create a customer summary that retains customers with no orders.
--    Hint: Left join from customers and count/order-sum nullable matches with `COALESCE` only where zero has clear meaning.
--    Inputs: For sql-07 Exercise 3, read from `customers`, and `orders`. Build the answer toward `customer_id`, `full_name`, `country`, `order_count`, and `stored_order_total`; keep `customer_id`, `full_name`, and `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-07 Exercise 3, expected output: One row per customer. The final columns are `customer_id`, `full_name`, `country`, `order_count`, and `stored_order_total`. The final order is `stored_order_total DESC, c.customer_id`.
--    Verify: For sql-07 Exercise 3, independently aggregate `customers`, and `orders` by `customer_id`, `full_name`, and `country`; require one output row for every distinct `customer_id`, `full_name`, and `country` tuple and compare `order_count`, and `stored_order_total` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `stored_order_total` for the existing `customer_id`, and `full_name` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-07 Exercise 3, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, `full_name`, and `country` so the exact fanout or loss is visible.
-- 4. [Debugging] Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows.
--    Hint: Aggregate each detail table to order grain first, then join the one-row-per-order relations.
--    Inputs: For sql-07 Exercise 4, read from `order_items`, `payments`, and `orders`. Build the answer toward `order_id`, `status`, `stored_total`, `line_total`, `storage_difference`, `paid_total`, and `unpaid_balance`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-07 Exercise 4, expected output: One row per order with signed differences. The final columns are `order_id`, `status`, `stored_total`, `line_total`, `storage_difference`, `paid_total`, and `unpaid_balance`. The final order is `ABS(o.total_amount - it.line_total) DESC, o.order_id`.
--    Verify: For sql-07 Exercise 4, project `order_id` plus the raw source columns from `order_items`, `payments`, and `orders` at each join stage; record row count and distinct `order_id`, then assert the final `order_id`, `status`, `stored_total`, `line_total`, `storage_difference`, `paid_total`, and `unpaid_balance` values match those staged rows without unintended fanout or loss. Add one source row with a new `order_id`; verify the result gains exactly one row carrying that `order_id` value.
--    Hint ladder, rung 1: For sql-07 Exercise 4, run `item_totals`, and `payment_totals` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. [Prediction] Build a monthly order trend and explain which months are absent rather than zero.
--    Hint: Grouping observed orders alone cannot create empty calendar months.
--    Inputs: For sql-07 Exercise 5, read from `orders`. Build the answer toward `order_month`, `order_count`, and `stored_revenue`; keep `order_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-07 Exercise 5, expected output: One row per observed order month. The final columns are `order_month`, `order_count`, and `stored_revenue`. The final order is `order_month`.
--    Verify: For sql-07 Exercise 5, independently aggregate `orders` by `order_id`; require one output row for every distinct `order_id` tuple and compare `order_month`, `order_count`, and `stored_revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_month`, `order_count`, and `stored_revenue` for the existing `order_id` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-07 Exercise 5, confirm the groups are `order_id`; then check `order_month` before applying the row cap.
-- 6. [Extension] Create a compact one-row audit of customer, order, item, and payment coverage.
--    Hint: Use scalar subqueries for independent counts; this avoids accidental cross multiplication.
--    Inputs: For sql-07 Exercise 6, read from `customers`, `orders`, `order_items`, and `payments`. Compute `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-07 Exercise 6, expected output: Exactly one audit row. The final columns are `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders`.
--    Verify: For sql-07 Exercise 6, evaluate each of `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders` in a separate control `SELECT` over `customers`, `orders`, `order_items`, and `payments`; require one final row and compare every value. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
--    Hint ladder, rung 1: For sql-07 Exercise 6, inspect the source keys that survive `WHERE`.

ROLLBACK;
