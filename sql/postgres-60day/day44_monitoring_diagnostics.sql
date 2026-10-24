-- Day 44: Monitoring & Diagnostics
-- BEGINNER WORKFLOW — sql-44: Monitoring Diagnostics
-- Guide: sql/postgres-60day/companion-guides/day44_monitoring_diagnostics.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-44/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: order_items, products, orders.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Active sessions
SELECT pid, usename, datname, state, query_start, NOW() - query_start AS running_for, left(query, 120) AS query
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY running_for DESC
LIMIT 20;

-- pg_stat_statements has three relevant states:
--   1. absent: its view does not exist;
--   2. installed but unusable: the view exists, but the server was not started
--      with pg_stat_statements in shared_preload_libraries;
--   3. installed and loaded: the view is readable.
-- Treat the first two as an explained empty optional result. Do not install the
-- extension or change server startup settings from this monitoring lesson.
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
-- 1. Identify the longest-running active queries on your system.
--    Inputs: For sql-44 Exercise 1, take a read-only snapshot of `pg_stat_activity`. Build the answer toward `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`; keep `pid` visible because the output grain is one backend session.
--    Expected result/shape: For sql-44 Exercise 1, expected output: zero or more currently active sessions, excluding the monitoring query itself. A long runtime can be normal; inspect wait events, locks, and the operation's purpose before intervening. The final columns are `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`. The final order is `runtime DESC NULLS LAST`.
--    Verify: For sql-44 Exercise 1, run an anti-check that counts rows where NOT (`state = 'active' AND pid <> pg_backend_pid()`); require unique `pid` and compare the projected `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query` with a second read-only snapshot of `pg_stat_activity`. When practical, open a controlled second `psql` session that runs `SELECT pg_sleep(...)`, observe it as active, then confirm it disappears after the statement finishes; do not cancel or terminate a session as part of this exercise.
--    Hint ladder, rung 1: For sql-44 Exercise 1, inspect the source keys that survive `WHERE`; then check `runtime DESC NULLS LAST` before applying the row cap.
-- 2. If pg_stat_statements is available, list top 10 queries by mean_exec_time and total time.
--    Inputs: For sql-44 Exercise 2, inspect `to_regclass('public.pg_stat_statements')`, then read the optional `public.pg_stat_statements` view into the course-owned temporary `top_statement_stats` table. Build `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`; do not install the extension or reset shared statistics.
--    Expected result/shape: For sql-44 Exercise 2, expected output: up to 20 rows when `pg_stat_statements` is installed and loaded, with at most 10 rows per ranking label (`total_exec_time` and `mean_exec_time`); otherwise emit an explanatory notice and return an empty result. Each row is one statement within a ranking, identified by (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`). The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
--    Verify: For sql-44 Exercise 2, if the optional view is absent or raises `object_not_in_prerequisite_state` because the module was not preloaded, require an explanatory notice and an empty result. If it is readable, require only the `total_exec_time` and `mean_exec_time` labels, at most 10 rows per label, unique (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), consecutive `rank_position` values from 1 through N, nonincreasing `total_exec_time` order for its label, nonincreasing `mean_exec_time` order for its label, and values that match a fresh read of `public.pg_stat_statements`.
--    Hint ladder, rung 1: For sql-44 Exercise 2, first prove whether the optional view exists. Then rank the same snapshot twice with deterministic tie-breakers and keep the monitored statistics unchanged.
-- 3. Prediction: explain why query_start is not the same as transaction start,
--    then display both ages for non-idle sessions.
--    Inputs: For sql-44 Exercise 3, take a read-only snapshot of `pg_stat_activity`. Build the answer toward `pid`, `usename`, `state`, `transaction_age`, and `statement_age`; keep `pid` visible because the output grain is one backend session.
--    Expected result/shape: For sql-44 Exercise 3, expected output: one row per `pid`. The final columns are `pid`, `usename`, `state`, `transaction_age`, and `statement_age`. The final order is `transaction_age DESC NULLS LAST`.
--    Verify: For sql-44 Exercise 3, run an anti-check that counts rows where NOT (`pid <> pg_backend_pid() AND state <> 'idle'`); require unique `pid` and compare `pid`, `usename`, `state`, `transaction_age`, and `statement_age` with `pg_stat_activity`. Require nonnegative ages for non-NULL timestamps and `transaction_age >= statement_age` when both exist. When practical, use a controlled second `psql` session with `BEGIN`, wait, and then a long-running query to observe both clocks; finish that session with `ROLLBACK`.
--    Hint ladder, rung 1: For sql-44 Exercise 3, inspect the source keys that survive `WHERE`; then check `transaction_age DESC NULLS LAST` before applying the row cap.
-- 4. Construction: summarize current connections by database, user, and state
--    without exposing complete SQL text.
--    Inputs: For sql-44 Exercise 4, take a read-only snapshot of `pg_stat_activity`. Group by `datname`, `usename`, and `state`, and calculate `connections`; keep the complete three-column group key visible.
--    Expected result/shape: For sql-44 Exercise 4, expected output: one row per `datname`, `usename`, and `state`. The final columns are `datname`, `usename`, `state`, and `connections`. The final order is `datname, usename, state`.
--    Verify: For sql-44 Exercise 4, independently aggregate `pg_stat_activity` by `datname`, `usename`, and `state`; require one output row for every distinct tuple and compare `connections` tuple by tuple, using `IS NOT DISTINCT FROM` when matching nullable catalog values. Also require `SUM(connections)` to equal `COUNT(*)` from the same source snapshot and require the output tuples to be unique.
--    Hint ladder, rung 1: For sql-44 Exercise 4, confirm the groups are `datname`, `usename`, and `state`; then check `datname, usename, state` before applying the row cap.
-- 5. Debugging: repair a “slow query” report that sorts only by mean time even
--    though one rarely executed outlier should not outrank total workload cost.
--    Inputs: For sql-44 Exercise 5, read the course-owned temporary `top_statement_stats` table without changing the monitored server statistics. Build the answer toward `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`; keep the complete statement-within-ranking key visible.
--    Expected result/shape: For sql-44 Exercise 5, expected output: one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), so each ranking label can contain multiple statements. The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
--    Verify: For sql-44 Exercise 5, require one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`) and compare `rank_position`, `query`, `calls`, `mean_exec_time`, and `total_exec_time` with `top_statement_stats`. When the optional source is available, require both ranking labels, at most 10 rows per label, consecutive `rank_position` values, `total_exec_time` order for that ranking, and `mean_exec_time` order for that ranking; `ranking` alone is deliberately non-unique.
--    Hint ladder, rung 1: For sql-44 Exercise 5, compare statements only within the ranking that produced them, and use `rank_position` rather than re-sorting both lists by one metric.
-- 6. Edge case: identify sessions that are idle in transaction and explain why
--    they can retain locks or old snapshots even while no statement is running.
--    Inputs: For sql-44 Exercise 6, take a read-only snapshot of `pg_stat_activity`. Build the answer toward `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`; keep `pid` visible because the output grain is one backend session.
--    Expected result/shape: For sql-44 Exercise 6, expected output: one row per `pid` whose state is `idle in transaction`. The final columns are `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`. The final order is `transaction_age DESC NULLS LAST`.
--    Verify: For sql-44 Exercise 6, run an anti-check for any row whose state is not `idle in transaction`; require unique `pid`, non-NULL transaction starts, and nonnegative `transaction_age`, and compare every projected value with `pg_stat_activity`. When practical, open a controlled second `psql` session, run `BEGIN`, wait without committing, observe the session, then run `ROLLBACK` and confirm that it disappears from this result.
--    Hint ladder, rung 1: For sql-44 Exercise 6, inspect the source keys that survive `WHERE`; then check `transaction_age DESC NULLS LAST` before applying the row cap.

ROLLBACK;
