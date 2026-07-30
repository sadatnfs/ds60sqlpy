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

-- Exercise 2: exactly at an upper bound, the old fact is excluded by [lower,
-- upper); the next adjacent fact would become eligible.
SELECT
    probe.valid_on,
    probe.known_at,
    COUNT(f.fact_version_id) AS matching_versions
FROM (
    VALUES
        (
            DATE '2026-03-31',
            TIMESTAMPTZ '2026-04-02 00:00+00'
        ),
        (
            DATE '2026-04-01',
            TIMESTAMPTZ '2026-04-02 00:00+00'
        )
) AS probe(valid_on, known_at)
LEFT JOIN pro_temporal_lab.facts AS f
  ON f.subject_key = 'SUB-1'
 AND f.valid_period @> probe.valid_on
 AND f.system_period @> probe.known_at
GROUP BY probe.valid_on, probe.known_at
ORDER BY probe.valid_on;

-- Exercise 3: an approved btree_gist exclusion constraint can reject current
-- period overlap under concurrency. The fallback must lock one stable business
-- key before checking; this core solution installs no extension.

-- Exercise 6: domain assumptions include zone/clock authority, half-open bounds,
-- lateness, overlap/gap, correction authority, identity, unit/ledger semantics,
-- retention/hold/deletion, and replica/backup treatment.

-- Exercise 7: retain both the authoritative instant and IANA source zone. These
-- civil examples are deliberately visible so the application can reject or ask
-- for disambiguation rather than accepting PostgreSQL's default interpretation.
SELECT
    local_time,
    zone_name,
    local_time AT TIME ZONE zone_name AS interpreted_instant
FROM (
    VALUES
        (
            TIMESTAMP '2026-03-08 02:30:00',
            'America/Los_Angeles'::text
        ),
        (
            TIMESTAMP '2026-11-01 01:30:00',
            'America/Los_Angeles'::text
        )
) AS civil(local_time, zone_name)
ORDER BY local_time;

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
    max(e.event_at) AS maximum_event_time,
    max(e.event_at) - INTERVAL '15 minutes' AS example_watermark,
    max(e.ingested_at - e.event_at) AS maximum_arrival_delay
FROM pro_temporal_lab.timed_events AS e;

-- Exercise 9: Type-2 dimension join uses business key plus half-open effective
-- containment and asserts at most one match.
CREATE TABLE pro_temporal_lab.customer_dimension (
    customer_version_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_key text NOT NULL,
    effective_period daterange NOT NULL,
    segment text NOT NULL,
    CHECK (NOT isempty(effective_period))
);

INSERT INTO pro_temporal_lab.customer_dimension (
    customer_key, effective_period, segment
)
VALUES
    (
        'CUS-1',
        daterange(DATE '2026-01-01', DATE '2026-02-01', '[)'),
        'starter'
    ),
    (
        'CUS-1',
        daterange(DATE '2026-02-01', NULL, '[)'),
        'established'
    );

SELECT
    order_fact.order_key,
    order_fact.ordered_on,
    d.customer_version_id,
    d.segment
FROM (
    VALUES
        ('ORD-A'::text, 'CUS-1'::text, DATE '2026-01-31'),
        ('ORD-B'::text, 'CUS-1'::text, DATE '2026-02-01')
) AS order_fact(order_key, customer_key, ordered_on)
LEFT JOIN pro_temporal_lab.customer_dimension AS d
  ON d.customer_key = order_fact.customer_key
 AND d.effective_period @> order_fact.ordered_on
ORDER BY order_fact.order_key;

-- Exercise 10: temporal parent/child containment is a cross-row rule. A safe
-- trigger locks one business-key namespace, checks containment, and validates
-- parent shrink/delete and concurrent changes; exclusion alone is insufficient.

-- Exercise 11: compare each lower bound with the running maximum *prior* upper
-- bound so an earlier long interval is not hidden by a shorter immediate row.
WITH periods(period_id, valid_period) AS (
    VALUES
        (1, daterange(DATE '2026-01-01', DATE '2026-01-10', '[)')),
        (2, daterange(DATE '2026-01-05', DATE '2026-01-07', '[)')),
        (3, daterange(DATE '2026-01-12', DATE '2026-01-15', '[)'))
),
with_prior AS (
    SELECT
        p.*,
        max(upper(p.valid_period)) OVER (
            ORDER BY lower(p.valid_period), upper(p.valid_period), p.period_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ) AS prior_max_upper
    FROM periods AS p
)
SELECT
    w.period_id,
    w.valid_period,
    CASE
        WHEN w.prior_max_upper IS NULL THEN 'first'
        WHEN lower(w.valid_period) < w.prior_max_upper THEN 'overlap'
        WHEN lower(w.valid_period) = w.prior_max_upper THEN 'adjacent'
        ELSE 'gap'
    END AS relationship_to_prior_coverage
FROM with_prior AS w
ORDER BY lower(w.valid_period), upper(w.valid_period), w.period_id;

-- Exercise 12: archive only after hold-aware inventory, detach/move review,
-- count/checksum/dependency verification, encrypted access-controlled storage,
-- restore proof, propagated hold state, and immutable deletion evidence.

ROLLBACK;
