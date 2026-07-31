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

- **Inputs/evidence:** For sql-prog-01 Exercise 1, read from `pro_routines_lab.work_item_audit`, `pro_routines_lab.work_items`, `OF`, `pro_routines_lab.status_change_count`, and `pro_routines_lab.reassign_open_items`. Build the answer toward `stable`; keep `stable` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-prog-01 Exercise 1, expected output: one row per `stable`. The final columns are `stable`. The final order is `wi.item_id`.
- **Independent verification:** For sql-prog-01 Exercise 1, run an anti-check that counts rows where NOT ((a.item_id = p_item_id $function$) OR (wi.owner_name = p_from_owner AND wi.status <> 'closed') OR (wi.item_id = 1)); require unique `stable` where the expected grain is one row per key and confirm the projected `stable` against `pro_routines_lab.work_item_audit`, `pro_routines_lab.work_items`, `OF`, `pro_routines_lab.status_change_count`, and `pro_routines_lab.reassign_open_items`. Repeat with `NULL` in `stable` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-prog-01 Exercise 1, inspect the source keys that survive `WHERE`; then check `wi.item_id` before applying the row cap.
- **Clause check:** For sql-prog-01 Exercise 1, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_routines_lab.work_item_audit`, `pro_routines_lab.work_items`, `OF`, `pro_routines_lab.status_change_count`, and `pro_routines_lab.reassign_open_items`, preserve one row per `stable`, and finish with `stable` ordered by `wi.item_id`.
- **Alternative/trade-off:** For sql-prog-01 Exercise 1, the chosen form is justified by this lesson-specific rationale: `status_change_count(bigint)` is `STABLE`, `PARALLEL SAFE`, and security invoker. Evaluate another form against the concrete expected result (one row per `stable`) and the verification above.
- **Edge case:** Repeat with `NULL` in `stable` and state whether the row is kept, rejected, or classified.

## Exercise 2 — Reassignment procedure

The procedure rejects a NULL/blank destination and updates only rows whose
status is not closed. It participates in the caller's transaction. Closed items
remain with their historical owner.

An alternative is one parameterized `UPDATE` from application code. A procedure
is justified when the command is shared by several trusted callers and its
permissions, migration, observability, and tests are maintained as an API.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 2, complete the reassignment procedure written analysis and support its claims with read-only evidence from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-prog-01 Exercise 2, expected output: a completed the reassignment procedure written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `update`.
- **Independent verification:** For sql-prog-01 Exercise 2, check the reassignment procedure written analysis against `update`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-prog-01 Exercise 2, check the reassignment procedure written analysis against `update`.
- **Clause check:** For sql-prog-01 Exercise 2, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_routines_lab.work_items`, `ON`, and `NEW.status` or label it as proposed policy.
- **Alternative/trade-off:** For sql-prog-01 Exercise 2, the chosen form is justified by this lesson-specific rationale: The procedure rejects a NULL/blank destination and updates only rows whose status is not closed. Evaluate another form against the concrete expected result (a completed the reassignment procedure written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 3 — Transition guard

The BEFORE trigger compares OLD and NEW status and raises `check_violation` for
`closed -> open`. The solution catches that expected condition and raises a
different exception if the forbidden update succeeds.

A richer workflow should usually model allowed transitions in data or expose
named application commands. A growing chain of trigger `IF` statements hides
business policy and can be difficult to version.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 3, complete the transition guard written analysis and support its claims with read-only evidence from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-prog-01 Exercise 3, expected output: a completed the transition guard written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `check_violation`, and `if`.
- **Independent verification:** For sql-prog-01 Exercise 3, check the transition guard written analysis against `check_violation`, and `if`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-prog-01 Exercise 3, check the transition guard written analysis against `check_violation`, and `if`.
- **Clause check:** For sql-prog-01 Exercise 3, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_routines_lab.work_items`, `ON`, and `NEW.status` or label it as proposed policy.
- **Alternative/trade-off:** For sql-prog-01 Exercise 3, the chosen form is justified by this lesson-specific rationale: The BEFORE trigger compares OLD and NEW status and raises `check_violation` for `closed -> open`. Evaluate another form against the concrete expected result (a completed the transition guard written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 4 — Audit grain

The learner row audit has grain “one changed item status.” The statement audit
has grain “one UPDATE statement,” with an array of affected item IDs. Therefore
two changed rows can legitimately produce two rows in one table and one row in
the other. Reconcile `SUM(changed_rows)` to the row-audit count, not raw table
row counts.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 4, read from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Build the answer toward `changed_rows`; keep `changed_rows` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-prog-01 Exercise 4, expected output: one row per `changed_rows`. The final columns are `changed_rows`.
- **Independent verification:** For sql-prog-01 Exercise 4, reselect the returned keys directly from the source; require unique `changed_rows` where the expected grain is one row per key and confirm the projected `changed_rows` against `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Add one source row with a new `changed_rows`; verify the result gains exactly one row carrying that `changed_rows` value.
- **Intermediate relation check:** For sql-prog-01 Exercise 4, select `changed_rows` from `pro_routines_lab.work_items`, `ON`, and `NEW.status` before adding derived columns.
- **Clause check:** For sql-prog-01 Exercise 4, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_routines_lab.work_items`, `ON`, and `NEW.status` or label it as proposed policy.
- **Alternative/trade-off:** For sql-prog-01 Exercise 4, the chosen form is justified by this lesson-specific rationale: The learner row audit has grain “one changed item status.” The statement audit has grain “one UPDATE statement,” with an array of affected item IDs. Evaluate another form against the concrete expected result (one row per `changed_rows`) and the verification above.
- **Edge case:** Add one source row with a new `changed_rows`; verify the result gains exactly one row carrying that `changed_rows` value.

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

- **Inputs/evidence:** For sql-prog-01 Exercise 5, complete the declarative boundary written analysis and support its claims with read-only evidence from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-prog-01 Exercise 5, expected output: a completed the declarative boundary written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `call`.
- **Independent verification:** For sql-prog-01 Exercise 5, check the declarative boundary written analysis against `call`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-prog-01 Exercise 5, check the declarative boundary written analysis against `call`.
- **Clause check:** For sql-prog-01 Exercise 5, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_routines_lab.work_items`, `ON`, and `NEW.status` or label it as proposed policy.
- **Alternative/trade-off:** For sql-prog-01 Exercise 5, the chosen form is justified by this lesson-specific rationale: Allowed status values are row-local and declarative, so a `CHECK` is visible, automatically enforced for every writer, and simpler than a trigger. Evaluate another form against the concrete expected result (a completed the declarative boundary written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

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

- **Inputs/evidence:** For sql-prog-01 Exercise 6, read from `pg_catalog.pg_proc`, and `pg_catalog.pg_namespace`. Build the answer toward `proname`, `volatility`, and `parallel_mode`; keep `proname` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-prog-01 Exercise 6, expected output: one row per `proname`. The final columns are `proname`, `volatility`, and `parallel_mode`. The final order is `p.proname`.
- **Independent verification:** For sql-prog-01 Exercise 6, project `proname` plus the raw source columns from `pg_catalog.pg_proc`, and `pg_catalog.pg_namespace` at each join stage; record row count and distinct `proname`, then assert the final `proname`, `volatility`, and `parallel_mode` values match those staged rows without unintended fanout or loss. Add one row for which `(n.nspname = 'pro_routines_lab')` is true and one for which it is false; verify only the matching `proname` value is returned.
- **Intermediate relation check:** For sql-prog-01 Exercise 6, start with the first relation in `pg_catalog.pg_proc`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `proname` so the exact fanout or loss is visible.
- **Clause check:** For sql-prog-01 Exercise 6, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_catalog.pg_proc`, and `pg_catalog.pg_namespace`, preserve one row per `proname`, and finish with `proname`, `volatility`, and `parallel_mode` ordered by `p.proname`.
- **Alternative/trade-off:** For sql-prog-01 Exercise 6, the chosen form is justified by this lesson-specific rationale: The audit-count function is STABLE because it reads tables and should see one statement snapshot; it is not IMMUTABLE because table contents can change. Evaluate another form against the concrete expected result (one row per `proname`) and the verification above.
- **Edge case:** Add one row for which `(n.nspname = 'pro_routines_lab')` is true and one for which it is false; verify only the matching `proname` value is returned.

## Exercise 7 — Statement trigger with transition tables

Define an AFTER UPDATE ... REFERENCING OLD TABLE/NEW TABLE trigger. Its function
counts rows whose status is distinct and stores one summary row for that
statement. Transition tables expose the whole affected set and are unavailable
to row triggers.

An UPDATE matching zero rows still fires an applicable statement trigger, so
decide whether to store a zero summary. Reconcile `sum(changed_rows)` to the
row-audit count over the same transaction/test window; raw statement rows have
a different grain.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 7, read the target keys from `pro_routines_lab.statement_status_summary`, `n.status`, `old_rows`, `new_rows`, and `ON` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-prog-01 Exercise 7, expected output: the command tag and an independently counted set of affected `integer` values. The final columns are `integer`. The final order is `s.summary_id`.
- **Independent verification:** For sql-prog-01 Exercise 7, materialize the intended `integer` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.statement_status_summary`, `n.status`, `old_rows`, `new_rows`, and `ON` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `integer` values in both cases.
- **Intermediate relation check:** For sql-prog-01 Exercise 7, start with the first relation in `pro_routines_lab.statement_status_summary`, `n.status`, `old_rows`, `new_rows`, and `ON`; after each join, record total rows and distinct `integer` so the exact fanout or loss is visible.
- **Clause check:** For sql-prog-01 Exercise 7, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, aggregate `FILTER`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_routines_lab.statement_status_summary`, `n.status`, `old_rows`, `new_rows`, and `ON`, preserve one row per `integer`, and finish with `integer` ordered by `s.summary_id`.
- **Alternative/trade-off:** For sql-prog-01 Exercise 7, the chosen form is justified by this lesson-specific rationale: Define an AFTER UPDATE . Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `integer` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `integer` values in both cases.

## Exercise 8 — Exact expected failure

A PL/pgSQL block with an inner `BEGIN ... EXCEPTION WHEN unique_violation`
creates a subtransaction. Changes inside the failed inner block roll back, while
earlier outer-block changes remain. After the handler, assert both facts.

The handler must raise if the statement succeeds and re-raise an unexpected
condition. `WHEN OTHERS THEN NULL` makes permission errors, missing tables, and
programmer mistakes look like passing negative tests.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 8, read the target keys from `pro_routines_lab.exception_probe` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-prog-01 Exercise 8, expected output: the command tag and an independently counted set of affected `unique_violation` values. The final columns are `unique_violation`.
- **Independent verification:** For sql-prog-01 Exercise 8, materialize the intended `unique_violation` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.exception_probe` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `unique_violation` values in both cases.
- **Intermediate relation check:** For sql-prog-01 Exercise 8, materialize the intended `unique_violation` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.exception_probe` again and prove rollback or idempotent retry.
- **Clause check:** For sql-prog-01 Exercise 8, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `pro_routines_lab.exception_probe`, preserve one row per `unique_violation`, and finish with `unique_violation`.
- **Alternative/trade-off:** For sql-prog-01 Exercise 8, the chosen form is justified by this lesson-specific rationale: A PL/pgSQL block with an inner `BEGIN . Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `unique_violation` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `unique_violation` values in both cases.

## Exercise 9 — SECURITY DEFINER hardening

Own the function with a NOLOGIN role that has only the required read access, set
a fixed safe `search_path`, qualify every relation/operator-sensitive object,
avoid writable helper schemas and unsafe dynamic SQL, validate parameters, and
return a bounded result. Revoke PUBLIC execution before granting named callers.

The routine executes with owner privileges, so changing its owner can silently
change its authority. Test identity, RLS behavior, error leakage, overloads,
temporary-object attacks, grants, and dependency changes as part of the API.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 9, read from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Build the answer toward `search_path`; keep `search_path` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-prog-01 Exercise 9, expected output: one row per `search_path`. The final columns are `search_path`.
- **Independent verification:** For sql-prog-01 Exercise 9, reselect the returned keys directly from the source; require unique `search_path` where the expected grain is one row per key and confirm the projected `search_path` against `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Add one source row with a new `search_path`; verify the result gains exactly one row carrying that `search_path` value.
- **Intermediate relation check:** For sql-prog-01 Exercise 9, select `search_path` from `pro_routines_lab.work_items`, `ON`, and `NEW.status` before adding derived columns.
- **Clause check:** For sql-prog-01 Exercise 9, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_routines_lab.work_items`, `ON`, and `NEW.status` or label it as proposed policy.
- **Alternative/trade-off:** For sql-prog-01 Exercise 9, the chosen form is justified by this lesson-specific rationale: Own the function with a NOLOGIN role that has only the required read access, set a fixed safe `search_path`, qualify every relation/operator-sensitive object, avoid writable helper schemas and unsafe dynamic SQ. Evaluate another form against the concrete expected result (one row per `search_path`) and the verification above.
- **Edge case:** Add one source row with a new `search_path`; verify the result gains exactly one row carrying that `search_path` value.

## Exercise 10 — Concurrent work claiming

In a short transaction, select eligible IDs in a deterministic order
`FOR UPDATE SKIP LOCKED LIMIT n`, then update only those IDs and commit. Competing
workers skip locks instead of blocking and cannot claim the same row.

This favors throughput, not fairness: a repeatedly locked early row can starve.
Use bounded batches, lease/attempt metadata, retry/backoff, stale-claim recovery,
and monitoring. Keep external work outside the lock transaction or use an
outbox so slow calls do not retain row locks.

### Reasoning and verification

- **Inputs/evidence:** For sql-prog-01 Exercise 10, read the target keys from `pro_routines_lab.claim_queue`, and `SKIP` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-prog-01 Exercise 10, expected output: one `RETURNING` row per affected `affected_row_count` plus the command tag, with pre-write and post-write values that reconcile. The final columns are `affected_row_count`, and `command_tag`.
- **Independent verification:** For sql-prog-01 Exercise 10, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.claim_queue`, and `SKIP` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.
- **Intermediate relation check:** For sql-prog-01 Exercise 10, run `claimable` one at a time. Record each CTE's row count and `affected_row_count` uniqueness before the next stage uses it.
- **Clause check:** For sql-prog-01 Exercise 10, the solution actually uses `WITH`, `FROM`, `WHERE`, `SELECT`, `ORDER BY`, `LIMIT`, and `RETURNING`. Read only those operations: begin at `pro_routines_lab.claim_queue`, and `SKIP`, preserve one row per `affected_row_count`, and finish with `affected_row_count`, and `command_tag`.
- **Alternative/trade-off:** For sql-prog-01 Exercise 10, the chosen form is justified by this lesson-specific rationale: In a short transaction, select eligible IDs in a deterministic order `FOR UPDATE SKIP LOCKED LIMIT n`, then update only those IDs and commit. Evaluate another form against the concrete expected result (one `RETURNING` row per affected `affected_row_count` plus the command tag, with pre-write and post-write values that reconcile) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.

## Edge cases

- Concurrent updates may interleave audit timestamps; use keys and transaction
  metadata rather than timestamp order alone.
- Bulk statements need bounded audit volume and retention.
- Disabling triggers for a load changes correctness and requires explicit
  reconciliation.
- Trigger functions should avoid unqualified objects and unexpected recursive
  writes.
