# Day 44 Solutions: Monitoring and Diagnostics


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day44_solutions.sql
```

In our container `psql` printed `BEGIN`, `SET`, an empty active-session list,
`CREATE TABLE` for `top_statement_stats`, the `NOTICE` that
`pg_stat_statements` is not installed, `DO`, the empty ranking, an empty age
list, a three-row connection summary, the empty ranking again, an empty
idle-in-transaction list and `ROLLBACK`. Empty lists are the right answer on a
quiet server; open a second session if you want rows to inspect. The `NOTICE`
is expected, but an `ERROR` is not, because the handler catches only the
not-preloaded case. The
[solution reading notes](../../STUDY-GUIDE.md#read-a-solution) describe how to
compare your attempt.

## Clause-by-clause reading map

The file has two halves. The session half is four plain queries over
`pg_stat_activity`; read each in
[logical order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order):
`FROM` yields one row per process, `WHERE` picks the states, `SELECT` computes
ages with `clock_timestamp()`, and `ORDER BY` puts the oldest first. The
statistics half has three parts:

- `CREATE TEMP TABLE top_statement_stats` declares the ten output columns, so
  the result keeps one shape whether or not the extension exists.
- A `DO` block asks `to_regclass('public.pg_stat_statements')` whether the
  view exists and only then runs two `INSERT ... SELECT` statements through
  `EXECUTE`: one ranked by `total_exec_time`, one by `mean_exec_time`, each
  numbered with `row_number()` and cut to ten rows.
- An inner `BEGIN ... EXCEPTION WHEN object_not_in_prerequisite_state` block
  catches the SQLSTATE 55000 error an installed but unloaded extension raises,
  empties the table and prints its own `NOTICE`. Any other error still stops
  the run.

Two final `SELECT`s read the table in `ranking, rank_position` order, once as
`SELECT *` and once with every column named.

The two deliverables inspect active work and, when available,
`pg_stat_statements`. The solution remains runnable on a fresh PostgreSQL
installation where that optional extension is absent or installed without its
shared-memory module being loaded at server startup. See
[`day44_solutions.sql`](day44_solutions.sql).

## Exercise 1: Longest-running active statements

```sql
SET search_path TO training, public;

SELECT
  pid,
  usename,
  datname,
  state,
  clock_timestamp() - query_start AS runtime,
  wait_event_type,
  wait_event,
  left (query,
    160) AS query
FROM
  pg_stat_activity
WHERE
  state = 'active'
  AND pid <> pg_backend_pid()
ORDER BY
  runtime DESC NULLS LAST;
```

Expected shape: zero or more currently active sessions, excluding the
monitoring query itself. A long runtime can be normal; inspect wait events,
locks, and the operation's purpose before intervening.

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 1, read `pg_stat_activity` once, keep backends with `state = 'active'` other than `pg_backend_pid()`, and compute `runtime` as `clock_timestamp() - query_start`, so the age is measured at read time rather than at the start of the lesson transaction; show `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`.
- **Expected result/shape:** For sql-44 Exercise 1, expected output: zero or more currently active sessions, excluding the monitoring query itself. A long runtime can be normal; inspect wait events, locks, and the operation's purpose before intervening. The final columns are `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`. The final order is `runtime DESC NULLS LAST`.
- **Independent verification:** For sql-44 Exercise 1, on a quiet server confirm 0 rows while `SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND pid = pg_backend_pid()` returns 1, which proves the self-exclusion works; then, from a second `psql` session, run `BEGIN; SELECT pg_sleep(1); SELECT pg_sleep(6);` and while it sleeps confirm exactly one row with a unique `pid`, `wait_event` `PgSleep`, `query` `SELECT pg_sleep(6);`, and a `runtime` that counts only the current statement, not the earlier one-second sleep; rerun after it finishes and confirm the row is gone. Do not cancel or terminate the session.
- **Intermediate relation check:** Run the `FROM` and `WHERE` alone with `SELECT pid, state` first. On a quiet server that returns nothing, which is right: the only active backend is the one running the check. Drop `pid <> pg_backend_pid()` and your own row appears, which proves the filter is doing the work.
- **Clause check:** `clock_timestamp() - query_start` is evaluated as each row is produced, so the age is measured from the moment of reading, not from the file's `BEGIN`. `left(query, 160)` keeps enough text to recognize a statement without dumping a long one, and `NULLS LAST` is defensive: an active backend should always have a `query_start`, so its runtime should never be `NULL`.
- **Alternative/trade-off:** Keeping the learner's `state <> 'idle'` would also list idle-in-transaction sessions, whose `query_start` belongs to a statement that already finished, so their "runtime" would measure idleness rather than work. Keeping `NOW()` would shorten every age by the time since the file's `BEGIN` and make the script's own row negative. `state = 'active'` with `clock_timestamp()` answers the exercise as written.
- **Edge case:** A quiet local database can correctly return zero rows. Use a controlled `pg_sleep` session when you need a positive observation, and never manufacture a row in a system view.

## Exercise 2: Optional top statement statistics

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
    BEGIN
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
    EXCEPTION
      WHEN object_not_in_prerequisite_state THEN
        TRUNCATE top_statement_stats;
        RAISE NOTICE
          'pg_stat_statements exists but is not loaded via shared_preload_libraries; optional result is empty';
    END;
  ELSE
    RAISE NOTICE 'pg_stat_statements is not installed; optional result is empty';
  END IF;
END
$optional_pg_stat_statements$;

SELECT
  *
FROM
  top_statement_stats
ORDER BY
  ranking,
  rank_position;

ROLLBACK;
```

