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
    payload jsonb NOT NULL CHECK (
        jsonb_typeof(payload) = 'object'
        AND payload ? 'amount'
        AND payload ? 'currency'
        AND payload ->> 'amount' ~ '^-?[0-9]+([.][0-9]{1,2})?$'
    ),
    idempotency_key text NOT NULL UNIQUE,
    reverses_entry_id bigint UNIQUE
        REFERENCES pro_temporal_lab.change_ledger (ledger_entry_id)
);

CREATE FUNCTION pro_temporal_lab.validate_ledger_reversal()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
DECLARE
    prior_entry pro_temporal_lab.change_ledger%ROWTYPE;
BEGIN
    IF NEW.reverses_entry_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT prior.*
    INTO prior_entry
    FROM pro_temporal_lab.change_ledger AS prior
    WHERE prior.ledger_entry_id = NEW.reverses_entry_id
    FOR KEY SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'reversed ledger entry % does not exist',
            NEW.reverses_entry_id
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    IF NEW.subject_key IS DISTINCT FROM prior_entry.subject_key
       OR NEW.payload ->> 'currency'
          IS DISTINCT FROM prior_entry.payload ->> 'currency'
       OR (NEW.payload ->> 'amount')::numeric
          + (prior_entry.payload ->> 'amount')::numeric <> 0 THEN
        RAISE EXCEPTION
            'a reversal must negate the same subject and currency'
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END
$function$;

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

CREATE TRIGGER change_ledger_validate_reversal
BEFORE INSERT ON pro_temporal_lab.change_ledger
FOR EACH ROW
EXECUTE FUNCTION pro_temporal_lab.validate_ledger_reversal();

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

DO $expected_delete_and_retry_rejections$
BEGIN
    BEGIN
        DELETE FROM pro_temporal_lab.change_ledger
        WHERE idempotency_key = 'LEDGER-100';
        RAISE EXCEPTION 'ledger deletion unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected append-only DELETE rejection';
    END;

    BEGIN
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
        RAISE EXCEPTION 'duplicate idempotency key unexpectedly succeeded';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Expected idempotent-retry rejection';
    END;
