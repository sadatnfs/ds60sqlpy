-- Day 15: Phase 1 Project - Complex Report
-- BEGINNER WORKFLOW - sql-15: Phase1 Project
-- Guide: sql/postgres-60day/companion-guides/day15_phase1_project.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-15.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items, customers.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.
-- Assumptions: All monetary summaries identify stored totals versus computed net line revenue. Reporting month uses UTC and empty populations remain visible where required.
-- Pitfall: Combining fact tables before fixing their grain multiplies measures; every project output must state its row grain and acceptance checks.
-- Predict row grain and NULL/order behavior before executing each example.
-- Customer purchase analysis with segmentation and temporal patterns
WITH line AS (
  SELECT
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date AS month_utc,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS revenue
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.customer_id,
    date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
),
segment AS (
  SELECT
    c.customer_id,
    COALESCE(c.segment, 'standard') AS segment,
    c.country
  FROM
    customers c
)
SELECT
  s.segment,
  s.country,
  l.month_utc,
  ROUND(SUM(l.revenue), 2) AS revenue,
  COUNT(DISTINCT l.customer_id) AS actives,
  ROUND(SUM(l.revenue) / NULLIF (COUNT(DISTINCT l.customer_id), 0), 2) AS rev_per_active
FROM
  line l
  JOIN segment s ON s.customer_id = l.customer_id
GROUP BY
  s.segment,
  s.country,
  l.month_utc
ORDER BY
  l.month_utc DESC,
  revenue DESC,
  s.segment,
  s.country
