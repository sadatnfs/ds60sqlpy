-- SQL-TEMPORAL-01 executable solutions
-- SOLUTION READING MAP — sql-temporal-01: Temporal and Domain Modelling
-- Explanation: sql/professional/solutions/sql_temporal_01_domain_modelling_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_temporal_01_domain_modelling_solutions.sql
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
CREATE SCHEMA pro_temporal_lab;

CREATE TABLE pro_temporal_lab.customer_terms (
    term_version_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_key text NOT NULL,
    valid_period daterange NOT NULL,
    system_period tstzrange NOT NULL,
    monthly_rate numeric(10, 2) NOT NULL CHECK (monthly_rate >= 0),
    recorded_reason text NOT NULL CHECK (btrim(recorded_reason) <> ''),
    CHECK (NOT isempty(valid_period)),
    CHECK (NOT isempty(system_period))
);

-- Initial and March correction.
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
        tstzrange(
            TIMESTAMPTZ '2026-03-01 00:00+00',
            TIMESTAMPTZ '2026-03-10 00:00+00',
            '[)'
        ),
        10.00,
        'initial value'
    ),
    (
        'CUS-100',
        daterange(DATE '2026-01-01', DATE '2026-04-01', '[)'),
        tstzrange(
            TIMESTAMPTZ '2026-03-10 00:00+00',
            TIMESTAMPTZ '2026-04-01 00:00+00',
            '[)'
        ),
        12.00,
        'March correction'
    ),
    -- Exercise 1: retroactive correction recorded April 1.
    (
        'CUS-100',
        daterange(DATE '2026-01-01', DATE '2026-04-01', '[)'),
        tstzrange(TIMESTAMPTZ '2026-04-01 00:00+00', NULL, '[)'),
        11.00,
        'retroactive correction recorded April 1'
    );

SELECT
    DATE '2026-02-15' AS valid_on,
    query.system_as_of,
    f.term_version_id,
    f.monthly_rate,
    f.recorded_reason
FROM (
    VALUES
        (TIMESTAMPTZ '2026-03-15 00:00+00'),
        (TIMESTAMPTZ '2026-04-02 00:00+00')
) AS query(system_as_of)
JOIN pro_temporal_lab.customer_terms AS f
  ON f.customer_key = 'CUS-100'
 AND f.valid_period @> DATE '2026-02-15'
 AND f.system_period @> query.system_as_of
ORDER BY query.system_as_of;

-- Exercise 4: immutable ledger and reversal of a reversal. A reversal must
-- negate exactly one prior entry, and each entry may be reversed only once.
CREATE TABLE pro_temporal_lab.ledger (
    entry_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject_key text NOT NULL,
    idempotency_key text NOT NULL UNIQUE,
    event_kind text NOT NULL,
    amount numeric(12, 2) NOT NULL,
    currency text NOT NULL CHECK (currency ~ '^[A-Z]{3}$'),
    reverses_entry_id bigint UNIQUE
        REFERENCES pro_temporal_lab.ledger (entry_id)
);

CREATE FUNCTION pro_temporal_lab.validate_ledger_append()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
DECLARE
    reversed_amount numeric(12, 2);
    reversed_subject_key text;
    reversed_currency text;
BEGIN
    IF NEW.reverses_entry_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT l.amount, l.subject_key, l.currency
    INTO reversed_amount, reversed_subject_key, reversed_currency
    FROM pro_temporal_lab.ledger AS l
    WHERE l.entry_id = NEW.reverses_entry_id
    FOR KEY SHARE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'reversed ledger entry % does not exist',
            NEW.reverses_entry_id
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    IF NEW.subject_key IS DISTINCT FROM reversed_subject_key
       OR NEW.currency IS DISTINCT FROM reversed_currency
       OR NEW.amount + reversed_amount <> 0 THEN
        RAISE EXCEPTION
            'reversal must negate prior amount % for the same subject/currency',
            reversed_amount
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
    RAISE EXCEPTION
        'ledger is append-only; append a reversal instead of changing history'
        USING ERRCODE = 'check_violation';
END
$function$;

CREATE TRIGGER ledger_validate_append
BEFORE INSERT ON pro_temporal_lab.ledger
FOR EACH ROW
EXECUTE FUNCTION pro_temporal_lab.validate_ledger_append();

CREATE TRIGGER ledger_immutable
BEFORE UPDATE OR DELETE ON pro_temporal_lab.ledger
FOR EACH ROW
EXECUTE FUNCTION pro_temporal_lab.reject_ledger_mutation();

-- The learner uses the domain name `change_ledger`; this automatically
-- updatable view exposes that name and the more descriptive identity column
-- while the base table retains the focused immutability trigger used below.
CREATE VIEW pro_temporal_lab.change_ledger AS
SELECT
    l.entry_id AS ledger_entry_id,
    l.subject_key,
    l.idempotency_key,
    l.event_kind,
    l.amount,
    l.currency,
    l.reverses_entry_id
FROM pro_temporal_lab.ledger AS l;

