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

-- Exercise 4: derive islands only after reducing to one row per user/day. This
-- fixture has no multi-day island, so the deterministic result is empty.
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
    ) AS month_1_users
FROM cohorts AS c
LEFT JOIN activity AS a
  ON a.user_id = c.user_id
GROUP BY c.cohort_month
ORDER BY c.cohort_month;

-- Exercise 7: the as-of contract is valid_from <= event_at AND
-- event_at < valid_to. It must assert at most one match, not hide overlap with
-- ORDER BY/LIMIT 1.

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
VALUES (1, NULL), (2, 1), (3, 2), (4, 3);

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

-- Exercise 14: validate parameters before applying the same half-open bound.
WITH parameters AS (
    SELECT
        TIMESTAMPTZ '2026-01-01 00:00+00' AS starts_at,
        TIMESTAMPTZ '2026-02-01 00:00+00' AS ends_at
)
SELECT de.source_event_id, de.event_at
FROM pro_analytics_lab.deduplicated_events AS de
CROSS JOIN parameters AS p
WHERE p.ends_at > p.starts_at
  AND de.event_at >= p.starts_at
  AND de.event_at < p.ends_at
ORDER BY de.event_at, de.source_event_id;

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
