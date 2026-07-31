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

## How to run this lesson

The rendered lesson page is for reading. PostgreSQL runs the real learner SQL.
For a first attempt, use the private course portal so the database check,
ignored working copy, and complete `psql` transcript remain together.

1. Open a terminal in the repository root. On Windows, double-click
   `START_DS60.cmd` or run:

   ```powershell
   .\START_DS60.cmd
   ```

   On macOS or Linux, run:

   ```bash
   .venv/bin/python scripts/learning_portal.py
   ```

2. Open **SQL-TEST-01 — SQL Tests, Migration Checks, and Data Contracts** and choose
   **Create/open guided SQL notebook**. Run its readiness cells from top to
   bottom. The runner accepts only the local disposable
   `advanced_sql_training` database.
3. Read the preparation warning. When you are ready to replace only the
   course-owned training state, set `CONFIRM_COURSE_RESET = True` and run the
   cell. It loads deterministic seed rows, verifies them, and prepares any
   cataloged stateful predecessor.
4. Open and edit the ignored learner copy at
   `.learning/sql/sql-test-01/sql_test_01_contracts_migrations.sql`. Save it, then run the notebook's
   full-script cell. It uses `psql -X -v ON_ERROR_STOP=1 -f`, preserving
   transaction and `psql` meta-command behavior.
5. Read output directly below the run cell. A `SELECT` prints column headings,
   table-shaped rows, and a row count; DDL/DML prints a command tag; `NOTICE`
   lines explain intentional checks. Success means no unexpected `ERROR`, exit
   code 0, the final cleanup/transaction boundary completes as documented, and the following verification cell passes.

