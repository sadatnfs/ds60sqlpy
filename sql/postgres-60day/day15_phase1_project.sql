-- Day 15: Phase 1 Project - Complex Report
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Deliver a reconciled Phase 1 report that combines filtering, joins, aggregation, text/time handling, and exact money semantics.
-- Assumptions: All monetary summaries identify stored totals versus computed net line revenue. Reporting month uses UTC and empty populations remain visible where required.
-- Pitfall: Combining fact tables before fixing their grain multiplies measures; every project output must state its row grain and acceptance checks.
-- Predict row grain and NULL/order behavior before executing each example.

-- Customer purchase analysis with segmentation and temporal patterns
WITH line AS (
  SELECT o.customer_id,
         date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
           AS month_utc,
         SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS revenue
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  GROUP BY o.customer_id,
           date_trunc('month', o.order_date AT TIME ZONE 'UTC')::date
),
segment AS (
  SELECT c.customer_id, COALESCE(c.segment,'standard') AS segment, c.country
  FROM customers c
)
SELECT s.segment, s.country, l.month_utc,
       ROUND(SUM(l.revenue),2) AS revenue,
       COUNT(DISTINCT l.customer_id) AS actives,
       ROUND(SUM(l.revenue)/NULLIF(COUNT(DISTINCT l.customer_id),0),2) AS rev_per_active
FROM line l
JOIN segment s ON s.customer_id = l.customer_id
GROUP BY s.segment, s.country, l.month_utc
ORDER BY l.month_utc DESC, revenue DESC, s.segment, s.country
LIMIT 200;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Create a customer performance table with order count, stored revenue, and latest order date, retaining customers with no orders.
--    Hint: Left join from customers and aggregate at customer grain.
-- 2. [Query writing] Create a product profitability table from net order-line revenue and catalog cost.
--    Hint: Calculate line revenue and line cost at item grain, then aggregate to product.
-- 3. [Query writing] Build a UTC monthly order-status report with counts and stored revenue.
--    Hint: Derive one reporting month and group by month/status.
-- 4. [Debugging] Reconcile stored order total, computed line total, and paid total without multiplying details.
--    Hint: Aggregate items and payments independently to order grain before joining.
-- 5. [Prediction] Compare monthly budgets with actual expenses and preserve missing sides.
--    Hint: Aggregate both sources to category/month grain, then full join and keep NULL distinct from a real zero.
-- 6. [Extension] Produce one executive summary row with population, activity, stored revenue, computed revenue, and payments.
--    Hint: Compute independent one-row aggregates, then cross join them to avoid detail multiplication.

ROLLBACK;
