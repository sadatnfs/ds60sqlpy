-- Day 41: Complex Aggregations (FILTER, conditional metrics, string aggregation)
-- BEGINNER WORKFLOW — sql-41: Complex Aggregations
-- Guide: sql/postgres-60day/companion-guides/day41_complex_aggregations.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-41/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: order_items, products, orders, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Multiple metrics with FILTER
SELECT p.category,
       SUM(oi.quantity)                                                   AS total_qty,
       SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '30 days') AS qty_30d,
       SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '90 days') AS qty_90d,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)),2)           AS revenue,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount))
             FILTER (WHERE o.order_date >= now() - interval '30 days'),2) AS revenue_30d
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o   ON o.order_id = oi.order_id
GROUP BY p.category
ORDER BY revenue DESC;

-- Conditional aggregation using CASE for multi-metric report
SELECT c.country,
       SUM(CASE WHEN o.status IN ('paid','shipped','delivered') THEN 1 ELSE 0 END) AS successful_orders,
       SUM(CASE WHEN o.status = 'returned' THEN 1 ELSE 0 END)                      AS returned_orders,
       ROUND(SUM(CASE WHEN o.status <> 'returned' THEN o.total_amount ELSE 0 END),2) AS net_revenue
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY net_revenue DESC;

-- String aggregation for labels
SELECT p.category,
       string_agg(DISTINCT p.name, ', ' ORDER BY p.name) AS sample_products
FROM products p
GROUP BY p.category
ORDER BY p.category
LIMIT 10;

-- Exercises
-- 1. Build a 6-metric dashboard by category using FILTER for various time windows.
--    Inputs: For sql-41 Exercise 1, read from `orders`, `order_items`, `products`, and `training.products`. Build the answer toward `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-41 Exercise 1, expected output: one row for each category in `training.products`, with six metric columns. The final columns are `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d`. The final order is `revenue_30d DESC NULLS LAST, category`.
--    Verify: For sql-41 Exercise 1, independently aggregate `orders`, `order_items`, `products`, and `training.products` by `category`; require one output row for every distinct `category` tuple and compare `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue_30d`, `revenue_90d`, and `orders_30d` for the existing `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-41 Exercise 1, run `lines` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 2. Create a per-country string_agg of top 5 product names by revenue.
--    Inputs: For sql-41 Exercise 2, read from `customers`, `orders`, `order_items`, and `products`. Build the answer toward `country`, and `top_five_products`; keep `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-41 Exercise 2, expected output: one row per represented country and one comma-separated label ordered from highest to lowest product revenue. The final columns are `country`, and `top_five_products`. The final order is `country`.
--    Verify: For sql-41 Exercise 2, independently aggregate `customers`, `orders`, `order_items`, and `products` by `country`; require one output row for every distinct `country` tuple satisfying `(product_rank <= 5)` and compare `top_five_products` tuple by tuple. Give two rows the same `country` value and different ``country`` values; verify `country` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-41 Exercise 2, run `product_revenue`, and `ranked` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
-- 3. Prediction: compare GROUPING SETS ((country), (category), ()) with CUBE
--    (country, category). Predict which country/category detail level is absent.
--    Inputs: For sql-41 Exercise 3, read from `orders`, `customers`, `order_items`, and `products`. Build the answer toward `country`, `category`, `revenue`, and `grouping_mask`; keep `country`, and `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-41 Exercise 3, expected output: one row per `country`, and `category`. The final columns are `country`, `category`, `revenue`, and `grouping_mask`. The final order is `grouping_mask, country, category`.
--    Verify: For sql-41 Exercise 3, independently aggregate `orders`, `customers`, `order_items`, and `products` by `country`, and `category`; require one output row for every distinct `country`, and `category` tuple and compare `revenue` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue` for the existing `country`, and `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-41 Exercise 3, run `lines` one at a time. Record each CTE's row count and `country`, and `category` uniqueness before the next stage uses it.
-- 4. Construction: report order count, paid revenue, returned revenue, and
--    distinct customers per country using FILTER.
--    Inputs: For sql-41 Exercise 4, read from `orders`, and `customers`. Build the answer toward `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers`; keep `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-41 Exercise 4, expected output: one row per `country`. The final columns are `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers`. The final order is `c.country`.
--    Verify: For sql-41 Exercise 4, independently aggregate `orders`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `orders`, `paid_orders`, and `paid_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-41 Exercise 4, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
-- 5. Debugging: distinguish a real NULL country from a subtotal NULL by adding
--    GROUPING(country) and a safe display label.
--    Inputs: For sql-41 Exercise 5, read from `customers`. Build the answer toward `country_label`, `is_subtotal`, and `customers`; keep `country_label`, and `is_subtotal` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-41 Exercise 5, expected output: one row per `country_label`, and `is_subtotal`. The final columns are `country_label`, `is_subtotal`, and `customers`. The final order is `is_subtotal, country_label`.
--    Verify: For sql-41 Exercise 5, independently aggregate `customers` by `country_label`, and `is_subtotal`; require one output row for every distinct `country_label`, and `is_subtotal` tuple and compare `customers` tuple by tuple. Repeat with `NULL` in `GROUPING` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-41 Exercise 5, confirm the groups are `country_label`, and `is_subtotal`; then check `is_subtotal, country_label` before applying the row cap.
-- 6. Edge case: return an empty array rather than NULL when an aggregate input
--    set is empty, and explain the COALESCE type cast.
--    Inputs: For sql-41 Exercise 6, read from `customers`. Build the answer toward `empty_email_array`; keep `customer_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-41 Exercise 6, expected output: one row per `customer_id`. The final columns are `empty_email_array`.
--    Verify: For sql-41 Exercise 6, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `empty_email_array` against `customers`. Repeat with `NULL` in `empty_email_array` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-41 Exercise 6, inspect the source keys that survive `WHERE`.

ROLLBACK;
