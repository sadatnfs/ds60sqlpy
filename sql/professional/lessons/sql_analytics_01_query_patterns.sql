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
    -- User 1 returns in month 1; user 2 does not. That deliberate contrast
    -- makes the January cohort's 1 / 2 = 0.5000 retention visible below.
    (1, DATE '2026-02-01'),
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
    ranked.ingestion_id,
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
    touch.touch_id,
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
    history.tier,
    history.valid_from,
    history.valid_to,
    count(history.tier) OVER (
        PARTITION BY de.source_event_id
    ) AS matching_tiers
FROM pro_analytics_lab.deduplicated_events AS de
LEFT JOIN pro_analytics_lab.tier_history AS history
  ON history.user_id = de.user_id
 AND history.valid_from <= de.event_at
 AND (history.valid_to IS NULL OR de.event_at < history.valid_to)
WHERE de.event_name = 'purchase'
ORDER BY de.source_event_id;

DO $as_of_invariant$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pro_analytics_lab.deduplicated_events AS de
        JOIN pro_analytics_lab.tier_history AS history
          ON history.user_id = de.user_id
         AND history.valid_from <= de.event_at
         AND (history.valid_to IS NULL OR de.event_at < history.valid_to)
        WHERE de.event_name = 'purchase'
        GROUP BY de.source_event_id
        HAVING count(*) > 1
    ) THEN
        RAISE EXCEPTION 'a purchase matched overlapping tier-history rows';
    END IF;
END
$as_of_invariant$;

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

DO $retention_fixture_invariant$
DECLARE
    january_cohort_users bigint;
    january_month_1_users bigint;
BEGIN
    SELECT
        count(DISTINCT u.user_id),
        count(DISTINCT da.user_id) FILTER (
            WHERE da.activity_date >= DATE '2026-02-01'
              AND da.activity_date < DATE '2026-03-01'
        )
    INTO january_cohort_users, january_month_1_users
    FROM pro_analytics_lab.users AS u
    LEFT JOIN pro_analytics_lab.daily_activity AS da
      ON da.user_id = u.user_id
    WHERE u.signup_at >= TIMESTAMPTZ '2026-01-01 00:00:00+00'
      AND u.signup_at < TIMESTAMPTZ '2026-02-01 00:00:00+00';

    IF january_cohort_users <> 2 OR january_month_1_users <> 1 THEN
        RAISE EXCEPTION
            'retention fixture drifted: expected January month-1 retention 1/2, got %/%',
            january_month_1_users,
            january_cohort_users;
    END IF;
END
$retention_fixture_invariant$;

