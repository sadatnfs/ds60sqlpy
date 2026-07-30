# SQL-OPS-02 Solutions — Backup and Recovery

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

## Exercise 2 — Corruption negative control

The source/restored ordered digests initially match. A savepoint update changes
one restored amount; the test requires a mismatch. Rolling back to the
savepoint must restore equality. This proves the checksum can detect the
specific corruption instead of always reporting success.

MD5 is used as a compact deterministic comparison, not to authenticate a backup
against a malicious actor. Authenticity needs trusted cryptographic controls and
key management outside this fixture.

## Exercise 3 — RPO/RTO strategy

The example's five-minute RPO cannot be met by a daily logical dump alone. It
chooses verified base backups plus continuous WAL for recoverability and a
separate replica for availability. The replica does not replace backup because
it can replay the same accidental write.

Measure RTO through timed end-to-end restore, replay, verification, application
startup, and controlled cutover—not file copy alone.

## Exercise 4 — Logical restore rehearsal

Use the exact OS-specific commands in the guide only after peer review. Verify
tool versions, artifact exit/checksum/size, target emptiness, restore exit,
schema/data/contracts, owners/grants, sequences, extensions, routines, and
application smoke queries. Record elapsed time and clean only the exact
`ds60_restore_rehearsal` database/artifact.

`--no-owner --no-privileges` is appropriate for this local course rehearsal but
means ownership/grants are intentionally not reproduced; production recovery
must define their restoration.

## Exercise 5 — PITR and retention

PITR needs a compatible base backup and an unbroken sequence of WAL through the
target, plus timeline history after recovery branches. Retain the base backup
and every required WAL segment together until a newer verified chain supersedes
them. Restore to a separate data directory/instance, replay to the last known
good target, verify, then decide promotion/cutover.

## Exercise 6 — Evidence standard

A zero backup exit code proves only that one command reported success. It does
not prove artifact retention, readability, decryption, version compatibility,
complete scope, replay continuity, restore time, application behavior, or team
ability to execute the runbook. Only repeated isolated restore rehearsals with
recorded verification support a recoverability claim.

## Exercise 7 — Encryption, authenticity, and custody

Encrypt artifacts in transit and at rest with approved rotated keys held
separately from the backup. Restrict backup/WAL/manifests to recovery roles,
audit access, test emergency key retrieval, and preserve old keys for every
retained generation. Define immutable retention and verified deletion.

Database page or dump checksums detect some accidental corruption; they do not
authenticate an artifact against malicious replacement. Sign or MAC trusted
manifests and verify them before restore without putting secrets in commands,
logs, or repository files.

## Exercise 8 — Restore the whole contract

Set sequence/identity state beyond current maxima and test the next insert.
Inventory large objects, extension versions, owners, memberships, object/default
privileges, RLS policies, security labels, routines, and external configuration.
Cluster-global roles/settings may be outside a database dump.

Classify each component by artifact/source of truth and test it explicitly. A
successful SELECT does not prove that a writer can generate a new identity or
that a low-privilege caller has intended access.

## Exercise 9 — Recover across a major version

Logical dump/restore rebuilds objects through SQL and supports transformation
but can be slow. `pg_upgrade` is faster under strict source/target binary and
extension requirements; it still needs backup and verification.

Rehearse exact versions with extensions, drivers, collations, and critical
queries. Run post-upgrade checks/ANALYZE, detect collation drift, time cutover,
verify applications, and preserve a fenced rollback window before accepting
incompatible new writes.

## Exercise 10 — Selective restore dependency boundary

Traverse types, sequences, functions, extensions, foreign keys in both
directions, views, triggers, policies, owners/ACLs, and downstream consumers.
Decide how external references and intentionally omitted rows remain valid.

When scope is uncertain, restore the full artifact to an isolated target first
and export/reconcile the intended subset. Selective recovery can be syntactically
successful but semantically incomplete.

## Exercise 11 — Capacity and RTO test

Measure discovery/transfer, decrypt/decompress, CPU, I/O, parallel jobs, WAL,
constraint/index creation, statistics, verification, application startup, and
routing. Record peak disk/memory/network, locks, throttling, and safety margin.

Small fixtures miss saturation, random I/O, checkpoint pressure, sort spills,
catalog contention, and skew. RTO ends at verified service readiness, not when
one restore command exits.

## Exercise 12 — Recovery game-day record

Preassign incident commander, operators, owners, observers, and stop authority.
Timestamp detection, decisions, commands, artifacts, injected failures,
verification, achieved data point/service time, and runbook deviations.

End with fenced cleanup, protected logs, unresolved risks with owners/dates,
runbook changes, and the next rehearsal. A narrative without raw evidence and
accountable follow-up is not a recovery control.

## Edge cases

- Long-running logical dumps observe a consistent snapshot but may increase
  retention pressure.
- Large objects and cluster-global roles need explicit scope.
- Encryption keys must remain recoverable but separate from protected backups.
- Legal retention and deletion requirements apply to backup copies too.