INSERT INTO pro_temporal_lab.change_ledger (
    subject_key, idempotency_key, event_kind, amount, currency
)
VALUES ('CUS-100', 'LEDGER-100', 'credit', 5.00, 'USD');

INSERT INTO pro_temporal_lab.change_ledger (
    subject_key,
    idempotency_key,
    event_kind,
    amount,
    currency,
    reverses_entry_id
)
SELECT
    l.subject_key,
    'LEDGER-101',
    'credit.reversal',
    -5.00,
    l.currency,
    l.ledger_entry_id
FROM pro_temporal_lab.change_ledger AS l
WHERE l.idempotency_key = 'LEDGER-100';

INSERT INTO pro_temporal_lab.change_ledger (
    subject_key,
    idempotency_key,
    event_kind,
    amount,
    currency,
    reverses_entry_id
)
SELECT
    l.subject_key,
    'LEDGER-102',
    'reversal.corrected',
    5.00,
    l.currency,
    l.ledger_entry_id
FROM pro_temporal_lab.change_ledger AS l
WHERE l.idempotency_key = 'LEDGER-101';

-- These negative controls prove the guarantees, rather than merely describing
-- them. Each inner block rolls back its failed statement automatically.
DO $ledger_negative_controls$
BEGIN
    BEGIN
        UPDATE pro_temporal_lab.change_ledger
        SET amount = 0
        WHERE idempotency_key = 'LEDGER-100';
        RAISE EXCEPTION 'ledger UPDATE unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected immutable-ledger UPDATE rejection';
    END;

    BEGIN
        DELETE FROM pro_temporal_lab.change_ledger
        WHERE idempotency_key = 'LEDGER-100';
        RAISE EXCEPTION 'ledger DELETE unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected immutable-ledger DELETE rejection';
    END;

    BEGIN
        INSERT INTO pro_temporal_lab.change_ledger (
            subject_key, idempotency_key, event_kind, amount, currency
        )
        VALUES (
            'CUS-100',
            'LEDGER-100',
            'duplicate.retry',
            5.00,
            'USD'
        );
        RAISE EXCEPTION 'duplicate idempotency key unexpectedly succeeded';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Expected duplicate idempotency-key rejection';
    END;

    BEGIN
        INSERT INTO pro_temporal_lab.change_ledger (
            subject_key,
            idempotency_key,
            event_kind,
            amount,
            currency,
            reverses_entry_id
        )
        SELECT
            l.subject_key,
            'LEDGER-BAD',
            'invalid.reversal',
            -4.00,
            l.currency,
            l.ledger_entry_id
        FROM pro_temporal_lab.change_ledger AS l
        WHERE l.idempotency_key = 'LEDGER-102';
        RAISE EXCEPTION 'invalid reversal amount unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected invalid reversal-amount rejection';
    END;
END
$ledger_negative_controls$;

SELECT
    l.ledger_entry_id,
    l.subject_key,
    l.idempotency_key,
    l.event_kind,
    l.amount,
    l.currency,
    l.reverses_entry_id
FROM pro_temporal_lab.change_ledger AS l
ORDER BY l.ledger_entry_id;

-- Exercise 5: immutable, idempotent decision log for hold release/review.
-- Eligibility remains a report; no fixture row is physically deleted.
CREATE TABLE pro_temporal_lab.retained_subjects (
    record_key text PRIMARY KEY,
    minimum_delete_at timestamptz NOT NULL
);

INSERT INTO pro_temporal_lab.retained_subjects
VALUES
    ('REC-1', TIMESTAMPTZ '2026-02-15 00:00+00'),
    ('REC-2', TIMESTAMPTZ '2026-02-15 00:00+00');

CREATE TABLE pro_temporal_lab.retention_decisions (
    decision_event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    decision_idempotency_key text NOT NULL UNIQUE,
    record_key text NOT NULL
        REFERENCES pro_temporal_lab.retained_subjects (record_key),
    decision text NOT NULL CHECK (
        decision IN ('hold_applied', 'hold_released', 'deletion_approved')
    ),
    approved_by text NOT NULL CHECK (btrim(approved_by) <> ''),
    reason text NOT NULL CHECK (btrim(reason) <> ''),
    decided_at timestamptz NOT NULL
);

CREATE FUNCTION pro_temporal_lab.validate_retention_decision()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
DECLARE
    previous_decision text;
    previous_decided_at timestamptz;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtextextended(NEW.record_key, 0));

    SELECT rd.decision, rd.decided_at
    INTO previous_decision, previous_decided_at
    FROM pro_temporal_lab.retention_decisions AS rd
    WHERE rd.record_key = NEW.record_key
    ORDER BY rd.decided_at DESC, rd.decision_event_id DESC
    LIMIT 1;

    IF previous_decided_at IS NOT NULL
       AND NEW.decided_at <= previous_decided_at THEN
        RAISE EXCEPTION
            'decision time % must be later than prior decision time %',
            NEW.decided_at,
            previous_decided_at
            USING ERRCODE = 'check_violation';
    END IF;

    IF NEW.decision = 'hold_released'
       AND previous_decision IS DISTINCT FROM 'hold_applied' THEN
        RAISE EXCEPTION 'hold release requires an active hold'
            USING ERRCODE = 'check_violation';
    END IF;

    IF NEW.decision = 'deletion_approved'
       AND previous_decision IS DISTINCT FROM 'hold_released' THEN
        RAISE EXCEPTION 'deletion approval requires a recorded hold release'
            USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END
