# Day 44: Monitoring and Diagnostics

## How to run this lesson

In `./classroom`, choose PostgreSQL, open **sql-44** and run it with
**Whole SQL lesson (psql)** against `advanced_sql_training`. Day 44 reads the
server's own state rather than changing course tables: the script opens
`BEGIN`, lists non-idle sessions from `pg_stat_activity`, prints an
`EXPLAIN ANALYZE` plan for a category join and ends with `ROLLBACK`. Its
`pg_stat_statements` query is commented out, so the starter never touches
that optional extension. Your editable copy is
`.learning/sql/sql-44/lesson/workspace/sql/postgres-60day/day44_monitoring_diagnostics.sql`
in the Docker learning volume. In our private PostgreSQL 17 container the
transcript was `BEGIN`, `SET`, a one-row session list, a plan of about 21
lines under `QUERY PLAN`, and `ROLLBACK`. The session list depends on who else
is connected, so the classroom can show more rows; the one row you can count
on is your own script, which is `active` while it runs. `psql` runs the file
with `ON_ERROR_STOP`, so the first `ERROR` ends the run. Setup and resume live
in the
[classroom launch steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom);
JupyterLab users can take the
[contributor notebook path](../../STUDY-GUIDE.md#optional-contributor-notebook-route)
instead.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 43; logical backup and recovery](day43_backup_recovery.md) Day 43 staged customer rows and checked them inside `BEGIN`/`ROLLBACK`; Day 44 writes no course rows at all and reads the server's activity views instead.
- **Artifacts:** [learner SQL](../day44_monitoring_diagnostics.sql) ·
  [solution reasoning](../solutions/day44_solutions.md) ·
  [executable solution](../solutions/day44_solutions.sql)

## A beginner's mental model for this lesson

Day 44 reads two kinds of evidence that look alike and mean different things.
`pg_stat_activity` is a live view with one row per server process at this
instant. `pg_stat_statements`, when installed and loaded, keeps running totals
per statement shape since its statistics were last reset. The first answers
"what is running now?"; the second answers "what has cost the most so far?".

A **Backend PID** is the process ID of one connection, and `pid` is the key of
every session exercise because it is unique in `pg_stat_activity`. Your own
monitoring query has one too, returned by `pg_backend_pid()`, which is why the
solution adds `pid <> pg_backend_pid()` when it lists active work: without it,
the query reports itself. At rest our container's view held six rows: the
script's own client backend plus five background processes (checkpointer,
background writer, WAL writer, autovacuum launcher and logical replication
launcher), all with a `NULL` `state`.

A **Wait event** names what a backend is waiting for. A second session
sleeping in `pg_sleep(6)` showed `wait_event_type` `Timeout` and `wait_event`
`PgSleep`; a session left open after `BEGIN; SELECT 1;` showed `Client` and
`ClientRead`, meaning the server is waiting for the client's next command.
Both wait columns are `NULL` when an active backend is busy rather than
waiting. A long runtime with a `Lock` wait is a different problem from a long
runtime with no wait at all.

A **Normalized statement** is the unit `pg_stat_statements` counts: constants
are replaced by placeholders, so `WHERE order_id = 7` and `WHERE order_id = 8`
add to one entry with one `queryid`. Its `calls`, `mean_exec_time` and
`total_exec_time` describe that shape over many runs, never one session.

