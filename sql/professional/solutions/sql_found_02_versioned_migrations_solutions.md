# SQL-FOUND-02 Solutions — Versioned Migrations


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_found_02_versioned_migrations_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_found_02_versioned_migrations_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Migration, Migration metadata, Immutable migration, Seed, Idempotent, Expand–migrate–contract. Its worked-model focus is:
The fixture owns one schema and five ordered files. Every migration starts a transaction, checks schemamigrations, performs its body only when absent, records metadata last, and commits. A failed statement prevents the metadata row from lying about a partial migration.

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

Run the complete solution from the repository root:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_found_02_versioned_migrations_solutions.sql
```

It resets the isolated fixture, verifies versions 1–5, implements exercise
versions 6–8, checks them, and removes `pro_migration_lab`.

## Exercise 1 — Deterministic manifest

The manifest must order by version explicitly:

```sql
SELECT
    sm.migration_id,
    sm.migration_name,
    sm.content_tag
FROM pro_migration_lab.schema_migrations AS sm
WHERE sm.migration_id BETWEEN 1 AND 5
ORDER BY sm.migration_id;
```

The solution also compares `array_agg(... ORDER BY migration_id)` with
`ARRAY[1,2,3,4,5]`. A row count of five is insufficient because versions
`1,2,3,4,9` also have a count of five.

The fixture's `content_tag` is educational metadata, not a cryptographic file
checksum. A production runner should calculate a checksum from migration bytes,
store it on first application, and fail if the same applied version later has
different bytes.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-02 Exercise 1, read from `pro_migration_lab.schema_migrations`. Build the answer toward `migration_id`, `migration_name`, and `content_tag`; keep `migration_id` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-found-02 Exercise 1, expected output: one row per `migration_id`. The final columns are `migration_id`, `migration_name`, and `content_tag`. The final order is `sm.migration_id`.
- **Independent verification:** For sql-found-02 Exercise 1, run an anti-check that counts rows where NOT ((sm.migration_id BETWEEN 1 AND 5)); require unique `migration_id` where the expected grain is one row per key and confirm the projected `migration_id`, `migration_name`, and `content_tag` against `pro_migration_lab.schema_migrations`. Add one row for which `(sm.migration_id BETWEEN 1 AND 5)` is true and one for which it is false; verify only the matching `migration_id` value is returned.
- **Intermediate relation check:** For sql-found-02 Exercise 1, inspect the source keys that survive `WHERE`; then check `sm.migration_id` before applying the row cap.
- **Clause check:** For sql-found-02 Exercise 1, the solution actually uses `FROM`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_migration_lab.schema_migrations`, preserve one row per `migration_id`, and finish with `migration_id`, `migration_name`, and `content_tag` ordered by `sm.migration_id`.
- **Alternative/trade-off:** For sql-found-02 Exercise 1, the chosen form is justified by this lesson-specific rationale: The manifest must order by version explicitly: The solution also compares `array_agg(. Evaluate another form against the concrete expected result (one row per `migration_id`) and the verification above.
- **Edge case:** Add one row for which `(sm.migration_id BETWEEN 1 AND 5)` is true and one for which it is false; verify only the matching `migration_id` value is returned.

## Exercise 2 — Compatibility and deployment order

At version 2, old storage remains in `urgency_label`, the new
`priority_code` is nullable, and the view returns
`COALESCE(priority_code, urgency_label)`. Existing rows therefore retain a
priority before backfill, while new application code can begin writing the new
column.

A safe high-level order is:

1. Deploy the additive schema and dual-compatible view.
2. Deploy application readers that accept the stable interface and writers that
   populate the new representation while old writers can still operate.
3. Backfill in measured batches and reconcile old versus new values.
4. Stop or upgrade every old writer.
5. Enforce the new constraints and remove the old representation.

Real deployment gates require traffic, lock, error, replica-lag, and data-quality
evidence. The tiny fixture proves logic, not production timing.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-02 Exercise 2, complete the compatibility written analysis and support its claims with read-only evidence from `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-found-02 Exercise 2, expected output: a completed the compatibility written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `urgency_label`, and `priority_code`.
- **Independent verification:** For sql-found-02 Exercise 2, check the compatibility written analysis against `urgency_label`, and `priority_code`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-found-02 Exercise 2, check the compatibility written analysis against `urgency_label`, and `priority_code`.
- **Clause check:** For sql-found-02 Exercise 2, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api` or label it as proposed policy.
- **Alternative/trade-off:** For sql-found-02 Exercise 2, the chosen form is justified by this lesson-specific rationale: At version 2, old storage remains in `urgency_label`, the new `priority_code` is nullable, and the view returns `COALESCE(priority_code, urgency_label)`. Evaluate another form against the concrete expected result (a completed the compatibility written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 3 — Versions 6–8

The solution uses three separate transactions:

- Version 6 adds nullable `assigned_team`.
- Version 7 backfills `high`/`critical` to `response` and everything else to
  `general`, then asserts no NULL remains.
- Version 8 adds the default, `NOT NULL`, and allowed-values `CHECK`.

This separation creates an application compatibility window. A single
transaction containing all three statements would be atomic, but it would not
allow independently deployed application versions or a large online backfill
to coexist.

The exercise uses migrations 6–8 rather than changing a prior file. Metadata is
inserted last in each transaction so a failed body cannot advertise success.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-02 Exercise 3, complete the forward series written analysis and support its claims with read-only evidence from `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-found-02 Exercise 3, expected output: a completed the forward series written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `assigned_team`, `high`, `critical`, `response`, and `general`.
- **Independent verification:** For sql-found-02 Exercise 3, check the forward series written analysis against `assigned_team`, `high`, `critical`, `response`, and `general`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-found-02 Exercise 3, check the forward series written analysis against `assigned_team`, `high`, `critical`, `response`, and `general`.
- **Clause check:** For sql-found-02 Exercise 3, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api` or label it as proposed policy.
- **Alternative/trade-off:** For sql-found-02 Exercise 3, the chosen form is justified by this lesson-specific rationale: The solution uses three separate transactions: - Version 6 adds nullable `assigned_team`. Evaluate another form against the concrete expected result (a completed the forward series written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 4 — Boundaries and recovery

Examples that require an explicit nontransactional boundary include:

- `CREATE DATABASE`
- `VACUUM`
- `CREATE INDEX CONCURRENTLY`

A capable runner marks and executes such a step deliberately; it does not wrap
every file in a transaction and hope PostgreSQL accepts it. Operationally large
backfills may also deserve their own batched, restartable boundary even though
ordinary `UPDATE` is transactional.

A universal down migration is unsafe because deletion, aggregation, and
representation changes can lose information. External clients may also have
observed the new state. Rolling schema syntax backward does not reconstruct
discarded values or undo side effects. If an applied migration is wrong, freeze
it, assess impact, and normally ship a reviewed forward fix. Restore or rollback
is an evidence-based incident decision, not a filename convention.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-02 Exercise 4, change only `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_class` rows.
- **Expected result/shape:** For sql-found-02 Exercise 4, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `vacuum`, and `update`.
- **Independent verification:** For sql-found-02 Exercise 4, inspect `pg_catalog.pg_class` for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
- **Intermediate relation check:** For sql-found-02 Exercise 4, inspect `pg_catalog.pg_class` for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
- **Clause check:** For sql-found-02 Exercise 4, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api` or label it as proposed policy.
- **Alternative/trade-off:** For sql-found-02 Exercise 4, the chosen form is justified by this lesson-specific rationale: Examples that require an explicit nontransactional boundary include: - `CREATE DATABASE` - `VACUUM` - `CREATE INDEX CONCURRENTLY` A capable runner marks and executes such a step deliberately; it does not wrap e. Evaluate another form against the concrete expected result (the requested DDL command tag plus catalog rows and one accepted and one rejected behavior) and the verification above.
- **Edge case:** Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.

