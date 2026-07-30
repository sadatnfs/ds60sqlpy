-- SQL-ANALYTICS-01: Reusable analytical query patterns
-- Target: PostgreSQL 16+

\set ON_ERROR_STOP on
\echo 'SQL-ANALYTICS-01: disposable analytical-pattern lab'
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_analytics_lab;

CREATE TABLE pro_analytics_lab.users (
    user_id bigint PRIMARY KEY,
    signup_at timestamptz NOT NULL
);

CREATE TABLE pro_analytics_lab.events (
    ingestion_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_event_id text NOT NULL,
    user_id bigint NOT NULL REFERENCES pro_analytics_lab.users (user_id),
    event_name text NOT NULL,
    event_at timestamptz NOT NULL,
    ingested_at timestamptz NOT NULL
);

CREATE TABLE pro_analytics_lab.daily_activity (
    user_id bigint NOT NULL REFERENCES pro_analytics_lab.users (user_id),
    activity_date date NOT NULL,
    PRIMARY KEY (user_id, activity_date)
);

CREATE TABLE pro_analytics_lab.campaign_touches (
    touch_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id bigint NOT NULL REFERENCES pro_analytics_lab.users (user_id),
    campaign text NOT NULL,
    touched_at timestamptz NOT NULL
);

CREATE TABLE pro_analytics_lab.tier_history (
    user_id bigint NOT NULL REFERENCES pro_analytics_lab.users (user_id),
    valid_from timestamptz NOT NULL,
    valid_to timestamptz,
    tier text NOT NULL,
    PRIMARY KEY (user_id, valid_from),
    CHECK (valid_to IS NULL OR valid_to > valid_from)
);

INSERT INTO pro_analytics_lab.users (user_id, signup_at)
VALUES
    (1, TIMESTAMPTZ '2026-01-01 09:00:00+00'),
    (2, TIMESTAMPTZ '2026-01-15 10:00:00+00'),
    (3, TIMESTAMPTZ '2026-02-01 08:00:00+00');

INSERT INTO pro_analytics_lab.events (
    source_event_id, user_id, event_name, event_at, ingested_at
)
VALUES
    ('E100', 1, 'signup',       TIMESTAMPTZ '2026-01-01 09:00:00+00', TIMESTAMPTZ '2026-01-01 09:01:00+00'),
    ('E101', 1, 'view_item',    TIMESTAMPTZ '2026-01-01 09:05:00+00', TIMESTAMPTZ '2026-01-01 09:06:00+00'),
    ('E102', 1, 'add_to_cart',  TIMESTAMPTZ '2026-01-01 09:10:00+00', TIMESTAMPTZ '2026-01-01 09:11:00+00'),
    ('E103', 1, 'purchase',     TIMESTAMPTZ '2026-01-01 09:20:00+00', TIMESTAMPTZ '2026-01-01 09:21:00+00'),
    ('E103', 1, 'purchase',     TIMESTAMPTZ '2026-01-01 09:20:00+00', TIMESTAMPTZ '2026-01-01 09:25:00+00'),
    ('E104', 1, 'view_item',    TIMESTAMPTZ '2026-01-01 11:00:00+00', TIMESTAMPTZ '2026-01-01 11:01:00+00'),
    ('E105', 1, 'active',       TIMESTAMPTZ '2026-01-02 12:00:00+00', TIMESTAMPTZ '2026-01-02 12:01:00+00'),
    ('E106', 1, 'active',       TIMESTAMPTZ '2026-01-03 12:00:00+00', TIMESTAMPTZ '2026-01-03 12:01:00+00'),
    ('E200', 2, 'signup',       TIMESTAMPTZ '2026-01-15 10:00:00+00', TIMESTAMPTZ '2026-01-15 10:01:00+00'),
    ('E201', 2, 'view_item',    TIMESTAMPTZ '2026-01-15 10:04:00+00', TIMESTAMPTZ '2026-01-15 10:05:00+00'),
    ('E202', 2, 'add_to_cart',  TIMESTAMPTZ '2026-01-15 10:07:00+00', TIMESTAMPTZ '2026-01-15 10:08:00+00'),
    ('E203', 2, 'purchase',     TIMESTAMPTZ '2026-01-15 10:15:00+00', TIMESTAMPTZ '2026-01-15 10:16:00+00'),
    ('E204', 2, 'active',       TIMESTAMPTZ '2026-01-16 09:00:00+00', TIMESTAMPTZ '2026-01-16 09:01:00+00'),
    ('E300', 3, 'signup',       TIMESTAMPTZ '2026-02-01 08:00:00+00', TIMESTAMPTZ '2026-02-01 08:01:00+00'),
    ('E301', 3, 'view_item',    TIMESTAMPTZ '2026-02-01 08:05:00+00', TIMESTAMPTZ '2026-02-01 08:06:00+00'),
    ('E302', 3, 'active',       TIMESTAMPTZ '2026-02-03 08:00:00+00', TIMESTAMPTZ '2026-02-03 08:01:00+00');