$function$;

CREATE FUNCTION pro_temporal_lab.reject_retention_decision_mutation()
RETURNS trigger
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = pg_catalog
AS $function$
BEGIN
    RAISE EXCEPTION
        'retention decisions are append-only; append a new decision event'
        USING ERRCODE = 'check_violation';
END
$function$;

CREATE TRIGGER retention_decision_validate_append
BEFORE INSERT ON pro_temporal_lab.retention_decisions
FOR EACH ROW
EXECUTE FUNCTION pro_temporal_lab.validate_retention_decision();

CREATE TRIGGER retention_decisions_immutable
BEFORE UPDATE OR DELETE ON pro_temporal_lab.retention_decisions
FOR EACH ROW
EXECUTE FUNCTION pro_temporal_lab.reject_retention_decision_mutation();

INSERT INTO pro_temporal_lab.retention_decisions (
    decision_idempotency_key,
    record_key,
    decision,
    approved_by,
    reason,
    decided_at
)
VALUES
    (
        'DEC-REC-1-HOLD',
        'REC-1',
        'hold_applied',
        'policy-reviewer',
        'active review',
        TIMESTAMPTZ '2026-02-01 00:00+00'
    ),
    (
        'DEC-REC-1-RELEASE',
        'REC-1',
        'hold_released',
        'policy-reviewer',
        'review completed',
        TIMESTAMPTZ '2026-03-01 00:00+00'
    ),
    (
        'DEC-REC-2-HOLD',
        'REC-2',
        'hold_applied',
        'policy-reviewer',
        'active investigation',
        TIMESTAMPTZ '2026-02-10 00:00+00'
    );

DO $retention_negative_controls$
BEGIN
    BEGIN
        INSERT INTO pro_temporal_lab.retention_decisions (
            decision_idempotency_key,
            record_key,
            decision,
            approved_by,
            reason,
            decided_at
        )
        VALUES (
            'DEC-REC-1-HOLD',
            'REC-1',
            'hold_applied',
            'retrying-client',
            'duplicate retry',
            TIMESTAMPTZ '2026-04-01 00:00+00'
        );
        RAISE EXCEPTION 'duplicate decision retry unexpectedly succeeded';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'Expected duplicate decision-key rejection';
    END;

    BEGIN
        UPDATE pro_temporal_lab.retention_decisions
        SET reason = 'rewritten history'
        WHERE decision_idempotency_key = 'DEC-REC-1-HOLD';
        RAISE EXCEPTION 'retention-decision UPDATE unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected immutable-decision rejection';
    END;

    BEGIN
        DELETE FROM pro_temporal_lab.retention_decisions
        WHERE decision_idempotency_key = 'DEC-REC-1-HOLD';
        RAISE EXCEPTION 'retention-decision DELETE unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected immutable-decision DELETE rejection';
    END;

    BEGIN
        INSERT INTO pro_temporal_lab.retention_decisions (
            decision_idempotency_key,
            record_key,
            decision,
            approved_by,
            reason,
            decided_at
        )
        VALUES (
            'DEC-REC-1-BACKDATED',
            'REC-1',
            'hold_applied',
            'policy-reviewer',
            'must fail because chronology is append ordered',
            TIMESTAMPTZ '2026-02-15 00:00+00'
        );
        RAISE EXCEPTION 'backdated decision unexpectedly succeeded';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected backdated-decision rejection';
    END;

    BEGIN
        INSERT INTO pro_temporal_lab.retention_decisions (
            decision_idempotency_key,
            record_key,
            decision,
            approved_by,
            reason,
            decided_at
        )
        VALUES (
            'DEC-REC-2-DELETE',
            'REC-2',
            'deletion_approved',
            'policy-reviewer',
            'must fail while hold remains active',
            TIMESTAMPTZ '2026-03-02 00:00+00'
        );
        RAISE EXCEPTION 'held record was approved for deletion';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'Expected active-hold protection';
    END;
END
$retention_negative_controls$;

WITH latest_decision AS (
    SELECT DISTINCT ON (rd.record_key)
        rd.record_key,
        rd.decision_event_id,
        rd.decision_idempotency_key,
        rd.decision,
        rd.approved_by,
        rd.reason,
        rd.decided_at
    FROM pro_temporal_lab.retention_decisions AS rd
    ORDER BY rd.record_key, rd.decided_at DESC, rd.decision_event_id DESC
)
SELECT
    rs.record_key,
    latest.decision_event_id,
    latest.decision_idempotency_key,
    latest.decision AS latest_decision,
    latest.approved_by,
    latest.reason,
    latest.decided_at,
    (
        TIMESTAMPTZ '2026-03-15 00:00+00' >= rs.minimum_delete_at
        AND latest.decision <> 'hold_applied'
    ) AS eligible_for_deletion_review
