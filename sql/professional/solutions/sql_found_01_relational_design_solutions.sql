-- SQL-FOUND-01 executable solutions
-- SOLUTION READING MAP — sql-found-01: Relational Design, DDL, and Integrity Constraints
-- Explanation: sql/professional/solutions/sql_found_01_relational_design_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_found_01_relational_design_solutions.sql
-- Read each answer from inputs to output: establish FROM/JOIN grain; apply
-- row filters; group/aggregate; filter groups; compute windows; project named
-- keys/measures; then order with a deterministic tie-breaker. Treat every CTE
-- as an intermediate relation whose keys, row count, and totals can be checked.
-- A command tag is not enough for DDL/DML: inspect catalogs or before/after
-- rows, test a boundary case, and reconcile with an independent control.
-- NULL, zero, empty input, missing rows, and ties need explicit policies.
-- The documented transaction/cleanup boundary must leave no unintended persistent object.
--
-- Creates and removes only pro_relational_lab.

BEGIN;
SET LOCAL search_path TO pg_catalog, public;

CREATE SCHEMA pro_relational_lab;

CREATE TABLE pro_relational_lab.equipment_items (
    item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_tag text NOT NULL UNIQUE,
    description text NOT NULL CHECK (btrim(description) <> '')
);

INSERT INTO pro_relational_lab.equipment_items (asset_tag, description)
VALUES
    ('AUD-001', 'Portable recorder'),
    ('TOL-001', 'Torque wrench');

-- Exercise 1: one row is one maintenance visit for one physical item.
CREATE TABLE pro_relational_lab.maintenance_visits (
    visit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id bigint NOT NULL
        REFERENCES pro_relational_lab.equipment_items (item_id)
        ON DELETE RESTRICT,
    opened_on date NOT NULL DEFAULT CURRENT_DATE,
    completed_on date,
    provider_name text NOT NULL
        CHECK (btrim(provider_name) <> ''),
    service_note text NOT NULL
        CHECK (btrim(service_note) <> ''),
    cost numeric(10, 2) NOT NULL DEFAULT 0
        CHECK (cost >= 0),
    external_reference text UNIQUE,
    service_days integer GENERATED ALWAYS AS
        (COALESCE(completed_on, opened_on) - opened_on) STORED,
    CONSTRAINT maintenance_completion_order_ck
        CHECK (completed_on IS NULL OR completed_on >= opened_on)
);

-- Exercise 2: one valid visit.
INSERT INTO pro_relational_lab.maintenance_visits (
    item_id,
    opened_on,
    completed_on,
    provider_name,
    service_note,
    cost,
    external_reference
)
SELECT
    i.item_id,
    DATE '2026-04-01',
    DATE '2026-04-03',
    'Community repair desk',
    'Calibration and safety check',
    28.50,
    'VISIT-100'
FROM pro_relational_lab.equipment_items AS i
WHERE i.asset_tag = 'AUD-001';

-- Exercise 2: safely prove that the database rejects a negative cost.
DO $solution$
BEGIN
    BEGIN
        INSERT INTO pro_relational_lab.maintenance_visits (
            item_id,
            opened_on,
            provider_name,
            service_note,
            cost
        )
        SELECT
            i.item_id,
            DATE '2026-04-04',
            'Community repair desk',
            'Impossible refund represented as service cost',
            -1.00
        FROM pro_relational_lab.equipment_items AS i
        WHERE i.asset_tag = 'AUD-001';
        RAISE EXCEPTION 'negative maintenance cost unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected negative-cost rejection: %', SQLERRM;
    END;
END
$solution$;

-- Exercise 3: two NULL external references are valid with ordinary UNIQUE.
INSERT INTO pro_relational_lab.maintenance_visits (
    item_id,
    opened_on,
    provider_name,
    service_note,
    cost,
    external_reference
)
SELECT
    i.item_id,
    dates.opened_on,
    'Internal maintenance',
    dates.service_note,
    0,
    NULL
FROM pro_relational_lab.equipment_items AS i
JOIN (
    VALUES
        ('AUD-001'::text, DATE '2026-05-01', 'Cleaned controls'::text),
        ('TOL-001'::text, DATE '2026-05-02', 'Checked calibration'::text)
) AS dates(asset_tag, opened_on, service_note)
  ON dates.asset_tag = i.asset_tag;

SELECT
    mv.visit_id,
    i.asset_tag,
    mv.opened_on,
    mv.completed_on,
    mv.service_days,
    mv.cost,
    mv.external_reference
