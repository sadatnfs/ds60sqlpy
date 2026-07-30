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

## Edge cases

- Concurrent updates may interleave audit timestamps; use keys and transaction
  metadata rather than timestamp order alone.
- Bulk statements need bounded audit volume and retention.
- Disabling triggers for a load changes correctness and requires explicit
  reconciliation.
- Trigger functions should avoid unqualified objects and unexpected recursive
  writes.

