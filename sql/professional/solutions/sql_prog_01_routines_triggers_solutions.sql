-- SQL-PROG-01 executable solutions
-- SOLUTION READING MAP — sql-prog-01: Functions, Procedures, and Triggers
-- Explanation: sql/professional/solutions/sql_prog_01_routines_triggers_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_prog_01_routines_triggers_solutions.sql
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
    ('Morgan', 'Three', 'in_progress'),
    ('Morgan', 'Four stays closed', 'closed');

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
    IF OLD.item_id IS DISTINCT FROM NEW.item_id THEN
        RAISE EXCEPTION 'item_id is immutable (% -> %)', OLD.item_id, NEW.item_id
            USING ERRCODE = 'check_violation';
    END IF;
    IF OLD.status = 'closed' AND NEW.status = 'open' THEN
        RAISE EXCEPTION 'closed item % cannot reopen directly', OLD.item_id
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END
$function$;

CREATE TRIGGER work_items_prevent_direct_reopen
BEFORE UPDATE ON pro_routines_lab.work_items
FOR EACH ROW
EXECUTE FUNCTION pro_routines_lab.prevent_direct_reopen();

UPDATE pro_routines_lab.work_items AS wi
SET status = 'closed'
WHERE wi.item_id = 1;

SELECT
    pro_routines_lab.status_change_count(1) AS item_1_changes,
    pro_routines_lab.status_change_count(3) AS item_3_changes,
    pro_routines_lab.status_change_count(NULL) AS null_item_changes;

CALL pro_routines_lab.reassign_open_items('Morgan', 'Taylor');

DO $solution$
BEGIN
    BEGIN
        CALL pro_routines_lab.reassign_open_items('Taylor', '   ');
        RAISE EXCEPTION 'blank destination unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected blank-owner rejection: %', SQLERRM;
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM pro_routines_lab.work_items AS wi
        WHERE wi.title = 'Three'
          AND wi.owner_name = 'Taylor'
          AND wi.status = 'in_progress'
    ) OR NOT EXISTS (
        SELECT 1
        FROM pro_routines_lab.work_items AS wi
        WHERE wi.title = 'Four stays closed'
          AND wi.owner_name = 'Morgan'
          AND wi.status = 'closed'
    ) THEN
        RAISE EXCEPTION 'procedure changed the wrong eligibility set';
    END IF;
END
$solution$;

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

DO $solution$
BEGIN
    BEGIN
        UPDATE pro_routines_lab.work_items
        SET item_id = DEFAULT
        WHERE item_id = 1;
        RAISE EXCEPTION 'item_id mutation unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected immutable-identity rejection: %', SQLERRM;
    END;
END
$solution$;

-- A second valid transition makes Exercise 1's multiple-row boundary visible.
UPDATE pro_routines_lab.work_items AS wi
SET status = 'in_progress'
WHERE wi.item_id = 1;

UPDATE pro_routines_lab.work_items AS wi
SET status = 'closed'
WHERE wi.item_id = 3;

SELECT *
FROM (
    VALUES
        ('zero matching audit rows'::text, 999::bigint,
         pro_routines_lab.status_change_count(999)),
        ('one matching audit row', 3::bigint,
         pro_routines_lab.status_change_count(3)),
        ('multiple matching audit rows', 1::bigint,
         pro_routines_lab.status_change_count(1)),
        ('NULL input policy', NULL::bigint,
         pro_routines_lab.status_change_count(NULL))
) AS probes(probe, item_id, observed_change_count)
ORDER BY probe;

SELECT
    wi.item_id,
    wi.owner_name,
    wi.status
FROM pro_routines_lab.work_items AS wi
ORDER BY wi.item_id;

DO $solution$
BEGIN
    IF pro_routines_lab.status_change_count(1) <> 2 THEN
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

-- Exercise 4 is reconciled after Exercise 7 creates the statement-level audit.

