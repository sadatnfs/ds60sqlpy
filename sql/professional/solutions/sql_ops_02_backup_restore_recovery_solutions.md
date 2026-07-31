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

- **Inputs/evidence:** For sql-ops-02 Exercise 1, canonicalize source and restored column, constraint, and index semantics from information schema and PostgreSQL catalogs, excluding volatile OIDs and generated object names before comparing or hashing.
- **Expected result/shape:** For sql-ops-02 Exercise 1, expected output: ordered semantic rows with contract side, relation role, object kind, item order/name, and JSON definition, followed by one fingerprint row where source and restored hashes match and `mismatch_rows = 0`.
- **Independent verification:** For sql-ops-02 Exercise 1, compare visible canonical rows before hashes, then alter a default, constraint, and index separately and require each change to produce diagnosable mismatch rows while an OID change remains outside the contract.

## Exercise 2 — Corruption negative control

The source/restored ordered digests initially match. A savepoint update changes
one restored amount; the test requires a mismatch. Rolling back to the
savepoint must restore equality. This proves the checksum can detect the
specific corruption instead of always reporting success.

MD5 is used as a compact deterministic comparison, not to authenticate a backup
against a malicious actor. Authenticity needs trusted cryptographic controls and
key management outside this fixture.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 2, record source/restored checksums and counts, corrupt one restored amount after a savepoint, compare again, roll back to that savepoint, and run the comparison a third time.
- **Expected result/shape:** For sql-ops-02 Exercise 2, expected output: baseline, corrupted, and after-savepoint-rollback observations; equality is true, false, then true, with row counts unchanged and the intentional mismatch explicitly observed.
- **Independent verification:** For sql-ops-02 Exercise 2, supplement digests with row counts and key-level detail, corrupt a second chosen key to prove the detail query identifies it, and require the post-rollback comparison to return to the reviewed baseline.

## Exercise 3 — RPO/RTO strategy

The example's five-minute RPO cannot be met by a daily logical dump alone. It
chooses verified base backups plus continuous WAL for recoverability and a
separate replica for availability. The replica does not replace backup because
it can replay the same accidental write.

Measure RTO through timed end-to-end restore, replay, verification, application
startup, and controlled cutover—not file copy alone.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 3, enter explicit service RPO and RTO requirements in `pro_recovery_lab.recovery_plan`, then choose backup and availability strategies separately with their limits.
- **Expected result/shape:** For sql-ops-02 Exercise 3, expected output: one row per service with `service_name`, `rpo`, `rto`, `backup_strategy`, and `availability_strategy`, ordered by service; the example targets five-minute RPO and thirty-minute RTO.
- **Independent verification:** For sql-ops-02 Exercise 3, map RPO to recoverable data age and RTO to restore-through-application-readiness time, then remove replicas and backups in separate thought experiments to prove neither substitutes for the other.

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

- **Inputs/evidence:** For sql-ops-02 Exercise 4, review literal dump/create/restore commands outside this transaction and use the SQL matrix to specify evidence for target isolation, catalogs, data, application behavior, and cleanup.
- **Expected result/shape:** For sql-ops-02 Exercise 4, expected output: seven ordered rows with `phase_number`, `phase_name`, and `required_evidence`, covering dump, target creation, restore, catalogs/security, data, application checks, and cleanup; no external command runs here.
- **Independent verification:** For sql-ops-02 Exercise 4, execute only in a separately created disposable database after peer review, reconcile rows and semantic objects including owners/grants and sequence state, and block completion on any failed phase.

## Exercise 5 — PITR and retention

PITR needs a compatible base backup and an unbroken sequence of WAL through the
target, plus timeline history after recovery branches. Retain the base backup
and every required WAL segment together until a newer verified chain supersedes
them. Restore to a separate data directory/instance, replay to the last known
good target, verify, then decide promotion/cutover.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 5, model the PITR evidence chain from a compatible base backup through every required WAL segment, timeline history, target specification, retention overlap, and recovered-state validation.
- **Expected result/shape:** For sql-ops-02 Exercise 5, expected output: six ordered rows with `component_number`, `component`, and `required_evidence`; the lesson records a recovery plan and does not configure archiving.
- **Independent verification:** For sql-ops-02 Exercise 5, remove one required WAL segment and then the usable base backup as separate negative controls, and assert both scenario results mark the target unrecoverable before application validation.

## Exercise 6 — Evidence standard

A zero backup exit code proves only that one command reported success. It does
not prove artifact retention, readability, decryption, version compatibility,
complete scope, replay continuity, restore time, application behavior, or team
ability to execute the runbook. Only repeated isolated restore rehearsals with
recorded verification support a recoverability claim.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 6, classify command exit, artifact manifest, isolated restore, catalog/data reconciliation, and application smoke tests as separate evidence layers.
- **Expected result/shape:** For sql-ops-02 Exercise 6, expected output: five ordered rows with `layer_number`, `evidence_layer`, `what_it_proves`, and `what_it_does_not_prove`; exit zero proves only that the backup program reported success.
- **Independent verification:** For sql-ops-02 Exercise 6, inject a valid-looking but incomplete artifact or omit one critical restored object, and prove early command evidence can pass while later reconciliation blocks a recoverable decision.

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

- **Inputs/evidence:** For sql-ops-02 Exercise 7, populate `pro_recovery_lab.artifact_controls` for logical dumps, base backups, and WAL archives, separating encryption, integrity manifest, key owner, and restore role.
- **Expected result/shape:** For sql-ops-02 Exercise 7, expected output: three ordered rows with `artifact_kind`, `encrypted`, `integrity_manifest`, `key_owner`, and `restore_role`; every restorable artifact is encrypted and has integrity evidence.
- **Independent verification:** For sql-ops-02 Exercise 7, verify key custody is distinct from restore authorization, extend the review to manifest/key records, and rehearse rotation and deletion without making retained backups permanently unrestorable.

