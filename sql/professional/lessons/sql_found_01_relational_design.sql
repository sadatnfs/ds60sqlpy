-- SQL-FOUND-01: Relational design, DDL, and integrity constraints
-- BEGINNER WORKFLOW — sql-found-01: Relational Design, DDL, and Integrity Constraints
-- Guide: sql/professional/companion-guides/sql_found_01_relational_design.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-found-01/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pro_relational_lab.members, pro_relational_lab.equipment_categories, pro_relational_lab.equipment_items, pro_relational_lab.loans.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Target: PostgreSQL 16+
--
-- This learner file is safe to run with:
-- psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
--   -f sql/professional/lessons/sql_found_01_relational_design.sql
--
-- Every object is created inside a transaction and removed by ROLLBACK.

\echo 'SQL-FOUND-01: building a disposable equipment-lending model'

BEGIN;
SET LOCAL search_path TO pg_catalog, public;

CREATE SCHEMA pro_relational_lab;

-- Requirement: one row represents one person who can borrow equipment.
-- The row grain is "one member", and member_id is its surrogate key.
CREATE TABLE pro_relational_lab.members (
    member_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    display_name text NOT NULL
        CHECK (btrim(display_name) <> ''),
    email text NOT NULL UNIQUE,
    backup_contact text UNIQUE,
    joined_on date NOT NULL DEFAULT CURRENT_DATE
);

-- Requirement: one row represents one reusable category, not one physical item.
CREATE TABLE pro_relational_lab.equipment_categories (
    category_code text PRIMARY KEY,
    display_name text NOT NULL UNIQUE,
    standard_loan_days integer NOT NULL
        CHECK (standard_loan_days BETWEEN 1 AND 90)
);

-- Requirement: one row represents one physical item.
-- The foreign key encodes many items belonging to one category.
CREATE TABLE pro_relational_lab.equipment_items (
    item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_tag text NOT NULL UNIQUE,
    category_code text NOT NULL
        REFERENCES pro_relational_lab.equipment_categories (category_code)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    description text NOT NULL
        CHECK (btrim(description) <> ''),
    replacement_cost numeric(10, 2) NOT NULL
        CHECK (replacement_cost >= 0),
    daily_fee numeric(8, 2) NOT NULL DEFAULT 0
        CHECK (daily_fee >= 0),
    item_condition text NOT NULL DEFAULT 'ready'
        CHECK (item_condition IN ('ready', 'on_loan', 'maintenance', 'retired')),
    catalog_label text GENERATED ALWAYS AS
        (asset_tag || ' - ' || description) STORED
);

-- Requirement: one row represents one checkout of one item to one member.
-- A member can have many loans; an item can appear in many historical loans.
CREATE TABLE pro_relational_lab.loans (
    loan_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id bigint NOT NULL
        REFERENCES pro_relational_lab.equipment_items (item_id)
        ON DELETE RESTRICT,
    member_id bigint NOT NULL
        REFERENCES pro_relational_lab.members (member_id)
        ON DELETE RESTRICT,
    checked_out_on date NOT NULL DEFAULT CURRENT_DATE,
    due_on date NOT NULL,
    returned_on date,
    -- This deliberate snapshot preserves the fee quoted for this checkout even
    -- if the item's current fee changes later.
    daily_fee_at_checkout numeric(8, 2) NOT NULL
        CHECK (daily_fee_at_checkout >= 0),
    planned_days integer GENERATED ALWAYS AS
        (due_on - checked_out_on) STORED,
    notes text,
    CONSTRAINT loans_due_after_checkout_ck
        CHECK (due_on >= checked_out_on),
    CONSTRAINT loans_return_after_checkout_ck
        CHECK (returned_on IS NULL OR returned_on >= checked_out_on),
    CONSTRAINT loans_item_checkout_uk
        UNIQUE (item_id, checked_out_on)
);

INSERT INTO pro_relational_lab.equipment_categories
    (category_code, display_name, standard_loan_days)
VALUES
    ('AUDIO', 'Audio equipment', 7),
    ('TOOL', 'Hand tools', 14);

-- PostgreSQL's ordinary UNIQUE constraint permits multiple NULL values because
-- NULL means "unknown", and two unknowns are not considered equal.
INSERT INTO pro_relational_lab.members
    (display_name, email, backup_contact, joined_on)
VALUES
    ('Avery Chen', 'avery@example.test', NULL, DATE '2026-01-10'),
    ('Morgan Diaz', 'morgan@example.test', NULL, DATE '2026-01-12');

INSERT INTO pro_relational_lab.equipment_items
    (asset_tag, category_code, description, replacement_cost, daily_fee)
