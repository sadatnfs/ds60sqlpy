# Day 44 — Monitoring and Diagnostics

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 43 — logical backup and recovery](day43_backup_recovery.md)
- **Artifacts:** [learner SQL](../day44_monitoring_diagnostics.sql) ·
  [solution reasoning](../solutions/day44_solutions.md) ·
  [executable solution](../solutions/day44_solutions.sql)

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-44 — Monitoring Diagnostics** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-44/lesson/workspace/sql/postgres-60day/day44_monitoring_diagnostics.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\day44_monitoring_diagnostics.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/day44_monitoring_diagnostics.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. The key vocabulary for this lesson is Wait event, Backend PID, Normalized statement. Its worked SQL reads or creates `order_items`, `products`, `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: Query pgstatactivity, exclude pgbackendpid(), and calculate runtime only for active statements. For one row, read user, state, wait type/event, and query together; a long duration alone does not prove a fault or authorize termination.
The first runnable example has a concrete contract: Example 1 returns one row per `pid`, `usename`, and `datname`, capped at 20 rows with columns `pid`, `usename`, `datname`, `state`, `query_start`, and `running_for` from `pg_stat_activity`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present. Its final projection is `pid`, `usename`, `datname`, `state`, `query_start`, `running_for`, and `query`. Reselect the returned key columns from `pg_stat_activity`, reject duplicate keys when the grain is one row per entity, and check the stated row cap and sort direction only when this example includes them. For tied business values, inspect the final ordering expression and verify its last key makes the displayed order reproducible.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/postgres-60day/day44_monitoring_diagnostics.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT pid, usename, datname, state, query_start, NOW() - query_start AS running_for, left(query, 120) AS query
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY running_for DESC
LIMIT 20;
```

**How to read it:** Example 1: Start with `pg_stat_activity` in `FROM`/`JOIN`; let `WHERE` remove nonqualifying rows. The final `SELECT` displays `pid`, `usename`, `datname`, `state`, `query_start`, `running_for`, and `query`. `ORDER BY` determines presentation order and the final `LIMIT 20` caps displayed rows. Before running, predict the row grain, row count, `NULL` positions, and first/last key; afterwards, compare each prediction with the transcript.

**Expected result/shape:** Example 1 returns one row per `pid`, `usename`, and `datname`, capped at 20 rows with columns `pid`, `usename`, `datname`, `state`, `query_start`, and `running_for` from `pg_stat_activity`. Compare the key set and row count with a simpler control over the same filter/window; inspect `NULL` versus zero/absent-row meaning and verify the final ordering/tie-breaker when present.

### Example 2

```sql
EXPLAIN ANALYZE
SELECT p.category, SUM(oi.quantity) AS qty
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
JOIN orders o ON o.order_id = oi.order_id
WHERE o.order_date >= now() - interval '180 days'
GROUP BY p.category
ORDER BY qty DESC;
```

**How to read it:** Example 2 returns plan rows rather than business rows. The node tree is evidence about one execution strategy; it does not replace a correctness check on the underlying query.

**Expected result/shape:** Example 2 prints a plan tree, not business rows. Run the underlying `SELECT` separately and reconcile its `category` key set and row count over `order_items`, `products`, and `orders`; then compare node estimates, actual rows × loops, buffers, and timing without requiring one fixed plan.

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
   **Inputs/evidence:** For sql-44 Exercise 1, take a read-only snapshot of `pg_stat_activity`. Build the answer toward `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`; keep `pid` visible because the output grain is one backend session.
   **Expected result/shape:** For sql-44 Exercise 1, expected output: zero or more currently active sessions, excluding the monitoring query itself. A long runtime can be normal; inspect wait events, locks, and the operation's purpose before intervening. The final columns are `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query`. The final order is `runtime DESC NULLS LAST`.
   **Verify:** For sql-44 Exercise 1, run an anti-check that counts rows where NOT (`state = 'active' AND pid <> pg_backend_pid()`); require unique `pid` and compare the projected `pid`, `usename`, `datname`, `state`, `runtime`, `wait_event_type`, `wait_event`, and `query` with a second read-only snapshot of `pg_stat_activity`. When practical, open a controlled second `psql` session that runs `SELECT pg_sleep(...)`, observe it as active, then confirm it disappears after the statement finishes; do not cancel or terminate a session as part of this exercise.
