# SQL-OPS-02 Solutions — Backup and Recovery


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_ops_02_backup_restore_recovery_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_ops_02_backup_restore_recovery_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Logical backup, Custom format, Physical base backup, WAL, PITR, Timeline. Its worked-model focus is:
The SQL learner path creates source and independent restored relations, records a deterministic manifest, copies fixture data, and compares ordered MD5 digests and row counts. MD5 here detects accidental fixture drift; it is not a cryptographic authenticity/signing design.

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

Run the safe SQL solution:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_ops_02_backup_restore_recovery_solutions.sql
```

It creates no files or databases and rolls back `pro_recovery_lab`.

## Exercise 1 — Structural fingerprint

The solution orders information-schema column position/name/type/nullability and
catalog constraint type/definition before hashing. Deterministic ordering is
essential. Add index definitions, defaults, owners, grants, policies, routines,
extensions, and sequence state when those are contractual.

A data checksum can pass after a restore that omitted a foreign key, privilege,
or sequence. Structure and behavior require separate evidence.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 1, read from `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`. Compute `constraints` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
- **Expected result/shape:** For sql-ops-02 Exercise 1, expected output: exactly one aggregate summary row. The final columns are `constraints`.
- **Independent verification:** For sql-ops-02 Exercise 1, evaluate each of `row_count` in a separate control `SELECT` over `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; require one final row and compare every value. Add one source row with a new `constraints`; verify the result gains exactly one row carrying that `constraints` value.
- **Intermediate relation check:** For sql-ops-02 Exercise 1, run `columns`, and `constraints` one at a time. Record each CTE's row count and `constraints` uniqueness before the next stage uses it.
- **Clause check:** For sql-ops-02 Exercise 1, the solution actually uses `WITH`, `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`, preserve exactly one summary row, and finish with `constraints`.
- **Alternative/trade-off:** For sql-ops-02 Exercise 1, the chosen form is justified by this lesson-specific rationale: The solution orders information-schema column position/name/type/nullability and catalog constraint type/definition before hashing. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Add one source row with a new `constraints`; verify the result gains exactly one row carrying that `constraints` value.

## Exercise 2 — Corruption negative control

The source/restored ordered digests initially match. A savepoint update changes
one restored amount; the test requires a mismatch. Rolling back to the
savepoint must restore equality. This proves the checksum can detect the
specific corruption instead of always reporting success.

MD5 is used as a compact deterministic comparison, not to authenticate a backup
against a malicious actor. Authenticity needs trusted cryptographic controls and
key management outside this fixture.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 2, read the target keys from `pro_recovery_lab.restored_records` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-ops-02 Exercise 2, expected output: the command tag and an independently counted set of affected `affected_row_count` values. The final columns are `affected_row_count`, and `command_tag`.
- **Independent verification:** For sql-ops-02 Exercise 2, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `pro_recovery_lab.restored_records` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.
- **Intermediate relation check:** For sql-ops-02 Exercise 2, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `pro_recovery_lab.restored_records` again and prove rollback or idempotent retry.
- **Clause check:** For sql-ops-02 Exercise 2, the solution actually uses `FROM`, and `WHERE`. Read only those operations: begin at `pro_recovery_lab.restored_records`, preserve one row per `affected_row_count`, and finish with `affected_row_count`, and `command_tag`.
- **Alternative/trade-off:** For sql-ops-02 Exercise 2, the chosen form is justified by this lesson-specific rationale: The source/restored ordered digests initially match. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `affected_row_count` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.

## Exercise 3 — RPO/RTO strategy

The example's five-minute RPO cannot be met by a daily logical dump alone. It
chooses verified base backups plus continuous WAL for recoverability and a
separate replica for availability. The replica does not replace backup because
it can replay the same accidental write.

Measure RTO through timed end-to-end restore, replay, verification, application
startup, and controlled cutover—not file copy alone.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 3, use `pro_recovery_lab.recovery_plan` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-ops-02 Exercise 3, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `service_name`, `rpo`, `rto`, `backup_strategy`, and `availability_strategy`. The final order is `rp.service_name`.
- **Independent verification:** For sql-ops-02 Exercise 3, restore into an isolated target and reconcile `pro_recovery_lab.recovery_plan` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-ops-02 Exercise 3, restore into an isolated target and reconcile `pro_recovery_lab.recovery_plan` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-ops-02 Exercise 3, the solution actually uses `WITH`, `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_recovery_lab.recovery_plan`, preserve one row per `service_name`, and finish with `service_name`, `rpo`, `rto`, `backup_strategy`, and `availability_strategy` ordered by `rp.service_name`.
- **Alternative/trade-off:** For sql-ops-02 Exercise 3, the chosen form is justified by this lesson-specific rationale: The example's five-minute RPO cannot be met by a daily logical dump alone. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Exercise 4 — Logical restore rehearsal

