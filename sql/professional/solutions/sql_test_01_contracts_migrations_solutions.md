# SQL-TEST-01 Solutions — Contracts and Migration Checks

Run:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_test_01_contracts_migrations_solutions.sql
```

The solution rolls back its schema and uses only PostgreSQL catalogs.

## Exercise 1 — Migration and currency contract

The exact manifest is `ARRAY[1,2,3]`. The column contract checks information
schema type `character`, length 3, `NOT NULL`, and a USD default. A production
contract should additionally define ISO vocabulary, conversion policy, and
whether totals may combine currencies.

## Exercise 2 — Duplicate producer keys

The detail query returns one row per duplicate key group and labels its count
`participating_rows`. The summary wraps that query and expects one duplicate
group. Counting all rows with a window would answer a different grain.

Raw staging intentionally permits duplicates so the contract test can observe
them. Curated storage should add the appropriate key only after a duplicate
resolution policy is explicit.

## Exercise 3 — Constraint contracts

The solution searches `pg_constraint` by schema, relation, type, and rendered
definition rather than relying on an auto-generated name. A more rigorous
helper can inspect `conkey` attribute numbers directly. Test semantic properties
while allowing harmless naming differences.

Primary keys, foreign keys, checks, defaults, ownership, privileges, indexes,
and RLS policies may all be part of a migration contract.

## Exercise 4 — Zero-line reconciliation

A LEFT JOIN retains orders with no line aggregate. `COALESCE(line_total, 0)`
implements the stated rule that no lines sum to numeric zero. Without that
business rule, missing may need to remain NULL and fail separately. `IS
DISTINCT FROM` compares NULL safely.

## Exercise 5 — Harness reasoning

Fixtures belong to this test module, carry deterministic keys/content tags, and
live in a rollback-isolated schema. A negative control proves failure detection.
CI requires raised errors plus `ON_ERROR_STOP=1`; human-readable failure rows
alone can still exit zero.

Tests must never reset production/shared schemas. Use a disposable database,
per-run schema/database, or transaction whose code does not require commits.

## Edge cases

- DDL that commits externally cannot be isolated by one rollback.
- Concurrent migration runners need serialization.
- Information-schema types can differ from domain/underlying type expectations.
- Reconciliation tolerances need explicit units and rounding rules.

