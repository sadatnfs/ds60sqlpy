-- SQL-ANALYTICS-01 executable solutions
-- SOLUTION READING MAP — sql-analytics-01: Reusable Analytical Query Patterns
-- Explanation: sql/professional/solutions/sql_analytics_01_query_patterns_solutions.md
-- Run from the repository root only against advanced_sql_training:
--   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_analytics_01_query_patterns_solutions.sql
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
    ('A6', 1, 'active',      TIMESTAMPTZ '2026-01-02 09:00+00', TIMESTAMPTZ '2026-01-02 09:01+00'),
    ('A7', 1, 'active',      TIMESTAMPTZ '2026-02-01 09:00+00', TIMESTAMPTZ '2026-02-01 09:01+00'),
    ('B1', 2, 'signup',      TIMESTAMPTZ '2026-01-02 09:00+00', TIMESTAMPTZ '2026-01-02 09:01+00'),
    ('B2', 2, 'view_item',   TIMESTAMPTZ '2026-01-02 09:10+00', TIMESTAMPTZ '2026-01-02 09:11+00'),
    ('B3', 2, 'purchase',    TIMESTAMPTZ '2026-01-10 09:30+00', TIMESTAMPTZ '2026-01-10 09:31+00');

CREATE VIEW pro_analytics_lab.deduplicated_events AS
SELECT
    ingestion_id,
    source_event_id,
    user_id,
    event_name,
    event_at,
    ingested_at
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
    COUNT(*) AS canonical_rows,
    max(de.ingested_at) AS winner_ingested_at,
    max(de.ingestion_id) AS winner_ingestion_id
FROM pro_analytics_lab.deduplicated_events AS de
GROUP BY de.source_event_id
ORDER BY de.source_event_id;

-- Retried delivery is not automatically harmless. This diagnostic reveals one
-- source ID carrying conflicting business fields; an empty result is expected
-- for the reference fixture.
SELECT
    e.source_event_id,
    COUNT(DISTINCT ROW(e.user_id, e.event_name, e.event_at)) AS payload_versions
FROM pro_analytics_lab.events AS e
GROUP BY e.source_event_id
HAVING COUNT(DISTINCT ROW(e.user_id, e.event_name, e.event_at)) > 1
ORDER BY e.source_event_id;

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

-- Exercise 4: derive islands only after reducing to one row per user/day. User
-- 1 has a positive Jan 1-Jan 2 island; many Jan 1 events still count as one
-- active day.
WITH active_days AS (
    SELECT DISTINCT de.user_id, de.event_at::date AS activity_date
    FROM pro_analytics_lab.deduplicated_events AS de
),
numbered AS (
    SELECT
        ad.*,
        ad.activity_date
        - row_number() OVER (
            PARTITION BY ad.user_id
            ORDER BY ad.activity_date
        )::integer AS island_key
    FROM active_days AS ad
)
SELECT
    n.user_id,
    min(n.activity_date) AS island_start,
    max(n.activity_date) AS island_end,
    COUNT(*) AS active_days
FROM numbered AS n
GROUP BY n.user_id, n.island_key
HAVING COUNT(*) >= 2
ORDER BY n.user_id, island_start;

-- Exercise 5: attribution needs separate touch/purchase fixture rows. The
-- reference rule is LEFT LATERAL, ordered touched_at DESC, touch_id DESC, so
-- purchases with no qualifying touch remain with NULL attribution.
CREATE TABLE pro_analytics_lab.campaign_touches (
    touch_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id bigint NOT NULL,
    campaign text NOT NULL,
    touched_at timestamptz NOT NULL
);

INSERT INTO pro_analytics_lab.campaign_touches (
    user_id, campaign, touched_at
)
VALUES
    (1, 'search', TIMESTAMPTZ '2026-01-01 08:00+00'),
    (1, 'email-a', TIMESTAMPTZ '2026-01-01 09:15+00'),
    (1, 'email-b', TIMESTAMPTZ '2026-01-01 09:15+00');

SELECT
    p.source_event_id,
    p.user_id,
    p.event_at AS purchased_at,
    selected.touch_id,
    selected.campaign,
    selected.touched_at
FROM pro_analytics_lab.deduplicated_events AS p
LEFT JOIN LATERAL (
    SELECT
        t.touch_id,
        t.campaign,
        t.touched_at
    FROM pro_analytics_lab.campaign_touches AS t
    WHERE t.user_id = p.user_id
      AND t.touched_at <= p.event_at
      AND t.touched_at > p.event_at - INTERVAL '7 days'
    ORDER BY t.touched_at DESC, t.touch_id DESC
    LIMIT 1
) AS selected
  ON true
