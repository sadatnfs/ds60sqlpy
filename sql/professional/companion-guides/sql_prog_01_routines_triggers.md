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
   **Inputs/evidence:** For sql-prog-01 Exercise 1, read from `pro_routines_lab.work_item_audit`, `pro_routines_lab.work_items`, `OF`, `pro_routines_lab.status_change_count`, and `pro_routines_lab.reassign_open_items`. Build the answer toward `stable`; keep `stable` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-prog-01 Exercise 1, expected output: one row per `stable`. The final columns are `stable`. The final order is `wi.item_id`.
   **Verify:** For sql-prog-01 Exercise 1, run an anti-check that counts rows where NOT ((a.item_id = p_item_id $function$) OR (wi.owner_name = p_from_owner AND wi.status <> 'closed') OR (wi.item_id = 1)); require unique `stable` where the expected grain is one row per key and confirm the projected `stable` against `pro_routines_lab.work_item_audit`, `pro_routines_lab.work_items`, `OF`, `pro_routines_lab.status_change_count`, and `pro_routines_lab.reassign_open_items`. Repeat with `NULL` in `stable` and state whether the row is kept, rejected, or classified.
2. **Reassignment procedure:** reject blank owners and prove closed rows remain
   unchanged.
   **Inputs/evidence:** For sql-prog-01 Exercise 2, complete the reassignment procedure written analysis and support its claims with read-only evidence from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-prog-01 Exercise 2, expected output: a completed the reassignment procedure written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `update`.
   **Verify:** For sql-prog-01 Exercise 2, check the reassignment procedure written analysis against `update`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
3. **Transition guard:** catch the expected denial and compare a trigger with an
   explicit workflow model.
   **Inputs/evidence:** For sql-prog-01 Exercise 3, complete the transition guard written analysis and support its claims with read-only evidence from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-prog-01 Exercise 3, expected output: a completed the transition guard written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `check_violation`, and `if`.
   **Verify:** For sql-prog-01 Exercise 3, check the transition guard written analysis against `check_violation`, and `if`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
4. **Audit grain:** reconcile one row per changed row with one row per statement.
   **Inputs/evidence:** For sql-prog-01 Exercise 4, read from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Build the answer toward `changed_rows`; keep `changed_rows` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-prog-01 Exercise 4, expected output: one row per `changed_rows`. The final columns are `changed_rows`.
   **Verify:** For sql-prog-01 Exercise 4, reselect the returned keys directly from the source; require unique `changed_rows` where the expected grain is one row per key and confirm the projected `changed_rows` against `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Add one source row with a new `changed_rows`; verify the result gains exactly one row carrying that `changed_rows` value.
5. **Declarative boundary:** explain checks, trigger use, function transactions,
   and top-level procedure transactions.
   **Inputs/evidence:** For sql-prog-01 Exercise 5, complete the declarative boundary written analysis and support its claims with read-only evidence from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Mark unverified assumptions explicitly.
   **Expected result/shape:** For sql-prog-01 Exercise 5, expected output: a completed the declarative boundary written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `call`.
   **Verify:** For sql-prog-01 Exercise 5, check the declarative boundary written analysis against `call`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
6. **Routine promises:** justify volatility and parallel-safety declarations;
   identify the failure caused by an over-strong promise.
   **Inputs/evidence:** For sql-prog-01 Exercise 6, read from `pg_catalog.pg_proc`, and `pg_catalog.pg_namespace`. Build the answer toward `proname`, `volatility`, and `parallel_mode`; keep `proname` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-prog-01 Exercise 6, expected output: one row per `proname`. The final columns are `proname`, `volatility`, and `parallel_mode`. The final order is `p.proname`.
   **Verify:** For sql-prog-01 Exercise 6, project `proname` plus the raw source columns from `pg_catalog.pg_proc`, and `pg_catalog.pg_namespace` at each join stage; record row count and distinct `proname`, then assert the final `proname`, `volatility`, and `parallel_mode` values match those staged rows without unintended fanout or loss. Add one row for which `(n.nspname = 'pro_routines_lab')` is true and one for which it is false; verify only the matching `proname` value is returned.
7. **Transition tables:** record a statement summary, including the zero-row
   update contract, and reconcile it to row audit.
   **Inputs/evidence:** For sql-prog-01 Exercise 7, read the target keys from `pro_routines_lab.statement_status_summary`, `n.status`, `old_rows`, `new_rows`, and `ON` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-prog-01 Exercise 7, expected output: the command tag and an independently counted set of affected `integer` values. The final columns are `integer`. The final order is `s.summary_id`.
   **Verify:** For sql-prog-01 Exercise 7, materialize the intended `integer` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.statement_status_summary`, `n.status`, `old_rows`, `new_rows`, and `ON` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `integer` values in both cases.
8. **Expected error:** catch one exact SQLSTATE in a nested block, prove outer
   work survives, and re-raise anything unexpected.
   **Inputs/evidence:** For sql-prog-01 Exercise 8, read the target keys from `pro_routines_lab.exception_probe` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-prog-01 Exercise 8, expected output: the command tag and an independently counted set of affected `unique_violation` values. The final columns are `unique_violation`.
   **Verify:** For sql-prog-01 Exercise 8, materialize the intended `unique_violation` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.exception_probe` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `unique_violation` values in both cases.
9. **Definer hardening:** review fixed search path, qualified objects, owner,
   inputs, PUBLIC revocation, and explicit execution grants.
   **Inputs/evidence:** For sql-prog-01 Exercise 9, read from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Build the answer toward `search_path`; keep `search_path` visible whenever the result has row-level grain.
   **Expected result/shape:** For sql-prog-01 Exercise 9, expected output: one row per `search_path`. The final columns are `search_path`.
   **Verify:** For sql-prog-01 Exercise 9, reselect the returned keys directly from the source; require unique `search_path` where the expected grain is one row per key and confirm the projected `search_path` against `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Add one source row with a new `search_path`; verify the result gains exactly one row carrying that `search_path` value.
10. **Concurrent claims:** design deterministic `FOR UPDATE SKIP LOCKED`
    batching with transaction, retry, fairness, and starvation boundaries.
   **Inputs/evidence:** For sql-prog-01 Exercise 10, read the target keys from `pro_routines_lab.claim_queue`, and `SKIP` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
   **Expected result/shape:** For sql-prog-01 Exercise 10, expected output: one `RETURNING` row per affected `affected_row_count` plus the command tag, with pre-write and post-write values that reconcile. The final columns are `affected_row_count`, and `command_tag`.
   **Verify:** For sql-prog-01 Exercise 10, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.claim_queue`, and `SKIP` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.

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
