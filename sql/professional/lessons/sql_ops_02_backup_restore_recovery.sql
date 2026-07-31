-- SQL-OPS-02: Backup, restore, and recovery rehearsals
-- BEGINNER WORKFLOW — sql-ops-02: Backup, Restore, and Recovery Rehearsals
-- Guide: sql/professional/companion-guides/sql_ops_02_backup_restore_recovery.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-ops-02/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pro_recovery_lab.source_accounts, pro_recovery_lab.source_entries, pro_recovery_lab.backup_manifest, pro_recovery_lab.restored_accounts, pro_recovery_lab.restored_entries.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Target: PostgreSQL 16+
-- This SQL simulates and verifies a logical restore inside one transaction.
-- It does not invoke pg_dump, change WAL settings, or perform cluster recovery.

\set ON_ERROR_STOP on
\echo 'SQL-OPS-02: disposable restore-verification simulation'
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_recovery_lab;

CREATE TABLE pro_recovery_lab.source_accounts (
    account_id bigint PRIMARY KEY,
    account_key text NOT NULL UNIQUE,
    display_name text NOT NULL
);

CREATE TABLE pro_recovery_lab.source_entries (
    entry_id bigint PRIMARY KEY,
    account_id bigint NOT NULL
        REFERENCES pro_recovery_lab.source_accounts (account_id),
    amount numeric(12, 2) NOT NULL,
    occurred_at timestamptz NOT NULL,
    note text NOT NULL
);

INSERT INTO pro_recovery_lab.source_accounts
VALUES
    (1, 'ACC-100', 'Operations'),
    (2, 'ACC-101', 'Learning');

INSERT INTO pro_recovery_lab.source_entries
VALUES
    (101, 1, 25.00, TIMESTAMPTZ '2026-03-01 10:00:00+00', 'Initial allocation'),
    (102, 1, -5.00, TIMESTAMPTZ '2026-03-02 11:00:00+00', 'Adjustment'),
    (103, 2, 12.50, TIMESTAMPTZ '2026-03-03 12:00:00+00', 'Reference material');

CREATE TABLE pro_recovery_lab.backup_manifest (
    backup_id text PRIMARY KEY,
    backup_kind text NOT NULL
        CHECK (backup_kind IN ('logical', 'physical')),
    backup_format text NOT NULL,
    source_database text NOT NULL,
    server_version_num integer NOT NULL,
    captured_at timestamptz NOT NULL,
    account_rows integer NOT NULL,
    entry_rows integer NOT NULL,
    accounts_checksum text NOT NULL,
    entries_checksum text NOT NULL
);

WITH account_digest AS (
    SELECT md5(
        string_agg(
            concat_ws('|', a.account_id, a.account_key, a.display_name),
            E'\n'
            ORDER BY a.account_id
        )
    ) AS checksum
    FROM pro_recovery_lab.source_accounts AS a
),
entry_digest AS (
    SELECT md5(
        string_agg(
            concat_ws(
                '|',
                e.entry_id,
                e.account_id,
                e.amount,
                e.occurred_at AT TIME ZONE 'UTC',
                e.note
            ),
            E'\n'
            ORDER BY e.entry_id
        )
    ) AS checksum
    FROM pro_recovery_lab.source_entries AS e
)
INSERT INTO pro_recovery_lab.backup_manifest (
    backup_id,
    backup_kind,
    backup_format,
    source_database,
    server_version_num,
    captured_at,
    account_rows,
    entry_rows,
    accounts_checksum,
    entries_checksum
)
SELECT
    'course-logical-20260303',
    'logical',
    'custom',
    current_database(),
    current_setting('server_version_num')::integer,
    TIMESTAMPTZ '2026-03-03 13:00:00+00',
    (SELECT COUNT(*) FROM pro_recovery_lab.source_accounts)::integer,
    (SELECT COUNT(*) FROM pro_recovery_lab.source_entries)::integer,
    account_digest.checksum,
    entry_digest.checksum
FROM account_digest
CROSS JOIN entry_digest;

-- A restore rehearsal must create independent target relations. LIKE INCLUDING
-- ALL copies many properties, but foreign keys are added explicitly and the
-- later contract checks must prove the actual result.
CREATE TABLE pro_recovery_lab.restored_accounts (
    LIKE pro_recovery_lab.source_accounts INCLUDING ALL
);

CREATE TABLE pro_recovery_lab.restored_entries (
    LIKE pro_recovery_lab.source_entries INCLUDING ALL
);