Expected shape: up to twenty rows when `pg_stat_statements` is installed and
loaded, at most ten for each ranking label. Otherwise the block emits an
explanatory notice and the final query returns an empty result.

An existence check is necessary but not sufficient. PostgreSQL can install the
extension's view without loading its shared-memory module at server startup.
The nested block catches only that documented
`object_not_in_prerequisite_state` condition. PL/pgSQL rolls back either
partial ranking inside the nested block, and `TRUNCATE` makes the empty-result
contract explicit. Any unrelated error still propagates.

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 2, inspect `to_regclass('public.pg_stat_statements')`, then read the optional `public.pg_stat_statements` view into the course-owned temporary `top_statement_stats` table. Build `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`; do not install the extension or reset shared statistics.
- **Expected result/shape:** For sql-44 Exercise 2, expected output: up to 20 rows when `pg_stat_statements` is installed and loaded, with at most 10 rows per ranking label (`total_exec_time` and `mean_exec_time`); otherwise emit an explanatory notice and return an empty result. Each row is one statement within a ranking, identified by (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`). The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
- **Independent verification:** For sql-44 Exercise 2, if the optional view is absent or raises `object_not_in_prerequisite_state` because the module was not preloaded, require an explanatory notice and an empty result. If it is readable, require only the `total_exec_time` and `mean_exec_time` labels, at most 10 rows per label, unique (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), consecutive `rank_position` values from 1 through N, nonincreasing `total_exec_time` order for its label, nonincreasing `mean_exec_time` order for its label, and values that match a fresh read of `public.pg_stat_statements`.
- **Intermediate relation check:** Check the branch before the ranking: `SELECT to_regclass('public.pg_stat_statements')` returned `NULL` in our container, which sends the block straight to the not-installed `NOTICE`. When the view is readable, run each `INSERT`'s `SELECT` by itself and confirm that `rank_position` runs 1, 2, 3 without gaps in each list before reading the combined table.
- **Clause check:** `row_number() OVER (ORDER BY total_exec_time DESC, userid, dbid, toplevel, queryid)` and the statement's own `ORDER BY ... LIMIT 10` use the same five keys, so the ten rows kept are exactly positions 1 to 10. The four tie-breakers are the view's identity: one normalized statement per user, database and top-level flag. `left(query, 200)` shortens the stored text, and the mean branch repeats the pattern with `mean_exec_time DESC` first.
- **Alternative/trade-off:** A plain `SELECT ... FROM pg_stat_statements` is shorter, but on a server like ours it fails with `relation "pg_stat_statements" does not exist` and stops the file under `ON_ERROR_STOP`. Catching `WHEN OTHERS` would keep the file running too, but a typo in the ranking query would then hide behind the same friendly `NOTICE`. The narrow handler costs a few lines and keeps real errors visible; when readable, the result is up to 20 rows, at most ten per label.
- **Edge case:** We exercised both empty branches in a private container. Absent gave `pg_stat_statements is not installed; optional result is empty`. In a throwaway transaction that ran `CREATE EXTENSION pg_stat_statements` and then rolled back, a direct read raised `pg_stat_statements must be loaded via "shared_preload_libraries"`, and the block printed `pg_stat_statements exists but is not loaded via shared_preload_libraries; optional result is empty` with a 0-row table. The lesson itself never installs the extension; a readable but nearly empty view simply yields fewer than ten rows per label.

## Reasoning, safety, and pitfalls

- `state = 'active'` is more precise than `state <> 'idle'` for the requested
  active-query list.
- `clock_timestamp()` advances during the statement and is appropriate for an
  observed runtime.
- Checking `to_regclass` keeps a missing extension view from ever being read.
  Inside PL/pgSQL the `IF` alone is enough, because a table name is resolved
  only when its statement first runs (a static `PERFORM` on the view inside the
  skipped branch ran cleanly in our container); `EXECUTE` makes that deferral
  explicit. Outside a `DO` block, a plain query naming the view fails with
  `relation "pg_stat_statements" does not exist`.
- These are diagnostic reads. Do not cancel or terminate sessions without
  confirming ownership and operational impact.

## Exercise 3: Separate query and transaction age

`query_start` belongs to the current statement; `xact_start` belongs to its
transaction. The latter can reveal long-lived snapshots hidden behind a short
or currently idle statement.

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 3, read `pg_stat_activity` once, drop this session with `pid <> pg_backend_pid()` and idle sessions with `state <> 'idle'` (which also drops background processes, whose `state` is `NULL`), and compute `transaction_age` from `xact_start` and `statement_age` from `query_start`, both against `clock_timestamp()`.
- **Expected result/shape:** For sql-44 Exercise 3, expected output: one row per `pid` for other non-idle client sessions, which is 0 rows on a quiet server; an open transaction shows a `transaction_age` at least as large as its `statement_age`, and an aborted transaction shows a `NULL` `transaction_age` and sorts last. The final columns are `pid`, `usename`, `state`, `transaction_age`, and `statement_age`. The final order is `transaction_age DESC NULLS LAST`.
- **Independent verification:** For sql-44 Exercise 3, open three controlled sessions: `BEGIN; SELECT pg_sleep(1); SELECT pg_sleep(6);`, `BEGIN; SELECT 1;` left open, and `BEGIN; SELECT 1/0;` left open; confirm three rows with unique `pid`, the sleeper's `transaction_age` about one second above its `statement_age`, the open `SELECT 1` session with both ages almost equal, and the aborted session in state `idle in transaction (aborted)` with a `NULL` `transaction_age`. Check clock order with `xact_start <= query_start`, not `transaction_age >= statement_age`, because the two `clock_timestamp()` reads can make an autocommit statement's age one microsecond larger. Finish each session with `ROLLBACK`.
- **Intermediate relation check:** Run the query once without `state <> 'idle'`. Idle sessions then appear with a `NULL` `xact_start`, because they have no open transaction, and a `statement_age` that only measures time since their last command started. The filter removes them, and with them every background process whose state is `NULL`.
- **Clause check:** Both ages use `clock_timestamp()`, so `transaction_age` minus `statement_age` shows how long the transaction ran before its current statement began: about one second for our sleeping session, near zero for the session that ran `SELECT 1` right after `BEGIN`. `NULLS LAST` matters here, because the default `DESC` order would put a `NULL` transaction age first.
- **Alternative/trade-off:** Showing only `xact_start` would hide the sleeping session's split (about 2.59 seconds of transaction against 1.58 of statement); showing only `query_start` would make the open `BEGIN; SELECT 1;` session look like an old statement when nothing is running. Computing both ages from one clock reading, for example `clock_timestamp()` in a `CROSS JOIN` subquery, would also remove the microsecond case where an autocommit statement's age edges past its transaction's.
- **Edge case:** A transaction that already failed shows `idle in transaction (aborted)` and, in our PostgreSQL 17 run, a `NULL` `xact_start`, so its `transaction_age` is `NULL` while its `statement_age` still counts from the failed `SELECT 1/0`. Preserve that `NULL` rather than turning it into a zero duration.

## Exercise 4: Summarize connections safely

Grouping by database, user, and state supports capacity triage without exposing
complete SQL text in a broadly shared report.

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 4, read `pg_stat_activity` once and group by `datname`, `usename`, and `state` with `COUNT(*) AS connections`, leaving out `query` so no statement text is exposed; background processes have `NULL` in some or all of the three key columns and form their own groups.
- **Expected result/shape:** For sql-44 Exercise 4, expected output: one row per `datname`, `usename`, and `state`. The final columns are `datname`, `usename`, `state`, and `connections`. The final order is `datname, usename, state`.
- **Independent verification:** For sql-44 Exercise 4, on a quiet container confirm three groups that sum to 6 and match `SELECT count(*) FROM pg_stat_activity` (6): (`advanced_sql_training`, `postgres`, `active`) with 1, which is this query itself, (`NULL`, `postgres`, `NULL`) with 1 for the logical replication launcher, and an all-`NULL` group with 4 for the checkpointer, background writer, WAL writer, and autovacuum launcher; then open one sleeping session, one open `BEGIN; SELECT 1;` session, and one aborted transaction and confirm five groups summing to 9, with `active` at 2 and separate `idle in transaction` and `idle in transaction (aborted)` rows of 1 connection each.
- **Intermediate relation check:** Before grouping, list `backend_type, datname, usename, state` from the view. In our container that showed one `client backend` and five background processes, which explains both `NULL` groups before you aggregate anything.
- **Clause check:** `COUNT(*)` counts processes, and `GROUP BY` puts all `NULL` values of a column in one group, which is why four different background processes collapse into one row of 4. `ORDER BY datname, usename, state` sorts those `NULL` groups last. Leaving `query` out of the `SELECT` keeps statement text out of a report meant for sharing.
- **Alternative/trade-off:** Adding `backend_type` to the key, or filtering to `backend_type = 'client backend'`, would name or remove the anonymous `NULL` rows. Both change the contract's three-column grain, so run them as a side query when the `NULL` groups need explaining.
- **Edge case:** This query does not exclude its own `pid`, so the `active` count for your database is never below 1 while you run it. Subtract that row before deciding the database is busy.

## Exercise 5: Retain mean and total workload views

Mean duration highlights individually expensive calls; total execution time
highlights cumulative cost. The answer keeps both rather than declaring one
universal “slow query” ranking.

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 5, read the temporary `top_statement_stats` table that Exercise 2 filled with up to 10 `total_exec_time` rows and up to 10 `mean_exec_time` rows from `pg_stat_statements` (0 rows and a NOTICE when the extension is not loaded, as on the course container), without resetting the monitored server statistics, and select `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time` so each list keeps its full statement key.
- **Expected result/shape:** For sql-44 Exercise 5, expected output: one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), so each ranking label can contain multiple statements. The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
- **Independent verification:** For sql-44 Exercise 5, require one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`) and compare `rank_position`, `query`, `calls`, `mean_exec_time`, and `total_exec_time` with `top_statement_stats`. When the optional source is available, require both ranking labels, at most 10 rows per label, consecutive `rank_position` values, `total_exec_time` order for that ranking, and `mean_exec_time` order for that ranking; `ranking` alone is deliberately non-unique.
- **Intermediate relation check:** Filter to `ranking = 'total_exec_time'` and confirm `total_exec_time` never increases as `rank_position` goes from 1 to 10; repeat for the mean list. Each list is sorted by its own metric, so the other metric's column can rise and fall within it.
- **Clause check:** The `SELECT` names all ten columns rather than reusing `SELECT *`, so the report keeps its column order even if the temporary table is later widened. `ORDER BY ranking, rank_position` prints the `mean_exec_time` list first, because the labels sort alphabetically, and numbers the rows within each list.
- **Alternative/trade-off:** Sorting the combined table by `mean_exec_time DESC` alone is the broken report the exercise describes. For example, a statement called once at 900 ms would outrank one called 50,000 times at 2 ms, which has cost 100 seconds in total. Two labeled lists show both the expensive call and the expensive habit without pretending one ranking covers both.
- **Edge case:** The same statement can appear once in each ranking. That is expected because `ranking` is part of the identity; it is not a duplicate to remove.