-- Exercise 5: choose the narrowest mechanism whose authority matches the rule.
SELECT *
FROM (
    VALUES
        ('allowed status vocabulary', 'CHECK constraint',
         'row-local and declarative; all writers receive the same rule'),
        ('OLD-to-NEW transition', 'row trigger',
         'requires both stored versions and may reject or audit a transition'),
        ('queryable reusable calculation', 'function',
         'composes in SQL but cannot COMMIT or ROLLBACK'),
        ('multi-step command', 'procedure called with CALL',
         'may control transactions only when invoked at an allowed top-level boundary')
) AS decision(rule, mechanism, reason)
ORDER BY rule;

-- Exercise 6: inspect the promises PostgreSQL's planner relies on.
SELECT
    CASE p.prokind
        WHEN 'f' THEN 'function'
        WHEN 'p' THEN 'procedure'
        ELSE p.prokind::text
    END AS routine_kind,
    p.proname,
    pg_get_function_identity_arguments(p.oid) AS identity_arguments,
    CASE p.provolatile
        WHEN 'i' THEN 'immutable'
        WHEN 's' THEN 'stable'
        ELSE 'volatile'
    END AS volatility,
    CASE p.proparallel
        WHEN 's' THEN 'safe'
        WHEN 'r' THEN 'restricted'
        ELSE 'unsafe'
    END AS parallel_mode
    ,
    p.prosecdef AS security_definer,
    p.proconfig AS routine_settings
FROM pg_catalog.pg_proc AS p
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = p.pronamespace
WHERE n.nspname = 'pro_routines_lab'
ORDER BY p.proname;

-- Exercise 7: transition tables expose the complete affected set once per
-- statement, including a legitimate zero-change status summary.
CREATE TABLE pro_routines_lab.statement_status_summary (
    summary_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    matched_rows integer NOT NULL,
    changed_status_rows integer NOT NULL
);

CREATE FUNCTION pro_routines_lab.summarize_status_statement()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
BEGIN
    INSERT INTO pro_routines_lab.statement_status_summary (
        matched_rows, changed_status_rows
    )
    SELECT
        COUNT(*)::integer,
        COUNT(*) FILTER (
            WHERE o.status IS DISTINCT FROM n.status
        )::integer
    FROM old_rows AS o
    JOIN new_rows AS n USING (item_id);
    RETURN NULL;
END
$function$;

CREATE TRIGGER work_items_statement_status_summary
AFTER UPDATE ON pro_routines_lab.work_items
REFERENCING OLD TABLE AS old_rows NEW TABLE AS new_rows
FOR EACH STATEMENT
EXECUTE FUNCTION pro_routines_lab.summarize_status_statement();

UPDATE pro_routines_lab.work_items AS wi
SET title = wi.title || ' (reviewed)'
WHERE wi.item_id IN (1, 3);

-- A statement trigger fires even when the target set is genuinely empty.
UPDATE pro_routines_lab.work_items AS wi
SET title = wi.title
WHERE false;

-- This two-row status transition supports the Exercise 4 reconciliation:
-- two row-level audit facts but one statement-level summary fact.
UPDATE pro_routines_lab.work_items AS wi
SET status = 'in_progress'
WHERE wi.item_id IN (2, 4);

SELECT
    s.summary_id,
    s.matched_rows,
    s.changed_status_rows
FROM pro_routines_lab.statement_status_summary AS s
ORDER BY s.summary_id;

SELECT
    (
        SELECT COUNT(*)
        FROM pro_routines_lab.work_item_audit AS a
        WHERE a.item_id IN (2, 4)
          AND a.old_status = 'closed'
          AND a.new_status = 'in_progress'
    ) AS row_audit_records,
    (
        SELECT COUNT(*)
        FROM pro_routines_lab.statement_status_summary AS s
        WHERE s.matched_rows = 2
          AND s.changed_status_rows = 2
    ) AS statement_audit_records,
    (
        SELECT MAX(s.changed_status_rows)
        FROM pro_routines_lab.statement_status_summary AS s
        WHERE s.matched_rows = 2
          AND s.changed_status_rows = 2
    ) AS statement_changed_status_rows;

