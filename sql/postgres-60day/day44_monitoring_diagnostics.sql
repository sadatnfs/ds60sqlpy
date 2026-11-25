-- Day 44: Monitoring & Diagnostics
-- BEGINNER WORKFLOW - sql-44: Monitoring Diagnostics
-- Guide: sql/postgres-60day/companion-guides/day44_monitoring_diagnostics.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-44.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
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
SELECT
  pid,
  usename,
  datname,
  state,
  query_start,
  NOW() - query_start AS running_for,
  left (query,
    120) AS query
FROM
  pg_stat_activity
WHERE
  state <> 'idle'
ORDER BY
  running_for DESC
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
SELECT
  p.category,
  SUM(oi.quantity) AS qty
FROM
  order_items oi
  JOIN products p ON p.product_id = oi.product_id
  JOIN orders o ON o.order_id = oi.order_id
WHERE
  o.order_date >= now() - interval '180 days'
GROUP BY
  p.category
ORDER BY
  qty DESC;

-- Exercises
-- 1. Identify the longest-running active queries on your system.
--    Inputs: For sql-44 Exercise 1, read `pg_stat_activity` once, keep backends with `state = 'active'` other than `pg_backend_pid()`, and compute `runtime` as `clock_timestamp() - query_start`, so the age is measured at read time rather than at the start of the lesson transaction; show `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`.
--    Expected result/shape: For sql-44 Exercise 1, expected output: zero or more currently active sessions, excluding the monitoring query itself. A long runtime can be normal; inspect wait events, locks, and the operation's purpose before intervening. The final columns are `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`. The final order is `runtime DESC NULLS LAST`.
--    Verify: For sql-44 Exercise 1, on a quiet server confirm 0 rows while `SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND pid = pg_backend_pid()` returns 1, which proves the self-exclusion works; then, from a second `psql` session, run `BEGIN; SELECT pg_sleep(1); SELECT pg_sleep(6);` and while it sleeps confirm exactly one row with a unique `pid`, `wait_event` `PgSleep`, `query` `SELECT pg_sleep(6);`, and a `runtime` that counts only the current statement, not the earlier one-second sleep; rerun after it finishes and confirm the row is gone. Do not cancel or terminate the session.
--    Hint ladder, rung 1: For sql-44 Exercise 1, run the `WHERE` filter without the `pid` test first and confirm your own session is the one active row; then add `pid <> pg_backend_pid()` and check `runtime DESC NULLS LAST`. There is no row cap.
-- 2. If pg_stat_statements is available, list top 10 queries by mean_exec_time and total time.
--    Inputs: For sql-44 Exercise 2, inspect `to_regclass('public.pg_stat_statements')`, then read the optional `public.pg_stat_statements` view into the course-owned temporary `top_statement_stats` table. Build `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`; do not install the extension or reset shared statistics.
--    Expected result/shape: For sql-44 Exercise 2, expected output: up to 20 rows when `pg_stat_statements` is installed and loaded, with at most 10 rows per ranking label (`total_exec_time` and `mean_exec_time`); otherwise emit an explanatory notice and return an empty result. Each row is one statement within a ranking, identified by (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`). The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
--    Verify: For sql-44 Exercise 2, if the optional view is absent or raises `object_not_in_prerequisite_state` because the module was not preloaded, require an explanatory notice and an empty result. If it is readable, require only the `total_exec_time` and `mean_exec_time` labels, at most 10 rows per label, unique (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), consecutive `rank_position` values from 1 through N, nonincreasing `total_exec_time` order for its label, nonincreasing `mean_exec_time` order for its label, and values that match a fresh read of `public.pg_stat_statements`.
--    Hint ladder, rung 1: For sql-44 Exercise 2, first prove whether the optional view exists. Then rank the same snapshot twice with deterministic tie-breakers and keep the monitored statistics unchanged.
-- 3. Prediction: explain why query_start is not the same as transaction start,
--    then display both ages for non-idle sessions.
--    Inputs: For sql-44 Exercise 3, read `pg_stat_activity` once, drop this session with `pid <> pg_backend_pid()` and idle sessions with `state <> 'idle'` (which also drops background processes, whose `state` is `NULL`), and compute `transaction_age` from `xact_start` and `statement_age` from `query_start`, both against `clock_timestamp()`.
--    Expected result/shape: For sql-44 Exercise 3, expected output: one row per `pid` for other non-idle client sessions, which is 0 rows on a quiet server; an open transaction shows a `transaction_age` at least as large as its `statement_age`, and an aborted transaction shows a `NULL` `transaction_age` and sorts last. The final columns are `pid`, `usename`, `state`, `transaction_age`, and `statement_age`. The final order is `transaction_age DESC NULLS LAST`.
--    Verify: For sql-44 Exercise 3, open three controlled sessions: `BEGIN; SELECT pg_sleep(1); SELECT pg_sleep(6);`, `BEGIN; SELECT 1;` left open, and `BEGIN; SELECT 1/0;` left open; confirm three rows with unique `pid`, the sleeper's `transaction_age` about one second above its `statement_age`, the open `SELECT 1` session with both ages almost equal, and the aborted session in state `idle in transaction (aborted)` with a `NULL` `transaction_age`. Check clock order with `xact_start <= query_start`, not `transaction_age >= statement_age`, because the two `clock_timestamp()` reads can make an autocommit statement's age one microsecond larger. Finish each session with `ROLLBACK`.
--    Hint ladder, rung 1: For sql-44 Exercise 3, select `xact_start` and `query_start` side by side before computing ages; a session in a multi-statement transaction shows the earlier `xact_start`. Then check `transaction_age DESC NULLS LAST`.
-- 4. Construction: summarize current connections by database, user, and state
--    without exposing complete SQL text.
--    Inputs: For sql-44 Exercise 4, read `pg_stat_activity` once and group by `datname`, `usename`, and `state` with `COUNT(*) AS connections`, leaving out `query` so no statement text is exposed; background processes have `NULL` in some or all of the three key columns and form their own groups.
--    Expected result/shape: For sql-44 Exercise 4, expected output: one row per `datname`, `usename`, and `state`. The final columns are `datname`, `usename`, `state`, and `connections`. The final order is `datname, usename, state`.
--    Verify: For sql-44 Exercise 4, on a quiet container confirm three groups that sum to 6 and match `SELECT count(*) FROM pg_stat_activity` (6): (`advanced_sql_training`, `postgres`, `active`) with 1, which is this query itself, (`NULL`, `postgres`, `NULL`) with 1 for the logical replication launcher, and an all-`NULL` group with 4 for the checkpointer, background writer, WAL writer, and autovacuum launcher; then open one sleeping session, one open `BEGIN; SELECT 1;` session, and one aborted transaction and confirm five groups summing to 9, with `active` at 2 and separate `idle in transaction` and `idle in transaction (aborted)` rows of 1 connection each.
--    Hint ladder, rung 1: For sql-44 Exercise 4, confirm the groups are `datname`, `usename`, and `state`, then compare `SUM(connections)` with `count(*)` from `pg_stat_activity`; there is no row cap, and the `NULL` groups sort last.
-- 5. Debugging: repair a “slow query” report that sorts only by mean time even
--    though one rarely executed outlier should not outrank total workload cost.
--    Inputs: For sql-44 Exercise 5, read the temporary `top_statement_stats` table that Exercise 2 filled with up to 10 `total_exec_time` rows and up to 10 `mean_exec_time` rows from `pg_stat_statements` (0 rows and a NOTICE when the extension is not loaded, as on the course container), without resetting the monitored server statistics, and select `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time` so each list keeps its full statement key.
--    Expected result/shape: For sql-44 Exercise 5, expected output: one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), so each ranking label can contain multiple statements. The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
--    Verify: For sql-44 Exercise 5, require one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`) and compare `rank_position`, `query`, `calls`, `mean_exec_time`, and `total_exec_time` with `top_statement_stats`. When the optional source is available, require both ranking labels, at most 10 rows per label, consecutive `rank_position` values, `total_exec_time` order for that ranking, and `mean_exec_time` order for that ranking; `ranking` alone is deliberately non-unique.
--    Hint ladder, rung 1: For sql-44 Exercise 5, compare statements only within the ranking that produced them, and use `rank_position` rather than re-sorting both lists by one metric.
-- 6. Edge case: identify sessions that are idle in transaction and explain why
--    they can retain locks or old snapshots even while no statement is running.
--    Inputs: For sql-44 Exercise 6, read `pg_stat_activity` once, keep only `state = 'idle in transaction'` (an equality test, so `idle in transaction (aborted)` is excluded), and compute `transaction_age` as `clock_timestamp() - xact_start`; show `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`.
--    Expected result/shape: For sql-44 Exercise 6, expected output: one row per `pid` whose state is `idle in transaction`. The final columns are `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`. The final order is `transaction_age DESC NULLS LAST`.
--    Verify: For sql-44 Exercise 6, confirm 0 rows on a quiet server; then open a second `psql` session, run `BEGIN; SELECT 1;`, and leave it open: confirm exactly one row with a unique `pid`, `wait_event_type` `Client`, `wait_event` `ClientRead`, and a growing `transaction_age`, while an aborted session (`BEGIN; SELECT 1/0;`) does not appear; run `ROLLBACK` in the open session and confirm the row disappears. Do not cancel or terminate the session.
--    Hint ladder, rung 1: For sql-44 Exercise 6, list the distinct `state` values first so you can see why `idle in transaction (aborted)` is a separate string; then check `transaction_age DESC NULLS LAST`.
ROLLBACK;