-- Exercises:
--
-- 1. Prove the dedup view has one row per source_event_id and document why the
--    latest ingested row wins.
--    Inputs: Compare `pro_analytics_lab.events` with
--    `pro_analytics_lab.deduplicated_events`. The winner order is
--    `ingested_at DESC, ingestion_id DESC` within each `source_event_id`.
--    Expected result/shape: One row per `source_event_id`, with
--    `source_event_id`, `canonical_rows`, `winner_ingested_at`, and
--    `winner_ingestion_id`, ordered by `source_event_id`; every
--    `canonical_rows` value is 1.
--    Verify: Independently rank the raw rows and prove source `A4` keeps the
--    later ingestion. Insert two copies with equal `ingested_at` and prove the
--    greater `ingestion_id` wins; separately flag conflicting business payload
--    for one source ID instead of silently calling it a harmless retry.
--    Hint ladder, rung 1: Deduplicate delivery attempts before any downstream
--    funnel, session, or retention aggregate.
-- 2. Recalculate sessions with a 60-minute threshold and add duration. Decide
--    whether an event exactly 60 minutes later starts a new session.
--    Inputs: Order canonical events by `event_at, source_event_id` per
--    `user_id`; start a new session only when the prior gap is greater than
--    `INTERVAL '60 minutes'`.
--    Expected result/shape: One row per `(user_id, session_number)`, with
--    `user_id`, `session_number`, `started_at`, `ended_at`, `duration`, and
--    `events`, ordered by `user_id, session_number`.
--    Verify: An event exactly 60 minutes later stays in the same session; a
--    60-minute-and-one-second gap starts another. Session event counts must sum
--    to the canonical event count, and a one-event session has zero duration.
--    Hint ladder, rung 1: Compute `lag()`, then a 0/1 boundary flag, then its
--    running sum; aggregate only after every event has a session number.
-- 3. Return one row per user with every funnel timestamp, then test that each
--    non-NULL step is no earlier than its predecessor.
--    Inputs: Anchor on each user's earliest canonical `signup`, then choose the
--    first `view_item`, `add_to_cart`, and `purchase` at or after the preceding
--    non-NULL step.
--    Expected result/shape: One row per user who has a signup, with `user_id`,
--    `signup_at`, `viewed_at`, `added_at`, and `purchased_at`, ordered by
--    `user_id`. Missing predecessors leave later steps NULL.
--    Verify: Require the non-NULL chain to be nondecreasing. A user with only a
--    view does not appear; a user with signup but no later step appears once
--    with NULL later timestamps.
--    Hint ladder, rung 1: A pre-signup event cannot satisfy a later funnel
--    step; each step is bounded by the timestamp chosen for its predecessor.
-- 4. Return only islands lasting at least two active days.
--    Inputs: Reduce canonical events to distinct `(user_id, activity_date)`
--    rows, derive an island key from date minus row number, and group by
--    `(user_id, island_key)`.
--    Expected result/shape: One row per consecutive-day island lasting at
--    least two days, with `user_id`, `island_start`, `island_end`, and
--    `active_days`, ordered by `user_id, island_start`.
--    Verify: Include a positive two-day island, a one-day island, a gap, and a
--    duplicate event on one active date. Only the consecutive run survives;
--    the duplicate does not inflate `active_days`.
--    Hint ladder, rung 1: Collapse multiple events on one date before numbering
--    dates and grouping islands.
-- 5. Add an unattributed purchase and two touches at the same timestamp. Define
--    and test the deterministic tie-break and NULL attribution behavior.
--    Inputs: Use `pro_analytics_lab.campaign_touches` and purchase rows from
--    `pro_analytics_lab.deduplicated_events`. For each purchase, choose at most
--    one touch in the preceding seven days with a LEFT LATERAL join ordered by
--    `touched_at DESC, touch_id DESC`.
--    Expected result/shape: One row per purchase `source_event_id`, with
--    `source_event_id`,
--    `user_id`, `purchased_at`, `touch_id`, `campaign`, and `touched_at`,
--    ordered by `source_event_id`. Unattributed purchases retain NULL touch fields;
--    greater `touch_id` wins an equal-time tie.
--    Verify: Output count equals purchase count and `source_event_id` is unique.
--    Remove the ID tie-breaker in a disposable copy and explain why a chosen
--    campaign is no longer deterministic.
--    Hint ladder, rung 1: Put window predicates inside the lateral subquery and
--    keep the outer join LEFT so unmatched purchases survive.
-- 6. Add month 1 activity and verify numerator, cohort denominator, and rate
--    independently before division.
--    Inputs: Define each user's cohort as the month of that user's earliest
--    canonical event, then reduce activity to distinct user/month rows.
--    Expected result/shape: One row per `cohort_month`, with `cohort_month`,
--    `cohort_users`, `month_1_users`, and `month_1_rate`, ordered by
--    `cohort_month`. The denominator includes users with no month-1 activity.
--    Verify: Independently list cohort and month-1 members and compare both
--    distinct counts. The fixture must include one retained and one nonretained
--    cohort member; adding another nonretained member changes only the
--    denominator and rate.
--    Hint ladder, rung 1: Keep cohort membership separate from activity
--    membership so the LEFT JOIN cannot shrink the denominator.
-- 7. Add an event exactly at a tier valid_to boundary and prove it joins the
--    successor [valid_from, valid_to) row, not both rows.
--    Inputs: Use adjacent half-open rows in
--    `pro_analytics_lab.tier_history(user_id, tier, valid_from, valid_to)` and
--    an inline `event_probes(probe_id, user_id, event_at)` CTE, including a
--    probe exactly at the shared boundary.
--    Expected result/shape: One row per `probe_id`, with `probe_id`, `event_at`,
--    `tier_name`, `valid_from`, `valid_to`, and `matching_tiers`, ordered by
--    `probe_id`. The boundary probe matches the successor exactly once.
--    Verify: Use `valid_from <= event_at` and
--    `event_at < COALESCE(valid_to, 'infinity')`, and assert no probe has more
--    than one match. Add an overlap and prove that assertion fails rather than
--    hiding the duplicate with `LIMIT 1`.
--    Hint ladder, rung 1: At the upper boundary `< valid_to` excludes the old
--    row while `valid_from <= event_at` includes the successor.
-- 8. Compute a trailing seven-day active-user metric over a dense date spine.
--    Compare ROWS and RANGE frames and prove missing calendar dates do not
--    silently change the business window.
--    Inputs: Generate the eight UTC business dates from 2026-01-01 through
--    2026-01-08; for each date count distinct users in the inclusive
--    seven-calendar-day window ending on that date.
--    Expected result/shape: Exactly eight rows, one per `report_date`, with
--    `report_date` and `trailing_7d_active_users`, ordered by `report_date`;
--    dates with no activity remain.
--    Verify: Independently list the distinct users for two dates using
--    `[report_date - 6 days, report_date + 1 day)`. Add the same user on two
--    days and prove the weekly unique count rises by at most one, unlike a sum
--    of daily distinct counts.
--    Hint ladder, rung 1: A dense spine preserves calendar days; keep user/date
--    grain until the seven-day distinct set is formed.
-- 9. Calculate median and 90th-percentile session duration with percentile_cont.
--    State input/output grain, interpolation behavior, NULL handling, and why
--    an average cannot answer the same distribution question.
--    Inputs: Derive one row per `(user_id, session_number)` with the Exercise 2
--    rule, then feed non-NULL `duration` values to ordered-set aggregates.
--    Expected result/shape: Exactly one aggregate row with `session_count` and
--    `median_and_p90`; the second column is a two-element interval array from
--    `percentile_cont(ARRAY[0.5, 0.9])`.
--    Verify: Materialize and sort session durations, confirm `session_count`,
--    and compare `percentile_cont`, `percentile_disc`, and `avg` on a tiny
--    skewed fixture. An empty input yields NULL percentiles, not zero duration.
--    Hint ladder, rung 1: Percentiles consume session rows, not event rows;
--    raw-event input overweights sessions containing more events.
-- 10. Return the top two event types per user with row_number, rank, and
--     dense_rank side by side. Define a deterministic tie policy and explain
--     when each ranking function changes the number of returned rows.
--    Inputs: Aggregate canonical events to one row per
--    `(user_id, event_name)`, then calculate `row_number`, `rank`, and
--    `dense_rank` within each user.
--    Expected result/shape: One row per `(user_id, event_name)`, with
--    `user_id`, `event_name`, `event_count`, `row_number_position`,
--    `rank_position`, and `dense_rank_position`, ordered by
--    `user_id, row_number_position`. Only `row_number` uses `event_name` as a
--    tie-break; the other two preserve count ties.
--    Verify: Create equal counts for two event names. `row_number <= 2`
--    returns exactly two rows; tie-preserving rank filters may return more.
--    State which meaning of “top two” the report adopts.
--    Hint ladder, rung 1: Adding `event_name` inside `rank()` destroys the
--    count tie whose behavior you are comparing.
-- 11. Traverse a parent/child campaign hierarchy with a recursive CTE. Include
--     depth, a path, and cycle detection; prove malformed cyclic input
--     terminates rather than looping until a resource limit.
--    Inputs: Seed a recursive CTE from `pro_analytics_lab.campaign_nodes`
--    rows whose `parent_campaign_id` is NULL. Carry `depth` and integer-array
--    `path`, and refuse a child already in that path. Include a separate
--    rootless two-node cycle in the fixture.
--    Expected result/shape: The hierarchy result has one row per
--    root-reachable node/path, with `campaign_id`, `parent_campaign_id`,
--    `depth`, and `path`, ordered by `path`. A second diagnostic result lists
--    unreachable `campaign_id` values, including the closed cycle.
--    Verify: No returned path repeats an ID, recursion terminates, and reachable
--    plus unreachable IDs equal all fixture IDs. Explain that a closed cycle in
--    this single-parent model is rootless; the diagnostic exposes it.
--    Hint ladder, rung 1: `tree` is the CTE being built, not a base relation;
--    anchor and recursive branches must project the same columns and types.
-- 12. Build a daily funnel report that retains zero-activity dates. Keep event
--     filters in the appropriate JOIN condition, make each denominator
--     explicit, and distinguish zero from missing data.
--    Inputs: Start from the four-date spine 2026-01-01 through 2026-01-04 and
--    LEFT JOIN canonical events with half-open UTC day bounds in `ON`.
--    Expected result/shape: Exactly four rows, one per `report_date`, with
--    `report_date`, `signups`, and `purchasers`, ordered by `report_date`.
--    Zero-activity dates retain zero counts.
--    Verify: Compare each day with a direct control query and prove the empty
--    dates remain. Move an event predicate to `WHERE` in a disposable copy and
--    observe the NULL-extended date rows disappear.
--    Hint ladder, rung 1: `WHERE` runs after the LEFT JOIN and can reject rows
--    the spine was supposed to preserve.
-- 13. Compare an exact distinct-user count with a documented approximate
--     strategy suitable for very large data. Define acceptable error, memory,
--     mergeability, refresh, and verification requirements before choosing.
--    Inputs: Compute core PostgreSQL's exact
--    `COUNT(DISTINCT user_id)` from `pro_analytics_lab.deduplicated_events`.
--    Separately review an adoption matrix for an optional approximate sketch;
--    do not pretend an unavailable extension executed.
--    Expected result/shape: The query returns exactly one row with
--    `exact_distinct_users`. The matrix has one row per criterion:
--    implementation/version, error budget, cardinality, memory, serialization,
--    mergeability, privacy, monitoring, fallback, and rebuild owner.
--    Verify: Compare the exact scalar with `SELECT DISTINCT user_id`. On any
--    approved sketch, sample against exact and record relative error; missing
--    capability or excess error must select the exact fallback.
--    Hint ladder, rung 1: Approximate distinct counting is a measured
--    capability decision, not a write or command-tag exercise.
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
--    Inputs: Accept typed `starts_at` and `ends_at` instants, reject NULL or
--    `ends_at <= starts_at`, and filter canonical events with
--    `starts_at <= event_at AND event_at < ends_at`.
--    Expected result/shape: One row per canonical `source_event_id` inside the
--    window, with `source_event_id` and `event_at`, ordered by
--    `event_at, source_event_id`. A valid empty window returns zero rows; an
--    invalid bound raises SQLSTATE `22023`.
--    Verify: Test events exactly at both endpoints, equal/reversed/NULL bounds,
--    duplicate raw deliveries, timestamp ties, an empty valid interval, and a
--    window crossing a daylight-saving transition expressed as instants.
--    Hint ladder, rung 1: Validate parameters before reading facts; converting
--    instants to local labels is a separate presentation rule.

ROLLBACK;
\echo 'SQL-ANALYTICS-01 complete: pro_analytics_lab was rolled back'
