-- Day 2: Aggregates, GROUP BY, HAVING
-- BEGINNER WORKFLOW - sql-02: Aggregates, GROUP BY and HAVING
-- Guide: sql/postgres-60day/companion-guides/day02_aggregates_groupby_having.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-02.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: customers, order_items, products, orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.
-- Assumptions: Money columns are exact `numeric`; round only presentation values. `COUNT(column)` excludes NULL while `COUNT(*)` counts rows.
-- Pitfall: Selecting a non-grouped, non-aggregated column or using `WHERE` for an aggregate condition changes or invalidates the question.
-- Predict row grain and NULL/order behavior before executing each example.
-- Example 1: Orders per country
SELECT
  c.country,
  COUNT(*) AS customers
FROM
  customers c
GROUP BY
  c.country
ORDER BY
  customers DESC,
  c.country;

-- Example 2: Revenue by category with HAVING
SELECT
  p.category,
  ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)), 2) AS revenue
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
GROUP BY
  p.category
HAVING
  SUM(oi.unit_price * oi.quantity) > 10000
ORDER BY
  revenue DESC,
  p.category;

-- Example 3: Monthly orders and average order total
SELECT
  date_trunc('month', o.order_date) AS month,
  COUNT(*) AS orders,
  ROUND(AVG(o.total_amount), 2) AS avg_order
FROM
  orders o
GROUP BY
  month
ORDER BY
  month DESC;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Count customers by country and order countries by count then country.
--    Hint: The output grain is one row per country; include a deterministic secondary sort.
--    Inputs: For sql-02 Exercise 1, read from `customers`. Build the answer toward `country`, and `customer_count`; keep `country` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-02 Exercise 1, expected output: One row per country. The final columns are `country`, and `customer_count`. The final order is `customer_count DESC, c.country`.
--    Verify: For sql-02 Exercise 1, independently aggregate `customers` by `country`; require one output row for every distinct `country` tuple and compare `customer_count` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `customer_count` for the existing `country` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-02 Exercise 1, confirm the groups are `country`; then check `customer_count DESC, c.country` before applying the row cap.
-- 2. [Query writing] Calculate net revenue and average unit price by product category, keeping categories above 100,000 in revenue.
--    Hint: Join at line grain, aggregate once per category, and place the aggregate predicate in `HAVING`.
--    Inputs: For sql-02 Exercise 2, read from `order_items`, and `products`. Build the answer toward `category`, `net_revenue`, and `average_unit_price`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-02 Exercise 2, expected output: One row per qualifying category. The final columns are `category`, `net_revenue`, and `average_unit_price`. The final order is `net_revenue DESC, p.category`.
--    Verify: For sql-02 Exercise 2, independently aggregate `order_items`, and `products` by `category`; require one output row for every distinct `category` tuple and compare `net_revenue`, and `average_unit_price` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `net_revenue`, and `average_unit_price` for the existing `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-02 Exercise 2, start with the first relation in `order_items`, and `products`; after each join, record total rows and distinct `category` so the exact fanout or loss is visible.
-- 3. [Query writing] Summarize order count and average total by status, retaining statuses with at least 100 orders.
--    Hint: Filter groups after aggregation with `HAVING COUNT(*)`.
--    Inputs: For sql-02 Exercise 3, read from `orders`. Build the answer toward `status`, `order_count`, and `average_order_total`; keep `status` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-02 Exercise 3, expected output: One row per qualifying order status. The final columns are `status`, `order_count`, and `average_order_total`. The final order is `order_count DESC, o.status`.
--    Verify: For sql-02 Exercise 3, independently aggregate `orders` by `status`; require one output row for every distinct `status` tuple and compare `order_count`, and `average_order_total` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `order_count`, and `average_order_total` for the existing `status` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-02 Exercise 3, confirm the groups are `status`; then check `order_count DESC, o.status` before applying the row cap.
-- 4. [Prediction] Show `COUNT(*)`, `COUNT(email)`, and missing-email count together; predict their relationship.
--    Hint: `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit.
--    Inputs: For sql-02 Exercise 4, read from `customers` and count, in one aggregate query, all rows as `all_rows`, rows with a non-null `email` as `nonnull_email_rows`, and rows whose `email` is NULL as `missing_email_rows`.
--    Expected result/shape: For sql-02 Exercise 4, expected output: One row; present plus missing equals total. The final columns are `all_rows`, `nonnull_email_rows`, and `missing_email_rows`.
--    Verify: For sql-02 Exercise 4, confirm `nonnull_email_rows + missing_email_rows = all_rows`; the seed returns 500, 500, and 0 because every seeded customer has an email. In a transaction you roll back, set one customer's `email` to NULL and rerun: expect 500, 499, and 1.
--    Hint ladder, rung 1: For sql-02 Exercise 4, write `COUNT(*)` and `COUNT(email)` first and compare them; their difference is the number of NULL emails.
-- 5. [Debugging] Repair a query that tries to filter `SUM(amount)` in `WHERE` by moving the aggregate condition to the correct clause.
--    Hint: `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward.
--    Inputs: For sql-02 Exercise 5, read from `expenses`. Build the answer toward `category`, and `total_expense`; keep `category` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-02 Exercise 5, expected output: One row per expense category over the threshold. The final columns are `category`, and `total_expense`. The final order is `total_expense DESC, e.category`.
--    Verify: For sql-02 Exercise 5, independently aggregate `expenses` by `category`; require one output row for every distinct `category` tuple and compare `total_expense` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `total_expense` for the existing `category` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-02 Exercise 5, confirm the groups are `category`; then check `total_expense DESC, e.category` before applying the row cap.
-- 6. [Extension] Produce monthly order count, total revenue, and returned-order count for the last 12 complete or partial months.
--    Hint: Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable.
--    Inputs: For sql-02 Exercise 6, read from `orders` placed on or after `date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'`, group them by `date_trunc('month', order_date)`, and return each month's order count, summed `total_amount`, and count of `returned` orders.
--    Expected result/shape: For sql-02 Exercise 6, expected output: Up to 12 month rows in chronological order. The final columns are `order_month`, `order_count`, `order_revenue`, and `returned_orders`. The final order is `order_month`.
--    Verify: For sql-02 Exercise 6, confirm that `order_month` values are unique and that `SUM(order_count)` equals `SELECT COUNT(*) FROM orders WHERE order_date >= date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'`; for one month, recount its `returned` orders directly and compare the result with `returned_orders`.
--    Hint ladder, rung 1: For sql-02 Exercise 6, run the `WHERE` filter alone and check the earliest `order_date` it keeps before you group by month.
ROLLBACK;
