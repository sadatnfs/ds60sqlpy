-- Day 14: Numeric functions & casting
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Choose numeric types and casts from domain precision, validate text before casting, and postpone rounding until presentation.
-- Assumptions: Money is exact `numeric`; division casts denominators to numeric where fractions matter. NULL/zero denominators return NULL through `NULLIF`.
-- Pitfall: Integer division truncates, unsafe text casts abort the statement, and repeated early rounding introduces avoidable error.
-- Predict row grain and NULL/order behavior before executing each example.

-- Rounding and casting
SELECT order_id,
       total_amount,
       round(total_amount, 0) AS rounded,
       cast(total_amount AS int) AS as_int
FROM orders
ORDER BY total_amount DESC, order_id
LIMIT 50;

-- Safe division and null handling
SELECT p.category,
       SUM(oi.quantity) AS qty,
       ROUND(SUM(oi.unit_price*oi.quantity*(1-oi.discount)) / NULLIF(SUM(oi.quantity),0), 2) AS avg_price
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY avg_price DESC, p.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Calculate product gross margin amount and percentage, returning NULL percentage for zero price.
--    Hint: Keep exact numeric arithmetic and guard the denominator with `NULLIF`.
-- 2. [Query writing] Safely cast a set of text values to numeric only when they match a numeric grammar.
--    Hint: Validate with a regex before casting; otherwise return NULL.
-- 3. [Query writing] Show order-item net revenue rounded only after summing.
--    Hint: Aggregate exact line expressions first; round the final display value.
-- 4. [Prediction] Compare integer division with numeric division for 1 divided by 4.
--    Hint: At least one operand must be numeric to preserve the fraction.
-- 5. [Debugging] Calculate average payment amount per paid order without dividing by zero or counting payment rows as orders.
--    Hint: Aggregate payment amount and count distinct order IDs at one common scope.
-- 6. [Extension] Compare sum-of-rounded line values with rounded exact total and quantify the rounding difference.
--    Hint: This diagnostic makes the consequence of early rounding visible.

ROLLBACK;