VALUES
    ('AUD-001', 'AUDIO', 'Portable recorder', 180.00, 3.50),
    ('TOL-001', 'TOOL', 'Torque wrench', 95.00, 2.00);

INSERT INTO pro_relational_lab.loans
    (item_id, member_id, checked_out_on, due_on, daily_fee_at_checkout, notes)
SELECT
    i.item_id,
    m.member_id,
    DATE '2026-02-01',
    DATE '2026-02-08',
    i.daily_fee,
    'Worked example'
FROM pro_relational_lab.equipment_items AS i
JOIN pro_relational_lab.members AS m
  ON m.email = 'avery@example.test'
WHERE i.asset_tag = 'AUD-001';

\echo 'A normalized join reconstructs a useful loan description'
SELECT
    l.loan_id,
    m.display_name AS borrower,
    i.catalog_label,
    c.display_name AS category,
    l.checked_out_on,
    l.due_on,
    l.planned_days,
    l.daily_fee_at_checkout
FROM pro_relational_lab.loans AS l
JOIN pro_relational_lab.members AS m
  ON m.member_id = l.member_id
JOIN pro_relational_lab.equipment_items AS i
  ON i.item_id = l.item_id
JOIN pro_relational_lab.equipment_categories AS c
  ON c.category_code = i.category_code
ORDER BY l.loan_id;

\echo 'Multiple NULL backup contacts are valid under ordinary UNIQUE semantics'
SELECT
    COUNT(*) FILTER (WHERE m.backup_contact IS NULL) AS null_backup_contacts,
    COUNT(DISTINCT m.backup_contact) AS distinct_nonnull_backup_contacts
FROM pro_relational_lab.members AS m;

\echo 'The loan fee snapshot does not change when the current catalog fee changes'
UPDATE pro_relational_lab.equipment_items AS i
SET daily_fee = 4.25
WHERE i.asset_tag = 'AUD-001';

SELECT
    i.daily_fee AS current_daily_fee,
    l.daily_fee_at_checkout AS quoted_daily_fee
FROM pro_relational_lab.loans AS l
JOIN pro_relational_lab.equipment_items AS i
  ON i.item_id = l.item_id
WHERE i.asset_tag = 'AUD-001'
ORDER BY l.loan_id;

-- These anonymous blocks catch an expected constraint exception. If an invalid
-- row unexpectedly succeeds, the explicit RAISE makes the lesson fail.
\echo 'Expected failure: duplicate email violates UNIQUE'
DO $lesson$
BEGIN
    BEGIN
        INSERT INTO pro_relational_lab.members (display_name, email)
        VALUES ('Duplicate Example', 'avery@example.test');
        RAISE EXCEPTION 'duplicate email unexpectedly succeeded';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Expected UNIQUE failure: %', SQLERRM;
    END;
END
$lesson$;

\echo 'Expected failure: due date before checkout violates CHECK'
DO $lesson$
BEGIN
    BEGIN
        INSERT INTO pro_relational_lab.loans (
            item_id,
            member_id,
            checked_out_on,
            due_on,
            daily_fee_at_checkout
        )
        SELECT
            i.item_id,
            m.member_id,
            DATE '2026-03-10',
            DATE '2026-03-09',
            2.00
        FROM pro_relational_lab.equipment_items AS i
        CROSS JOIN pro_relational_lab.members AS m
        WHERE i.asset_tag = 'TOL-001'
          AND m.email = 'morgan@example.test';
        RAISE EXCEPTION 'invalid date range unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected CHECK failure: %', SQLERRM;
    END;
END
$lesson$;

\echo 'Expected failure: nonexistent member violates the foreign key'
DO $lesson$
BEGIN
    BEGIN
        INSERT INTO pro_relational_lab.loans (
            item_id,
            member_id,
            checked_out_on,
            due_on,
            daily_fee_at_checkout
        )
        SELECT
            i.item_id,
            999999,
            DATE '2026-03-10',
            DATE '2026-03-12',
            2.00
        FROM pro_relational_lab.equipment_items AS i
        WHERE i.asset_tag = 'TOL-001';
        RAISE EXCEPTION 'orphan loan unexpectedly succeeded';
    EXCEPTION
        WHEN foreign_key_violation THEN
            RAISE NOTICE 'Expected FOREIGN KEY failure: %', SQLERRM;
    END;
END
$lesson$;

