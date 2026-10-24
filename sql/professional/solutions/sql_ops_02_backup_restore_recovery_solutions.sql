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
            COALESCE(
                jsonb_agg(
                    jsonb_build_array(r.record_id, r.record_key, r.amount)
                    ORDER BY r.record_id
                )::text,
                '[]'
            )
        )
        INTO result
        FROM pro_recovery_lab.restored_records AS r;
    ELSE
        SELECT md5(
            COALESCE(
                jsonb_agg(
                    jsonb_build_array(r.record_id, r.record_key, r.amount)
                    ORDER BY r.record_id
                )::text,
                '[]'
            )
        )
        INTO result
        FROM pro_recovery_lab.source_records AS r;
    END IF;
    RETURN result;
END
$function$;

-- Exercise 1: compare normalized source and restore contracts. Generated
-- relation, constraint, and index names are implementation details, so the
-- contract records semantic properties instead of comparing raw DDL text.
CREATE VIEW pro_recovery_lab.schema_contract AS
WITH relations(contract_side, physical_name) AS (
    VALUES
        ('source'::text, 'source_records'::text),
        ('restored'::text, 'restored_records'::text)
)
SELECT
    r.contract_side,
    'records'::text AS relation_role,
    'column'::text AS object_kind,
    c.ordinal_position AS item_order,
    c.column_name::text AS item_name,
    jsonb_build_object(
        'data_type', c.data_type,
        'udt_schema', c.udt_schema,
        'udt_name', c.udt_name,
        'character_maximum_length', c.character_maximum_length,
        'numeric_precision', c.numeric_precision,
        'numeric_scale', c.numeric_scale,
        'datetime_precision', c.datetime_precision,
        'is_nullable', c.is_nullable,
        'column_default', c.column_default,
        'is_identity', c.is_identity,
        'identity_generation', c.identity_generation,
        'identity_start', c.identity_start,
        'identity_increment', c.identity_increment,
        'is_generated', c.is_generated,
        'generation_expression', c.generation_expression,
        'collation_schema', c.collation_schema,
        'collation_name', c.collation_name
    ) AS semantic_definition
FROM relations AS r
JOIN information_schema.columns AS c
  ON c.table_schema = 'pro_recovery_lab'
 AND c.table_name = r.physical_name

UNION ALL

SELECT
    r.contract_side,
    'records',
    'constraint',
    10000 + row_number() OVER (
        PARTITION BY r.contract_side
        ORDER BY con.contype, pg_catalog.pg_get_constraintdef(con.oid, true)
    )::integer,
    CASE con.contype
        WHEN 'p' THEN 'primary_key'
        WHEN 'u' THEN 'unique'
        WHEN 'f' THEN 'foreign_key'
        WHEN 'c' THEN 'check'
        ELSE con.contype::text
    END,
    jsonb_build_object(
        'constraint_type', con.contype,
        'definition', pg_catalog.pg_get_constraintdef(con.oid, true),
        'deferrable', con.condeferrable,
        'initially_deferred', con.condeferred,
        'validated', con.convalidated
    )
FROM relations AS r
JOIN pg_catalog.pg_namespace AS n
  ON n.nspname = 'pro_recovery_lab'
JOIN pg_catalog.pg_class AS rel
  ON rel.relnamespace = n.oid
 AND rel.relname = r.physical_name
JOIN pg_catalog.pg_constraint AS con
  ON con.conrelid = rel.oid

UNION ALL

SELECT
    r.contract_side,
    'records',
    'index',
    20000 + row_number() OVER (
        PARTITION BY r.contract_side
        ORDER BY
            idx.indisprimary DESC,
            idx.indisunique DESC,
            keys.key_items::text,
            included.include_items::text
    )::integer,
    CASE
        WHEN idx.indisprimary THEN 'primary_key_index'
        WHEN idx.indisunique THEN 'unique_index'
        ELSE 'index'
    END,
    jsonb_build_object(
        'access_method', am.amname,
        'unique', idx.indisunique,
        'primary', idx.indisprimary,
        'valid', idx.indisvalid,
        'ready', idx.indisready,
        'key_expressions', keys.key_items,
        'included_expressions', included.include_items,
        'predicate', pg_catalog.pg_get_expr(
            idx.indpred,
            idx.indrelid,
            true
        )
    )
