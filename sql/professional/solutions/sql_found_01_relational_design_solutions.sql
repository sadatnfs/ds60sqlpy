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

-- The worked baseline and the exercises use the same core identities. Keeping
-- them here makes the solution's catalog audit cover the same relationships a
-- learner sees before beginning the numbered work.
CREATE TABLE pro_relational_lab.members (
    member_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    display_name text NOT NULL CHECK (btrim(display_name) <> ''),
    email text NOT NULL UNIQUE
);

CREATE TABLE pro_relational_lab.equipment_categories (
    category_code text PRIMARY KEY,
    display_name text NOT NULL UNIQUE
);

CREATE TABLE pro_relational_lab.equipment_items (
    item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_tag text NOT NULL UNIQUE,
    category_code text NOT NULL
        REFERENCES pro_relational_lab.equipment_categories (category_code)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    description text NOT NULL CHECK (btrim(description) <> ''),
    current_daily_fee numeric(10, 2) NOT NULL CHECK (current_daily_fee >= 0)
);

INSERT INTO pro_relational_lab.equipment_categories (
    category_code,
    display_name
)
VALUES
    ('AUDIO', 'Audio equipment'),
    ('TOOL', 'Hand tools');

INSERT INTO pro_relational_lab.members (display_name, email)
VALUES ('Avery Chen', 'avery@example.test');

INSERT INTO pro_relational_lab.equipment_items (
    asset_tag,
    category_code,
    description,
    current_daily_fee
)
VALUES
    ('AUD-001', 'AUDIO', 'Portable recorder', 12.00),
    ('TOL-001', 'TOOL', 'Torque wrench', 8.00);

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
        (
            CASE
                WHEN completed_on IS NULL THEN NULL
                ELSE completed_on - opened_on
            END
        ) STORED,
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
WHERE i.asset_tag = 'AUD-001'
RETURNING visit_id, item_id, cost;

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
CREATE TABLE pro_relational_lab.loans (
    loan_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id bigint NOT NULL
        REFERENCES pro_relational_lab.equipment_items (item_id)
        ON DELETE RESTRICT,
    member_id bigint NOT NULL
        REFERENCES pro_relational_lab.members (member_id)
        ON DELETE RESTRICT,
    checked_out_on date NOT NULL,
    daily_fee_at_checkout numeric(10, 2) NOT NULL
        CHECK (daily_fee_at_checkout >= 0)
);

INSERT INTO pro_relational_lab.loans (
    item_id,
    member_id,
    checked_out_on,
    daily_fee_at_checkout
)
SELECT
    i.item_id,
    m.member_id,
    DATE '2026-03-15',
    i.current_daily_fee
FROM pro_relational_lab.equipment_items AS i
CROSS JOIN pro_relational_lab.members AS m
WHERE i.asset_tag = 'AUD-001';

UPDATE pro_relational_lab.equipment_items AS i
SET current_daily_fee = 15.00
WHERE i.asset_tag = 'AUD-001';

SELECT
    l.loan_id,
    i.asset_tag,
    i.current_daily_fee,
    l.daily_fee_at_checkout
FROM pro_relational_lab.loans AS l
JOIN pro_relational_lab.equipment_items AS i
  ON i.item_id = l.item_id
ORDER BY l.loan_id;

SELECT *
FROM (
    VALUES (
        'daily_fee_at_checkout'::text,
        'deliberate denormalization'::text,
        'one immutable quoted fee per loan'::text,
        'What fee did the borrower agree to at checkout?'::text
    )
) AS classification(
    attribute_name,
    classification,
    invariant,
    historical_question
);

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

-- One visit has one provider in this model, while one provider can serve many
-- visits. A PRIMARY KEY on visit_id enforces that one-provider-per-visit rule.
CREATE TABLE pro_relational_lab.visit_providers (
    visit_id bigint PRIMARY KEY
        REFERENCES pro_relational_lab.maintenance_visits (visit_id)
        ON DELETE CASCADE,
    provider_id bigint NOT NULL
        REFERENCES pro_relational_lab.providers (provider_id)
        ON DELETE RESTRICT
);

INSERT INTO pro_relational_lab.providers (provider_name)
SELECT DISTINCT mv.provider_name
FROM pro_relational_lab.maintenance_visits AS mv
ORDER BY mv.provider_name;

INSERT INTO pro_relational_lab.technicians (technician_name)
VALUES ('Riley Chen'), ('Sam Rivera');

INSERT INTO pro_relational_lab.visit_providers (visit_id, provider_id)
SELECT mv.visit_id, p.provider_id
FROM pro_relational_lab.maintenance_visits AS mv
JOIN pro_relational_lab.providers AS p
  ON p.provider_name = mv.provider_name
;

-- The bridge is now the source of truth. Keeping a mutable provider_name on
-- the visit would permit it to disagree with provider_id.
ALTER TABLE pro_relational_lab.maintenance_visits
    DROP COLUMN provider_name;

INSERT INTO pro_relational_lab.visit_technicians (visit_id, technician_id)
SELECT mv.visit_id, t.technician_id
FROM pro_relational_lab.maintenance_visits AS mv
CROSS JOIN pro_relational_lab.technicians AS t
WHERE mv.external_reference = 'VISIT-100';

