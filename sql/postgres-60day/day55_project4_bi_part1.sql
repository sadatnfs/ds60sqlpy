-- Day 55: Project 4 - Complex BI (Part 1)
-- BEGINNER WORKFLOW - sql-55: Project 4 BI Part 1
-- Guide: sql/postgres-60day/companion-guides/day55_project4_bi_part1.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-55.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: payments, orders, customers, order_items, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Multi-dimensional analysis (drill-down capability)
BEGIN;
SET search_path TO training, public;

-- Use GROUPING SETS/ROLLUP/CUBE for flexible drilldowns.
-- Dimensions: country, category, primary payment method, month.
-- An order can have split payments, so first choose one reporting label:
-- the method with the greatest paid amount (method name breaks ties).
WITH payment_by_method AS (
  SELECT
    order_id,
    method,
    SUM(amount) AS method_amount
  FROM
    payments
  GROUP BY
    order_id,
    method
),
primary_payment_method AS (
  SELECT
    order_id,
    method
  FROM (
    SELECT
      order_id,
      method,
      ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY method_amount DESC,
        method) AS method_rank
  FROM
    payment_by_method) ranked_methods
  WHERE
    method_rank = 1
),
line AS (
  SELECT
    c.country,
    p.category,
    COALESCE(pm.method, 'unpaid') AS payment_method,
    date_trunc('month', o.order_date)::date AS month,
    (oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue,
    oi.quantity AS qty
  FROM
    orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
    LEFT JOIN primary_payment_method pm ON pm.order_id = o.order_id
)
SELECT
  country,
  category,
  payment_method,
  month,
  ROUND(SUM(revenue), 2) AS revenue,
  SUM(qty) AS units,
  GROUPING (country) AS g_country,
  GROUPING (category) AS g_category,
  GROUPING (payment_method) AS g_method,
  GROUPING (month) AS g_month
FROM
  line
GROUP BY
  ROLLUP (country, category, payment_method, month)
ORDER BY
  country NULLS FIRST,
  category NULLS FIRST,
  payment_method NULLS FIRST,
  month NULLS FIRST;

-- Drill-down example: country -> category -> product (top-N per level)
WITH prod_rev AS (
  SELECT
    c.country,
    p.category,
    p.product_id,
    p.name,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN products p ON p.product_id = oi.product_id
  GROUP BY
    c.country,
    p.category,
    p.product_id,
    p.name
),
ranked AS (
  SELECT
    *,
    RANK() OVER (PARTITION BY country,
      category ORDER BY revenue DESC) AS rnk
  FROM
    prod_rev
)
SELECT
  *
FROM
  ranked
WHERE
  rnk <= 5
ORDER BY
  country,
  category,
  rnk;

-- Exercises
-- 1. Replace ROLLUP with CUBE to get all subtotal combinations and compare row counts.
--    Inputs: For sql-55 Exercise 1, join `orders`, `customers`, `order_items`, and `products` into one revenue line per order item (13,085 lines carrying `country` and `category`), group those lines once with `ROLLUP (country, category)` and once with `CUBE (country, category)`, and count the rows each grouping produces.
--    Expected result/shape: For sql-55 Exercise 1, expected output: one row with `rollup_row_count` 50 and `cube_row_count` 56. Both share the 42 country and category detail rows, the 7 country subtotals, and the grand total; the 6 extra `CUBE` rows are the category-only subtotals. BR has no orders, so it appears in neither grouping.
--    Verify: For sql-55 Exercise 1, rebuild both counts from distinct values: 42 distinct (country, category) pairs plus 7 countries plus 1 total gives 50, and adding the 6 categories gives 56. In a rolled-back transaction, give BR customer 8 one order with a single Apparel line: both counts rise by 2 (52 and 58), one BR detail row and one BR subtotal, while the category-only subtotal count stays 6.
--    Hint ladder, rung 1: For sql-55 Exercise 1, run `rollup_rows` and `cube_rows` as plain `SELECT`s before counting them: the rows with `country` `NULL` and a category present (6 of them) exist only in the `CUBE` output.
-- 2. Add a dimension for order status and re-run the drill-down with top-5.
--    Inputs: For sql-55 Exercise 2, sum line revenue (`unit_price * quantity * (1 - discount)`) per `country`, `category`, `status`, `product_id`, and `name` (7,566 product rows), then number the products inside each (country, category, status) group with `ROW_NUMBER()` ordered by `revenue DESC, product_id` and keep numbers 1 to 5.
--    Expected result/shape: For sql-55 Exercise 2, expected output: 1,050 rows, exactly five for each of the 210 (country, category, status) groups (7 countries, 6 categories, 5 statuses, each group holding 30 to 42 products), with columns `country`, `category`, `status`, `product_id`, `name`, `revenue` (rounded to 2 places), and `product_rank`. The final order is `country, category, status, product_rank`; the first group is AU, Apparel, `delivered`, led by product 241 at 793.36.
--    Verify: For sql-55 Exercise 2, check that AU, Apparel, `delivered` lists products 241, 223, 163, 121, and 97 (793.36 down to 727.36), with product 109 sixth at 651.77, and that no (country, category, status, `product_id`) repeats. In a rolled-back transaction, add a 150.00 line for product 109 to AU order 47 (delivered): product 109 moves to rank 1 at 801.77, product 97 drops out, and the group still returns five rows.
--    Hint ladder, rung 1: For sql-55 Exercise 2, count `product_revenue` on its own first (7,566 rows), then count its distinct (country, category, status) groups (210); five rows per group is the target, and a group returning six means the ranking function or its `product_id` tie-breaker is wrong.
-- 3. Prediction: list the grouping sets produced by ROLLUP(country, category,
--    month) and contrast them with CUBE before running either query.
--    Inputs: For sql-55 Exercise 3, first write down the grouping sets of `ROLLUP (country, category, month)` (4 sets, from full detail to the grand total) and of `CUBE` on the same columns (8 sets), then run `ROLLUP (country, category)` over the order-item revenue lines and expose `GROUPING (country, category)` as `grouping_mask`.
--    Expected result/shape: For sql-55 Exercise 3, expected output: 50 rows with columns `country`, `category`, `revenue`, and `grouping_mask`, ordered by `grouping_mask, country, category`: 42 detail rows with mask 0 (AU Apparel 54,277.4215), 7 country subtotals with mask 1 (AU 330,947.6960), and 1 grand total with mask 3 (2,355,647.1235). No row has mask 2, because `ROLLUP` never totals a category across countries.
--    Verify: For sql-55 Exercise 3, count the rows per mask (42, 7, 1) and confirm that the 7 mask 1 rows add up to the mask 3 total of 2,355,647.1235. In a rolled-back transaction, give BR customer 8 one order with a 20.00 Apparel line: the result grows to 52 rows (43 with mask 0, 8 with mask 1), and BR shows 20.0000 at both the detail and subtotal level.
--    Hint ladder, rung 1: For sql-55 Exercise 3, run the grouped query without `ORDER BY` and add `COUNT(*)` beside the mask: a mask 0 row sums the lines of one country and category, while the mask 1 and mask 3 rows sum every line of a country or of the whole load.
-- 4. Construction: use PostgreSQL's GROUPING(country, category) bit mask to
--    assign stable detail/subtotal/grand-total labels without mistaking stored
--    NULLs for subtotal markers.
--    Inputs: For sql-55 Exercise 4, group the same order-item revenue lines with `ROLLUP (country, category)` and return `GROUPING (country, category)` as `level_id`, plus a `CASE` on that same mask that maps 0, 1, and 3 to `level_name` values 'country/category detail', 'country subtotal', and 'grand total'.
--    Expected result/shape: For sql-55 Exercise 4, expected output: the same 50 rows as Exercise 3 with columns `level_id`, `level_name`, `country`, `category`, and `revenue`, ordered by `level_id, country, category`: 42 rows at level 0, 7 at level 1, and 1 at level 3, and no `NULL` `level_name`.
--    Verify: For sql-55 Exercise 4, count rows per `level_id` and `level_name` (42, 7, 1) and confirm each `level_id` maps to exactly one name. In a rolled-back transaction, run `ALTER TABLE products ALTER COLUMN category DROP NOT NULL` and set product 241's category to `NULL`: level 0 grows to 49 rows, 7 of them with a stored `NULL` category, and all 7 still say 'country/category detail' because the label reads the mask, not the column.
--    Hint ladder, rung 1: For sql-55 Exercise 4, select `GROUPING (country, category)`, `country`, and `category` side by side before writing the `CASE`: mask 1 always pairs with a `NULL` category and mask 3 with two `NULL`s, so the mask, not `IS NULL`, decides the label.
-- 5. Debugging: replace RANK with ROW_NUMBER plus a deterministic tie-breaker
--    when the dashboard must show exactly five products per group.
--    Inputs: For sql-55 Exercise 5, sum order-item revenue per `country`, `product_id`, and `name` (1,925 rows, 275 products in each of 7 countries), then number the products inside each country with `ROW_NUMBER()` ordered by `revenue DESC, product_id` as `position` and keep positions 1 to 5.
--    Expected result/shape: For sql-55 Exercise 5, expected output: 35 rows, one per country and `position` 1 to 5, with columns `country`, `product_id`, `name`, `revenue`, and `position`. The final order is `country, position`; AU starts with product 238 at 3,319.3310, followed by products 207, 251, 261, and 243 (2,692.5745).
--    Verify: For sql-55 Exercise 5, confirm that no (country, `product_id`) repeats and that AU product 233 sits sixth at 2,684.2590. In a rolled-back transaction, add a line for product 233 to AU order 46 with `unit_price` 166.31 and `discount` 0.95 (8.3155): products 233 and 243 tie at 2,692.5745, `RANK() <= 5` now returns 36 rows, and `ROW_NUMBER` still returns 35, giving position 5 to product 233 because it has the lower `product_id`.
--    Hint ladder, rung 1: For sql-55 Exercise 5, look at positions 4 to 7 of one country with both `RANK()` and `ROW_NUMBER()` beside `revenue`: the two only differ when revenue ties, so build a tie in a transaction to see the cut change.
-- 6. Edge case: preserve a real '(unknown)' country member separately from the
--    ALL-countries subtotal in both machine-readable and display columns.
--    Inputs: For sql-55 Exercise 6, read the 500 `customers` rows and group them with `GROUPING SETS ((country), ())`, returning `GROUPING (country)` as `is_generated_total` and a `display_country` that says 'ALL' only when that flag is 1 and '(unknown member)' for a stored `NULL` country.
--    Expected result/shape: For sql-55 Exercise 6, expected output: 9 rows with columns `display_country`, `is_generated_total`, and `customers`, ordered by `is_generated_total, display_country`: eight countries including BR (62 or 63 customers each, flag 0), then `ALL` with 500 and flag 1.
--    Verify: For sql-55 Exercise 6, compare each country row with `SELECT country, COUNT(*) FROM customers GROUP BY country` and confirm the eight counts add up to the `ALL` row. `country` is `NOT NULL` (default 'US'), so in a rolled-back transaction run `ALTER TABLE customers ALTER COLUMN country DROP NOT NULL` and insert one customer with a `NULL` country: the result has 10 rows, a '(unknown member)' row with 1 customer and flag 0, and `ALL` at 501.
--    Hint ladder, rung 1: For sql-55 Exercise 6, select `country` and `GROUPING (country)` side by side first: the generated total and a stored `NULL` country both show `NULL` in `country`, and only the `GROUPING` value tells them apart.
ROLLBACK;