DO $solution$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pro_routines_lab.statement_status_summary AS s
        WHERE s.matched_rows = 0
          AND s.changed_status_rows = 0
    ) THEN
        RAISE EXCEPTION 'zero-row UPDATE did not record (0, 0)';
    END IF;

    IF (
        SELECT COUNT(*)
        FROM pro_routines_lab.work_item_audit AS a
        WHERE a.item_id IN (2, 4)
          AND a.old_status = 'closed'
          AND a.new_status = 'in_progress'
    ) <> 2 THEN
        RAISE EXCEPTION 'row-level audit reconciliation failed';
    END IF;
END
$solution$;

-- Exercise 8: only the inner duplicate insert rolls back. The outer marker
-- remains, and an unexpected condition is never swallowed.
CREATE TABLE pro_routines_lab.exception_probe (
    probe_key text PRIMARY KEY
);

DO $solution$
BEGIN
    INSERT INTO pro_routines_lab.exception_probe VALUES ('outer-survives');
    BEGIN
        INSERT INTO pro_routines_lab.exception_probe VALUES ('duplicate');
        INSERT INTO pro_routines_lab.exception_probe VALUES ('duplicate');
        RAISE EXCEPTION 'duplicate insert unexpectedly succeeded';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Expected unique violation rolled back inner work';
    END;

    IF NOT EXISTS (
        SELECT 1
        FROM pro_routines_lab.exception_probe AS p
        WHERE p.probe_key = 'outer-survives'
    ) OR EXISTS (
        SELECT 1
        FROM pro_routines_lab.exception_probe AS p
        WHERE p.probe_key = 'duplicate'
    ) THEN
        RAISE EXCEPTION 'subtransaction rollback boundary was incorrect';
    END IF;
END
$solution$;

-- Exercise 9: this lesson deliberately creates no SECURITY DEFINER routine.
-- Inventory the actual state, then return a design-only hardening checklist;
-- SQL-SEC-01 performs the privileged role/grant exercise.
SELECT
    p.proname,
    pg_get_function_identity_arguments(p.oid) AS identity_arguments,
    p.prosecdef AS security_definer,
    pg_get_userbyid(p.proowner) AS owner_name,
    p.proconfig AS routine_settings,
    p.proacl AS execute_acl
FROM pg_catalog.pg_proc AS p
JOIN pg_catalog.pg_namespace AS n
  ON n.oid = p.pronamespace
WHERE n.nspname = 'pro_routines_lab'
ORDER BY p.proname, identity_arguments;

SELECT *
FROM (
    VALUES
        (1, 'dedicated owner', 'NOLOGIN role with only required object privileges'),
        (2, 'fixed path', 'SET search_path = pg_catalog and schema-qualify every object'),
        (3, 'validated input', 'reject NULL, blank, out-of-range, and unauthorized values'),
        (4, 'closed execution surface', 'REVOKE ALL ON FUNCTION ... FROM PUBLIC'),
        (5, 'explicit caller', 'GRANT EXECUTE only to the reviewed application role'),
        (6, 'catalog verification', 'inspect owner, prosecdef, proconfig, and proacl')
) AS hardening(step_number, control, required_evidence)
ORDER BY step_number;

-- Exercise 10: claim a deterministic batch under row locks. Production workers
-- commit quickly, recover stale leases, and keep external work out of this lock.
CREATE TABLE pro_routines_lab.claim_queue (
    queue_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    claimed_by text,
    claimed_at timestamptz
);

INSERT INTO pro_routines_lab.claim_queue (claimed_by)
VALUES (NULL), (NULL), (NULL);

WITH claimable AS (
    SELECT q.queue_id
    FROM pro_routines_lab.claim_queue AS q
    WHERE q.claimed_by IS NULL
    ORDER BY q.queue_id
    FOR UPDATE SKIP LOCKED
    LIMIT 2
)
UPDATE pro_routines_lab.claim_queue AS q
SET claimed_by = 'worker-1',
    claimed_at = TIMESTAMPTZ '2026-06-01 00:00:00+00'
FROM claimable AS c
WHERE q.queue_id = c.queue_id
RETURNING q.queue_id, q.claimed_by, q.claimed_at;

ROLLBACK;
