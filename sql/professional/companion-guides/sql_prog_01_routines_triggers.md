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
2. **Reassignment procedure:** reject blank owners and prove closed rows remain
   unchanged.
3. **Transition guard:** catch the expected denial and compare a trigger with an
   explicit workflow model.
4. **Audit grain:** reconcile one row per changed row with one row per statement.
5. **Declarative boundary:** explain checks, trigger use, function transactions,
   and top-level procedure transactions.
6. **Routine promises:** justify volatility and parallel-safety declarations;
   identify the failure caused by an over-strong promise.
7. **Transition tables:** record a statement summary, including the zero-row
   update contract, and reconcile it to row audit.
8. **Expected error:** catch one exact SQLSTATE in a nested block, prove outer
   work survives, and re-raise anything unexpected.
9. **Definer hardening:** review fixed search path, qualified objects, owner,
   inputs, PUBLIC revocation, and explicit execution grants.
10. **Concurrent claims:** design deterministic `FOR UPDATE SKIP LOCKED`
    batching with transaction, retry, fairness, and starvation boundaries.

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
