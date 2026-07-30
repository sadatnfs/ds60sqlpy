-- Day 11: CASE expressions and conditional logic
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use `CASE` to encode mutually exclusive business rules in deliberate order while preserving NULL as a distinct state when required.
-- Assumptions: Searched `CASE` uses first-match wins. Status/category labels are illustrative course rules, not universal business definitions.
-- Pitfall: Overlapping broad conditions placed first make later branches unreachable; an omitted `ELSE` produces NULL.
-- Predict row grain and NULL/order behavior before executing each example.

-- Label orders by size
SELECT o.order_id, o.total_amount,
  CASE
    WHEN o.total_amount >= 1000 THEN 'XL'
    WHEN o.total_amount >= 300 THEN 'L'
    WHEN o.total_amount >= 100 THEN 'M'
    ELSE 'S'
  END AS order_size
FROM orders o
ORDER BY o.total_amount DESC, o.order_id
LIMIT 50;

-- Conditional aggregation with CASE
SELECT p.category,
  SUM(CASE WHEN o.order_date >= now() - interval '30 days' THEN oi.quantity ELSE 0 END) AS qty_30d,
  SUM(CASE WHEN o.order_date >= now() - interval '90 days' THEN oi.quantity ELSE 0 END) AS qty_90d
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY qty_30d DESC, p.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Classify orders as small, medium, or large by total amount.
--    Hint: Validate boundaries and place the highest threshold first.
-- 2. [Query writing] Count order statuses in paid-like, open, returned, and other buckets with conditional aggregation.
--    Hint: Each `COUNT(*) FILTER` or `SUM(CASE...)` should state its denominator.
-- 3. [Query writing] Label missing customer segments separately from known segment values.
--    Hint: Test `IS NULL` before comparing text values.
-- 4. [Prediction] Predict the label for 500 when `>= 100` appears before `>= 500`, then repair the branch order.
--    Hint: First-match wins, so specific/high thresholds must precede broader/lower ones.
-- 5. [Debugging] Replace a CASE expression that returns mixed numeric and text types with one consistent output type.
--    Hint: All result branches must resolve to a compatible PostgreSQL type.
-- 6. [Extension] Create payment-method display labels and preserve unknown future methods with an explicit fallback.
--    Hint: A simple CASE fits equality mapping; `ELSE` prevents silent NULL labels.

ROLLBACK;