FROM pro_temporal_lab.retained_subjects AS rs
LEFT JOIN latest_decision AS latest
  ON latest.record_key = rs.record_key
ORDER BY rs.record_key;

DO $solution$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM pro_temporal_lab.customer_terms AS f
        WHERE f.valid_period @> DATE '2026-02-15'
          AND f.system_period @> TIMESTAMPTZ '2026-04-02 00:00+00'
    ) <> 1 THEN
        RAISE EXCEPTION 'retroactive as-of result is not single-valued';
    END IF;

    IF (SELECT COUNT(*) FROM pro_temporal_lab.ledger) <> 3
       OR (SELECT SUM(l.amount) FROM pro_temporal_lab.ledger AS l) <> 5.00 THEN
        RAISE EXCEPTION 'ledger reversal chain does not reconcile';
    END IF;

    IF (
        SELECT COUNT(*)
        FROM pro_temporal_lab.retention_decisions
    ) <> 3 THEN
        RAISE EXCEPTION 'retention decision log drifted';
    END IF;
END
$solution$;

-- Exercise 2: probe immediately before and exactly at both upper bounds.
-- Half-open [lower, upper) means the old version stops matching at the upper
-- instant; an adjacent successor starts there without double matching.
WITH probes(probe_id, valid_on, known_at, expected_matches) AS (
    VALUES
        (
            'valid-before-upper',
            DATE '2026-03-31',
            TIMESTAMPTZ '2026-04-02 00:00+00',
            1::bigint
        ),
        (
            'valid-at-upper',
            DATE '2026-04-01',
            TIMESTAMPTZ '2026-04-02 00:00+00',
            0::bigint
        ),
        (
            'system-before-march-boundary',
            DATE '2026-02-15',
            TIMESTAMPTZ '2026-03-09 23:59:59+00',
            1::bigint
        ),
        (
            'system-at-march-boundary',
            DATE '2026-02-15',
            TIMESTAMPTZ '2026-03-10 00:00:00+00',
            1::bigint
        ),
        (
            'system-before-april-boundary',
            DATE '2026-02-15',
            TIMESTAMPTZ '2026-03-31 23:59:59+00',
            1::bigint
        ),
        (
            'system-at-april-boundary',
            DATE '2026-02-15',
            TIMESTAMPTZ '2026-04-01 00:00:00+00',
            1::bigint
        )
)
SELECT
    p.probe_id,
    p.valid_on,
    p.known_at,
    COUNT(f.term_version_id) AS matching_versions,
    p.expected_matches,
    COUNT(f.term_version_id) = p.expected_matches AS matches_expectation
FROM probes AS p
LEFT JOIN pro_temporal_lab.customer_terms AS f
  ON f.customer_key = 'CUS-100'
 AND f.valid_period @> p.valid_on
 AND f.system_period @> p.known_at
GROUP BY p.probe_id, p.valid_on, p.known_at, p.expected_matches
ORDER BY p.probe_id;

DO $boundary_invariant$
BEGIN
    IF EXISTS (
        WITH probes(valid_on, known_at, expected_matches) AS (
            VALUES
                (
                    DATE '2026-03-31',
                    TIMESTAMPTZ '2026-04-02 00:00+00',
                    1::bigint
                ),
                (
                    DATE '2026-04-01',
                    TIMESTAMPTZ '2026-04-02 00:00+00',
                    0::bigint
                ),
                (
                    DATE '2026-02-15',
                    TIMESTAMPTZ '2026-03-10 00:00+00',
                    1::bigint
                ),
                (
                    DATE '2026-02-15',
                    TIMESTAMPTZ '2026-04-01 00:00+00',
                    1::bigint
                )
        ),
        observed AS (
            SELECT
                p.valid_on,
                p.known_at,
                p.expected_matches,
                COUNT(f.term_version_id) AS matching_versions
            FROM probes AS p
            LEFT JOIN pro_temporal_lab.customer_terms AS f
              ON f.customer_key = 'CUS-100'
             AND f.valid_period @> p.valid_on
             AND f.system_period @> p.known_at
            GROUP BY p.valid_on, p.known_at, p.expected_matches
        )
        SELECT 1
        FROM observed AS o
        WHERE o.matching_versions <> o.expected_matches
           OR o.matching_versions > 1
    ) THEN
        RAISE EXCEPTION 'half-open boundary invariant failed';
    END IF;
END
$boundary_invariant$;

