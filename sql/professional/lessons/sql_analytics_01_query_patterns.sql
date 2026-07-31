-- SQL-ANALYTICS-01: Reusable analytical query patterns
-- BEGINNER WORKFLOW — sql-analytics-01: Reusable Analytical Query Patterns
-- Guide: sql/professional/companion-guides/sql_analytics_01_query_patterns.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-analytics-01/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: pro_analytics_lab.users, pro_analytics_lab.events, pro_analytics_lab.daily_activity, pro_analytics_lab.campaign_touches, pro_analytics_lab.tier_history.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
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
--    Inputs: For sql-analytics-01 Exercise 1, complete the deduplication written analysis and support its claims with read-only evidence from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Mark unverified assumptions explicitly.
--    Expected result/shape: For sql-analytics-01 Exercise 1, expected output: a completed the deduplication written analysis with explicit `decision`, `evidence`, `owner`, `failure_response`, `fallback`, and `rollback_limit` fields. The final columns are `source_event_id`, `ingested_at`, and `ingestion_id`.
--    Verify: For sql-analytics-01 Exercise 1, check the deduplication written analysis against `source_event_id`, `ingested_at`, and `ingestion_id`. Each recommendation must cite an observed catalog/query result or be labeled an assumption, and must name an owner, failure response, fallback, and rollback/rebuild limit. Add one counterexample that invalidates the preferred decision and show which `fallback` and `rollback_limit` entries govern it.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 1, check the deduplication written analysis against `source_event_id`, `ingested_at`, and `ingestion_id`.
-- 2. Recalculate sessions with a 60-minute threshold and add duration. Decide
--    whether an event exactly 60 minutes later starts a new session.
--    Inputs: For sql-analytics-01 Exercise 2, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `user_id`, `session_number`, `started_at`, `ended_at`, `duration`, and `events`; keep `user_id`, and `session_number` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-analytics-01 Exercise 2, expected output: one row per `user_id`, and `session_number`. The final columns are `user_id`, `session_number`, `started_at`, `ended_at`, `duration`, and `events`. The final order is `user_id, session_number`.
--    Verify: For sql-analytics-01 Exercise 2, independently aggregate `pro_analytics_lab.deduplicated_events` by `user_id`, and `session_number`; require one output row for every distinct `user_id`, and `session_number` tuple and compare `duration`, and `events` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `duration`, and `events` for the existing `user_id`, and `session_number` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 2, run `lagged`, and `numbered` one at a time. Record each CTE's row count and `user_id`, and `session_number` uniqueness before the next stage uses it.
-- 3. Return one row per user with every funnel timestamp, then test that each
--    non-NULL step is no earlier than its predecessor.
--    Inputs: For sql-analytics-01 Exercise 3, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at`; keep `user_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-analytics-01 Exercise 3, expected output: one row per `user_id`. The final columns are `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at`. The final order is `c.user_id`.
--    Verify: For sql-analytics-01 Exercise 3, reselect the returned keys directly from the source; require unique `user_id` where the expected grain is one row per key and confirm the projected `user_id`, `signup_at`, `viewed_at`, `added_at`, and `purchased_at` against `pro_analytics_lab.deduplicated_events`. Add one source row with a new `user_id`; verify the result gains exactly one row carrying that `user_id` value.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 3, run `signup`, `funnel`, and `completed` one at a time. Record each CTE's row count and `user_id` uniqueness before the next stage uses it.
-- 4. Return only islands lasting at least two active days.
--    Inputs: For sql-analytics-01 Exercise 4, read from `pro_analytics_lab.deduplicated_events`. Compute `user_id`, `island_start`, `island_end`, and `active_days` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-analytics-01 Exercise 4, expected output: one row per user-date. The final columns are `user_id`, `island_start`, `island_end`, and `active_days`. The final order is `n.user_id, island_start`.
--    Verify: For sql-analytics-01 Exercise 4, evaluate each of `island_start`, `island_end`, and `active_days` in a separate control `SELECT` over `pro_analytics_lab.deduplicated_events`; require one final row and compare every value. Add one row to an existing group and one row for a new group; recompute `island_start`, `island_end`, and `active_days` for the existing `user_id`, and `island_key` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 4, run `active_days`, and `numbered` one at a time. Record each CTE's row count and `user_id`, and `island_key` uniqueness before the next stage uses it.
-- 5. Add an unattributed purchase and two touches at the same timestamp. Define
--    and test the deterministic tie-break and NULL attribution behavior.
--    Inputs: For sql-analytics-01 Exercise 5, read from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Build the answer toward `touched_at`, and `touch_id`; keep `touch_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-analytics-01 Exercise 5, expected output: one row per `touch_id`. The final columns are `touched_at`, and `touch_id`.
--    Verify: For sql-analytics-01 Exercise 5, reselect the returned keys directly from the source; require unique `touch_id` where the expected grain is one row per key and confirm the projected `touched_at`, and `touch_id` against `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Add two tied candidates and prove `touch_id` identifies both without accidental loss.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 5, select `touch_id` from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity` before adding derived columns.
-- 6. Add month 1 activity and verify numerator, cohort denominator, and rate
--    independently before division.
--    Inputs: For sql-analytics-01 Exercise 6, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `cohort_month`, `cohort_users`, and `month_1_users`; keep `cohort_month` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-analytics-01 Exercise 6, expected output: one row per `cohort_month`. The final columns are `cohort_month`, `cohort_users`, and `month_1_users`. The final order is `c.cohort_month`.
--    Verify: For sql-analytics-01 Exercise 6, independently aggregate `pro_analytics_lab.deduplicated_events` by `cohort_month`; require one output row for every distinct `cohort_month` tuple and compare `cohort_users`, and `month_1_users` tuple by tuple. Add one row to an existing group and one row for a new group; recompute `cohort_users`, and `month_1_users` for the existing `cohort_month` tuple and verify the new tuple appears exactly once.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 6, run `cohorts`, and `activity` one at a time. Record each CTE's row count and `cohort_month` uniqueness before the next stage uses it.
-- 7. Add an event exactly at a tier valid_to boundary and prove it joins the
--    successor [valid_from, valid_to) row, not both rows.
--    Inputs: For sql-analytics-01 Exercise 7, read from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Build the answer toward `valid_from`, `event_at`, and `valid_to`; keep `valid_from` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-analytics-01 Exercise 7, expected output: one row per `valid_from`. The final columns are `valid_from`, `event_at`, and `valid_to`.
--    Verify: For sql-analytics-01 Exercise 7, reselect the returned keys directly from the source; require unique `valid_from` where the expected grain is one row per key and confirm the projected `valid_from`, `event_at`, and `valid_to` against `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity`. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 7, select `valid_from` from `pro_analytics_lab.users`, `pro_analytics_lab.events`, and `pro_analytics_lab.daily_activity` before adding derived columns.
-- 8. Compute a trailing seven-day active-user metric over a dense date spine.
--    Compare ROWS and RANGE frames and prove missing calendar dates do not
--    silently change the business window.
--    Inputs: For sql-analytics-01 Exercise 8, read from `pro_analytics_lab.deduplicated_events`. Compute `report_date`, and `trailing_7d_active_users` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-analytics-01 Exercise 8, expected output: one row per calendar date in the requested business zone and LEFT JOIN deduplicated activity by local date. The final columns are `report_date`, and `trailing_7d_active_users`. The final order is `s.report_date`.
--    Verify: For sql-analytics-01 Exercise 8, evaluate each of `report_date`, and `trailing_7d_active_users` in a separate control `SELECT` over `pro_analytics_lab.deduplicated_events`; require one final row and compare every value. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 8, run `spine` one at a time. Record each CTE's row count and `report_date` uniqueness before the next stage uses it.
-- 9. Calculate median and 90th-percentile session duration with percentile_cont.
--    State input/output grain, interpolation behavior, NULL handling, and why
--    an average cannot answer the same distribution question.
--    Inputs: For sql-analytics-01 Exercise 9, use `pro_analytics_lab.deduplicated_events` in a disposable restore target. Record artifact identity, PostgreSQL/tool versions, command exit status, start/end time, and the requested recovery point.
--    Expected result/shape: For sql-analytics-01 Exercise 9, expected output: one row per session with duration. The final columns are `session_count`, and `median_and_p90`.
--    Verify: For sql-analytics-01 Exercise 9, restore into an isolated target and reconcile `pro_analytics_lab.deduplicated_events` using schema inventory, object/row counts, key samples, critical aggregates/checksums, application smoke tests, and an explicit cleanup result. Inject one missing or invalid artifact in the disposable target and prove validation stops before cutover.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 9, run `lagged`, `numbered`, and `sessions` one at a time. Record each CTE's row count and `artifact_name` and `restored_object` uniqueness before the next stage uses it.
-- 10. Return the top two event types per user with row_number, rank, and
--     dense_rank side by side. Define a deterministic tie policy and explain
--     when each ranking function changes the number of returned rows.
--    Inputs: For sql-analytics-01 Exercise 10, read from `pro_analytics_lab.deduplicated_events`. Compute `user_id`, and `event_name` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-analytics-01 Exercise 10, expected output: one row per `(user_id,event_name)`, then calculate all three functions ordered by count descending. The final columns are `user_id`, and `event_name`. The final order is `c.user_id, row_number_position`.
--    Verify: For sql-analytics-01 Exercise 10, evaluate each of `event_name` in a separate control `SELECT` over `pro_analytics_lab.deduplicated_events`; require one final row and compare every value. Give two rows the same `c.user_id` value and different `row_number_position` values; verify `c.user_id, row_number_position` produces the intended rank and display order.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 10, run `counts` one at a time. Record each CTE's row count and `user_id` uniqueness before the next stage uses it.
-- 11. Traverse a parent/child campaign hierarchy with a recursive CTE. Include
--     depth, a path, and cycle detection; prove malformed cyclic input
--     terminates rather than looping until a resource limit.
--    Inputs: For sql-analytics-01 Exercise 11, read from `pro_analytics_lab.campaign_nodes`, and `tree`. Compute `campaign_id`, `parent_campaign_id`, `depth`, and `path` with no outer `GROUP BY`; return exactly one aggregate row and label every expression.
--    Expected result/shape: For sql-analytics-01 Exercise 11, expected output: one row per node in a multi-parent graph. The final columns are `campaign_id`, `parent_campaign_id`, `depth`, and `path`. The final order is `path`.
--    Verify: For sql-analytics-01 Exercise 11, evaluate each of `parent_campaign_id`, `depth`, and `path` in a separate control `SELECT` over `pro_analytics_lab.campaign_nodes`, and `tree`; require one final row and compare every value. Add one source row with a new `campaign_id`; verify the result gains exactly one row carrying that `campaign_id` value.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 11, start with the first relation in `pro_analytics_lab.campaign_nodes`, and `tree`; after each join, record total rows and distinct `campaign_id` so the exact fanout or loss is visible.
-- 12. Build a daily funnel report that retains zero-activity dates. Keep event
--     filters in the appropriate JOIN condition, make each denominator
--     explicit, and distinguish zero from missing data.
--    Inputs: For sql-analytics-01 Exercise 12, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `report_date`, `signups`, and `purchasers`; keep `report_date` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-analytics-01 Exercise 12, expected output: one row per `report_date`. The final columns are `report_date`, `signups`, and `purchasers`. The final order is `s.report_date`.
--    Verify: For sql-analytics-01 Exercise 12, independently aggregate `pro_analytics_lab.deduplicated_events` by `report_date`; require one output row for every distinct `report_date` tuple and compare `signups`, and `purchasers` tuple by tuple. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 12, run `spine` one at a time. Record each CTE's row count and `report_date` uniqueness before the next stage uses it.
-- 13. Compare an exact distinct-user count with a documented approximate
--     strategy suitable for very large data. Define acceptable error, memory,
--     mergeability, refresh, and verification requirements before choosing.
--    Inputs: For sql-analytics-01 Exercise 13, read the target keys from `pro_analytics_lab.deduplicated_events` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-analytics-01 Exercise 13, expected output: the command tag and an independently counted set of affected `exact_distinct_users` values. The final columns are `exact_distinct_users`.
--    Verify: For sql-analytics-01 Exercise 13, materialize the intended `exact_distinct_users` target set first; require the command tag/`RETURNING` set to match it, then query `pro_analytics_lab.deduplicated_events` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `exact_distinct_users` values in both cases.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 13, materialize the intended `exact_distinct_users` target set first; require the command tag/`RETURNING` set to match it, then query `pro_analytics_lab.deduplicated_events` again and prove rollback or idempotent retry.
-- 14. Turn one analysis into a reusable parameterized query. Validate time-zone,
--     interval, and cohort inputs; preserve half-open bounds and deterministic
--     order; add grain, duplicate, NULL, and boundary contract checks.

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
--    Inputs: For sql-analytics-01 Exercise 14, read from `pro_analytics_lab.deduplicated_events`. Build the answer toward `source_event_id`, and `event_at`; keep `source_event_id` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-analytics-01 Exercise 14, expected output: one row per `source_event_id`. The final columns are `source_event_id`, and `event_at`. The final order is `de.event_at, de.source_event_id`.
--    Verify: For sql-analytics-01 Exercise 14, project `source_event_id` plus the raw source columns from `pro_analytics_lab.deduplicated_events` at each join stage; record row count and distinct `source_event_id`, then assert the final `source_event_id`, and `event_at` values match those staged rows without unintended fanout or loss. Repeat with `NULL` in `source_event_id`, and `event_at` and state whether the row is kept, rejected, or classified.
--    Hint ladder, rung 1: For sql-analytics-01 Exercise 14, run `parameters` one at a time. Record each CTE's row count and `source_event_id` uniqueness before the next stage uses it.

ROLLBACK;
\echo 'SQL-ANALYTICS-01 complete: pro_analytics_lab was rolled back'