ALTER TABLE pro_recovery_lab.restored_entries
ADD CONSTRAINT restored_entries_account_fk
FOREIGN KEY (account_id)
REFERENCES pro_recovery_lab.restored_accounts (account_id);

INSERT INTO pro_recovery_lab.restored_accounts
SELECT a.*
FROM pro_recovery_lab.source_accounts AS a
ORDER BY a.account_id;

INSERT INTO pro_recovery_lab.restored_entries
SELECT e.*
FROM pro_recovery_lab.source_entries AS e
ORDER BY e.entry_id;

CREATE TABLE pro_recovery_lab.restore_results (
    check_name text PRIMARY KEY,
    expected_value text NOT NULL,
    observed_value text NOT NULL,
    passed boolean NOT NULL
);

WITH observed AS (
    SELECT
        COUNT(*)::integer AS row_count,
        md5(
            string_agg(
                concat_ws('|', a.account_id, a.account_key, a.display_name),
                E'\n'
                ORDER BY a.account_id
            )
        ) AS checksum
    FROM pro_recovery_lab.restored_accounts AS a
)
INSERT INTO pro_recovery_lab.restore_results
SELECT
    'accounts rows',
    bm.account_rows::text,
    observed.row_count::text,
    bm.account_rows = observed.row_count
FROM pro_recovery_lab.backup_manifest AS bm
CROSS JOIN observed
UNION ALL
SELECT
    'accounts checksum',
    bm.accounts_checksum,
    observed.checksum,
    bm.accounts_checksum = observed.checksum
FROM pro_recovery_lab.backup_manifest AS bm
CROSS JOIN observed;

WITH observed AS (
    SELECT
        COUNT(*)::integer AS row_count,
        md5(
            string_agg(
                concat_ws(
                    '|',
                    e.entry_id,
                    e.account_id,
                    e.amount,
                    e.occurred_at AT TIME ZONE 'UTC',
                    e.note
                ),
                E'\n'
                ORDER BY e.entry_id
            )
        ) AS checksum
    FROM pro_recovery_lab.restored_entries AS e
)
INSERT INTO pro_recovery_lab.restore_results
SELECT
    'entries rows',
    bm.entry_rows::text,
    observed.row_count::text,
    bm.entry_rows = observed.row_count
FROM pro_recovery_lab.backup_manifest AS bm
CROSS JOIN observed
UNION ALL
SELECT
    'entries checksum',
    bm.entries_checksum,
    observed.checksum,
    bm.entries_checksum = observed.checksum
FROM pro_recovery_lab.backup_manifest AS bm
CROSS JOIN observed;

\echo 'Restore evidence: data checks plus structural constraints'
SELECT
    rr.check_name,
    rr.expected_value,
    rr.observed_value,
    rr.passed
FROM pro_recovery_lab.restore_results AS rr
ORDER BY rr.check_name;

SELECT
    rel.relname AS table_name,
    con.contype AS constraint_type,
    pg_catalog.pg_get_constraintdef(con.oid) AS definition
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS rel
  ON rel.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = rel.relnamespace
WHERE n.nspname = 'pro_recovery_lab'
  AND rel.relname IN ('restored_accounts', 'restored_entries')
ORDER BY rel.relname, con.contype, definition;

CREATE TABLE pro_recovery_lab.recovery_objectives (
    service_name text PRIMARY KEY,
    maximum_data_loss interval NOT NULL,
    target_restore_time interval NOT NULL,
    strategy text NOT NULL
);

INSERT INTO pro_recovery_lab.recovery_objectives
VALUES
    ('course analytics', INTERVAL '24 hours', INTERVAL '4 hours', 'nightly logical dump'),
    ('transaction service', INTERVAL '5 minutes', INTERVAL '30 minutes', 'base backup plus archived WAL');

CREATE TABLE pro_recovery_lab.recovery_timeline (
    timeline_event_id integer PRIMARY KEY,
    event_at timestamptz NOT NULL,
    event_name text NOT NULL,
    recover_through boolean NOT NULL
);

INSERT INTO pro_recovery_lab.recovery_timeline
VALUES
    (1, TIMESTAMPTZ '2026-03-04 12:00:00+00', 'base backup completed', true),
    (2, TIMESTAMPTZ '2026-03-04 12:20:00+00', 'last confirmed good transaction', true),
    (3, TIMESTAMPTZ '2026-03-04 12:30:00+00', 'accidental destructive change', false),
    (4, TIMESTAMPTZ '2026-03-04 12:40:00+00', 'problem detected', false);