-- Exercise 3: an approved btree_gist exclusion constraint can reject current
-- period overlap under concurrency. The fallback must lock one stable business
-- key before checking; this core solution installs no extension.
SELECT *
FROM (
    VALUES
        (
            1,
            'btree_gist exclusion constraint',
            'declarative equality on customer_key plus && on valid_period',
            'requires approved extension and applies to the represented rows',
            'database constraint handles concurrent conflicting writes'
        ),
        (
            2,
            'advisory-lock trigger fallback',
            'lock hash(customer_key), then test current rows for overlap',
            'all writers must use the same stable lock protocol',
            'trigger raises exclusion_violation before the write'
        )
) AS enforcement_comparison(
    approach_number,
    approach,
    enforcement_mechanism,
    assumption_or_limit,
    concurrent_failure_behavior
)
ORDER BY approach_number;

-- Exercise 6: domain assumptions include zone/clock authority, half-open bounds,
-- lateness, overlap/gap, correction authority, identity, unit/ledger semantics,
-- retention/hold/deletion, and replica/backup treatment.
SELECT *
FROM (
    VALUES
        (
            1,
            'time zone',
            'store authoritative instants as timestamptz and retain IANA source zone',
            'domain owner',
            'reject unclassified ambiguous/nonexistent civil time'
        ),
        (
            2,
            'clock authority',
            'source event time is business time; database clock is record time',
            'platform owner',
            'quarantine events from clocks outside the approved skew'
        ),
        (
            3,
            'late arrival',
            '15-minute watermark is an example, not an approved production SLA',
            'analytics owner',
            'publish a correction/retraction for accepted late data'
        ),
        (
            4,
            'overlap and gap',
            'current periods may be adjacent but never overlap per business key',
            'data model owner',
            'reject overlap; report gaps for domain review'
        ),
        (
            5,
            'history correction',
            'authorized writers append system-time versions and ledger reversals',
            'security owner',
            'deny UPDATE/DELETE on immutable audit relations'
        ),
        (
            6,
            'retention and legal hold',
            'eligibility is reviewed; a hold blocks deletion approval',
            'records-policy owner',
            'retain data and escalate conflicting policy'
        ),
        (
            7,
            'replicas and backups',
            'retention, holds, and deletion evidence cover every maintained copy',
            'recovery owner',
            'stop deletion until propagation and restore tests are evidenced'
        )
) AS assumption_register(
    assumption_number,
    topic,
    decision_or_assumption,
    owner,
    failure_response
)
ORDER BY assumption_number;

-- Exercise 7: retain both the authoritative instant and IANA source zone. These
-- civil examples are classified *before* accepting PostgreSQL's silent default
-- interpretation. Zero matching instants means nonexistent; multiple matching
-- instants mean ambiguous.
WITH civil(case_id, local_time, zone_name) AS (
    VALUES
        (
            'spring-gap',
            TIMESTAMP '2026-03-08 02:30:00',
            'America/Los_Angeles'::text
        ),
        (
            'fall-fold',
            TIMESTAMP '2026-11-01 01:30:00',
            'America/Los_Angeles'::text
        ),
        (
            'ordinary-time',
            TIMESTAMP '2026-02-01 12:00:00',
            'America/Los_Angeles'::text
        )
),
defaults AS (
    SELECT
        c.*,
        c.local_time AT TIME ZONE c.zone_name AS default_interpreted_instant
    FROM civil AS c
),
candidate_instants AS (
    SELECT
        d.case_id,
        candidate_instant
    FROM defaults AS d
    CROSS JOIN LATERAL generate_series(
        d.default_interpreted_instant - INTERVAL '2 hours',
        d.default_interpreted_instant + INTERVAL '2 hours',
        INTERVAL '15 minutes'
    ) AS candidate_instant
    WHERE candidate_instant AT TIME ZONE d.zone_name = d.local_time
),
classified AS (
    SELECT
        d.case_id,
        d.local_time,
        d.zone_name,
        d.default_interpreted_instant,
        COUNT(ci.candidate_instant) AS matching_instants,
        array_agg(ci.candidate_instant ORDER BY ci.candidate_instant)
            FILTER (WHERE ci.candidate_instant IS NOT NULL)
            AS candidate_instants
    FROM defaults AS d
    LEFT JOIN candidate_instants AS ci
      ON ci.case_id = d.case_id
    GROUP BY
        d.case_id,
        d.local_time,
        d.zone_name,
        d.default_interpreted_instant
)
SELECT
    c.case_id,
    c.local_time,
    c.zone_name,
    CASE
        WHEN c.matching_instants = 0 THEN 'nonexistent'
        WHEN c.matching_instants > 1 THEN 'ambiguous'
        ELSE 'ordinary'
    END AS civil_time_status,
    c.matching_instants,
    c.candidate_instants,
    c.default_interpreted_instant,
    CASE
        WHEN c.matching_instants = 0
        THEN 'reject or require an explicit business-approved shift'
        WHEN c.matching_instants > 1
        THEN 'require the intended UTC offset or selected candidate instant'
        ELSE 'accept the sole round-trip candidate'
    END AS resolution_policy
FROM classified AS c
ORDER BY c.case_id;

DO $dst_fixture_invariant$
DECLARE
    nonexistent_count bigint;
    ambiguous_count bigint;