## Exercise 6: Identify idle-in-transaction sessions

The read-only diagnostic returns age and wait fields. It does not cancel a
backend; ownership and operational impact must be confirmed first.

### Reasoning and verification

- **Inputs/evidence:** For sql-44 Exercise 6, read `pg_stat_activity` once, keep only `state = 'idle in transaction'` (an equality test, so `idle in transaction (aborted)` is excluded), and compute `transaction_age` as `clock_timestamp() - xact_start`; show `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`.
- **Expected result/shape:** For sql-44 Exercise 6, expected output: one row per `pid` whose state is `idle in transaction`. The final columns are `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`. The final order is `transaction_age DESC NULLS LAST`.
- **Independent verification:** For sql-44 Exercise 6, confirm 0 rows on a quiet server; then open a second `psql` session, run `BEGIN; SELECT 1;`, and leave it open: confirm exactly one row with a unique `pid`, `wait_event_type` `Client`, `wait_event` `ClientRead`, and a growing `transaction_age`, while an aborted session (`BEGIN; SELECT 1/0;`) does not appear; run `ROLLBACK` in the open session and confirm the row disappears. Do not cancel or terminate the session.
- **Intermediate relation check:** Before filtering, list `pid, state` for every `client backend`. With our controlled sessions that showed `idle in transaction`, `idle in transaction (aborted)` and two `active` rows (one of them the check itself), and the filter keeps only the first.
- **Clause check:** The equality `state = 'idle in transaction'` does not match the aborted variant. `wait_event_type` `Client` with `wait_event` `ClientRead` means the server is waiting for the client to send something, not for a lock; the risk is in what the idle session holds, which other sessions may be waiting on. `clock_timestamp() - xact_start` measures how long it has held it.
- **Alternative/trade-off:** Joining `pg_locks` on `pid` shows what an idle transaction holds: in our test, `AccessShareLock` on `training.customers` for a session that had run `LOCK TABLE`, and a `backend_xmin` snapshot plus locks on `orders` for a `REPEATABLE READ` session that had counted orders. That join changes the grain to one row per lock, so keep it as a follow-up query rather than the answer.
- **Edge case:** A correct result may be empty. Create the state only in a controlled second session, then cleanly roll it back.