FROM relations AS r
JOIN pg_catalog.pg_namespace AS n
  ON n.nspname = 'pro_recovery_lab'
JOIN pg_catalog.pg_class AS rel
  ON rel.relnamespace = n.oid
 AND rel.relname = r.physical_name
JOIN pg_catalog.pg_index AS idx
  ON idx.indrelid = rel.oid
JOIN pg_catalog.pg_class AS index_rel
  ON index_rel.oid = idx.indexrelid
JOIN pg_catalog.pg_am AS am
  ON am.oid = index_rel.relam
CROSS JOIN LATERAL (
    SELECT COALESCE(
        jsonb_agg(
            pg_catalog.pg_get_indexdef(idx.indexrelid, key_number, true)
            ORDER BY key_number
        ),
        '[]'::jsonb
    ) AS key_items
    FROM generate_series(1, idx.indnkeyatts) AS key_number
) AS keys
CROSS JOIN LATERAL (
    SELECT COALESCE(
        jsonb_agg(
            pg_catalog.pg_get_indexdef(
                idx.indexrelid,
                included_number,
                true
            )
            ORDER BY included_number
        ),
        '[]'::jsonb
    ) AS include_items
    FROM generate_series(idx.indnkeyatts + 1, idx.indnatts)
        AS included_number
) AS included;

CREATE VIEW pro_recovery_lab.schema_contract_mismatches AS
WITH source_contract AS (
    SELECT
        sc.relation_role,
        sc.object_kind,
        sc.item_order,
        sc.item_name,
        sc.semantic_definition
    FROM pro_recovery_lab.schema_contract AS sc
    WHERE sc.contract_side = 'source'
),
restored_contract AS (
    SELECT
        sc.relation_role,
        sc.object_kind,
        sc.item_order,
        sc.item_name,
        sc.semantic_definition
    FROM pro_recovery_lab.schema_contract AS sc
    WHERE sc.contract_side = 'restored'
)
SELECT 'source_only'::text AS mismatch_side, difference.*
FROM (
    SELECT * FROM source_contract
    EXCEPT
    SELECT * FROM restored_contract
) AS difference
UNION ALL
SELECT 'restored_only'::text AS mismatch_side, difference.*
FROM (
    SELECT * FROM restored_contract
    EXCEPT
    SELECT * FROM source_contract
) AS difference;

SELECT
    sc.contract_side,
    sc.relation_role,
    sc.object_kind,
    sc.item_order,
    sc.item_name,
    sc.semantic_definition
FROM pro_recovery_lab.schema_contract AS sc
ORDER BY
    sc.contract_side,
    sc.object_kind,
    sc.item_order,
    sc.item_name,
    sc.semantic_definition;

WITH fingerprints AS (
    SELECT
        sc.contract_side,
        md5(
            COALESCE(
                jsonb_agg(
                    jsonb_build_array(
                        sc.relation_role,
                        sc.object_kind,
                        sc.item_order,
                        sc.item_name,
                        sc.semantic_definition
                    )
                    ORDER BY
                        sc.object_kind,
                        sc.item_order,
                        sc.item_name,
                        sc.semantic_definition
                )::text,
                '[]'
            )
        ) AS schema_fingerprint
    FROM pro_recovery_lab.schema_contract AS sc
    GROUP BY sc.contract_side
)
SELECT
    max(f.schema_fingerprint) FILTER (
        WHERE f.contract_side = 'source'
    ) AS source_schema_fingerprint,
    max(f.schema_fingerprint) FILTER (
        WHERE f.contract_side = 'restored'
    ) AS restored_schema_fingerprint,
    max(f.schema_fingerprint) FILTER (
        WHERE f.contract_side = 'source'
    ) IS NOT DISTINCT FROM max(f.schema_fingerprint) FILTER (
        WHERE f.contract_side = 'restored'
    ) AS contracts_match,
    (SELECT COUNT(*) FROM pro_recovery_lab.schema_contract_mismatches)
        AS mismatch_rows
FROM fingerprints AS f;

DO $solution$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pro_recovery_lab.schema_contract_mismatches
    ) THEN
        RAISE EXCEPTION 'restored schema differs from the source contract';
    END IF;
END
$solution$;

