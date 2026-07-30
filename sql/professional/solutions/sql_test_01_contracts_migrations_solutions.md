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

## Exercise 6 — Assert the intended error

Wrap the duplicate insert in a nested block, require `unique_violation`
(SQLSTATE `23505`), and raise if the insert succeeds. Optionally inspect
`CONSTRAINT_NAME` with `GET STACKED DIAGNOSTICS` when the exact stable constraint
is contractual; do not accept every integrity error as proof of this rule.

Full server messages vary with version, locale, detail, and object names.
Matching them makes tests brittle, while `WHEN OTHERS` can falsely pass on
permissions, missing objects, or syntax defects.

## Exercise 7 — Table-driven boundaries

Represent cases as rows with case ID, input fields, and expected accept/reject
or normalized result. Cover just below, exact, and just above numeric/date
bounds; NULL versus empty; Unicode normalization/case/length; malformed values;
and arithmetic overflow/rounding.

Execute each case in an isolated subtransaction when rejection is expected and
record observed SQLSTATE. Finally assert every case ran exactly once and matched
its expected outcome so an accidentally filtered case cannot disappear.

## Exercise 8 — Deterministic concurrency test

Use two independent sessions because one PostgreSQL transaction cannot observe
every competing-transaction anomaly. Establish fixture state, set short
`lock_timeout`/`statement_timeout`, coordinate named barriers, perform the
interleaving, commit/rollback explicitly, and assert final rows plus errors.

Avoid arbitrary sleeps as the only synchronization—they create flaky tests.
Use locks/advisory barriers or a harness that waits for observable session state,
capture both session logs, and always clean a disposable target after failure.

## Exercise 9 — Stable schema fingerprint

Canonicalize ordered semantic rows for columns/types/defaults/nullability,
constraints and referenced columns, indexes/predicates/operator classes,
privileges/policies, and routine signatures/attributes. Compare expected and
observed rows directly before hashing so drift remains diagnosable.

Exclude OIDs, relation file identifiers, statistics, timestamps, and
auto-generated names unless explicitly contractual. Test both missing and
unexpected objects; a one-way expected-subset check misses accidental exposure.

## Exercise 10 — Destructive migration rehearsal

Restore a representative, access-isolated backup to a disposable database,
record tool/server versions and baseline contracts, run the exact migration,
then reconcile counts/checksums/rejected keys and execute critical read/write
queries with compatible application versions.

Measure locks, WAL, lag proxy, storage, and elapsed time. Determine whether
rollback preserves new writes or whether recovery requires restore/forward fix.
Archive results, approvals, cleanup, gaps, and owners; never infer production
permission from a successful course fixture.

## Edge cases

- DDL that commits externally cannot be isolated by one rollback.
- Concurrent migration runners need serialization.
- Information-schema types can differ from domain/underlying type expectations.
- Reconciliation tolerances need explicit units and rounding rules.