WHERE p.event_name = 'purchase'
ORDER BY p.source_event_id;

-- Exercise 6: expose cohort denominator and retained numerator before division.
WITH cohorts AS (
    SELECT
        de.user_id,
        date_trunc('month', min(de.event_at))::date AS cohort_month
    FROM pro_analytics_lab.deduplicated_events AS de
    GROUP BY de.user_id
),
activity AS (
    SELECT DISTINCT
        de.user_id,
        date_trunc('month', de.event_at)::date AS activity_month
    FROM pro_analytics_lab.deduplicated_events AS de
)
SELECT
    c.cohort_month,
    COUNT(DISTINCT c.user_id) AS cohort_users,
    COUNT(DISTINCT a.user_id) FILTER (
        WHERE a.activity_month = (c.cohort_month + INTERVAL '1 month')::date
    ) AS month_1_users,
    round(
        COUNT(DISTINCT a.user_id) FILTER (
            WHERE a.activity_month
                  = (c.cohort_month + INTERVAL '1 month')::date
        )::numeric
        / NULLIF(COUNT(DISTINCT c.user_id), 0),
        4
    ) AS month_1_rate
FROM cohorts AS c
LEFT JOIN activity AS a
  ON a.user_id = c.user_id
GROUP BY c.cohort_month
ORDER BY c.cohort_month;

DO $solution$
DECLARE
    january_cohort_users bigint;
    january_month_1_users bigint;
BEGIN
    WITH cohorts AS (
        SELECT
            de.user_id,
            date_trunc('month', min(de.event_at))::date AS cohort_month
        FROM pro_analytics_lab.deduplicated_events AS de
        GROUP BY de.user_id
    ),
    activity AS (
        SELECT DISTINCT
            de.user_id,
            date_trunc('month', de.event_at)::date AS activity_month
        FROM pro_analytics_lab.deduplicated_events AS de
    )
    SELECT
        count(DISTINCT c.user_id),
        count(DISTINCT a.user_id) FILTER (
            WHERE a.activity_month = DATE '2026-02-01'
        )
    INTO january_cohort_users, january_month_1_users
    FROM cohorts AS c
    LEFT JOIN activity AS a
      ON a.user_id = c.user_id
    WHERE c.cohort_month = DATE '2026-01-01';

    IF january_cohort_users <> 2 OR january_month_1_users <> 1 THEN
        RAISE EXCEPTION
            'month-1 retention fixture drifted: expected 1/2, got %/%',
            january_month_1_users,
            january_cohort_users;
    END IF;
END
$solution$;

-- Exercise 7: the as-of contract is valid_from <= event_at AND
-- event_at < valid_to. It must assert at most one match, not hide overlap with
-- ORDER BY/LIMIT 1.
CREATE TABLE pro_analytics_lab.user_tiers (
    user_id bigint NOT NULL,
    tier_name text NOT NULL,
    valid_from timestamptz NOT NULL,
    valid_to timestamptz,
    PRIMARY KEY (user_id, valid_from),
    CHECK (valid_to IS NULL OR valid_to > valid_from)
);

CREATE TABLE pro_analytics_lab.event_probes (
    probe_id text PRIMARY KEY,
    user_id bigint NOT NULL,
    event_at timestamptz NOT NULL
);

INSERT INTO pro_analytics_lab.user_tiers
VALUES
    (1, 'basic', TIMESTAMPTZ '2026-01-01 00:00+00', TIMESTAMPTZ '2026-01-10 00:00+00'),
    (1, 'pro', TIMESTAMPTZ '2026-01-10 00:00+00', NULL);

INSERT INTO pro_analytics_lab.event_probes
VALUES
    ('before', 1, TIMESTAMPTZ '2026-01-09 23:59:59+00'),
    ('boundary', 1, TIMESTAMPTZ '2026-01-10 00:00:00+00'),
    ('after', 1, TIMESTAMPTZ '2026-01-10 00:00:01+00');

SELECT
    p.probe_id,
    p.event_at,
    min(t.tier_name) AS tier_name,
    min(t.valid_from) AS valid_from,
    min(t.valid_to) AS valid_to,
    COUNT(t.tier_name) AS matching_tiers
