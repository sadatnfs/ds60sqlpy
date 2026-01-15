-- Day 44: Monitoring & Diagnostics
BEGIN;
SET search_path TO training, public;

-- Active sessions
SELECT pid, usename, datname, state, query_start, NOW() - query_start AS running_for, left(query, 120) AS query
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY running_for DESC
LIMIT 20;

-- If pg_stat_statements is enabled (recommended), inspect top queries
-- Note: enabling requires CREATE EXTENSION pg_stat_statements; (may need superuser)
-- SELECT queryid, calls, total_exec_time, mean_exec_time, rows, left(query, 120) AS q
-- FROM pg_stat_statements
-- ORDER BY total_exec_time DESC
-- LIMIT 20;

-- Slow queries from logs are an ops topic; here we simulate using EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT p.category, SUM(oi.quantity) AS qty
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_date >= now() - interval '180 days'
GROUP BY p.category
ORDER BY qty DESC;

-- Exercises
-- 1) Identify the longest-running active queries on your system.
-- 2) If pg_stat_statements is available, list top 10 queries by mean_exec_time and total time.

ROLLBACK;