## Exercise 5 — Retry after uncertain completion

Serialize the runner, begin a transaction, lock/read the manifest row, and
compare both recorded checksum and observed schema precondition. If neither
version nor column exists, apply DDL, verify its exact properties, then insert
metadata and commit. If both match, report “already applied.” If only one exists
or properties differ, stop for investigation.

`IF NOT EXISTS` is not a drift detector: it accepts any same-named object even
when its type, default, nullability, or ownership is wrong. Idempotency means
repeating the operation reaches the same verified state, not suppressing every
error.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-02 Exercise 5, read from `pro_migration_lab.schema_migrations`, and `information_schema.columns`. Compute `manifest_matches`, and `schema_matches` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-found-02 Exercise 5, expected output: exactly one aggregate summary row. The final columns are `manifest_matches`, and `schema_matches`.
- **Independent verification:** For sql-found-02 Exercise 5, evaluate each of `manifest_matches`, and `schema_matches` in a separate control `SELECT` over `pro_migration_lab.schema_migrations`, and `information_schema.columns`; require one final row and compare every value. Add one source row with a new `version`; verify the result gains exactly one row carrying that `version` value.
- **Intermediate relation check:** For sql-found-02 Exercise 5, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-found-02 Exercise 5, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `pro_migration_lab.schema_migrations`, and `information_schema.columns`, preserve exactly one summary row, and finish with `manifest_matches`, and `schema_matches`.
- **Alternative/trade-off:** For sql-found-02 Exercise 5, the chosen form is justified by this lesson-specific rationale: Serialize the runner, begin a transaction, lock/read the manifest row, and compare both recorded checksum and observed schema precondition. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add one source row with a new `version`; verify the result gains exactly one row carrying that `version` value.

## Exercise 6 — Low-lock index and constraint rollout

`CREATE INDEX CONCURRENTLY` must run outside a transaction block and can leave
an invalid index after interruption. Record progress, validity, locks, lag, and
disk before retrying or explicitly dropping only the known invalid artifact.
Attach it as a constraint in a later reviewed transaction when appropriate.

