# SQL-PROG-01 — Functions, Procedures, and Triggers

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisite:** `sql-found-02`
- **Prerequisites:** [SQL-FOUND-02 — versioned migrations](sql_found_02_versioned_migrations.md),
  transactions, constraints, and multirow `UPDATE`.
- **Artifacts:** [learner SQL](../lessons/sql_prog_01_routines_triggers.sql) ·
  [solution reasoning](../solutions/sql_prog_01_routines_triggers_solutions.md) ·
  [executable solution](../solutions/sql_prog_01_routines_triggers_solutions.sql)

Run from the repository root on Windows PowerShell, macOS, or Linux:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_prog_01_routines_triggers.sql
```

The schema, functions, procedures, triggers, and audit rows are created inside
one transaction and removed by `ROLLBACK`.

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

2. Open **SQL-PROG-01 — Functions, Procedures, and Triggers** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Use the **editable-copy link inside the generated notebook**. It opens the ignored learner copy at
   `.learning/sql/sql-prog-01/lesson/workspace/sql/professional/lessons/sql_prog_01_routines_triggers.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_prog_01_routines_triggers.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_prog_01_routines_triggers.sql
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
on screen are not automatically stored. The key vocabulary for this lesson is Routine, Function, Procedure, Volatility, Security invoker/definer, Trigger. Its worked SQL reads or creates `pro_routines_lab.work_items`, `pro_routines_lab.work_item_audit`, `pro_routines_lab.statement_audit`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The worked walkthrough's lesson-specific task is: openitemcount(text) is a STABLE, PARALLEL SAFE, SECURITY INVOKER SQL function. It reads one statement snapshot and composes inside SELECT. Do not label a routine IMMUTABLE merely because its source text looks simple: a table-reading function changes when table data changes.
The first runnable example has a concrete contract: Example 1 must print the expected DDL command tag for `pro_routines_lab.work_items`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state. Its final projection is the columns written in the final `SELECT`. Verify the command tag in `pg_catalog`/`information_schema`, run one accepted value and one value the declared rule rejects, and confirm the lesson rollback removes the course-owned object. Where this query can emit `NULL`, identify the exact source expression and explain whether the output preserves, classifies, or rejects it.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/professional/lessons/sql_prog_01_routines_triggers.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TABLE pro_routines_lab.work_items (
    item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_name text NOT NULL CHECK (btrim(owner_name) <> ''),
    title text NOT NULL CHECK (btrim(title) <> ''),
    status text NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'in_progress', 'closed')),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 1 must print the expected DDL command tag for `pro_routines_lab.work_items`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

### Example 2

