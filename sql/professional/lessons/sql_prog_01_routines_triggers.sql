-- SQL-PROG-01: Functions, procedures, and triggers
-- Target: PostgreSQL 16+
-- All objects are rolled back.

\set ON_ERROR_STOP on
\echo 'SQL-PROG-01: disposable routines and trigger lab'

BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_routines_lab;

-- Declarative constraints are the first choice for row-local invariants.
CREATE TABLE pro_routines_lab.work_items (
    item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_name text NOT NULL CHECK (btrim(owner_name) <> ''),
    title text NOT NULL CHECK (btrim(title) <> ''),
    status text NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'in_progress', 'closed')),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE pro_routines_lab.work_item_audit (
    audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id bigint NOT NULL,
    old_status text NOT NULL,
    new_status text NOT NULL,
    changed_by text NOT NULL,
    changed_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE pro_routines_lab.statement_audit (
    statement_audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    changed_rows integer NOT NULL CHECK (changed_rows >= 0),
    item_ids bigint[] NOT NULL,
    changed_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

INSERT INTO pro_routines_lab.work_items (owner_name, title, status)
VALUES
    ('Avery', 'Review intake form', 'open'),
    ('Avery', 'Publish reference notes', 'in_progress'),
    ('Morgan', 'Archive completed records', 'open');

-- Query functions can be composed inside SELECT. STABLE promises that this
-- function does not modify data and sees one statement snapshot.
CREATE FUNCTION pro_routines_lab.open_item_count(p_owner_name text)
RETURNS bigint
LANGUAGE sql
STABLE
PARALLEL SAFE
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
    SELECT COUNT(*)
    FROM pro_routines_lab.work_items AS wi
    WHERE wi.owner_name = p_owner_name
      AND wi.status <> 'closed'
$function$;

-- A BEFORE row trigger may replace NEW before storage.
CREATE FUNCTION pro_routines_lab.set_work_item_updated_at()
RETURNS trigger
LANGUAGE plpgsql
VOLATILE
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
BEGIN
    NEW.updated_at := clock_timestamp();
    RETURN NEW;
END
$function$;

CREATE TRIGGER work_items_set_updated_at
BEFORE UPDATE ON pro_routines_lab.work_items
FOR EACH ROW
EXECUTE FUNCTION pro_routines_lab.set_work_item_updated_at();

-- An AFTER row trigger records one audit row per status transition.
CREATE FUNCTION pro_routines_lab.audit_work_item_status()
RETURNS trigger
LANGUAGE plpgsql
VOLATILE
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO pro_routines_lab.work_item_audit (
            item_id,
            old_status,
            new_status,
            changed_by
        )
        VALUES (
            NEW.item_id,
            OLD.status,
            NEW.status,
            CURRENT_USER
        );
    END IF;
    RETURN NULL;
END
$function$;

CREATE TRIGGER work_items_status_audit
AFTER UPDATE ON pro_routines_lab.work_items
FOR EACH ROW
EXECUTE FUNCTION pro_routines_lab.audit_work_item_status();

-- A statement trigger runs once and can inspect transition tables containing
-- all OLD and NEW rows affected by that statement.
CREATE FUNCTION pro_routines_lab.audit_work_item_statement()
RETURNS trigger
LANGUAGE plpgsql
VOLATILE
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
BEGIN
    INSERT INTO pro_routines_lab.statement_audit (changed_rows, item_ids)
    SELECT
        COUNT(*)::integer,
        COALESCE(
            array_agg(n.item_id ORDER BY n.item_id),
            ARRAY[]::bigint[]
        )
    FROM new_rows AS n
    JOIN old_rows AS o
      ON o.item_id = n.item_id
    WHERE ROW(n.owner_name, n.title, n.status)
          IS DISTINCT FROM
          ROW(o.owner_name, o.title, o.status);
    RETURN NULL;
END
$function$;

CREATE TRIGGER work_items_statement_audit
AFTER UPDATE ON pro_routines_lab.work_items
REFERENCING OLD TABLE AS old_rows NEW TABLE AS new_rows
FOR EACH STATEMENT
EXECUTE FUNCTION pro_routines_lab.audit_work_item_statement();

-- Procedures are invoked with CALL and do not return a query relation. This
-- procedure deliberately participates in its caller's transaction.
CREATE PROCEDURE pro_routines_lab.close_owner_items(p_owner_name text)
LANGUAGE plpgsql
SECURITY INVOKER
AS $procedure$
BEGIN
    UPDATE pro_routines_lab.work_items AS wi
    SET status = 'closed'
    WHERE wi.owner_name = p_owner_name
      AND wi.status <> 'closed';
END
$procedure$;

\echo 'Function used as a query expression'
SELECT
    owners.owner_name,
    pro_routines_lab.open_item_count(owners.owner_name) AS open_items
FROM (
    VALUES ('Avery'::text), ('Morgan'::text)
) AS owners(owner_name)
ORDER BY owners.owner_name;

\echo 'One multirow statement fires two row audits and one statement audit'
UPDATE pro_routines_lab.work_items AS wi
SET status = 'closed'
WHERE wi.owner_name = 'Avery';

SELECT
    a.item_id,
    a.old_status,
    a.new_status,
    a.changed_by
FROM pro_routines_lab.work_item_audit AS a
ORDER BY a.audit_id;

SELECT
    sa.changed_rows,
    sa.item_ids
FROM pro_routines_lab.statement_audit AS sa
ORDER BY sa.statement_audit_id;

\echo 'Procedure invoked with CALL inside the caller-owned transaction'
CALL pro_routines_lab.close_owner_items('Morgan');

SELECT
    wi.item_id,
    wi.owner_name,
    wi.title,
    wi.status
FROM pro_routines_lab.work_items AS wi
ORDER BY wi.item_id;

-- Exercises:
--
-- 1. Write a STABLE SQL function status_change_count(item_id) that returns the
--    number of audit rows for one item. Decide what NULL input should return.
--
-- 2. Write a procedure reassign_open_items(from_owner, to_owner) that changes
--    only non-closed items and rejects a blank destination owner.
--
-- 3. Add a BEFORE UPDATE trigger that rejects a direct closed -> open
--    transition. Safely prove the rejection and explain when application code
--    or a dedicated transition table would be clearer.
--
-- 4. Compare the number of row-audit records with statement-audit records after
--    a multirow update. State the grain of each audit table.
--
-- 5. Explain why a CHECK constraint, not a trigger, enforces the allowed status
--    values. Explain why functions cannot COMMIT, and when a top-level procedure
--    may control transactions.

DO $self_check$
BEGIN
    IF (SELECT COUNT(*) FROM pro_routines_lab.work_items) <> 3 THEN
        RAISE EXCEPTION 'unexpected work-item count';
    END IF;
    IF (SELECT COUNT(*) FROM pro_routines_lab.work_item_audit) <> 3 THEN
        RAISE EXCEPTION 'expected three row-level status audits';
    END IF;
    IF (
        SELECT COALESCE(SUM(sa.changed_rows), 0)
        FROM pro_routines_lab.statement_audit AS sa
    ) <> 3 THEN
        RAISE EXCEPTION 'statement audit did not account for three changed rows';
    END IF;
END
$self_check$;

ROLLBACK;
\echo 'SQL-PROG-01 complete: pro_routines_lab was rolled back'

