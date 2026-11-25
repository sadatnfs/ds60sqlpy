-- Day 23: CTEs Introduction
-- BEGINNER WORKFLOW - sql-23: Common Table Expressions
-- Guide: sql/postgres-60day/companion-guides/day23_ctes_intro.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-23.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use CTEs to name grains and decisions in a multi-stage query, while understanding that readability, not forced materialization, is the default goal.
-- Assumptions: Each CTE declares its output grain. PostgreSQL inlines a side-effect-free CTE that is referenced once unless `MATERIALIZED` is requested; a CTE referenced more than once is materialized (computed once) by default.
-- Pitfall: A CTE does not automatically improve performance; duplicated rows or ambiguous names remain logical bugs even when split into stages.
-- Predict row grain and NULL/order behavior before executing each example.
-- Rewrite subqueries as CTEs
WITH order_lines AS (
  SELECT
    o.order_id,
    o.customer_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_total
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.order_id,
    o.customer_id
),
top_customers AS (
  SELECT
    customer_id,
    SUM(order_total) AS lifetime_revenue
  FROM
    order_lines
  GROUP BY
    customer_id
)
SELECT
  tc.customer_id,
  tc.lifetime_revenue
FROM
  top_customers tc
ORDER BY
  lifetime_revenue DESC,
  tc.customer_id
