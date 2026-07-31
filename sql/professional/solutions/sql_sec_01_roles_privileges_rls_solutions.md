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

- **Inputs/evidence:** For sql-sec-01 Exercise 1, complete the two-layer reads written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-sec-01 Exercise 1, expected output: a completed the two-layer reads written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `usage`, `has_schema_privilege`, `has_table_privilege`, and `insert`.
- **Independent verification:** For sql-sec-01 Exercise 1, check the two-layer reads written analysis against `usage`, `has_schema_privilege`, `has_table_privilege`, and `insert`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-sec-01 Exercise 1, check the two-layer reads written analysis against `usage`, `has_schema_privilege`, `has_table_privilege`, and `insert`.
- **Clause check:** For sql-sec-01 Exercise 1, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_catalog.pg_roles`, `PUBLIC`, and `TO` or label it as proposed policy.
- **Alternative/trade-off:** For sql-sec-01 Exercise 1, the chosen form is justified by this lesson-specific rationale: `has_schema_privilege(role, schema, 'USAGE')` and `has_table_privilege(role, table, 'SELECT')` answer different questions. Evaluate another form against the concrete expected result (a completed the two-layer reads written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

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

- **Inputs/evidence:** For sql-sec-01 Exercise 2, change only `auditor_read`, `pro_security_lab.documents`, and `ds60_sec_auditor` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_roles`, `information_schema.role_table_grants`, `pg_catalog.pg_policies`, and `pg_catalog.pg_class` rows.
- **Expected result/shape:** For sql-sec-01 Exercise 2, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `usage`.
- **Independent verification:** For sql-sec-01 Exercise 2, inspect `pg_catalog.pg_roles`, `information_schema.role_table_grants`, `pg_catalog.pg_policies`, and `pg_catalog.pg_class` for `auditor_read`, `pro_security_lab.documents`, and `ds60_sec_auditor`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
- **Intermediate relation check:** For sql-sec-01 Exercise 2, inspect `pg_catalog.pg_roles`, `information_schema.role_table_grants`, `pg_catalog.pg_policies`, and `pg_catalog.pg_class` for `auditor_read`, `pro_security_lab.documents`, and `ds60_sec_auditor`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
- **Clause check:** For sql-sec-01 Exercise 2, the solution actually uses `SELECT`. Read only those operations: begin at `auditor_read`, `pro_security_lab.documents`, and `ds60_sec_auditor`, preserve exactly one summary row, and finish with `usage`.
- **Alternative/trade-off:** For sql-sec-01 Exercise 2, the chosen form is justified by this lesson-specific rationale: The solution creates a NOLOGIN `ds60_sec_auditor`, grants schema `USAGE`, lets the owner's default privileges grant future table `SELECT`, and adds: The auditor sees both seeded rows because the policy delibera. Evaluate another form against the concrete expected result (the requested DDL command tag plus catalog rows and one accepted and one rejected behavior) and the verification above.
- **Edge case:** Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.

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

- **Inputs/evidence:** For sql-sec-01 Exercise 3, read from `ds60_sec_owner`. Compute `ds60_sec_auditor` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-sec-01 Exercise 3, expected output: exactly one aggregate summary row. The final columns are `ds60_sec_auditor`.
- **Independent verification:** For sql-sec-01 Exercise 3, evaluate each of `row_count` in a separate control `SELECT` over `ds60_sec_owner`; require one final row and compare every value. Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.
- **Intermediate relation check:** For sql-sec-01 Exercise 3, select `ds60_sec_auditor` from `ds60_sec_owner` before adding derived columns.
- **Clause check:** For sql-sec-01 Exercise 3, the solution actually uses `SELECT`. Read only those operations: begin at `ds60_sec_owner`, preserve exactly one summary row, and finish with `ds60_sec_auditor`.
- **Alternative/trade-off:** For sql-sec-01 Exercise 3, the chosen form is justified by this lesson-specific rationale: `audit_notes` is created by `ds60_sec_owner` after: The assertion confirms auditor `SELECT` arrived automatically. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.

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

