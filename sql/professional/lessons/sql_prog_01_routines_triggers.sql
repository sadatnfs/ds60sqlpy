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
--    Inputs: For sql-prog-01 Exercise 1, read from `pro_routines_lab.work_item_audit`, `pro_routines_lab.work_items`, `OF`, `pro_routines_lab.status_change_count`, and `pro_routines_lab.reassign_open_items`. Build the answer toward `stable`; keep `stable` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-prog-01 Exercise 1, expected output: one row per `stable`. The final columns are `stable`. The final order is `wi.item_id`.
--    Verify: For sql-prog-01 Exercise 1, run an anti-check that counts rows where NOT ((a.item_id = p_item_id $function$) OR (wi.owner_name = p_from_owner AND wi.status <> 'closed') OR (wi.item_id = 1)); require unique `stable` where the expected grain is one row per key and confirm the projected `stable` against `pro_routines_lab.work_item_audit`, `pro_routines_lab.work_items`, `OF`, `pro_routines_lab.status_change_count`, and `pro_routines_lab.reassign_open_items`. Repeat with `NULL` in `stable` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 1, inspect the source keys that survive `WHERE`; then check `wi.item_id` before applying the row cap.
-- 2. Write a procedure reassign_open_items(from_owner, to_owner) that changes
--    only non-closed items and rejects a blank destination owner.
--
--    Inputs: For sql-prog-01 Exercise 2, complete the reassignment procedure written analysis and support its claims with read-only evidence from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-prog-01 Exercise 2, expected output: a completed the reassignment procedure written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `update`.
--    Verify: For sql-prog-01 Exercise 2, check the reassignment procedure written analysis against `update`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 2, check the reassignment procedure written analysis against `update`.
-- 3. Add a BEFORE UPDATE trigger that rejects a direct closed -> open
--    transition. Safely prove the rejection and explain when application code
--    or a dedicated transition table would be clearer.
--
--    Inputs: For sql-prog-01 Exercise 3, complete the transition guard written analysis and support its claims with read-only evidence from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-prog-01 Exercise 3, expected output: a completed the transition guard written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `check_violation`, and `if`.
--    Verify: For sql-prog-01 Exercise 3, check the transition guard written analysis against `check_violation`, and `if`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 3, check the transition guard written analysis against `check_violation`, and `if`.
-- 4. Compare the number of row-audit records with statement-audit records after
--    a multirow update. State the grain of each audit table.
--
--    Inputs: For sql-prog-01 Exercise 4, read from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Build the answer toward `changed_rows`; keep `changed_rows` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-prog-01 Exercise 4, expected output: one row per `changed_rows`. The final columns are `changed_rows`.
--    Verify: For sql-prog-01 Exercise 4, reselect the returned keys directly from the source; require unique `changed_rows` where the expected grain is one row per key and confirm the projected `changed_rows` against `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Add one source row with a new `changed_rows`; verify the result gains exactly one row carrying that `changed_rows` value.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 4, select `changed_rows` from `pro_routines_lab.work_items`, `ON`, and `NEW.status` before adding derived columns.
-- 5. Explain why a CHECK constraint, not a trigger, enforces the allowed status
--    values. Explain why functions cannot COMMIT, and when a top-level procedure
--    may control transactions.
--
--    Inputs: For sql-prog-01 Exercise 5, complete the declarative boundary written analysis and support its claims with read-only evidence from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-prog-01 Exercise 5, expected output: a completed the declarative boundary written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `call`.
--    Verify: For sql-prog-01 Exercise 5, check the declarative boundary written analysis against `call`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 5, check the declarative boundary written analysis against `call`.
-- 6. Classify the lesson routines as VOLATILE, STABLE, or IMMUTABLE and decide
--    whether each can be PARALLEL SAFE. Explain why an incorrect promise can
--    produce wrong plans or results even when a demo appears to work.
--
--    Inputs: For sql-prog-01 Exercise 6, read from `pg_catalog.pg_proc`, and `pg_catalog.pg_namespace`. Build the answer toward `proname`, `volatility`, and `parallel_mode`; keep `proname` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-prog-01 Exercise 6, expected output: one row per `proname`. The final columns are `proname`, `volatility`, and `parallel_mode`. The final order is `p.proname`.
--    Verify: For sql-prog-01 Exercise 6, project `proname` plus the raw source columns from `pg_catalog.pg_proc`, and `pg_catalog.pg_namespace` at each join stage; record row count and distinct `proname`, then assert the final `proname`, `volatility`, and `parallel_mode` values match those staged rows without unintended fanout or loss. Add one row for which `(n.nspname = 'pro_routines_lab')` is true and one for which it is false; verify only the matching `proname` value is returned.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 6, start with the first relation in `pg_catalog.pg_proc`, and `pg_catalog.pg_namespace`; after each join, record total rows and distinct `proname` so the exact fanout or loss is visible.
-- 7. Add an AFTER UPDATE statement trigger with transition tables that records
--    one summary row per statement. Reconcile affected rows against the
--    row-level audit and define behavior for an update that changes zero rows.
--
--    Inputs: For sql-prog-01 Exercise 7, read the target keys from `pro_routines_lab.statement_status_summary`, `n.status`, `old_rows`, `new_rows`, and `ON` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-prog-01 Exercise 7, expected output: the command tag and an independently counted set of affected `integer` values. The final columns are `integer`. The final order is `s.summary_id`.
--    Verify: For sql-prog-01 Exercise 7, materialize the intended `integer` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.statement_status_summary`, `n.status`, `old_rows`, `new_rows`, and `ON` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `integer` values in both cases.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 7, start with the first relation in `pro_routines_lab.statement_status_summary`, `n.status`, `old_rows`, `new_rows`, and `ON`; after each join, record total rows and distinct `integer` so the exact fanout or loss is visible.
-- 8. Use a nested PL/pgSQL block to catch one expected unique_violation, then
--    prove only the inner subtransaction was rolled back. Re-raise every
--    unexpected SQLSTATE instead of using WHEN OTHERS as silent control flow.
--
--    Inputs: For sql-prog-01 Exercise 8, read the target keys from `pro_routines_lab.exception_probe` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-prog-01 Exercise 8, expected output: the command tag and an independently counted set of affected `unique_violation` values. The final columns are `unique_violation`.
--    Verify: For sql-prog-01 Exercise 8, materialize the intended `unique_violation` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.exception_probe` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `unique_violation` values in both cases.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 8, materialize the intended `unique_violation` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.exception_probe` again and prove rollback or idempotent retry.
-- 9. Harden a SECURITY DEFINER reporting function: fixed search_path,
--    schema-qualified objects, validated parameters, revoked PUBLIC execution,
--    narrow owner privileges, and explicit grants. State why ownership itself
--    is part of the security boundary.
--
--    Inputs: For sql-prog-01 Exercise 9, read from `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Build the answer toward `search_path`; keep `search_path` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-prog-01 Exercise 9, expected output: one row per `search_path`. The final columns are `search_path`.
--    Verify: For sql-prog-01 Exercise 9, reselect the returned keys directly from the source; require unique `search_path` where the expected grain is one row per key and confirm the projected `search_path` against `pro_routines_lab.work_items`, `ON`, and `NEW.status`. Add one source row with a new `search_path`; verify the result gains exactly one row carrying that `search_path` value.
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
--    Inputs: For sql-prog-01 Exercise 10, read the target keys from `pro_routines_lab.claim_queue`, and `SKIP` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-prog-01 Exercise 10, expected output: one `RETURNING` row per affected `affected_row_count` plus the command tag, with pre-write and post-write values that reconcile. The final columns are `affected_row_count`, and `command_tag`.
--    Verify: For sql-prog-01 Exercise 10, materialize the intended `affected_row_count` target set first; require the command tag/`RETURNING` set to match it, then query `pro_routines_lab.claim_queue`, and `SKIP` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `command_tag` values in both cases.
--    Hint ladder, rung 1: For sql-prog-01 Exercise 10, run `claimable` one at a time. Record each CTE's row count and `affected_row_count` uniqueness before the next stage uses it.

ROLLBACK;
\echo 'SQL-PROG-01 complete: pro_routines_lab was rolled back'
