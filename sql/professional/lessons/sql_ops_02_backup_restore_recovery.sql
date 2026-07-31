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
--    Inputs: For sql-ops-02 Exercise 1, read from `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`. Compute `constraints` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-ops-02 Exercise 1, expected output: exactly one aggregate summary row. The final columns are `constraints`.
--    Verify: For sql-ops-02 Exercise 1, evaluate each of `row_count` in a separate control `SELECT` over `information_schema.columns`, `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; require one final row and compare every value. Add one source row with a new `constraints`; verify the result gains exactly one row carrying that `constraints` value.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 1, run `columns`, and `constraints` one at a time. Record each CTE's row count and `constraints` uniqueness before the next stage uses it.
-- 2. Inside a savepoint, corrupt one restored row and prove the checksum test
--    fails; roll back to the savepoint and prove it passes again.
--    Inputs: For sql-ops-02 Exercise 2, read the target keys from `pro_recovery_lab.restored_records` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-ops-02 Exercise 2, expected output: the command tag and an independently counted set of affected `affected_row_count` values. The final columns are `affected_row_count`, and `command_tag`.
--    Verify: For sql-ops-02 Exercise 2, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `pro_recovery_lab.restored_records` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 2, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `pro_recovery_lab.restored_records` again and prove rollback or idempotent retry.
-- 3. Write RPO/RTO requirements for a new service, then choose logical dumps,
--    physical base backup plus WAL, replication, or a combination. Separate
--    availability from backup.
--    Inputs: For sql-ops-02 Exercise 3, use `pro_recovery_lab.recovery_plan` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-ops-02 Exercise 3, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `service_name`, `rpo`, `rto`, `backup_strategy`, and `availability_strategy`. The final order is `rp.service_name`.
--    Verify: For sql-ops-02 Exercise 3, restore into an isolated target and reconcile `pro_recovery_lab.recovery_plan` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 3, restore into an isolated target and reconcile `pro_recovery_lab.recovery_plan` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
-- 4. Draft and peer-review exact pg_dump/pg_restore commands for an isolated
--    ds60_restore_rehearsal database. Verify rows, constraints, owners/grants,
--    sequences, functions, extensions, and application queries before cleanup.
--    Inputs: For sql-ops-02 Exercise 4, use `ds60_restore_rehearsal` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-ops-02 Exercise 4, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
--    Verify: For sql-ops-02 Exercise 4, restore into an isolated target and reconcile `ds60_restore_rehearsal` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 4, restore into an isolated target and reconcile `ds60_restore_rehearsal` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
-- 5. Explain WAL archiving, base backups, timelines, recovery target time, and
--    retention. State why archived WAL without a usable base backup is not PITR.
--    Inputs: For sql-ops-02 Exercise 5, use `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-ops-02 Exercise 5, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `artifact_name`, `restored_object`, `row_count`, and `reconciliation_status`.
--    Verify: For sql-ops-02 Exercise 5, restore into an isolated target and reconcile `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 5, restore into an isolated target and reconcile `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
-- 6. Explain why “backup command exited zero” is not recovery evidence.
--    Inputs: For sql-ops-02 Exercise 6, complete the evidence written analysis and support its claims with read-only evidence from `pro_recovery_lab.source_accounts`, `pro_recovery_lab.source_entries`, and `pro_recovery_lab.backup_manifest`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-ops-02 Exercise 6, expected output: a completed the evidence written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
--    Verify: For sql-ops-02 Exercise 6, check the evidence written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 6, check the evidence written analysis against `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit`.
-- 7. Design encryption and custody for dump files, base backups, WAL archives,
--    manifests, and keys. Separate transport/storage encryption from database
--    checksums; include rotation, least privilege, restore access, and deletion.
--    Inputs: For sql-ops-02 Exercise 7, read from `pro_recovery_lab.artifact_controls`. Build the answer toward `encryptioncustody_answer`; keep `encryptioncustody_answer` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-02 Exercise 7, expected output: one row per `encryptioncustody_answer`. The final columns are `encryptioncustody_answer`. The final order is `artifact_kind`.
--    Verify: For sql-ops-02 Exercise 7, reselect the returned keys directly from the source; require unique `encryptioncustody_answer` where the expected grain is one row per key and confirm the projected `encryptioncustody_answer` against `pro_recovery_lab.artifact_controls`. Add one source row with a new `encryptioncustody_answer`; verify the result gains exactly one row carrying that `encryptioncustody_answer` value.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 7, check `artifact_kind` before applying the row cap.
-- 8. Extend the restore checklist for sequences/identity state, large objects,
--    owners, memberships, default privileges, security labels, extensions, and
--    configuration outside the database. Classify what each backup format omits.
--    Inputs: For sql-ops-02 Exercise 8, read from the inline `VALUES` fixture. Build the answer toward `component`, and `expected_source`; keep `component` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-02 Exercise 8, expected output: one row per `component`. The final columns are `component`, and `expected_source`. The final order is `component`.
--    Verify: For sql-ops-02 Exercise 8, reselect the returned keys directly from the source; require unique `component` where the expected grain is one row per key and confirm the projected `component`, and `expected_source` against the inline `VALUES` fixture. Add one source row with a new `component`; verify the result gains exactly one row carrying that `component` value.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 8, check `component` before applying the row cap.
-- 9. Plan a PostgreSQL major-version recovery rehearsal. Compare logical restore
--    with pg_upgrade, extension compatibility, collation changes, ANALYZE,
--    application-driver tests, rollback window, and cutover evidence.
--    Inputs: For sql-ops-02 Exercise 9, use `pg_catalog.pg_database`, and `pg_upgrade` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-ops-02 Exercise 9, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `server_version`, `server_version_num`, `datcollate`, and `datctype`.
--    Verify: For sql-ops-02 Exercise 9, restore into an isolated target and reconcile `pg_catalog.pg_database`, and `pg_upgrade` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 9, restore into an isolated target and reconcile `pg_catalog.pg_database`, and `pg_upgrade` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result.
-- 10. Design a selective table/schema restore without violating dependencies.
--     Inventory foreign keys, types, functions, sequences, privileges, and
--     downstream consumers; explain when full isolated restore is safer.
--    Inputs: For sql-ops-02 Exercise 10, use `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-ops-02 Exercise 10, expected output: a restore manifest, object/count reconciliation, recovery-point evidence, smoke-test result, and cleanup record. The final columns are `contype`, and `dependency_contract`. The final order is `rel.relname, con.contype, dependency_contract`.
--    Verify: For sql-ops-02 Exercise 10, restore into an isolated target and reconcile `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 10, start with the first relation in `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `contype` so the exact fanout or loss is visible.
-- 11. Create a restore-capacity test: artifact size, transfer throughput, CPU,
--     I/O, parallel jobs, WAL volume, index build, validation, and safety margin.
--     Explain why a small-fixture linear extrapolation can miss bottlenecks.
--    Inputs: For sql-ops-02 Exercise 11, read from `pro_recovery_lab.capacity_budget`. Build the answer toward `capacity_answer`; keep `capacity_answer` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-02 Exercise 11, expected output: one row per `capacity_answer`. The final columns are `capacity_answer`. The final order is `phase`.
--    Verify: For sql-ops-02 Exercise 11, reselect the returned keys directly from the source; require unique `capacity_answer` where the expected grain is one row per key and confirm the projected `capacity_answer` against `pro_recovery_lab.capacity_budget`. Add one source row with a new `capacity_answer`; verify the result gains exactly one row carrying that `capacity_answer` value.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 11, check `phase` before applying the row cap.
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
--    Inputs: For sql-ops-02 Exercise 12, read from the inline `VALUES` fixture. Build the answer toward `role_name`, and `responsibility`; keep `role_name` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-ops-02 Exercise 12, expected output: one row per `role_name`. The final columns are `role_name`, and `responsibility`. The final order is `role_name`.
--    Verify: For sql-ops-02 Exercise 12, reselect the returned keys directly from the source; require unique `role_name` where the expected grain is one row per key and confirm the projected `role_name`, and `responsibility` against the inline `VALUES` fixture. Run the same operation as one allowed identity and one denied identity; record both outcomes without granting new access.
--    Hint ladder, rung 1: For sql-ops-02 Exercise 12, check `role_name` before applying the row cap.

ROLLBACK;
\echo 'SQL-OPS-02 complete: pro_recovery_lab was rolled back'
