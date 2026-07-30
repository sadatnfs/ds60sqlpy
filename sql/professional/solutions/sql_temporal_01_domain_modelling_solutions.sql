-- SQL-TEMPORAL-01 executable solutions
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_temporal_lab;

CREATE TABLE pro_temporal_lab.facts (
    fact_version_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    subject_key text NOT NULL,
    valid_period daterange NOT NULL,
    system_period tstzrange NOT NULL,
    value text NOT NULL,
    CHECK (NOT isempty(valid_period)),
    CHECK (NOT isempty(system_period))
);

-- Initial and March correction.
INSERT INTO pro_temporal_lab.facts (
    subject_key, valid_period, system_period, value
)
VALUES
    (
        'SUB-1',
        daterange(DATE '2026-01-01', DATE '2026-04-01', '[)'),
        tstzrange(
            TIMESTAMPTZ '2026-03-01 00:00+00',
            TIMESTAMPTZ '2026-03-10 00:00+00',
            '[)'
        ),
        'value-10'
    ),
    (
        'SUB-1',
        daterange(DATE '2026-01-01', DATE '2026-04-01', '[)'),
        tstzrange(
            TIMESTAMPTZ '2026-03-10 00:00+00',
            TIMESTAMPTZ '2026-04-01 00:00+00',
            '[)'
        ),
        'value-12'
    ),
    -- Exercise 1: retroactive correction recorded April 1.
    (
        'SUB-1',
        daterange(DATE '2026-01-01', DATE '2026-04-01', '[)'),
        tstzrange(TIMESTAMPTZ '2026-04-01 00:00+00', NULL, '[)'),
        'value-11'
    );

SELECT
    query.system_as_of,
    f.value
FROM (
    VALUES
        (TIMESTAMPTZ '2026-03-15 00:00+00'),
        (TIMESTAMPTZ '2026-04-02 00:00+00')
) AS query(system_as_of)
JOIN pro_temporal_lab.facts AS f
  ON f.subject_key = 'SUB-1'
 AND f.valid_period @> DATE '2026-02-15'
 AND f.system_period @> query.system_as_of
ORDER BY query.system_as_of;

-- Exercise 4: immutable ledger and reversal of a reversal.
CREATE TABLE pro_temporal_lab.ledger (
    entry_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    idempotency_key text NOT NULL UNIQUE,
    event_kind text NOT NULL,
    amount numeric(12, 2) NOT NULL,
    reverses_entry_id bigint REFERENCES pro_temporal_lab.ledger (entry_id)
);

INSERT INTO pro_temporal_lab.ledger (
    idempotency_key, event_kind, amount
)
VALUES ('L-1', 'credit', 5.00);

INSERT INTO pro_temporal_lab.ledger (
    idempotency_key, event_kind, amount, reverses_entry_id
)
SELECT 'L-2', 'credit.reversal', -5.00, l.entry_id
FROM pro_temporal_lab.ledger AS l
WHERE l.idempotency_key = 'L-1';

INSERT INTO pro_temporal_lab.ledger (
    idempotency_key, event_kind, amount, reverses_entry_id
)
SELECT 'L-3', 'reversal.corrected', 5.00, l.entry_id
FROM pro_temporal_lab.ledger AS l
WHERE l.idempotency_key = 'L-2';

SELECT
    l.entry_id,
    l.idempotency_key,
    l.event_kind,
    l.amount,
    l.reverses_entry_id
FROM pro_temporal_lab.ledger AS l
ORDER BY l.entry_id;

-- Exercise 5: immutable decision log for hold release/review.
CREATE TABLE pro_temporal_lab.retention_decisions (
    decision_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    record_key text NOT NULL,
    decision text NOT NULL CHECK (
        decision IN ('hold_applied', 'hold_released', 'deletion_approved')
    ),
    decided_by text NOT NULL,
    reason text NOT NULL,
    decided_at timestamptz NOT NULL,
    UNIQUE (record_key, decision, decided_at)
);

INSERT INTO pro_temporal_lab.retention_decisions (
    record_key, decision, decided_by, reason, decided_at
)
VALUES
    (
        'REC-1',
        'hold_applied',
        'policy-reviewer',
        'active review',
        TIMESTAMPTZ '2026-02-01 00:00+00'
    ),
    (
        'REC-1',
        'hold_released',
        'policy-reviewer',
        'review completed',
        TIMESTAMPTZ '2026-03-01 00:00+00'
    );

DO $solution$
BEGIN
    IF (
        SELECT COUNT(*)
        FROM pro_temporal_lab.facts AS f
        WHERE f.valid_period @> DATE '2026-02-15'
          AND f.system_period @> TIMESTAMPTZ '2026-04-02 00:00+00'
    ) <> 1 THEN
        RAISE EXCEPTION 'retroactive as-of result is not single-valued';
    END IF;

    IF (SELECT SUM(l.amount) FROM pro_temporal_lab.ledger AS l) <> 5.00 THEN
        RAISE EXCEPTION 'ledger reversal chain does not reconcile';
    END IF;
END
$solution$;

ROLLBACK;

