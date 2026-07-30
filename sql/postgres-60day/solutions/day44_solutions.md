# Day 44 Solutions — Monitoring and Diagnostics

The two deliverables inspect active work and, when available,
`pg_stat_statements`. The solution remains runnable on a fresh PostgreSQL
installation where that optional extension is absent. See
[`day44_solutions.sql`](day44_solutions.sql).

## Exercise 1 — Longest-running active statements

```sql
SET search_path TO training, public;

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
```

Expected shape: zero or more currently active sessions, excluding the
monitoring query itself. A long runtime can be normal; inspect wait events,
locks, and the operation's purpose before intervening.

## Exercise 2 — Optional top statement statistics

```sql
BEGIN;
SET search_path TO training, public;

CREATE TEMP TABLE top_statement_stats (
  query text,
  calls bigint,
  mean_exec_time double precision,
  total_exec_time double precision
);

DO $optional_pg_stat_statements$
BEGIN
  IF to_regclass('public.pg_stat_statements') IS NOT NULL THEN
    EXECUTE $query$
      INSERT INTO top_statement_stats
      SELECT left(query, 200), calls, mean_exec_time, total_exec_time
      FROM public.pg_stat_statements
      ORDER BY total_exec_time DESC
      LIMIT 10
    $query$;
  ELSE
    RAISE NOTICE 'pg_stat_statements is not installed; optional result is empty';
  END IF;
END
$optional_pg_stat_statements$;

SELECT *
FROM top_statement_stats
ORDER BY total_exec_time DESC;

ROLLBACK;
```

Expected shape: up to ten rows when `pg_stat_statements` is installed and
loaded; otherwise an explanatory notice and an empty result.

## Reasoning, safety, and pitfalls

- `state = 'active'` is more precise than `state <> 'idle'` for the requested
  active-query list.
- `clock_timestamp()` advances during the statement and is appropriate for an
  observed runtime.
- Checking `to_regclass` avoids a parse-time reference to a missing extension
  view; dynamic SQL defers that reference until the view is known to exist.
- These are diagnostic reads. Do not cancel or terminate sessions without
  confirming ownership and operational impact.

## Exercise 3 — Separate query and transaction age

`query_start` belongs to the current statement; `xact_start` belongs to its
transaction. The latter can reveal long-lived snapshots hidden behind a short
or currently idle statement.

## Exercise 4 — Summarize connections safely

Grouping by database, user, and state supports capacity triage without exposing
complete SQL text in a broadly shared report.

## Exercise 5 — Retain mean and total workload views

Mean duration highlights individually expensive calls; total execution time
highlights cumulative cost. The answer keeps both rather than declaring one
universal “slow query” ranking.

## Exercise 6 — Identify idle-in-transaction sessions

The read-only diagnostic returns age and wait fields. It does not cancel a
backend; ownership and operational impact must be confirmed first.