Use the exact OS-specific commands in the guide only after peer review. Verify
tool versions, artifact exit/checksum/size, target emptiness, restore exit,
schema/data/contracts, owners/grants, sequences, extensions, routines, and
application smoke queries. Record elapsed time and clean only the exact
`ds60_restore_rehearsal` database/artifact.

`--no-owner --no-privileges` is appropriate for this local course rehearsal but
means ownership/grants are intentionally not reproduced; production recovery
must define their restoration.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 4, use `ds60_restore_rehearsal` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-ops-02 Exercise 4, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
- **Independent verification:** For sql-ops-02 Exercise 4, restore into an isolated target and reconcile `ds60_restore_rehearsal` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-ops-02 Exercise 4, restore into an isolated target and reconcile `ds60_restore_rehearsal` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-ops-02 Exercise 4, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `ds60_restore_rehearsal` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ops-02 Exercise 4, the chosen form is justified by this lesson-specific rationale: Use the exact OS-specific commands in the guide only after peer review. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Exercise 5 — PITR and retention

PITR needs a compatible base backup and an unbroken sequence of WAL through the
target, plus timeline history after recovery branches. Retain the base backup
and every required WAL segment together until a newer verified chain supersedes
them. Restore to a separate data directory/instance, replay to the last known
good target, verify, then decide promotion/cutover.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 5, use `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-ops-02 Exercise 5, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
- **Independent verification:** For sql-ops-02 Exercise 5, restore into an isolated target and reconcile `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-ops-02 Exercise 5, restore into an isolated target and reconcile `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-ops-02 Exercise 5, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ops-02 Exercise 5, the chosen form is justified by this lesson-specific rationale: PITR needs a compatible base backup and an unbroken sequence of WAL through the target, plus timeline history after recovery branches. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Exercise 6 — Evidence standard

A zero backup exit code proves only that one command reported success. It does
not prove artifact retention, readability, decryption, version compatibility,
complete scope, replay continuity, restore time, application behavior, or team
ability to execute the runbook. Only repeated isolated restore rehearsals with
recorded verification support a recoverability claim.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 6, complete the evidence written analysis and support its claims with read-only evidence from `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest`. Mark unverified assumptions explicitly.
- **Expected result/shape:** For sql-ops-02 Exercise 6, expected output: a completed the evidence written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Independent verification:** For sql-ops-02 Exercise 6, check the evidence written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
- **Intermediate relation check:** For sql-ops-02 Exercise 6, check the evidence written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
- **Clause check:** For sql-ops-02 Exercise 6, this is a written operational artifact rather than a clause-reading exercise; trace each claim to `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest` or label it as proposed policy.
- **Alternative/trade-off:** For sql-ops-02 Exercise 6, the chosen form is justified by this lesson-specific rationale: A zero backup exit code proves only that one command reported success. Evaluate another form against the concrete expected result (a completed the evidence written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields) and the verification above.
- **Edge case:** Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.

## Exercise 7 — Encryption, authenticity, and custody

Encrypt artifacts in transit and at rest with approved rotated keys held
separately from the backup. Restrict backup/WAL/manifests to recovery roles,
audit access, test emergency key retrieval, and preserve old keys for every
retained generation. Define immutable retention and verified deletion.

Database page or dump checksums detect some accidental corruption; they do not
authenticate an artifact against malicious replacement. Sign or MAC trusted
manifests and verify them before restore without putting secrets in commands,
logs, or repository files.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 7, read from `pro_recovery_lab.artifact_controls`. Build the answer toward `encryptioncustody_answer`; keep `encryptioncustody_answer` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-02 Exercise 7, expected output: one row per `encryptioncustody_answer`. The final columns are `encryptioncustody_answer`. The final order is `artifact_kind`.
- **Independent verification:** For sql-ops-02 Exercise 7, reselect the returned keys directly from the source; require unique `encryptioncustody_answer` where the expected grain is one row per key and confirm the projected `encryptioncustody_answer` against `pro_recovery_lab.artifact_controls`. Add one source row with a new `encryptioncustody_answer`; verify the result gains exactly one row carrying that `encryptioncustody_answer` value.
- **Intermediate relation check:** For sql-ops-02 Exercise 7, check `artifact_kind` before applying the row cap.
- **Clause check:** For sql-ops-02 Exercise 7, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_recovery_lab.artifact_controls`, preserve one row per `encryptioncustody_answer`, and finish with `encryptioncustody_answer` ordered by `artifact_kind`.
- **Alternative/trade-off:** For sql-ops-02 Exercise 7, the chosen form is justified by this lesson-specific rationale: Encrypt artifacts in transit and at rest with approved rotated keys held separately from the backup. Evaluate another form against the concrete expected result (one row per `encryptioncustody_answer`) and the verification above.
- **Edge case:** Add one source row with a new `encryptioncustody_answer`; verify the result gains exactly one row carrying that `encryptioncustody_answer` value.

