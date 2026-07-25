-- Day 44 solutions: monitoring and diagnostics
BEGIN;
SET search_path TO training, public;

-- Exercise 1: longest-running active statements, excluding this session.
SELECT pid,
       usename,
       datname,
       state,
       clock_timestamp() - query_start AS runtime,
       wait_event_type,
       wait_event,
       left(query, 160) AS query
FROM pg_stat_activity
WHERE state = 'active'
  AND pid <> pg_backend_pid()
ORDER BY runtime DESC NULLS LAST;

-- Exercise 2: pg_stat_statements is optional. Dynamic SQL keeps this file
-- runnable when the extension is not installed.
CREATE TEMP TABLE top_statement_stats (
  ranking text,
  query text,
  calls bigint,
  mean_exec_time double precision,
  total_exec_time double precision
);

DO $optional_pg_stat_statements$
BEGIN
  IF to_regclass('public.pg_stat_statements') IS NOT NULL THEN
    EXECUTE $by_total$
      INSERT INTO top_statement_stats
      SELECT 'total_exec_time', left(query, 200), calls, mean_exec_time, total_exec_time
      FROM public.pg_stat_statements
      ORDER BY total_exec_time DESC
      LIMIT 10
    $by_total$;
    EXECUTE $by_mean$
      INSERT INTO top_statement_stats
      SELECT 'mean_exec_time', left(query, 200), calls, mean_exec_time, total_exec_time
      FROM public.pg_stat_statements
      ORDER BY mean_exec_time DESC
      LIMIT 10
    $by_mean$;
  ELSE
    RAISE NOTICE 'pg_stat_statements is not installed; optional result is empty';
  END IF;
END
$optional_pg_stat_statements$;

SELECT *
FROM top_statement_stats
ORDER BY ranking, total_exec_time DESC;

ROLLBACK;