## Exercise 8 — Restore the whole contract

Set sequence/identity state beyond current maxima and test the next insert.
Inventory large objects, extension versions, owners, memberships, object/default
privileges, RLS policies, security labels, routines, and external configuration.
Cluster-global roles/settings may be outside a database dump.

Classify each component by artifact/source of truth and test it explicitly. A
successful SELECT does not prove that a writer can generate a new identity or
that a low-privilege caller has intended access.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 8, classify restored data/schema, roles/memberships, sequences/identity, extensions, and external configuration by their authoritative source rather than assuming one artifact contains everything.
- **Expected result/shape:** For sql-ops-02 Exercise 8, expected output: five ordered baseline rows with `component` and `expected_source`; the accompanying checklist extends coverage to large objects, default privileges, and security labels when required.
- **Independent verification:** For sql-ops-02 Exercise 8, mark each required component as artifact-contained, separately captured, or rebuilt for the chosen backup format, and fail the checklist when any component lacks both a source and validation query.

## Exercise 9 — Recover across a major version

Logical dump/restore rebuilds objects through SQL and supports transformation
but can be slow. `pg_upgrade` is faster under strict source/target binary and
extension requirements; it still needs backup and verification.

Rehearse exact versions with extensions, drivers, collations, and critical
queries. Run post-upgrade checks/ANALYZE, detect collation drift, time cutover,
verify applications, and preserve a fenced rollback window before accepting
incompatible new writes.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 9, query the current database for server version number plus database collation/ctype and separately review logical-restore versus binary-upgrade compatibility, extension, statistics, driver, and rollback evidence.
- **Expected result/shape:** For sql-ops-02 Exercise 9, expected output: exactly one local capability row with `server_version`, `server_version_num`, `datcollate`, and `datctype`; the broader major-version plan remains explicitly review-only.
- **Independent verification:** For sql-ops-02 Exercise 9, capture the same capability row in the isolated target and block cutover on extension incompatibility, collation drift, missing ANALYZE evidence, or failed driver/application tests even when upgrade tooling exits zero.

## Exercise 10 — Selective restore dependency boundary

Traverse types, sequences, functions, extensions, foreign keys in both
directions, views, triggers, policies, owners/ACLs, and downstream consumers.
Decide how external references and intentionally omitted rows remain valid.

When scope is uncertain, restore the full artifact to an isolated target first
and export/reconcile the intended subset. Selective recovery can be syntactically
successful but semantically incomplete.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 10, inspect `pg_constraint`, `pg_class`, and `pg_namespace` for recovery-lab relations, then extend the selective-restore inventory to referenced types, functions, sequences, privileges, and downstream consumers.
- **Expected result/shape:** For sql-ops-02 Exercise 10, expected output: one row per semantic constraint dependency with `relation_name`, `constraint_type`, and `dependency_contract`, ordered by all three fields.
- **Independent verification:** For sql-ops-02 Exercise 10, prove every referenced and referencing object is restored or deliberately remapped, remove one required dependency in an isolated target, and choose a full isolated restore when closure cannot be established.

## Exercise 11 — Capacity and RTO test

Measure discovery/transfer, decrypt/decompress, CPU, I/O, parallel jobs, WAL,
constraint/index creation, statistics, verification, application startup, and
routing. Record peak disk/memory/network, locks, throttling, and safety margin.

Small fixtures miss saturation, random I/O, checkpoint pressure, sort spills,
catalog contention, and skew. RTO ends at verified service readiness, not when
one restore command exits.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 11, fill `pro_recovery_lab.capacity_budget` with measured transfer, restore, verification, and routing phases, recording duration, peak bytes, and evidence notes at representative scale.
- **Expected result/shape:** For sql-ops-02 Exercise 11, expected output: four ordered rows with `phase`, `measured_seconds`, `peak_bytes`, and `evidence_note`; NULL measurements in the starter matrix are explicit work still to complete, not passing evidence.
- **Independent verification:** For sql-ops-02 Exercise 11, sum the measured critical path plus named safety margin against RTO and separately record throughput, CPU, I/O, parallelism, WAL, and free-space headroom instead of linearly extrapolating a tiny fixture.

## Exercise 12 — Recovery game-day record

Preassign incident commander, operators, owners, observers, and stop authority.
Timestamp detection, decisions, commands, artifacts, injected failures,
verification, achieved data point/service time, and runbook deviations.

End with fenced cleanup, protected logs, unresolved risks with owners/dates,
runbook changes, and the next rehearsal. A narrative without raw evidence and
accountable follow-up is not a recovery control.

### Reasoning and verification

- **Inputs/evidence:** For sql-ops-02 Exercise 12, use the inline authority map for incident commander, recovery operator, application owner, and observer, then attach those roles to a timestamped recovery game-day record.
- **Expected result/shape:** For sql-ops-02 Exercise 12, expected output: four ordered rows with `role_name` and `responsibility`; the completed record also captures decisions, injected failures, achieved RPO/RTO, gaps, cleanup, owners, and next rehearsal date.
- **Independent verification:** For sql-ops-02 Exercise 12, require exactly one accountable role for every action, link each injected failure to observed evidence, assign owner/due date to every gap, and compare achieved RPO/RTO with Exercise 3 requirements.

## Edge cases

- Long-running logical dumps observe a consistent snapshot but may increase
  retention pressure.
- Large objects and cluster-global roles need explicit scope.
- Encryption keys must remain recoverable but separate from protected backups.
- Legal retention and deletion requirements apply to backup copies too.
