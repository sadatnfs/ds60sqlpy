# SQL-PROG-01 Solutions — Routines and Triggers

Run:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_prog_01_routines_triggers_solutions.sql
```

The solution is transactional and leaves no schema behind.

## Exercise 1 — Audit-count function

`status_change_count(bigint)` is `STABLE`, `PARALLEL SAFE`, and security
invoker. It uses `COUNT(*)`, so a NULL or unknown item returns zero rather than
NULL. That behavior is part of the function contract and should be tested.

It is not immutable: inserting an audit row changes the result for the same
argument.

## Exercise 2 — Reassignment procedure

The procedure rejects a NULL/blank destination and updates only rows whose
status is not closed. It participates in the caller's transaction. Closed items
remain with their historical owner.

An alternative is one parameterized `UPDATE` from application code. A procedure
is justified when the command is shared by several trusted callers and its
permissions, migration, observability, and tests are maintained as an API.

## Exercise 3 — Transition guard

The BEFORE trigger compares OLD and NEW status and raises `check_violation` for
`closed -> open`. The solution catches that expected condition and raises a
different exception if the forbidden update succeeds.

A richer workflow should usually model allowed transitions in data or expose
named application commands. A growing chain of trigger `IF` statements hides
business policy and can be difficult to version.

## Exercise 4 — Audit grain

The learner row audit has grain “one changed item status.” The statement audit
has grain “one UPDATE statement,” with an array of affected item IDs. Therefore
two changed rows can legitimately produce two rows in one table and one row in
the other. Reconcile `SUM(changed_rows)` to the row-audit count, not raw table
row counts.

## Exercise 5 — Declarative and transaction boundaries

Allowed status values are row-local and declarative, so a `CHECK` is visible,
automatically enforced for every writer, and simpler than a trigger. Audit
history needs OLD/NEW event context, which fits a trigger.

Functions execute within their statement and cannot commit. Procedures may
control transactions only in permitted top-level `CALL` contexts; nested calls,
explicit outer transactions, exception blocks, and certain procedure attributes
restrict that ability. Default to caller-owned transactions unless the
procedure's transaction contract is deliberate and integration-tested.

## Exercise 6 — Volatility and parallel promises

The audit-count function is STABLE because it reads tables and should see one
statement snapshot; it is not IMMUTABLE because table contents can change.
Procedures and trigger functions that write are VOLATILE. A pure immutable
arithmetic function can be IMMUTABLE only when its result does not depend on
tables, configuration, collation changes, clock, or session state.

Read-only SQL may be parallel safe, but routines that write, manipulate
sequences, use unsafe functions, or depend on backend-local state are unsafe.
PostgreSQL trusts these declarations for planning and constant folding, so an
incorrect promise can reuse a stale result or execute in an invalid worker.

## Exercise 7 — Statement trigger with transition tables

Define an AFTER UPDATE ... REFERENCING OLD TABLE/NEW TABLE trigger. Its function
counts rows whose status is distinct and stores one summary row for that
statement. Transition tables expose the whole affected set and are unavailable
to row triggers.

An UPDATE matching zero rows still fires an applicable statement trigger, so
decide whether to store a zero summary. Reconcile `sum(changed_rows)` to the
row-audit count over the same transaction/test window; raw statement rows have
a different grain.

## Exercise 8 — Exact expected failure

A PL/pgSQL block with an inner `BEGIN ... EXCEPTION WHEN unique_violation`
creates a subtransaction. Changes inside the failed inner block roll back, while
earlier outer-block changes remain. After the handler, assert both facts.

The handler must raise if the statement succeeds and re-raise an unexpected
condition. `WHEN OTHERS THEN NULL` makes permission errors, missing tables, and
programmer mistakes look like passing negative tests.

## Exercise 9 — SECURITY DEFINER hardening

Own the function with a NOLOGIN role that has only the required read access, set
a fixed safe `search_path`, qualify every relation/operator-sensitive object,
avoid writable helper schemas and unsafe dynamic SQL, validate parameters, and
return a bounded result. Revoke PUBLIC execution before granting named callers.

The routine executes with owner privileges, so changing its owner can silently
change its authority. Test identity, RLS behavior, error leakage, overloads,
temporary-object attacks, grants, and dependency changes as part of the API.

## Exercise 10 — Concurrent work claiming

In a short transaction, select eligible IDs in a deterministic order
`FOR UPDATE SKIP LOCKED LIMIT n`, then update only those IDs and commit. Competing
workers skip locks instead of blocking and cannot claim the same row.

This favors throughput, not fairness: a repeatedly locked early row can starve.
Use bounded batches, lease/attempt metadata, retry/backoff, stale-claim recovery,
and monitoring. Keep external work outside the lock transaction or use an
outbox so slow calls do not retain row locks.

## Edge cases

- Concurrent updates may interleave audit timestamps; use keys and transaction
  metadata rather than timestamp order alone.
- Bulk statements need bounded audit volume and retention.
- Disabling triggers for a load changes correctness and requires explicit
  reconciliation.
- Trigger functions should avoid unqualified objects and unexpected recursive
  writes.
