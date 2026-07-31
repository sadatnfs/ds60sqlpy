# SQL-SEC-01 — Roles, Privileges, and Row-Level Security

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-found-02` and `sql-39`
- **Prerequisites:** [SQL-FOUND-01 — relational design](sql_found_01_relational_design.md),
  [SQL-FOUND-02 — migrations](sql_found_02_versioned_migrations.md), SQL Day 38
  transactions, [SQL Day 39 locks and deadlocks](../../postgres-60day/companion-guides/day39_locks_deadlocks.md),
  and the disposable `advanced_sql_training` database.
- **Optional capability:** hands-on role tests require the connected PostgreSQL
  role to have `CREATEROLE` or superuser status. The default script checks first
  and safely skips without creating anything when that capability is absent.
- **Artifacts:** [learner SQL](../lessons/sql_sec_01_roles_privileges_rls.sql) ·
  [solution reasoning](../solutions/sql_sec_01_roles_privileges_rls_solutions.md) ·
  [executable solution](../solutions/sql_sec_01_roles_privileges_rls_solutions.sql)

This command is portable across Windows PowerShell, macOS, and Linux:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_sec_01_roles_privileges_rls.sql
```

Do not connect as an administrator to a shared or valuable database merely to
make the optional path run. The lab creates only NOLOGIN roles inside one
transaction and ends with `ROLLBACK`; it never sets passwords, changes server
configuration, or grants broad access.

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

2. Open **SQL-SEC-01 — Schemas, Roles, Privileges, and Row-Level Security** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-sec-01/sql_sec_01_roles_privileges_rls.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Some demonstrations require privileges or server features a normal course role may not have. Run the capability check first. The supported default path still teaches inspection and design without creating cluster-wide roles, extensions, or replication objects.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_sec_01_roles_privileges_rls.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_sec_01_roles_privileges_rls.sql
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
Role, Owner, Privilege, Least privilege, Schema USAGE, Search path. Its worked SQL reads or creates `pg_catalog.pg_roles`, `pro_security_lab.documents`, `pro_security_lab.announcements`, `pro_security_lab.owner_context_documents`, `pro_security_lab.visible_documents`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: The script first queries pgroles and stores a Boolean for a psql \if. Restricted installations print a safe skip and current capability summary. No attempted CREATE ROLE is used as feature detection, so an expected denial does not leave a failed transaction or noisy partial setup.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/professional/lessons/sql_sec_01_roles_privileges_rls.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
SELECT COALESCE(
    (
        SELECT r.rolsuper OR r.rolcreaterole
        FROM pg_catalog.pg_roles AS r
        WHERE r.rolname = CURRENT_USER
    ),
    false
) AS ds60_can_manage_roles
;
```

**How to read it:** Example 1 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
SELECT NOT EXISTS (
        SELECT 1
        FROM pg_catalog.pg_roles AS r
        WHERE r.rolname IN (
            'ds60_sec_owner',
            'ds60_sec_north',
            'ds60_sec_south'
        )
    ) AS ds60_role_names_available
;
```

**How to read it:** Example 2 returns a table-shaped result. Read `FROM`/`JOIN` as the input relation, then filters, grouping or windows, and finally the selected columns. Predict the keys before running it; The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

## Learning objectives

- Separate ownership from privileges, explain schema `USAGE` and a safe
  `search_path`, and grant minimum table/sequence/function capabilities.
- Define creator-specific default privileges and compare invoker with definer
  execution contexts.
- Test row-level security (RLS) as different roles and explain owner,
  superuser, and `BYPASSRLS` exceptions.

## Vocabulary and concepts

- **Role:** a PostgreSQL identity that may own objects, receive privileges, and
  optionally allow login. Group-like NOLOGIN roles are useful privilege bundles.
- **Owner:** the role with authority to alter or drop an object and normally
  grant its privileges. Ownership is stronger than a list of grants.
- **Privilege:** a specific allowed operation such as schema `USAGE`, table
  `SELECT`, sequence `USAGE`, or function `EXECUTE`.
