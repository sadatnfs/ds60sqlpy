# Day 44 Solutions — Monitoring and Diagnostics


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day44_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day44_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Wait event, Backend PID, Normalized statement. Its worked-model focus is:
Query pgstatactivity, exclude pgbackendpid(), and calculate runtime only for active statements. For one row, read user, state, wait type/event, and query together; a long duration alone does not prove a fault or authorize termination.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 1, take a read-only snapshot of `pg_stat_activity`. Build the answer toward `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`; keep `pid` visible because the output grain is one backend session.
- **Expected result/shape:** For sql-44 Exercise 1, expected output: zero or more currently active sessions, excluding the monitoring query itself. A long runtime can be normal; inspect wait events, locks, and the operation's purpose before intervening. The final columns are `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`. The final order is `runtime DESC NULLS LAST`.
- **Independent verification:** For sql-44 Exercise 1, run an anti-check that counts rows where NOT (`state = 'active' AND pid <> pg_backend_pid()`); require unique `pid` and compare the projected `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query` with a second read-only snapshot of `pg_stat_activity`. When practical, open a controlled second `psql` session that runs `SELECT pg_sleep(...)`, observe it as active, then confirm it disappears after the statement finishes; do not cancel or terminate a session as part of this exercise.
- **Intermediate relation check:** For sql-44 Exercise 1, inspect the source keys that survive `WHERE`; then check `runtime DESC NULLS LAST` before applying the row cap.
- **Clause check:** For sql-44 Exercise 1, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_stat_activity`, preserve one row per `pid`, and finish with `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query` ordered by `runtime DESC NULLS LAST`.
- **Alternative/trade-off:** For sql-44 Exercise 1, the chosen form is justified by this lesson-specific rationale: Expected shape: zero or more currently active sessions, excluding the monitoring query itself. Evaluate another form against the concrete expected result (zero or more currently active sessions, excluding the monitoring query itself. A long runtime can be normal; inspect wait events, locks, and the operation's purpose before intervening) and the verification above.
- **Edge case:** A quiet local database can correctly return zero rows. Use a controlled `pg_sleep` session when you need a positive observation, and never manufacture a row in a system view.

## Exercise 2 — Optional top statement statistics

```sql
BEGIN;
SET search_path TO training, public;