SELECT
    ro.service_name,
    ro.maximum_data_loss AS rpo,
    ro.target_restore_time AS rto,
    ro.strategy
FROM pro_recovery_lab.recovery_objectives AS ro
ORDER BY ro.service_name;

SELECT
    max(rt.event_at) FILTER (WHERE rt.recover_through) AS last_good_target,
    min(rt.event_at) FILTER (WHERE NOT rt.recover_through) AS first_bad_event
FROM pro_recovery_lab.recovery_timeline AS rt;

\echo 'Read-only server recovery posture; no setting values are changed'
SELECT
    current_database() AS database_name,
    current_setting('server_version') AS server_version,
    current_setting('wal_level') AS wal_level,
    current_setting('archive_mode') AS archive_mode,
    pg_catalog.pg_is_in_recovery() AS is_in_recovery,
    CASE
        WHEN pg_catalog.pg_is_in_recovery()
        THEN pg_catalog.pg_last_wal_replay_lsn()
        ELSE NULL
    END AS replay_lsn,
    CASE
        WHEN NOT pg_catalog.pg_is_in_recovery()
        THEN pg_catalog.pg_current_wal_lsn()
        ELSE NULL
    END AS current_wal_lsn;

-- Exercises:
--
-- 1. Add a schema fingerprint based on expected columns, types, nullability,
--    constraints, and indexes. Explain why a data checksum alone is incomplete.
--    Inputs: Canonicalize `pro_recovery_lab.restored_accounts` and
--    `restored_entries` metadata from `information_schema.columns` and
--    PostgreSQL catalogs. Include type/schema/domain, length or precision,
--    nullability, default, identity/generated state, collation, constraints,
--    and indexes; exclude OIDs and generated names.
--    Expected result/shape: First return ordered canonical rows with columns
--    `object_kind`, `relation_name`, `item_order`, `item_name`, and
--    `semantic_definition`. Then return exactly one row with
--    `restored_schema_fingerprint`.
--    Verify: Compare canonical rows before hashes. Changing a default, dropping
--    a constraint, or adding an index must change a visible semantic row and
--    the fingerprint, while a volatile OID change must not.
--    Hint ladder, rung 1: An opaque digest is useful only after its stable,
--    diagnosable input rows are defined.
-- 2. Inside a savepoint, corrupt one restored row and prove the checksum test
--    fails; roll back to the savepoint and prove it passes again.
--    Inputs: Record the source and restored account/entry checksums, create a
--    savepoint, update one `pro_recovery_lab.restored_entries.amount`, compare
--    again, roll back to the savepoint, and compare a third time.
--    Expected result/shape: Three named observations: baseline checksums match;
--    the corrupted restored checksum differs; after savepoint rollback the
--    checksums match again. The intentional mismatch is reported and caught,
--    not allowed to abort the remaining demonstration.
--    Verify: Also compare row counts and a key-level detail query so a NULL or
--    colliding digest cannot be the sole proof. Corrupt a second key and prove
--    the detail query identifies exactly that key.
--    Hint ladder, rung 1: A savepoint lets you prove the negative control and
--    still restore the transaction to its known-good state.
-- 3. Write RPO/RTO requirements for a new service, then choose logical dumps,
--    physical base backup plus WAL, replication, or a combination. Separate
--    availability from backup.
--    Inputs: Fill `pro_recovery_lab.recovery_plan` from explicit business RPO
--    and RTO requirements. Choose backup and availability strategies
--    separately and state each strategy's limit.
--    Expected result/shape: One row per `service_name`, with `service_name`,
--    `rpo`, `rto`, `backup_strategy`, and `availability_strategy`, ordered by
--    `service_name`.
--    Verify: For every row, map RPO to recoverable data age and RTO to the full
--    restore-through-validation timeline. Remove replicas and prove a usable
--    backup path remains; remove backups and explain why replicas alone cannot
--    recover deleted/corrupted data.
--    Hint ladder, rung 1: Availability reduces interruption; backup preserves
--    a recoverable historical state. Neither substitutes automatically.
-- 4. Draft and peer-review exact pg_dump/pg_restore commands for an isolated
--    ds60_restore_rehearsal database. Verify rows, constraints, owners/grants,
--    sequences, functions, extensions, and application queries before cleanup.
--    Inputs: Draft literal `pg_dump`/`createdb`/`pg_restore` commands for a
--    separately created disposable database named `ds60_restore_rehearsal`.
--    Record artifact path/hash, tool/server versions, exact flags, start/end
--    time, exit status, and cleanup command. Do not run external commands from
--    this SQL transaction.
--    Expected result/shape: One reviewed row per phase—dump, create isolated
--    target, restore, catalogs, data, security, application smoke tests, and
--    cleanup—with `phase_number`, `command_or_check`, `required_evidence`,
--    `owner`, and `status`.
--    Verify: Execute only after peer review; reconcile rows, constraints,
--    owners/grants, identity/sequence state, functions, extensions, and critical
--    queries. A missing artifact or failed check blocks completion and cutover.
--    Hint ladder, rung 1: `ds60_restore_rehearsal` is a database target name,
--    not a relation to select from.
-- 5. Explain WAL archiving, base backups, timelines, recovery target time, and
--    retention. State why archived WAL without a usable base backup is not PITR.
--    Inputs: Build a PITR evidence chain that names one compatible base backup,
--    every required WAL segment, timeline history, recovery target, retention
--    horizon, restore configuration, and validation/cleanup owner.
--    Expected result/shape: One row per chain component, with `component`,
--    `artifact_identity`, `required_from`, `required_through`, `observed_status`,
--    and `failure_response`. This lesson records a plan; it does not configure
--    archiving or execute recovery.
--    Verify: Remove one required WAL segment and separately remove the usable
--    base backup; each negative control makes the target unrecoverable. Record
--    the actual recovered timeline/time and application checks in an isolated
--    rehearsal rather than accepting file presence alone.
--    Hint ladder, rung 1: WAL replays changes after a compatible starting
--    backup; an archive by itself is not a full database image.
-- 6. Explain why “backup command exited zero” is not recovery evidence.
--    Inputs: Classify evidence from the dump command, artifact manifest,
--    isolated restore, catalog/data reconciliation, recovery-point proof, and
--    application read/write smoke tests.
--    Expected result/shape: One row per evidence layer, with `evidence_layer`,
--    `what_it_proves`, `what_it_does_not_prove`, `failure_signal`, and `owner`.
--    An exit-zero dump is only the first layer.
--    Verify: Inject a syntactically valid but incomplete artifact or a restore
--    that lacks one critical object. Command exit evidence may pass, while the
--    later reconciliation must fail and prevent a “recoverable” decision.
--    Hint ladder, rung 1: Evidence should advance from “bytes were written” to
--    “a representative application can safely use the restored state.”
-- 7. Design encryption and custody for dump files, base backups, WAL archives,
--    manifests, and keys. Separate transport/storage encryption from database
--    checksums; include rotation, least privilege, restore access, and deletion.
--    Inputs: Complete `pro_recovery_lab.artifact_controls` for dump files, base
--    backups, WAL archives, manifests, and keys. Keep artifact encryption,
--    integrity/authenticity, key custody, and restore authorization separate.
--    Expected result/shape: One row per `artifact_kind`, with `artifact_kind`,
--    `encrypted`, `integrity_manifest`, `key_owner`, and `restore_role`, ordered
--    by `artifact_kind`.
--    Verify: Every artifact except the key record names encryption at rest and
--    every restorable artifact has integrity evidence plus a distinct
--    least-privileged restore role. Walk one key rotation and deletion event
--    without making old retained backups permanently unrestorable.
--    Hint ladder, rung 1: PostgreSQL page checksums detect some storage
--    corruption; they do not encrypt a dump or prove artifact provenance.
-- 8. Extend the restore checklist for sequences/identity state, large objects,
--    owners, memberships, default privileges, security labels, extensions, and
--    configuration outside the database. Classify what each backup format omits.
--    Inputs: Classify each inline restore component—identity/sequence state,
--    large objects, owners, memberships, default privileges, security labels,
--    extensions, and external configuration—by its authoritative source.
--    Expected result/shape: One row per `component`, with `component` and
--    `expected_source`, ordered by `component`.
--    Verify: For each chosen dump format, mark whether the component is inside
--    the artifact, requires separate global/config capture, or must be rebuilt.
--    A checklist is incomplete if any required component has no source and
--    validation query.
--    Hint ladder, rung 1: Database contents, cluster-global objects, and
--    host/service configuration have different backup boundaries.
-- 9. Plan a PostgreSQL major-version recovery rehearsal. Compare logical restore
--    with pg_upgrade, extension compatibility, collation changes, ANALYZE,
--    application-driver tests, rollback window, and cutover evidence.
--    Inputs: Query the current database and server for `server_version`,
--    `server_version_num`, `datcollate`, and `datctype`; separately draft the
--    logical-restore versus `pg_upgrade` rehearsal decision.
--    Expected result/shape: Exactly one local capability row with those four
--    columns. The reviewed plan also records source/target versions, extension
--    and collation compatibility, ANALYZE, driver/application tests, rollback
--    window, cutover evidence, and cleanup.
--    Verify: Capture the same capability row in the isolated target and compare
--    it with the planned target. A missing extension version, collation drift,
--    or failed application test blocks cutover even if `pg_upgrade --check` or
--    restore exits zero.
--    Hint ladder, rung 1: `pg_upgrade` is an external program, not a catalog
--    relation in this query.
-- 10. Design a selective table/schema restore without violating dependencies.
--     Inventory foreign keys, types, functions, sequences, privileges, and
--     downstream consumers; explain when full isolated restore is safer.
--    Inputs: Inspect `pg_constraint`, `pg_class`, and `pg_namespace` for
--    relations in `pro_recovery_lab`, then extend the dependency inventory to
--    types, functions, sequences, privileges, and downstream consumers.
--    Expected result/shape: One row per `(relation_name, constraint_type,
--    dependency_contract)`, with those three columns ordered by
--    `relation_name, constraint_type, dependency_contract`.
--    Verify: For every selected table, prove its referenced and referencing
--    objects are either restored or deliberately remapped. Remove one required
--    parent/table/type in an isolated target and prove validation stops; choose
--    full isolated restore when the closure cannot be established safely.
--    Hint ladder, rung 1: Constraint type alone is not an identity; retain the
--    relation and rendered dependency definition.
-- 11. Create a restore-capacity test: artifact size, transfer throughput, CPU,
--     I/O, parallel jobs, WAL volume, index build, validation, and safety margin.
--     Explain why a small-fixture linear extrapolation can miss bottlenecks.
--    Inputs: Fill `pro_recovery_lab.capacity_budget` with measured restore
--    phases, including artifact transfer, data load, index build, WAL catch-up,
--    validation, and application readiness.
--    Expected result/shape: One row per `phase`, with `phase`,
--    `measured_seconds`, `peak_bytes`, and `evidence_note`, ordered by `phase`.
--    Verify: Sum the measured critical path plus a named safety margin and
--    compare it with RTO; separately record CPU, I/O, parallel jobs, transfer
--    throughput, and free-space headroom. Repeat at a representative scale
--    because small-fixture linear extrapolation is not sufficient evidence.
--    Hint ladder, rung 1: RTO ends after validation and application readiness,
--    not when the last table finishes loading.
-- 12. Write a recovery-game-day record with incident commander, operators,
--     observers, decision log, timestamps, injected failures, achieved RPO/RTO,
--     unresolved gaps, cleanup, follow-up owners, and the next rehearsal date.