- **Inputs/evidence:** For sql-sec-01 Exercise 4, complete the definer boundary written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-sec-01 Exercise 4, expected output: a completed the definer boundary written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `document_count_for_tenant`, `search_path`, and `current_user`.
- **Independent verification:** For sql-sec-01 Exercise 4, check the definer boundary written analysis against `document_count_for_tenant`, `search_path`, and `current_user`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-sec-01 Exercise 4, check the definer boundary written analysis against `document_count_for_tenant`, `search_path`, and `current_user`.
- **Clause check:** For sql-sec-01 Exercise 4, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_catalog.pg_roles`, `PUBLIC`, and `TO` or label it as proposed policy.
- **Alternative/trade-off:** For sql-sec-01 Exercise 4, the chosen form is justified by this lesson-specific rationale: The solution's `document_count_for_tenant(text)` demonstrates minimum controls: - a NOLOGIN owner with narrowly managed membership; - `SET search_path = pg_catalog`; - a fully qualified relation; - a bounded ag. Evaluate another form against the concrete expected result (a completed the definer boundary written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

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

- **Inputs/evidence:** For sql-sec-01 Exercise 5, complete the rls bypass written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-sec-01 Exercise 5, expected output: a completed the rls bypass written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `bypassrls`.
- **Independent verification:** For sql-sec-01 Exercise 5, check the rls bypass written analysis against `bypassrls`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-sec-01 Exercise 5, check the rls bypass written analysis against `bypassrls`.
- **Clause check:** For sql-sec-01 Exercise 5, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_catalog.pg_roles`, `PUBLIC`, and `TO` or label it as proposed policy.
- **Alternative/trade-off:** For sql-sec-01 Exercise 5, the chosen form is justified by this lesson-specific rationale: - An ordinary table owner normally bypasses RLS. Evaluate another form against the concrete expected result (a completed the rls bypass written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

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

- **Inputs/evidence:** For sql-sec-01 Exercise 6, complete the effective access written analysis and support its claims with read-only evidence from `pg_auth_members`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-sec-01 Exercise 6, expected output: a completed the effective access written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `has__privilege`, `aclexplode`, `insert`, and `usage`.
- **Independent verification:** For sql-sec-01 Exercise 6, check the effective access written analysis against `has__privilege`, `aclexplode`, `insert`, and `usage`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-sec-01 Exercise 6, check the effective access written analysis against `has__privilege`, `aclexplode`, `insert`, and `usage`.
- **Clause check:** For sql-sec-01 Exercise 6, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_auth_members` or label it as proposed policy.
- **Alternative/trade-off:** For sql-sec-01 Exercise 6, the chosen form is justified by this lesson-specific rationale: Use `has__privilege` functions for the final yes/no matrix because they account for ownership, membership inheritance, and PUBLIC grants. Evaluate another form against the concrete expected result (a completed the effective access written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

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

- **Inputs/evidence:** For sql-sec-01 Exercise 7, complete the identity context written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-sec-01 Exercise 7, expected output: a completed the identity context written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `session_user`, and `current_user`.
- **Independent verification:** For sql-sec-01 Exercise 7, check the identity context written analysis against `session_user`, and `current_user`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-sec-01 Exercise 7, check the identity context written analysis against `session_user`, and `current_user`.
- **Clause check:** For sql-sec-01 Exercise 7, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_catalog.pg_roles`, `PUBLIC`, and `TO` or label it as proposed policy.
- **Alternative/trade-off:** For sql-sec-01 Exercise 7, the chosen form is justified by this lesson-specific rationale: `SESSION_USER` is the authenticated session identity. Evaluate another form against the concrete expected result (a completed the identity context written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

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

- **Inputs/evidence:** For sql-sec-01 Exercise 8, complete the fail-closed tenancy written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-sec-01 Exercise 8, expected output: a completed the fail-closed tenancy written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Independent verification:** For sql-sec-01 Exercise 8, check the fail-closed tenancy written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-sec-01 Exercise 8, check the fail-closed tenancy written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Clause check:** For sql-sec-01 Exercise 8, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_catalog.pg_roles`, `PUBLIC`, and `TO` or label it as proposed policy.
- **Alternative/trade-off:** For sql-sec-01 Exercise 8, the chosen form is justified by this lesson-specific rationale: The safe policy maps only exact allowed identities/context values and returns NULL/false for everything else. Evaluate another form against the concrete expected result (a completed the fail-closed tenancy written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 9 — A narrow writer

Grant schema `USAGE`, `INSERT` on only permitted columns, and sequence `USAGE`
when an identity sequence requires it. Grant `SELECT` only on columns allowed in
`RETURNING`; otherwise a write can succeed while the return expression is
denied. Add an RLS `WITH CHECK` policy for the writer's tenant.

Prove the intended insert, then assert that forbidden columns, another tenant,
UPDATE, DELETE, and broad RETURNING all fail. PostgreSQL may require column
references used by policies or expressions to be readable through a carefully
designed API; test the actual statement shape.

### Reasoning and verification

- **Inputs/evidence:** For sql-sec-01 Exercise 9, complete the narrow writer written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-sec-01 Exercise 9, expected output: a completed the narrow writer written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `usage`, `insert`, and `returning`.
- **Independent verification:** For sql-sec-01 Exercise 9, check the narrow writer written analysis against `usage`, `insert`, and `returning`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-sec-01 Exercise 9, check the narrow writer written analysis against `usage`, `insert`, and `returning`.
- **Clause check:** For sql-sec-01 Exercise 9, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_catalog.pg_roles`, `PUBLIC`, and `TO` or label it as proposed policy.
- **Alternative/trade-off:** For sql-sec-01 Exercise 9, the chosen form is justified by this lesson-specific rationale: Grant schema `USAGE`, `INSERT` on only permitted columns, and sequence `USAGE` when an identity sequence requires it. Evaluate another form against the concrete expected result (a completed the narrow writer written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

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

- **Inputs/evidence:** For sql-sec-01 Exercise 10, complete the revocation runbook written analysis and support its claims with read-only evidence from `pg_catalog.pg_roles`, `PUBLIC`, and `TO`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-sec-01 Exercise 10, expected output: a completed the revocation runbook written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Independent verification:** For sql-sec-01 Exercise 10, check the revocation runbook written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-sec-01 Exercise 10, check the revocation runbook written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Clause check:** For sql-sec-01 Exercise 10, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pg_catalog.pg_roles`, `PUBLIC`, and `TO` or label it as proposed policy.
- **Alternative/trade-off:** For sql-sec-01 Exercise 10, the chosen form is justified by this lesson-specific rationale: First disable login/rotate the external credential and terminate or drain approved sessions according to incident authority. Evaluate another form against the concrete expected result (a completed the revocation runbook written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

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