CREATE TEMP TABLE top_statement_stats (
  ranking text,
  rank_position integer,
  userid oid,
  dbid oid,
  toplevel boolean,
  queryid bigint,
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
      SELECT 'total_exec_time',
             row_number() OVER (
               ORDER BY total_exec_time DESC,
                        userid, dbid, toplevel, queryid
             )::integer,
             userid,
             dbid,
             toplevel,
             queryid,
             left(query, 200),
             calls,
             mean_exec_time,
             total_exec_time
      FROM public.pg_stat_statements
      ORDER BY total_exec_time DESC, userid, dbid, toplevel, queryid
      LIMIT 10
    $by_total$;
    EXECUTE $by_mean$
      INSERT INTO top_statement_stats
      SELECT 'mean_exec_time',
             row_number() OVER (
               ORDER BY mean_exec_time DESC,
                        userid, dbid, toplevel, queryid
             )::integer,
             userid,
             dbid,
             toplevel,
             queryid,
             left(query, 200),
             calls,
             mean_exec_time,
             total_exec_time
      FROM public.pg_stat_statements
      ORDER BY mean_exec_time DESC, userid, dbid, toplevel, queryid
      LIMIT 10
    $by_mean$;
  ELSE
    RAISE NOTICE 'pg_stat_statements is not installed; optional result is empty';
  END IF;
END
$optional_pg_stat_statements$;

SELECT *
FROM top_statement_stats
ORDER BY ranking, rank_position;

ROLLBACK;
```

Expected shape: up to twenty rows when `pg_stat_statements` is installed and
loaded—at most ten for each ranking label. Otherwise the block emits an
explanatory notice and the final query returns an empty result.

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 2, inspect `to_regclass('public.pg_stat_statements')`, then read the optional `public.pg_stat_statements` view into the course-owned temporary `top_statement_stats` table. Build `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`; do not install the extension or reset shared statistics.
- **Expected result/shape:** For sql-44 Exercise 2, expected output: up to 20 rows when `pg_stat_statements` is installed and loaded, with at most 10 rows per ranking label (`total_exec_time` and `mean_exec_time`); otherwise emit an explanatory notice and return an empty result. Each row is one statement within a ranking, identified by (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`). The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
- **Independent verification:** For sql-44 Exercise 2, if the optional view is absent, require the notice and empty result. If it is present, require only the `total_exec_time` and `mean_exec_time` labels, at most 10 rows per label, unique (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), consecutive `rank_position` values from 1 through N, nonincreasing `total_exec_time` order for its label, nonincreasing `mean_exec_time` order for its label, and values that match a fresh read of `public.pg_stat_statements`.
- **Intermediate relation check:** For sql-44 Exercise 2, inspect the existence check first, then compare the by-total and by-mean selections separately before reading the combined temporary relation.
- **Clause check:** For sql-44 Exercise 2, the solution uses dynamic `SELECT`, window `OVER`, `FROM`, `ORDER BY`, and `LIMIT` clauses. Each branch preserves one statement per (`userid`, `dbid`, `toplevel`, `queryid`) within its `ranking`, assigns `rank_position`, and limits that ranking to ten rows.
- **Alternative/trade-off:** For sql-44 Exercise 2, the chosen form is justified by this lesson-specific rationale: Expected shape: up to ten rows when `pg_stat_statements` is installed and loaded; otherwise an explanatory notice and an empty result. Evaluate another form against the concrete expected result (up to ten rows when `pg_stat_statements` is installed and loaded; otherwise an explanatory notice and an empty result) and the verification above.
- **Edge case:** The optional view can be absent or contain fewer than ten statements. Both states are valid and leave the monitored statistics unchanged.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 3, take a read-only snapshot of `pg_stat_activity`. Build the answer toward `pid`, `usename`, `state`, `transaction_age`, and `statement_age`; keep `pid` visible because the output grain is one backend session.
- **Expected result/shape:** For sql-44 Exercise 3, expected output: one row per `pid`. The final columns are `pid`, `usename`, `state`, `transaction_age`, and `statement_age`. The final order is `transaction_age DESC NULLS LAST`.
- **Independent verification:** For sql-44 Exercise 3, run an anti-check that counts rows where NOT (`pid <> pg_backend_pid() AND state <> 'idle'`); require unique `pid` and compare `pid`, `usename`, `state`, `transaction_age`, and `statement_age` with `pg_stat_activity`. Require nonnegative ages for non-NULL timestamps and `transaction_age >= statement_age` when both exist. When practical, use a controlled second `psql` session with `BEGIN`, wait, and then a long-running query to observe both clocks; finish that session with `ROLLBACK`.
- **Intermediate relation check:** For sql-44 Exercise 3, inspect the source keys that survive `WHERE`; then check `transaction_age DESC NULLS LAST` before applying the row cap.
- **Clause check:** For sql-44 Exercise 3, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_stat_activity`, preserve one row per `pid`, and finish with `pid`, `usename`, `state`, `transaction_age`, and `statement_age` ordered by `transaction_age DESC NULLS LAST`.
- **Alternative/trade-off:** For sql-44 Exercise 3, the chosen form is justified by this lesson-specific rationale: `query_start` belongs to the current statement; `xact_start` belongs to its transaction. Evaluate another form against the concrete expected result (one row per `pid`) and the verification above.
- **Edge case:** A backend outside an explicit transaction can have a NULL `xact_start`; preserve that NULL rather than converting it to a misleading zero duration.

## Exercise 4 — Summarize connections safely

Grouping by database, user, and state supports capacity triage without exposing
complete SQL text in a broadly shared report.

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 4, take a read-only snapshot of `pg_stat_activity`. Group by `datname`, `usename`, and `state`, and calculate `connections`; keep the complete three-column group key visible.
- **Expected result/shape:** For sql-44 Exercise 4, expected output: one row per `datname`, `usename`, and `state`. The final columns are `datname`, `usename`, `state`, and `connections`. The final order is `datname, usename, state`.
- **Independent verification:** For sql-44 Exercise 4, independently aggregate `pg_stat_activity` by `datname`, `usename`, and `state`; require one output row for every distinct tuple and compare `connections` tuple by tuple, using `IS NOT DISTINCT FROM` when matching nullable catalog values. Also require `SUM(connections)` to equal `COUNT(*)` from the same source snapshot and require the output tuples to be unique.
- **Intermediate relation check:** For sql-44 Exercise 4, confirm the groups are `datname`, `usename`, and `state`; then check `datname, usename, state` before applying the row cap.
- **Clause check:** For sql-44 Exercise 4, the solution actually uses `FROM`, `GROUP BY`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_stat_activity`, preserve one row per `datname`, `usename`, and `state`, and finish with `datname`, `usename`, `state`, and `connections` ordered by `datname, usename, state`.
- **Alternative/trade-off:** For sql-44 Exercise 4, the chosen form is justified by this lesson-specific rationale: Grouping by database, user, and state supports capacity triage without exposing complete SQL text in a broadly shared report. Evaluate another form against the concrete expected result (one row per `datname`, `usename`, and `state`) and the verification above.
- **Edge case:** Background workers can expose NULL database or user values; grouped NULLs are legitimate categories and must survive verification.

