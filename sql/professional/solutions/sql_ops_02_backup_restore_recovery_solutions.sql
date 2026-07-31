-- SQL-OPS-02 executable solutions
-- SOLUTION READING MAP — sql-ops-02: Backup, Restore, and Recovery Rehearsals
-- Explanation: sql/professional/solutions/sql_ops_02_backup_restore_recovery_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_ops_02_backup_restore_recovery_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_recovery_lab;

CREATE TABLE pro_recovery_lab.source_records (
    record_id bigint PRIMARY KEY,
    record_key text NOT NULL UNIQUE,
    amount numeric(12, 2) NOT NULL
);

INSERT INTO pro_recovery_lab.source_records
VALUES (1, 'REC-100', 10.00), (2, 'REC-101', 20.00);

CREATE TABLE pro_recovery_lab.restored_records (
    LIKE pro_recovery_lab.source_records INCLUDING ALL
);

INSERT INTO pro_recovery_lab.restored_records
SELECT sr.*
FROM pro_recovery_lab.source_records AS sr
ORDER BY sr.record_id;

CREATE FUNCTION pro_recovery_lab.records_checksum(p_restored boolean)
RETURNS text
LANGUAGE plpgsql
STABLE
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
DECLARE
    result text;
BEGIN
    IF p_restored THEN
        SELECT md5(
            string_agg(
                concat_ws('|', r.record_id, r.record_key, r.amount),
                E'\n'
                ORDER BY r.record_id
            )
        )
        INTO result
        FROM pro_recovery_lab.restored_records AS r;
    ELSE
        SELECT md5(
            string_agg(
                concat_ws('|', r.record_id, r.record_key, r.amount),
                E'\n'
                ORDER BY r.record_id
            )
        )
        INTO result
        FROM pro_recovery_lab.source_records AS r;
    END IF;
    RETURN result;
END
$function$;

-- Exercise 1: structural fingerprint from stable catalog properties.
WITH columns AS (
    SELECT string_agg(
        concat_ws(
            '|',
            c.ordinal_position,
            c.column_name,
            c.data_type,
            c.is_nullable
        ),
        E'\n'
        ORDER BY c.ordinal_position
    ) AS column_contract
    FROM information_schema.columns AS c
    WHERE c.table_schema = 'pro_recovery_lab'
      AND c.table_name = 'restored_records'
),
constraints AS (
    SELECT string_agg(
        concat_ws('|', con.contype, pg_catalog.pg_get_constraintdef(con.oid)),
        E'\n'
        ORDER BY con.contype, pg_catalog.pg_get_constraintdef(con.oid)
    ) AS constraint_contract
    FROM pg_catalog.pg_constraint AS con
    JOIN pg_catalog.pg_class AS rel
      ON rel.oid = con.conrelid
    JOIN pg_catalog.pg_namespace AS n
      ON n.oid = rel.relnamespace
    WHERE n.nspname = 'pro_recovery_lab'
      AND rel.relname = 'restored_records'
)
SELECT md5(
    COALESCE(columns.column_contract, '')
    || E'\n--constraints--\n'
    || COALESCE(constraints.constraint_contract, '')
) AS restored_schema_fingerprint
FROM columns
CROSS JOIN constraints;

-- Exercise 2: corruption must fail comparison, then savepoint rollback restores
-- the verified state.
DO $solution$
BEGIN
    IF pro_recovery_lab.records_checksum(false)
       IS DISTINCT FROM pro_recovery_lab.records_checksum(true) THEN
        RAISE EXCEPTION 'initial restored checksum mismatch';
    END IF;
END
$solution$;

SAVEPOINT before_corruption;
UPDATE pro_recovery_lab.restored_records AS rr
SET amount = rr.amount + 1
WHERE rr.record_id = 2;

DO $solution$
BEGIN
    IF pro_recovery_lab.records_checksum(false)
       = pro_recovery_lab.records_checksum(true) THEN
        RAISE EXCEPTION 'corruption negative control was not detected';
    END IF;
    RAISE NOTICE 'Expected checksum mismatch detected';
END
$solution$;

ROLLBACK TO SAVEPOINT before_corruption;
RELEASE SAVEPOINT before_corruption;

DO $solution$
BEGIN
    IF pro_recovery_lab.records_checksum(false)
       IS DISTINCT FROM pro_recovery_lab.records_checksum(true) THEN
        RAISE EXCEPTION 'checksum did not recover after savepoint rollback';
    END IF;
END
$solution$;

