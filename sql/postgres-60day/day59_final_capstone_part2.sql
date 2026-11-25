-- Day 59: Final Capstone - Integrated Data Challenge (Part 2)
-- BEGINNER WORKFLOW - sql-59: Final Capstone Part 2
-- Guide: sql/postgres-60day/companion-guides/day59_final_capstone_part2.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-59.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: orders, order_items, customers, events, products.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Focus: Complex business logic, performance requirements, stakeholder queries
BEGIN;
SET search_path TO training, public;

-- 1. Business KPI Suite (multi-level calculations)
-- a) LTV by cohort and segment
WITH order_values AS (
  SELECT
    o.customer_id,
    o.order_id,
    SUM(oi.unit_price * oi.quantity * (1 - oi.discount)) AS order_value,
    o.order_date
  FROM
    orders o
    JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY
    o.customer_id,
    o.order_id,
    o.order_date
),
ltv AS (
  SELECT
    customer_id,
    date_trunc('month', MIN(order_date))::date AS first_order_month,
    SUM(order_value) AS ltv
  FROM
    order_values
  GROUP BY
    customer_id
),
cohort AS (
  SELECT
    c.customer_id,
    date_trunc('month', c.created_at)::date AS cohort_month,
    COALESCE(c.segment, 'standard') AS segment
  FROM
    customers c
)
SELECT
  cohort.segment,
  cohort.cohort_month,
  ROUND(AVG(ltv.ltv), 2) AS avg_ltv,
  COUNT(*) AS customers
FROM
  ltv
  JOIN cohort ON cohort.customer_id = ltv.customer_id
GROUP BY
  cohort.segment,
  cohort.cohort_month
ORDER BY
  cohort.cohort_month DESC,
  avg_ltv DESC
LIMIT 100;

-- b) Ordered conversion funnel from events -> orders (last 90 days).
-- First collect the earliest page view. Each later CTE can only choose a
-- timestamp at or after the timestamp supplied by its previous stage.
WITH viewed_stage AS (
  SELECT
    c.customer_id,
    MIN(e.event_time) FILTER (WHERE e.event_type = 'page_view') AS viewed_at
  FROM
    customers c
    LEFT JOIN events e ON e.customer_id = c.customer_id
      AND e.event_time >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY
    c.customer_id
),
added_stage AS (
  SELECT
    viewed.customer_id,
    viewed.viewed_at,
    MIN(event.event_time) AS added_at
  FROM
    viewed_stage viewed
    LEFT JOIN events event ON event.customer_id = viewed.customer_id
      AND event.event_type = 'add_to_cart'
      AND event.event_time >= viewed.viewed_at
  GROUP BY
    viewed.customer_id,
    viewed.viewed_at
),
checkout_stage AS (
  SELECT
    added.customer_id,
    added.viewed_at,
    added.added_at,
    MIN(event.event_time) AS checkout_at
  FROM
    added_stage added
    LEFT JOIN events event ON event.customer_id = added.customer_id
      AND event.event_type = 'checkout'
      AND event.event_time >= added.added_at
  GROUP BY
    added.customer_id,
    added.viewed_at,
    added.added_at
),
purchase_stage AS (
  SELECT
    checkout.customer_id,
    checkout.viewed_at,
    checkout.added_at,
    checkout.checkout_at,
    MIN(customer_order.order_date) AS purchased_at
  FROM
    checkout_stage checkout
    LEFT JOIN orders customer_order ON customer_order.customer_id = checkout.customer_id
      AND customer_order.order_date >= checkout.checkout_at
      AND customer_order.order_date >= CURRENT_TIMESTAMP - interval '90 days'
  GROUP BY
    checkout.customer_id,
    checkout.viewed_at,
    checkout.added_at,
    checkout.checkout_at
),
activity AS (
  SELECT
    customer_id,
    viewed_at IS NOT NULL AS viewed,
    added_at IS NOT NULL
    AND added_at >= viewed_at AS added,
    checkout_at IS NOT NULL
    AND checkout_at >= added_at AS checked_out,
    purchased_at IS NOT NULL
    AND purchased_at >= checkout_at AS bought
  FROM
    purchase_stage
)
SELECT
  COUNT(*) FILTER (WHERE viewed) AS viewers,
  COUNT(*) FILTER (WHERE added) AS adders,
  COUNT(*) FILTER (WHERE checked_out) AS checkouts,
  COUNT(*) FILTER (WHERE bought) AS buyers
