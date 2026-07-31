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

- **Expected result/shape:** Exercise 1 must make “Manifest: return versions 1–5 once and in order with stable metadata” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `sm`, `api`, `sr`, `pro_migration_lab.service_requests`.
- **Independent verification:** For Exercise 1, inspect the relevant `pg_catalog` or `information_schema` rows for `sm`, `api`, `sr`, `pro_migration_lab.service_requests`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 1: deterministic metadata manifest.
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

- **Expected result/shape:** Exercise 2 must make “Compatibility: explain the version-2 view and order schema, reader, writer, backfill, validation, and contract deployments” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement.
- **Independent verification:** For Exercise 2, inspect the relevant `pg_catalog` or `information_schema` rows for `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 2: compatibility is demonstrated above: the stable API query still has its original interface while migrations 6-8 evolve only storage.
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

- **Expected result/shape:** Exercise 3 returns a table-shaped answer to “Forward series: design versions 6–8 for assignedteam as separate expand, backfill, and contract steps” at one result row per key or group explicitly named in the prompt. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 3, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
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

- **Expected result/shape:** Exercise 4 needs a labeled transaction/session transcript that demonstrates “Runner boundaries: identify nontransactional operations and explain why lossy changes do not have universal “down” migrations”. Capture statement order, affected keys/counts, lock or snapshot state, and the expected SQLSTATE when an error is part of the exercise; finish with no open lesson transaction or leftover shared fixture. Named evidence columns/objects: `CONCURRENTLY`.
- **Independent verification:** For Exercise 4, replay the written Session A/Session B order against `advanced_sql_training`, compare the observed values/SQLSTATE with the prediction, then query/drop the disposable fixture and confirm neither session retains a transaction or lock. The executable solution's check is: Exercise 4: CREATE DATABASE, VACUUM, and CREATE INDEX CONCURRENTLY need a runner-managed nontransactional boundary. Lossy recovery is a restore or forward-fix decision, not an automatic down-file convention.
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

- **Expected result/shape:** Exercise 5 returns a table-shaped answer to “Interrupted retry: make version 6 recoverable after an uncertain client disconnect, while detecting rather than concealing incompatible drift” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `sm`, `manifest_matches`, `c`, `schema_matches`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 5, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pro_migration_lab.schema_migrations`, `information_schema.columns`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 5: classify retry state before doing anything. Only (manifest present + exact observed contract) is safely "already applied"; every partial or incompatible state must stop for investigation.
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

- **Expected result/shape:** Exercise 6 needs a labeled transaction/session transcript that demonstrates “Low-lock rollout: mark boundaries and evidence for concurrent index creation and NOT VALID/VALIDATE CONSTRAINT”. Capture statement order, affected keys/counts, lock or snapshot state, and the expected SQLSTATE when an error is part of the exercise; finish with no open lesson transaction or leftover shared fixture. Named evidence columns/objects: `not`, `valid`, `validate`, `constraint`, `CONCURRENTLY`.
- **Independent verification:** For Exercise 6, replay the written Session A/Session B order against `advanced_sql_training`, compare the observed values/SQLSTATE with the prediction, then query/drop the disposable fixture and confirm neither session retains a transaction or lock. The executable solution's check is: Exercise 6: these reviewed templates are intentionally not executed in this fixture because CREATE INDEX CONCURRENTLY cannot run in a transaction: CREATE INDEX CONCURRENTLY servicerequeststeamidx ON promigrationlab.servicerequests (assignedteam); A low-lock CHECK rollout uses ADD ... NOT VALID, remediation, and a separate VALIDATE CONSTRAINT step with timeouts and monitoring.
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

- **Expected result/shape:** Exercise 7 needs the plan evidence for “Drift report: compare expected and observed columns, constraints, and indexes; label missing, unexpected, and changed objects deterministically”: one plan tree per compared query with node type, estimated rows, actual rows/loops when ANALYZE is used, and buffers or predicate details requested by the prompt. The underlying query must still return one catalog/behavior check per object or invariant. Named evidence columns/objects: `c`, `column_name`, `drift_status`, `e`, `o`.
- **Independent verification:** For Exercise 7, hold SQL text, parameters, seed data, and settings constant except for the intended change; compare result keys/counts from `information_schema.columns` before interpreting scan/join nodes, estimates, actual rows, loops, and buffers. The executable solution's check is: Exercise 7: a compact expected-versus-observed column drift report. Production contracts should extend this pattern to defaults, constraints, and indexes.
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

- **Expected result/shape:** Exercise 8 returns a table-shaped answer to “Failed deployment: write phase-specific compatibility, pause, restore, reconciliation, and decision evidence for recovery” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `recovery`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 8, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pro_migration_lab.schema_migrations`, `pro_migration_lab.service_requests`, `pro_migration_lab.service_requests_api`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 8: recovery is phase-specific; this deterministic matrix is a runbook skeleton, not permission to mutate a real environment.
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