Manual `psql` fallback:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\lessons\sql_test_01_contracts_migrations.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/lessons/sql_test_01_contracts_migrations.sql
```

The terminal is then the output surface. If PowerShell says `psql` is not
recognized, restart with `START_DS60.cmd`; it can discover PostgreSQL for that
process. If the database or a relation is missing, return to the notebook
preparation cell and explicitly prepare the disposable database. For
authentication failures, rerun setup/doctor—never put a password in SQL, a
notebook, or Git. With `ON_ERROR_STOP`, fix the **first** error and rerun the
whole file instead of trusting partial output.

## A beginner's mental model for this lesson

A **table** stores facts in named columns. A **row** is one occurrence at the
table's declared grain. A query creates a temporary **result set**: rows printed
on screen are not automatically stored. This lesson introduces or reinforces
Assertion, Fixture, Negative control, Contract, Invariant test, Reconciliation. Its worked SQL reads or creates `pro_contract_test_lab.schema_migrations`, `pro_contract_test_lab.customers`, `pro_contract_test_lab.orders`, `pro_contract_test_lab.order_lines`, `pro_contract_test_lab.fixture_manifest`.

Before writing a query, complete this sentence: “One output row represents
___.” Joins can multiply rows, filters can remove them, grouping can collapse
many rows into one, and window functions can add calculations while preserving
row count. For a normal analytical `SELECT`, use this logical reading order:
`FROM`/`JOIN` (including `ON`) → `WHERE` → `GROUP BY`/aggregates → `HAVING` →
window calculations → `SELECT` → `ORDER BY` → `LIMIT`. PostgreSQL may execute a
different physical plan while preserving those semantics.

The lesson-specific reasoning path is: asserttrue(name, condition, detail) treats both false and NULL as failure, raises an exception, and emits a PASS notice only after success. With ONERRORSTOP=1, an uncaught failed assertion gives the command a nonzero exit status—CI cannot mistake printed warnings for success.
The expected contract is that the result must preserve the row grain described in the walkthrough and expose every named key or measure. Predict keys, row count, `NULL` behavior,
and ordering before running. Afterwards, compare keys/counts/totals with an
independent control. A blank string, SQL `NULL`, numeric zero, and a missing row
are different facts; use `COALESCE` only after choosing which meaning the
business question requires.

## Two worked SQL examples

These are answer-free worked excerpts from `sql/professional/lessons/sql_test_01_contracts_migrations.sql`. Run the complete file through the guided notebook or `psql` because setup and transaction context can matter.

### Example 1

```sql
CREATE TABLE pro_contract_test_lab.schema_migrations (
    migration_id integer PRIMARY KEY,
    migration_name text NOT NULL UNIQUE
);
```

**How to read it:** Example 1 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

### Example 2

```sql
CREATE TABLE pro_contract_test_lab.customers (
    customer_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_key text NOT NULL UNIQUE,
    display_name text NOT NULL CHECK (btrim(display_name) <> '')
);
```

**How to read it:** Example 2 is data definition language (DDL). `psql` prints a command tag when PostgreSQL accepts the definition; a later catalog or behavior check must prove that the intended rule exists.

**Expected result/shape:** The output or command tag must match the statement's
declared columns/object and the lesson's stated grain; unexpected duplicates,
missing keys, or an unreported `NULL` require investigation.

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
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
2. **Producer duplicates:** report duplicate groups and participating detail
   rows without confusing their grains.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
3. **Key contracts:** inspect defaults, primary/unique keys, and foreign keys
   by properties rather than generated names.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
4. **Zero-line reconciliation:** preserve every order and distinguish absent
   detail from a numeric zero.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
5. **Harness:** document fixture ownership, isolation, negative control, CI exit,
   and cleanup.
   **Expected result/shape:** Evidence of the incorrect behavior followed by a corrected result at the declared grain, with the violated invariant made visible.
   **Verify:** Keep a minimal failing case, rerun the corrected form, and compare keys/counts/totals so the repair is proved rather than asserted.
6. **Expected SQLSTATE:** reject a duplicate for the intended category and fail
   if no error or the wrong error occurs.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
7. **Boundary matrix:** drive below/exact/above/malformed/NULL cases from data
   with an expected outcome for each.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
8. **Concurrency:** specify sessions, barriers, timeouts, observed states,
   deterministic assertions, and cleanup.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
9. **Schema fingerprint:** compare stable semantic properties while excluding
   OIDs and unstable generated names.
   **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
   **Verify:** Inspect the applicable `pg_catalog`/`information_schema` entry and run one valid plus one boundary case inside the lesson's safety boundary.
10. **Destructive rehearsal:** restore, migrate, reconcile, test critical
    queries, measure, assess rollback, and preserve approval evidence.
   **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
   **Verify:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.

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

## Ask Codex about this lesson

Codex is optional; the guide, learner SQL, PostgreSQL, and expected checks are
enough to complete the lesson offline. If you want a patient tutor, copy this
prompt after opening the repository in Codex:

```text
Tutor me through sql-test-01 — SQL Tests, Migration Checks, and Data Contracts.

I am a complete beginner. Use these checked-in sources:
- Guide: sql/professional/companion-guides/sql_test_01_contracts_migrations.md
- Answer-free learner SQL: sql/professional/lessons/sql_test_01_contracts_migrations.sql

The lesson concepts include Assertion, Fixture, Negative control, Contract, Invariant test, Reconciliation. First define those terms in plain
language and explain table, row, column, result set, row grain, SQL NULL, and
deterministic ordering where they apply. Then explain the important clauses in
logical order and state the expected row grain/shape before asking me to run
anything. The guide's lesson-specific worked-model focus is: asserttrue(name, condition, detail) treats both false and NULL as failure, raises an exception, and emits a PASS notice only after success. With ONERRORSTOP=1, an uncaught failed assertion gives the command a nonzero exit status—CI cannot mistake printed warnings for success.

Use only the local disposable advanced_sql_training database. Prefer the
lesson reader's Create/open guided SQL notebook action and its ignored
.learning/sql/sql-test-01/ working copy. Never point setup, reset, DDL, or DML
at a shared or valuable database, and never ask me to paste a password.

Follow guide -> prediction -> my attempt -> one progressive hint at a time ->
solution comparison. Do not open, quote, or summarize an official solution
unless I explicitly ask after attempting the exercise. Ask for my actual SQL
and the complete psql transcript/query result; inspect that evidence rather
than assuming a completion declaration proves mastery. Explain the first error
before changing later code. Finish with 2-3 retrieval questions and one small
transfer task that I answer without looking back.
```