FROM
  activity;

-- c) Top product pairs by co-occurrence (market basket)
WITH items AS (
  SELECT
    order_id,
    product_id
  FROM
    order_items
  GROUP BY
    order_id,
    product_id
),
pairs AS (
  SELECT
    a.product_id AS p1,
    b.product_id AS p2,
    COUNT(*) AS together
  FROM
    items a
    JOIN items b ON a.order_id = b.order_id
      AND a.product_id < b.product_id
  GROUP BY
    a.product_id,
    b.product_id
)
SELECT
  p1.name AS product_a,
  p2.name AS product_b,
  together
FROM
  pairs
  JOIN products p1 ON p1.product_id = pairs.p1
  JOIN products p2 ON p2.product_id = pairs.p2
ORDER BY
  together DESC
LIMIT 20;

-- 2. Performance Aids (indexes/partitioning hints) - run EXPLAIN before/after
-- Note: These DDLs are rolled back unless you COMMIT intentionally
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders (customer_id, order_date);

CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items (order_id);

CREATE INDEX IF NOT EXISTS idx_payments_order_date ON payments (order_id, payment_date);

EXPLAIN ANALYZE
SELECT
  o.customer_id,
  SUM(o.total_amount)
FROM
  orders o
WHERE
  o.order_date >= now() - interval '180 days'
GROUP BY
  o.customer_id
ORDER BY
  SUM(o.total_amount) DESC
LIMIT 50;

-- 3. Stakeholder Views
-- a) Finance: Budget vs Actual YTD by category
WITH ytd_exp AS (
  SELECT
    date_trunc('year', expense_date)::date AS yr,
    category,
    SUM(amount) AS actual
  FROM
    expenses
  WHERE
    expense_date >= date_trunc('year', now())
  GROUP BY
    1,
    2
),
ytd_bud AS (
  SELECT
    date_trunc('year', period)::date AS yr,
    category,
    SUM(amount) AS budget
  FROM
    budgets
  WHERE
    period >= date_trunc('year', now())
  GROUP BY
    1,
    2
)
SELECT
  COALESCE(b.category, e.category) AS category,
  COALESCE(b.yr, e.yr) AS year,
  COALESCE(b.budget, 0) AS budget_ytd,
  COALESCE(e.actual, 0) AS actual_ytd,
  ROUND(COALESCE(e.actual, 0) - COALESCE(b.budget, 0), 2) AS variance
FROM
  ytd_bud b
  FULL OUTER JOIN ytd_exp e ON e.yr = b.yr
  AND e.category = b.category
ORDER BY
  category;

-- b) Marketing: Campaign-assisted purchases (within 7 days)
WITH first_purchase AS (
  SELECT
    o.customer_id,
    MIN(o.order_date) AS first_buy
  FROM
    orders o
  GROUP BY
    o.customer_id
),
touch AS (
  SELECT
    e.customer_id,
    e.event_time,
    e.metadata ->> 'campaign' AS campaign
  FROM
    events e
  WHERE
    e.event_type IN ('page_view', 'add_to_cart', 'checkout')
    AND e.metadata ? 'campaign'
    AND NULLIF (trim(e.metadata ->> 'campaign'), '') IS NOT NULL
)
SELECT
  t.campaign,
  COUNT(DISTINCT t.customer_id) AS assisted_customers
FROM
  touch t
  JOIN first_purchase fp ON fp.customer_id = t.customer_id
WHERE
  t.event_time BETWEEN fp.first_buy - interval '7 days' AND fp.first_buy
GROUP BY
  t.campaign
ORDER BY
  assisted_customers DESC
LIMIT 20;

