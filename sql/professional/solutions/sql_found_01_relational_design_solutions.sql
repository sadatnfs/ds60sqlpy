-- SQL-FOUND-01 executable solutions
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

ROLLBACK;

