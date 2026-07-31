-- SQL-TEMPORAL-01: Temporal and domain modelling
-- BEGINNER WORKFLOW — sql-temporal-01: Temporal and Domain Modelling
-- Guide: sql/professional/companion-guides/sql_temporal_01_domain_modelling.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-temporal-01/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
-- Target: PostgreSQL 16+

\set ON_ERROR_STOP on
\echo 'SQL-TEMPORAL-01: disposable bitemporal, ledger, and retention lab'
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_temporal_lab;

-- One row is one recorded version of one customer's terms.
CREATE TABLE pro_temporal_lab.customer_terms (
    term_version_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_key text NOT NULL,
    valid_period daterange NOT NULL CHECK (
        NOT isempty(valid_period)
        AND lower_inc(valid_period)
        AND NOT upper_inc(valid_period)
    ),
    system_period tstzrange NOT NULL CHECK (
        NOT isempty(system_period)
        AND lower_inc(system_period)
        AND NOT upper_inc(system_period)
    ),
    monthly_rate numeric(10, 2) NOT NULL CHECK (monthly_rate >= 0),
    recorded_reason text NOT NULL CHECK (btrim(recorded_reason) <> '')
);

-- Built-in fallback for per-customer current-valid overlap. The advisory lock
-- serializes writers for one hashed customer key. An approved btree_gist
-- extension can express equality+range overlap as a declarative exclusion
-- constraint; this lesson never enables it.
CREATE FUNCTION pro_temporal_lab.prevent_current_term_overlap()
RETURNS trigger
LANGUAGE plpgsql
VOLATILE
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
BEGIN
    IF upper_inf(NEW.system_period) THEN
        PERFORM pg_advisory_xact_lock(
            hashtextextended(NEW.customer_key, 0)
        );

        IF EXISTS (
            SELECT 1
            FROM pro_temporal_lab.customer_terms AS existing
            WHERE existing.customer_key = NEW.customer_key
              AND existing.term_version_id <> COALESCE(
                  NEW.term_version_id,
                  -1
              )
              AND upper_inf(existing.system_period)
              AND existing.valid_period && NEW.valid_period
        ) THEN
            RAISE EXCEPTION
                'current valid periods overlap for customer %',
                NEW.customer_key
                USING ERRCODE = 'exclusion_violation';
        END IF;
    END IF;
    RETURN NEW;
END
$function$;

CREATE TRIGGER customer_terms_current_overlap
BEFORE INSERT OR UPDATE ON pro_temporal_lab.customer_terms
FOR EACH ROW
EXECUTE FUNCTION pro_temporal_lab.prevent_current_term_overlap();

-- Initial fact as first recorded on March 1.
INSERT INTO pro_temporal_lab.customer_terms (
    customer_key,
    valid_period,
    system_period,
    monthly_rate,
    recorded_reason
)
VALUES (
    'CUS-100',
    daterange(DATE '2026-01-01', DATE '2026-04-01', '[)'),
    tstzrange(TIMESTAMPTZ '2026-03-01 00:00:00+00', NULL, '[)'),
    10.00,
    'initial import'
);

-- On March 10, correct what the system knows without rewriting history.
UPDATE pro_temporal_lab.customer_terms AS ct
SET system_period = tstzrange(
        lower(ct.system_period),
        TIMESTAMPTZ '2026-03-10 00:00:00+00',
        '[)'
    )
WHERE ct.customer_key = 'CUS-100'
  AND upper_inf(ct.system_period)
  AND ct.valid_period
      = daterange(DATE '2026-01-01', DATE '2026-04-01', '[)');

INSERT INTO pro_temporal_lab.customer_terms (
    customer_key,
    valid_period,
    system_period,
    monthly_rate,
    recorded_reason
)
VALUES
    (
        'CUS-100',
        daterange(DATE '2026-01-01', DATE '2026-04-01', '[)'),
        tstzrange(TIMESTAMPTZ '2026-03-10 00:00:00+00', NULL, '[)'),
        12.00,
        'source correction received'
    ),
    (
        'CUS-100',
        daterange(DATE '2026-04-01', DATE '2026-07-01', '[)'),
        tstzrange(TIMESTAMPTZ '2026-03-10 00:00:00+00', NULL, '[)'),
        15.00,
        'future approved terms'
    );

\echo 'Bitemporal query: valid on date, as known at system timestamp'
SELECT
    ct.customer_key,
    ct.valid_period,
    ct.system_period,
    ct.monthly_rate,
    ct.recorded_reason
FROM pro_temporal_lab.customer_terms AS ct
WHERE ct.customer_key = 'CUS-100'
  AND ct.valid_period @> DATE '2026-02-15'
  AND ct.system_period @> TIMESTAMPTZ '2026-03-05 12:00:00+00'
ORDER BY ct.term_version_id;