2. Conditionally rank `pg_stat_statements` by mean and total time.
   **Inputs/evidence:** For sql-44 Exercise 2, inspect `to_regclass('public.pg_stat_statements')`, then read the optional `public.pg_stat_statements` view into the course-owned temporary `top_statement_stats` table. Build `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`; do not install the extension or reset shared statistics.
   **Expected result/shape:** For sql-44 Exercise 2, expected output: up to 20 rows when `pg_stat_statements` is installed and loaded, with at most 10 rows per ranking label (`total_exec_time` and `mean_exec_time`); otherwise emit an explanatory notice and return an empty result. Each row is one statement within a ranking, identified by (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`). The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
   **Verify:** For sql-44 Exercise 2, if the optional view is absent, require the notice and empty result. If it is present, require only the `total_exec_time` and `mean_exec_time` labels, at most 10 rows per label, unique (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), consecutive `rank_position` values from 1 through N, nonincreasing `total_exec_time` order for its label, nonincreasing `mean_exec_time` order for its label, and values that match a fresh read of `public.pg_stat_statements`.
3. Compare statement age with transaction age.
   **Inputs/evidence:** For sql-44 Exercise 3, take a read-only snapshot of `pg_stat_activity`. Build the answer toward `pid`, `usename`, `state`, `transaction_age`, and `statement_age`; keep `pid` visible because the output grain is one backend session.
   **Expected result/shape:** For sql-44 Exercise 3, expected output: one row per `pid`. The final columns are `pid`, `usename`, `state`, `transaction_age`, and `statement_age`. The final order is `transaction_age DESC NULLS LAST`.
   **Verify:** For sql-44 Exercise 3, run an anti-check that counts rows where NOT (`pid <> pg_backend_pid() AND state <> 'idle'`); require unique `pid` and compare `pid`, `usename`, `state`, `transaction_age`, and `statement_age` with `pg_stat_activity`. Require nonnegative ages for non-NULL timestamps and `transaction_age >= statement_age` when both exist. When practical, use a controlled second `psql` session with `BEGIN`, wait, and then a long-running query to observe both clocks; finish that session with `ROLLBACK`.
4. Summarize connections by database, user, and state.
   **Inputs/evidence:** For sql-44 Exercise 4, take a read-only snapshot of `pg_stat_activity`. Group by `datname`, `usename`, and `state`, and calculate `connections`; keep the complete three-column group key visible.
   **Expected result/shape:** For sql-44 Exercise 4, expected output: one row per `datname`, `usename`, and `state`. The final columns are `datname`, `usename`, `state`, and `connections`. The final order is `datname, usename, state`.
   **Verify:** For sql-44 Exercise 4, independently aggregate `pg_stat_activity` by `datname`, `usename`, and `state`; require one output row for every distinct tuple and compare `connections` tuple by tuple, using `IS NOT DISTINCT FROM` when matching nullable catalog values. Also require `SUM(connections)` to equal `COUNT(*)` from the same source snapshot and require the output tuples to be unique.
5. Repair a report that ranks only mean duration.
   **Inputs/evidence:** For sql-44 Exercise 5, read the course-owned temporary `top_statement_stats` table without changing the monitored server statistics. Build the answer toward `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`; keep the complete statement-within-ranking key visible.
   **Expected result/shape:** For sql-44 Exercise 5, expected output: one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), so each ranking label can contain multiple statements. The final columns are `ranking`, `rank_position`, `userid`, `dbid`, `toplevel`, `queryid`, `query`, `calls`, `mean_exec_time`, and `total_exec_time`. The final order is `ranking, rank_position`.
   **Verify:** For sql-44 Exercise 5, require one row per (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`) and compare `rank_position`, `query`, `calls`, `mean_exec_time`, and `total_exec_time` with `top_statement_stats`. When the optional source is available, require both ranking labels, at most 10 rows per label, consecutive `rank_position` values, `total_exec_time` order for that ranking, and `mean_exec_time` order for that ranking; `ranking` alone is deliberately non-unique.
