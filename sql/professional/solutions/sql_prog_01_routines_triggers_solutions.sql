-- SQL-PROG-01 executable solutions
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_routines_lab;

CREATE TABLE pro_routines_lab.work_items (
    item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    owner_name text NOT NULL CHECK (btrim(owner_name) <> ''),
    title text NOT NULL,
    status text NOT NULL CHECK (status IN ('open', 'in_progress', 'closed'))
);

CREATE TABLE pro_routines_lab.work_item_audit (
    audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id bigint NOT NULL,
    old_status text NOT NULL,
    new_status text NOT NULL
);

INSERT INTO pro_routines_lab.work_items (owner_name, title, status)
VALUES
    ('Avery', 'One', 'open'),
    ('Avery', 'Two', 'closed'),
    ('Morgan', 'Three', 'in_progress');

CREATE FUNCTION pro_routines_lab.audit_status()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO pro_routines_lab.work_item_audit (
            item_id, old_status, new_status
        )
        VALUES (NEW.item_id, OLD.status, NEW.status);
    END IF;
    RETURN NULL;
END
$function$;

CREATE TRIGGER work_items_audit_status
AFTER UPDATE ON pro_routines_lab.work_items
FOR EACH ROW
EXECUTE FUNCTION pro_routines_lab.audit_status();

-- Exercise 1: NULL input returns zero because equality matches no item.
CREATE FUNCTION pro_routines_lab.status_change_count(p_item_id bigint)
RETURNS bigint
LANGUAGE sql
STABLE
PARALLEL SAFE
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
    SELECT COUNT(*)
    FROM pro_routines_lab.work_item_audit AS a
    WHERE a.item_id = p_item_id
$function$;

-- Exercise 2.
CREATE PROCEDURE pro_routines_lab.reassign_open_items(
    p_from_owner text,
    p_to_owner text
)
LANGUAGE plpgsql
SECURITY INVOKER
AS $procedure$
BEGIN
    IF p_to_owner IS NULL OR btrim(p_to_owner) = '' THEN
        RAISE EXCEPTION 'destination owner must not be blank'
            USING ERRCODE = 'check_violation';
    END IF;

    UPDATE pro_routines_lab.work_items AS wi
    SET owner_name = p_to_owner
    WHERE wi.owner_name = p_from_owner
      AND wi.status <> 'closed';
END
$procedure$;

-- Exercise 3.
CREATE FUNCTION pro_routines_lab.prevent_direct_reopen()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
BEGIN
    IF OLD.status = 'closed' AND NEW.status = 'open' THEN
        RAISE EXCEPTION 'closed item % cannot reopen directly', OLD.item_id
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END
$function$;

CREATE TRIGGER work_items_prevent_direct_reopen
BEFORE UPDATE OF status ON pro_routines_lab.work_items
FOR EACH ROW
EXECUTE FUNCTION pro_routines_lab.prevent_direct_reopen();

UPDATE pro_routines_lab.work_items AS wi
SET status = 'closed'
WHERE wi.item_id = 1;

SELECT
    pro_routines_lab.status_change_count(1) AS item_1_changes,
    pro_routines_lab.status_change_count(NULL) AS null_item_changes;

CALL pro_routines_lab.reassign_open_items('Morgan', 'Taylor');

DO $solution$
BEGIN
    BEGIN
        UPDATE pro_routines_lab.work_items AS wi
        SET status = 'open'
        WHERE wi.item_id = 2;
        RAISE EXCEPTION 'direct reopen unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected transition rejection: %', SQLERRM;
    END;
END
$solution$;

SELECT
    wi.item_id,
    wi.owner_name,
    wi.status
FROM pro_routines_lab.work_items AS wi
ORDER BY wi.item_id;

DO $solution$
BEGIN
    IF pro_routines_lab.status_change_count(1) <> 1 THEN
        RAISE EXCEPTION 'status-change function returned wrong count';
    END IF;
    IF NOT EXISTS (
        SELECT 1
        FROM pro_routines_lab.work_items AS wi
        WHERE wi.item_id = 3
          AND wi.owner_name = 'Taylor'
    ) THEN
        RAISE EXCEPTION 'procedure did not reassign eligible item';
    END IF;
END
$solution$;

ROLLBACK;

