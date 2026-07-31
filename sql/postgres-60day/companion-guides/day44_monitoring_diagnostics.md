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
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-44/day44_monitoring_diagnostics.sql`. Save it, then run the notebook's
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
on screen are not automatically stored. This lesson introduces or reinforces
Wait event, Backend PID, Normalized statement. Its worked SQL reads or creates `order_items`, `products`, `orders`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: Query pgstatactivity, exclude pgbackendpid(), and calculate runtime only for active statements. For one row, read user, state, wait type/event, and query together; a long duration alone does not prove a fault or authorize termination.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

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

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
2. Conditionally rank `pg_stat_statements` by mean and total time.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. Compare statement age with transaction age.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
4. Summarize connections by database, user, and state.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. Repair a report that ranks only mean duration.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. Identify and explain idle-in-transaction sessions.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.

If the extension is unavailable, document that boundary without changing server
configuration.

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

## Practice — match the learner prompts exactly

1. List the longest-running sessions whose state is `active`, excluding your
   monitoring query with `pid <> pg_backend_pid()`. Include runtime and wait
   event columns.
2. If `pg_stat_statements` is installed and loaded, list the top ten statements
   by total execution time and expose mean execution time as well.

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

I am a complete beginner. Use these checked-in sources:
- Guide: sql/postgres-60day/companion-guides/day44_monitoring_diagnostics.md
- Answer-free learner SQL: sql/postgres-60day/day44_monitoring_diagnostics.sql

The lesson concepts include Wait event, Backend PID, Normalized statement. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: Query pgstatactivity, exclude pgbackendpid(), and calculate runtime only for active statements. For one row, read user, state, wait type/event, and query together; a long duration alone does not prove a fault or authorize termination.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-44/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