6. Identify and explain idle-in-transaction sessions.
   **Inputs/evidence:** For sql-44 Exercise 6, take a read-only snapshot of `pg_stat_activity`. Build the answer toward `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`; keep `pid` visible because the output grain is one backend session.
   **Expected result/shape:** For sql-44 Exercise 6, expected output: one row per `pid` whose state is `idle in transaction`. The final columns are `pid`, `usename`, `datname`, `transaction_age`, `wait_event_type`, and `wait_event`. The final order is `transaction_age DESC NULLS LAST`.
   **Verify:** For sql-44 Exercise 6, run an anti-check for any row whose state is not `idle in transaction`; require unique `pid`, non-NULL transaction starts, and nonnegative `transaction_age`, and compare every projected value with `pg_stat_activity`. When practical, open a controlled second `psql` session, run `BEGIN`, wait without committing, observe the session, then run `ROLLBACK` and confirm that it disappears from this result.

If the extension is unavailable, document that boundary without changing server
configuration.

## Common mistakes and how to recover

- **Lesson-specific semantic mistake:** Do not skip this worked-model requirement: Query pgstatactivity, exclude pgbackendpid(), and calculate runtime only for active statements. For one row, read user, state, wait type/event, and query together; a long duration alone does not prove a fault or authorize termination.
- **Unexpected row count:** display keys before aggregates, count rows after
  each join/filter stage, and find the first stage whose grain differs from the
  contract. Do not hide fanout with `DISTINCT`.
- **Unexpected `NULL` or missing row:** decide whether the fact is unknown,
  inapplicable, zero, or absent before using `COALESCE`; inspect outer-join
  predicate placement and empty-input aggregate behavior.
- **Unstable top/first/last output:** add `ORDER BY` with a unique final
  tie-breaker before `LIMIT` or order-sensitive windows/aggregates.
- **`psql` stops on an error:** fix the first error shown by
  `ON_ERROR_STOP`, restore the declared transaction/setup state, and rerun the
  complete file. A later successful statement does not validate a partial run.

## Self-check

- Can you tell whether evidence describes a current session or historical
  aggregates?
- Have you avoided extension installation, statistics resets, cancellation, and
  termination?

## Next step

Continue to [Day 45 — optimization project](day45_phase3_optimization_project.md).

## Deep dive and reference

## What you will learn

- Find active statements and calculate their current runtime.
- Interpret wait events before deciding that a query is stuck.
- Read optional aggregate statement statistics when the extension is available.

## How the learner script works

The starter queries `pg_stat_activity`, then runs `EXPLAIN ANALYZE` on recent
category units. Its `pg_stat_statements` query is commented because the
extension may require server configuration and elevated access.

For PostgreSQL 16, the relevant extension columns include `calls`,
`total_exec_time`, and `mean_exec_time`. Use the current `_exec_time` names
rather than column names from older PostgreSQL examples.

## Practice map

Use the numbered **Exercises** section above as the single authoritative practice contract. Its prompts, expected shapes, and verification checks map one-for-one to the learner SQL and both solution companions.

## Interpretation and safety

- A long-running query can be legitimate; inspect owner, purpose, wait state,
  locks, and plan before intervening.
- `pg_stat_statements` aggregates normalized statement history; it is not a list
  of currently active sessions.
- Statistics reset, server restarts, and extension availability affect the
  observation window.
- Never install extensions, change `shared_preload_libraries`, reset statistics,
  cancel queries, or terminate backends merely to complete this lesson.
- The executable solution can remain portable by checking for the extension
  view and using dynamic SQL only when it exists.

## Expanded practice lab

Prompts 3–6 build read-only operational judgment. `query_start` measures the
current statement while `xact_start` measures the enclosing transaction; show
both because long idle transactions can retain locks and old snapshots.

Aggregate connection counts instead of exposing full SQL text in a shared
report. For historical workload, examine both `mean_exec_time` and
`total_exec_time`: one reveals expensive calls, the other cumulative load.
Never cancel a session as part of this practice.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-44 — Monitoring Diagnostics.

I have completed the direct catalog prerequisite: `sql-43`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/postgres-60day/companion-guides/day44_monitoring_diagnostics.md
- Answer-free learner SQL: sql/postgres-60day/day44_monitoring_diagnostics.sql

Key terms to teach in context: Wait event, Backend PID, Normalized statement. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Query pgstatactivity, exclude pgbackendpid(), and calculate runtime only for active statements. For one row, read user, state, wait type/event, and query together; a long duration alone does not prove a fault or authorize termination.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
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