DO $self_check$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pro_recovery_lab.restore_results AS rr
        WHERE NOT rr.passed
    ) THEN
        RAISE EXCEPTION 'restore verification has failed checks';
    END IF;

    IF (
        SELECT COUNT(*)
        FROM pg_catalog.pg_constraint AS con
        JOIN pg_catalog.pg_class AS rel
          ON rel.oid = con.conrelid
        JOIN pg_catalog.pg_namespace AS n
          ON n.oid = rel.relnamespace
        WHERE n.nspname = 'pro_recovery_lab'
          AND rel.relname = 'restored_entries'
          AND con.contype = 'f'
    ) <> 1 THEN
        RAISE EXCEPTION 'restored foreign key is missing';
    END IF;
END
$self_check$;
--    Inputs: Use the inline role fixture as the minimum authority map, then add
--    named incident commander, operators, observers, and follow-up owners to a
--    timestamped game-day record.
--    Expected result/shape: One row per `role_name`, with `role_name` and
--    `responsibility`, ordered by `role_name`; the accompanying record includes
--    decision timestamps, injected failures, achieved RPO/RTO, gaps, cleanup,
--    owners, and next rehearsal date.
--    Verify: Every decision and action has exactly one accountable role, every
--    injected failure links to observed evidence, and all unresolved gaps have
--    an owner/due date. Compare achieved RPO/RTO with Exercise 3's requirements.
--    Hint ladder, rung 1: This is an authority and evidence-coverage check, not
--    a permission-granting exercise.

ROLLBACK;
\echo 'SQL-OPS-02 complete: pro_recovery_lab was rolled back'
