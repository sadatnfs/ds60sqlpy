# SQL-TEST-01 Solutions — Contracts and Migration Checks


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_test_01_contracts_migrations_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_test_01_contracts_migrations_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Assertion, Fixture, Negative control, Contract, Invariant test, Reconciliation. Its worked-model focus is:
asserttrue(name, condition, detail) treats both false and NULL as failure, raises an exception, and emits a PASS notice only after success. With ONERRORSTOP=1, an uncaught failed assertion gives the command a nonzero exit status—CI cannot mistake printed warnings for success.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 1, alter `pro_contract_test_lab.orders` with required `currency_code character(3) DEFAULT 'USD'`, add migration ID 3, and extend the expected column contract inside the rollback-only fixture.
- **Expected result/shape:** For sql-test-01 Exercise 1, expected output: the version and currency assertions pass, followed by one evidence row with migration IDs `{1,2,3}`, type `character`, length 3, `is_nullable = 'NO'`, and a default containing USD.
- **Independent verification:** For sql-test-01 Exercise 1, independently query the ordered migration IDs and the `information_schema.columns` row; then change the length or omit migration 3 in a negative control and require the assertion to raise.

## Exercise 2 — Duplicate producer keys

The detail query returns one row per duplicate key group and labels its count
`participating_rows`. The summary wraps that query and expects one duplicate
group. Counting all rows with a window would answer a different grain.

Raw staging intentionally permits duplicates so the contract test can observe
them. Curated storage should add the appropriate key only after a duplicate
resolution policy is explicit.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 2, populate `pro_contract_test_lab.raw_orders` with two `ORD-100` producer rows and one `ORD-101` row, then group by `source_order_key` and retain duplicate groups with `HAVING COUNT(*) > 1`.
- **Expected result/shape:** For sql-test-01 Exercise 2, expected output: one row per duplicate producer key with columns `source_order_key` and `participating_rows`, ordered by key; the supplied fixture returns `ORD-100` with 2 participating rows.
- **Independent verification:** For sql-test-01 Exercise 2, independently assert one duplicate group and two participating rows; add another `ORD-100` plus two `ORD-102` rows and prove both groups appear once while `ORD-101` remains absent.

## Exercise 3 — Constraint contracts

The solution searches `pg_constraint` by schema, relation, type, and rendered
definition rather than relying on an auto-generated name. A more rigorous
helper can inspect `conkey` attribute numbers directly. Test semantic properties
while allowing harmless naming differences.

Primary keys, foreign keys, checks, defaults, ownership, privileges, indexes,
and RLS policies may all be part of a migration contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 3, inspect order defaults through `information_schema.columns` and inspect primary, unique, and foreign-key semantics through `pg_constraint`, `pg_class`, and `pg_namespace` without relying on generated names.
- **Expected result/shape:** For sql-test-01 Exercise 3, expected output: four named assertions pass for the required defaults, primary key on `order_id`, unique key on `order_key`, and `customer_id` foreign key; no constraint name is contractual.
- **Independent verification:** For sql-test-01 Exercise 3, render candidates with `pg_get_constraintdef`, require exactly one semantic match per rule, and prove a negative control looking for a nonexistent `UNIQUE (reported_total)` contract raises.

## Exercise 4 — Zero-line reconciliation

A LEFT JOIN retains orders with no line aggregate. `COALESCE(line_total, 0)`
implements the stated rule that no lines sum to numeric zero. Without that
business rule, missing may need to remain NULL and fail separately. `IS
DISTINCT FROM` compares NULL safely.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 4, pre-aggregate `pro_contract_test_lab.order_lines` by `order_id`, LEFT JOIN those totals to every order, and apply the stated policy that no lines means numeric zero.
- **Expected result/shape:** For sql-test-01 Exercise 4, expected output: one row per order with `order_id`, `order_key`, `reported_total`, `line_total`, and `reconciles`, ordered by `order_id`; zero-line orders remain and show zero.
- **Independent verification:** For sql-test-01 Exercise 4, reconcile output count and unique IDs with the orders table, prove `ORD-200` totals 5 and `ORD-201` totals 0, then corrupt a reported total under a savepoint and require the assertion to fail.

## Exercise 5 — Harness reasoning

Fixtures belong to this test module, carry deterministic keys/content tags, and
live in a rollback-isolated schema. A negative control proves failure detection.
CI requires raised errors plus `ON_ERROR_STOP=1`; human-readable failure rows
alone can still exit zero.

Tests must never reset production/shared schemas. Use a disposable database,
per-run schema/database, or transaction whose code does not require commits.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 5, derive a harness checklist from the fixture manifest, outer transaction, caught negative control, raised assertions, final rollback, and psql `ON_ERROR_STOP=1` behavior.
- **Expected result/shape:** For sql-test-01 Exercise 5, expected output: exactly four ordered rows with `step_number`, `control_name`, `required_evidence`, and `failure_if_missing`, covering fixture ownership, rollback isolation, negative control, and process failure.
- **Independent verification:** For sql-test-01 Exercise 5, run one intentionally false assertion in a disposable invocation and require a nonzero psql exit, then rerun the valid suite and confirm rollback leaves no `pro_contract_test_lab` schema.

## Exercise 6 — Assert the intended error

Wrap the duplicate insert in a nested block, require `unique_violation`
(SQLSTATE `23505`), and raise if the insert succeeds. Optionally inspect
`CONSTRAINT_NAME` with `GET STACKED DIAGNOSTICS` when the exact stable constraint
is contractual; do not accept every integrity error as proof of this rule.

