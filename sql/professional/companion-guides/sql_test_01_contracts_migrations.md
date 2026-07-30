# SQL-TEST-01 — SQL Tests, Migration Checks, and Data Contracts

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-found-02` and `sql-42`
- **Prerequisites:** [SQL-FOUND-02 — migrations](sql_found_02_versioned_migrations.md),
  [SQL Day 42 data-quality checks](../../postgres-60day/companion-guides/day42_data_quality_validation.md),
  constraints, catalogs, and transactions.
- **Artifacts:** [learner SQL](../lessons/sql_test_01_contracts_migrations.sql) ·
  [solution reasoning](../solutions/sql_test_01_contracts_migrations_solutions.md) ·
  [executable solution](../solutions/sql_test_01_contracts_migrations_solutions.sql)

Run on any supported operating system:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_test_01_contracts_migrations.sql
```

The harness needs no third-party framework and rolls back its test schema.

## Learning objectives

- Build fail-fast SQL assertions, deterministic owned fixtures, and schema
  contract comparisons.
- Verify exact migration manifests with invariant, reconciliation, and negative
  controls.
- Use rollback isolation in a CI database created solely for testing.

## Vocabulary and concepts

- **Assertion:** named condition that raises an error when false or unknown.
- **Fixture:** controlled input data with explicit owner, version, and expected
  grain/count.
- **Negative control:** deliberately invalid case proving a test detects the
  failure it claims to detect.
- **Contract:** expected columns, types, nullability, keys, semantics, and
  compatibility between producer and consumer.
- **Invariant test:** proves a condition such as no orphan keys.
- **Reconciliation:** compares independently derived totals/counts at a stated
  grain.
- **Migration regression:** checks exact ordered versions and post-migration
  schema behavior.
- **Isolation:** preventing tests from depending on or polluting other runs.

## Worked example / walkthrough

`assert_true(name, condition, detail)` treats both false and NULL as failure,
raises an exception, and emits a PASS notice only after success. With
`ON_ERROR_STOP=1`, an uncaught failed assertion gives the command a nonzero exit
status—CI cannot mistake printed warnings for success.

The fixture manifest names its owner (`sql-test-01`), content tag, and expected
row count. This distinguishes course-owned deterministic rows from arbitrary
business data. A test may reset its own schema; it must not delete shared data
to obtain repeatability.

The expected orders contract compares ordinal position, name, information-schema
type, and nullability through a full join. A missing, extra, reordered, retyped,
or nullability-changed column becomes a visible mismatch. Production contracts
also need semantic meaning, units, time zone, keys, defaults, and compatibility
policy; catalogs cannot infer those.

Migration testing uses an ordered integer array, not only a count. Versions
`1,2,9` have the same count as `1,2,3` but different history. Applied checksums
belong in a real migration runner.

The invariant anti-join duplicates the foreign-key claim deliberately: it
detects drift in imported/disabled-constraint scenarios and documents intent.
The total reconciliation derives line totals independently from
`reported_total`. Its grain is one order and its money type is fixed-scale
numeric.

The negative control invokes the assertion with false and catches only its
expected named exception. If the assertion stops failing, the control raises an
unexpected error. This tests the test rather than trusting its appearance.

## Exercises

Complete all five prompts: migrate and update the contract, detect producer
duplicates with precise grains, inspect key/default constraints without brittle
generated names, reconcile zero-line orders correctly, and explain ownership
and CI behavior.

For each check, write expected result, observed result, result grain, and failure
action. Detection is not automatic remediation permission.

## Self-check

- Does false or NULL make the process exit nonzero unless intentionally caught?
- Does the negative control prove the assertion path?
- Are fixture owner, content tag, expected count, and deterministic keys clear?
- Does the contract detect missing and extra columns?
- Does the migration check prove exact ordered versions?
- Do reconciliations include missing-side rows where required?
- Can tests run repeatedly without depending on another test?
- Does rollback leave no schema or fixture rows?

## Common pitfalls

- Printing “FAIL” while exiting zero creates false-green automation.
- Comparing only row counts can miss replacements and duplicates.
- Querying generated constraint names makes tests brittle across versions.
- `COUNT(column)` ignores NULL; know whether that is intended.
- Inner joins silently exclude missing-side records from reconciliation.
- Production-like random fixtures make failures difficult to reproduce.
- Resetting a shared schema for test isolation destroys other users' state.
- Schema equality does not prove semantic compatibility or safe rollout order.
- Golden snapshots without reviewed change policy normalize accidental drift.

## Next step

Continue to [SQL-ANALYTICS-01 — reusable analytical query patterns](sql_analytics_01_query_patterns.md)
and apply these assertion/reconciliation habits to every pattern. Pair this
module with migration delivery so contract tests run on both fresh installs and
upgrades.
