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
--    Inputs: Use `pro_relational_lab.maintenance_visits` plus only the small disposable fixture explicitly requested by Exercise 1; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 1 must make “Maintenance DDL: translate every visit requirement into a column, constraint, key, default, or generated expression; annotate the table grain” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `IDENTITY`, `ddl`, `pro_relational_lab.maintenance_visits`.
--    Verify: For Exercise 1, inspect the relevant `pg_catalog` or `information_schema` rows for `IDENTITY`, `ddl`, `pro_relational_lab.maintenance_visits`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: State the invariant and object grain first, implement the smallest DDL step, then design its catalog and negative-case proof.
-- 2. Insert one valid visit, then safely prove that a negative cost is rejected.
--
--    Inputs: Use `pro_relational_lab.maintenance_visits`, `pro_relational_lab.equipment_items` plus only the small disposable fixture explicitly requested by Exercise 2; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 2 needs a labeled transaction/session transcript that demonstrates “Negative cost: insert one valid visit, isolate the rejected insert in a nested block, and verify the expected SQLSTATE category”. Capture statement order, affected keys/counts, lock or snapshot state, and the expected SQLSTATE when an error is part of the exercise; finish with no open lesson transaction or leftover shared fixture. Named evidence columns/objects: `service`, `i`, `sqlstate`.
--    Verify: For Exercise 2, replay the written Session A/Session B order against `advanced_sql_training`, compare the observed values/SQLSTATE with the prediction, then query/drop the disposable fixture and confirm neither session retains a transaction or lock.
--    Hint ladder, rung 1: Write the exact Session A/Session B schedule before opening either transaction; change only one isolation/lock step at a time.
-- 3. Insert two visits whose external_reference is NULL. Explain why an ordinary
--    UNIQUE constraint permits them. What PostgreSQL 15+ syntax would you choose
--    if NULL had to behave like a duplicate?
--
--    Inputs: Use `pro_relational_lab.maintenance_visits`, `pro_relational_lab.equipment_items` plus only the small disposable fixture explicitly requested by Exercise 3; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 3 requires a written prediction and the observed result for “NULL uniqueness: insert two NULL references, explain the observed rule, and write—but do not blindly apply—the stricter PostgreSQL 15+ alternative”. Show both compared result shapes at one row per requested calendar/cohort bucket and grouping key, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `i`, `dates`, `mv`.
--    Verify: For Exercise 3, run the two forms over the identical rows in `pro_relational_lab.maintenance_visits`, `pro_relational_lab.equipment_items`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.
-- 4. Classify daily_fee_at_checkout as normalized duplication, an accidental
--    inconsistency, or deliberate denormalization. State the invariant and the
--    historical question that justify your choice.
--
--    Inputs: Use `pro_relational_lab.members`, `pro_relational_lab.equipment_categories`, `pro_relational_lab.equipment_items`, `pro_relational_lab.loans` plus only the small disposable fixture explicitly requested by Exercise 4; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 4 requires a written prediction and the observed result for “Historical fee: state the invariant, the historical question, and why the checkout snapshot is or is not deliberate denormalization”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys.
--    Verify: For Exercise 4, run the two forms over the identical rows in `pro_relational_lab.members`, `pro_relational_lab.equipment_categories`, `pro_relational_lab.equipment_items`, `pro_relational_lab.loans`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.
-- 5. A provider can perform many visits and a visit can involve several
--    technicians. Model providers, technicians, and visit assignments without
--    storing comma-separated names. State the grain and keys of every table.
--
--    Inputs: Use `pro_relational_lab.providers`, `pro_relational_lab.technicians`, `pro_relational_lab.visit_technicians`, `pro_relational_lab.maintenance_visits` plus only the small disposable fixture explicitly requested by Exercise 5; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 5 must make “Many-to-many work: model providers, technicians, and assignments with one declared grain and key per relation; do not use delimited text” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `IDENTITY`, `mv`, `t`, `pro_relational_lab.providers`, `pro_relational_lab.technicians`, `pro_relational_lab.visit_technicians`.
--    Verify: For Exercise 5, inspect the relevant `pg_catalog` or `information_schema` rows for `IDENTITY`, `mv`, `t`, `pro_relational_lab.providers`, `pro_relational_lab.technicians`, `pro_relational_lab.visit_technicians`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: State the invariant and object grain first, implement the smallest DDL step, then design its catalog and negative-case proof.
-- 6. Write a query that reports every equipment item, including items with no
--    loans, plus its loan count and latest checkout date. Explain why filtering
--    the loan table in WHERE can accidentally turn the LEFT JOIN into an inner
--    join, and make ties deterministic.
--
--    Inputs: Use `pro_relational_lab.loans`, `pro_relational_lab.equipment_items` plus only the small disposable fixture explicitly requested by Exercise 6; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 6 must make “Outer-join report: retain never-borrowed equipment, make date ties deterministic, and test the result with an item that has no loan” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `IDENTITY`, `i`, `loan_count`, `latest_checkout`, `l`, `pro_relational_lab.loans`.
--    Verify: For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `IDENTITY`, `i`, `loan_count`, `latest_checkout`, `l`, `pro_relational_lab.loans`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: State the invariant and object grain first, implement the smallest DDL step, then design its catalog and negative-case proof.
-- 7. Choose ON DELETE behavior for category -> equipment, equipment -> loans,
--    and equipment -> maintenance_visits. Defend each RESTRICT, CASCADE, or
--    SET NULL decision in terms of historical truth rather than convenience.
--
--    Inputs: Use `pro_relational_lab.members`, `pro_relational_lab.equipment_categories`, `pro_relational_lab.equipment_items`, `pro_relational_lab.loans` plus only the small disposable fixture explicitly requested by Exercise 7; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 7 must make “Deletion policy: choose and defend one referential action for each named relationship, including what happens to historical records” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `historical`.
--    Verify: For Exercise 7, inspect the relevant `pg_catalog` or `information_schema` rows for `historical`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state.
--    Hint ladder, rung 1: State the invariant and object grain first, implement the smallest DDL step, then design its catalog and negative-case proof.
-- 8. Write catalog queries that prove the maintenance_visits primary key,
--    foreign key, checks, generated column, and NULL-aware uniqueness contract.
--    Do not depend on PostgreSQL-generated constraint names.
--    Inputs: Use `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, `pg_catalog.pg_attrdef` plus only the small disposable fixture explicitly requested by Exercise 8; keep the same filters/time window for its control query.
--    Expected result/shape: Exercise 8 returns a table-shaped answer to “Contract introspection: prove key, check, generated-value, and uniqueness properties from catalogs without depending on generated object names” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `constraint_definition`, `con`, `rel`, `n`, `column_name`, `generated_expression`, `def`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
--    Verify: For Exercise 8, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, `pg_catalog.pg_attrdef`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary.
--    Hint ladder, rung 1: Build and inspect the input relation and keys first; add one filter, grouping/window, projection, and ordering stage at a time.

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