LIMIT 200;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Create a customer performance table with order count, stored revenue, and latest order date, retaining customers with no orders.
--    Hint: Left join from customers and aggregate at customer grain.
--    Inputs: For sql-15 Exercise 1, `LEFT JOIN` all 500 `customers` to their `orders`, then count `o.order_id`, sum `total_amount` with `COALESCE(..., 0)`, and take `MAX(order_date)` per customer.
--    Expected result/shape: For sql-15 Exercise 1, return 500 rows, one per customer, led by customer 181 (FR, 16 orders, 9502.21) and ending with the 62 `BR` customers who never ordered, each with 0 orders, 0 revenue, and a `NULL` `latest_order_date`. The final columns are `customer_id`, `full_name`, `country`, `order_count`, `stored_revenue`, and `latest_order_date`. The final order is `stored_revenue DESC, c.customer_id`.
--    Verify: For sql-15 Exercise 1, confirm 500 distinct `customer_id` values, `SUM(order_count)` = 4,362, and `SUM(stored_revenue)` = 2355646.89, matching `orders`. Swap `COUNT(o.order_id)` for `COUNT(*)` and the 62 no-order customers must show 1 instead of 0. Customers 51 and 428 tie at 8970.66, so `c.customer_id` must place 51 first on every run.
--    Hint ladder, rung 1: For sql-15 Exercise 1, start with the first relation in `customers`, and `orders`; after each join, record total rows and distinct `customer_id`, `full_name`, and `country` so the exact fanout or loss is visible.
-- 2. [Query writing] Create a product profitability table from net order-line revenue and catalog cost.
--    Hint: Calculate line revenue and line cost at item grain, then aggregate to product.
--    Inputs: For sql-15 Exercise 2, inner-join `products` to `order_items` and, per product, sum `quantity`, net line revenue, catalog cost `p.cost * oi.quantity`, and their difference as `gross_profit`.
--    Expected result/shape: For sql-15 Exercise 2, return 275 rows, one per product that has sold at least once, led by product 271 (Apparel, 160 units, `gross_profit` 10939.20) and ending with product 3 at 323.61; products 276 to 300 have no item rows and are left out. The final columns are `product_id`, `name`, `category`, `units_sold`, `net_revenue`, `catalog_cost`, and `gross_profit`. The final order is `gross_profit DESC, p.product_id`.
--    Verify: For sql-15 Exercise 2, confirm 275 distinct `product_id` values, `SUM(units_sold)` = 39,257, and `SUM(net_revenue)` = 2355647.12, the item-level total. Inside a rolled-back transaction, insert one `order_items` row for product 300 on order 1; the result must grow to 276 rows with product 300 at 1 unit sold.
--    Hint ladder, rung 1: For sql-15 Exercise 2, start with the first relation in `products`, and `order_items`; after each join, record total rows and distinct `product_id`, `name`, and `category` so the exact fanout or loss is visible.
-- 3. [Query writing] Build a UTC monthly order-status report with counts and stored revenue.
--    Hint: Derive one reporting month and group by month/status.
--    Inputs: For sql-15 Exercise 3, group all 4,362 `orders` by UTC month (`date_trunc('month', o.order_date AT TIME ZONE 'UTC')`) and `status`, counting orders and summing `total_amount`.
--    Expected result/shape: For sql-15 Exercise 3, return 224 rows, one per observed month and status pair, starting with `2023-02-01` `delivered` (1 order, 986.42); 46 months times 5 statuses would give 230, but the first three months lack 6 of the pairs. The final columns are `utc_month`, `status`, `order_count`, and `stored_revenue`. The final order is `utc_month, o.status`.
--    Verify: For sql-15 Exercise 3, confirm 224 distinct (`utc_month`, `status`) pairs and that the `order_count` values add up to 4,362; `2023-02-01` must show only `delivered` and `shipped`. Inside a rolled-back transaction, insert one order with status `cancelled`; the result must grow to 225 rows with the new pair in the current month at 1 order.
--    Hint ladder, rung 1: For sql-15 Exercise 3, confirm the groups are `status`; then check `utc_month, o.status` before applying the row cap.
-- 4. [Debugging] Reconcile stored order total, computed line total, and paid total without multiplying details.
--    Hint: Aggregate items and payments independently to order grain before joining.
--    Inputs: For sql-15 Exercise 4, pre-aggregate `order_items` to `line_totals` and `payments` to `paid_totals`, one row per `order_id` each, then join both to `orders` (inner to line totals, left to payments).
--    Expected result/shape: For sql-15 Exercise 4, return 4,362 rows, one per order; every `stored_minus_lines` is 0.00 after rounding (2,855 orders differ by under half a cent), so the order falls back to `order_id`, starting with order 21. 1,072 rows have a positive `unpaid_balance`, 873 of them `placed` orders with no payment row. The final columns are `order_id`, `stored_total`, `line_total`, `paid_total`, `stored_minus_lines`, and `unpaid_balance`. The final order is `ABS(o.total_amount - lt.line_total) DESC, o.order_id`.
--    Verify: For sql-15 Exercise 4, confirm 4,362 distinct `order_id` values, 0 rows with a negative `unpaid_balance`, and that `SUM(unpaid_balance)` is 523746.08, which equals 2355646.89 stored minus 1831900.81 paid. Inside a rolled-back transaction, set order 1's `total_amount` to 250.20; order 1 must jump to the first row with `stored_minus_lines` and `unpaid_balance` both 10.00.
--    Hint ladder, rung 1: For sql-15 Exercise 4, run `line_totals`, and `paid_totals` one at a time. Record each CTE's row count and `order_id` uniqueness before the next stage uses it.
-- 5. [Prediction] Compare monthly budgets with actual expenses and preserve missing sides.
--    Hint: Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero.
--    Inputs: For sql-15 Exercise 5, sum the 10,000 `expenses` rows by `category` and calendar month, sum the 125 `budgets` rows by `category` and `period`, then `FULL JOIN` the two summaries on both keys.
--    Expected result/shape: For sql-15 Exercise 5, return 125 rows, 5 categories (`COGS`, `G&A`, `Infrastructure`, `Marketing`, `Payroll`) times 25 months from `2024-11-01` to `2026-11-01`; on the fixture every pair has both a budget and an actual, so no column is `NULL`. The first row is `COGS` for `2024-11-01` with 654000.00 budgeted against 72384.36 spent. The final columns are `category`, `period`, `budget_amount`, `actual_amount`, and `variance`. The final order is `period, category`.
--    Verify: For sql-15 Exercise 5, confirm 125 distinct (`category`, `period`) pairs; joining raw `budgets` to raw `expenses` instead returns 10,000 rows, one per expense, which is the fanout the two summaries prevent. Inside a rolled-back transaction, add a `Travel` budget for `2026-11-01` and a `Legal` expense dated `2026-11-10`; both must appear, `Travel` with a `NULL` actual and `Legal` with a `NULL` budget, and both with a `NULL` variance.
--    Hint ladder, rung 1: For sql-15 Exercise 5, run `actual`, and `planned` one at a time. Record each CTE's row count and `category` uniqueness before the next stage uses it.
-- 6. [Extension] Produce one executive summary row with population, activity, stored revenue, computed revenue, and payments.
--    Hint: Compute independent one-row aggregates, then cross join them to avoid detail multiplication.
--    Inputs: For sql-15 Exercise 6, compute each total in its own single-row CTE (customer count, order count and stored revenue, line revenue from `order_items`, and payment sum) and `CROSS JOIN` the four one-row results.
--    Expected result/shape: For sql-15 Exercise 6, return one row: 500 customers, 4,362 orders, `stored_revenue` 2355646.89, `computed_revenue` 2355647.12, and `payments` 1831900.81. The final columns are `customers`, `orders`, `stored_revenue`, `computed_revenue`, and `payments`.
--    Verify: For sql-15 Exercise 6, confirm each value against its own query, for example `SELECT ROUND(SUM(amount), 2) FROM payments` returns 1831900.81. Then sum `o.total_amount` after `orders JOIN order_items` and get 8633041.53, more than 3.6 times the stored figure; that fanout is why every total is computed before the `CROSS JOIN`.
--    Hint ladder, rung 1: For sql-15 Exercise 6, run `customer_kpis`, `order_kpis`, `line_kpis`, and `payment_kpis` one at a time. Record each CTE's row count and `customer_id` uniqueness before the next stage uses it.
ROLLBACK;