-- Exercises (leave your answers below each prompt or in a scratch copy).
--
-- 1. Translate these requirements into a maintenance_visits table:
--    * one row per visit for one equipment item;
--    * an identity primary key and a foreign key to equipment_items;
--    * opened_on defaults to the current date;
--    * provider_name and service_note cannot be blank;
--    * cost cannot be negative;
--    * completed_on is NULL while open, otherwise it cannot precede opened_on;
--    * external_reference is unique when supplied, but may be NULL;
--    * service_days is a stored generated value.
--
--    Inputs: For sql-found-01 Exercise 1, change only `pro_relational_lab.equipment_items`, and `pro_relational_lab.maintenance_visits` inside the lesson rollback/cleanup boundary. Capture the DDL command tag and the relevant `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `information_schema.columns` rows.
--    Expected result/shape: For sql-found-01 Exercise 1, expected output: the requested DDL command tag plus catalog rows and one accepted and one rejected behavior. The final columns are `external_reference`, `service_days`, `completed_on`, `opened_on`, and `coalesce`.
--    Verify: For sql-found-01 Exercise 1, inspect `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `information_schema.columns` for `pro_relational_lab.equipment_items`, and `pro_relational_lab.maintenance_visits`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object. Run one value that satisfies the new rule and one value that must fail; record the catalog definition and SQLSTATE.
--    Hint ladder, rung 1: For sql-found-01 Exercise 1, inspect `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, and `information_schema.columns` for `pro_relational_lab.equipment_items`, and `pro_relational_lab.maintenance_visits`; run one accepted and one rejected operation, record the SQLSTATE, and confirm rollback/cleanup removes the course-owned object.
-- 2. Insert one valid visit, then safely prove that a negative cost is rejected.
--
--    Inputs: For sql-found-01 Exercise 2, read the target keys from `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-found-01 Exercise 2, expected output: the command tag and an independently counted set of affected `item_id` values. The final columns are `item_id`.
--    Verify: For sql-found-01 Exercise 2, materialize the intended `item_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `item_id` values in both cases.
--    Hint ladder, rung 1: For sql-found-01 Exercise 2, materialize the intended `item_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` again and prove rollback or idempotent retry.
-- 3. Insert two visits whose external_reference is NULL. Explain why an ordinary
--    UNIQUE constraint permits them. What PostgreSQL 15+ syntax would you choose
--    if NULL had to behave like a duplicate?
--
--    Inputs: For sql-found-01 Exercise 3, read the target keys from `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-found-01 Exercise 3, expected output: at most one row may have no external reference,” PostgreSQL 15+ supports: That is uncommon for external identifiers. The final columns are `item_id`, `opened_on`, `service_note`, and `NULL`. The final order is `mv.visit_id`.
--    Verify: For sql-found-01 Exercise 3, materialize the intended `item_id` target set first; require the command tag/`RETURNING` set to match it, then query `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `item_id` values in both cases.
--    Hint ladder, rung 1: For sql-found-01 Exercise 3, count the input rows from `pro_relational_lab.maintenance_visits`, and `pro_relational_lab.equipment_items`, then run each aggregate `FILTER` predicate as its own count before combining the values into the one-row summary.
-- 4. Classify daily_fee_at_checkout as normalized duplication, an accidental
--    inconsistency, or deliberate denormalization. State the invariant and the
--    historical question that justify your choice.
--
--    Inputs: For sql-found-01 Exercise 4, read from `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Build the answer toward `daily_fee_at_checkout`; keep `item_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-found-01 Exercise 4, expected output: one row per `item_id`. The final columns are `daily_fee_at_checkout`.
--    Verify: For sql-found-01 Exercise 4, reselect the returned keys directly from the source; require unique `item_id` where the expected grain is one row per key and confirm the projected `daily_fee_at_checkout` against `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.
--    Hint ladder, rung 1: For sql-found-01 Exercise 4, select `item_id` from `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items` before adding derived columns.
-- 5. A provider can perform many visits and a visit can involve several
--    technicians. Model providers, technicians, and visit assignments without
--    storing comma-separated names. State the grain and keys of every table.
--
--    Inputs: For sql-found-01 Exercise 5, read from `pro_relational_lab.maintenance_visits`, `pro_relational_lab.technicians`, `pro_relational_lab.providers`, and `pro_relational_lab.visit_technicians`. Compute `visit_id`, and `technician_id` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-found-01 Exercise 5, expected output: one row per provider, one row per technician, and one row per visit/technician assignment. The final columns are `visit_id`, and `technician_id`.
--    Verify: For sql-found-01 Exercise 5, evaluate each of `technician_id` in a separate control `SELECT` over `pro_relational_lab.maintenance_visits`, `pro_relational_lab.technicians`, `pro_relational_lab.providers`, and `pro_relational_lab.visit_technicians` using `(mv.external_reference = 'VISIT-100')`; require one final row and compare every value. Add one row for which `(mv.external_reference = 'VISIT-100')` is true and one for which it is false; verify only the matching `visit_id` value is returned.
--    Hint ladder, rung 1: For sql-found-01 Exercise 5, start with the first relation in `pro_relational_lab.maintenance_visits`, `pro_relational_lab.technicians`, `pro_relational_lab.providers`, and `pro_relational_lab.visit_technicians`; after each join, record total rows and distinct `visit_id` so the exact fanout or loss is visible.
-- 6. Write a query that reports every equipment item, including items with no
--    loans, plus its loan count and latest checkout date. Explain why filtering
--    the loan table in WHERE can accidentally turn the LEFT JOIN into an inner
--    join, and make ties deterministic.
--
--    Inputs: For sql-found-01 Exercise 6, read from `pro_relational_lab.equipment_items`, and `pro_relational_lab.loans`. Build the answer toward `item_id`; keep `item_id`, and `asset_tag` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-found-01 Exercise 6, expected output: one row per `item_id`, and `asset_tag`. The final columns are `item_id`. The final order is `i.asset_tag`.
--    Verify: For sql-found-01 Exercise 6, independently aggregate `pro_relational_lab.equipment_items`, and `pro_relational_lab.loans` by `item_id`, and `asset_tag`; require one output row for every distinct `item_id`, and `asset_tag` tuple satisfying `(i.asset_tag = 'AUD-001')` and compare `row_count` tuple by tuple. Give two rows the same `i.asset_tag` value and different ``item_id`, and `asset_tag`` values; verify `i.asset_tag` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-found-01 Exercise 6, start with the first relation in `pro_relational_lab.equipment_items`, and `pro_relational_lab.loans`; after each join, record total rows and distinct `item_id`, and `asset_tag` so the exact fanout or loss is visible.
-- 7. Choose ON DELETE behavior for category -> equipment, equipment -> loans,
--    and equipment -> maintenance_visits. Defend each RESTRICT, CASCADE, or
--    SET NULL decision in terms of historical truth rather than convenience.
--
--    Inputs: For sql-found-01 Exercise 7, read from `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Build the answer toward `maintenance_visits`; keep `item_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-found-01 Exercise 7, expected output: one row per `item_id`. The final columns are `maintenance_visits`.
--    Verify: For sql-found-01 Exercise 7, reselect the returned keys directly from the source; require unique `item_id` where the expected grain is one row per key and confirm the projected `maintenance_visits` against `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items`. Add one source row with a new `item_id`; verify the result gains exactly one row carrying that `item_id` value.
--    Hint ladder, rung 1: For sql-found-01 Exercise 7, select `item_id` from `pro_relational_lab.equipment_categories`, `CASCADE`, and `pro_relational_lab.equipment_items` before adding derived columns.
-- 8. Write catalog queries that prove the maintenance_visits primary key,
--    foreign key, checks, generated column, and NULL-aware uniqueness contract.
--    Do not depend on PostgreSQL-generated constraint names.
--    Inputs: For sql-found-01 Exercise 8, read from `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, and `pg_catalog.pg_attrdef`. Build the answer toward `contype`, and `constraint_definition`; keep `contype` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-found-01 Exercise 8, expected output: one row per `contype`. The final columns are `contype`, and `constraint_definition`. The final order is `a.attnum`.
--    Verify: For sql-found-01 Exercise 8, project `contype` plus the raw source columns from `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, and `pg_catalog.pg_attrdef` at each join stage; record row count and distinct `contype`, then assert the final `contype`, and `constraint_definition` values match those staged rows without unintended fanout or loss. Give two rows the same `a.attnum` value and different ``contype`` values; verify `a.attnum` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-found-01 Exercise 8, start with the first relation in `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, and `pg_catalog.pg_attrdef`; after each join, record total rows and distinct `contype` so the exact fanout or loss is visible.

\echo 'Self-check: the worked model has the expected deterministic row counts'
DO $lesson$
DECLARE
    member_count integer;
    item_count integer;
    loan_count integer;
BEGIN
    SELECT COUNT(*) INTO member_count
    FROM pro_relational_lab.members;
    SELECT COUNT(*) INTO item_count
    FROM pro_relational_lab.equipment_items;
    SELECT COUNT(*) INTO loan_count
    FROM pro_relational_lab.loans;

    IF member_count <> 2 OR item_count <> 2 OR loan_count <> 1 THEN
        RAISE EXCEPTION
            'unexpected counts: members %, items %, loans %',
            member_count,
            item_count,
            loan_count;
    END IF;
END
$lesson$;

ROLLBACK;
\echo 'SQL-FOUND-01 complete: pro_relational_lab was rolled back'
