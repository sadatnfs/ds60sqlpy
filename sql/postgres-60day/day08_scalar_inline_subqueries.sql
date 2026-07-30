-- Day 8: Scalar & Inline Subqueries
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use scalar and inline subqueries only when their one-row or one-value cardinality is guaranteed and visible.
-- Assumptions: A scalar subquery returning no rows becomes NULL; more than one row is an error. Order a `LIMIT 1` subquery deterministically.
-- Pitfall: Adding `LIMIT 1` to hide an unintended multi-row result creates arbitrary logic unless `ORDER BY` defines the chosen row.
-- Predict row grain and NULL/order behavior before executing each example.

-- Scalar subquery in SELECT: customer lifetime revenue
SELECT c.customer_id, c.full_name,
  (
    SELECT ROUND(COALESCE(SUM(oi.unit_price * oi.quantity * (1 - oi.discount)),0),2)
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.customer_id = c.customer_id
  ) AS lifetime_revenue
FROM customers c
ORDER BY lifetime_revenue DESC, c.customer_id
LIMIT 20;

-- Inline subquery in FROM
SELECT x.category, ROUND(AVG(x.order_total),2) AS avg_order_total
FROM (
  SELECT p.category, o.order_id, SUM(oi.unit_price*oi.quantity*(1-oi.discount)) AS order_total
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  GROUP BY p.category, o.order_id
) x
GROUP BY x.category
ORDER BY avg_order_total DESC, x.category;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return orders whose total exceeds the overall average order total.
--    Hint: The aggregate subquery is guaranteed to return exactly one value.
-- 2. [Query writing] Add the total customer count as a scalar column beside each country-level customer count.
--    Hint: An uncorrelated aggregate subquery is one row and repeats safely for each grouped output row.
-- 3. [Query writing] Show each customer with their latest order timestamp using a scalar correlated subquery.
--    Hint: Use `MAX` to guarantee one result and let customers without orders receive NULL.
-- 4. [Prediction] Demonstrate that a scalar subquery with no matching rows returns NULL.
--    Hint: Use a deliberately impossible product key and test the scalar result with `IS NULL`.
-- 5. [Debugging] Repair a scalar subquery that returns many product prices by aggregating to the intended single value.
--    Hint: Choose the business reduction explicitly; this answer uses maximum price.
-- 6. [Extension] Rewrite a repeated scalar aggregate as a one-row CTE crossed into a customer-country report.
--    Hint: Compute the global total once, then cross join the guaranteed one-row relation.

ROLLBACK;