## Exercise 8 — Restore the whole contract

Set sequence/identity state beyond current maxima and test the next insert.
Inventory large objects, extension versions, owners, memberships, object/default
privileges, RLS policies, security labels, routines, and external configuration.
Cluster-global roles/settings may be outside a database dump.

Classify each component by artifact/source of truth and test it explicitly. A
successful SELECT does not prove that a writer can generate a new identity or
that a low-privilege caller has intended access.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 8, read from the inline `VALUES` fixture. Build the answer toward `component`, and `expected_source`; keep `component` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-02 Exercise 8, expected output: one row per `component`. The final columns are `component`, and `expected_source`. The final order is `component`.
- **Independent verification:** For sql-ops-02 Exercise 8, reselect the returned keys directly from the source; require unique `component` where the expected grain is one row per key and confirm the projected `component`, and `expected_source` against the inline `VALUES` fixture. Add one source row with a new `component`; verify the result gains exactly one row carrying that `component` value.
- **Intermediate relation check:** For sql-ops-02 Exercise 8, check `component` before applying the row cap.
- **Clause check:** For sql-ops-02 Exercise 8, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `component`, and finish with `component`, and `expected_source` ordered by `component`.
- **Alternative/trade-off:** For sql-ops-02 Exercise 8, the chosen form is justified by this lesson-specific rationale: Set sequence/identity state beyond current maxima and test the next insert. Evaluate another form against the concrete expected result (one row per `component`) and the verification above.
- **Edge case:** Add one source row with a new `component`; verify the result gains exactly one row carrying that `component` value.

## Exercise 9 — Recover across a major version

Logical dump/restore rebuilds objects through SQL and supports transformation
but can be slow. `pg_upgrade` is faster under strict source/target binary and
extension requirements; it still needs backup and verification.

Rehearse exact versions with extensions, drivers, collations, and critical
queries. Run post-upgrade checks/ANALYZE, detect collation drift, time cutover,
verify applications, and preserve a fenced rollback window before accepting
incompatible new writes.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 9, use `pg_catalog.pg_database`, and `pg_upgrade` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-ops-02 Exercise 9, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `server_version`, `server_version_num`, `datcollate`, and `datctype`.
- **Independent verification:** For sql-ops-02 Exercise 9, restore into an isolated target and reconcile `pg_catalog.pg_database`, and `pg_upgrade` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-ops-02 Exercise 9, restore into an isolated target and reconcile `pg_catalog.pg_database`, and `pg_upgrade` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
- **Clause check:** For sql-ops-02 Exercise 9, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `pg_catalog.pg_database`, and `pg_upgrade`, preserve one row per `server_version`, and finish with `server_version`, `server_version_num`, `datcollate`, and `datctype`.
- **Alternative/trade-off:** For sql-ops-02 Exercise 9, the chosen form is justified by this lesson-specific rationale: Logical dump/restore rebuilds objects through SQL and supports transformation but can be slow. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Exercise 10 — Selective restore dependency boundary

Traverse types, sequences, functions, extensions, foreign keys in both
directions, views, triggers, policies, owners/ACLs, and downstream consumers.
Decide how external references and intentionally omitted rows remain valid.