SELECT *
FROM (
    VALUES
        ('providers'::text, 'one row per provider'::text, 'provider_id'::text),
        ('technicians', 'one row per technician', 'technician_id'),
        ('visit_providers', 'one provider assignment per visit', 'visit_id'),
        (
            'visit_technicians',
            'one technician assignment per visit',
            'visit_id + technician_id'
        )
) AS grain_map(relation_name, row_grain, key_columns)
ORDER BY relation_name;

SELECT
    mv.visit_id,
    p.provider_name,
    t.technician_id,
    t.technician_name
FROM pro_relational_lab.maintenance_visits AS mv
JOIN pro_relational_lab.visit_providers AS vp
  ON vp.visit_id = mv.visit_id
JOIN pro_relational_lab.providers AS p
  ON p.provider_id = vp.provider_id
JOIN pro_relational_lab.visit_technicians AS vt
  ON vt.visit_id = mv.visit_id
JOIN pro_relational_lab.technicians AS t
  ON t.technician_id = vt.technician_id
WHERE mv.external_reference = 'VISIT-100'
ORDER BY mv.visit_id, t.technician_id;

-- Exercise 6: count a nullable-side key, not COUNT(*), so never-loaned items
-- correctly report zero. A loan-side date predicate would belong in ON.
SELECT
    i.item_id,
    i.asset_tag,
    COUNT(l.loan_id) AS loan_count,
    MAX(l.checked_out_on) AS latest_checkout
FROM pro_relational_lab.equipment_items AS i
LEFT JOIN pro_relational_lab.loans AS l
  ON l.item_id = i.item_id
GROUP BY i.item_id, i.asset_tag
ORDER BY i.asset_tag, i.item_id;

-- Exercise 7: compare the intended referential action with the action actually
-- stored in pg_constraint. RESTRICT preserves historical facts; CASCADE is
-- limited to assignment rows that have no meaning without their parent visit.
WITH expected(child_table, parent_table, expected_action, rationale) AS (
    VALUES
        ('equipment_items'::text, 'equipment_categories'::text, 'RESTRICT'::text,
         'a catalog item must retain its category identity'::text),
        ('loans'::text, 'equipment_items'::text, 'RESTRICT'::text,
         'a checkout must retain its physical-item identity'::text),
        ('loans', 'members', 'RESTRICT',
         'a checkout must retain its borrower identity'),
        ('maintenance_visits', 'equipment_items', 'RESTRICT',
         'a maintenance fact must retain its physical-item identity'),
        ('visit_providers', 'maintenance_visits', 'CASCADE',
         'a provider assignment has no meaning without its visit'),
        ('visit_providers', 'providers', 'RESTRICT',
         'a referenced provider must be retired rather than erased'),
        ('visit_technicians', 'maintenance_visits', 'CASCADE',
         'a technician assignment has no meaning without its visit'),
        ('visit_technicians', 'technicians', 'RESTRICT',
         'a referenced technician must be retired rather than erased')
),
actual AS (
    SELECT
        child.relname::text AS child_table,
        parent.relname::text AS parent_table,
        CASE con.confdeltype
            WHEN 'a' THEN 'NO ACTION'
            WHEN 'r' THEN 'RESTRICT'
            WHEN 'c' THEN 'CASCADE'
            WHEN 'n' THEN 'SET NULL'
            WHEN 'd' THEN 'SET DEFAULT'
        END AS actual_action
    FROM pg_catalog.pg_constraint AS con
    JOIN pg_catalog.pg_class AS child
      ON child.oid = con.conrelid
    JOIN pg_catalog.pg_class AS parent
      ON parent.oid = con.confrelid
    JOIN pg_catalog.pg_namespace AS n
      ON n.oid = child.relnamespace
    WHERE n.nspname = 'pro_relational_lab'
      AND con.contype = 'f'
)
SELECT
    e.child_table || ' -> ' || e.parent_table AS relationship,
    e.expected_action,
    a.actual_action,
    CASE
        WHEN a.child_table IS NULL THEN 'missing'
        WHEN e.expected_action IS DISTINCT FROM a.actual_action THEN 'changed'
        ELSE 'matches'
    END AS drift_status,
    e.rationale
FROM expected AS e
LEFT JOIN actual AS a
  ON a.child_table = e.child_table
 AND a.parent_table = e.parent_table
ORDER BY e.child_table, e.parent_table;

-- Exercise 8: inspect semantic catalog properties instead of generated names.
SELECT
    con.conname,
    con.contype,
    pg_catalog.pg_get_constraintdef(con.oid) AS constraint_definition
FROM pg_catalog.pg_constraint AS con
JOIN pg_catalog.pg_class AS rel
  ON rel.oid = con.conrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = rel.relnamespace
WHERE n.nspname = 'pro_relational_lab'
  AND rel.relname = 'maintenance_visits'
ORDER BY con.conname;

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

SELECT
    idx.indisunique,
    idx.indnullsnotdistinct,
    pg_catalog.pg_get_indexdef(idx.indexrelid) AS index_definition
FROM pg_catalog.pg_index AS idx
JOIN pg_catalog.pg_class AS rel
  ON rel.oid = idx.indrelid
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = rel.relnamespace
JOIN pg_catalog.pg_attribute AS a
  ON a.attrelid = rel.oid
 AND a.attname = 'external_reference'
WHERE n.nspname = 'pro_relational_lab'
  AND rel.relname = 'maintenance_visits'
  AND a.attnum = ANY (idx.indkey)
ORDER BY idx.indexrelid;

ROLLBACK;
