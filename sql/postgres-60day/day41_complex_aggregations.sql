-- Day 41: Complex Aggregations (FILTER, conditional metrics, string aggregation)
-- BEGINNER WORKFLOW - sql-41: Complex Aggregations
-- Guide: sql/postgres-60day/companion-guides/day41_complex_aggregations.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-41.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
SELECT
  p.category,
  SUM(oi.quantity) AS total_qty,
  SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '30 days') AS qty_30d,
  SUM(oi.quantity) FILTER (WHERE o.order_date >= now() - interval '90 days') AS qty_90d,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) FILTER (WHERE o.order_date >= now() - interval '30 days'), 2) AS revenue_30d
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
  JOIN orders o ON o.order_id = oi.order_id
GROUP BY
  p.category
ORDER BY
  revenue DESC;

-- Conditional aggregation using CASE for multi-metric report
SELECT
  c.country,
  SUM(
    CASE WHEN o.status IN ('paid', 'shipped', 'delivered') THEN
      1
    ELSE
      0
    END) AS successful_orders,
  SUM(
    CASE WHEN o.status = 'returned' THEN
      1
    ELSE
      0
    END) AS returned_orders,
  ROUND(SUM(
      CASE WHEN o.status <> 'returned' THEN
        o.total_amount
      ELSE
        0
      END), 2) AS net_revenue
FROM
  orders o
  JOIN customers c ON c.customer_id = o.customer_id
GROUP BY
  c.country
ORDER BY
  net_revenue DESC;

-- String aggregation for labels
SELECT
  p.category,
  string_agg(DISTINCT p.name, ', ' ORDER BY p.name) AS sample_products
FROM
  products p
GROUP BY
  p.category