FROM pro_analytics_lab.event_probes AS p
LEFT JOIN pro_analytics_lab.user_tiers AS t
  ON t.user_id = p.user_id
 AND t.valid_from <= p.event_at
 AND p.event_at < COALESCE(t.valid_to, 'infinity'::timestamptz)
GROUP BY p.probe_id, p.event_at
ORDER BY p.probe_id;

DO $solution$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pro_analytics_lab.event_probes AS p
        JOIN pro_analytics_lab.user_tiers AS t
          ON t.user_id = p.user_id
         AND t.valid_from <= p.event_at
         AND p.event_at < COALESCE(t.valid_to, 'infinity'::timestamptz)
        GROUP BY p.probe_id
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'an event probe matched overlapping tier rows';
    END IF;
END
$solution$;

-- Exercise 8: a dense spine preserves calendar meaning for the trailing window.
WITH spine AS (
    SELECT day::date AS report_date
    FROM generate_series(
        DATE '2026-01-01',
        DATE '2026-01-08',
        INTERVAL '1 day'
    ) AS day
)
SELECT
    s.report_date,
    (
        SELECT COUNT(DISTINCT de.user_id)
        FROM pro_analytics_lab.deduplicated_events AS de
        WHERE de.event_at >= s.report_date::timestamp
                              AT TIME ZONE 'UTC' - INTERVAL '6 days'
          AND de.event_at < (s.report_date + 1)::timestamp
                             AT TIME ZONE 'UTC'
    ) AS trailing_7d_active_users
FROM spine AS s
ORDER BY s.report_date;

-- Exercise 9: percentile input is exactly one row per derived session.
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
        l.*,
        sum(
            CASE
                WHEN l.previous_at IS NULL
                  OR l.event_at - l.previous_at > INTERVAL '60 minutes'
                THEN 1 ELSE 0
            END
        ) OVER (
            PARTITION BY l.user_id
            ORDER BY l.event_at, l.source_event_id
            ROWS UNBOUNDED PRECEDING
        ) AS session_number
    FROM lagged AS l
),
sessions AS (
    SELECT
        n.user_id,
        n.session_number,
        max(n.event_at) - min(n.event_at) AS duration
    FROM numbered AS n
    GROUP BY n.user_id, n.session_number
)
SELECT
    COUNT(*) AS session_count,
    percentile_cont(ARRAY[0.5, 0.9])
        WITHIN GROUP (ORDER BY s.duration) AS median_and_p90
FROM sessions AS s;

-- Exercise 10: compare rank semantics before choosing the top-N contract.
WITH counts AS (
    SELECT de.user_id, de.event_name, COUNT(*) AS event_count
    FROM pro_analytics_lab.deduplicated_events AS de
    GROUP BY de.user_id, de.event_name
)
SELECT
    c.*,
    row_number() OVER (
        PARTITION BY c.user_id
        ORDER BY c.event_count DESC, c.event_name
    ) AS row_number_position,
    rank() OVER (
        PARTITION BY c.user_id ORDER BY c.event_count DESC
    ) AS rank_position,
    dense_rank() OVER (
        PARTITION BY c.user_id ORDER BY c.event_count DESC
    ) AS dense_rank_position
FROM counts AS c
ORDER BY c.user_id, row_number_position;

-- Exercise 11: carry a visited-ID path and refuse to recurse into it.
CREATE TABLE pro_analytics_lab.campaign_nodes (
    campaign_id integer PRIMARY KEY,
    parent_campaign_id integer
);

INSERT INTO pro_analytics_lab.campaign_nodes
VALUES
    (1, NULL), (2, 1), (3, 2), (4, 3),
    (5, 6), (6, 5);

WITH RECURSIVE tree AS (
    SELECT
        c.campaign_id,
        c.parent_campaign_id,
        0 AS depth,
        ARRAY[c.campaign_id] AS path
    FROM pro_analytics_lab.campaign_nodes AS c
    WHERE c.parent_campaign_id IS NULL

    UNION ALL

    SELECT
        child.campaign_id,
        child.parent_campaign_id,
        tree.depth + 1,
        tree.path || child.campaign_id
    FROM tree
    JOIN pro_analytics_lab.campaign_nodes AS child
      ON child.parent_campaign_id = tree.campaign_id
    WHERE NOT child.campaign_id = ANY (tree.path)
)
SELECT campaign_id, parent_campaign_id, depth, path
FROM tree
ORDER BY path;