Full server messages vary with version, locale, detail, and object names.
Matching them makes tests brittle, while `WHEN OTHERS` can falsely pass on
permissions, missing objects, or syntax defects.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 6, record the order count, attempt a duplicate `order_key` inside a nested exception block, capture returned SQLSTATE and constraint name, and record the post-attempt count.
- **Expected result/shape:** For sql-test-01 Exercise 6, expected output: one `negative_test_results` row showing SQLSTATE `23505`, a nonblank constraint name, unchanged before/after counts, and `passed = true`, followed by a passing assertion.
- **Independent verification:** For sql-test-01 Exercise 6, fail if the insert succeeds or raises any category other than `unique_violation`, compare the before/after counts independently, and verify the duplicate row is absent.

## Exercise 7 — Table-driven boundaries

Represent cases as rows with case ID, input fields, and expected accept/reject
or normalized result. Cover just below, exact, and just above numeric/date
bounds; NULL versus empty; Unicode normalization/case/length; malformed values;
and arithmetic overflow/rounding.

Execute each case in an isolated subtransaction when rejection is expected and
record observed SQLSTATE. Finally assert every case ran exactly once and matched
its expected outcome so an accidentally filtered case cannot disappear.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 7, drive six quantity cases—below, lower bound, upper bound, above, NULL, and malformed—from data, executing each insert in its own exception subtransaction and recording observed SQLSTATE.
- **Expected result/shape:** For sql-test-01 Exercise 7, expected output: six rows with `case_id`, raw value, expected/observed acceptance, observed SQLSTATE, and `matches`; bounds 1 and 100 pass, and all four invalid cases fail with their intended category.
- **Independent verification:** For sql-test-01 Exercise 7, require exactly six unique case IDs and no false `matches`, independently inspect accepted rows, and prove an omitted or misclassified case makes the final assertion raise.

## Exercise 8 — Deterministic concurrency test

Use two independent sessions because one PostgreSQL transaction cannot observe
every competing-transaction anomaly. Establish fixture state, set short
`lock_timeout`/`statement_timeout`, coordinate named barriers, perform the
interleaving, commit/rollback explicitly, and assert final rows plus errors.

Avoid arbitrary sleeps as the only synchronization—they create flaky tests.
Use locks/advisory barriers or a harness that waits for observable session state,
capture both session logs, and always clean a disposable target after failure.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 8, specify a two-session lock test with named setup, session barriers, bounded lock and statement timeouts, captured outcomes, deterministic final reconciliation, and cleanup.
- **Expected result/shape:** For sql-test-01 Exercise 8, expected output: seven ordered protocol rows with `step_number`, `session_name`, `action`, `wait_for`, `expected_observation`, and `failure_evidence`, from setup through cleanup.
- **Independent verification:** For sql-test-01 Exercise 8, execute the protocol only in two disposable sessions, capture both transcripts and the final row, require one committed owner plus the expected losing outcome, and restore the fixture even after failure.

## Exercise 9 — Stable schema fingerprint

Canonicalize ordered semantic rows for columns/types/defaults/nullability,
constraints and referenced columns, indexes/predicates/operator classes,
privileges/policies, and routine signatures/attributes. Compare expected and
observed rows directly before hashing so drift remains diagnosable.

Exclude OIDs, relation file identifiers, statistics, timestamps, and
auto-generated names unless explicitly contractual. Test both missing and
unexpected objects; a one-way expected-subset check misses accidental exposure.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 9, inventory ordered order-column properties from `information_schema.columns` and semantic constraint definitions from PostgreSQL catalogs, excluding OIDs, statistics, timestamps, and generated names.
- **Expected result/shape:** For sql-test-01 Exercise 9, expected output: one deterministic result set at one-row-per-column grain and another at one-row-per-constraint grain, with definitions ordered by constraint type and definition.
- **Independent verification:** For sql-test-01 Exercise 9, compare visible semantic rows before any hash, inject one missing and one unexpected property, and prove both drift directions are diagnosable without depending on an OID or generated name.

## Exercise 10 — Destructive migration rehearsal

Restore a representative, access-isolated backup to a disposable database,
record tool/server versions and baseline contracts, run the exact migration,
then reconcile counts/checksums/rejected keys and execute critical read/write
queries with compatible application versions.

Measure locks, WAL, lag proxy, storage, and elapsed time. Determine whether
rollback preserves new writes or whether recovery requires restore/forward fix.
Archive results, approvals, cleanup, gaps, and owners; never infer production
permission from a successful course fixture.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 10, describe a destructive-migration rehearsal in an isolated restored database, covering artifact identity, baseline contracts, migration evidence, reconciliation, application checks, recovery decision, approval, and cleanup.
- **Expected result/shape:** For sql-test-01 Exercise 10, expected output: eight ordered rows with `phase_number`, `phase_name`, and `required_evidence`, beginning with restore and ending with cleanup; the SQL lesson records the plan but does not perform an external restore.
- **Independent verification:** For sql-test-01 Exercise 10, rehearse against a disposable representative restore, inject one missing or invalid artifact, require validation to stop before cutover, and archive measured duration, rollback limits, approval, and cleanup evidence.

## Edge cases

- DDL that commits externally cannot be isolated by one rollback.
- Concurrent migration runners need serialization.
- Information-schema types can differ from domain/underlying type expectations.
- Reconciliation tolerances need explicit units and rounding rules.
