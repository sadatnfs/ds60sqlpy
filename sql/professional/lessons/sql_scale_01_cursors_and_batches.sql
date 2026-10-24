-- SQL-SCALE-01: Cursor Pagination and Bounded Batches

-- Guide: sql/professional/companion-guides/sql_scale_01_cursors_and_batches.md

-- Use Create/open guided SQL notebook and the ignored learner copy.

-- Run the complete file with psql -X -v ON_ERROR_STOP=1.

-- Only the local disposable advanced_sql_training database is permitted.

-- Setup is supplied. Write attempts before the final ROLLBACK.

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

CREATE TEMP TABLE scale_events (
  event_id integer PRIMARY KEY, received_seq integer UNIQUE NOT NULL,
  occurred_at timestamptz
) ON COMMIT DROP;
INSERT INTO scale_events VALUES
(1,1,TIMESTAMPTZ '2024-01-01 10:00+00'),
(2,2,TIMESTAMPTZ '2024-01-01 10:00+00'),
(3,3,TIMESTAMPTZ '2024-01-01 11:00+00'),
(4,4,NULL), (5,5,TIMESTAMPTZ '2024-01-01 09:00+00'),
(6,6,TIMESTAMPTZ '2024-01-01 12:00+00');
CREATE INDEX ON scale_events (occurred_at DESC NULLS LAST,event_id DESC);

-- Example 1: Save the whole boundary from the first page
-- Expected: Two event rows, columns event_id, occurred_at: IDs 6 then 3; cursor (2024-01-01 11:00+00,3).
SELECT event_id, occurred_at
FROM scale_events
ORDER BY occurred_at DESC NULLS LAST, event_id DESC
LIMIT 2;

-- Example 2: Continue across a tied timestamp
-- Expected: Two event rows, columns event_id, occurred_at: IDs 2 then 1, both 10:00 UTC.
SELECT event_id, occurred_at
FROM scale_events
WHERE (occurred_at,event_id) < (TIMESTAMPTZ '2024-01-01 11:00+00',3)
ORDER BY occurred_at DESC NULLS LAST,event_id DESC
LIMIT 2;

-- Exercises
-- Keep predictions and attempts in your own working copy.

-- 1. Record an exact first-page boundary.
-- Inputs/evidence: For sql-scale-01 Exercise 1, Return the first two event rows with event_id, occurred_at. Record both cursor fields and explain why timestamp alone is insufficient.
-- Expected result/shape: For sql-scale-01 Exercise 1, Two rows keyed by event_id, columns event_id, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: IDs 6,3. Cursor is (11:00 UTC on January 1 2024,3).
-- Verify: For sql-scale-01 Exercise 1, Inspect page IDs 6,3 and save both values from the last returned row, timestamp 11:00 UTC and ID 3. A separately computed maximum ID is not this cursor.
-- Hint: The cursor comes from the last row actually returned.

-- 2. Traverse a timestamp tie without overlap.
-- Inputs/evidence: For sql-scale-01 Exercise 2, Continue after (2024-01-01 11:00+00,3) for two known-timestamp rows, projecting event_id, occurred_at. Use a strict compound boundary.
-- Expected result/shape: For sql-scale-01 Exercise 2, Two rows keyed by event_id, columns event_id, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: IDs 2,1. Neither appears on page one; both timestamp ties survive.
-- Verify: For sql-scale-01 Exercise 2, Compare ordered IDs 2,1, require no overlap with first-page IDs 6,3, and retain both equal 10:00 timestamps. A timestamp-only or non-strict boundary fails these controls.
-- Hint: Compare the row pair in the same direction as the final sort.

-- 3. Cross into the unknown-timestamp phase.
-- Inputs/evidence: For sql-scale-01 Exercise 3, Continue after the last known boundary (2024-01-01 09:00+00,5) and include the NULL tail. Return event_id, occurred_at. Explain the follow-on predicate after a NULL cursor at ID 4.
-- Expected result/shape: For sql-scale-01 Exercise 3, One event row keyed by event_id, columns event_id, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: ID 4 with NULL. After that NULL cursor, occurred_at IS NULL AND event_id < 4 returns zero rows.
-- Verify: For sql-scale-01 Exercise 3, Require ID 4 with occurred_at NULL, then inspect the follow-on NULL-only identity predicate and confirm it returns zero rows for this fixture.
-- Hint: A known boundary admits its earlier known rows plus the NULL phase.

-- 4. Expose positional drift after an insertion.
-- Inputs/evidence: For sql-scale-01 Exercise 4, Model inserting event 7 at 13:00 after page one. Compare an OFFSET 2 page with the original compound cursor page. Return path, event_id, occurred_at for both two-row pages.
-- Expected result/shape: For sql-scale-01 Exercise 4, Four path-event rows identified by (path,event_id), columns path, event_id, occurred_at; final ORDER BY path, occurred_at DESC NULLS LAST, event_id DESC. cursor gives 2,1; offset gives 3,2, repeating page-one ID 3.
-- Verify: For sql-scale-01 Exercise 4, Compare offset page IDs 3,2 with cursor page IDs 2,1. Only the offset result repeats first-page ID 3, and a separate source count still equals six.
-- Hint: Use a CTE that UNION ALL adds event 7 without changing the fixture.

-- 5. Exclude a late arrival with a declared sealed prefix.
-- Inputs/evidence: For sql-scale-01 Exercise 5, Add an illustrative event 7 received_seq 7 with event timestamp 10:30. Continue after (11:00,3) under the sealed received_seq <= 6 fence, including NULLs. Return event_id, received_seq, occurred_at.
-- Expected result/shape: For sql-scale-01 Exercise 5, Four event rows keyed by event_id, columns event_id, received_seq, occurred_at; final ORDER BY occurred_at DESC NULLS LAST, event_id DESC: IDs 2,1,5,4. Late event 7 is excluded despite fitting the time cursor.
-- Verify: For sql-scale-01 Exercise 5, Inspect returned event_id values 2,1,5,4 under the sealed prefix and confirm incoming ID 7 is excluded despite fitting the timestamp cursor. Explain why allocated sequence order is not committed-prefix completeness.
-- Hint: Apply membership and continuation as separate AND conditions; group the OR continuation cases.

-- 6. Prove bounded traversal covers the static fixture.
-- Inputs/evidence: For sql-scale-01 Exercise 6, Build a deterministic batch manifest over all six rows with a batch size of two using row_number only as a validation oracle. Return batch_no, event_ids, row_count. Explain why this oracle is not the production cursor algorithm.
-- Expected result/shape: For sql-scale-01 Exercise 6, Three manifest rows keyed by batch_no, columns batch_no, event_ids, row_count; final ORDER BY batch_no: (1,{6,3},2),(2,{2,1},2),(3,{5,4},2). Concatenated identities cover all six exactly once.
-- Verify: For sql-scale-01 Exercise 6, Inspect batch arrays {6,3},{2,1},{5,4}, each size two. Their concatenation must contain all six source event_id values exactly once, including the unknown timestamp row.
-- Hint: Number the fixed ordered input and group each consecutive pair.

ROLLBACK;