- **Least privilege:** give a role only the operations, objects, rows, and
  columns required for its task.
- **Schema USAGE:** permission to resolve and access objects inside a schema; it
  does not grant operations on those objects.
- **Search path:** the ordered schemas used for unqualified names. An unsafe
  writable schema early in the path can redirect a lookup.
- **Default privileges:** grants applied to future objects created by one
  specific owner; they do not rewrite existing objects or all creators.
- **Security invoker:** execute using the caller's permission and RLS context.
- **Security definer:** execute with the routine owner's `current_user` and
  privileges; powerful, but dangerous without a narrow interface and safe path.
- **Row-level security:** policies that add per-role row filters and write
  checks after the table privilege layer permits an operation.
- **USING:** policy expression selecting which existing rows are visible or
  targetable.
- **WITH CHECK:** policy expression validating a proposed inserted or updated
  row.

## Worked example / walkthrough

The script first queries `pg_roles` and stores a Boolean for a `psql` `\if`.
Restricted installations print a safe skip and current capability summary. No
attempted `CREATE ROLE` is used as feature detection, so an expected denial does
not leave a failed transaction or noisy partial setup.

On the optional admin path, three NOLOGIN roles are created:

- `ds60_sec_owner` owns the isolated schema and creates its objects.
- `ds60_sec_north` operates only north-tenant rows.
- `ds60_sec_south` operates only south-tenant rows.

The current training role receives temporary membership in the owner role so
the script can use `SET ROLE`. Every role, grant, object, policy, and membership
is transactional and disappears at the final rollback.

The privilege layers are intentionally separate:

1. `USAGE` allows names inside `pro_security_lab` to resolve.
2. `SELECT` arrives through owner-specific default table privileges.
3. Column-level `INSERT` and `UPDATE` grants allow only the required writes.
4. Sequence `USAGE`/`SELECT` supports generated identity values.
5. Function `EXECUTE` is revoked from `PUBLIC` and granted explicitly.
6. RLS filters permitted table operations to the active tenant.

Default privileges are set while `current_user` is `ds60_sec_owner`, before
tables and views are created. `announcements` proves that future objects inherit
the intended `SELECT`. If another role creates a table, that creator's defaults
apply instead.

The select, insert, and update policies map the active NOLOGIN role to one
`tenant_key`. North and south run the same invoker view but receive different
rows. North can insert a north row and update north content. A south insert is
rejected by `WITH CHECK`; a delete is rejected earlier because `DELETE` was
never granted. The anonymous test blocks catch those exact expected failures
and fail if the forbidden statement unexpectedly succeeds.

`visible_documents` uses PostgreSQL's `security_invoker=true` view option, so
the caller's table grants and RLS policies apply. A default owner-context view
is created only to inspect the boundary and is explicitly revoked from tenant
roles.

Functions are `SECURITY INVOKER` unless declared otherwise.
`visible_document_count()` returns the caller's RLS-filtered count.
`owner_document_count(text)` is `SECURITY DEFINER`, fixes `search_path` to
`pg_catalog`, fully qualifies its table, returns a narrow aggregate, revokes
`PUBLIC`, and is not granted to tenant roles. Even with those controls, its
arbitrary tenant parameter would be an authorization bypass if exposed to a
role that should see only its own tenant.

RLS is not a substitute for grants. A role needs the underlying operation
privilege before a policy matters. Table owners normally bypass RLS unless
`FORCE ROW LEVEL SECURITY` is enabled. Superusers and roles with `BYPASSRLS`
still bypass policies; test with ordinary application-like roles.

## Exercises

Complete all ten prompts in the learner file. Begin with privilege introspection,
add a read-only auditor role and policy, prove the owner-specific default grant,
review the definer routine's boundary and RLS bypass, then cover effective
access, identity context, fail-closed tenancy, a narrow writer, and revocation.
Keep new roles inside the existing transaction and do not add `LOGIN`, passwords,
`SUPERUSER`, `BYPASSRLS`, database-wide grants, or `PUBLIC` access.