-- Exercise 2: corruption must fail comparison, then savepoint rollback restores
-- the verified state.
SELECT
    'baseline'::text AS observation,
    pro_recovery_lab.records_checksum(false) AS source_checksum,
    pro_recovery_lab.records_checksum(true) AS restored_checksum,
    (SELECT COUNT(*) FROM pro_recovery_lab.source_records) AS source_rows,
    (SELECT COUNT(*) FROM pro_recovery_lab.restored_records) AS restored_rows,
    pro_recovery_lab.records_checksum(false)
        IS NOT DISTINCT FROM pro_recovery_lab.records_checksum(true)
        AS checksums_match;

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

SELECT
    'corrupted'::text AS observation,
    pro_recovery_lab.records_checksum(false) AS source_checksum,
    pro_recovery_lab.records_checksum(true) AS restored_checksum,
    (SELECT COUNT(*) FROM pro_recovery_lab.source_records) AS source_rows,
    (SELECT COUNT(*) FROM pro_recovery_lab.restored_records) AS restored_rows,
    pro_recovery_lab.records_checksum(false)
        IS NOT DISTINCT FROM pro_recovery_lab.records_checksum(true)
        AS checksums_match;

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

SELECT
    'after_savepoint_rollback'::text AS observation,
    pro_recovery_lab.records_checksum(false) AS source_checksum,
    pro_recovery_lab.records_checksum(true) AS restored_checksum,
    (SELECT COUNT(*) FROM pro_recovery_lab.source_records) AS source_rows,
    (SELECT COUNT(*) FROM pro_recovery_lab.restored_records) AS restored_rows,
    pro_recovery_lab.records_checksum(false)
        IS NOT DISTINCT FROM pro_recovery_lab.records_checksum(true)
        AS checksums_match;

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
SELECT *
FROM (
    VALUES
        (1, 'dump', 'artifact path/hash, pg_dump version, command and exit status'),
        (2, 'create target', 'isolated ds60_restore_rehearsal identity and access boundary'),
        (3, 'restore', 'pg_restore version, exact flags, transcript and duration'),
        (4, 'catalogs', 'columns, constraints, indexes, owners, grants, routines and extensions'),
        (5, 'data', 'row counts, length-safe checksums, key samples and sequence next-value tests'),
        (6, 'application', 'critical reads and rollback-safe writes with compatible clients'),
        (7, 'cleanup', 'target removal or named retention/custody record')
) AS logical_rehearsal(phase_number, phase_name, required_evidence)
ORDER BY phase_number;

-- Exercise 5: PITR requires a compatible base backup plus an unbroken WAL chain
-- through the target and timeline history. Archived WAL alone is insufficient.
SELECT *
FROM (
    VALUES
        (1, 'base backup', 'compatible image plus manifest/checksum'),
        (2, 'WAL chain', 'every segment from backup start through recovery target'),
        (3, 'timeline history', 'correct ancestry after any prior promotion'),
        (4, 'target', 'timestamp/LSN/name and inclusive/exclusive action'),
        (5, 'retention', 'base backup and WAL coexist for the promised window'),
        (6, 'recovery validation', 'observed stop point, catalogs, data and application tests')
) AS pitr_chain(component_number, component, required_evidence)
ORDER BY component_number;

-- Exercise 6: exit zero is only one evidence field; restore and application
-- verification must be recorded separately.
SELECT *
FROM (
    VALUES
        (1, 'command exit', 'the backup program reported success', 'artifact completeness or restorability'),
        (2, 'artifact manifest', 'expected files/parts and hashes exist', 'server can restore them'),
        (3, 'isolated restore', 'server accepted and materialized the artifact', 'semantic completeness'),
        (4, 'reconciliation', 'catalog/data invariants match expectations', 'application behavior'),
        (5, 'application smoke tests', 'critical compatible reads/writes work', 'future recoverability')
) AS evidence_layers(
    layer_number,
    evidence_layer,
    what_it_proves,
    what_it_does_not_prove
)
ORDER BY layer_number;

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
    rel.relname AS relation_name,
    con.contype AS constraint_type,
    pg_catalog.pg_get_constraintdef(con.oid) AS dependency_contract
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS rel
  ON rel.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = rel.relnamespace
WHERE n.nspname = 'pro_recovery_lab'
ORDER BY relation_name, constraint_type, dependency_contract;

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