BEGIN
    WITH civil(case_id, local_time, zone_name) AS (
        VALUES
            (
                'spring-gap',
                TIMESTAMP '2026-03-08 02:30:00',
                'America/Los_Angeles'::text
            ),
            (
                'fall-fold',
                TIMESTAMP '2026-11-01 01:30:00',
                'America/Los_Angeles'::text
            )
    ),
    candidate_counts AS (
        SELECT
            c.case_id,
            COUNT(candidate_instant) FILTER (
                WHERE candidate_instant AT TIME ZONE c.zone_name = c.local_time
            ) AS matching_instants
        FROM civil AS c
        CROSS JOIN LATERAL generate_series(
            (c.local_time AT TIME ZONE c.zone_name) - INTERVAL '2 hours',
            (c.local_time AT TIME ZONE c.zone_name) + INTERVAL '2 hours',
            INTERVAL '15 minutes'
        ) AS candidate_instant
        GROUP BY c.case_id
    )
    SELECT
        COUNT(*) FILTER (WHERE matching_instants = 0),
        COUNT(*) FILTER (WHERE matching_instants > 1)
    INTO nonexistent_count, ambiguous_count
    FROM candidate_counts;

    IF nonexistent_count <> 1 OR ambiguous_count <> 1 THEN
        RAISE EXCEPTION
            'DST fixture did not expose one nonexistent and one ambiguous case';
    END IF;
END
$dst_fixture_invariant$;

-- Exercise 8: keep all three clocks and derive a documented watermark from
-- event time; data beyond it needs a correction/retraction policy.
CREATE TABLE pro_temporal_lab.timed_events (
    event_key text PRIMARY KEY,
    event_at timestamptz NOT NULL,
    ingested_at timestamptz NOT NULL,
    processed_at timestamptz NOT NULL
);

INSERT INTO pro_temporal_lab.timed_events
VALUES
    (
        'EV-1',
        TIMESTAMPTZ '2026-01-01 10:00+00',
        TIMESTAMPTZ '2026-01-01 10:02+00',
        TIMESTAMPTZ '2026-01-01 10:03+00'
    ),
    (
        'EV-LATE',
        TIMESTAMPTZ '2026-01-01 09:30+00',
        TIMESTAMPTZ '2026-01-01 11:00+00',
        TIMESTAMPTZ '2026-01-01 11:01+00'
    );

SELECT
    COUNT(*) AS event_count,
    max(e.event_at) AS maximum_event_time,
    max(e.event_at) - INTERVAL '15 minutes' AS example_watermark,
    max(e.ingested_at - e.event_at) AS maximum_arrival_delay,
    max(e.processed_at - e.ingested_at) AS maximum_processing_delay,
    COUNT(*) FILTER (
        WHERE e.event_at
              < (
                  SELECT max(w.event_at) - INTERVAL '15 minutes'
                  FROM pro_temporal_lab.timed_events AS w
              )
    ) AS events_behind_watermark,
    'publish a corrected aggregate with stable window/version identity'
        AS late_data_correction_policy
FROM pro_temporal_lab.timed_events AS e;

-- Exercise 9: Type-2 dimension join uses business key plus half-open effective
-- containment and asserts at most one match.
CREATE TABLE pro_temporal_lab.customer_dimension (
    customer_version_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_key text NOT NULL,
    effective_period daterange NOT NULL,
    segment text NOT NULL,
    is_current boolean NOT NULL,
    correction_reason text NOT NULL,
    recorded_at timestamptz NOT NULL,
    CHECK (NOT isempty(effective_period)),
    CHECK (is_current = upper_inf(effective_period))
);

INSERT INTO pro_temporal_lab.customer_dimension (
    customer_key,
    effective_period,
    segment,
    is_current,
    correction_reason,
    recorded_at
)
VALUES
    (
        'CUS-1',
        daterange(DATE '2026-01-01', DATE '2026-02-01', '[)'),
        'starter',
        false,
        'initial classification',
        TIMESTAMPTZ '2026-01-01 00:00+00'
    ),
    (
        'CUS-1',
        daterange(DATE '2026-02-01', NULL, '[)'),
        'established',
        true,
        'scheduled segment transition',
        TIMESTAMPTZ '2026-01-20 00:00+00'
    );

CREATE TABLE pro_temporal_lab.order_facts (
    order_key text PRIMARY KEY,
    customer_key text NOT NULL,
    ordered_on date NOT NULL
);

INSERT INTO pro_temporal_lab.order_facts
VALUES
    ('ORD-A', 'CUS-1', DATE '2026-01-31'),
    ('ORD-B', 'CUS-1', DATE '2026-02-01');

CREATE VIEW pro_temporal_lab.order_dimension_resolution AS
SELECT
    order_fact.order_key,
    order_fact.customer_key,
    order_fact.ordered_on,
    d.customer_version_id,
    d.segment,
    d.effective_period,
    d.is_current,
    d.correction_reason,
    d.recorded_at