```sql
CREATE TABLE pro_routines_lab.work_item_audit (
    audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id bigint NOT NULL,
    old_status text NOT NULL,
    new_status text NOT NULL,
    changed_by text NOT NULL,
    changed_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** Example 2 must print the expected DDL command tag for `pro_routines_lab.work_item_audit`. Verify the object in `pg_catalog.pg_class`, run one accepted behavior and one rejected boundary behavior, and confirm the lesson rollback/cleanup removes only course-owned state.

## Learning objectives

- Create composable SQL functions, caller-transaction procedures, and
  `BEFORE`/`AFTER` triggers.
- Build row-level and statement-level audit trails with transition-table tests.
- Choose volatility and security attributes, distinguish declarative
  constraints from procedural enforcement, and explain where transaction
  control is permitted.

## Vocabulary and concepts

- **Routine:** a function or procedure stored in PostgreSQL.
- **Function:** invoked in an expression or query and returns a value or rows;
  it cannot commit or roll back its caller's transaction.
- **Procedure:** invoked with `CALL`; a top-level procedure can sometimes use
  transaction control, subject to call context and procedure definition.
- **Volatility:** `IMMUTABLE`, `STABLE`, or `VOLATILE`, describing whether a
  routine's result can change and whether it may modify data.
- **Security invoker/definer:** execute with caller or owner privileges.
- **Trigger:** a routine invoked automatically by a table event.
- **OLD/NEW:** row images made available to row triggers.
- **Transition table:** statement-level relation containing all affected OLD or
  NEW rows.
- **Trigger grain:** once per row versus once per statement.

## Worked example / walkthrough

`open_item_count(text)` is a `STABLE`, `PARALLEL SAFE`, `SECURITY INVOKER` SQL
function. It reads one statement snapshot and composes inside `SELECT`. Do not
label a routine `IMMUTABLE` merely because its source text looks simple: a
table-reading function changes when table data changes.

The allowed `status` values remain a `CHECK` constraint. A trigger would hide a
row-local invariant behind procedural code and be harder for tools to inspect.
Triggers are used where their event context is useful:

- a BEFORE row trigger updates `NEW.updated_at`;
- an AFTER row trigger records one row per status transition; and
- an AFTER statement trigger uses `OLD TABLE` and `NEW TABLE` to record the
  changed row count and IDs once per update statement.

`close_owner_items(text)` is a procedure because it represents a command rather
than a query value. It does not commit; the caller owns the transaction. A
procedure may issue `COMMIT`/`ROLLBACK` only from a permitted top-level `CALL`
context, not when nested inside this lesson's explicit transaction, and not
when its definition imposes incompatible `SET` or security-definer restrictions.
Application-managed transactions should normally remain application-managed.

All routines qualify relations and avoid dynamic SQL. When dynamic identifiers
are genuinely required, validate them and use `format('%I', identifier)` or a
client identifier API; never interpolate untrusted text as SQL.

## Exercises

Implement all ten prompts in a scratch copy of the learner script. Start with a
audit-count function, a reassigning procedure, a transition guard trigger,
row-versus-statement grain reconciliation, and constraint/transaction
boundaries; then address routine promises, transition tables, exact errors,
definer hardening, and concurrent claims. Keep tests deterministic and inside
the outer transaction.

The guard exercise is intentionally debatable. A complex workflow may deserve
an explicit transition table and service command rather than a growing trigger.
State the trade-off in your answer.

Use a scratch transaction and label routine volatility, caller/owner identity,
input contract, output grain, side effects, and failure behavior:

1. **Audit count function:** define NULL behavior and verify zero, one, and
   multiple matching rows.
   **Inputs/evidence:** For sql-prog-01 Exercise 1, create the STABLE SQL function `status_change_count(p_item_id bigint)` over `work_item_audit`, with the explicit policy that NULL or an unknown ID returns zero.
   **Expected result/shape:** For sql-prog-01 Exercise 1, expected output: one scalar count per invocation plus a four-row probe matrix demonstrating zero, one, multiple, and NULL-input cases; every count is a nonnegative bigint.
   **Verify:** For sql-prog-01 Exercise 1, compare each function result with an independent filtered `COUNT(*)`, assert item 1 has multiple audits, item 3 has one, an absent ID has zero, and NULL has zero because SQL equality matches no row.
2. **Reassignment procedure:** reject blank owners and prove closed rows remain
   unchanged.
   **Inputs/evidence:** For sql-prog-01 Exercise 2, create and call `reassign_open_items(p_from_owner, p_to_owner)`, rejecting NULL/blank destinations before updating only source-owner rows whose status is not `closed`.
   **Expected result/shape:** For sql-prog-01 Exercise 2, expected output: a successful CALL that moves Morgan's eligible item to Taylor, while Morgan's closed item remains unchanged; a blank destination is caught as SQLSTATE class `check_violation`.
   **Verify:** For sql-prog-01 Exercise 2, snapshot eligible and closed source rows before CALL, reconcile the changed target set afterward, and prove the nested invalid CALL changes no owner values.
3. **Transition guard:** catch the expected denial and compare a trigger with an
   explicit workflow model.
   **Inputs/evidence:** For sql-prog-01 Exercise 3, use a BEFORE UPDATE row trigger to reject direct `closed` to `open` transitions and primary-key mutation, returning NEW for allowed updates.
   **Expected result/shape:** For sql-prog-01 Exercise 3, expected output: allowed transitions succeed, direct reopen and identity mutation each emit an expected rejection notice, and rejected rows retain their original values.
   **Verify:** For sql-prog-01 Exercise 3, attempt both an allowed `closed` to `in_progress` transition and a forbidden `closed` to `open` transition, record SQLSTATE `23514`, and reselect the row after each attempt.
4. **Audit grain:** reconcile one row per changed row with one row per statement.
   **Inputs/evidence:** For sql-prog-01 Exercise 4, compare row-level status audits with the statement-level summary produced by one two-row status UPDATE.
   **Expected result/shape:** For sql-prog-01 Exercise 4, expected output: one reconciliation row with `row_audit_records = 2`, `statement_audit_records = 1`, and `statement_changed_status_rows = 2`.
   **Verify:** For sql-prog-01 Exercise 4, filter row audits to the two known item IDs and transition, identify the one matching statement summary, and explain that row-audit grain is one changed item while statement-audit grain is one UPDATE statement.
5. **Declarative boundary:** explain checks, trigger use, function transactions,
   and top-level procedure transactions.
   **Inputs/evidence:** For sql-prog-01 Exercise 5, return a rule-to-mechanism decision matrix covering a row-local CHECK, OLD/NEW trigger, query function, and multi-step procedure.
   **Expected result/shape:** For sql-prog-01 Exercise 5, expected output: four rows with `rule`, `mechanism`, and `reason`, ordered deterministically by rule.
   **Verify:** For sql-prog-01 Exercise 5, reject one disallowed status through the CHECK, prove the transition trigger sees OLD/NEW, and state that functions cannot transaction-control while a procedure may do so only at an allowed top-level CALL boundary.
6. **Routine promises:** justify volatility and parallel-safety declarations;
   identify the failure caused by an over-strong promise.
   **Inputs/evidence:** For sql-prog-01 Exercise 6, inspect `pg_proc`/`pg_namespace` for every lab function and procedure, including kind, name, identity arguments, volatility, parallel mode, security mode, and routine settings.
   **Expected result/shape:** For sql-prog-01 Exercise 6, expected output: one row per routine signature, ordered by routine name, with overloaded routines distinguishable through `identity_arguments`.
   **Verify:** For sql-prog-01 Exercise 6, compare catalog values with every `CREATE FUNCTION/PROCEDURE` declaration and explain that falsely promising STABLE/IMMUTABLE or PARALLEL SAFE can permit invalid planner assumptions and wrong results.
7. **Transition tables:** record a statement summary, including the zero-row
   update contract, and reconcile it to row audit.
   **Inputs/evidence:** For sql-prog-01 Exercise 7, create an AFTER UPDATE statement trigger with OLD/NEW transition tables, joining on the enforced immutable `item_id`, then run a multirow title update and a truly zero-target `WHERE false` update.
   **Expected result/shape:** For sql-prog-01 Exercise 7, expected output: one summary row `(matched_rows=2, changed_status_rows=0)`, one `(0,0)` row for the empty target, and one `(2,2)` row for a two-item status change.
   **Verify:** For sql-prog-01 Exercise 7, assert exactly one summary per UPDATE statement, reconcile changed-status counts with row audits, prove the zero-target statement records `(0,0)`, and keep `item_id` immutable so transition-table pairing cannot undercount.
8. **Expected error:** catch one exact SQLSTATE in a nested block, prove outer
   work survives, and re-raise anything unexpected.
   **Inputs/evidence:** For sql-prog-01 Exercise 8, insert an outer marker, provoke one duplicate key inside a nested PL/pgSQL exception block, and catch only `unique_violation`.
   **Expected result/shape:** For sql-prog-01 Exercise 8, expected output: one expected NOTICE; the outer marker remains, while both inner `duplicate` inserts are absent because the inner block rolled back.
   **Verify:** For sql-prog-01 Exercise 8, query `exception_probe` for both keys after the handler and fail unless outer count is one and duplicate count is zero; never use a silent `WHEN OTHERS` branch.
9. **Definer hardening:** review fixed search path, qualified objects, owner,
   inputs, PUBLIC revocation, and explicit execution grants.
   **Inputs/evidence:** For sql-prog-01 Exercise 9, inventory actual routine owner/security/path/ACL metadata, then return an explicitly design-only six-step SECURITY DEFINER hardening checklist; this lesson creates no definer routine.
   **Expected result/shape:** For sql-prog-01 Exercise 9, expected output: catalog rows proving every lab routine is security-invoker, followed by six ordered controls covering NOLOGIN ownership, fixed path, qualified objects, validation, PUBLIC revocation, narrow grant, and catalog verification.
   **Verify:** For sql-prog-01 Exercise 9, require `prosecdef = false` for the executable lab and treat the checklist as proposed policy; perform privileged role/grant validation only in SQL-SEC-01 rather than implying it happened here.
10. **Concurrent claims:** design deterministic `FOR UPDATE SKIP LOCKED`
    batching with transaction, retry, fairness, and starvation boundaries.
   **Inputs/evidence:** For sql-prog-01 Exercise 10, select the first two unclaimed queue rows by `queue_id` under `FOR UPDATE SKIP LOCKED`, then update those exact rows with a worker and timestamp.
   **Expected result/shape:** For sql-prog-01 Exercise 10, expected output: two `RETURNING` rows with `queue_id`, `claimed_by`, and `claimed_at`, ordered by the deterministic claim selection.
   **Verify:** For sql-prog-01 Exercise 10, reconcile returned IDs with the preselected batch, simulate a second transaction seeing different unlocked rows, keep the lock transaction short, and define retry, stale-lease, and starvation monitoring policies.

## Self-check

- Can the query function be used in `SELECT` without modifying data?
- Does one two-row update create two row audit records and one statement record?
- Does the statement audit list IDs in deterministic order?
- Does `CALL` participate in the lesson's transaction?
- Does an unexpected forbidden transition make the solution fail?
- Are relations qualified and routines left as `SECURITY INVOKER` unless an
  audited privilege boundary requires otherwise?
- Does rollback remove every routine and trigger?

## Common pitfalls

- Marking a table-reading function `IMMUTABLE` can produce incorrect cached or
  indexed results.
- Row triggers multiply work by affected rows; bulk updates can amplify hidden
  I/O dramatically.
- Statement triggers fire even when zero rows change, so define the recorded
  meaning precisely.
- Recursive triggers can update their own table repeatedly.
- Trigger order and side effects become difficult to reason about when many
  routines mutate `NEW`.
- A SECURITY DEFINER routine needs fixed path, qualified objects, narrow grants,
  and adversarial tests.
- A procedure is not automatic permission to commit inside any call stack.
- DDL and routine changes belong in ordered migrations, not manual production
  console edits.

## Next step

Continue to [SQL-TYPES-01 — PostgreSQL-native types and searchable documents](sql_types_01_native_types_search.md).
Later, combine routines with the migration and contract-test modules so their
signatures, owners, grants, triggers, and side effects are release-tested.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-prog-01 — Functions, Procedures, and Triggers.

I have completed the direct catalog prerequisite: `sql-found-02`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_prog_01_routines_triggers.md
- Answer-free learner SQL: sql/professional/lessons/sql_prog_01_routines_triggers.sql

Key terms to teach in context: Routine, Function, Procedure, Volatility, Security invoker/definer, Trigger. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: openitemcount(text) is a STABLE, PARALLEL SAFE, SECURITY INVOKER SQL function. It reads one statement snapshot and composes inside SELECT. Do not label a routine IMMUTABLE merely because its source text looks simple: a table-reading function changes when table data changes.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-prog-01/ working copy. Never point setup, reset, DDL, or DML
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