## Exercise 5 — Retain mean and total workload views

Mean duration highlights individually expensive calls; total execution time
highlights cumulative cost. The answer keeps both rather than declaring one
universal “slow query” ranking.

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 5, read the course-owned temporary `top_statement_stats` table without changing the monitored server statistics. Build the answer toward `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`; keep the complete statement-within-ranking key visible.
- **Expected result/shape:** For sql-44 Exercise 5, expected output: one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), so each ranking label can contain multiple statements. The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
- **Independent verification:** For sql-44 Exercise 5, require one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`) and compare `rank_position`, `query`, `calls`, `mean_exec_time`, and `total_exec_time` with `top_statement_stats`. When the optional source is available, require both ranking labels, at most 10 rows per label, consecutive `rank_position` values, `total_exec_time` order for that ranking, and `mean_exec_time` order for that ranking; `ranking` alone is deliberately non-unique.
- **Intermediate relation check:** For sql-44 Exercise 5, inspect each ranking label separately and verify that its stored `rank_position` still matches the metric that produced the list.
- **Clause check:** For sql-44 Exercise 5, the solution uses `FROM`, `SELECT`, and `ORDER BY`: it preserves one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`) and displays the two lists in `ranking, rank_position` order.
- **Alternative/trade-off:** For sql-44 Exercise 5, the chosen form is justified by this lesson-specific rationale: Mean duration highlights individually expensive calls; total execution time highlights cumulative cost. Evaluate another form against the concrete statement-within-ranking grain and the verification above.
- **Edge case:** The same statement can appear once in each ranking. That is expected because `ranking` is part of the identity; it is not a duplicate to remove.

## Exercise 6 — Identify idle-in-transaction sessions

The read-only diagnostic returns age and wait fields. It does not cancel a
backend; ownership and operational impact must be confirmed first.

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 6, take a read-only snapshot of `pg_stat_activity`. Build the answer toward `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`; keep `pid` visible because the output grain is one backend session.
- **Expected result/shape:** For sql-44 Exercise 6, expected output: one row per `pid` whose state is `idle in transaction`. The final columns are `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`. The final order is `transaction_age DESC NULLS LAST`.
- **Independent verification:** For sql-44 Exercise 6, run an anti-check for any row whose state is not `idle in transaction`; require unique `pid`, non-NULL transaction starts, and nonnegative `transaction_age`, and compare every projected value with `pg_stat_activity`. When practical, open a controlled second `psql` session, run `BEGIN`, wait without committing, observe the session, then run `ROLLBACK` and confirm that it disappears from this result.
- **Intermediate relation check:** For sql-44 Exercise 6, inspect the source keys that survive `WHERE`; then check `transaction_age DESC NULLS LAST` before applying the row cap.
- **Clause check:** For sql-44 Exercise 6, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_stat_activity`, preserve one row per `pid`, and finish with `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event` ordered by `transaction_age DESC NULLS LAST`.
- **Alternative/trade-off:** For sql-44 Exercise 6, the chosen form is justified by this lesson-specific rationale: The read-only diagnostic returns age and wait fields. Evaluate another form against the concrete expected result (one row per `pid`) and the verification above.
- **Edge case:** A correct result may be empty. Create the state only in a controlled second session, then cleanly roll it back.
