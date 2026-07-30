-- SQL-OPS-02 executable solutions
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

ROLLBACK;

