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

Complete the five prompts in the learner file. Extend privilege introspection,
add a read-only auditor role and policy, prove the owner-specific default grant,
review the definer routine's boundary, and explain RLS bypass cases. Keep the
new role inside the existing transaction and do not add `LOGIN`, passwords,
`SUPERUSER`, `BYPASSRLS`, database-wide grants, or `PUBLIC` access.

For denied operations, use a small exception-catching test like the worked
examples. A forbidden action that succeeds must fail the lesson rather than
print a reassuring message.

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