INSERT INTO pro_analytics_lab.daily_activity (user_id, activity_date)
VALUES
    (1, DATE '2026-01-01'),
    (1, DATE '2026-01-02'),
    (1, DATE '2026-01-03'),
    (1, DATE '2026-01-05'),
    (1, DATE '2026-01-06'),
    (2, DATE '2026-01-15'),
    (2, DATE '2026-01-16'),
    (2, DATE '2026-01-18'),
    (3, DATE '2026-02-01'),
    (3, DATE '2026-02-03');

INSERT INTO pro_analytics_lab.campaign_touches (
    user_id, campaign, touched_at
)
VALUES
    (1, 'search', TIMESTAMPTZ '2025-12-30 10:00:00+00'),
    (1, 'email',  TIMESTAMPTZ '2026-01-01 09:15:00+00'),
    (2, 'search', TIMESTAMPTZ '2026-01-10 12:00:00+00'),
    (3, 'social', TIMESTAMPTZ '2026-01-20 12:00:00+00');

INSERT INTO pro_analytics_lab.tier_history (
    user_id, valid_from, valid_to, tier
)
VALUES
    (1, TIMESTAMPTZ '2026-01-01 00:00:00+00', TIMESTAMPTZ '2026-01-10 00:00:00+00', 'basic'),
    (1, TIMESTAMPTZ '2026-01-10 00:00:00+00', NULL, 'pro'),
    (2, TIMESTAMPTZ '2026-01-01 00:00:00+00', NULL, 'basic'),
    (3, TIMESTAMPTZ '2026-02-01 00:00:00+00', NULL, 'basic');

-- Canonicalize duplicate ingestion with an explicit winner rule.
CREATE VIEW pro_analytics_lab.deduplicated_events AS
SELECT
    ranked.source_event_id,
    ranked.user_id,
    ranked.event_name,
    ranked.event_at,
    ranked.ingested_at
FROM (
    SELECT
        e.*,
        row_number() OVER (
            PARTITION BY e.source_event_id
            ORDER BY e.ingested_at DESC, e.ingestion_id DESC
        ) AS winner_rank
    FROM pro_analytics_lab.events AS e
) AS ranked
WHERE ranked.winner_rank = 1;

\echo 'Deduplication: one deterministic winner per source event'
SELECT
    de.source_event_id,
    de.user_id,
    de.event_name,
    de.event_at,
    de.ingested_at
FROM pro_analytics_lab.deduplicated_events AS de
ORDER BY de.source_event_id;

\echo 'Sessionization: a new session starts after more than 30 minutes'
WITH lagged AS (
    SELECT
        de.*,
        lag(de.event_at) OVER (
            PARTITION BY de.user_id
            ORDER BY de.event_at, de.source_event_id
        ) AS previous_event_at
    FROM pro_analytics_lab.deduplicated_events AS de
),
marked AS (
    SELECT
        lagged.*,
        CASE
            WHEN lagged.previous_event_at IS NULL
              OR lagged.event_at - lagged.previous_event_at > INTERVAL '30 minutes'
            THEN 1
            ELSE 0
        END AS new_session
    FROM lagged
),
numbered AS (
    SELECT
        marked.*,
        sum(marked.new_session) OVER (
            PARTITION BY marked.user_id
            ORDER BY marked.event_at, marked.source_event_id
            ROWS UNBOUNDED PRECEDING
        ) AS session_number
    FROM marked
)
SELECT
    numbered.user_id,
    numbered.session_number,
    min(numbered.event_at) AS session_started_at,
    max(numbered.event_at) AS session_ended_at,
    count(*) AS event_count
