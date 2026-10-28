# Day 44: Monitoring and Diagnostics

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-44**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-44/lesson/workspace/sql/postgres-60day/day44_monitoring_diagnostics.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-44
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 43; logical backup and recovery](day43_backup_recovery.md)
- **Artifacts:** [learner SQL](../day44_monitoring_diagnostics.sql) ·
  [solution reasoning](../solutions/day44_solutions.md) ·
  [executable solution](../solutions/day44_solutions.sql)

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

These worked excerpts come from `sql/postgres-60day/day44_monitoring_diagnostics.sql`. Use **Whole SQL lesson (psql)** in the unified classroom for the complete file, including its fixture and transaction context. The optional contributor notebook and prepared `psql` routes are described above.

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
   **Verify:** For sql-44 Exercise 2, if the optional view is absent or raises `object_not_in_prerequisite_state` because the module was not preloaded, require an explanatory notice and an empty result. If it is readable, require only the `total_exec_time` and `mean_exec_time` labels, at most 10 rows per label, unique (`ranking`, `userid`, `dbid`, `toplevel`, `queryid`), consecutive `rank_position` values from 1 through N, nonincreasing `total_exec_time` order for its label, nonincreasing `mean_exec_time` order for its label, and values that match a fresh read of `public.pg_stat_statements`.
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
- The executable solution remains portable by checking for the extension view,
  using dynamic SQL only when it exists, and catching only the defined
  installed-but-not-preloaded SQLSTATE around that optional read.

## Expanded practice lab

Prompts 3–6 build read-only operational judgment. `query_start` measures the
current statement while `xact_start` measures the enclosing transaction; show
both because long idle transactions can retain locks and old snapshots.

Aggregate connection counts instead of exposing full SQL text in a shared
report. For historical workload, examine both `mean_exec_time` and
`total_exec_time`: one reveals expensive calls, the other cumulative load.
Never cancel a session as part of this practice.

## Ask an AI tutor about this lesson

An AI tutor is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in the AI tutor:

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
