# Day 44 — Monitoring and Diagnostics

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 43 — logical backup and recovery](day43_backup_recovery.md)
- **Artifacts:** [learner SQL](../day44_monitoring_diagnostics.sql) ·
  [solution reasoning](../solutions/day44_solutions.md) ·
  [executable solution](../solutions/day44_solutions.sql)

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

Complete the prompts in the [learner SQL](../day44_monitoring_diagnostics.sql).
If `pg_stat_statements` is unavailable, document that capability boundary
instead of changing server configuration.

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
