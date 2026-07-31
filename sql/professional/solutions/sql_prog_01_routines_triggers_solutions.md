# SQL-PROG-01 Solutions — Routines and Triggers


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_prog_01_routines_triggers_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_prog_01_routines_triggers_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Routine, Function, Procedure, Volatility, Security invoker/definer, Trigger. Its worked-model focus is:
openitemcount(text) is a STABLE, PARALLEL SAFE, SECURITY INVOKER SQL function. It reads one statement snapshot and composes inside SELECT. Do not label a routine IMMUTABLE merely because its source text looks simple: a table-reading function changes when table data changes.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 1, create the STABLE SQL function `status_change_count(p_item_id bigint)` over `work_item_audit`, with the explicit policy that NULL or an unknown ID returns zero.
- **Expected result/shape:** For sql-prog-01 Exercise 1, expected output: one scalar count per invocation plus a four-row probe matrix demonstrating zero, one, multiple, and NULL-input cases; every count is a nonnegative bigint.
- **Independent verification:** For sql-prog-01 Exercise 1, compare each function result with an independent filtered `COUNT(*)`, assert item 1 has multiple audits, item 3 has one, an absent ID has zero, and NULL has zero because SQL equality matches no row.

## Exercise 2 — Reassignment procedure

The procedure rejects a NULL/blank destination and updates only rows whose
status is not closed. It participates in the caller's transaction. Closed items
remain with their historical owner.

An alternative is one parameterized `UPDATE` from application code. A procedure
is justified when the command is shared by several trusted callers and its
permissions, migration, observability, and tests are maintained as an API.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 2, create and call `reassign_open_items(p_from_owner, p_to_owner)`, rejecting NULL/blank destinations before updating only source-owner rows whose status is not `closed`.
- **Expected result/shape:** For sql-prog-01 Exercise 2, expected output: a successful CALL that moves Morgan's eligible item to Taylor, while Morgan's closed item remains unchanged; a blank destination is caught as SQLSTATE class `check_violation`.
- **Independent verification:** For sql-prog-01 Exercise 2, snapshot eligible and closed source rows before CALL, reconcile the changed target set afterward, and prove the nested invalid CALL changes no owner values.

## Exercise 3 — Transition guard

The BEFORE trigger compares OLD and NEW status and raises `check_violation` for
`closed -> open`. The solution catches that expected condition and raises a
different exception if the forbidden update succeeds.

A richer workflow should usually model allowed transitions in data or expose
named application commands. A growing chain of trigger `IF` statements hides
business policy and can be difficult to version.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 3, use a BEFORE UPDATE row trigger to reject direct `closed` to `open` transitions and primary-key mutation, returning NEW for allowed updates.
- **Expected result/shape:** For sql-prog-01 Exercise 3, expected output: allowed transitions succeed, direct reopen and identity mutation each emit an expected rejection notice, and rejected rows retain their original values.
- **Independent verification:** For sql-prog-01 Exercise 3, attempt both an allowed `closed` to `in_progress` transition and a forbidden `closed` to `open` transition, record SQLSTATE `23514`, and reselect the row after each attempt.

## Exercise 4 — Audit grain

The learner row audit has grain “one changed item status.” The statement audit
has grain “one UPDATE statement,” with an array of affected item IDs. Therefore
two changed rows can legitimately produce two rows in one table and one row in
the other. Reconcile `SUM(changed_rows)` to the row-audit count, not raw table
row counts.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 4, compare row-level status audits with the statement-level summary produced by one two-row status UPDATE.
- **Expected result/shape:** For sql-prog-01 Exercise 4, expected output: one reconciliation row with `row_audit_records = 2`, `statement_audit_records = 1`, and `statement_changed_status_rows = 2`.
- **Independent verification:** For sql-prog-01 Exercise 4, filter row audits to the two known item IDs and transition, identify the one matching statement summary, and explain that row-audit grain is one changed item while statement-audit grain is one UPDATE statement.

## Exercise 5 — Declarative and transaction boundaries

Allowed status values are row-local and declarative, so a `CHECK` is visible,
automatically enforced for every writer, and simpler than a trigger. Audit
history needs OLD/NEW event context, which fits a trigger.

Functions execute within their statement and cannot commit. Procedures may
control transactions only in permitted top-level `CALL` contexts; nested calls,
explicit outer transactions, exception blocks, and certain procedure attributes
restrict that ability. Default to caller-owned transactions unless the
procedure's transaction contract is deliberate and integration-tested.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 5, return a rule-to-mechanism decision matrix covering a row-local CHECK, OLD/NEW trigger, query function, and multi-step procedure.
- **Expected result/shape:** For sql-prog-01 Exercise 5, expected output: four rows with `rule`, `mechanism`, and `reason`, ordered deterministically by rule.
- **Independent verification:** For sql-prog-01 Exercise 5, reject one disallowed status through the CHECK, prove the transition trigger sees OLD/NEW, and state that functions cannot transaction-control while a procedure may do so only at an allowed top-level CALL boundary.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 6, inspect `pg_proc`/`pg_namespace` for every lab function and procedure, including kind, name, identity arguments, volatility, parallel mode, security mode, and routine settings.
- **Expected result/shape:** For sql-prog-01 Exercise 6, expected output: one row per routine signature, ordered by routine name, with overloaded routines distinguishable through `identity_arguments`.
- **Independent verification:** For sql-prog-01 Exercise 6, compare catalog values with every `CREATE FUNCTION/PROCEDURE` declaration and explain that falsely promising STABLE/IMMUTABLE or PARALLEL SAFE can permit invalid planner assumptions and wrong results.