FROM numbered
GROUP BY numbered.user_id, numbered.session_number
ORDER BY numbered.user_id, numbered.session_number;

\echo 'Gaps and islands: consecutive activity dates'
WITH numbered AS (
    SELECT
        da.user_id,
        da.activity_date,
        da.activity_date
            - row_number() OVER (
                PARTITION BY da.user_id
                ORDER BY da.activity_date
            )::integer AS island_key
    FROM pro_analytics_lab.daily_activity AS da
)
SELECT
    numbered.user_id,
    min(numbered.activity_date) AS island_start,
    max(numbered.activity_date) AS island_end,
    count(*) AS active_days
FROM numbered
GROUP BY numbered.user_id, numbered.island_key
ORDER BY numbered.user_id, island_start;

\echo 'Ordered funnel: later steps must occur after the prior step'
WITH step_1 AS (
    SELECT de.user_id, min(de.event_at) AS signup_at
    FROM pro_analytics_lab.deduplicated_events AS de
    WHERE de.event_name = 'signup'
    GROUP BY de.user_id
),
step_2 AS (
    SELECT
        s1.user_id,
        s1.signup_at,
        min(de.event_at) FILTER (
            WHERE de.event_name = 'view_item'
              AND de.event_at >= s1.signup_at
        ) AS viewed_at
    FROM step_1 AS s1
    LEFT JOIN pro_analytics_lab.deduplicated_events AS de
      ON de.user_id = s1.user_id
    GROUP BY s1.user_id, s1.signup_at
),
step_3 AS (
    SELECT
        s2.user_id,
        s2.signup_at,
        s2.viewed_at,
        min(de.event_at) FILTER (
            WHERE de.event_name = 'add_to_cart'
              AND de.event_at >= s2.viewed_at
        ) AS added_at
    FROM step_2 AS s2
    LEFT JOIN pro_analytics_lab.deduplicated_events AS de
      ON de.user_id = s2.user_id
    GROUP BY s2.user_id, s2.signup_at, s2.viewed_at
),
step_4 AS (
    SELECT
        s3.user_id,
        s3.signup_at,
        s3.viewed_at,
        s3.added_at,
        min(de.event_at) FILTER (
            WHERE de.event_name = 'purchase'
              AND de.event_at >= s3.added_at
        ) AS purchased_at
    FROM step_3 AS s3
    LEFT JOIN pro_analytics_lab.deduplicated_events AS de
      ON de.user_id = s3.user_id
    GROUP BY s3.user_id, s3.signup_at, s3.viewed_at, s3.added_at
)
SELECT
    count(*) AS signed_up,
    count(*) FILTER (WHERE viewed_at IS NOT NULL) AS viewed,
    count(*) FILTER (WHERE added_at IS NOT NULL) AS added,
    count(*) FILTER (WHERE purchased_at IS NOT NULL) AS purchased
FROM step_4;

\echo 'Last-touch attribution within a seven-day lookback'
SELECT
    purchase.source_event_id AS purchase_event_id,
    purchase.user_id,
    purchase.event_at AS purchased_at,
    touch.campaign,
    touch.touched_at
FROM pro_analytics_lab.deduplicated_events AS purchase
LEFT JOIN LATERAL (
    SELECT
        ct.campaign,
        ct.touched_at,
        ct.touch_id
    FROM pro_analytics_lab.campaign_touches AS ct
    WHERE ct.user_id = purchase.user_id
      AND ct.touched_at <= purchase.event_at
      AND ct.touched_at >= purchase.event_at - INTERVAL '7 days'
    ORDER BY ct.touched_at DESC, ct.touch_id DESC
    LIMIT 1
) AS touch
  ON true
