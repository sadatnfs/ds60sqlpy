-- Day 7: Week 1 Mini-Project
-- BEGINNER WORKFLOW - sql-07: Week 1 Project
-- Guide: sql/postgres-60day/companion-guides/day07_week1_project.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-07.
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
  SELECT
    *
  FROM
    orders
  WHERE
    order_date >= now() - interval '90 days'
),
line AS (
  SELECT
    ro.order_id,
    ro.customer_id,
    c.country,
    p.category,
    (oi.unit_price * oi.quantity * (1 - oi.discount)) AS line_revenue
FROM
  recent_orders ro
  JOIN customers c ON c.customer_id = ro.customer_id
  JOIN order_items oi ON oi.order_id = ro.order_id
  JOIN products p ON p.product_id = oi.product_id
)
SELECT
  country,
  category,
  ROUND(SUM(line_revenue), 2) AS revenue,
  COUNT(DISTINCT customer_id) AS buyers,
  ROUND(SUM(line_revenue) / NULLIF (COUNT(DISTINCT customer_id), 0), 2) AS rev_per_buyer
FROM
  line
GROUP BY
  country,
  category
ORDER BY
  revenue DESC,
  country,
  category
LIMIT 50;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Build an order KPI table by status with order count, revenue, average order value, and distinct customers.
--    Hint: Aggregate orders at status grain and round only displayed monetary values.
--    Inputs: For sql-07 Exercise 1, group the 4,362 `orders` rows by `status`; there are five statuses, `placed` and `shipped` with 873 orders each and `delivered`, `paid`, and `returned` with 872 each.
--    Expected result/shape: For sql-07 Exercise 1, return 5 rows, one per status, led by `paid` with 872 orders, 432 customers, and 478068.36 revenue, and ending with `returned` at 468083.26. The final columns are `status`, `order_count`, `customer_count`, `revenue`, and `average_order_value`. The final order is `revenue DESC, o.status`.
--    Verify: For sql-07 Exercise 1, confirm the five `order_count` values sum to 4362 and the five `revenue` values sum to 2355646.89, the same as `SELECT ROUND(SUM(total_amount), 2) FROM orders`. Inside a rolled-back transaction, set order 21's status to `cancelled`; the result must grow to 6 rows, with `cancelled` showing 1 order and `paid` dropping to 871.
--    Hint ladder, rung 1: For sql-07 Exercise 1, confirm the groups are `status`; then check `revenue DESC, o.status` before applying the row cap.
-- 2. [Query writing] Return the 20 products with the highest net line revenue.
--    Hint: Aggregate order items by product before ranking; use product ID as tie-breaker.
--    Inputs: For sql-07 Exercise 2, join the 13,085 `order_items` rows to `products`, sum `unit_price * quantity * (1 - discount)` per product across the 275 products that have sold, and keep the top 20.
--    Expected result/shape: For sql-07 Exercise 2, return 20 rows, one per product, from product 271 (Apparel, 17643.20) down to product 260 (Electronics, 15292.80). The final columns are `product_id`, `name`, `category`, and `net_revenue`. The final order is `net_revenue DESC, p.product_id`.
--    Verify: For sql-07 Exercise 2, confirm 20 distinct `product_id` values with `net_revenue` never rising from one row to the next. Rerun with `LIMIT 21`; the only added row must be product 231 at 15275.20, which is below product 260, so the cutoff falls between two different values rather than inside a tie.
--    Hint ladder, rung 1: For sql-07 Exercise 2, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id`, `name`, and `category` so the exact fanout or loss is visible.
-- 3. [Query writing] Create a customer summary that retains customers with no orders.
--    Hint: Left join from customers and count/order-sum nullable matches with `COALESCE` only where zero has clear meaning.
--    Inputs: For sql-07 Exercise 3, `LEFT JOIN` the 500 `customers` rows to `orders`, count `o.order_id` and sum `total_amount` per customer, and turn a missing sum into 0 with `COALESCE`.
--    Expected result/shape: For sql-07 Exercise 3, return 500 rows, one per customer, led by customer 181 (FR, 16 orders, 9502.21); the 62 customers without orders sort last with 0 orders and a 0 total. The final columns are `customer_id`, `full_name`, `country`, `order_count`, and `stored_order_total`. The final order is `stored_order_total DESC, c.customer_id`.
--    Verify: For sql-07 Exercise 3, confirm the `order_count` column sums to 4362, `stored_order_total` sums to 2355646.89, and exactly 62 rows show 0 orders. An inner join must return only 438 rows, and counting `*` instead of `o.order_id` must wrongly give those 62 customers an `order_count` of 1.
--    Hint ladder, rung 1: For sql-07 Exercise 3, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, `full_name`, and `country` so the exact fanout or loss is visible.
-- 4. [Debugging] Reconcile stored order totals, computed line totals, and payments without multiplying item and payment rows.
--    Hint: Aggregate each detail table to order grain first, then join the one-row-per-order relations.
--    Inputs: For sql-07 Exercise 4, pre-aggregate `order_items` to one `line_total` per order and `payments` to one `paid_total` per order, then join both to the 4,362 `orders` rows, with `LEFT JOIN` for payments because 873 orders have none.
--    Expected result/shape: For sql-07 Exercise 4, return 4,362 rows, one per order; every `storage_difference` rounds to 0.00 (the largest raw gap is 0.0045), while 1,072 rows have a nonzero `unpaid_balance` of up to 1432.49. The final columns are `order_id`, `status`, `stored_total`, `line_total`, `storage_difference`, `paid_total`, and `unpaid_balance`. The final order is `ABS(o.total_amount - it.line_total) DESC, o.order_id`.
--    Verify: For sql-07 Exercise 4, confirm 4,362 distinct `order_id` values and that the 1,072 nonzero balances split into 873 orders with `paid_total` 0.00 and 199 paid orders whose payments differ from `total_amount`. Joining raw `order_items` and `payments` to `orders` without pre-aggregation returns 13,432 rows and inflates the summed `total_amount` to 8673949.32.
--    Hint ladder, rung 1: For sql-07 Exercise 4, run `item_totals`, and `payment_totals` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. [Prediction] Build a monthly order trend and explain which months are absent rather than zero.
--    Hint: Grouping observed orders alone cannot create empty calendar months.
--    Inputs: For sql-07 Exercise 5, read from `orders`, group by `date_trunc('month', order_date)`, and return each month's `order_count` and `stored_revenue` (`SUM(total_amount)` rounded to 2 places).
--    Expected result/shape: For sql-07 Exercise 5, return 46 rows, one per calendar month with orders, from 2023-02-01 with 2 orders to the current month, which has 151 orders on a freshly loaded fixture. The final columns are `order_month`, `order_count`, and `stored_revenue`. The final order is `order_month`.
--    Verify: For sql-07 Exercise 5, confirm that `order_month` is unique, that `SUM(order_count)` equals `SELECT COUNT(*) FROM orders` (4362), and that the monthly `stored_revenue` values add up to `SELECT ROUND(SUM(total_amount), 2) FROM orders` (2355646.89).
--    Hint ladder, rung 1: For sql-07 Exercise 5, group by the same `date_trunc('month', order_date)` expression you select; grouping by `order_id` would return one row per order.
-- 6. [Extension] Create a compact one-row audit of customer, order, item, and payment coverage.
--    Hint: Use scalar subqueries for independent counts; this avoids accidental cross multiplication.
--    Inputs: For sql-07 Exercise 6, read from `customers`, `orders`, `order_items`, and `payments`. Compute `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-07 Exercise 6, return one row: 500 customer rows, 4,362 order rows, 13,085 order item rows, 3,836 payment rows, and 62 customers without orders. The final columns are `customer_rows`, `order_rows`, `order_item_rows`, `payment_rows`, and `customers_without_orders`.
--    Verify: For sql-07 Exercise 6, confirm each value equals its own standalone `COUNT(*)`, and that 62 matches Exercise 3's count of zero-order customers. Inside a rolled-back transaction, insert one customer with no orders; the result must stay one row, with `customer_rows` at 501 and `customers_without_orders` at 63.
--    Hint ladder, rung 1: For sql-07 Exercise 6, inspect the source keys that survive `WHERE`.
ROLLBACK;
