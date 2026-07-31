# SQL-SEC-01 Solutions — Roles, Privileges, and RLS


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_sec_01_roles_privileges_rls_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_sec_01_roles_privileges_rls_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Role, Owner, Privilege, Least privilege, Schema USAGE, Search path. Its worked-model focus is:
The script first queries pgroles and stores a Boolean for a psql \if. Restricted installations print a safe skip and current capability summary. No attempted CREATE ROLE is used as feature detection, so an expected denial does not leave a failed transaction or noisy partial setup.

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

Run the optional hands-on solution with:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_sec_01_roles_privileges_rls_solutions.sql
```

It performs the same capability check as the learner file. With role-admin
capability it creates NOLOGIN course roles inside one transaction; without that
capability it prints a read-only skip. Normal completion leaves no roles,
memberships, grants, or schema.

## Exercise 1 — Prove both privilege layers

`has_schema_privilege(role, schema, 'USAGE')` and
`has_table_privilege(role, table, 'SELECT')` answer different questions.
Schema `USAGE` permits object lookup but no table operation. Table `SELECT`
permits the operation but cannot make a hidden schema path accessible.

The executable solution reports both columns plus `INSERT` for north, south,
and auditor roles. The expected auditor shape is `USAGE=true`, `SELECT=true`,
and `INSERT=false`.

### Reasoning and verification

- **Inputs/evidence:** For sql-sec-01 Exercise 1, test schema USAGE and table SELECT as separate privilege layers, first before schema grants and then after temporarily removing one table grant.
- **Expected result/shape:** For sql-sec-01 Exercise 1, expected output: evidence for table SELECT without schema USAGE, schema USAGE without table SELECT, and a final three-role matrix with USAGE/SELECT true and INSERT false.
- **Independent verification:** For sql-sec-01 Exercise 1, assert the two observed boolean rows equal `(USAGE=false, SELECT=true)` and `(USAGE=true, SELECT=false)`, attempt the corresponding qualified SELECTs, and restore only the intended least-privilege state before later exercises.

## Exercise 2 — Read-only auditor

The solution creates a NOLOGIN `ds60_sec_auditor`, grants schema `USAGE`, lets
the owner's default privileges grant future table `SELECT`, and adds:

```sql
CREATE POLICY auditor_read
ON pro_security_lab.documents
FOR SELECT
TO ds60_sec_auditor
USING (true);
```

The auditor sees both seeded rows because the policy deliberately spans both
tenants. It has no insert, update, delete, or sequence grant. An exception test
proves an insert is denied. The policy does not create a write privilege.

In a real system, an all-tenant auditor is a sensitive role. Its membership,
login path, logging, export controls, and retention policy need review beyond
this SQL lesson.

### Reasoning and verification

- **Inputs/evidence:** For sql-sec-01 Exercise 2, grant the auditor table SELECT via owner defaults, schema USAGE explicitly, and an RLS SELECT policy with `USING (true)`; grant no table writes.
- **Expected result/shape:** For sql-sec-01 Exercise 2, expected output: two tenant rows when SET ROLE auditor, correct north/south definer counts, and an expected insufficient-privilege notice for INSERT.
- **Independent verification:** For sql-sec-01 Exercise 2, assert the auditor sees exactly both seeded IDs, has no INSERT/UPDATE/DELETE privilege, and cannot execute routines except those explicitly granted.

## Exercise 3 — Owner-specific default privileges

`audit_notes` is created by `ds60_sec_owner` after:

```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA pro_security_lab
    GRANT SELECT ON TABLES TO ds60_sec_auditor;
