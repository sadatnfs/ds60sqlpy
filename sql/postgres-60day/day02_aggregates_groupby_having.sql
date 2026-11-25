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
--    Inputs: For sql-02 Exercise 1, read all 500 `customers` rows; `country` is `NOT NULL` and takes 8 values. Return `country` and `customer_count`.
--    Expected result/shape: For sql-02 Exercise 1, return 8 rows, one per country: `CA`, `DE`, `GB`, and `US` with 63 customers each, then `AU`, `BR`, `FR`, and `IN` with 62 each. The final columns are `country`, and `customer_count`. The final order is `customer_count DESC, c.country`.
--    Verify: For sql-02 Exercise 1, confirm the 8 counts sum to 500, matching `SELECT COUNT(*) FROM customers`, and that the four-way tie at 63 is listed alphabetically. Inside a rolled-back transaction, move customer 1 from `US` to `NZ`; the result must grow to 9 rows, with `US` falling to 62 and `NZ` appearing last with 1.
--    Hint ladder, rung 1: For sql-02 Exercise 1, confirm the groups are `country`; then check `customer_count DESC, c.country` before applying the row cap.
-- 2. [Query writing] Calculate net revenue and average unit price by product category, keeping categories above 100,000 in revenue.
--    Hint: Join at line grain, aggregate once per category, and place the aggregate predicate in `HAVING`.
--    Inputs: For sql-02 Exercise 2, join the 13,085 `order_items` rows to `products` on `product_id`; every item finds its product, and the 6 categories hold between 2,145 and 2,192 items each. Return `category`, `net_revenue`, and `average_unit_price`.
--    Expected result/shape: For sql-02 Exercise 2, return 6 rows, because every category clears the 100,000 `HAVING` threshold; `Sports` leads at 397427.70 and `Books` is last at 386192.77. The final columns are `category`, `net_revenue`, and `average_unit_price`. The final order is `net_revenue DESC, p.category`.
--    Verify: For sql-02 Exercise 2, confirm the 6 `net_revenue` values sum to 2355647.12, the same total that `SUM(unit_price * quantity * (1 - discount))` gives over all of `order_items`. Raise the threshold to 395000 and only `Sports` must remain, which proves `HAVING` filters groups after they are summed.
--    Hint ladder, rung 1: For sql-02 Exercise 2, start with the first relation in `order_items`, and `products`; after each join, record total rows and distinct `category` so the exact fanout or loss is visible.
-- 3. [Query writing] Summarize order count and average total by status, retaining statuses with at least 100 orders.
--    Hint: Filter groups after aggregation with `HAVING COUNT(*)`.
--    Inputs: For sql-02 Exercise 3, read all 4,362 `orders` rows across 5 `status` values. Return `status`, `order_count`, and `average_order_total`.
--    Expected result/shape: For sql-02 Exercise 3, return 5 rows, since every status has far more than 100 orders: `placed` and `shipped` with 873 each, then `delivered`, `paid`, and `returned` with 872 each. The final columns are `status`, `order_count`, and `average_order_total`. The final order is `order_count DESC, o.status`.
--    Verify: For sql-02 Exercise 3, confirm the 5 counts sum to 4,362 and that `paid` has the highest average at 548.24. Change the filter to `HAVING COUNT(*) >= 873`; only `placed` and `shipped` must remain, so the tie at 873 is broken by `status` name.
--    Hint ladder, rung 1: For sql-02 Exercise 3, confirm the groups are `status`; then check `order_count DESC, o.status` before applying the row cap.
-- 4. [Prediction] Show `COUNT(*)`, `COUNT(email)`, and missing-email count together; predict their relationship.
--    Hint: `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit.
--    Inputs: For sql-02 Exercise 4, read from `customers` and count, in one aggregate query, all rows as `all_rows`, rows with a non-null `email` as `nonnull_email_rows`, and rows whose `email` is NULL as `missing_email_rows`.
--    Expected result/shape: For sql-02 Exercise 4, expected output: One row; present plus missing equals total. The final columns are `all_rows`, `nonnull_email_rows`, and `missing_email_rows`.
--    Verify: For sql-02 Exercise 4, confirm `nonnull_email_rows + missing_email_rows = all_rows`; the seed returns 500, 500, and 0 because every seeded customer has an email. In a transaction you roll back, set one customer's `email` to NULL and rerun: expect 500, 499, and 1.
--    Hint ladder, rung 1: For sql-02 Exercise 4, write `COUNT(*)` and `COUNT(email)` first and compare them; their difference is the number of NULL emails.
-- 5. [Debugging] Repair a query that tries to filter `SUM(amount)` in `WHERE` by moving the aggregate condition to the correct clause.
--    Hint: `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward.
--    Inputs: For sql-02 Exercise 5, read the 10,000 `expenses` rows, 2,000 in each of 5 categories, with amounts from 100.51 to 9998.28. Return `category` and `total_expense`.
--    Expected result/shape: For sql-02 Exercise 5, return 5 rows, because every category total is above 1,000,000: `Marketing` first at 10108910.00 and `Infrastructure` last at 10080670.00. The final columns are `category`, and `total_expense`. The final order is `total_expense DESC, e.category`.
--    Verify: For sql-02 Exercise 5, rerun the grouping without `HAVING` and confirm the same 5 totals, each over 2,000 rows. Raise the threshold to 10100000; only `Marketing` and `COGS` (10103230.00) must remain.
--    Hint ladder, rung 1: For sql-02 Exercise 5, confirm the groups are `category`; then check `total_expense DESC, e.category` before applying the row cap.
-- 6. [Extension] Produce monthly order count, total revenue, and returned-order count for the last 12 complete or partial months.
--    Hint: Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable.
--    Inputs: For sql-02 Exercise 6, read from `orders` placed on or after `date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'`, group them by `date_trunc('month', order_date)`, and return each month's order count, summed `total_amount`, and count of `returned` orders.
--    Expected result/shape: For sql-02 Exercise 6, return 12 month rows in chronological order, since every month of the window has orders; the first `order_month` is the first day of the month eleven months before the current one, and the last is the current month. The final columns are `order_month`, `order_count`, `order_revenue`, and `returned_orders`. The final order is `order_month`.
--    Verify: For sql-02 Exercise 6, confirm that `order_month` values are unique and that `SUM(order_count)` equals `SELECT COUNT(*) FROM orders WHERE order_date >= date_trunc('month', CURRENT_TIMESTAMP) - INTERVAL '11 months'`; for one month, recount its `returned` orders directly and compare the result with `returned_orders`.
--    Hint ladder, rung 1: For sql-02 Exercise 6, run the `WHERE` filter alone and check the earliest `order_date` it keeps before you group by month.
ROLLBACK;