For denied operations, use a small exception-catching test like the worked
examples. A forbidden action that succeeds must fail the lesson rather than
print a reassuring message.

Security work is complete only when both allowed and denied paths are proven:

1. **Two-layer reads:** show schema `USAGE` and table `SELECT` independently.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
2. **Auditor:** create a NOLOGIN read-only role, explicit policy, positive read
   test, and negative write tests.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
3. **Default privileges:** prove which object owner’s future table receives the
   grant and which different owner does not.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
4. **Definer boundary:** inventory owner, search path, qualification, parameter,
   PUBLIC, grant, and RLS risks around the routine.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. **RLS bypass:** compare ordinary caller, owner, forced owner, BYPASSRLS, and
   superuser semantics without granting bypass attributes.
   **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
   **Verify:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
6. **Effective access:** reconcile schema, relation, column, sequence, routine,
   membership, inheritance, and PUBLIC access.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
7. **Identity context:** observe `SESSION_USER` and `CURRENT_USER` across
   `SET ROLE` and a definer call; choose audit identities deliberately.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
8. **Fail-closed tenancy:** test NULL, case variants, unknown tenants, and
   unvalidated/reset session context.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
9. **Narrow writer:** prove only required insert columns/sequence/return values
   work and all unrelated writes or reads fail.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
10. **Revocation runbook:** document sessions, membership, ownership, default
    grants, dependent ACLs, verification, recovery, and durable audit evidence.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

## Self-check

- Does the no-admin path exit successfully without attempting a mutation?
- Do north and south see different deterministic row sets through the same
  security-invoker view?
- Does a valid same-tenant insert succeed and a cross-tenant insert fail?
- Does the absence of `DELETE` block deletion before a policy can broaden it?
- Can you identify the object creator whose default privileges took effect?
- Is every definer routine fully qualified, fixed-path, narrow, and revoked from
  `PUBLIC` before any deliberate grant?
- Do owner/superuser bypass caveats appear in your threat model and tests?
- Does the final rollback remove the schema, roles, and memberships?

## Common pitfalls

- Granting `ALL` at the database or schema level is not a shortcut for designing
  an application role.
- Schema `USAGE` alone cannot read tables, and a table grant is unusable without
  access to its schema.
- A permissive `search_path` can make an unqualified name resolve to an
  attacker-controlled object.
- Default privileges are not retroactive and are scoped to the object creator.
- Identity/serial-backed inserts may need sequence privileges in addition to
  table privileges.
- Multiple permissive RLS policies combine with OR; restrictive policies have
  different composition rules.
- Testing as the table owner or a superuser can make a broken policy appear to
  work because those roles bypass RLS.
- `SECURITY DEFINER` is not an authorization system by itself. Parameters,
  ownership, grants, path resolution, SQL injection, and returned data all need
  review.
- Role creation is cluster-wide, so even disposable role labs belong only on a
  disposable local server or explicitly approved training cluster.

## Next step

Revisit SQL Days 38–44 with separate owner, migration, application, and
read-only operational roles in mind. Then continue to the future professional
modules on routines/triggers, SQL contract tests, index operations, and recovery
rehearsals; use the [curriculum gap backlog](../../../docs/curriculum-gap-backlog.md)
to see their planned order.

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-sec-01 — Schemas, Roles, Privileges, and Row-Level Security.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/professional/companion-guides/sql_sec_01_roles_privileges_rls.md
- Answer-free learner SQL: sql/professional/lessons/sql_sec_01_roles_privileges_rls.sql

The lesson concepts include Role, Owner, Privilege, Least privilege, Schema USAGE, Search path. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: The script first queries pgroles and stores a Boolean for a psql \if. Restricted installations print a safe skip and current capability summary. No attempted CREATE ROLE is used as feature detection, so an expected denial does not leave a failed transaction or noisy partial setup.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-sec-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
