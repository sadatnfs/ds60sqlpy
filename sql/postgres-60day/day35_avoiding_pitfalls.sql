-- Day 35: Avoiding Common Performance Pitfalls
BEGIN;
SET search_path TO training, public;

-- Pitfall: function on column prevents index usage
EXPLAIN ANALYZE SELECT * FROM orders WHERE date_trunc('day', order_date) = date_trunc('day', now());
-- Better:
EXPLAIN ANALYZE SELECT * FROM orders WHERE order_date >= date_trunc('day', now()) AND order_date < date_trunc('day', now()) + interval '1 day';

-- Pitfall: Correlated subquery per row
EXPLAIN ANALYZE
SELECT c.customer_id,
       (SELECT SUM(o.total_amount) FROM orders o WHERE o.customer_id = c.customer_id)
FROM customers c;
-- Better: pre-aggregate and join
EXPLAIN ANALYZE
WITH agg AS (
  SELECT customer_id, SUM(total_amount) AS sum_total FROM orders GROUP BY customer_id
)
SELECT c.customer_id, a.sum_total
FROM customers c LEFT JOIN agg a ON a.customer_id = c.customer_id;

-- N+1 pattern in application layer (illustrated only)
-- Prefer set-based queries over per-row queries.

-- Exercises
-- 1) Rewrite 3 queries to avoid functions on indexed columns.
-- 2) Replace correlated subqueries with joins/CTEs.

ROLLBACK;
