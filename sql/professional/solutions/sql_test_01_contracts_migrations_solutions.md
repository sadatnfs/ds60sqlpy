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

- **Inputs/evidence:** For sql-test-01 Exercise 1, complete the currency migration written analysis and support its claims with read-only evidence from `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-test-01 Exercise 1, expected output: a completed the currency migration written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `character`.
- **Independent verification:** For sql-test-01 Exercise 1, check the currency migration written analysis against `character`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-test-01 Exercise 1, check the currency migration written analysis against `character`.
- **Clause check:** For sql-test-01 Exercise 1, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders` or label it as proposed policy.
- **Alternative/trade-off:** For sql-test-01 Exercise 1, the chosen form is justified by this lesson-specific rationale: The exact manifest is `ARRAY[1,2,3]`. Evaluate another form against the concrete expected result (a completed the currency migration written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 2 — Duplicate producer keys

The detail query returns one row per duplicate key group and labels its count
`participating_rows`. The summary wraps that query and expects one duplicate
group. Counting all rows with a window would answer a different grain.

Raw staging intentionally permits duplicates so the contract test can observe
them. Curated storage should add the appropriate key only after a duplicate
resolution policy is explicit.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 2, read from `pro_contract_test_lab.raw_orders`. Compute `source_order_key`, and `participating_rows` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-test-01 Exercise 2, expected output: one row per duplicate key group and labels its count `participating_rows`. The final columns are `source_order_key`, and `participating_rows`. The final order is `ro.source_order_key`.
- **Independent verification:** For sql-test-01 Exercise 2, evaluate each of `source_order_key`, and `participating_rows` in a separate control `SELECT` over `pro_contract_test_lab.raw_orders`; require one final row and compare every value. Add duplicate source candidates for `source_order_key`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.
- **Intermediate relation check:** For sql-test-01 Exercise 2, confirm the groups are `source_order_key`; then check `ro.source_order_key` before applying the row cap.
- **Clause check:** For sql-test-01 Exercise 2, the solution actually uses `FROM`, `GROUP BY`, `HAVING`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_contract_test_lab.raw_orders`, preserve one row per `source_order_key`, and finish with `source_order_key`, and `participating_rows` ordered by `ro.source_order_key`.
- **Alternative/trade-off:** For sql-test-01 Exercise 2, the chosen form is justified by this lesson-specific rationale: The detail query returns one row per duplicate key group and labels its count `participating_rows`. Evaluate another form against the concrete expected result (one row per duplicate key group and labels its count `participating_rows`) and the verification above.
- **Edge case:** Add duplicate source candidates for `source_order_key`; verify the final SELECT returns each required key tuple exactly once and does not discard distinct tuples that share only part of the key.

## Exercise 3 — Constraint contracts

The solution searches `pg_constraint` by schema, relation, type, and rendered
definition rather than relying on an auto-generated name. A more rigorous
helper can inspect `conkey` attribute numbers directly. Test semantic properties
while allowing harmless naming differences.

Primary keys, foreign keys, checks, defaults, ownership, privileges, indexes,
and RLS policies may all be part of a migration contract.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 3, read from `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, and `pg_constraint`. Compute `conkey` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-test-01 Exercise 3, expected output: exactly one aggregate summary row. The final columns are `conkey`.
- **Independent verification:** For sql-test-01 Exercise 3, evaluate each of `row_count` in a separate control `SELECT` over `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, and `pg_constraint`; require one final row and compare every value. Add two tied candidates and prove `conkey` identifies both without accidental loss.
- **Intermediate relation check:** For sql-test-01 Exercise 3, start with the first relation in `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, and `pg_constraint`; after each join, record total rows and distinct `conkey` so the exact fanout or loss is visible.
- **Clause check:** For sql-test-01 Exercise 3, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, and `SELECT`. Read only those operations: begin at `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, and `pg_constraint`, preserve exactly one summary row, and finish with `conkey`.
- **Alternative/trade-off:** For sql-test-01 Exercise 3, the chosen form is justified by this lesson-specific rationale: The solution searches `pg_constraint` by schema, relation, type, and rendered definition rather than relying on an auto-generated name. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add two tied candidates and prove `conkey` identifies both without accidental loss.

## Exercise 4 — Zero-line reconciliation

A LEFT JOIN retains orders with no line aggregate. `COALESCE(line_total, 0)`
implements the stated rule that no lines sum to numeric zero. Without that
business rule, missing may need to remain NULL and fail separately. `IS
DISTINCT FROM` compares NULL safely.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 4, read from `pro_contract_test_lab.orders`, `pro_contract_test_lab.order_lines`, and `line`. Build the answer toward `order_id`; keep `order_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-test-01 Exercise 4, expected output: one row per `order_id`. The final columns are `order_id`.
- **Independent verification:** For sql-test-01 Exercise 4, project `order_id` plus the raw source columns from `pro_contract_test_lab.orders`, `pro_contract_test_lab.order_lines`, and `line` at each join stage; record row count and distinct `order_id`, then assert the final `order_id` values match those staged rows without unintended fanout or loss. Add one row for which `(o.order_key = 'ORD-200')` is true and one for which it is false; verify only the matching `order_id` value is returned.
- **Intermediate relation check:** For sql-test-01 Exercise 4, start with the first relation in `pro_contract_test_lab.orders`, `pro_contract_test_lab.order_lines`, and `line`; after each join, record total rows and distinct `order_id` so the exact fanout or loss is visible.
- **Clause check:** For sql-test-01 Exercise 4, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `GROUP BY`, and `SELECT`. Read only those operations: begin at `pro_contract_test_lab.orders`, `pro_contract_test_lab.order_lines`, and `line`, preserve one row per `order_id`, and finish with `order_id`.
- **Alternative/trade-off:** For sql-test-01 Exercise 4, the chosen form is justified by this lesson-specific rationale: A LEFT JOIN retains orders with no line aggregate. Evaluate another form against the concrete expected result (one row per `order_id`) and the verification above.
- **Edge case:** Add one row for which `(o.order_key = 'ORD-200')` is true and one for which it is false; verify only the matching `order_id` value is returned.

## Exercise 5 — Harness reasoning

Fixtures belong to this test module, carry deterministic keys/content tags, and
live in a rollback-isolated schema. A negative control proves failure detection.
CI requires raised errors plus `ON_ERROR_STOP=1`; human-readable failure rows
alone can still exit zero.

Tests must never reset production/shared schemas. Use a disposable database,
per-run schema/database, or transaction whose code does not require commits.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 5, complete the harness written analysis and support its claims with read-only evidence from `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-test-01 Exercise 5, expected output: a completed the harness written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `on_error_stop`.
- **Independent verification:** For sql-test-01 Exercise 5, check the harness written analysis against `on_error_stop`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-test-01 Exercise 5, check the harness written analysis against `on_error_stop`.
- **Clause check:** For sql-test-01 Exercise 5, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders` or label it as proposed policy.
- **Alternative/trade-off:** For sql-test-01 Exercise 5, the chosen form is justified by this lesson-specific rationale: Fixtures belong to this test module, carry deterministic keys/content tags, and live in a rollback-isolated schema. Evaluate another form against the concrete expected result (a completed the harness written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 6 — Assert the intended error

Wrap the duplicate insert in a nested block, require `unique_violation`
(SQLSTATE `23505`), and raise if the insert succeeds. Optionally inspect
`CONSTRAINT_NAME` with `GET STACKED DIAGNOSTICS` when the exact stable constraint
is contractual; do not accept every integrity error as proof of this rule.

Full server messages vary with version, locale, detail, and object names.
Matching them makes tests brittle, while `WHEN OTHERS` can falsely pass on
permissions, missing objects, or syntax defects.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 6, read the target keys from `pro_contract_test_lab.orders` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-test-01 Exercise 6, expected output: the command tag and an independently counted set of affected `order_id` values. The final columns are `unique_violation`, and `constraint_name`.
- **Independent verification:** For sql-test-01 Exercise 6, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_contract_test_lab.orders` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.
- **Intermediate relation check:** For sql-test-01 Exercise 6, materialize the intended `order_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_contract_test_lab.orders` again and prove rollback or idempotent retry.
- **Clause check:** For sql-test-01 Exercise 6, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_contract_test_lab.orders` or label it as proposed policy.
- **Alternative/trade-off:** For sql-test-01 Exercise 6, the chosen form is justified by this lesson-specific rationale: Wrap the duplicate insert in a nested block, require `unique_violation` (SQLSTATE `23505`), and raise if the insert succeeds. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `order_id` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `order_id` values in both cases.

## Exercise 7 — Table-driven boundaries

Represent cases as rows with case ID, input fields, and expected accept/reject
or normalized result. Cover just below, exact, and just above numeric/date
bounds; NULL versus empty; Unicode normalization/case/length; malformed values;
and arithmetic overflow/rounding.

Execute each case in an isolated subtransaction when rejection is expected and
record observed SQLSTATE. Finally assert every case ran exactly once and matched
its expected outcome so an accidentally filtered case cannot disappear.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 7, read from `pro_contract_test_lab.boundary_probe`, and `pro_contract_test_lab.boundary_results`. Build the answer toward `case_id`, `quantity`, and `expected_accept`; keep `case_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-test-01 Exercise 7, expected output: one row per `case_id`. The final columns are `case_id`, `quantity`, and `expected_accept`. The final order is `case_id LOOP accepted := true`.
- **Independent verification:** For sql-test-01 Exercise 7, reselect the returned keys directly from the source; require unique `case_id` where the expected grain is one row per key and confirm the projected `case_id`, `quantity`, and `expected_accept` against `pro_contract_test_lab.boundary_probe`, and `pro_contract_test_lab.boundary_results`. Repeat with `NULL` in `case_id`, and `quantity` and state whether the row is kept, rejected, or classified.
- **Intermediate relation check:** For sql-test-01 Exercise 7, inspect the source keys that survive `WHERE`; then check `case_id LOOP accepted := true` before applying the row cap.
- **Clause check:** For sql-test-01 Exercise 7, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_contract_test_lab.boundary_probe`, and `pro_contract_test_lab.boundary_results`, preserve one row per `case_id`, and finish with `case_id`, `quantity`, and `expected_accept` ordered by `case_id LOOP accepted := true`.
- **Alternative/trade-off:** For sql-test-01 Exercise 7, the chosen form is justified by this lesson-specific rationale: Represent cases as rows with case ID, input fields, and expected accept/reject or normalized result. Evaluate another form against the concrete expected result (one row per `case_id`) and the verification above.
- **Edge case:** Repeat with `NULL` in `case_id`, and `quantity` and state whether the row is kept, rejected, or classified.

## Exercise 8 — Deterministic concurrency test

Use two independent sessions because one PostgreSQL transaction cannot observe
every competing-transaction anomaly. Establish fixture state, set short
`lock_timeout`/`statement_timeout`, coordinate named barriers, perform the
interleaving, commit/rollback explicitly, and assert final rows plus errors.

Avoid arbitrary sleeps as the only synchronization—they create flaky tests.
Use locks/advisory barriers or a harness that waits for observable session state,
capture both session logs, and always clean a disposable target after failure.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 8, read from `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders`. Build the answer toward `lock_timeout`, and `statement_timeout`; keep `customer_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-test-01 Exercise 8, expected output: one row per `customer_id`. The final columns are `lock_timeout`, and `statement_timeout`.
- **Independent verification:** For sql-test-01 Exercise 8, reselect the returned keys directly from the source; require unique `customer_id` where the expected grain is one row per key and confirm the projected `lock_timeout`, and `statement_timeout` against `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders`. Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.
- **Intermediate relation check:** For sql-test-01 Exercise 8, select `customer_id` from `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders` before adding derived columns.
- **Clause check:** For sql-test-01 Exercise 8, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders` or label it as proposed policy.
- **Alternative/trade-off:** For sql-test-01 Exercise 8, the chosen form is justified by this lesson-specific rationale: Use two independent sessions because one PostgreSQL transaction cannot observe every competing-transaction anomaly. Evaluate another form against the concrete expected result (one row per `customer_id`) and the verification above.
- **Edge case:** Add one source row with a new `customer_id`; verify the result gains exactly one row carrying that `customer_id` value.

## Exercise 9 — Stable schema fingerprint

Canonicalize ordered semantic rows for columns/types/defaults/nullability,
constraints and referenced columns, indexes/predicates/operator classes,
privileges/policies, and routine signatures/attributes. Compare expected and
observed rows directly before hashing so drift remains diagnosable.

Exclude OIDs, relation file identifiers, statistics, timestamps, and
auto-generated names unless explicitly contractual. Test both missing and
unexpected objects; a one-way expected-subset check misses accidental exposure.

### Reasoning and verification

- **Inputs/evidence:** For sql-test-01 Exercise 9, read from `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`. Build the answer toward `ordinal_position`, `column_name`, `data_type`, `is_nullable`, and `column_default`; keep `ordinal_position` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-test-01 Exercise 9, expected output: one row per `ordinal_position`. The final columns are `ordinal_position`, `column_name`, `data_type`, `is_nullable`, and `column_default`. The final order is `con.contype, definition`.
- **Independent verification:** For sql-test-01 Exercise 9, project `ordinal_position` plus the raw source columns from `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` at each join stage; record row count and distinct `ordinal_position`, then assert the final `ordinal_position`, `column_name`, `data_type`, `is_nullable`, and `column_default` values match those staged rows without unintended fanout or loss. Give two rows the same `con.contype` value and different `definition` values; verify `con.contype, definition` produces the intended rank and display order.
- **Intermediate relation check:** For sql-test-01 Exercise 9, start with the first relation in `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `ordinal_position` so the exact fanout or loss is visible.
- **Clause check:** For sql-test-01 Exercise 9, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`, preserve one row per `ordinal_position`, and finish with `ordinal_position`, `column_name`, `data_type`, `is_nullable`, and `column_default` ordered by `con.contype, definition`.
- **Alternative/trade-off:** For sql-test-01 Exercise 9, the chosen form is justified by this lesson-specific rationale: Canonicalize ordered semantic rows for columns/types/defaults/nullability, constraints and referenced columns, indexes/predicates/operator classes, privileges/policies, and routine signatures/attributes. Evaluate another form against the concrete expected result (one row per `ordinal_position`) and the verification above.
- **Edge case:** Give two rows the same `con.contype` value and different `definition` values; verify `con.contype, definition` produces the intended rank and display order.

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

- **Inputs/evidence:** For sql-test-01 Exercise 10, use `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-test-01 Exercise 10, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
- **Independent verification:** For sql-test-01 Exercise 10, restore into an isolated target and reconcile `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-test-01 Exercise 10, restore into an isolated target and reconcile `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-test-01 Exercise 10, the solution actually uses `WITH`. Read only those operations: begin at `true`, `pro_contract_test_lab.customers`, and `pro_contract_test_lab.orders`, preserve one row per `customer_id`, and finish with `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
- **Alternative/trade-off:** For sql-test-01 Exercise 10, the chosen form is justified by this lesson-specific rationale: Restore a representative, access-isolated backup to a disposable database, record tool/server versions and baseline contracts, run the exact migration, then reconcile counts/checksums/rejected keys and execute. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Edge cases

- DDL that commits externally cannot be isolated by one rollback.
- Concurrent migration runners need serialization.
- Information-schema types can differ from domain/underlying type expectations.
- Reconciliation tolerances need explicit units and rounding rules.
