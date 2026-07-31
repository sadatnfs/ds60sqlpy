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
--    Inputs: For sql-ops-02 Exercise 1, canonicalize source and restored column, constraint, and index semantics from information schema and PostgreSQL catalogs, excluding volatile OIDs and generated object names before comparing or hashing.
--    Expected result/shape: For sql-ops-02 Exercise 1, expected output: ordered semantic rows with contract side, relation role, object kind, item order/name, and JSON definition, followed by one fingerprint row where source and restored hashes match and `mismatch_rows = 0`.
--    Verify: For sql-ops-02 Exercise 1, compare visible canonical rows before hashes, then alter a default, constraint, and index separately and require each change to produce diagnosable mismatch rows while an OID change remains outside the contract.
--    Hint ladder, rung 1: An opaque digest is useful only after its stable,
--    diagnosable input rows are defined.
-- 2. Inside a savepoint, corrupt one restored row and prove the checksum test
--    fails; roll back to the savepoint and prove it passes again.
--    Inputs: For sql-ops-02 Exercise 2, record source/restored checksums and counts, corrupt one restored amount after a savepoint, compare again, roll back to that savepoint, and run the comparison a third time.
--    Expected result/shape: For sql-ops-02 Exercise 2, expected output: baseline, corrupted, and after-savepoint-rollback observations; equality is true, false, then true, with row counts unchanged and the intentional mismatch explicitly observed.
--    Verify: For sql-ops-02 Exercise 2, supplement digests with row counts and key-level detail, corrupt a second chosen key to prove the detail query identifies it, and require the post-rollback comparison to return to the reviewed baseline.
--    Hint ladder, rung 1: A savepoint lets you prove the negative control and
--    still restore the transaction to its known-good state.
-- 3. Write RPO/RTO requirements for a new service, then choose logical dumps,
--    physical base backup plus WAL, replication, or a combination. Separate
--    availability from backup.
--    Inputs: For sql-ops-02 Exercise 3, enter explicit service RPO and RTO requirements in `pro_recovery_lab.recovery_plan`, then choose backup and availability strategies separately with their limits.
--    Expected result/shape: For sql-ops-02 Exercise 3, expected output: one row per service with `service_name`, `rpo`, `rto`, `backup_strategy`, and `availability_strategy`, ordered by service; the example targets five-minute RPO and thirty-minute RTO.
--    Verify: For sql-ops-02 Exercise 3, map RPO to recoverable data age and RTO to restore-through-application-readiness time, then remove replicas and backups in separate thought experiments to prove neither substitutes for the other.
--    Hint ladder, rung 1: Availability reduces interruption; backup preserves
--    a recoverable historical state. Neither substitutes automatically.
-- 4. Draft and peer-review exact pg_dump/pg_restore commands for an isolated
--    ds60_restore_rehearsal database. Verify rows, constraints, owners/grants,
--    sequences, functions, extensions, and application queries before cleanup.
--    Inputs: For sql-ops-02 Exercise 4, review literal dump/create/restore commands outside this transaction and use the SQL matrix to specify evidence for target isolation, catalogs, data, application behavior, and cleanup.
--    Expected result/shape: For sql-ops-02 Exercise 4, expected output: seven ordered rows with `phase_number`, `phase_name`, and `required_evidence`, covering dump, target creation, restore, catalogs/security, data, application checks, and cleanup; no external command runs here.
--    Verify: For sql-ops-02 Exercise 4, execute only in a separately created disposable database after peer review, reconcile rows and semantic objects including owners/grants and sequence state, and block completion on any failed phase.
--    Hint ladder, rung 1: `ds60_restore_rehearsal` is a database target name,
--    not a relation to select from.
-- 5. Explain WAL archiving, base backups, timelines, recovery target time, and
--    retention. State why archived WAL without a usable base backup is not PITR.
--    Inputs: For sql-ops-02 Exercise 5, model the PITR evidence chain from a compatible base backup through every required WAL segment, timeline history, target specification, retention overlap, and recovered-state validation.
--    Expected result/shape: For sql-ops-02 Exercise 5, expected output: six ordered rows with `component_number`, `component`, and `required_evidence`; the lesson records a recovery plan and does not configure archiving.
--    Verify: For sql-ops-02 Exercise 5, remove one required WAL segment and then the usable base backup as separate negative controls, and assert both scenario results mark the target unrecoverable before application validation.
--    Hint ladder, rung 1: WAL replays changes after a compatible starting
--    backup; an archive by itself is not a full database image.
-- 6. Explain why “backup command exited zero” is not recovery evidence.
--    Inputs: For sql-ops-02 Exercise 6, classify command exit, artifact manifest, isolated restore, catalog/data reconciliation, and application smoke tests as separate evidence layers.
--    Expected result/shape: For sql-ops-02 Exercise 6, expected output: five ordered rows with `layer_number`, `evidence_layer`, `what_it_proves`, and `what_it_does_not_prove`; exit zero proves only that the backup program reported success.
--    Verify: For sql-ops-02 Exercise 6, inject a valid-looking but incomplete artifact or omit one critical restored object, and prove early command evidence can pass while later reconciliation blocks a recoverable decision.
--    Hint ladder, rung 1: Evidence should advance from “bytes were written” to
--    “a representative application can safely use the restored state.”
-- 7. Design encryption and custody for dump files, base backups, WAL archives,
--    manifests, and keys. Separate transport/storage encryption from database
--    checksums; include rotation, least privilege, restore access, and deletion.
--    Inputs: For sql-ops-02 Exercise 7, populate `pro_recovery_lab.artifact_controls` for logical dumps, base backups, and WAL archives, separating encryption, integrity manifest, key owner, and restore role.
--    Expected result/shape: For sql-ops-02 Exercise 7, expected output: three ordered rows with `artifact_kind`, `encrypted`, `integrity_manifest`, `key_owner`, and `restore_role`; every restorable artifact is encrypted and has integrity evidence.
--    Verify: For sql-ops-02 Exercise 7, verify key custody is distinct from restore authorization, extend the review to manifest/key records, and rehearse rotation and deletion without making retained backups permanently unrestorable.
--    Hint ladder, rung 1: PostgreSQL page checksums detect some storage
--    corruption; they do not encrypt a dump or prove artifact provenance.
-- 8. Extend the restore checklist for sequences/identity state, large objects,
--    owners, memberships, default privileges, security labels, extensions, and
--    configuration outside the database. Classify what each backup format omits.
--    Inputs: For sql-ops-02 Exercise 8, classify restored data/schema, roles/memberships, sequences/identity, extensions, and external configuration by their authoritative source rather than assuming one artifact contains everything.
--    Expected result/shape: For sql-ops-02 Exercise 8, expected output: five ordered baseline rows with `component` and `expected_source`; the accompanying checklist extends coverage to large objects, default privileges, and security labels when required.
--    Verify: For sql-ops-02 Exercise 8, mark each required component as artifact-contained, separately captured, or rebuilt for the chosen backup format, and fail the checklist when any component lacks both a source and validation query.
--    Hint ladder, rung 1: Database contents, cluster-global objects, and
--    host/service configuration have different backup boundaries.
-- 9. Plan a PostgreSQL major-version recovery rehearsal. Compare logical restore
--    with pg_upgrade, extension compatibility, collation changes, ANALYZE,
--    application-driver tests, rollback window, and cutover evidence.
--    Inputs: For sql-ops-02 Exercise 9, query the current database for server version number plus database collation/ctype and separately review logical-restore versus binary-upgrade compatibility, extension, statistics, driver, and rollback evidence.
--    Expected result/shape: For sql-ops-02 Exercise 9, expected output: exactly one local capability row with `server_version`, `server_version_num`, `datcollate`, and `datctype`; the broader major-version plan remains explicitly review-only.
--    Verify: For sql-ops-02 Exercise 9, capture the same capability row in the isolated target and block cutover on extension incompatibility, collation drift, missing ANALYZE evidence, or failed driver/application tests even when upgrade tooling exits zero.
--    Hint ladder, rung 1: `pg_upgrade` is an external program, not a catalog
--    relation in this query.
-- 10. Design a selective table/schema restore without violating dependencies.
--     Inventory foreign keys, types, functions, sequences, privileges, and
--     downstream consumers; explain when full isolated restore is safer.
--    Inputs: For sql-ops-02 Exercise 10, inspect `pg_constraint`, `pg_class`, and `pg_namespace` for recovery-lab relations, then extend the selective-restore inventory to referenced types, functions, sequences, privileges, and downstream consumers.
--    Expected result/shape: For sql-ops-02 Exercise 10, expected output: one row per semantic constraint dependency with `relation_name`, `constraint_type`, and `dependency_contract`, ordered by all three fields.
--    Verify: For sql-ops-02 Exercise 10, prove every referenced and referencing object is restored or deliberately remapped, remove one required dependency in an isolated target, and choose a full isolated restore when closure cannot be established.
--    Hint ladder, rung 1: Constraint type alone is not an identity; retain the
--    relation and rendered dependency definition.
-- 11. Create a restore-capacity test: artifact size, transfer throughput, CPU,
--     I/O, parallel jobs, WAL volume, index build, validation, and safety margin.
--     Explain why a small-fixture linear extrapolation can miss bottlenecks.
--    Inputs: For sql-ops-02 Exercise 11, fill `pro_recovery_lab.capacity_budget` with measured transfer, restore, verification, and routing phases, recording duration, peak bytes, and evidence notes at representative scale.
--    Expected result/shape: For sql-ops-02 Exercise 11, expected output: four ordered rows with `phase`, `measured_seconds`, `peak_bytes`, and `evidence_note`; NULL measurements in the starter matrix are explicit work still to complete, not passing evidence.
--    Verify: For sql-ops-02 Exercise 11, sum the measured critical path plus named safety margin against RTO and separately record throughput, CPU, I/O, parallelism, WAL, and free-space headroom instead of linearly extrapolating a tiny fixture.
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
--    Inputs: For sql-ops-02 Exercise 12, use the inline authority map for incident commander, recovery operator, application owner, and observer, then attach those roles to a timestamped recovery game-day record.
--    Expected result/shape: For sql-ops-02 Exercise 12, expected output: four ordered rows with `role_name` and `responsibility`; the completed record also captures decisions, injected failures, achieved RPO/RTO, gaps, cleanup, owners, and next rehearsal date.
--    Verify: For sql-ops-02 Exercise 12, require exactly one accountable role for every action, link each injected failure to observed evidence, assign owner/due date to every gap, and compare achieved RPO/RTO with Exercise 3 requirements.
--    Hint ladder, rung 1: This is an authority and evidence-coverage check, not
--    a permission-granting exercise.

ROLLBACK;
\echo 'SQL-OPS-02 complete: pro_recovery_lab was rolled back'