SELECT
    ct.customer_key,
    ct.valid_period,
    ct.system_period,
    ct.monthly_rate,
    ct.recorded_reason
FROM pro_temporal_lab.customer_terms AS ct
WHERE ct.customer_key = 'CUS-100'
  AND ct.valid_period @> DATE '2026-02-15'
  AND ct.system_period @> TIMESTAMPTZ '2026-03-15 12:00:00+00'
ORDER BY ct.term_version_id;

DO $expected_overlap$
BEGIN
    BEGIN
        INSERT INTO pro_temporal_lab.customer_terms (
            customer_key,
            valid_period,
            system_period,
            monthly_rate,
            recorded_reason
        )
        VALUES (
            'CUS-100',
            daterange(DATE '2026-03-15', DATE '2026-05-01', '[)'),
            tstzrange(TIMESTAMPTZ '2026-03-20 00:00:00+00', NULL, '[)'),
            99.00,
            'overlap negative control'
        );
        RAISE EXCEPTION 'overlapping current term unexpectedly succeeded';
    EXCEPTION
        WHEN exclusion_violation THEN
            RAISE NOTICE 'Expected current-period rejection: %', SQLERRM;
    END;
END
$expected_overlap$;

-- Built-in declarative exclusion for one global resource. Per-key equality plus
-- range overlap normally uses the optional btree_gist extension.
CREATE TABLE pro_temporal_lab.global_maintenance_windows (
    window_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    window_period tstzrange NOT NULL CHECK (NOT isempty(window_period)),
    reason text NOT NULL,
    EXCLUDE USING gist (window_period WITH &&)
);

INSERT INTO pro_temporal_lab.global_maintenance_windows (
    window_period, reason
)
VALUES
    (
        tstzrange(
            TIMESTAMPTZ '2026-07-01 09:00:00+00',
            TIMESTAMPTZ '2026-07-01 10:00:00+00',
            '[)'
        ),
        'planned maintenance'
    ),
    (
        tstzrange(
            TIMESTAMPTZ '2026-07-01 10:00:00+00',
            TIMESTAMPTZ '2026-07-01 11:00:00+00',
            '[)'
        ),
        'adjacent non-overlapping window'
    );

SELECT
    e.name,
    e.default_version,
    e.installed_version
FROM pg_catalog.pg_available_extensions AS e
WHERE e.name = 'btree_gist';

-- Append-only domain ledger. Corrections are new reversal/correction entries.
CREATE TABLE pro_temporal_lab.change_ledger (
    ledger_entry_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject_key text NOT NULL,
    event_kind text NOT NULL,
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL,
    payload jsonb NOT NULL CHECK (jsonb_typeof(payload) = 'object'),
    idempotency_key text NOT NULL UNIQUE,
    reverses_entry_id bigint
        REFERENCES pro_temporal_lab.change_ledger (ledger_entry_id)
);

CREATE FUNCTION pro_temporal_lab.reject_ledger_mutation()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
BEGIN
    RAISE EXCEPTION 'change ledger is append-only; write a reversal/correction'
        USING ERRCODE = 'check_violation';
END
$function$;

CREATE TRIGGER change_ledger_immutable
BEFORE UPDATE OR DELETE ON pro_temporal_lab.change_ledger
FOR EACH ROW
EXECUTE FUNCTION pro_temporal_lab.reject_ledger_mutation();

INSERT INTO pro_temporal_lab.change_ledger (
    subject_key,
    event_kind,
    effective_at,
    recorded_at,
    payload,
    idempotency_key
)
VALUES (
    'CUS-100',
    'credit.applied',
    TIMESTAMPTZ '2026-03-01 00:00:00+00',
    TIMESTAMPTZ '2026-03-01 00:01:00+00',
    '{"amount":"5.00","currency":"USD"}',
    'LEDGER-100'
);

INSERT INTO pro_temporal_lab.change_ledger (
    subject_key,
    event_kind,
    effective_at,
    recorded_at,
    payload,
    idempotency_key,
    reverses_entry_id
)
SELECT
    l.subject_key,
    'credit.reversed',
    TIMESTAMPTZ '2026-03-02 00:00:00+00',
    TIMESTAMPTZ '2026-03-02 00:01:00+00',
    '{"amount":"-5.00","currency":"USD"}',
    'LEDGER-101',
    l.ledger_entry_id
FROM pro_temporal_lab.change_ledger AS l
WHERE l.idempotency_key = 'LEDGER-100';

DO $expected_immutability$
BEGIN
    BEGIN
        UPDATE pro_temporal_lab.change_ledger
        SET payload = '{"amount":"0.00","currency":"USD"}'
        WHERE idempotency_key = 'LEDGER-100';
        RAISE EXCEPTION 'ledger mutation unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected append-only rejection: %', SQLERRM;
    END;
END
$expected_immutability$;