-- Exercise 3: requirements precede strategy selection.
CREATE TABLE pro_recovery_lab.recovery_plan (
    service_name text PRIMARY KEY,
    rpo interval NOT NULL,
    rto interval NOT NULL,
    backup_strategy text NOT NULL,
    availability_strategy text NOT NULL
);

INSERT INTO pro_recovery_lab.recovery_plan
VALUES (
    'example transaction service',
    INTERVAL '5 minutes',
    INTERVAL '30 minutes',
    'daily verified base backup plus continuous WAL archive',
    'separate monitored replica with controlled failover'
);

SELECT
    rp.service_name,
    rp.rpo,
    rp.rto,
    rp.backup_strategy,
    rp.availability_strategy
FROM pro_recovery_lab.recovery_plan AS rp
ORDER BY rp.service_name;

-- Exercise 4: exact pg_dump/pg_restore commands remain in the guide because
-- this safe SQL script creates neither files nor databases. It verifies the
-- same schema/data behavior a restore rehearsal must prove.

-- Exercise 5: PITR requires a compatible base backup plus an unbroken WAL chain
-- through the target and timeline history. Archived WAL alone is insufficient.

-- Exercise 6: exit zero is only one evidence field; restore and application
-- verification must be recorded separately.

-- Exercise 7: keep backup artifacts and key custody as separate controls.
CREATE TABLE pro_recovery_lab.artifact_controls (
    artifact_kind text PRIMARY KEY,
    encrypted boolean NOT NULL,
    integrity_manifest boolean NOT NULL,
    key_owner text NOT NULL,
    restore_role text NOT NULL
);

INSERT INTO pro_recovery_lab.artifact_controls
VALUES
    ('logical_dump', true, true, 'security-recovery', 'database-recovery'),
    ('base_backup', true, true, 'security-recovery', 'database-recovery'),
    ('wal_archive', true, true, 'security-recovery', 'database-recovery');

SELECT *
FROM pro_recovery_lab.artifact_controls
ORDER BY artifact_kind;

-- Exercise 8: restoration scope includes semantic objects and external sources
-- of truth, not only table rows.
SELECT *
FROM (
    VALUES
        ('data/schema'::text, 'database dump or physical backup'::text),
        ('roles/memberships', 'cluster-global reviewed export'),
        ('sequences/identity', 'restored catalog plus next-value test'),
        ('extensions', 'DDL plus compatible installed binaries'),
        ('external configuration', 'separate configuration source')
) AS restore_scope(component, expected_source)
ORDER BY component;

-- Exercise 9: capture exact server/tool/extension/collation compatibility during
-- a major-version rehearsal. This local query is capability evidence only.
SELECT
    current_setting('server_version') AS server_version,
    current_setting('server_version_num') AS server_version_num,
    pg_catalog.pg_database.datcollate,
    pg_catalog.pg_database.datctype
FROM pg_catalog.pg_database
WHERE pg_catalog.pg_database.datname = current_database();

-- Exercise 10: catalog dependencies are an input to selective-restore review.
-- A full isolated restore is safer when dependency closure is uncertain.
SELECT
    con.contype,
    pg_catalog.pg_get_constraintdef(con.oid) AS dependency_contract
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS rel
  ON rel.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = rel.relnamespace
WHERE n.nspname = 'pro_recovery_lab'
ORDER BY rel.relname, con.contype, dependency_contract;

-- Exercise 11: total RTO ends after validation and application readiness.
CREATE TABLE pro_recovery_lab.capacity_budget (
    phase text PRIMARY KEY,
    measured_seconds numeric,
    peak_bytes bigint,
    evidence_note text NOT NULL
);

INSERT INTO pro_recovery_lab.capacity_budget
VALUES
    ('transfer', NULL, NULL, 'measure representative artifact and network'),
    ('restore', NULL, NULL, 'measure CPU, I/O, jobs, WAL, and index work'),
    ('verify', NULL, NULL, 'measure contracts and application smoke tests'),
    ('route', NULL, NULL, 'measure safe client cutover and readiness');

SELECT *
FROM pro_recovery_lab.capacity_budget
ORDER BY phase;

-- Exercise 12: a game-day record assigns authority and preserves evidence.
SELECT *
FROM (
    VALUES
        ('incident_commander'::text, 'owns decisions and stop authority'::text),
        ('recovery_operator', 'executes reviewed recovery runbook'),
        ('application_owner', 'verifies critical read/write behavior'),
        ('observer', 'records chronology, gaps, and follow-up owners')
) AS game_day(role_name, responsibility)
ORDER BY role_name;

ROLLBACK;