```

The assertion confirms auditor `SELECT` arrived automatically. If another role
created the table, that other role's defaults would apply. Existing tables are
unchanged by `ALTER DEFAULT PRIVILEGES`; use an explicit `GRANT` for them.

### Reasoning and verification

- **Inputs/evidence:** For sql-sec-01 Exercise 3, create one future table as the role whose default privileges were configured and one as a different NOLOGIN owner with schema CREATE authority.
- **Expected result/shape:** For sql-sec-01 Exercise 3, expected output: the auditor has SELECT on `audit_notes` created by `ds60_sec_owner` but not on `other_owner_notes` created by `ds60_sec_other_owner`.
- **Independent verification:** For sql-sec-01 Exercise 3, compare `has_table_privilege` for both tables and state that ALTER DEFAULT PRIVILEGES uses only the current object's creating role—not inherited membership defaults.

## Exercise 4 — Review the definer boundary

The solution's `document_count_for_tenant(text)` demonstrates minimum controls:

- a NOLOGIN owner with narrowly managed membership;
- `SET search_path = pg_catalog`;
- a fully qualified relation;
- a bounded aggregate result rather than arbitrary rows;
- an allow-list for tenant input;
- `PUBLIC` execution revoked; and
- an explicit grant only to the already read-all auditor.

This does not mean every definer routine is safe. Dynamic SQL, writable
temporary schemas, broad owner privileges, mutable helper functions, unexpected
overloads, error leakage, and race conditions can all widen the boundary. Prefer
security-invoker behavior when the caller's grants and RLS can express the rule.

Granting the learner file's arbitrary-tenant owner function to north or south
would bypass their row boundary: the function owner's `current_user` and owner
status can see rows that the caller cannot.

### Reasoning and verification

- **Inputs/evidence:** For sql-sec-01 Exercise 4, create a validated, fixed-search-path SECURITY DEFINER tenant-count function owned by the NOLOGIN owner, revoke PUBLIC, grant only the auditor, and inspect `pg_proc`.
- **Expected result/shape:** For sql-sec-01 Exercise 4, expected output: valid north/south counts, an invalid-parameter rejection for unknown tenant, and catalog rows with owner, `prosecdef`, `proconfig`, and `proacl`.
- **Independent verification:** For sql-sec-01 Exercise 4, test allowed and NULL/unknown inputs under SET ROLE auditor, assert PUBLIC lacks EXECUTE, confirm the owner cannot login, and trace every referenced object as schema-qualified.

## Exercise 5 — RLS bypass cases

- An ordinary table owner normally bypasses RLS.
- `ALTER TABLE ... FORCE ROW LEVEL SECURITY` makes an ordinary owner subject to
  policies in normal operation.
- A superuser bypasses RLS.
- A role with `BYPASSRLS` bypasses RLS.

Therefore a correct RLS test uses the actual low-privilege application roles,
not the migration owner or administrator. `FORCE RLS` can provide defense in
depth for an ordinary owner, but it does not turn a superuser into a meaningful
tenant-policy test identity.

### Reasoning and verification

- **Inputs/evidence:** For sql-sec-01 Exercise 5, SET LOCAL ROLE north and south separately, query the RLS table, then FORCE RLS and test the table owner; inventory superuser/BYPASSRLS separately.
- **Expected result/shape:** For sql-sec-01 Exercise 5, expected output: north sees only north, south sees only south, the forced owner sees zero without a matching policy, and bypass-capable roles are clearly labeled unsuitable tenant-test identities.
- **Independent verification:** For sql-sec-01 Exercise 5, assert one own-tenant row and zero cross-tenant rows for each low-privilege role, distinguish owner bypass before FORCE from forced-owner behavior, and never grant or rely on BYPASSRLS for tenants.

## Exercise 6 — Effective-access inventory

Use `has_*_privilege` functions for the final yes/no matrix because they account
for ownership, membership inheritance, and PUBLIC grants. Pair that with
`aclexplode`/catalog ACLs and `pg_auth_members` to explain *why* access exists.
Report schema, table, column, sequence, and routine privileges separately;
table `INSERT` and sequence `USAGE` are independent.

Evaluate both the login role and every reachable `SET ROLE` target. ACL text
alone misses ownership and inherited capability, while role attributes such as
SUPERUSER or BYPASSRLS can dominate ordinary grants.

### Reasoning and verification

- **Inputs/evidence:** For sql-sec-01 Exercise 6, use PostgreSQL `has_*_privilege` functions to report schema, table, column, sequence, and function access for north, south, and auditor roles.
- **Expected result/shape:** For sql-sec-01 Exercise 6, expected output: one row per role with five distinct privilege booleans and an `effective_source` explanation distinguishing owner-default table grants from direct function grants.
- **Independent verification:** For sql-sec-01 Exercise 6, compare every effective-access boolean row with object ACLs, role membership, ownership, and PUBLIC and record the matching source evidence; do not infer the grant source from a true boolean alone.

## Exercise 7 — Session and execution identity

`SESSION_USER` is the authenticated session identity. `CURRENT_USER` changes
during `SET ROLE` and becomes the routine owner during SECURITY DEFINER
execution. After `RESET ROLE`, current identity returns to the session's active
identity.

An audit commonly records both authenticated actor and effective authorization
identity, plus an application/request identity established through a trusted
channel. Recording only `CURRENT_USER` inside a definer function can make every
action appear to come from its owner.

### Reasoning and verification

- **Inputs/evidence:** For sql-sec-01 Exercise 7, display SESSION_USER/CURRENT_USER before SET ROLE, after SET ROLE auditor, and from inside an auditor-invoked SECURITY DEFINER identity probe.
- **Expected result/shape:** For sql-sec-01 Exercise 7, expected output: authenticated identity remains SESSION_USER; effective identity changes to auditor under SET ROLE and to the function owner inside SECURITY DEFINER.
- **Independent verification:** For sql-sec-01 Exercise 7, compare all three evidence rows and design audit fields that preserve both identities plus the called routine and tenant context.

## Exercise 8 — Fail-closed tenant context

The safe policy maps only exact allowed identities/context values and returns
NULL/false for everything else. Test NULL, empty, case variants, unknown values,
and a reused pooled connection. If a custom setting is used, read it with the
missing-ok form, validate it through a trusted entry point, and reset it on
checkout/check-in.

Never treat a client-writable session variable as authorization by itself. Bind
the tenant to authenticated server-side state and preserve negative tests for
cross-tenant SELECT, INSERT, UPDATE, and DELETE.

### Reasoning and verification

- **Inputs/evidence:** For sql-sec-01 Exercise 8, map exact role names to tenant keys with a fail-closed CASE; test lowercase valid roles, case mismatch, unknown, and NULL.
- **Expected result/shape:** For sql-sec-01 Exercise 8, expected output: four rows with `candidate_role`, `derived_tenant`, and `accepted_identity`; only exact north/south role names are accepted.
- **Independent verification:** For sql-sec-01 Exercise 8, assert unknown, case-changed, and NULL identities derive NULL and `accepted_identity = false`; if a pooled custom setting is adopted instead, validate and transaction-locally reset it.

## Exercise 9 — A narrow writer

Use one coherent API-only design: the writer receives schema `USAGE` and
`EXECUTE` on a fixed-path SECURITY DEFINER insert function, but no table or
identity-sequence grants. The function owner is NOLOGIN, its PUBLIC execution
is revoked, its inputs are validated, and FORCE RLS plus owner-scoped policies
limit it to north rows. `RETURNING` exposes only the inserted ID, tenant, and
title.

Prove that API call, then attempt a direct cross-tenant INSERT, UPDATE, DELETE,
and table SELECT under `SET ROLE ds60_sec_writer`; all must fail. Mixing direct
table grants with this API would add an unused second write path and would no
longer be the minimum model.

### Reasoning and verification

- **Inputs/evidence:** For sql-sec-01 Exercise 9, create a NOLOGIN API-only writer with schema USAGE and one explicit function EXECUTE grant; give it no table or sequence privileges, while the hardened owner API enforces north-only INSERT/RETURNING under FORCE RLS.
- **Expected result/shape:** For sql-sec-01 Exercise 9, expected output: one returned north document from the insert API; cross-tenant INSERT, direct UPDATE, DELETE, and table SELECT each produce an expected denial.
- **Independent verification:** For sql-sec-01 Exercise 9, SET LOCAL ROLE writer for every probe, assert the API owner/path/ACL and owner-scoped RLS policies in catalogs, confirm no direct table or sequence privilege, and prove the failed operations leave no rows changed.

## Exercise 10 — Offboarding and emergency revocation

First disable login/rotate the external credential and terminate or drain
approved sessions according to incident authority. Revoke memberships and
direct grants, reassign or explicitly handle owned objects, update the relevant
creator's default privileges, and inspect dependent grants/routines/policies.

Use a preserved admin path to avoid locking out recovery. Verify effective
access as the real principal, record exact objects and approvals, keep audit
records, and distinguish reversible access removal from destructive ownership
changes. Cluster-wide commands remain reviewed runbook steps, not lesson SQL.

### Reasoning and verification

- **Inputs/evidence:** For sql-sec-01 Exercise 10, return a non-destructive offboarding plan covering login/session fencing, ownership, memberships, current/default grants, dependent credentials, negative verification, and break-glass recovery.
- **Expected result/shape:** For sql-sec-01 Exercise 10, expected output: seven rows ordered by `step_number` with `action` and `required_evidence`; no cluster-wide destructive command is executed.
- **Independent verification:** For sql-sec-01 Exercise 10, rehearse the plan with an expendable role and record an evidence checklist: owned/dependent-object counts before revocation, denied-login/query results, application smoke-test result, and independently tested recovery administrator.

## Edge cases and alternatives

- Membership inheritance and `SET ROLE` options deserve explicit review in
  PostgreSQL 16+, especially when a login belongs to several group roles.
- Multiple permissive policies combine with OR. Use restrictive policies only
  with a clear composition test.
- Connection pools must reset role and session state between borrowers.
- A session variable used as a tenant identifier needs trusted assignment; a
  client-controlled setting is not authorization.
- Views and functions are API boundaries. Version and test their grants,
  execution context, path, parameters, errors, and row behavior like
  application code.