## Exercise 7 — Statement trigger with transition tables

Define an AFTER UPDATE statement trigger with REFERENCING OLD TABLE and
NEW TABLE. Its function
counts rows whose status is distinct and stores one summary row for that
statement. Transition tables expose the whole affected set and are unavailable
to row triggers.

An UPDATE matching zero rows still fires an applicable statement trigger, so
decide whether to store a zero summary. Reconcile `sum(changed_rows)` to the
row-audit count over the same transaction/test window; raw statement rows have
a different grain.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 7, create an AFTER UPDATE statement trigger with OLD/NEW transition tables, joining on the enforced immutable `item_id`, then run a multirow title update and a truly zero-target `WHERE false` update.
- **Expected result/shape:** For sql-prog-01 Exercise 7, expected output: one summary row `(matched_rows=2, changed_status_rows=0)`, one `(0,0)` row for the empty target, and one `(2,2)` row for a two-item status change.
- **Independent verification:** For sql-prog-01 Exercise 7, assert exactly one summary per UPDATE statement, reconcile changed-status counts with row audits, prove the zero-target statement records `(0,0)`, and keep `item_id` immutable so transition-table pairing cannot undercount.

## Exercise 8 — Exact expected failure

A PL/pgSQL block with an inner `BEGIN ... EXCEPTION WHEN unique_violation`
creates a subtransaction. Changes inside the failed inner block roll back, while
earlier outer-block changes remain. After the handler, assert both facts.

The handler must raise if the statement succeeds and re-raise an unexpected
condition. `WHEN OTHERS THEN NULL` makes permission errors, missing tables, and
programmer mistakes look like passing negative tests.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 8, insert an outer marker, provoke one duplicate key inside a nested PL/pgSQL exception block, and catch only `unique_violation`.
- **Expected result/shape:** For sql-prog-01 Exercise 8, expected output: one expected NOTICE; the outer marker remains, while both inner `duplicate` inserts are absent because the inner block rolled back.
- **Independent verification:** For sql-prog-01 Exercise 8, query `exception_probe` for both keys after the handler and fail unless outer count is one and duplicate count is zero; never use a silent `WHEN OTHERS` branch.

## Exercise 9 — SECURITY DEFINER hardening

Own the function with a NOLOGIN role that has only the required read access, set
a fixed safe `search_path`, qualify every relation/operator-sensitive object,
avoid writable helper schemas and unsafe dynamic SQL, validate parameters, and
return a bounded result. Revoke PUBLIC execution before granting named callers.

The routine executes with owner privileges, so changing its owner can silently
change its authority. Test identity, RLS behavior, error leakage, overloads,
temporary-object attacks, grants, and dependency changes as part of the API.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 9, inventory actual routine owner/security/path/ACL metadata, then return an explicitly design-only six-step SECURITY DEFINER hardening checklist; this lesson creates no definer routine.
- **Expected result/shape:** For sql-prog-01 Exercise 9, expected output: catalog rows proving every lab routine is security-invoker, followed by six ordered controls covering NOLOGIN ownership, fixed path, qualified objects, validation, PUBLIC revocation, narrow grant, and catalog verification.
- **Independent verification:** For sql-prog-01 Exercise 9, require `prosecdef = false` for the executable lab and treat the checklist as proposed policy; perform privileged role/grant validation only in SQL-SEC-01 rather than implying it happened here.

## Exercise 10 — Concurrent work claiming

In a short transaction, select eligible IDs in a deterministic order
`FOR UPDATE SKIP LOCKED LIMIT n`, then update only those IDs and commit. Competing
workers skip locks instead of blocking and cannot claim the same row.

This favors throughput, not fairness: a repeatedly locked early row can starve.
Use bounded batches, lease/attempt metadata, retry/backoff, stale-claim recovery,
and monitoring. Keep external work outside the lock transaction or use an
outbox so slow calls do not retain row locks.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 10, select the first two unclaimed queue rows by `queue_id` under `FOR UPDATE SKIP LOCKED`, then update those exact rows with a worker and timestamp.
- **Expected result/shape:** For sql-prog-01 Exercise 10, expected output: two `RETURNING` rows with `queue_id`, `claimed_by`, and `claimed_at`, ordered by the deterministic claim selection.
- **Independent verification:** For sql-prog-01 Exercise 10, reconcile returned IDs with the preselected batch, simulate a second transaction seeing different unlocked rows, keep the lock transaction short, and define retry, stale-lease, and starvation monitoring policies.

## Edge cases

- Concurrent updates may interleave audit timestamps; use keys and transaction
  metadata rather than timestamp order alone.
- Bulk statements need bounded audit volume and retention.
- Disabling triggers for a load changes correctness and requires explicit
  reconciliation.
- Trigger functions should avoid unqualified objects and unexpected recursive
  writes.