WITH RECURSIVE reachable AS (
    SELECT
        c.campaign_id,
        ARRAY[c.campaign_id] AS path
    FROM pro_analytics_lab.campaign_nodes AS c
    WHERE c.parent_campaign_id IS NULL

    UNION ALL

    SELECT
        child.campaign_id,
        reachable.path || child.campaign_id
    FROM reachable
    JOIN pro_analytics_lab.campaign_nodes AS child
      ON child.parent_campaign_id = reachable.campaign_id
    WHERE NOT child.campaign_id = ANY (reachable.path)
)
SELECT c.campaign_id AS unreachable_campaign_id
FROM pro_analytics_lab.campaign_nodes AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM reachable AS r
    WHERE r.campaign_id = c.campaign_id
)
ORDER BY c.campaign_id;

-- Exercise 12: start from dates and keep event filters in the join/aggregate.
WITH spine AS (
    SELECT day::date AS report_date
    FROM generate_series(
        DATE '2026-01-01',
        DATE '2026-01-04',
        INTERVAL '1 day'
    ) AS day
)
SELECT
    s.report_date,
    COUNT(DISTINCT de.user_id) FILTER (
        WHERE de.event_name = 'signup'
    ) AS signups,
    COUNT(DISTINCT de.user_id) FILTER (
        WHERE de.event_name = 'purchase'
    ) AS purchasers
FROM spine AS s
LEFT JOIN pro_analytics_lab.deduplicated_events AS de
  ON de.event_at >= s.report_date::timestamp AT TIME ZONE 'UTC'
 AND de.event_at < (s.report_date + 1)::timestamp AT TIME ZONE 'UTC'
GROUP BY s.report_date
ORDER BY s.report_date;

-- Exercise 13: core PostgreSQL gives an exact answer. An approximate sketch
-- requires an approved implementation and a measured error/merge contract.
SELECT COUNT(DISTINCT de.user_id) AS exact_distinct_users
FROM pro_analytics_lab.deduplicated_events AS de;

SELECT *
FROM (
    VALUES
        (1, 'implementation/version', 'name the approved sketch and serialized format'),
        (2, 'error budget', 'measure relative error at expected cardinalities'),
        (3, 'mergeability', 'prove period sketches combine without summing estimates'),
        (4, 'fallback', 'use exact count when capability or accuracy is unavailable'),
        (5, 'ownership', 'name monitoring, upgrade, privacy, and rebuild owners')
) AS approximation_review(criterion_number, criterion, required_evidence)
ORDER BY criterion_number;

-- Exercise 14: reject invalid parameters before applying the half-open bound.
CREATE FUNCTION pro_analytics_lab.valid_time_window(
    p_starts_at timestamptz,
    p_ends_at timestamptz
)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $function$
BEGIN
    IF p_starts_at IS NULL
       OR p_ends_at IS NULL
       OR p_ends_at <= p_starts_at THEN
        RAISE EXCEPTION USING
            ERRCODE = '22023',
            MESSAGE = 'ends_at must be greater than starts_at';
    END IF;
    RETURN true;
END
$function$;

WITH parameters AS (
    SELECT
        TIMESTAMPTZ '2026-01-01 00:00+00' AS starts_at,
        TIMESTAMPTZ '2026-02-01 00:00+00' AS ends_at
)
SELECT de.source_event_id, de.event_at
FROM pro_analytics_lab.deduplicated_events AS de
CROSS JOIN parameters AS p
WHERE pro_analytics_lab.valid_time_window(p.starts_at, p.ends_at)
  AND de.event_at >= p.starts_at
  AND de.event_at < p.ends_at
ORDER BY de.event_at, de.source_event_id;

DO $solution$
BEGIN
    BEGIN
        PERFORM pro_analytics_lab.valid_time_window(
            TIMESTAMPTZ '2026-01-02 00:00+00',
            TIMESTAMPTZ '2026-01-01 00:00+00'
        );
        RAISE EXCEPTION 'reversed window unexpectedly passed';
    EXCEPTION
        WHEN invalid_parameter_value THEN
            RAISE NOTICE 'Expected invalid time window was rejected';
    END;
END
$solution$;

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

    IF (SELECT COUNT(*) FROM pro_analytics_lab.deduplicated_events) <> 10 THEN
        RAISE EXCEPTION 'unexpected canonical event count';
    END IF;
END
$solution$;

ROLLBACK;
