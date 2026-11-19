-- Day 37: Partitioning & Data Sharding (PostgreSQL native partitioning demo)
-- BEGINNER WORKFLOW - sql-37: Partitioning Sharding
-- Guide: sql/postgres-60day/companion-guides/day37_partitioning_sharding.md
-- Recommended runner: ./classroom -> PostgreSQL -> sql-37.
-- Choose "Whole SQL lesson (psql)" and edit its saved learner copy.
-- Docker supplies the client and the disposable advanced_sql_training database.
-- Read the full transcript and retain the declared transaction/cleanup boundary.
-- The optional contributor notebook route is described separately in the guide.
-- Read every SELECT as FROM/JOIN -> WHERE -> GROUP BY/aggregate -> HAVING ->
-- window calculation -> SELECT -> ORDER BY -> LIMIT. Before each statement,
-- declare what one input row and one output row represent. A displayed result
-- set is temporary; NULL, zero, an empty string, and an absent row differ.
-- Primary objects in the worked examples: big_events, big_events_2025_01, big_events_2025_02.
-- Success means the first error never appears, psql exits 0, result keys and
-- control totals match the stated contract, and verification passes. The lesson's documented transaction/cleanup boundary restores disposable state.
-- Keep all numbered exercises answer-free here: write predictions and attempts
-- only in your ignored working copy.
--
BEGIN;
SET search_path TO training, public;

-- Create a partitioned table for large events (demo table)
CREATE TABLE big_events (
  id BIGSERIAL,
  event_time TIMESTAMPTZ NOT NULL,
  customer_id INT,
  payload JSONB
)
PARTITION BY RANGE (event_time);

-- Create monthly partitions
CREATE TABLE big_events_2025_01 PARTITION OF big_events
FOR VALUES FROM ('2025-01-01 00:00:00+00') TO ('2025-02-01 00:00:00+00');

CREATE TABLE big_events_2025_02 PARTITION OF big_events
FOR VALUES FROM ('2025-02-01 00:00:00+00') TO ('2025-03-01 00:00:00+00');

-- Insert 1,000 sample rows, one every 83 minutes from 2025-01-01 00:00 UTC:
-- 537 land in the January partition and 463 in the February partition.
INSERT INTO big_events (event_time, customer_id, payload)
SELECT
  timestamp with time zone '2025-01-01 00:00:00+00' + ((event_no * 83) % (59 * 24 * 60)) * interval '1 minute',
  1 + ((event_no * 29 - 1) % 500),
  jsonb_build_object('k', 'v', 'source_row', event_no)
FROM
  generate_series(1, 1000) AS g (event_no);

-- A range that spans both months: neither partition can be pruned.
EXPLAIN ANALYZE
SELECT
  COUNT(*)
FROM
  big_events
WHERE
  event_time >= timestamptz '2025-01-15 00:00:00+00'
  AND event_time < timestamptz '2025-02-15 00:00:00+00';

-- A January-only range: the planner prunes big_events_2025_02.
EXPLAIN ANALYZE
SELECT
  COUNT(*)
FROM
  big_events
WHERE
  event_time >= timestamptz '2025-01-15 00:00:00+00'
  AND event_time < timestamptz '2025-01-20 00:00:00+00';

