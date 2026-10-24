-- SQL-PROG-01: Functions, procedures, and triggers
-- BEGINNER WORKFLOW — sql-prog-01: Functions, Procedures, and Triggers
-- Guide: sql/professional/companion-guides/sql_prog_01_routines_triggers.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-prog-01/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pro_routines_lab.work_items, pro_routines_lab.work_item_audit, pro_routines_lab.statement_audit.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
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
--    Inputs: For sql-prog-01 Exercise 1, create the STABLE SQL function `status_change_count(p_item_id bigint)` over `work_item_audit`, with the explicit policy that NULL or an unknown ID returns zero.
--    Expected result/shape: For sql-prog-01 Exercise 1, expected output: one scalar count per invocation plus a four-row probe matrix demonstrating zero, one, multiple, and NULL-input cases; every count is a nonnegative bigint.
--    Verify: For sql-prog-01 Exercise 1, compare each function result with an independent filtered `COUNT(*)`, assert item 1 has multiple audits, item 3 has one, an absent ID has zero, and NULL has zero because SQL equality matches no row.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 1, inspect the source keys that survive `WHERE`; then check `wi.item_id` before applying the row cap.
-- 2. Write a procedure reassign_open_items(from_owner, to_owner) that changes
--    only non-closed items and rejects a blank destination owner.
--
--    Inputs: For sql-prog-01 Exercise 2, create and call `reassign_open_items(p_from_owner, p_to_owner)`, rejecting NULL/blank destinations before updating only source-owner rows whose status is not `closed`.
--    Expected result/shape: For sql-prog-01 Exercise 2, expected output: a successful CALL that moves Morgan's eligible item to Taylor, while Morgan's closed item remains unchanged; a blank destination is caught as SQLSTATE class `check_violation`.
--    Verify: For sql-prog-01 Exercise 2, snapshot eligible and closed source rows before CALL, reconcile the changed target set afterward, and prove the nested invalid CALL changes no owner values.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 2, check the reassignment procedure written analysis against `update`.
-- 3. Add a BEFORE UPDATE trigger that rejects a direct closed -> open
--    transition. Safely prove the rejection and explain when application code
--    or a dedicated transition table would be clearer.
--
--    Inputs: For sql-prog-01 Exercise 3, use a BEFORE UPDATE row trigger to reject direct `closed` to `open` transitions and primary-key mutation, returning NEW for allowed updates.
--    Expected result/shape: For sql-prog-01 Exercise 3, expected output: allowed transitions succeed, direct reopen and identity mutation each emit an expected rejection notice, and rejected rows retain their original values.
--    Verify: For sql-prog-01 Exercise 3, attempt both an allowed `closed` to `in_progress` transition and a forbidden `closed` to `open` transition, record SQLSTATE `23514`, and reselect the row after each attempt.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 3, check the transition guard written analysis against `check_violation`, and `if`.
-- 4. Compare the number of row-audit records with statement-audit records after
--    a multirow update. State the grain of each audit table.
--
--    Inputs: For sql-prog-01 Exercise 4, compare row-level status audits with the statement-level summary produced by one two-row status UPDATE.
--    Expected result/shape: For sql-prog-01 Exercise 4, expected output: one reconciliation row with `row_audit_records = 2`, `statement_audit_records = 1`, and `statement_changed_status_rows = 2`.
--    Verify: For sql-prog-01 Exercise 4, filter row audits to the two known item IDs and transition, identify the one matching statement summary, and explain that row-audit grain is one changed item while statement-audit grain is one UPDATE statement.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 4, select `changed_rows` from `pro_routines_lab.work_items`, `ON`, and `NEW.status` before adding derived columns.
-- 5. Explain why a CHECK constraint, not a trigger, enforces the allowed status
--    values. Explain why functions cannot COMMIT, and when a top-level procedure
--    may control transactions.
--
--    Inputs: For sql-prog-01 Exercise 5, return a rule-to-mechanism decision matrix covering a row-local CHECK, OLD/NEW trigger, query function, and multi-step procedure.
--    Expected result/shape: For sql-prog-01 Exercise 5, expected output: four rows with `rule`, `mechanism`, and `reason`, ordered deterministically by rule.
--    Verify: For sql-prog-01 Exercise 5, reject one disallowed status through the CHECK, prove the transition trigger sees OLD/NEW, and state that functions cannot transaction-control while a procedure may do so only at an allowed top-level CALL boundary.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 5, check the declarative boundary written analysis against `call`.
-- 6. Classify the lesson routines as VOLATILE, STABLE, or IMMUTABLE and decide
--    whether each can be PARALLEL SAFE. Explain why an incorrect promise can
--    produce wrong plans or results even when a demo appears to work.
--
--    Inputs: For sql-prog-01 Exercise 6, inspect `pg_proc`/`pg_namespace` for every lab function and procedure, including kind, name, identity arguments, volatility, parallel mode, security mode, and routine settings.
--    Expected result/shape: For sql-prog-01 Exercise 6, expected output: one row per routine signature, ordered by routine name, with overloaded routines distinguishable through `identity_arguments`.
--    Verify: For sql-prog-01 Exercise 6, compare catalog values with every `CREATE FUNCTION/PROCEDURE` declaration and explain that falsely promising STABLE/IMMUTABLE or PARALLEL SAFE can permit invalid planner assumptions and wrong results.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 6, start with the first relation in `pg_catalog.pg_proc`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `proname` so the exact fanout or loss is visible.
-- 7. Add an AFTER UPDATE statement trigger with transition tables that records
--    one summary row per statement. Reconcile affected rows against the
--    row-level audit and define behavior for an update that changes zero rows.
--
--    Inputs: For sql-prog-01 Exercise 7, create an AFTER UPDATE statement trigger with OLD/NEW transition tables, joining on the enforced immutable `item_id`, then run a multirow title update and a truly zero-target `WHERE false` update.
--    Expected result/shape: For sql-prog-01 Exercise 7, expected output: one summary row `(matched_rows=2, changed_status_rows=0)`, one `(0,0)` row for the empty target, and one `(2,2)` row for a two-item status change.
--    Verify: For sql-prog-01 Exercise 7, assert exactly one summary per UPDATE statement, reconcile changed-status counts with row audits, prove the zero-target statement records `(0,0)`, and keep `item_id` immutable so transition-table pairing cannot undercount.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 7, start with the first relation in `pro_routines_lab.statement_status_summary`, `n.status`, `old_rows`, `new_rows`, and `ON`; after each join, record total rows and distinct `integer` so the exact fanout or loss is visible.
-- 8. Use a nested PL/pgSQL block to catch one expected unique_violation, then
--    prove only the inner subtransaction was rolled back. Re-raise every
--    unexpected SQLSTATE instead of using WHEN OTHERS as silent control flow.
--
--    Inputs: For sql-prog-01 Exercise 8, insert an outer marker, provoke one duplicate key inside a nested PL/pgSQL exception block, and catch only `unique_violation`.
--    Expected result/shape: For sql-prog-01 Exercise 8, expected output: one expected NOTICE; the outer marker remains, while both inner `duplicate` inserts are absent because the inner block rolled back.
--    Verify: For sql-prog-01 Exercise 8, query `exception_probe` for both keys after the handler and fail unless outer count is one and duplicate count is zero; never use a silent `WHEN OTHERS` branch.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 8, materialize the intended `unique_violation` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.exception_probe` again and prove rollback or idempotent retry.
-- 9. Harden a SECURITY DEFINER reporting function: fixed search_path,
--    schema-qualified objects, validated parameters, revoked PUBLIC execution,
--    narrow owner privileges, and explicit grants. State why ownership itself
--    is part of the security boundary.
--
--    Inputs: For sql-prog-01 Exercise 9, inventory actual routine owner/security/path/ACL metadata, then return an explicitly design-only six-step SECURITY DEFINER hardening checklist; this lesson creates no definer routine.
--    Expected result/shape: For sql-prog-01 Exercise 9, expected output: catalog rows proving every lab routine is security-invoker, followed by six ordered controls covering NOLOGIN ownership, fixed path, qualified objects, validation, PUBLIC revocation, narrow grant, and catalog verification.
--    Verify: For sql-prog-01 Exercise 9, require `prosecdef = false` for the executable lab and treat the checklist as proposed policy; perform privileged role/grant validation only in SQL-SEC-01 rather than implying it happened here.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 9, select `search_path` from `pro_routines_lab.work_items`, `ON`, and `NEW.status` before adding derived columns.
-- 10. Simulate two workers claiming open items. Design one solution using
--     SELECT ... FOR UPDATE SKIP LOCKED, define deterministic batch order, and
--     explain starvation, retry, and transaction-length trade-offs.

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
--    Inputs: For sql-prog-01 Exercise 10, select the first two unclaimed queue rows by `queue_id` under `FOR UPDATE SKIP LOCKED`, then update those exact rows with a worker and timestamp.
--    Expected result/shape: For sql-prog-01 Exercise 10, expected output: two `RETURNING` rows with `queue_id`, `claimed_by`, and `claimed_at`, ordered by the deterministic claim selection.
--    Verify: For sql-prog-01 Exercise 10, reconcile returned IDs with the preselected batch, simulate a second transaction seeing different unlocked rows, keep the lock transaction short, and define retry, stale-lease, and starvation monitoring policies.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 10, run `claimable` one at a time. Record each CTE's row count and `affected_row_count` uniqueness before the next stage uses it.

ROLLBACK;
\echo 'SQL-PROG-01 complete: pro_routines_lab was rolled back'