-- 4. Large-scale considerations
-- For 100M+ rows, favor partitioning by time on orders/events, and use partial indexes on recent partitions.
-- Ensure queries constrain partition key (order_date, event_time) to enable pruning.
-- Exercises
-- 1. Prediction: state the grain of every CTE in the LTV query and identify the
--    exact step where order-grain values become customer-grain values.
--    Inputs: For sql-59 Exercise 1, read the learner LTV query in section 1a (`order_values`, then `ltv`, then `cohort`, then the grouped `SELECT`) and record each aggregation step in an inline `VALUES` fixture with `step_name`, `row_grain`, and `key_columns`.
--    Expected result/shape: For sql-59 Exercise 1, expected output: 3 rows, one per `step_name`: `order_values` at one row per order keyed by `customer_id + order_id`, `customer_ltv` at one row per customer keyed by `customer_id`, and `cohort_segment_summary` at one row per cohort/segment keyed by `cohort_month + segment`. The final columns are `step_name`, `row_grain`, and `key_columns`.
--    Verify: For sql-59 Exercise 1, prove each grain claim by running the learner CTEs: `order_values` has 4,362 rows and 4,362 distinct `order_id` values but only 438 distinct `customer_id` values, `ltv` has 438 rows (the order-to-customer step, since 62 of the 500 customers never ordered), `cohort` has 500, and the summary has 191 (`segment`, `cohort_month`) groups whose `customers` add back to 438 before `LIMIT 100` trims the output.
--    Hint ladder, rung 1: For sql-59 Exercise 1, run `SELECT COUNT(*), COUNT(DISTINCT order_id), COUNT(DISTINCT customer_id) FROM order_values` with the learner CTE in front; 4,362, 4,362, and 438 show which key the first step really has.
-- 2. Construction: turn the funnel counts into step-to-step and overall
--    conversion rates while preserving customers who purchased without a
--    recorded event.
--    Inputs: For sql-59 Exercise 2, derive `viewed_at`, `added_at`, `checkout_at`, and `purchased_at` per customer over the same trailing-90-day window.
--    Expected result/shape: For sql-59 Exercise 2, expected output: exactly one summary row with ordered stage counts, `buyers_without_view`, and three conversion rates whose denominators are the preceding ordered populations.
--    Verify: For sql-59 Exercise 2, confirm one row with 398 viewers, 340 adders, 275 checkouts, 130 buyers, `buyers_without_view` 29, and rates 0.8543, 0.8088, and 0.4727; the unordered reach counts for the same window (398 customers with a `page_view`, 399 with `add_to_cart`, 397 with `checkout`, 290 with an order) show why reach is not a funnel. In a rolled-back transaction give customer 45, who has no recent `page_view`, an `add_to_cart` 2 days ago and a `checkout` 1 day ago: every count stays the same. Add a `page_view` 3 days ago and the row becomes 399, 341, 276, and 130 with `buyers_without_view` 28, because the September order precedes the new checkout.
--    Hint ladder, rung 1: For sql-59 Exercise 2, run the stage CTEs as plain `SELECT`s for customer 45, who has events but no `page_view` in the window, and see that `viewed_stage` has no row for them, so no later stage can either.
-- 3. Debugging: reconcile stored order totals, calculated line revenue, and
--    payments before choosing which measure each stakeholder KPI should use.
--    Inputs: For sql-59 Exercise 3, start from `orders` and `LEFT JOIN` two order-grain CTEs: `lines`, which sums `quantity * unit_price * (1 - discount)` from `order_items`, and `paid`, which sums `amount` from `payments`; derive `header_minus_lines` and `paid_minus_header` from the three amounts.
--    Expected result/shape: For sql-59 Exercise 3, expected output: exactly 50 rows, `order_id` 1 through 50 in order, one per order. The final columns are `order_id`, `stored_order_total`, `line_revenue`, `paid_amount`, `header_minus_lines`, and `paid_minus_header`; orders 5, 9, 14, 20, 25, 27, 32, 40, 45, and 49 show NULL `paid_amount` and `paid_minus_header`.
--    Verify: For sql-59 Exercise 3, confirm `lines` has 4,362 rows and `paid` has 3,489 rows built from 3,836 payment rows (347 orders have more than one payment), and that the absolute `header_minus_lines` never exceeds 0.0045 across all 4,362 orders. The ten NULL-payment orders are all `placed`. In a rolled-back transaction insert a second 10.00 payment for order 1 (header 240.20): the output stays at 50 rows, `paid` still has 3,489 rows, and order 1 shows `paid_amount` 250.20 and `paid_minus_header` 10.00.
--    Hint ladder, rung 1: For sql-59 Exercise 3, run `lines` and then `paid` alone and compare `COUNT(*)` with `COUNT(DISTINCT order_id)`: 4,362 and 3,489, both unique, so the two `LEFT JOIN`s keep one row per order.
-- 4. Edge case: assign purchases with no qualifying campaign touch to a
--    '(direct)' bucket and prove attribution counts reconcile to purchases.
--    Inputs: For sql-59 Exercise 4, start from `orders` and choose at most one event whose `event_type` is in the declared marketing-touch whitelist (`page_view`, `add_to_cart`, `checkout`), whose campaign metadata is present, and whose timestamp is in the preceding seven-day half-open window.
--    Expected result/shape: For sql-59 Exercise 4, expected output: 6 rows, one per `attribution_bucket`: `(direct)` 2,895, `none` 310, `fall` 305, `spring` 288, `summer` 282, and `winter` 282, summing to 4,362 orders; `none` is a literal campaign value, not a missing one. The final order is `purchases DESC, attribution_bucket`.
--    Verify: For sql-59 Exercise 4, assert that `SUM(purchases)` equals the 4,362 rows of `orders`. Then in a rolled-back transaction use order 31 (customer 5, currently `(direct)`): a `support` event tagged `spring` 1 day before the order changes nothing; adding a `page_view` tagged `fall` 2 days before, a `page_view` tagged `summer` 1 day before, and a `checkout` tagged `winter` also 1 day before but inserted last moves order 31 to `winter`, giving `(direct)` 2,894 and `winter` 283, because the higher `event_id` breaks the timestamp tie.
--    Hint ladder, rung 1: For sql-59 Exercise 4, run the `LATERAL` lookup for order 31 alone and then count the rows leaving the join before grouping: 4,362, one per `order_id`, because `LIMIT 1` returns at most one touch and `ON true` keeps orders with none.
-- 5. Performance: compare the customer/date index with a date/customer index
--    for the date-bounded aggregation; explain the leftmost-column tradeoff.
--    Inputs: For sql-59 Exercise 5, run the 180-day `SUM(total_amount)` per `customer_id` over `orders` with only the customer-leading index, then create `idx_orders_date_customer_day59_solution` on `(order_date, customer_id) INCLUDE (total_amount)` and capture `EXPLAIN (ANALYZE, BUFFERS)` for the same query; check that `pg_class.relallvisible` equals `relpages` (65) for `orders` first, and run `VACUUM orders` if earlier practice writes lowered it.
--    Expected result/shape: For sql-59 Exercise 5, expected output: 410 rows, one per `customer_id`, from 1,538 orders in the window, with the same totals under both indexes. The final columns are `customer_id` and `revenue`.
--    Verify: For sql-59 Exercise 5, save the 410 rows before any index change and compare them afterward. With the customer-leading index alone the plan is a `Seq Scan` over 65 pages; with the date-leading index and a fully visible table it becomes an `Index Only Scan` with `Heap Fetches: 0` touching 11 buffers. A 1,500-day window returns 438 rows from a `Seq Scan` over all 4,362 orders, while `WHERE customer_id = 42 ORDER BY order_date` uses the customer-leading index for 7 rows.
--    Hint ladder, rung 1: For sql-59 Exercise 5, run `SELECT relpages, relallvisible FROM pg_class WHERE relname = 'orders'` before reading any plan; an `Index Only Scan` needs nearly every page marked all-visible, so 65 and 65 is the baseline to compare against.
-- 6. Explanation: write a metric contract for one KPI covering name, grain,
--    numerator, denominator, time zone, NULL policy, exclusions, and owner.
--    Inputs: For sql-59 Exercise 6, write one inline `VALUES` row for `viewer_to_buyer_rate` with `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`, describing the ordered funnel from the headline query.
--    Expected result/shape: For sql-59 Exercise 6, expected output: 1 row, `metric_name` `viewer_to_buyer_rate`. The final columns are `metric_name`, `grain`, `numerator`, `denominator`, `time_window`, `null_policy`, `exclusions`, and `owner`.
--    Verify: For sql-59 Exercise 6, rebuild the KPI from the text alone: the headline funnel gives 130 ordered buyers over 398 viewers, 0.3266, while the solution's numerator wording, "distinct customers with an order", would count 290 customers and give 0.7286, so the numerator text must name the ordered sequence. To test `null_policy`, move the window start to `CURRENT_TIMESTAMP + interval '1 day'` in the headline query: viewers become 0 and `viewer_to_buyer_rate` is NULL.
--    Hint ladder, rung 1: For sql-59 Exercise 6, write the contract next to the headline funnel and copy each column's wording from a clause you can point to: the 90-day `WHERE`, the `NULLIF` on viewers, and the four ordered stage CTEs.
-- 7. Construction: produce a stakeholder-safe product-pair report with support,
--    confidence, lift, minimum basket count, and deterministic ordering.
--    Inputs: For sql-59 Exercise 7, read `order_items` through four CTEs: `baskets` (distinct `order_id`, `product_id`), `totals` (4,362 baskets), `product_baskets` (basket count per product), and `pairs` (a self-join on `order_id` with `a.product_id < b.product_id`); build `together`, `support`, `confidence_a_to_b`, and `lift` from them.
--    Expected result/shape: For sql-59 Exercise 7, expected output: 20 rows, one per (`product_a`, `product_b`) pair. The final columns are `product_a`, `product_b`, `together`, `support`, `confidence_a_to_b`, and `lift`. The final order is `lift DESC, together DESC, product_a, product_b`, and the first four rows tie at lift 63.2174 with together 30: 14/45, 14/258, 31/62, and 31/275.
--    Verify: For sql-59 Exercise 7, confirm `pairs` has 770 rows with the rarest at 15 baskets, so `together >= 2` removes nothing here, and hand-check the top row: 30 × 4,362 / (45 × 46) = 63.2174, where product 14 is in 45 baskets and product 45 in 46. In a rolled-back transaction insert `(order_id, product_id, quantity, unit_price)` = `(238, 14, 1, 10.00)` into `order_items` (order 238 already holds product 14): `order_items` grows to 13,086 rows but `baskets` stays at 13,085 and pair 14/45 stays at 30, while a self-join on raw `order_items` would report 31.
--    Hint ladder, rung 1: For sql-59 Exercise 7, run `baskets`, `totals`, `product_baskets`, and `pairs` one at a time: 13,085 rows, one value of 4,362, 275 products, and 770 pairs, each unique on its key before the final join uses it.
-- 8. Sign-off: assemble one result set that reconciles the customer, finance,
--    funnel, attribution, and market-basket outputs to named control totals.
--    Inputs: For sql-59 Exercise 8, build a control-total result with `UNION ALL`: one labeled row each for the customer count, the order count, the stored order revenue, the line revenue, and the payment total, with every value cast to `numeric`.
--    Expected result/shape: For sql-59 Exercise 8, expected output: 5 rows, one per `control_name`: `customers` 500, `line_revenue` 2355647.12, `orders` 4362, `payments` 1831900.81, and `stored_order_revenue` 2355646.89. The final columns are `control_name` and `observed_value`. The final order is `control_name`.
--    Verify: For sql-59 Exercise 8, confirm that each `observed_value` equals its standalone query, for example `SELECT ROUND(SUM(amount), 2) FROM payments` for `payments`; `stored_order_revenue` is 0.23 lower than `line_revenue` because each order stores its own line total rounded to cents, so record that gap as a known difference rather than a defect.
--    Hint ladder, rung 1: For sql-59 Exercise 8, run each control query alone first and cast it to `numeric`, so every `UNION ALL` branch returns the same column types.
ROLLBACK;
