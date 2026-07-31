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

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** An alternative physical/object design is valid only if catalog inspection and valid/invalid behavior prove the same invariant.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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
