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

- **Inputs/evidence:** For sql-found-02 Exercise 1, read versions 1–5 from `pro_migration_lab.schema_migrations`, preserving the immutable migration identity fields `migration_id`, `migration_name`, and `content_tag`.
- **Expected result/shape:** For sql-found-02 Exercise 1, expected output: exactly five rows at one-row-per-migration grain, columns `migration_id`, `migration_name`, and `content_tag`, ordered by `migration_id`; the independent invariant is the exact array `[1, 2, 3, 4, 5]`.
- **Independent verification:** For sql-found-02 Exercise 1, assert the exact ordered ID array, count five distinct IDs, compare each name/tag with the reviewed fixture manifest, and prove that a missing, duplicate, reordered, or altered identity fails rather than being silently accepted.

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

- **Inputs/evidence:** For sql-found-02 Exercise 2, inspect version-2 storage and `service_requests_api` before the backfill, then return a five-step deployment matrix covering expand, compatible code, backfill, validation, and contract.
- **Expected result/shape:** For sql-found-02 Exercise 2, expected output: three request rows showing NULL `expanded_storage` but unchanged `stable_api_value`, followed by five ordered rollout rows with `step_number`, compatibility, write policy, and promotion gate.
- **Independent verification:** For sql-found-02 Exercise 2, assert every stable API value equals `COALESCE(expanded_storage, legacy_storage)`, the API keeps its five-column interface, and the contract step is gated on zero old-writer traffic plus a complete backfill.

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

- **Inputs/evidence:** For sql-found-02 Exercise 3, apply three new immutable migrations: nullable `assigned_team`, deterministic backfill, then default/NOT NULL/allowed-values CHECK; record metadata last inside each transaction.
- **Expected result/shape:** For sql-found-02 Exercise 3, expected output: command tags for migrations 6–8; one row per request with `assigned_team`; three manifest rows; one column-catalog row proving text, NOT NULL, and `'general'` default; and one validated CHECK definition.
- **Independent verification:** For sql-found-02 Exercise 3, assert manifest IDs are exactly `[1..8]`, every high/critical request is `response`, every other request is `general`, no NULL or disallowed value remains, the stable API projection is unchanged, and the catalog matches the promised contract.

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

- **Inputs/evidence:** For sql-found-02 Exercise 4, build an inspectable decision matrix for `CREATE DATABASE`, `VACUUM`, `CREATE INDEX CONCURRENTLY`, and a lossy data change; do not pretend those operations ran inside the disposable lesson.
- **Expected result/shape:** For sql-found-02 Exercise 4, expected output: four rows ordered by `step_number` with columns `operation`, `transaction_requirement`, `reason`, and `recovery_policy`.
- **Independent verification:** For sql-found-02 Exercise 4, cross-check each PostgreSQL transaction restriction in a disposable environment, distinguish retry/forward-fix from destructive rollback, and require backup plus reconciliation evidence before any recovery from a lossy change.

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

- **Inputs/evidence:** For sql-found-02 Exercise 5, independently test the version-006 manifest identity and the observed `assigned_team` schema contract, returning two labeled booleans in one row.
- **Expected result/shape:** For sql-found-02 Exercise 5, expected output: exactly one row with `manifest_matches` and `schema_matches`; only `(true, true)` is the already-applied state, `(false, false)` is eligible to apply, and either mixed state must stop.
- **Independent verification:** For sql-found-02 Exercise 5, probe all four manifest/schema truth combinations, verify name and content identity as well as column type/nullability/default, serialize deployers, and prove incompatible same-named state fails instead of being hidden by `IF NOT EXISTS`.

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

- **Inputs/evidence:** For sql-found-02 Exercise 6, return an eight-step low-lock rollout plan for concurrent index creation and `CHECK ... NOT VALID`/remediation/`VALIDATE CONSTRAINT`, with explicit transaction boundaries, evidence, and abort conditions.
- **Expected result/shape:** For sql-found-02 Exercise 6, expected output: eight rows ordered by `step_number` with `rollout_step`, `transaction_boundary`, `required_evidence`, and `abort_condition`; the SQL templates remain deliberately unexecuted.
- **Independent verification:** For sql-found-02 Exercise 6, require pre/post catalog checks for index readiness/validity and constraint validation, bounded lock/lag/WAL/disk thresholds, restartable backfill reconciliation, and an explicit policy for a known invalid index artifact.

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

- **Inputs/evidence:** For sql-found-02 Exercise 7, FULL JOIN expected and unfiltered observed manifests for all `service_requests` columns, constraints, and indexes, comparing semantic properties rather than OIDs or storage details.
- **Expected result/shape:** For sql-found-02 Exercise 7, expected output: three deterministic result sets—one row per column, constraint, and index—with expected/observed evidence and `drift_status` equal to `matches`, `missing`, `unexpected`, or `changed`.
- **Independent verification:** For sql-found-02 Exercise 7, prove the clean fixture reports only `matches`; inject one disposable missing, unexpected, and changed object; confirm every branch is reachable, defaults and validation state are checked, and ordering uses the displayed object identity.

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

- **Inputs/evidence:** For sql-found-02 Exercise 8, model expand, backfill, and contract recovery as an ordered inline matrix with compatible versions, write state, reversible action, required evidence, and primary action.
- **Expected result/shape:** For sql-found-02 Exercise 8, expected output: exactly three rows ordered by numeric `step_number` from expand through contract, retaining every recovery field rather than sorting phases lexically.
- **Independent verification:** For sql-found-02 Exercise 8, walk one failure injected at each phase, prove promotion stops when its evidence is absent, and record that schema reversal cannot reconstruct discarded values or undo externally observed writes.

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
