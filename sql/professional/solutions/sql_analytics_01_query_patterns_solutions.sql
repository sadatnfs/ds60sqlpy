-- SQL-ANALYTICS-01 executable solutions
\set ON_ERROR_STOP on
BEGIN;
SET LOCAL search_path TO pg_catalog, public;
CREATE SCHEMA pro_analytics_lab;

CREATE TABLE pro_analytics_lab.events (
    ingestion_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_event_id text NOT NULL,
    user_id bigint NOT NULL,
    event_name text NOT NULL,
    event_at timestamptz NOT NULL,
    ingested_at timestamptz NOT NULL
);

INSERT INTO pro_analytics_lab.events (
    source_event_id, user_id, event_name, event_at, ingested_at
)
VALUES
    ('A1', 1, 'signup',      TIMESTAMPTZ '2026-01-01 09:00+00', TIMESTAMPTZ '2026-01-01 09:01+00'),
    ('A2', 1, 'view_item',   TIMESTAMPTZ '2026-01-01 09:10+00', TIMESTAMPTZ '2026-01-01 09:11+00'),
    ('A3', 1, 'add_to_cart', TIMESTAMPTZ '2026-01-01 09:20+00', TIMESTAMPTZ '2026-01-01 09:21+00'),
    ('A4', 1, 'purchase',    TIMESTAMPTZ '2026-01-01 09:30+00', TIMESTAMPTZ '2026-01-01 09:31+00'),
    ('A4', 1, 'purchase',    TIMESTAMPTZ '2026-01-01 09:30+00', TIMESTAMPTZ '2026-01-01 09:32+00'),
    ('A5', 1, 'view_item',   TIMESTAMPTZ '2026-01-01 10:30+00', TIMESTAMPTZ '2026-01-01 10:31+00'),
    ('B1', 2, 'signup',      TIMESTAMPTZ '2026-01-02 09:00+00', TIMESTAMPTZ '2026-01-02 09:01+00'),
    ('B2', 2, 'view_item',   TIMESTAMPTZ '2026-01-02 09:10+00', TIMESTAMPTZ '2026-01-02 09:11+00');

CREATE VIEW pro_analytics_lab.deduplicated_events AS
SELECT source_event_id, user_id, event_name, event_at, ingested_at
FROM (
    SELECT
        e.*,
        row_number() OVER (
            PARTITION BY e.source_event_id
            ORDER BY e.ingested_at DESC, e.ingestion_id DESC
        ) AS rn
    FROM pro_analytics_lab.events AS e
) AS ranked
WHERE rn = 1;

-- Exercise 1.
SELECT
    de.source_event_id,
    COUNT(*) AS canonical_rows
FROM pro_analytics_lab.deduplicated_events AS de
GROUP BY de.source_event_id
ORDER BY de.source_event_id;

-- Exercise 2: exactly 60 minutes remains in the same session because the rule
-- starts a new session only when the gap is greater than 60 minutes.
WITH lagged AS (
    SELECT
        de.*,
        lag(de.event_at) OVER (
            PARTITION BY de.user_id
            ORDER BY de.event_at, de.source_event_id
        ) AS previous_at
    FROM pro_analytics_lab.deduplicated_events AS de
),
numbered AS (
    SELECT
        lagged.*,
        sum(
            CASE
                WHEN previous_at IS NULL
                  OR event_at - previous_at > INTERVAL '60 minutes'
                THEN 1 ELSE 0
            END
        ) OVER (
            PARTITION BY user_id
            ORDER BY event_at, source_event_id
            ROWS UNBOUNDED PRECEDING
        ) AS session_number
    FROM lagged
)
SELECT
    user_id,
    session_number,
    min(event_at) AS started_at,
    max(event_at) AS ended_at,
    max(event_at) - min(event_at) AS duration,
    count(*) AS events
FROM numbered
GROUP BY user_id, session_number
ORDER BY user_id, session_number;

-- Exercise 3: ordered per-user funnel timestamps.
WITH signup AS (
    SELECT user_id, min(event_at) AS signup_at
    FROM pro_analytics_lab.deduplicated_events
    WHERE event_name = 'signup'
    GROUP BY user_id
),
funnel AS (
    SELECT
        s.user_id,
        s.signup_at,
        (
            SELECT min(v.event_at)
            FROM pro_analytics_lab.deduplicated_events AS v
            WHERE v.user_id = s.user_id
              AND v.event_name = 'view_item'
              AND v.event_at >= s.signup_at
        ) AS viewed_at
    FROM signup AS s
),
completed AS (
    SELECT
        f.*,
        (
            SELECT min(a.event_at)
            FROM pro_analytics_lab.deduplicated_events AS a
            WHERE a.user_id = f.user_id
              AND a.event_name = 'add_to_cart'
              AND a.event_at >= f.viewed_at
        ) AS added_at
    FROM funnel AS f
)
SELECT
    c.user_id,
    c.signup_at,
    c.viewed_at,
    c.added_at,
    (
        SELECT min(p.event_at)
        FROM pro_analytics_lab.deduplicated_events AS p
        WHERE p.user_id = c.user_id
          AND p.event_name = 'purchase'
          AND p.event_at >= c.added_at
    ) AS purchased_at
FROM completed AS c
ORDER BY c.user_id;

DO $solution$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pro_analytics_lab.deduplicated_events AS de
        GROUP BY de.source_event_id
        HAVING COUNT(*) <> 1
    ) THEN
        RAISE EXCEPTION 'deduplication grain failed';
    END IF;

    IF (SELECT COUNT(*) FROM pro_analytics_lab.deduplicated_events) <> 7 THEN
        RAISE EXCEPTION 'unexpected canonical event count';
    END IF;
END
$solution$;

ROLLBACK;