FROM pro_relational_lab.maintenance_visits AS mv
JOIN pro_relational_lab.equipment_items AS i
  ON i.item_id = mv.item_id
ORDER BY mv.visit_id;

DO $solution$
DECLARE
    visit_count integer;
    null_reference_count integer;
BEGIN
    SELECT
        COUNT(*),
        COUNT(*) FILTER (WHERE mv.external_reference IS NULL)
    INTO visit_count, null_reference_count
    FROM pro_relational_lab.maintenance_visits AS mv;

    IF visit_count <> 3 OR null_reference_count <> 2 THEN
        RAISE EXCEPTION
            'unexpected visit counts: total %, NULL references %',
            visit_count,
            null_reference_count;
    END IF;
END
$solution$;

-- Exercise 4: daily_fee_at_checkout belongs on a loan because it is the quoted
-- historical value. A later equipment price change must not rewrite it.

-- Exercise 5: names become referenced entities; the bridge grain is one
-- technician assignment to one maintenance visit.
CREATE TABLE pro_relational_lab.providers (
    provider_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider_name text NOT NULL UNIQUE CHECK (btrim(provider_name) <> '')
);

CREATE TABLE pro_relational_lab.technicians (
    technician_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    technician_name text NOT NULL CHECK (btrim(technician_name) <> '')
);

CREATE TABLE pro_relational_lab.visit_technicians (
    visit_id bigint NOT NULL
        REFERENCES pro_relational_lab.maintenance_visits (visit_id)
        ON DELETE CASCADE,
    technician_id bigint NOT NULL
        REFERENCES pro_relational_lab.technicians (technician_id)
        ON DELETE RESTRICT,
    PRIMARY KEY (visit_id, technician_id)
);

INSERT INTO pro_relational_lab.providers (provider_name)
VALUES ('Community repair desk');

INSERT INTO pro_relational_lab.technicians (technician_name)
VALUES ('Riley Chen'), ('Sam Rivera');

INSERT INTO pro_relational_lab.visit_technicians (visit_id, technician_id)
SELECT mv.visit_id, t.technician_id
FROM pro_relational_lab.maintenance_visits AS mv
CROSS JOIN pro_relational_lab.technicians AS t
WHERE mv.external_reference = 'VISIT-100';

-- Exercise 6: count a nullable-side key, not COUNT(*), so never-loaned items
-- correctly report zero. A loan-side date predicate would belong in ON.
CREATE TABLE pro_relational_lab.loans (
    loan_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id bigint NOT NULL
        REFERENCES pro_relational_lab.equipment_items (item_id)
        ON DELETE RESTRICT,
    checked_out_on date NOT NULL
);

INSERT INTO pro_relational_lab.loans (item_id, checked_out_on)
SELECT i.item_id, DATE '2026-03-15'
FROM pro_relational_lab.equipment_items AS i
WHERE i.asset_tag = 'AUD-001';

SELECT
    i.item_id,
    i.asset_tag,
    COUNT(l.loan_id) AS loan_count,
    MAX(l.checked_out_on) AS latest_checkout
FROM pro_relational_lab.equipment_items AS i
LEFT JOIN pro_relational_lab.loans AS l
  ON l.item_id = i.item_id
GROUP BY i.item_id, i.asset_tag
ORDER BY i.asset_tag;

-- Exercise 7: RESTRICT preserves visits and loans as historical facts. CASCADE
-- is used only for the assignment bridge, which has no meaning without a visit.

-- Exercise 8: inspect semantic catalog properties instead of generated names.
SELECT
    con.contype,
    pg_catalog.pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS rel
  ON rel.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = rel.relnamespace
WHERE n.nspname = 'pro_relational_lab'
  AND rel.relname = 'maintenance_visits'
ORDER BY con.contype, constraint_definition;

SELECT
    a.attname AS column_name,
    a.attgenerated,
    pg_catalog.pg_get_expr(def.adbin, def.adrelid) AS generated_expression
FROM pg_catalog.pg_attribute AS a
JOIN pg_catalog.pg_class AS rel
  ON rel.oid = a.attrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = rel.relnamespace
LEFT JOIN pg_catalog.pg_attrdef AS def
  ON def.adrelid = a.attrelid
 AND def.adnum = a.attnum
WHERE n.nspname = 'pro_relational_lab'
  AND rel.relname = 'maintenance_visits'
  AND a.attnum > 0
  AND NOT a.attisdropped
ORDER BY a.attnum;

ROLLBACK;
