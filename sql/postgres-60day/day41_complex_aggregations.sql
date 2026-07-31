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

-- CUBE / GROUPING reading key
-- CUBE(country, category) expands to four grouping sets:
--   (country, category) -> detail
--   (country)           -> country subtotal
--   (category)          -> category subtotal
--   ()                  -> grand total
-- GROUPING(country, category) encodes those levels as 0, 1, 2, and 3.
-- The rightmost argument is the least-significant bit. A stored NULL in a
-- grouped column still has bit 0; only omission by a grouping set produces 1.

-- Exercises
-- 1. Build a 6-metric dashboard by category using FILTER for various time windows.
--    Inputs: For sql-41 Exercise 1, read from `orders`, `order_items`, `products`, and `training.products`. Build the answer toward `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-41 Exercise 1, expected output: one row for each category in `training.products`, with six metric columns. The final columns are `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d`. The final order is `revenue_30d DESC NULLS LAST, category`.
--    Verify: For sql-41 Exercise 1, independently aggregate `orders`, `order_items`, `products`, and `training.products` by `category`; require one output row for every distinct `category` tuple and compare `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `revenue_30d`, `revenue_90d`, and `orders_30d` for the existing `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-41 Exercise 1, run `lines` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 2. Create a per-country string_agg of top 5 product names by revenue.
--    Inputs: For sql-41 Exercise 2, read from `customers`, `orders`, `order_items`, and `products`. First aggregate at (`country`, `product_id`, `name`) grain, then rank products within each country; build the answer toward `country` and `top_five_products`.
--    Expected result/shape: For sql-41 Exercise 2, expected output: one row per represented country. `top_five_products` contains at most five product names ordered by `revenue DESC, product_id`; `product_id` is the deterministic tie-breaker. The final columns are `country` and `top_five_products`. The final order is `country`.
--    Verify: For sql-41 Exercise 2, independently aggregate line revenue at (`country`, `product_id`, `name`) grain and rank with `ROW_NUMBER() OVER (PARTITION BY country ORDER BY revenue DESC, product_id)`. For every country, compare the ordered products used by `string_agg`, require no more than five ranked products, and confirm a country with fewer than five products is not padded.
--    Hint ladder, rung 1: For sql-41 Exercise 2, run `product_revenue`, and `ranked` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
-- 3. Prediction: compare GROUPING SETS ((country), (category), ()) with CUBE
--    (country, category). Predict which country/category detail level is absent.
--    Inputs: For sql-41 Exercise 3, calculate line revenue from `orders`, `customers`, `order_items`, and `products`, then aggregate with `CUBE(country, category)`. Build the answer toward `country`, `category`, `revenue`, `grouping_mask`, and `grouping_level`.
--    Expected result/shape: For sql-41 Exercise 3, expected output: every grouping level emitted by the two-dimensional cube. `grouping_mask` is `0` for detail, `1` for a country subtotal, `2` for a category subtotal, and `3` for the grand total. The final columns are `country`, `category`, `revenue`, `grouping_mask`, and `grouping_level`. The final order is `grouping_mask, country, category`.
--    Verify: For sql-41 Exercise 3, compare mask `0` with an independent (`country`, `category`) aggregate, mask `1` with a country aggregate, and mask `2` with a category aggregate; require exactly one mask `3` row. Within each mask, the sum of `revenue` must equal the independent all-lines revenue total.
--    Hint ladder, rung 1: For sql-41 Exercise 3, run `lines` one at a time. Record each CTE's row count and `country`, and `category` uniqueness before the next stage uses it.
-- 4. Construction: report order count, paid revenue, returned revenue, and
--    distinct customers per country using FILTER.
--    Inputs: For sql-41 Exercise 4, read from `orders`, and `customers`. Build the answer toward `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers`; keep `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-41 Exercise 4, expected output: one row per `country`. The final columns are `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers`. The final order is `c.country`.
--    Verify: For sql-41 Exercise 4, independently aggregate `orders`, and `customers` by `country`; require one output row for every distinct `country` tuple and compare `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `orders`, `paid_orders`, and `paid_revenue` for the existing `country` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-41 Exercise 4, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
-- 5. Debugging: distinguish a real NULL country from a subtotal NULL by adding
--    GROUPING(country) and a safe display label.
--    Inputs: For sql-41 Exercise 5, read `customers.country` and append one controlled `NULL::text` input row in a `country_input` CTE. Apply `GROUPING(country)` to the grouped expression and build `country_label`, `is_subtotal`, and `customers`.
--    Expected result/shape: For sql-41 Exercise 5, expected output: one detail row per distinct input country with `is_subtotal = 0`, including a `(stored null)` row, plus exactly one `ALL COUNTRIES` row with `is_subtotal = 1`. The final columns are `country_label`, `is_subtotal`, and `customers`. The final order is `is_subtotal, country_label`.
--    Verify: For sql-41 Exercise 5, require exactly one row with `is_subtotal = 1`, require the `(stored null)` row to have `is_subtotal = 0`, and verify that detail-row `customers` sum to the grand-total `customers`. `GROUPING` receives the grouped `country` expression; do not try to call `GROUPING(NULL)`.
--    Hint ladder, rung 1: For sql-41 Exercise 5, confirm the groups are `country_label`, and `is_subtotal`; then check `is_subtotal, country_label` before applying the row cap.
-- 6. Edge case: return an empty array rather than NULL when an aggregate input
--    set is empty, and explain the COALESCE type cast.
--    Inputs: For sql-41 Exercise 6, read `customers.email` through `array_agg(email) FILTER (WHERE false)` and use a same-type `COALESCE` fallback. Build the answer toward `empty_email_array`.
--    Expected result/shape: For sql-41 Exercise 6, expected output: exactly one scalar row with one column, `empty_email_array`, whose value is the non-NULL empty `text[]` value `{}`. There is no customer-level key because the query has no `GROUP BY`.
--    Verify: For sql-41 Exercise 6, assert that the uncoalesced filtered `array_agg` result is `NULL`, while the final result satisfies `empty_email_array IS NOT NULL` and `cardinality(empty_email_array) = 0`.
--    Hint ladder, rung 1: For sql-41 Exercise 6, inspect the source keys that survive `WHERE`.

ROLLBACK;