ORDER BY
  p.category
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
--    Inputs: For sql-41 Exercise 1, join `orders`, `order_items`, and `products` once in a `lines` CTE (13,085 rows, one per order line) carrying `category`, `order_id`, `customer_id`, `order_date`, `quantity`, and line revenue `unit_price * quantity * (1 - discount)`; every metric is a `FILTER` over that relation with 30-day or 90-day windows anchored at `CURRENT_TIMESTAMP`.
--    Expected result/shape: For sql-41 Exercise 1, return 6 rows, one per sold category (`Apparel`, `Beauty`, `Books`, `Electronics`, `Home`, `Sports`); the window values move with the load date because the seed dates are relative to it. The final columns are `category`, `revenue_30d`, `revenue_90d`, `orders_30d`, `units_30d`, `customers_90d`, and `revenue_per_order_30d`. The final order is `revenue_30d DESC NULLS LAST, category`.
--    Verify: For sql-41 Exercise 1, confirm 6 rows with unique `category`, `revenue_90d >= revenue_30d` on every row, and `revenue_per_order_30d` within 0.01 of `revenue_30d / orders_30d`; recompute `Books` with a plain `WHERE p.category = 'Books' AND o.order_date >= CURRENT_TIMESTAMP - interval '30 days'` query and match `revenue_30d`, `orders_30d`, and `units_30d`; then, in a rolled-back transaction, insert a product in a new `Garden` category and confirm the result still has 6 rows, because categories come from order lines.
--    Hint ladder, rung 1: For sql-41 Exercise 1, run `lines` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 2. Create a per-country string_agg of top 5 product names by revenue.
--    Inputs: For sql-41 Exercise 2, join `customers`, `orders`, `order_items`, and `products`, sum line revenue at (`country`, `product_id`, `name`) grain in `product_revenue`, rank it with `ROW_NUMBER() OVER (PARTITION BY country ORDER BY revenue DESC, product_id)` in `ranked`, and keep ranks 1 to 5 for `string_agg`.
--    Expected result/shape: For sql-41 Exercise 2, return 7 rows, one per country with orders (`AU`, `CA`, `DE`, `FR`, `GB`, `IN`, `US`; `BR` has no orders), each listing exactly five names in rank order, for example `AU` = `Product 238, Product 207, Product 251, Product 261, Product 243`. The final columns are `country` and `top_five_products`. The final order is `country`.
--    Verify: For sql-41 Exercise 2, rerun `ranked` alone with `WHERE country = 'AU' AND product_rank <= 5` and match the five `AU` names in order; confirm every country bought 275 distinct products, so no list is short; then add `WHERE o.order_id = 1` inside `product_revenue` and confirm one row whose list has only the order's two products, `Product 79, Product 48`, with no padding.
--    Hint ladder, rung 1: For sql-41 Exercise 2, run `product_revenue`, and `ranked` one at a time. Record each CTE's row count and `country` uniqueness before the next stage uses it.
-- 3. Prediction: compare GROUPING SETS ((country), (category), ()) with CUBE
--    (country, category). Predict which country/category detail level is absent.
--    Inputs: For sql-41 Exercise 3, build a `lines` CTE of order-line revenue with each line's customer `country` and product `category` (13,085 rows), then aggregate it with `GROUP BY CUBE (country, category)` and label `GROUPING(country, category)` as `grouping_mask` and `grouping_level`.
--    Expected result/shape: For sql-41 Exercise 3, return 56 rows: 42 detail rows (7 countries times 6 categories, mask `0`), 7 country subtotals (mask `1`), 6 category subtotals (mask `2`), and one grand total (mask `3`) of 2355647.1235. `grouping_mask` is `0` for detail, `1` for a country subtotal, `2` for a category subtotal, and `3` for the grand total. The final columns are `country`, `category`, `revenue`, `grouping_mask`, and `grouping_level`. The final order is `grouping_mask, country, category`.
--    Verify: For sql-41 Exercise 3, count rows per `grouping_mask` (42, 7, 6, 1) and confirm that `revenue` sums to 2355647.1235 within each mask; check one cell such as `AU`/`Apparel` = 54277.4215 against a plain filtered sum; then replace `CUBE` with `GROUPING SETS ((country), (category), ())` and confirm 14 rows, because the 42 country-by-category detail rows are the level that list omits.
--    Hint ladder, rung 1: For sql-41 Exercise 3, run `lines` one at a time. Record each CTE's row count and `country`, and `category` uniqueness before the next stage uses it.
-- 4. Construction: report order count, paid revenue, returned revenue, and
--    distinct customers per country using FILTER.
--    Inputs: For sql-41 Exercise 4, join `orders` to `customers` (4,362 order rows), group by `c.country`, and compute every measure with `COUNT` or `SUM` plus `FILTER (WHERE o.status = ...)` over the same rows; `status` has five values (`placed`, `paid`, `shipped`, `delivered`, `returned`).
--    Expected result/shape: For sql-41 Exercise 4, return 7 rows, one per country with orders; `BR` is absent because none of its 62 customers ordered. `AU` shows 613 orders, 123 paid orders, 66338.06 paid revenue, 66707.95 returned revenue, and 62 customers. The final columns are `country`, `orders`, `paid_orders`, `paid_revenue`, `returned_revenue`, and `customers`. The final order is `c.country`.
--    Verify: For sql-41 Exercise 4, confirm `orders` sums to 4362, `paid_orders` to 872, and `paid_revenue` to 478068.36, matching `SELECT count(*), sum(total_amount) FROM orders WHERE status = 'paid'`; then rewrite the join as `customers LEFT JOIN orders` and observe that `BR` appears with `orders = 1` from `COUNT(*)` but `customers = 0`, so a left-join version must count `o.order_id`.
--    Hint ladder, rung 1: For sql-41 Exercise 4, start with the first relation in `orders`, and `customers`; after each join, record total rows and distinct `country` so the exact fanout or loss is visible.
-- 5. Debugging: distinguish a real NULL country from a subtotal NULL by adding
--    GROUPING(country) and a safe display label.
--    Inputs: For sql-41 Exercise 5, read `customers.country` (500 rows) and append one controlled `NULL::text` row with `UNION ALL` in a `country_input` CTE; group by `GROUPING SETS ((country), ())`, and use `GROUPING(country)` to build `country_label`, `is_subtotal`, and `customers`.
--    Expected result/shape: For sql-41 Exercise 5, return 10 rows: 8 country rows and one `(stored null)` row with 1 customer, all with `is_subtotal = 0`, plus one `ALL COUNTRIES` row with `is_subtotal = 1` and 501 customers. The final columns are `country_label`, `is_subtotal`, and `customers`. The final order is `is_subtotal, country_label`.
--    Verify: For sql-41 Exercise 5, confirm exactly one row has `is_subtotal = 1` and that the nine detail `customers` values sum to its 501; confirm `(stored null)` carries `is_subtotal = 0`; then remove the `UNION ALL` branch and confirm 9 rows with a 500 total. `GROUPING` receives the grouped `country` expression; do not try to call `GROUPING(NULL)`.
--    Hint ladder, rung 1: For sql-41 Exercise 5, run `country_input` alone first (501 rows: the 500 customers plus the `NULL::text` row), then check that `GROUPING SETS ((country), ())` labels the stored `NULL` as `(stored null)` with `is_subtotal = 0` and that `is_subtotal, country_label` puts the nine detail rows before `ALL COUNTRIES`.
-- 6. Edge case: return an empty array rather than NULL when an aggregate input
--    set is empty, and explain the COALESCE type cast.
--    Inputs: For sql-41 Exercise 6, read `customers.email` through `array_agg(email) FILTER (WHERE false)`, which sees all 500 rows but aggregates none, and wrap it in `COALESCE(..., '{}'::text[])` so both branches are `text[]`.
--    Expected result/shape: For sql-41 Exercise 6, return exactly one row with one column, `empty_email_array`, whose value is the non-NULL empty `text[]` value `{}`. There is no customer-level key because the query has no `GROUP BY`.
--    Verify: For sql-41 Exercise 6, select the uncoalesced filtered `array_agg` and confirm `IS NULL` is true, while the final result satisfies `empty_email_array IS NOT NULL` and `cardinality(empty_email_array) = 0`; then replace the fallback with a bare `ARRAY[]` and confirm the error `cannot determine type of empty array`.
--    Hint ladder, rung 1: For sql-41 Exercise 6, run `SELECT array_agg(email) FILTER (WHERE false) FROM customers` alone first and note that it returns `NULL`, not `{}`.
ROLLBACK;