Read every session query in
[logical clause order](../../STUDY-GUIDE.md#reading-any-query-in-logical-order):
`FROM pg_stat_activity` yields one row per process, `WHERE` keeps the states
the exercise names, and only then does `SELECT` compute an age. Because
`WHERE` runs first, any test on `state` silently drops the background
processes too, since `NULL <> 'idle'` is not true.

## Two worked SQL examples

Both excerpts come from `day44_monitoring_diagnostics.sql` and run between its
`BEGIN` and `ROLLBACK`. The first reads the system view `pg_stat_activity`,
which lives in `pg_catalog`; PostgreSQL searches that schema before `training`
and `public` even though the file's `SET search_path` line does not name it.
The second sends the course tables `order_items`, `products` and `orders`
through `EXPLAIN ANALYZE`.

### Example 1

```sql
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
```

**How to read it:** `FROM pg_stat_activity` produces one row per server process. `WHERE state <>
'idle'` keeps active and idle-in-transaction sessions and drops the background
processes, whose `state` is `NULL`. `SELECT` computes `running_for` as
`NOW() - query_start` and trims the SQL text with `left(query, 120)`.
`ORDER BY running_for DESC` puts the oldest statement first and `LIMIT 20`
keeps at most twenty. Compare it with the first exercise: there is no
`pid <> pg_backend_pid()` filter and no wait columns yet.

**Expected result/shape:** In our quiet container it returned one row: the script itself, user
`postgres`, database `advanced_sql_training`, state `active`, and a
`running_for` of about `-00:00:00.0002`. The negative age is real. `NOW()` is
frozen at the start of the transaction, the `BEGIN` line, while `query_start`
is the start of this later `SELECT`, so the subtraction runs backwards; after
a `pg_sleep(0.2)` inside the same transaction the gap grew to about minus 0.2
seconds. The solution uses `clock_timestamp()`, which reads the clock when the
row is evaluated. The `query` column prints over several lines ending in `+`
because the stored SQL text keeps its line breaks. Your `pid` will differ.

### Example 2

```sql
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
```

**How to read it:** `EXPLAIN ANALYZE` runs the query for real and prints the plan with measured
times instead of the result rows. Underneath, the query starts from
`order_items`, joins each line to its product and its order, keeps orders
placed in the last 180 days, sums `quantity` per `p.category` and sorts by
that sum. Read the plan from the most indented nodes outward, because those
produce rows first.

**Expected result/shape:** Our plan had 21 lines: a `Sort` on `sum(oi.quantity) DESC` above a
`HashAggregate` keyed on `p.category`, above two hash joins. The inner join
scans all 13,085 `order_items` rows and hashes `orders` after a `Filter` on
`order_date` kept 1,538 orders and removed 2,824; the outer join hashes the
300 `products`. The planner estimated 4,608 joined lines and 4,665 arrived,
6 groups came out, every node ran once (`loops=1`), and execution took 2 to
6 ms across our runs. The same query without `EXPLAIN ANALYZE` returned
Apparel 2,382, Beauty 2,382, Books 2,338, Sports 2,324, Electronics 2,305 and
Home 2,287. Apparel and Beauty tie, and `ORDER BY qty DESC` has no second key,
so their order is not guaranteed. Because the window is
`now() - interval '180 days'`, these counts move as the calendar passes the
fixture's order dates; ours were taken two days after its newest order.

## Learning objectives

- Distinguish active session state from aggregated statement history.
- Collect wait, runtime, and plan evidence before proposing intervention.

## Vocabulary and concepts

- **Wait event:** the resource or condition an active backend is waiting on.
- **Backend PID:** the process identifier for one PostgreSQL session.
- **Normalized statement:** structurally equivalent SQL grouped for aggregate
  statistics.

## Worked example / walkthrough

Query `pg_stat_activity`, exclude `pg_backend_pid()`, and calculate runtime only
for active statements. For one row, read user, state, wait type/event, and query
together; a long duration alone does not prove a fault or authorize
termination.

## Exercises

Complete these in the
[learner SQL](../day44_monitoring_diagnostics.sql):

1. Identify longest-running active statements.
   **Inputs/evidence:** For sql-44 Exercise 1, read `pg_stat_activity` once, keep backends with `state = 'active'` other than `pg_backend_pid()`, and compute `runtime` as `clock_timestamp() - query_start`, so the age is measured at read time rather than at the start of the lesson transaction; show `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`.
   **Expected result/shape:** For sql-44 Exercise 1, expected output: zero or more currently active sessions, excluding the monitoring query itself. A long runtime can be normal; inspect wait events, locks, and the operation's purpose before intervening. The final columns are `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`. The final order is `runtime DESC NULLS LAST`.
   **Verify:** For sql-44 Exercise 1, on a quiet server confirm 0 rows while `SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND pid = pg_backend_pid()` returns 1, which proves the self-exclusion works; then, from a second `psql` session, run `BEGIN; SELECT pg_sleep(1); SELECT pg_sleep(6);` and while it sleeps confirm exactly one row with a unique `pid`, `wait_event` `PgSleep`, `query` `SELECT pg_sleep(6);`, and a `runtime` that counts only the current statement, not the earlier one-second sleep; rerun after it finishes and confirm the row is gone. Do not cancel or terminate the session.
   **Data check:** In our container the solution returned zero rows on a quiet server, because its own session is excluded. With a second session running `BEGIN; SELECT pg_sleep(1); SELECT pg_sleep(6);` it returned one row: state `active`, `runtime` about 1.6 seconds, `wait_event_type` `Timeout`, `wait_event` `PgSleep` and `query` `SELECT pg_sleep(6);`. The runtime covers only the current statement, not the earlier one-second sleep.
2. Conditionally rank `pg_stat_statements` by mean and total time.
   **Inputs/evidence:** For sql-44 Exercise 2, inspect `to_regclass('public.pg_stat_statements')`, then read the optional `public.pg_stat_statements` view into the course-owned temporary `top_statement_stats` table. Build `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`; do not install the extension or reset shared statistics.
   **Expected result/shape:** For sql-44 Exercise 2, expected output: up to 20 rows when `pg_stat_statements` is installed and loaded, with at most 10 rows per ranking label (`total_exec_time` and `mean_exec_time`); otherwise emit an explanatory notice and return an empty result. Each row is one statement within a ranking, identified by (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`). The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
   **Verify:** For sql-44 Exercise 2, if the optional view is absent or raises `object_not_in_prerequisite_state` because the module was not preloaded, require an explanatory notice and an empty result. If it is readable, require only the `total_exec_time` and `mean_exec_time` labels, at most 10 rows per label, unique (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), consecutive `rank_position` values from 1 through N, nonincreasing `total_exec_time` order for its label, nonincreasing `mean_exec_time` order for its label, and values that match a fresh read of `public.pg_stat_statements`.
   **Data check:** Our container lists `pg_stat_statements` 1.11 as available but not installed, and `shared_preload_libraries` is empty, so the solution printed `NOTICE: pg_stat_statements is not installed; optional result is empty` and a 0-row table with all ten column headers. A default classroom database is likely to behave the same way.
3. Compare statement age with transaction age.
   **Inputs/evidence:** For sql-44 Exercise 3, read `pg_stat_activity` once, drop this session with `pid <> pg_backend_pid()` and idle sessions with `state <> 'idle'` (which also drops background processes, whose `state` is `NULL`), and compute `transaction_age` from `xact_start` and `statement_age` from `query_start`, both against `clock_timestamp()`.
   **Expected result/shape:** For sql-44 Exercise 3, expected output: one row per `pid` for other non-idle client sessions, which is 0 rows on a quiet server; an open transaction shows a `transaction_age` at least as large as its `statement_age`, and an aborted transaction shows a `NULL` `transaction_age` and sorts last. The final columns are `pid`, `usename`, `state`, `transaction_age`, and `statement_age`. The final order is `transaction_age DESC NULLS LAST`.
   **Verify:** For sql-44 Exercise 3, open three controlled sessions: `BEGIN; SELECT pg_sleep(1); SELECT pg_sleep(6);`, `BEGIN; SELECT 1;` left open, and `BEGIN; SELECT 1/0;` left open; confirm three rows with unique `pid`, the sleeper's `transaction_age` about one second above its `statement_age`, the open `SELECT 1` session with both ages almost equal, and the aborted session in state `idle in transaction (aborted)` with a `NULL` `transaction_age`. Check clock order with `xact_start <= query_start`, not `transaction_age >= statement_age`, because the two `clock_timestamp()` reads can make an autocommit statement's age one microsecond larger. Finish each session with `ROLLBACK`.
   **Data check:** With three controlled sessions open the solution returned three rows. The `BEGIN; SELECT 1;` session showed both ages at about 2.64 seconds, because its last statement began right after `BEGIN`. The sleeping session showed a transaction age of about 2.59 seconds and a statement age of about 1.58: its first one-second sleep belongs to the transaction but not to the current statement. A session whose `SELECT 1/0` had failed showed `idle in transaction (aborted)` with a `NULL` transaction age, sorted last by `NULLS LAST`. One caution for the "transaction age at least statement age" check: for a single autocommit statement `xact_start` equals `query_start`, and because the query reads `clock_timestamp()` twice, our run showed a statement age one microsecond larger. Compare `xact_start <= query_start` instead.
4. Summarize connections by database, user, and state.
   **Inputs/evidence:** For sql-44 Exercise 4, read `pg_stat_activity` once and group by `datname`, `usename`, and `state` with `COUNT(*) AS connections`, leaving out `query` so no statement text is exposed; background processes have `NULL` in some or all of the three key columns and form their own groups.
   **Expected result/shape:** For sql-44 Exercise 4, expected output: one row per `datname`, `usename`, and `state`. The final columns are `datname`, `usename`, `state`, and `connections`. The final order is `datname, usename, state`.
   **Verify:** For sql-44 Exercise 4, on a quiet container confirm three groups that sum to 6 and match `SELECT count(*) FROM pg_stat_activity` (6): (`advanced_sql_training`, `postgres`, `active`) with 1, which is this query itself, (`NULL`, `postgres`, `NULL`) with 1 for the logical replication launcher, and an all-`NULL` group with 4 for the checkpointer, background writer, WAL writer, and autovacuum launcher; then open one sleeping session, one open `BEGIN; SELECT 1;` session, and one aborted transaction and confirm five groups summing to 9, with `active` at 2 and separate `idle in transaction` and `idle in transaction (aborted)` rows of 1 connection each.
   **Data check:** On a quiet container the solution returned three groups adding up to six processes: `advanced_sql_training`, `postgres`, `active` with 1 (the script itself, since this query keeps its own `pid`); a `NULL` database with user `postgres` and a `NULL` state with 1 (the logical replication launcher); and an all-`NULL` group of 4 (checkpointer, background writer, WAL writer and autovacuum launcher). With three extra sessions open it returned five groups adding up to nine. The `NULL` groups sort last because ascending order places `NULL` after every value.
5. Repair a report that ranks only mean duration.
   **Inputs/evidence:** For sql-44 Exercise 5, read the temporary `top_statement_stats` table that Exercise 2 filled with up to 10 `total_exec_time` rows and up to 10 `mean_exec_time` rows from `pg_stat_statements` (0 rows and a NOTICE when the extension is not loaded, as on the course container), without resetting the monitored server statistics, and select `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time` so each list keeps its full statement key.
   **Expected result/shape:** For sql-44 Exercise 5, expected output: one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), so each ranking label can contain multiple statements. The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
   **Verify:** For sql-44 Exercise 5, require one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`) and compare `rank_position`, `query`, `calls`, `mean_exec_time`, and `total_exec_time` with `top_statement_stats`. When the optional source is available, require both ranking labels, at most 10 rows per label, consecutive `rank_position` values, `total_exec_time` order for that ranking, and `mean_exec_time` order for that ranking; `ranking` alone is deliberately non-unique.
   **Data check:** Here the result is the same 0-row table as the optional ranking, because `top_statement_stats` stayed empty. If the extension were readable, the `mean_exec_time` list would print before the `total_exec_time` list, because `ORDER BY ranking` sorts the label text alphabetically, even though the `DO` block inserts the total list first.
6. Identify and explain idle-in-transaction sessions.
   **Inputs/evidence:** For sql-44 Exercise 6, read `pg_stat_activity` once, keep only `state = 'idle in transaction'` (an equality test, so `idle in transaction (aborted)` is excluded), and compute `transaction_age` as `clock_timestamp() - xact_start`; show `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`.
   **Expected result/shape:** For sql-44 Exercise 6, expected output: one row per `pid` whose state is `idle in transaction`. The final columns are `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`. The final order is `transaction_age DESC NULLS LAST`.
   **Verify:** For sql-44 Exercise 6, confirm 0 rows on a quiet server; then open a second `psql` session, run `BEGIN; SELECT 1;`, and leave it open: confirm exactly one row with a unique `pid`, `wait_event_type` `Client`, `wait_event` `ClientRead`, and a growing `transaction_age`, while an aborted session (`BEGIN; SELECT 1/0;`) does not appear; run `ROLLBACK` in the open session and confirm the row disappears. Do not cancel or terminate the session.
   **Data check:** With the controlled sessions open the solution returned one row: the `BEGIN; SELECT 1;` session, with `wait_event_type` `Client` and `wait_event` `ClientRead`. The failed session did not appear, because its state is the longer string `idle in transaction (aborted)` and the filter is an equality test. In a separate check, a session that ran `LOCK TABLE training.customers IN ACCESS SHARE MODE` before going idle still held that lock in `pg_locks`, while the aborted session held no relation locks at all.

If the extension is unavailable, document that boundary without changing server
configuration.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** treating the monitoring query's own
  row as a finding. Example 1 has no `pid <> pg_backend_pid()` filter, so on a
  quiet server its only row is the script itself, `active`, with a negative
  `running_for`. Exclude your own `pid` before reading anything into the list.
- **A negative or shrunken age:** `NOW()` returns the transaction start, so
  inside the file's `BEGIN` it is earlier than the current statement's
  `query_start`, and every other session's age is short by the time since
  `BEGIN`. Use `clock_timestamp()` for ages computed inside a transaction.
- **Background processes vanish or crowd in:** any `WHERE` test on `state`
  drops every process whose state is `NULL`, while the unfiltered connection
  summary keeps them as `NULL` groups. In our container they were five of the
  six rows, so decide which view you want before counting.
- **Missing failed transactions:** `state = 'idle in transaction'` does not
  match `idle in transaction (aborted)`. That is correct for a lock hunt (our
  aborted session held no relation locks), but a connection count must still
  include those sessions, because each one occupies a slot until `ROLLBACK`.
- **`relation "pg_stat_statements" does not exist`:** a plain query naming the
  view fails this way when the extension is absent, and an installed but
  unloaded extension raises `pg_stat_statements must be loaded via
  "shared_preload_libraries"` (SQLSTATE 55000). Keep the solution's
  `to_regclass` check and narrow handler instead of installing anything.
- **`psql` stopped partway:** fix the first error and rerun the whole file
  from `BEGIN`; the
  [failure recovery checklist](../../STUDY-GUIDE.md#recover-from-common-failures)
  covers container and path problems.

## Self-check

- Can you tell whether evidence describes a current session or historical
  aggregates?
- Have you avoided extension installation, statistics resets, cancellation, and
  termination?

## Next step

Continue to [Day 45; optimization project](day45_phase3_optimization_project.md).

## Deep dive and reference

## What you will learn

- Find active statements and calculate their current runtime.
- Interpret wait events before deciding that a query is stuck.
- Read optional aggregate statement statistics when the extension is available.

## How the learner script works

The starter queries `pg_stat_activity`, then runs `EXPLAIN ANALYZE` on recent
category units. Its `pg_stat_statements` query is commented because the
extension may require server configuration and elevated access.

There are three distinct states to reason about:

1. **Absent:** `to_regclass('public.pg_stat_statements')` is NULL.
2. **Installed but not loaded:** the view exists, but reading it raises
   `object_not_in_prerequisite_state` because
   `shared_preload_libraries` did not load the module at server startup.
3. **Installed and loaded:** the view is readable and can be ranked.

The portable solution treats the first two states as an explained empty
optional result. It catches only the known not-preloaded condition; unrelated
SQL errors still stop the script and must be diagnosed.

The course server runs PostgreSQL 17, where the relevant extension columns
include `calls`, `total_exec_time` and `mean_exec_time`. These `_exec_time`
names date from PostgreSQL 13; older examples that read `total_time` or
`mean_time` fail against this version.

## Practice map

The six numbered exercises above are the practice set, in two families. The
first, third, fourth and sixth read `pg_stat_activity`, and on a quiet server
three of them correctly return nothing. When you can open a second `psql`
connection, leave it in `pg_sleep` or in an open `BEGIN` while you run your
answers, then `ROLLBACK` it. The second and fifth read `pg_stat_statements`
through the temporary `top_statement_stats` table that the second one builds,
so write that one first; without the extension both print an empty result
after a `NOTICE`. The data checks quote our container, where the number of
open sessions changed between runs, so compare shapes, states and orderings
rather than exact ages.

## Interpretation and safety

- A long-running query can be legitimate; inspect owner, purpose, wait state,
  locks, and plan before intervening.
- `pg_stat_statements` aggregates normalized statement history; it is not a list
  of currently active sessions.
- Statistics reset, server restarts, and extension availability affect the
  observation window.
- Never install extensions, change `shared_preload_libraries`, reset statistics,
  cancel queries, or terminate backends merely to complete this lesson.
- The executable solution remains portable by checking for the extension view,
  using dynamic SQL only when it exists, and catching only the defined
  installed-but-not-preloaded SQLSTATE around that optional read.

## Expanded practice lab

Prompts 3-6 build read-only operational judgment. `query_start` measures the
current statement while `xact_start` measures the enclosing transaction; show
both because long idle transactions can retain locks and old snapshots.

Aggregate connection counts instead of exposing full SQL text in a shared
report. For historical workload, examine both `mean_exec_time` and
`total_exec_time`: one reveals expensive calls, the other cumulative load.
Never cancel a session as part of this practice.

## Ask an AI tutor about this lesson

A tutor is optional; this guide, the learner file and PostgreSQL are enough
for Day 44. The
[tutor section of the study guide](../../STUDY-GUIDE.md#use-an-ai-tutor-optional)
lists what to share. Monitoring output is hard to rehearse without live
traffic, so a tutor is most useful as a source of invented snapshots: ask it
for a made-up `pg_stat_activity` row with a state, two ages and a wait event,
and say what you would check next before it answers. Ask it this after your
first quiet-database run:

```text
Tutor me through sql-44: Monitoring and Diagnostics.

I have completed the direct catalog prerequisite: `sql-43`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day44_monitoring_diagnostics.md
- Answer-free learner SQL: sql/postgres-60day/day44_monitoring_diagnostics.sql

Key terms to teach in context: Wait event, Backend PID, Normalized statement. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Query `pg_stat_activity`, exclude `pg_backend_pid()`, and calculate runtime only for active statements. For one row, read user, state, wait type/event, and query together; a long duration alone does not prove a fault or authorize termination.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-44/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Treat every path under `solutions/` as closed until I explicitly ask after an attempt.

Follow guide -> predict -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back. Done when I can explain the row grain and clause order, produce a passing transcript for the current exercise, justify its verification evidence, and answer the retrieval questions without copying the solution.
```
