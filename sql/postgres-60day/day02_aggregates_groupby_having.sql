-- Day 2: Aggregates, GROUP BY, HAVING
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Aggregate rows only after naming the grouping grain, then filter groups with `HAVING` and preserve numeric meaning.
-- Assumptions: Money columns are exact `numeric`; round only presentation values. `COUNT(column)` excludes NULL while `COUNT(*)` counts rows.
-- Pitfall: Selecting a non-grouped, non-aggregated column or using `WHERE` for an aggregate condition changes or invalidates the question.
-- Predict row grain and NULL/order behavior before executing each example.

-- Example 1: Orders per country
SELECT c.country, COUNT(*) AS customers
FROM customers c
GROUP BY c.country
ORDER BY customers DESC, c.country;

-- Example 2: Revenue by category with HAVING
SELECT p.category, ROUND(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),2) AS revenue
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
HAVING SUM(oi.unit_price * oi.quantity) > 10000
ORDER BY revenue DESC, p.category;

-- Example 3: Monthly orders and average order total
SELECT date_trunc('month', o.order_date) AS month,
       COUNT(*) AS orders,
       ROUND(AVG(o.total_amount),2) AS avg_order
FROM orders o
GROUP BY month
ORDER BY month DESC;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Count customers by country and order countries by count then country.
--    Hint: The output grain is one row per country; include a deterministic secondary sort.
-- 2. [Query writing] Calculate net revenue and average unit price by product category, keeping categories above 100,000 in revenue.
--    Hint: Join at line grain, aggregate once per category, and place the aggregate predicate in `HAVING`.
-- 3. [Query writing] Summarize order count and average total by status, retaining statuses with at least 100 orders.
--    Hint: Filter groups after aggregation with `HAVING COUNT(*)`.
-- 4. [Prediction] Show `COUNT(*)`, `COUNT(email)`, and missing-email count together; predict their relationship.
--    Hint: `COUNT(email)` ignores NULL, while a filtered count makes missingness explicit.
-- 5. [Debugging] Repair a query that tries to filter `SUM(amount)` in `WHERE` by moving the aggregate condition to the correct clause.
--    Hint: `WHERE` filters expense rows before grouping; `HAVING` filters category groups afterward.
-- 6. [Extension] Produce monthly order count, total revenue, and returned-order count for the last 12 complete or partial months.
--    Hint: Group by a month expression, use conditional aggregation, and keep the timestamp predicate sargable.

ROLLBACK;
