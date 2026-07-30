-- Day 9: Correlated Subqueries, EXISTS/IN
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use correlated subqueries for row-specific existence or comparison while keeping correlation keys and NULL behavior explicit.
-- Assumptions: `EXISTS` tests whether at least one row qualifies and ignores selected values. `NOT EXISTS` remains safe when inner columns can be NULL.
-- Pitfall: A correlated subquery can run conceptually per outer row; do not use it when a join or pre-aggregation states the grain more clearly.
-- Predict row grain and NULL/order behavior before executing each example.

-- EXISTS: customers who purchased Electronics
SELECT c.*
FROM customers c
WHERE EXISTS (
  SELECT 1
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.order_id
  JOIN products p ON p.product_id = oi.product_id
  WHERE o.customer_id = c.customer_id
    AND p.category = 'Electronics'
)
ORDER BY c.customer_id;

-- IN with correlated condition
SELECT p.product_id, p.name
FROM products p
WHERE p.product_id IN (
  SELECT DISTINCT oi.product_id
  FROM order_items oi
  JOIN orders o ON o.order_id = oi.order_id
  WHERE o.order_date >= now() - interval '30 days'
)
ORDER BY p.product_id;

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] Return customers who have at least one delivered order.
--    Hint: `EXISTS` expresses the yes/no question without multiplying customer rows.
-- 2. [Query writing] Return products that have never been sold.
--    Hint: `NOT EXISTS` correlates on product ID and is not confused by NULL membership.
-- 3. [Query writing] Return each customer's orders that are above that customer's average order total.
--    Hint: Correlate the average to the current order's customer, not to the current order ID.
-- 4. [Prediction] Explain and avoid the `NOT IN` plus NULL trap by finding customers without orders using `NOT EXISTS`.
--    Hint: Correlate on the customer key; a matching row alone determines exclusion.
-- 5. [Debugging] Return only each customer's most recent order without an arbitrary `LIMIT 1`.
--    Hint: Compare to the correlated `MAX(order_date)` and break timestamp ties with the maximum ID at that timestamp.
-- 6. [Extension] Return customers for whom every order has at least one payment, excluding customers with no orders.
--    Hint: Require an order to exist, then prove no order lacks a payment using double `NOT EXISTS`.

ROLLBACK;