-- Exercises
-- 1. Add more partitions and test pruning.
--    Inputs: For sql-37 Exercise 1, extend `solution_events` (January and February partitions) with March and April partitions, load the 5,000 deterministic rows spread from 2025-01-01 to 2025-04-30, then run `EXPLAIN (ANALYZE, BUFFERS)` on a March-only `COUNT(*)` with constant `timestamptz` bounds.
--    Expected result/shape: For sql-37 Exercise 1, expected output: a plan whose only scan node reads `solution_events_2025_03`, with `actual ... rows=950`; January, February, and April are pruned at planning time. `EXPLAIN` prints one text column named `QUERY PLAN`, not business rows.
--    Verify: For sql-37 Exercise 1, run the same `SELECT COUNT(*)` without `EXPLAIN` and confirm it returns `950`, the scan node's actual rows; then plan a count with no `WHERE` clause and confirm that all four monthly partitions appear under one `Append` node.
--    Hint ladder, rung 1: For sql-37 Exercise 1, half-open monthly bounds `[FROM, TO)` must cover every timestamp exactly once; write them on a timeline before creating the partitions.
-- 2. Create indexes on partitions and compare query plans.
--    Inputs: For sql-37 Exercise 2, create one index on the partitioned parent, `solution_events (customer_id, event_time)`, then run `EXPLAIN (ANALYZE, BUFFERS)` on `SELECT *` for `customer_id = 42` in March.
--    Expected result/shape: For sql-37 Exercise 2, expected output: `pg_indexes` lists the parent index plus one `(customer_id, event_time)` index for each of the four monthly partitions, and the plan reads only `solution_events_2025_03`, returning `rows=2`. On this seed the scan uses `solution_events_2025_03_customer_id_event_time_idx`; another access path is acceptable when statistics differ.
--    Verify: For sql-37 Exercise 2, query `SELECT tablename, indexname FROM pg_indexes WHERE tablename LIKE 'solution_events%' ORDER BY tablename` and confirm five rows; then run the query without `EXPLAIN` and confirm it returns the same two rows that the plan reports.
--    Hint ladder, rung 1: For sql-37 Exercise 2, create the index once on the parent; PostgreSQL creates and attaches the matching partition indexes for you.
-- 3. Prediction: remove the event_time predicate and predict how many
--    partitions appear in the plan. Restore the predicate and verify pruning.
--    Inputs: For sql-37 Exercise 3, run plain `EXPLAIN` (without `ANALYZE`) on `SELECT COUNT(*) FROM solution_events` with no predicate, then on the same count restricted to the March half-open range.
--    Expected result/shape: For sql-37 Exercise 3, expected output: the unfiltered plan lists four scans, one per monthly partition, under one `Append`; the March plan lists only `solution_events_2025_03` and has no `Append` node.
--    Verify: For sql-37 Exercise 3, write the predicted number of scanned partitions (4 and 1) before running both plans, then count the `Seq Scan on solution_events_...` lines in each plan and compare them with the prediction.
--    Hint ladder, rung 1: For sql-37 Exercise 3, pruning needs a predicate on the partition key; a predicate on `customer_id` alone cannot remove any month.
-- 4. Construction: add a DEFAULT partition, insert an event dated 2025-06-15
--    (outside every monthly partition), and use tableoid::regclass to prove
--    which physical partition owns it.
--    Inputs: For sql-37 Exercise 4, add `solution_events_default` as the DEFAULT partition and insert one event dated `2025-06-15 00:00:00+00`, which no monthly partition covers.
--    Expected result/shape: For sql-37 Exercise 4, expected output: one row, `physical_partition` = `solution_events_default` and `event_time` = `2025-06-15 00:00:00+00`.
--    Verify: For sql-37 Exercise 4, before the DEFAULT partition exists, the same insert fails with SQLSTATE `23514` (`no partition of relation "solution_events" found for row`); after it exists, `SELECT COUNT(*) FROM solution_events_default` returns `1`.
--    Hint ladder, rung 1: For sql-37 Exercise 4, `tableoid::regclass` names the physical partition that stores each row.
-- 5. Debugging: before any DEFAULT partition exists, insert a row dated after
--    the last monthly partition (2025-07-01 once April exists). Read the error
--    and explain the range-boundary gap from the partition bound list.
--    Inputs: For sql-37 Exercise 5, list the leaf partitions of `solution_events` and their bounds from `pg_partition_tree('solution_events')` joined to `pg_class`, after Exercises 1 to 4 created four monthly partitions and the DEFAULT partition.
--    Expected result/shape: For sql-37 Exercise 5, expected output: five rows ordered by `c.relname`, with columns `partition_name` and `partition_bound`: four `FOR VALUES FROM (...) TO (...)` rows for January to April and one `DEFAULT` row for `solution_events_default`.
--    Verify: For sql-37 Exercise 5, compare the bound text with the dates you wrote in Exercise 1; then, in a scratch transaction before any DEFAULT partition exists, insert a `2025-07-01 00:00:00+00` row and confirm SQLSTATE `23514`, which this catalog query explains because no listed bound covers July.
--    Hint ladder, rung 1: For sql-37 Exercise 5, read the uncovered date from the error detail (`Partition key of the failing row contains ...`), then find the gap in the bound list.
-- 6. Edge case: test exactly 2025-02-01 00:00:00+00 and explain why FROM is
--    inclusive while TO is exclusive.
--    Inputs: For sql-37 Exercise 6, insert one row at exactly `2025-02-01 00:00:00+00` with `payload` `{"source":"boundary"}`, then read it back by that payload value.
--    Expected result/shape: For sql-37 Exercise 6, expected output: one row, `physical_partition` = `solution_events_2025_02` and `event_time` = `2025-02-01 00:00:00+00`, because `FROM` bounds are inclusive and `TO` bounds are exclusive.
--    Verify: For sql-37 Exercise 6, insert a second row at `2025-01-31 23:59:59.999999+00` and confirm that `tableoid::regclass` reports `solution_events_2025_01` for it, so the two instants one microsecond apart land in different partitions.
--    Hint ladder, rung 1: For sql-37 Exercise 6, midnight on February 1 is the first instant of February's range and is outside January's range.
ROLLBACK;