END
$expected_delete_and_retry_rejections$;

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
--    Inputs: For sql-temporal-01 Exercise 1, Close only the current `CUS-100` row whose `valid_period` contains `2026-02-15` at system time `2026-04-01 00:00+00`, then append the corrected rate as a new current `pro_temporal_lab.customer_terms` row.
--    Expected result/shape: For sql-temporal-01 Exercise 1, One row per `(valid_on, system_as_of)` probe, with `valid_on`, `system_as_of`, `term_version_id`, `monthly_rate`, and `recorded_reason`, ordered by `system_as_of`; March 15 returns the prior rate and April 2 returns the retroactive correction.
--    Verify: For sql-temporal-01 Exercise 1, Group the as-of join by both probe columns and require exactly one match per probe. Prove the earlier system-period row still exists and that no current valid periods overlap for `CUS-100`.
-- 2. Test facts exactly at every valid/system upper boundary. Prove [lower,upper)
--    gives at most one current match.
--    Inputs: For sql-temporal-01 Exercise 2, Build an inline probe relation around every lower and upper bound in `pro_temporal_lab.customer_terms`: immediately before, exactly at, and immediately after each valid-date or system-time boundary.
--    Expected result/shape: For sql-temporal-01 Exercise 2, One row per `probe_id`, with `valid_on`, `known_at`, `matching_versions`, and `expected_matches`, ordered by `probe_id`; no `matching_versions` value is greater than one.
--    Verify: For sql-temporal-01 Exercise 2, Independently count matching `term_version_id` values for every probe. Require the old version to stop at the upper bound and an adjacent successor, when present, to begin there without a double match.
-- 3. If btree_gist is already approved in an isolated environment, write (do
--    not run here) an exclusion constraint for customer_key equality and current
--    valid-period overlap. Compare it with the advisory-lock trigger fallback.
--    Inputs: For sql-temporal-01 Exercise 3, Use the read-only `pg_available_extensions` result, the existing advisory-lock trigger, and a written (not executed) `btree_gist` exclusion constraint design for `customer_key WITH =, valid_period WITH &&`.
--    Expected result/shape: For sql-temporal-01 Exercise 3, One comparison row per enforcement approach, with `approach`, `enforcement_mechanism`, `assumption_or_limit`, and `concurrent_failure_behavior`.
--    Verify: For sql-temporal-01 Exercise 3, The comparison output records which writes each approach locks or constrains, how a conflicting concurrent transaction fails, and what happens if an application writer bypasses the agreed advisory-lock protocol.
-- 4. Add a correction ledger entry that reverses LEDGER-101 without updating
--    history. Verify idempotency keys and reversal references.
--    Inputs: For sql-temporal-01 Exercise 4, Append `LEDGER-102` to `pro_temporal_lab.change_ledger` as the exact same-subject, same-currency negation of `LEDGER-101`; set `reverses_entry_id` from the referenced row instead of hard-coding it.
--    Expected result/shape: For sql-temporal-01 Exercise 4, One row per `ledger_entry_id`, with `idempotency_key`, `event_kind`, signed amount, `reverses_entry_id`, and a scalar reconciled amount, ordered by `ledger_entry_id`.
--    Verify: For sql-temporal-01 Exercise 4, Require three rows and a reconciled amount of `5.00`. Prove an UPDATE, DELETE, duplicate `LEDGER-102` retry, second reversal of the same entry, and wrong-sign reversal all fail without changing the row count.
-- 5. Add a retention exception/hold release workflow with approver, reason,
--    decision time, and immutable audit. Do not auto-delete fixture rows.
--    Inputs: For sql-temporal-01 Exercise 5, Create append-only `pro_temporal_lab.retention_decisions` with a stable decision idempotency key, `record_key`, decision, approver, reason, and authoritative `decided_at`. Lock per record and reject backdated decisions or a deletion approval while the latest decision is a hold.
--    Expected result/shape: For sql-temporal-01 Exercise 5, One row per retained `record_key`, with the latest decision event/key, approver, reason, decision time, and `eligible_for_deletion_review`, ordered by `record_key`.
--    Verify: For sql-temporal-01 Exercise 5, Prove decision UPDATE/DELETE and duplicate/backdated appends fail. Keep a held fixture ineligible, release another through an ordered event, and confirm no `retained_records` row is actually deleted.
-- 6. State domain assumptions: time zone, clock authority, late arrival,
--    overlap/gap policy, deletion/anonymization, ledger meaning, and who may
--    correct system history.
--    Inputs: For sql-temporal-01 Exercise 6, Use observed lesson behavior plus explicitly labeled assumptions for time zone, clock authority, lateness, overlap/gaps, correction authority, ledger units, retention/holds, and replicas/backups.
--    Expected result/shape: For sql-temporal-01 Exercise 6, One row per assumption topic, with `topic`, `decision_or_assumption`, `evidence`, `owner`, and `failure_response`.
--    Verify: For sql-temporal-01 Exercise 6, Every row names an accountable owner and an operational response; every claimed fact cites a query/catalog result, while policy not present in the repository is labeled as an assumption needing approval.
-- 7. Model a local-time business rule across a daylight-saving transition.
--    Store the source zone and UTC instant, test ambiguous/nonexistent local
--    times, and explain why a bare timestamp or fixed UTC offset is insufficient.
--    Inputs: For sql-temporal-01 Exercise 7, Use three keyed civil-time cases in `America/Los_Angeles`: spring `2026-03-08 02:30`, fall `2026-11-01 01:30`, and one ordinary time. Round-trip candidate UTC instants rather than trusting one silent `AT TIME ZONE` default.
--    Expected result/shape: For sql-temporal-01 Exercise 7, One row per `case_id`, with `local_time`, `zone_name`, `civil_time_status`, candidate instants, PostgreSQL's default interpreted instant, and `resolution_policy`, ordered by `case_id`.
--    Verify: For sql-temporal-01 Exercise 7, The result contains exactly one `nonexistent`, one `ambiguous`, and one `ordinary` case. A nonexistent time has zero round-trip candidates; an ambiguous time has more than one and requires explicit disambiguation.
-- 8. Distinguish event time, ingestion time, and processing time for late data.
--    Define a watermark and allowed lateness, then show how a late event changes
--    a previously published aggregate and how the correction is communicated.
--    Inputs: For sql-temporal-01 Exercise 8, Create `pro_temporal_lab.timed_events(event_key, event_at, ingested_at, processed_at)` with one on-time and one late event. Use a fixed 15-minute example lateness allowance.
--    Expected result/shape: For sql-temporal-01 Exercise 8, Exactly one summary row with `event_count`, `maximum_event_time`, `example_watermark`, `maximum_arrival_delay`, `maximum_processing_delay`, `events_behind_watermark`, and the correction policy.
--    Verify: For sql-temporal-01 Exercise 8, Recompute arrival and processing delays row by row, require the late fixture to fall behind the watermark, and describe a stable window/version identity for the corrected aggregate.
-- 9. Implement a Type-2 dimension as-of join with surrogate key, business key,
--    effective half-open range, current marker, and correction metadata. Prove
--    every fact resolves to at most one dimension row.
--    Inputs: For sql-temporal-01 Exercise 9, Create `pro_temporal_lab.customer_dimension` with surrogate `customer_version_id`, business key, half-open `effective_period`, `is_current`, segment, correction reason, and record time; join `pro_temporal_lab.order_facts` on business key plus range containment.
--    Expected result/shape: For sql-temporal-01 Exercise 9, One row per `order_key`, with `ordered_on`, `customer_version_id`, segment, effective period, current marker, and correction metadata, ordered by `order_key`.
--    Verify: For sql-temporal-01 Exercise 9, Require output count to equal fact count and group by `order_key` with `HAVING count(customer_version_id) > 1` returning no rows. Inject one overlapping dimension row, prove the diagnostic catches it, then roll it back.
-- 10. Design temporal referential integrity when a child period must be
--     contained by a parent period. Compare trigger/exclusion approaches,
--     concurrency locking, deferred validation, and repair of historical gaps.
--    Inputs: For sql-temporal-01 Exercise 10, Cover child insert/update, parent shrink/delete, bulk historical repair, and deferred validation. State the shared business-key locking namespace and containment predicate for each write path.
--    Expected result/shape: For sql-temporal-01 Exercise 10, One row per write path, with `write_path`, `concurrency_or_validation_control`, and `failure_response`.
--    Verify: For sql-temporal-01 Exercise 10, Walk through two concurrent transactions for both child insertion and parent shrink. Identify the lock acquired first and show that cutover is blocked whenever the final containment diagnostic is nonempty.
-- 11. Produce a deterministic gap-and-overlap report per business key using
--     lag/lead and multirange operations. Define whether adjacency is valid and
--     fail on duplicate or empty periods.
--    Inputs: For sql-temporal-01 Exercise 11, Use keyed fixtures containing duplicate, overlapping, adjacent, gapped, empty, and unbounded-upper `daterange` values. Preserve unbounded prior coverage with `upper_inf()` or an explicit infinity sentinel.
--    Expected result/shape: For sql-temporal-01 Exercise 11, One row per `period_id`, with `business_key`, `valid_period`, `has_unbounded_upper`, duplicate count, prior maximum upper bound, and `relationship_to_prior_coverage`, ordered by bounds and `period_id`.
--    Verify: For sql-temporal-01 Exercise 11, Require explicit `duplicate`, `empty`, `gap`, `adjacent`, and `overlap` outcomes. Add a bounded period after an unbounded range and prove it is classified as overlap rather than first/gap.
-- 12. Plan time-based partition archival without violating legal holds.
--     Inventory cross-partition keys, indexes, detach/archive/verify steps,
--     encryption and access, hold exceptions, restore tests, and deletion proof.
--    Inputs: For sql-temporal-01 Exercise 12, Design ordered phases for inventory, hold gate, detach, encrypted archive, reconciliation, restore test, and eventual source deletion.
--    Expected result/shape: For sql-temporal-01 Exercise 12, One row per `step_number`, with `phase`, `required_control`, and `required_evidence`, ordered by `step_number`.
--    Verify: For sql-temporal-01 Exercise 12, Each phase names a stop condition. Trace one active-hold fixture through every maintained copy and require a successful isolated restore plus source/archive count and checksum reconciliation before deletion.

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

ROLLBACK;
\echo 'SQL-TEMPORAL-01 complete: pro_temporal_lab was rolled back'