CREATE TABLE pro_temporal_lab.retention_classes (
    retention_class text PRIMARY KEY,
    minimum_retention interval NOT NULL,
    policy_basis text NOT NULL
);

CREATE TABLE pro_temporal_lab.retained_records (
    record_key text PRIMARY KEY,
    retention_class text NOT NULL
        REFERENCES pro_temporal_lab.retention_classes (retention_class),
    created_at timestamptz NOT NULL,
    legal_hold boolean NOT NULL DEFAULT false,
    deleted_at timestamptz
);

INSERT INTO pro_temporal_lab.retention_classes
VALUES
    ('operational-30d', INTERVAL '30 days', 'approved operational policy'),
    ('audit-365d', INTERVAL '365 days', 'approved audit policy');

INSERT INTO pro_temporal_lab.retained_records
VALUES
    ('REC-100', 'operational-30d', TIMESTAMPTZ '2026-01-01 00:00:00+00', false, NULL),
    ('REC-101', 'operational-30d', TIMESTAMPTZ '2026-01-01 00:00:00+00', true, NULL),
    ('REC-102', 'audit-365d', TIMESTAMPTZ '2026-01-01 00:00:00+00', false, NULL);

\echo 'Eligibility report only: policy approval precedes any deletion'
SELECT
    rr.record_key,
    rr.retention_class,
    rr.created_at,
    rc.minimum_retention,
    rr.legal_hold,
    (
        NOT rr.legal_hold
        AND rr.deleted_at IS NULL
        AND TIMESTAMPTZ '2026-03-15 00:00:00+00'
            >= rr.created_at + rc.minimum_retention
    ) AS eligible_for_review
FROM pro_temporal_lab.retained_records AS rr
JOIN pro_temporal_lab.retention_classes AS rc
  ON rc.retention_class = rr.retention_class
ORDER BY rr.record_key;

-- Exercises:
--
-- 1. Add a retroactive valid-time correction recorded April 1. Query the value
--    valid February 15 as known March 15 versus as known April 2.
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Test facts exactly at every valid/system upper boundary. Prove [lower,upper)
--    gives at most one current match.
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 3. If btree_gist is already approved in an isolated environment, write (do
--    not run here) an exclusion constraint for customer_key equality and current
--    valid-period overlap. Compare it with the advisory-lock trigger fallback.
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 4. Add a correction ledger entry that reverses LEDGER-101 without updating
--    history. Verify idempotency keys and reversal references.
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 5. Add a retention exception/hold release workflow with approver, reason,
--    decision time, and immutable audit. Do not auto-delete fixture rows.
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 6. State domain assumptions: time zone, clock authority, late arrival,
--    overlap/gap policy, deletion/anonymization, ledger meaning, and who may
--    correct system history.
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 7. Model a local-time business rule across a daylight-saving transition.
--    Store the source zone and UTC instant, test ambiguous/nonexistent local
--    times, and explain why a bare timestamp or fixed UTC offset is insufficient.
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 8. Distinguish event time, ingestion time, and processing time for late data.
--    Define a watermark and allowed lateness, then show how a late event changes
--    a previously published aggregate and how the correction is communicated.
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 9. Implement a Type-2 dimension as-of join with surrogate key, business key,
--    effective half-open range, current marker, and correction metadata. Prove
--    every fact resolves to at most one dimension row.
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 10. Design temporal referential integrity when a child period must be
--     contained by a parent period. Compare trigger/exclusion approaches,
--     concurrency locking, deferred validation, and repair of historical gaps.
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 11. Produce a deterministic gap-and-overlap report per business key using
--     lag/lead and multirange operations. Define whether adjacency is valid and
--     fail on duplicate or empty periods.
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 12. Plan time-based partition archival without violating legal holds.
--     Inventory cross-partition keys, indexes, detach/archive/verify steps,
--     encryption and access, hold exceptions, restore tests, and deletion proof.

DO $self_check$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM pro_temporal_lab.customer_terms AS ct
        WHERE ct.customer_key = 'CUS-100'
          AND ct.valid_period @> DATE '2026-02-15'
          AND ct.system_period @> TIMESTAMPTZ '2026-03-15 00:00:00+00'
    ) <> 1 THEN
        RAISE EXCEPTION 'bitemporal as-of query is not single-valued';
    END IF;

    IF (SELECT COUNT(*) FROM pro_temporal_lab.change_ledger) <> 2 THEN
        RAISE EXCEPTION 'append-only ledger count drifted';
    END IF;
END
$self_check$;
--    Inputs: Use only the declared lesson objects (pro_temporal_lab.customer_terms, pro_temporal_lab.global_maintenance_windows, pg_catalog.pg_available_extensions, pro_temporal_lab.change_ledger, pro_temporal_lab.retention_classes) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.

ROLLBACK;
\echo 'SQL-TEMPORAL-01 complete: pro_temporal_lab was rolled back'
