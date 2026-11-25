# SQL-TEST-01: SQL Tests, Migration Checks, and Data Contracts

## How to run this lesson

Start **sql-test-01** from `./classroom` using the shared [run steps](../../STUDY-GUIDE.md#run-a-lesson-in-the-classroom).

Choose **Whole SQL lesson (psql)**. The script runs on `advanced_sql_training`
in one transaction. It creates the `assert_true` helper, a two-step migration
ledger, 2 customers, 2 orders, 3 order lines and a fixture manifest, then runs
five assertions. A clean run prints five `PASS [...]` notices
(`orders column contract`, `ordered migration manifest`, `no order orphans`,
`reported totals reconcile`, `fixture manifest counts`) followed by
`Expected assertion failure was observed` from the negative control. Any
`FAIL [...]` error stops the script, because the runner uses `ON_ERROR_STOP=1`.
`ROLLBACK` then removes `pro_contract_test_lab`. Save attempts in
`.learning/sql/sql-test-01/lesson/workspace/sql/professional/lessons/sql_test_01_contracts_migrations.sql`.

The optional notebook route starts with `uv run --no-sync python scripts/course.py sql notebook sql-test-01`; see the [study guide](../../STUDY-GUIDE.md#optional-contributor-notebook-route).

## Level and prerequisites

- **Level:** Advanced
- **Catalog prerequisites:** `sql-found-02` and `sql-42`
- **Prerequisites:** [SQL-FOUND-02; migrations](sql_found_02_versioned_migrations.md),
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

## A beginner's mental model for this lesson

A SQL test is a query whose answer must be true. This lesson turns schema
contracts, invariants and reconciliations into calls to one helper that raises
an error when the answer is false or unknown, so a broken rule stops the run
instead of printing a row someone has to notice. The vocabulary below
(assertion, fixture, negative control, contract, invariant test,
reconciliation) names the parts of that harness.

Here most output is notices rather than rows. Each `assert_true` call evaluates
one boolean over the whole fixture, usually `NOT EXISTS (...)`, so "one
assertion" is the grain. The `orders_contract_mismatches` view is the
exception: it full-joins actual and expected columns by position and returns
one row per position whose name, type or nullability differs from
`expected_orders_contract`, so a correct schema returns zero rows.

`assert_true(name, condition, detail)` tests
`p_condition IS DISTINCT FROM true`, so both `false` and `NULL` fail. That
matters because a comparison against a missing value is `NULL`, and a helper
that only rejected `false` would let it pass silently. Under `ON_ERROR_STOP=1`
an uncaught failure gives `psql` a nonzero exit status, which is what CI needs.
The negative control then calls the helper with `false` on purpose and catches
only the expected `FAIL [negative control]` message, proving the helper can
fail.

## Two worked SQL examples

Examples 1 and 2 are the first two tables of the fixture that the assertions
check.

### Example 1

```sql
CREATE TABLE pro_contract_test_lab.schema_migrations (
  migration_id integer PRIMARY KEY,
  migration_name text NOT NULL UNIQUE
);
```

**How to read it:** `migration_id` orders the steps and `migration_name` is
unique, so the same migration cannot be recorded twice under different numbers.
The `ordered migration manifest` assertion later checks the ledger holds
exactly steps 1 and 2.

**Expected result/shape:** `CREATE TABLE`. Two rows follow:
`create_order_model` and `require_order_status`.

### Example 2

```sql
CREATE TABLE pro_contract_test_lab.customers (
  customer_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_key text NOT NULL UNIQUE,
  display_name text NOT NULL CHECK (btrim(display_name) <> '')
);
```

**How to read it:** The identity key is internal, `customer_key` is the stable
business key, and the `CHECK` rejects a blank or all-space name. Orders are
later loaded by joining on `customer_key`, so the fixture never hard-codes
generated ids.

**Expected result/shape:** `CREATE TABLE`, then two customers, `CUS-100`
(Avery) and `CUS-101` (Morgan). Their orders reconcile exactly: ORD-100 lines
total 1 x 10.00 + 3 x 5.00 = 25.00 and ORD-101 totals 2 x 7.00 = 14.00.

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
status, CI cannot mistake printed warnings for success.

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

Complete all ten prompts. Begin by migrating and updating the contract, detecting producer
duplicates with precise grains, inspect key/default constraints without brittle
generated names, reconcile zero-line orders correctly, and explain ownership
and CI behavior; then test SQLSTATEs, boundaries, concurrency, schema drift, and
a destructive-migration rehearsal.

For each check, write expected result, observed result, result grain, and failure
action. Detection is not automatic remediation permission.

Make every test fail loudly on the wrong result and independently verify the
test harness with a negative control:

1. **Currency migration:** update migration manifest and expected contract for
   the new required defaulted column.
   **Inputs/evidence:** For sql-test-01 Exercise 1, alter `pro_contract_test_lab.orders` with required `currency_code character(3) DEFAULT 'USD'`, add migration ID 3, and extend the expected column contract inside the rollback-only fixture.
   **Expected result/shape:** For sql-test-01 Exercise 1, expected output: the version and currency assertions pass, followed by one evidence row with migration IDs `{1,2,3}`, type `character`, length 3, `is_nullable = 'NO'`, and a default containing USD.
   **Verify:** For sql-test-01 Exercise 1, independently query the ordered migration IDs and the `information_schema.columns` row; then change the length or omit migration 3 in a negative control and require the assertion to raise.
2. **Producer duplicates:** report duplicate groups and participating detail
   rows without confusing their grains.
   **Inputs/evidence:** For sql-test-01 Exercise 2, populate `pro_contract_test_lab.raw_orders` with two `ORD-100` producer rows and one `ORD-101` row, then group by `source_order_key` and retain duplicate groups with `HAVING COUNT(*) > 1`.
   **Expected result/shape:** For sql-test-01 Exercise 2, expected output: one row per duplicate producer key with columns `source_order_key` and `participating_rows`, ordered by key; the supplied fixture returns `ORD-100` with 2 participating rows.
   **Verify:** For sql-test-01 Exercise 2, independently assert one duplicate group and two participating rows; add another `ORD-100` plus two `ORD-102` rows and prove both groups appear once while `ORD-101` remains absent.
3. **Key contracts:** inspect defaults, primary/unique keys, and foreign keys
   by properties rather than generated names.
   **Inputs/evidence:** For sql-test-01 Exercise 3, inspect order defaults through `information_schema.columns` and inspect primary, unique, and foreign-key semantics through `pg_constraint`, `pg_class`, and `pg_namespace` without relying on generated names.
   **Expected result/shape:** For sql-test-01 Exercise 3, expected output: four named assertions pass for the required defaults, primary key on `order_id`, unique key on `order_key`, and `customer_id` foreign key; no constraint name is contractual.
   **Verify:** For sql-test-01 Exercise 3, render candidates with `pg_get_constraintdef`, require exactly one semantic match per rule, and prove a negative control looking for a nonexistent `UNIQUE (reported_total)` contract raises.
4. **Zero-line reconciliation:** preserve every order and distinguish absent
   detail from a numeric zero.
   **Inputs/evidence:** For sql-test-01 Exercise 4, pre-aggregate `pro_contract_test_lab.order_lines` by `order_id`, LEFT JOIN those totals to every order, and apply the stated policy that no lines means numeric zero.
   **Expected result/shape:** For sql-test-01 Exercise 4, expected output: one row per order with `order_id`, `order_key`, `reported_total`, `line_total`, and `reconciles`, ordered by `order_id`; zero-line orders remain and show zero.
   **Verify:** For sql-test-01 Exercise 4, reconcile output count and unique IDs with the orders table, prove `ORD-200` totals 5 and `ORD-201` totals 0, then corrupt a reported total under a savepoint and require the assertion to fail.
5. **Harness:** document fixture ownership, isolation, negative control, CI exit,
   and cleanup.
   **Inputs/evidence:** For sql-test-01 Exercise 5, derive a harness checklist from the fixture manifest, outer transaction, caught negative control, raised assertions, final rollback, and psql `ON_ERROR_STOP=1` behavior.
   **Expected result/shape:** For sql-test-01 Exercise 5, expected output: exactly four ordered rows with `step_number`, `control_name`, `required_evidence`, and `failure_if_missing`, covering fixture ownership, rollback isolation, negative control, and process failure.
   **Verify:** For sql-test-01 Exercise 5, run one intentionally false assertion in a disposable invocation and require a nonzero psql exit, then rerun the valid suite and confirm rollback leaves no `pro_contract_test_lab` schema.
6. **Expected SQLSTATE:** reject a duplicate for the intended category and fail
   if no error or the wrong error occurs.
   **Inputs/evidence:** For sql-test-01 Exercise 6, record the order count, attempt a duplicate `order_key` inside a nested exception block, capture returned SQLSTATE and constraint name, and record the post-attempt count.
   **Expected result/shape:** For sql-test-01 Exercise 6, expected output: one `negative_test_results` row showing SQLSTATE `23505`, a nonblank constraint name, unchanged before/after counts, and `passed = true`, followed by a passing assertion.
   **Verify:** For sql-test-01 Exercise 6, fail if the insert succeeds or raises any category other than `unique_violation`, compare the before/after counts independently, and verify the duplicate row is absent.
7. **Boundary matrix:** drive below/exact/above/malformed/NULL cases from data
   with an expected outcome for each.
   **Inputs/evidence:** For sql-test-01 Exercise 7, drive six quantity cases, below, lower bound, upper bound, above, NULL, and malformed, from data, executing each insert in its own exception subtransaction and recording observed SQLSTATE.
   **Expected result/shape:** For sql-test-01 Exercise 7, expected output: six rows with `case_id`, raw value, expected/observed acceptance, observed SQLSTATE, and `matches`; bounds 1 and 100 pass, and all four invalid cases fail with their intended category.
   **Verify:** For sql-test-01 Exercise 7, require exactly six unique case IDs and no false `matches`, independently inspect accepted rows, and prove an omitted or misclassified case makes the final assertion raise.
8. **Concurrency:** specify sessions, barriers, timeouts, observed states,
   deterministic assertions, and cleanup.
   **Inputs/evidence:** For sql-test-01 Exercise 8, specify a two-session lock test with named setup, session barriers, bounded lock and statement timeouts, captured outcomes, deterministic final reconciliation, and cleanup.
   **Expected result/shape:** For sql-test-01 Exercise 8, expected output: seven ordered protocol rows with `step_number`, `session_name`, `action`, `wait_for`, `expected_observation`, and `failure_evidence`, from setup through cleanup.
   **Verify:** For sql-test-01 Exercise 8, execute the protocol only in two disposable sessions, capture both transcripts and the final row, require one committed owner plus the expected losing outcome, and restore the fixture even after failure.
9. **Schema fingerprint:** compare stable semantic properties while excluding
   OIDs and unstable generated names.
   **Inputs/evidence:** For sql-test-01 Exercise 9, inventory ordered order-column properties from `information_schema.columns` and semantic constraint definitions from PostgreSQL catalogs, excluding OIDs, statistics, timestamps, and generated names.
   **Expected result/shape:** For sql-test-01 Exercise 9, expected output: one deterministic result set at one-row-per-column grain and another at one-row-per-constraint grain, with definitions ordered by constraint type and definition.
   **Verify:** For sql-test-01 Exercise 9, compare visible semantic rows before any hash, inject one missing and one unexpected property, and prove both drift directions are diagnosable without depending on an OID or generated name.
10. **Destructive rehearsal:** restore, migrate, reconcile, test critical
    queries, measure, assess rollback, and preserve approval evidence.
   **Inputs/evidence:** For sql-test-01 Exercise 10, describe a destructive-migration rehearsal in an isolated restored database, covering artifact identity, baseline contracts, migration evidence, reconciliation, application checks, recovery decision, approval, and cleanup.
   **Expected result/shape:** For sql-test-01 Exercise 10, expected output: eight ordered rows with `phase_number`, `phase_name`, and `required_evidence`, beginning with restore and ending with cleanup; the SQL lesson records the plan but does not perform an external restore.
   **Verify:** For sql-test-01 Exercise 10, rehearse against a disposable representative restore, inject one missing or invalid artifact, require validation to stop before cutover, and archive measured duration, rollback limits, approval, and cleanup evidence.

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

Continue to [SQL-ANALYTICS-01; reusable analytical query patterns](sql_analytics_01_query_patterns.md)
and apply these assertion/reconciliation habits to every pattern. Pair this
module with migration delivery so contract tests run on both fresh installs and
upgrades.

## Ask an AI tutor about this lesson

The lesson and expected observations are sufficient offline. For optional
coaching, copy:

```text
Tutor me through sql-test-01: SQL Tests, Migration Checks, and Data Contracts.

I have completed the direct catalog prerequisites: `sql-found-02`, `sql-42`. Assume mastery only through those lessons; define and demonstrate every new concept patiently. Follow the checked-in `guide-ds60sqlpy-learning` tutoring skill and use these sources:
- Guide: sql/professional/companion-guides/sql_test_01_contracts_migrations.md
- Answer-free learner SQL: sql/professional/lessons/sql_test_01_contracts_migrations.sql

Key terms to teach in context: Assertion, Fixture, Negative control, Contract, Invariant test, Reconciliation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: `assert_true(name, condition, detail)` treats both false and NULL as failure, raises an exception, and emits a PASS notice only after success. With `ON_ERROR_STOP=1`, an uncaught failed assertion gives the command a nonzero exit status, CI cannot mistake printed warnings for success.

Use only the local disposable advanced_sql_training database. Prefer the
Docker classroom's Whole SQL lesson (psql) workspace and its ignored
.learning/sql/sql-test-01/ working copy. Never point setup, reset, DDL, or DML
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
