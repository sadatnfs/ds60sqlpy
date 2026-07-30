-- SQL-OPS-02: Backup, restore, and recovery rehearsals
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
-- 2. Inside a savepoint, corrupt one restored row and prove the checksum test
--    fails; roll back to the savepoint and prove it passes again.
-- 3. Write RPO/RTO requirements for a new service, then choose logical dumps,
--    physical base backup plus WAL, replication, or a combination. Separate
--    availability from backup.
-- 4. Draft and peer-review exact pg_dump/pg_restore commands for an isolated
--    ds60_restore_rehearsal database. Verify rows, constraints, owners/grants,
--    sequences, functions, extensions, and application queries before cleanup.
-- 5. Explain WAL archiving, base backups, timelines, recovery target time, and
--    retention. State why archived WAL without a usable base backup is not PITR.
-- 6. Explain why “backup command exited zero” is not recovery evidence.
-- 7. Design encryption and custody for dump files, base backups, WAL archives,
--    manifests, and keys. Separate transport/storage encryption from database
--    checksums; include rotation, least privilege, restore access, and deletion.
-- 8. Extend the restore checklist for sequences/identity state, large objects,
--    owners, memberships, default privileges, security labels, extensions, and
--    configuration outside the database. Classify what each backup format omits.
-- 9. Plan a PostgreSQL major-version recovery rehearsal. Compare logical restore
--    with pg_upgrade, extension compatibility, collation changes, ANALYZE,
--    application-driver tests, rollback window, and cutover evidence.
-- 10. Design a selective table/schema restore without violating dependencies.
--     Inventory foreign keys, types, functions, sequences, privileges, and
--     downstream consumers; explain when full isolated restore is safer.
-- 11. Create a restore-capacity test: artifact size, transfer throughput, CPU,
--     I/O, parallel jobs, WAL volume, index build, validation, and safety margin.
--     Explain why a small-fixture linear extrapolation can miss bottlenecks.
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

ROLLBACK;
\echo 'SQL-OPS-02 complete: pro_recovery_lab was rolled back'
