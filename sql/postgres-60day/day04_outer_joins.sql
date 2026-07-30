-- Day 4: LEFT/RIGHT/FULL OUTER JOINs and NULL handling
BEGIN;
SET search_path TO training, public;

-- Study contract
-- Focus: Use outer joins to preserve a declared side and make absence visible without accidentally filtering it away.
-- Assumptions: Missing matches appear as NULL-extended columns. Decide whether absence means zero, unknown, or an exception before applying `COALESCE`.
-- Pitfall: A right-side predicate in `WHERE` can turn a left join into an inner join; put match-qualification predicates in `ON` when unmatched left rows must remain.
-- Predict row grain and NULL/order behavior before executing each example.

-- LEFT JOIN: customers without orders
SELECT c.customer_id, c.full_name, COUNT(o.order_id) AS orders
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.full_name
ORDER BY orders ASC, c.customer_id
LIMIT 25;

-- RIGHT JOIN: products that appear in orders (or not)
SELECT p.product_id, p.name, COALESCE(SUM(oi.quantity),0) AS sold_qty
FROM order_items oi
RIGHT JOIN products p ON p.product_id = oi.product_id
GROUP BY p.product_id, p.name
ORDER BY sold_qty ASC, p.product_id
LIMIT 25;

-- FULL OUTER JOIN: payments vs orders.
-- A payment foreign key prevents an orphan payment in this dataset, while an
-- order may legitimately have no payment. Keep both keys visible when auditing.
SELECT o.order_id,
       p.payment_id,
       p.order_id AS payment_order_id,
       o.total_amount,
       p.amount AS payment_amount
FROM orders o
FULL OUTER JOIN payments p ON p.order_id = o.order_id
WHERE o.order_id IS NULL OR p.order_id IS NULL
ORDER BY COALESCE(o.order_id, p.order_id), p.payment_id; -- mismatches

-- Exercises
-- Work prediction -> query writing -> debugging -> extension in order.
-- Keep answers in your own scratch file; this learner script remains answer-free.
-- 1. [Query writing] List every customer with order count, including customers with zero orders.
--    Hint: Start from customers, left join orders, and count the nullable order key rather than `COUNT(*)`.
-- 2. [Query writing] Find products that have never appeared in an order item.
--    Hint: Left join and retain rows where the right-side primary key is NULL.
-- 3. [Query writing] Compare monthly budgets and expenses by category with a full outer join.
--    Hint: Aggregate each side to the same category/month grain before joining; preserve keys from either side.
-- 4. [Prediction] Preserve every customer while counting only delivered orders; compare a status predicate in `ON` with the same predicate in `WHERE`.
--    Hint: Place `o.status = 'delivered'` in `ON`; `WHERE` would remove NULL-extended customers.
-- 5. [Debugging] Repair `COUNT(*)` in a left-join order count so customers without orders report zero rather than one.
--    Hint: Count a non-nullable right-side key that becomes NULL for an unmatched row.
-- 6. [Extension] Reconcile product/order-item coverage as matched products, unsold products, and orphan item product keys.
--    Hint: Use a full join and conditional distinct counts; the foreign key should make right-only product IDs zero.

ROLLBACK;