When scope is uncertain, restore the full artifact to an isolated target first
and export/reconcile the intended subset. Selective recovery can be syntactically
successful but semantically incomplete.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 10, use `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
- **Expected result/shape:** For sql-ops-02 Exercise 10, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `contype`, and `dependency_contract`. The final order is `rel.relname, con.contype, dependency_contract`.
- **Independent verification:** For sql-ops-02 Exercise 10, restore into an isolated target and reconcile `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
- **Intermediate relation check:** For sql-ops-02 Exercise 10, start with the first relation in `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `contype` so the exact fanout or loss is visible.
- **Clause check:** For sql-ops-02 Exercise 10, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`, preserve one row per `contype`, and finish with `contype`, and `dependency_contract` ordered by `rel.relname, con.contype, dependency_contract`.
- **Alternative/trade-off:** For sql-ops-02 Exercise 10, the chosen form is justified by this lesson-specific rationale: Traverse types, sequences, functions, extensions, foreign keys in both directions, views, triggers, policies, owners/ACLs, and downstream consumers. Evaluate another form against the concrete expected result (a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record) and the verification above.
- **Edge case:** Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.

## Exercise 11 — Capacity and RTO test

Measure discovery/transfer, decrypt/decompress, CPU, I/O, parallel jobs, WAL,
constraint/index creation, statistics, verification, application startup, and
routing. Record peak disk/memory/network, locks, throttling, and safety margin.

Small fixtures miss saturation, random I/O, checkpoint pressure, sort spills,
catalog contention, and skew. RTO ends at verified service readiness, not when
one restore command exits.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 11, read from `pro_recovery_lab.capacity_budget`. Build the answer toward `capacity_answer`; keep `capacity_answer` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-02 Exercise 11, expected output: one row per `capacity_answer`. The final columns are `capacity_answer`. The final order is `phase`.
- **Independent verification:** For sql-ops-02 Exercise 11, reselect the returned keys directly from the source; require unique `capacity_answer` where the expected grain is one row per key and confirm the projected `capacity_answer` against `pro_recovery_lab.capacity_budget`. Add one source row with a new `capacity_answer`; verify the result gains exactly one row carrying that `capacity_answer` value.
- **Intermediate relation check:** For sql-ops-02 Exercise 11, check `phase` before applying the row cap.
- **Clause check:** For sql-ops-02 Exercise 11, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pro_recovery_lab.capacity_budget`, preserve one row per `capacity_answer`, and finish with `capacity_answer` ordered by `phase`.
- **Alternative/trade-off:** For sql-ops-02 Exercise 11, the chosen form is justified by this lesson-specific rationale: Measure discovery/transfer, decrypt/decompress, CPU, I/O, parallel jobs, WAL, constraint/index creation, statistics, verification, application startup, and routing. Evaluate another form against the concrete expected result (one row per `capacity_answer`) and the verification above.
- **Edge case:** Add one source row with a new `capacity_answer`; verify the result gains exactly one row carrying that `capacity_answer` value.

## Exercise 12 — Recovery game-day record

Preassign incident commander, operators, owners, observers, and stop authority.
Timestamp detection, decisions, commands, artifacts, injected failures,
verification, achieved data point/service time, and runbook deviations.

End with fenced cleanup, protected logs, unresolved risks with owners/dates,
runbook changes, and the next rehearsal. A narrative without raw evidence and
accountable follow-up is not a recovery control.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 12, read from the inline `VALUES` fixture. Build the answer toward `role_name`, and `responsibility`; keep `role_name` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-ops-02 Exercise 12, expected output: one row per `role_name`. The final columns are `role_name`, and `responsibility`. The final order is `role_name`.
- **Independent verification:** For sql-ops-02 Exercise 12, reselect the returned keys directly from the source; require unique `role_name` where the expected grain is one row per key and confirm the projected `role_name`, and `responsibility` against the inline `VALUES` fixture. Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.
- **Intermediate relation check:** For sql-ops-02 Exercise 12, check `role_name` before applying the row cap.
- **Clause check:** For sql-ops-02 Exercise 12, the solution actually uses `FROM`, `SELECT`, and `ORDER BY`. Read only those operations: begin at the inline `VALUES` fixture, preserve one row per `role_name`, and finish with `role_name`, and `responsibility` ordered by `role_name`.
- **Alternative/trade-off:** For sql-ops-02 Exercise 12, the chosen form is justified by this lesson-specific rationale: Preassign incident commander, operators, owners, observers, and stop authority. Evaluate another form against the concrete expected result (one row per `role_name`) and the verification above.
- **Edge case:** Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.

## Edge cases

- Long-running logical dumps observe a consistent snapshot but may increase
  retention pressure.
- Large objects and cluster-global roles need explicit scope.
- Encryption keys must remain recoverable but separate from protected backups.
- Legal retention and deletion requirements apply to backup copies too.