FROM pro_temporal_lab.order_facts AS order_fact
LEFT JOIN pro_temporal_lab.customer_dimension AS d
  ON d.customer_key = order_fact.customer_key
 AND d.effective_period @> order_fact.ordered_on;

SELECT
    resolution.order_key,
    resolution.ordered_on,
    resolution.customer_version_id,
    resolution.segment,
    resolution.effective_period,
    resolution.is_current,
    resolution.correction_reason
FROM pro_temporal_lab.order_dimension_resolution AS resolution
ORDER BY resolution.order_key;

DO $type_2_invariant$
BEGIN
    IF EXISTS (
        SELECT order_fact.order_key
        FROM pro_temporal_lab.order_facts AS order_fact
        LEFT JOIN pro_temporal_lab.customer_dimension AS d
          ON d.customer_key = order_fact.customer_key
         AND d.effective_period @> order_fact.ordered_on
        GROUP BY order_fact.order_key
        HAVING COUNT(d.customer_version_id) > 1
    ) THEN
        RAISE EXCEPTION 'one order matched multiple dimension versions';
    END IF;

    IF (
        SELECT COUNT(*)
        FROM pro_temporal_lab.order_dimension_resolution
    ) <> (
        SELECT COUNT(*)
        FROM pro_temporal_lab.order_facts
    ) THEN
        RAISE EXCEPTION 'Type-2 join lost or duplicated an order fact';
    END IF;
END
$type_2_invariant$;

-- The negative control deliberately adds an overlapping version, proves the
-- diagnostic detects ORD-B, and then rolls back only that injected corruption.
SAVEPOINT before_type_2_overlap;
INSERT INTO pro_temporal_lab.customer_dimension (
    customer_key,
    effective_period,
    segment,
    is_current,
    correction_reason,
    recorded_at
)
VALUES (
    'CUS-1',
    daterange(DATE '2026-01-15', DATE '2026-02-15', '[)'),
    'overlap-negative-control',
    false,
    'deliberate overlap for invariant test',
    TIMESTAMPTZ '2026-01-25 00:00+00'
);

SELECT
    order_fact.order_key,
    COUNT(d.customer_version_id) AS matching_versions
FROM pro_temporal_lab.order_facts AS order_fact
LEFT JOIN pro_temporal_lab.customer_dimension AS d
  ON d.customer_key = order_fact.customer_key
 AND d.effective_period @> order_fact.ordered_on
GROUP BY order_fact.order_key
HAVING COUNT(d.customer_version_id) > 1
ORDER BY order_fact.order_key;

DO $type_2_negative_control$
BEGIN
    IF NOT EXISTS (
        SELECT order_fact.order_key
        FROM pro_temporal_lab.order_facts AS order_fact
        LEFT JOIN pro_temporal_lab.customer_dimension AS d
          ON d.customer_key = order_fact.customer_key
         AND d.effective_period @> order_fact.ordered_on
        GROUP BY order_fact.order_key
        HAVING COUNT(d.customer_version_id) > 1
    ) THEN
        RAISE EXCEPTION 'overlap negative control was not detected';
    END IF;
END
$type_2_negative_control$;
ROLLBACK TO SAVEPOINT before_type_2_overlap;

-- Exercise 10: temporal parent/child containment is a cross-row rule. A safe
-- trigger locks one business-key namespace, checks containment, and validates
-- parent shrink/delete and concurrent changes; exclusion alone is insufficient.
SELECT *
FROM (
    VALUES
        (
            1,
            'child insert/update',
            'advisory lock on business key, then require a containing parent',
            'reject missing or multiply matching parent'
        ),
        (
            2,
            'parent shrink/delete',
            'same lock namespace, then prove every child remains contained',
            'reject the parent change or repair children first'
        ),
        (
            3,
            'bulk historical repair',
            'stage, validate gaps/overlaps, then swap in one controlled transaction',
            'retain old snapshot and reconciliation evidence'
        ),
        (
            4,
            'deferred validation',
            'use only when the domain permits a bounded temporarily invalid state',
            'block cutover until the final invariant query is empty'
        )
) AS temporal_integrity_plan(
    step_number,
    write_path,
    concurrency_or_validation_control,
    failure_response
)
ORDER BY step_number;

-- Exercise 11: compare each lower bound with the running maximum *prior* upper
-- bound. `upper()` is NULL for an unbounded range, so `upper_inf()` plus an
-- explicit infinity sentinel preserves that prior coverage.
CREATE TABLE pro_temporal_lab.period_cases (
    period_id integer PRIMARY KEY,
    business_key text NOT NULL,
    valid_period daterange NOT NULL
);