WHERE purchase.event_name = 'purchase'
ORDER BY purchase.source_event_id;

\echo 'As-of join: [valid_from, valid_to) tier at event time'
SELECT
    de.source_event_id,
    de.user_id,
    de.event_at,
    history.tier
FROM pro_analytics_lab.deduplicated_events AS de
LEFT JOIN LATERAL (
    SELECT th.tier
    FROM pro_analytics_lab.tier_history AS th
    WHERE th.user_id = de.user_id
      AND th.valid_from <= de.event_at
      AND (th.valid_to IS NULL OR de.event_at < th.valid_to)
    ORDER BY th.valid_from DESC
    LIMIT 1
) AS history
  ON true
WHERE de.event_name = 'purchase'
ORDER BY de.source_event_id;

\echo 'Monthly cohort retention with explicit denominator'
WITH cohorts AS (
    SELECT
        u.user_id,
        date_trunc('month', u.signup_at AT TIME ZONE 'UTC')::date
            AS cohort_month
    FROM pro_analytics_lab.users AS u
),
activity AS (
    SELECT DISTINCT
        da.user_id,
        date_trunc('month', da.activity_date::timestamp)::date
            AS activity_month
    FROM pro_analytics_lab.daily_activity AS da
),
retention AS (
    SELECT
        c.cohort_month,
        (
            extract(year FROM age(a.activity_month, c.cohort_month)) * 12
            + extract(month FROM age(a.activity_month, c.cohort_month))
        )::integer AS month_number,
        count(DISTINCT a.user_id) AS retained_users
    FROM cohorts AS c
    JOIN activity AS a
      ON a.user_id = c.user_id
     AND a.activity_month >= c.cohort_month
    GROUP BY c.cohort_month, month_number
),
sizes AS (
    SELECT c.cohort_month, count(*) AS cohort_users
    FROM cohorts AS c
    GROUP BY c.cohort_month
)
SELECT
    r.cohort_month,
    r.month_number,
    s.cohort_users,
    r.retained_users,
    round(r.retained_users::numeric / NULLIF(s.cohort_users, 0), 4)
        AS retention_rate
FROM retention AS r
JOIN sizes AS s USING (cohort_month)
ORDER BY r.cohort_month, r.month_number;

-- Exercises:
--
-- 1. Prove the dedup view has one row per source_event_id and document why the
--    latest ingested row wins.
-- 2. Recalculate sessions with a 60-minute threshold and add duration. Decide
--    whether an event exactly 60 minutes later starts a new session.
-- 3. Return one row per user with every funnel timestamp, then test that each
--    non-NULL step is no earlier than its predecessor.
-- 4. Return only islands lasting at least two active days.
-- 5. Add an unattributed purchase and two touches at the same timestamp. Define
--    and test the deterministic tie-break and NULL attribution behavior.
-- 6. Add month 1 activity and verify numerator, cohort denominator, and rate
--    independently before division.
-- 7. Add an event exactly at a tier valid_to boundary and prove it joins the
--    successor [valid_from, valid_to) row, not both rows.

DO $self_check$
BEGIN
    IF (SELECT COUNT(*) FROM pro_analytics_lab.events) <> 16 THEN
        RAISE EXCEPTION 'unexpected raw event count';
    END IF;
    IF (
        SELECT COUNT(*)
        FROM pro_analytics_lab.deduplicated_events
    ) <> 15 THEN
        RAISE EXCEPTION 'deduplication did not remove exactly one retry';
    END IF;
    IF (
        SELECT COUNT(*)
        FROM pro_analytics_lab.deduplicated_events AS de
        WHERE de.event_name = 'purchase'
    ) <> 2 THEN
        RAISE EXCEPTION 'unexpected purchase grain';
    END IF;
END
$self_check$;

ROLLBACK;
\echo 'SQL-ANALYTICS-01 complete: pro_analytics_lab was rolled back'

