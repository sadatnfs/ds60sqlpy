-- sql-deep-03: ROWS, RANGE, GROUPS, Exclusions, and Sessionization
-- Guide: sql/professional/companion-guides/sql_deep_03.md
-- Use the complete file in the disposable advanced_sql_training database.

BEGIN;
DO $course_target$
BEGIN
  IF current_database() <> 'advanced_sql_training' THEN
    RAISE EXCEPTION 'Use only the disposable advanced_sql_training database';
  END IF;
END
$course_target$;
SET LOCAL TIME ZONE 'UTC';
SET LOCAL statement_timeout = '15s';

CREATE TEMP TABLE deep3_events(event_id integer PRIMARY KEY,customer_id text NOT NULL,occurred_at timestamptz NOT NULL,amount integer NOT NULL) ON COMMIT DROP;
INSERT INTO deep3_events VALUES
 (1,'a','2026-01-01T10:00Z',1),(2,'a','2026-01-01T10:00Z',2),
 (3,'a','2026-01-01T10:10Z',3),(4,'a','2026-01-01T10:40Z',4),
 (5,'a','2026-01-01T11:11Z',5),(6,'b','2026-01-01T10:05Z',10),
 (7,'b','2026-01-01T10:35Z',20);

-- Worked example 1
WITH samples(event_id,tick,amount) AS (VALUES(1,1,4),(2,1,6),(3,2,3))
SELECT event_id,
 sum(amount) OVER(ORDER BY tick,event_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS row_total,
 sum(amount) OVER(ORDER BY tick RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS peer_total
FROM samples ORDER BY event_id;

-- Worked example 2
WITH samples(event_id,amount) AS (VALUES(1,3),(2,9))
SELECT event_id,last_value(amount) OVER(ORDER BY event_id) AS default_last,
 last_value(amount) OVER(ORDER BY event_id ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS partition_last
FROM samples ORDER BY event_id;

-- Exercises
-- Write attempts in your ignored working copy before the final ROLLBACK.

-- 1. Compare row and peer running totals
-- Prompt: For customer a only, return event_id, row_total, peer_total. Use ROWS with occurred_at, event_id for row_total and RANGE with occurred_at alone for peer_total. Both frames start at UNBOUNDED PRECEDING and end at CURRENT ROW. Order final rows by event_id.
-- Expected: IDs 1..5 have row_total[1,3,6,10,15] and peer_total[3,3,6,10,15]. The two 10:00 events share only the peer-aware total.

-- 2. Compare neighboring rows with neighboring peer groups
-- Prompt: For customer a, return event_id, two_rows, two_groups. The first frame is ROWS BETWEEN 1 PRECEDING AND CURRENT ROW ordered by timestamp, event_id; the second is GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW ordered by timestamp alone. Final order is event_id.
-- Expected: two_rows is[1,3,5,7,9] and two_groups is[3,3,6,7,9]. At event 3 the previous peer group contains both events 1 and 2.

-- 3. Distinguish the three exclusion policies
-- Prompt: For customer a, return event_id, without_current, without_group, without_other_ties using a RANGE unbounded-preceding-to-current frame ordered by timestamp. Apply EXCLUDE CURRENT ROW, EXCLUDE GROUP and EXCLUDE TIES respectively. Preserve NULL for empty frames and order by event_id.
-- Expected: ID 1 gives 2, NULL,1; ID 2 gives 1, NULL,2; ID 3 gives 3,3,6; ID 4 gives 6,6,10; ID 5 gives 10,10,15.

-- 4. Make LAST_VALUE refer to the intended horizon
-- Prompt: For customer a, return event_id, prefix_last, partition_last. Order both windows by timestamp, event_id. Use the default ordered frame for prefix_last and explicit ROWS UNBOUNDED PRECEDING TO UNBOUNDED FOLLOWING for partition_last. Final order is event_id.
-- Expected: prefix_last is[1,2,3,4,5], while partition_last is 5 for every row. No row is removed or collapsed.

-- 5. Build a strictly prior elapsed-time feature
-- Prompt: For all customers return event_id, prior_30m over [occurred_at-30minutes, occurred_at), excluding every event at the current timestamp. Use a timestamp RANGE frame plus EXCLUDE GROUP and partition by customer_id. Treat an empty complete-log window as zero. Order by event_id.
-- Expected: IDs 1..7 yield prior_30m[0,0,3,3,0,0,10]. Event 4 includes the exact 10:10 lower boundary; event 5 excludes 10:40 because it is 31 minutes old.

-- 6. Derive sessions in separate window stages
-- Prompt: Define a new session for a customer's first event or a gap strictly greater than 30 minutes. Return customer_id, session_id, event_count, first_event_id, last_event_id, one row per customer/session, ordered by customer_id, session_id. Use deterministic timestamp, event_id ordering and separate lag, flag, cumulative stages.
-- Expected: Rows are(a,1,4,1,4),(a,2,1,5,5),(b,1,2,6,7). Exact 30-minute gaps stay in the same session; the 31-minute a gap starts session 2.

ROLLBACK;
