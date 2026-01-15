-- Day 31: Query Execution Plans (EXPLAIN/ANALYZE)
BEGIN;
SET search_path TO training, public;

-- Baseline query
EXPLAIN SELECT o.order_id, o.total_amount FROM orders o WHERE o.total_amount > 500;
EXPLAIN ANALYZE SELECT o.order_id, o.total_amount FROM orders o WHERE o.total_amount > 500 LIMIT 100;

-- Join with filter
EXPLAIN
SELECT c.country, SUM(oi.quantity) AS qty
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.order_date >= now() - interval '90 days'
GROUP BY c.country
ORDER BY qty DESC;

-- Using an index candidate (to be added on Day 32) and compare
-- Rerun EXPLAIN after creating indexes in Day 32 to observe plan changes.

-- Exercises
-- 1) Add WHERE predicates and observe selectivity effects.
-- 2) Compare EXPLAIN vs EXPLAIN ANALYZE outputs; note actual vs estimated rows.

ROLLBACK;