Add a CHECK as `NOT VALID` in a short transaction, observe that new writes are
still checked, remediate existing violations in batches, then run `VALIDATE
CONSTRAINT` separately. “Lower lock” is not “no impact”; define timeouts,
abort thresholds, and postcondition queries.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-02 Exercise 6, change only `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_constraint` rows.
- **Expected result/shape:** For sql-found-02 Exercise 6, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `object_name`, `catalog_definition`, `accepted_case`, and `rejected_sqlstate`.
- **Independent verification:** For sql-found-02 Exercise 6, inspect `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_constraint` for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
- **Intermediate relation check:** For sql-found-02 Exercise 6, inspect `pg_catalog.pg_index`, `pg_catalog.pg_indexes`, and `pg_catalog.pg_constraint` for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
- **Clause check:** For sql-found-02 Exercise 6, the solution actually uses `WITH`. Read only those operations: begin at `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, and `pro_migration_lab.service_requests_api`, preserve one row per `version`, and finish with `object_name`, `catalog_definition`, `accepted_case`, and `rejected_sqlstate`.
- **Alternative/trade-off:** For sql-found-02 Exercise 6, the chosen form is justified by this lesson-specific rationale: `CREATE INDEX CONCURRENTLY` must run outside a transaction block and can leave an invalid index after interruption. Evaluate another form against the concrete expected result (the requested DDL command tag plus catalog rows and one accepted and one rejected behavior) and the verification above.
- **Edge case:** Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.

## Exercise 7 — Semantic drift report

Build expected rows with stable identities such as
`(schema, table, column, ordinal)` and compare them to catalog-derived observed
rows using full joins or `EXCEPT` in both directions. Canonicalize types with
`format_type`, expressions with `pg_get_expr`, constraints with catalog keys and
definitions, and indexes with semantic columns/predicate/operator classes.

Emit `missing`, `unexpected`, and `changed` rows in a deterministic order. Do
not hash OIDs, physical file locations, statistics, or generated names into the
contract unless they are deliberately contractual.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-02 Exercise 7, read from `information_schema.columns`, `expected`, and `pg_get_expr`. Build the answer toward `column_name`; keep `column_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-found-02 Exercise 7, expected output: one row per `column_name`. The final columns are `column_name`. The final order is `column_name`.
- **Independent verification:** For sql-found-02 Exercise 7, project `column_name` plus the raw source columns from `information_schema.columns`, `expected`, and `pg_get_expr` at each join stage; record row count and distinct `column_name`, then assert the final `column_name` values match those staged rows without unintended fanout or loss. Add one source row with a new `column_name`; verify the result gains exactly one row carrying that `column_name` value.
- **Intermediate relation check:** For sql-found-02 Exercise 7, run `observed` one at a time. Record each CTE's row count and `column_name` uniqueness before the next stage uses it.
- **Clause check:** For sql-found-02 Exercise 7, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `information_schema.columns`, `expected`, and `pg_get_expr`, preserve one row per `column_name`, and finish with `column_name` ordered by `column_name`.
- **Alternative/trade-off:** For sql-found-02 Exercise 7, the chosen form is justified by this lesson-specific rationale: Build expected rows with stable identities such as `(schema, table, column, ordinal)` and compare them to catalog-derived observed rows using full joins or `EXCEPT` in both directions. Evaluate another form against the concrete expected result (one row per `column_name`) and the verification above.
- **Edge case:** Add one source row with a new `column_name`; verify the result gains exactly one row carrying that `column_name` value.

## Exercise 8 — Phase-specific recovery

During expand, old code should still work; recovery may be a forward fix while
the additive object remains. During dual-write/backfill, pause or fence writers
before choosing a source of truth and reconcile every key. During contract,
old writers must already be absent; re-enabling them can corrupt the new rule.

Record compatible application versions, traffic state, lock/lag/error evidence,
backup restore point, lossy transformations, and decision owner at each gate.
A schema rollback is unsafe once new-only writes or external side effects have
occurred unless their data path is explicitly reversible and verified.

### Reasoning and verification

- **Inputs/evidence:** For sql-found-02 Exercise 8, use the inline `VALUES` fixture in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-found-02 Exercise 8, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`. The final order is `phase`.
- **Independent verification:** For sql-found-02 Exercise 8, restore into an isolated target and reconcile the inline `VALUES` fixture using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-found-02 Exercise 8, restore into an isolated target and reconcile the inline `VALUES` fixture using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-found-02 Exercise 8, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `artifact_name` and `restored_object`, and finish with `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status` ordered by `phase`.
- **Alternative/trade-off:** For sql-found-02 Exercise 8, the chosen form is justified by this lesson-specific rationale: During expand, old code should still work; recovery may be a forward fix while the additive object remains. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Edge cases and alternatives

- Parallel deployers need an advisory lock or a migration tool that serializes
  the manifest; this single-session fixture does not simulate a deployment race.
- `NOT VALID` reduces the initial validation work but does not make a malformed
  foreign key acceptable forever.
- A production backfill should be restartable and report progress, failed keys,
  WAL/replica impact, and reconciliation counts.
- Reference seeds need an ownership policy. `ON CONFLICT DO UPDATE` can overwrite
  operator-owned changes if ownership is not clear.
- An additive view contract helps readers, but writers need a deliberately
  compatible API, trigger, or application rollout plan of their own.