LIMIT 20;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Build order-level net value in one CTE and summarize it by customer in the outer query.
--    Hint: Name the one-row-per-order grain before changing to customer grain.
--    Inputs: For sql-23 Exercise 1, read `orders` joined to `order_items`, build the `order_values` CTE at one row per `order_id` with net value `unit_price * quantity * (1 - discount)`, then group that CTE by `customer_id`; `order_id` disappears in the outer aggregate.
--    Expected result/shape: For sql-23 Exercise 1, expected output: 438 rows, one per ordering customer, led by customer 181 with 16 orders and 9502.22 of item-level net revenue. The final columns are `customer_id`, `order_count`, and `net_revenue`. The final order is `net_revenue DESC, ov.customer_id`.
--    Verify: For sql-23 Exercise 1, confirm `SUM(order_count)` is 4362 and matches `SELECT COUNT(*) FROM orders`, and that the unrounded revenue total equals `SELECT ROUND(SUM(unit_price * quantity * (1 - discount)), 2) FROM order_items` (2355647.12); then count joined rows for customer 181 without the CTE, `SELECT COUNT(*) FROM orders o JOIN order_items oi USING (order_id) WHERE o.customer_id = 181`, and see 50 item rows instead of 16 orders, which is the fanout the order-grain CTE prevents.
--    Hint ladder, rung 1: For sql-23 Exercise 1, run `order_values` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
-- 2. [Query writing] Use one category-revenue CTE twice to return the highest category and total revenue.
--    Hint: A named aggregate can support multiple scalar reads without repeating the business formula.
--    Inputs: For sql-23 Exercise 2, read `order_items` joined to `products`, aggregate net item revenue by `category` once in `category_revenue`, and read that CTE twice: once in a scalar subquery ordered by revenue then category with `LIMIT 1`, and once in a scalar `SUM`; there is no outer `FROM` or `GROUP BY`.
--    Expected result/shape: For sql-23 Exercise 2, expected output: exactly one row, `top_category` `Sports` and `all_revenue` 2355647.12. The final columns are `top_category`, and `all_revenue`.
--    Verify: For sql-23 Exercise 2, run the CTE body alone and confirm six category rows led by Sports at 397427.70 ahead of Electronics at 394424.39, and that they add to the same 2355647.12 as `SELECT ROUND(SUM(unit_price * quantity * (1 - discount)), 2) FROM order_items`; then add `WHERE false` inside `category_revenue` and confirm the query still returns one row, now with both values NULL, because scalar subqueries over an empty CTE yield NULL rather than no row.
--    Hint ladder, rung 1: For sql-23 Exercise 2, run `category_revenue` one at a time. Record each CTE's row count and `order_item_id` uniqueness before the next stage uses it.
-- 3. [Query writing] Create staged payment reconciliation CTEs at order grain.
--    Hint: Aggregate payment detail before joining to orders and preserve unpaid orders with a left join.
--    Inputs: For sql-23 Exercise 3, read `payments` (3836 rows for 3489 orders) and pre-aggregate them to one `paid_amount` per `order_id` in `paid`, then `LEFT JOIN` that CTE to all 4362 `orders` in `reconciled` and turn a missing payment into 0 with `COALESCE`.
--    Expected result/shape: For sql-23 Exercise 3, expected output: 4362 rows, one per order; 873 orders have no payment, 199 more are partly paid, none is overpaid, and the first rows are orders 2029, 3129, and 3679 each with 1432.49 unpaid. The final columns are `order_id`, `order_total`, `paid_amount`, and `unpaid_balance`. The final order is `ABS(total_amount - paid_amount) DESC, order_id`.
--    Verify: For sql-23 Exercise 3, confirm the row count equals `SELECT COUNT(*) FROM orders` (4362), that `SUM(paid_amount)` equals `SELECT SUM(amount) FROM payments` (1831900.81), and that the 873 zero-paid rows are exactly the `placed` orders; then join `payments` to `orders` without the `paid` CTE and see 4709 rows, because 347 orders have more than one payment.
--    Hint ladder, rung 1: For sql-23 Exercise 3, run `paid`, and `reconciled` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 4. [Prediction] Compare `MATERIALIZED` and `NOT MATERIALIZED` syntax on a side-effect-free filtered order CTE without claiming one is universally faster.
--    Hint: Both return the same rows; planning effects require `EXPLAIN` evidence in a representative environment.
--    Inputs: For sql-23 Exercise 4, read from `orders` through two side-effect-free CTEs that both keep `delivered` orders, one declared `AS MATERIALIZED` and one `AS NOT MATERIALIZED`, and count the rows each returns.
--    Expected result/shape: For sql-23 Exercise 4, expected output: two rows, `materialized` and `not_materialized`, each with `row_count` 872. The final columns are `variant`, and `row_count`. The final order is `variant`.
--    Verify: For sql-23 Exercise 4, confirm both `row_count` values are 872, equal to `SELECT COUNT(*) FROM orders WHERE status = 'delivered'`; then run `EXPLAIN` on the query: the `MATERIALIZED` CTE appears as a separate `CTE materialized_orders` step read through a `CTE Scan`, while the `NOT MATERIALIZED` CTE is folded into a `Seq Scan on orders` with the status filter.
--    Hint ladder, rung 1: For sql-23 Exercise 4, run each CTE's `SELECT` alone and compare the counts before you compare plans.
-- 5. [Debugging] Repair a multi-stage query whose repeated `total` column names are ambiguous by assigning grain-specific aliases.
--    Hint: Name measures `order_value`, `customer_revenue`, and similar rather than carrying generic `total`.
--    Inputs: For sql-23 Exercise 5, read `orders` and `order_items` into the order-grain CTE `order_values`, roll it up to one `customer_revenue` per customer, and only then join `customers` and group by `country`, giving each stage its own alias instead of a reused `total`.
--    Expected result/shape: For sql-23 Exercise 5, expected output: 7 rows, one per country with orders, from FR at 343290.13 down to IN at 329081.73; BR's 62 customers place no orders, so BR is absent. The final columns are `country`, and `country_revenue`. The final order is `country_revenue DESC, c.country`.
--    Verify: For sql-23 Exercise 5, confirm the seven values add to the item-level total `SELECT ROUND(SUM(unit_price * quantity * (1 - discount)), 2) FROM order_items` (2355647.12) within one cent of rounding, and that `SELECT country, COUNT(*) FROM customers GROUP BY country` lists eight countries; change the final join to `customers LEFT JOIN customer_revenue` and BR appears with a NULL revenue, which shows why the inner join drops it.
--    Hint ladder, rung 1: For sql-23 Exercise 5, run `order_values`, and `customer_revenue` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
-- 6. [Extension] Use a data-modifying CTE to demonstrate an update and inspect its returned rows without persistence.
--    Hint: The outer lesson transaction rolls back; the CTE exposes changed rows as a relation.
--    Inputs: For sql-23 Exercise 6, read `products` in the `candidates` CTE to pick the three lowest `product_id` values (1, 2, 3, priced 10.37, 10.74, and 11.11), update only those rows in the data-modifying CTE `updated`, and read its `RETURNING` rows; `SAVEPOINT exercise_6` and `ROLLBACK TO SAVEPOINT` undo the change.
--    Expected result/shape: For sql-23 Exercise 6, expected output: one summary row with `updated_rows` 3, `first_updated_product` 1, and `last_updated_product` 3. The final columns are `updated_rows`, `first_updated_product`, and `last_updated_product`.
--    Verify: For sql-23 Exercise 6, add `string_agg(price::text, ',' ORDER BY product_id)` to the outer query and confirm the returned new prices are 10.47, 10.85, and 11.22; after `ROLLBACK TO SAVEPOINT exercise_6`, `SELECT product_id, price FROM products WHERE product_id <= 3` must show 10.37, 10.74, and 11.11 again. With `LIMIT 0` in `candidates` the summary row still appears, with 0 updated rows and NULL first and last products.
--    Hint ladder, rung 1: For sql-23 Exercise 6, run `candidates`, and `updated` one at a time. Record each CTE's row count and `product_id` uniqueness before the next stage uses it.
ROLLBACK;