INSERT INTO pro_temporal_lab.period_cases
VALUES
    (1, 'ACCOUNT-1', daterange(DATE '2026-01-01', DATE '2026-01-10', '[)')),
    (2, 'ACCOUNT-1', daterange(DATE '2026-01-01', DATE '2026-01-10', '[)')),
    (3, 'ACCOUNT-1', daterange(DATE '2026-01-05', DATE '2026-01-07', '[)')),
    (4, 'ACCOUNT-1', daterange(DATE '2026-01-10', DATE '2026-01-12', '[)')),
    (5, 'ACCOUNT-1', daterange(DATE '2026-01-15', DATE '2026-01-18', '[)')),
    (6, 'ACCOUNT-1', daterange(DATE '2026-01-18', NULL, '[)')),
    (7, 'ACCOUNT-1', daterange(DATE '2026-01-20', DATE '2026-01-21', '[)')),
    (8, 'ACCOUNT-1', 'empty'::daterange);

CREATE VIEW pro_temporal_lab.period_diagnostics AS
WITH duplicate_counts AS (
    SELECT
        p.*,
        COUNT(*) OVER (
            PARTITION BY p.business_key, p.valid_period
        ) AS duplicate_count
    FROM pro_temporal_lab.period_cases AS p
),
with_prior AS (
    SELECT
        p.*,
        max(
            CASE
                WHEN NOT isempty(p.valid_period)
                THEN COALESCE(upper(p.valid_period), 'infinity'::date)
            END
        ) OVER (
            PARTITION BY p.business_key
            ORDER BY
                isempty(p.valid_period),
                lower(p.valid_period),
                COALESCE(upper(p.valid_period), 'infinity'::date),
                p.period_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prior_max_upper
    FROM duplicate_counts AS p
)
SELECT
    w.period_id,
    w.business_key,
    w.valid_period,
    upper_inf(w.valid_period) AS has_unbounded_upper,
    w.duplicate_count,
    w.prior_max_upper,
    CASE
        WHEN isempty(w.valid_period) THEN 'empty'
        WHEN w.duplicate_count > 1 THEN 'duplicate'
        WHEN w.prior_max_upper IS NULL THEN 'first'
        WHEN lower(w.valid_period) < w.prior_max_upper THEN 'overlap'
        WHEN lower(w.valid_period) = w.prior_max_upper THEN 'adjacent'
        ELSE 'gap'
    END AS relationship_to_prior_coverage
FROM with_prior AS w
;

SELECT
    d.period_id,
    d.business_key,
    d.valid_period,
    d.has_unbounded_upper,
    d.duplicate_count,
    d.prior_max_upper,
    d.relationship_to_prior_coverage
FROM pro_temporal_lab.period_diagnostics AS d
ORDER BY
    isempty(d.valid_period),
    lower(d.valid_period),
    COALESCE(upper(d.valid_period), 'infinity'::date),
    d.period_id;

DO $period_diagnostics_invariant$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pro_temporal_lab.period_diagnostics
        WHERE relationship_to_prior_coverage = 'duplicate'
    ) OR NOT EXISTS (
        SELECT 1
        FROM pro_temporal_lab.period_diagnostics
        WHERE relationship_to_prior_coverage = 'empty'
    ) OR NOT EXISTS (
        SELECT 1
        FROM pro_temporal_lab.period_diagnostics
        WHERE relationship_to_prior_coverage = 'gap'
    ) OR NOT EXISTS (
        SELECT 1
        FROM pro_temporal_lab.period_diagnostics
        WHERE relationship_to_prior_coverage = 'adjacent'
    ) OR NOT EXISTS (
        SELECT 1
        FROM pro_temporal_lab.period_diagnostics
        WHERE period_id = 7
          AND relationship_to_prior_coverage = 'overlap'
          AND prior_max_upper = 'infinity'::date
    ) THEN
        RAISE EXCEPTION
            'period fixture must expose duplicate, empty, gap, adjacency, and unbounded overlap';
    END IF;
END
$period_diagnostics_invariant$;

-- Exercise 12: archive only after hold-aware inventory, detach/move review,
-- count/checksum/dependency verification, encrypted access-controlled storage,
-- restore proof, propagated hold state, and immutable deletion evidence.
SELECT *
FROM (
    VALUES
        (
            1,
            'inventory',
            'partition bounds, cross-partition keys, indexes, dependencies, holds',
            'signed candidate manifest'
        ),
        (
            2,
            'hold gate',
            'exclude any partition or row covered by active legal hold',
            'empty unresolved-hold report'
        ),
        (
            3,
            'detach',
            'quiesce or lock the write path and detach in a controlled window',
            'catalog evidence and rollback point'
        ),
        (
            4,
            'archive',
            'encrypt, checksum, restrict access, and record custody/location',
            'artifact identity and checksum'
        ),
        (
            5,
            'reconcile',
            'compare schema, counts, keys, aggregates, and checksums',
            'source/archive reconciliation report'
        ),
        (
            6,
            'restore test',
            'restore the artifact into an isolated target and run smoke queries',
            'timestamped successful restore evidence'
        ),
        (
            7,
            'source deletion',
            'delete only after approval, hold propagation, and restore proof',
            'immutable deletion evidence or explicit retention decision'
        )
) AS archive_plan(step_number, phase, required_control, required_evidence)
ORDER BY step_number;

ROLLBACK;
