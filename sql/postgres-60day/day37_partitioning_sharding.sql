-- Day 37: Partitioning & Data Sharding (PostgreSQL native partitioning demo)
-- BEGINNER WORKFLOW — sql-37: Partitioning Sharding
-- Guide: sql/postgres-60day/companion-guides/day37_partitioning_sharding.md
-- Recommended runner: open the private lesson reader and choose
-- "Create/open guided SQL notebook". It verifies advanced_sql_training,
-- creates an ignored .learning/sql/sql-37/ copy, and prints the full
-- psql transcript below the run cell. Edit that private copy, not this official
-- source, while studying.
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
) PARTITION BY RANGE (event_time);

-- Create monthly partitions
CREATE TABLE big_events_2025_01 PARTITION OF big_events
  FOR VALUES FROM ('2025-01-01 00:00:00+00') TO ('2025-02-01 00:00:00+00');
CREATE TABLE big_events_2025_02 PARTITION OF big_events
  FOR VALUES FROM ('2025-02-01 00:00:00+00') TO ('2025-03-01 00:00:00+00');

-- Insert sample rows
INSERT INTO big_events(event_time, customer_id, payload)
SELECT timestamp with time zone '2025-01-01 00:00:00+00'
         + ((event_no * 37) % (59 * 24 * 60)) * interval '1 minute',
       1 + ((event_no * 29 - 1) % 500),
       jsonb_build_object('k', 'v', 'source_row', event_no)
FROM generate_series(1, 1000) AS g(event_no);

-- Query with partition pruning
EXPLAIN ANALYZE
SELECT COUNT(*) FROM big_events
WHERE event_time >= '2025-01-15' AND event_time < '2025-02-15';

-- Exercises
-- 1. Add more partitions and test pruning.
--    Inputs: For sql-37 Exercise 1, run the underlying read-only query over `solution_big_events` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-37 Exercise 1, expected output: one row per `big_events`. The final columns are `big_events`.
--    Verify: For sql-37 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `big_events` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-37 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `big_events` rows.
-- 2. Create indexes on partitions and compare query plans.
--    Inputs: For sql-37 Exercise 2, run the underlying read-only query over `indexed_big_events`, `indexed_big_events_2025_01_time_idx`, `indexed_big_events_2025_02_time_idx`, `indexed_big_events_2025_03_time_idx`, and `indexed_big_events_2025_01` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-37 Exercise 2, expected output: one row per `plan_node`. The final columns are `plan_node`, `estimated_rows`, `actual_rows`, `loops`, and `buffers`.
--    Verify: For sql-37 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-37 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows.
-- 3. Prediction: remove the event_time predicate and predict how many
--    partitions appear in the plan. Restore the predicate and verify pruning.
--    Inputs: For sql-37 Exercise 3, run the underlying read-only query over `solution_events` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
--    Expected result/shape: For sql-37 Exercise 3, expected output: exactly one aggregate summary row. The final columns are `plan_node`, `estimated_rows`, `actual_rows`, `loops`, and `buffers`.
--    Verify: For sql-37 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
--    Hint ladder, rung 1: For sql-37 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows.
-- 4. Construction: add a DEFAULT partition, insert an April event, and use
--    tableoid::regclass to prove which physical partition owns it.
--    Inputs: For sql-37 Exercise 4, read from `solution_events`, and `solution_events_default`. Build the answer toward `physical_partition`, and `event_time`; keep `physical_partition` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-37 Exercise 4, expected output: one row per `physical_partition`. The final columns are `physical_partition`, and `event_time`.
--    Verify: For sql-37 Exercise 4, run an anti-check that counts rows where NOT ((event_time = timestamptz '2025-06-15 00:00:00+00')); require unique `physical_partition` where the expected grain is one row per key and confirm the projected `physical_partition`, and `event_time` against `solution_events`, and `solution_events_default`. Add one row for which `(event_time = timestamptz '2025-06-15 00:00:00+00')` is true and one for which it is false; verify only the matching `physical_partition` value is returned.
--    Hint ladder, rung 1: For sql-37 Exercise 4, inspect the source keys that survive `WHERE`.
-- 5. Debugging: attempt to insert a March row before adding a matching/default
--    partition. Read the error and explain the range-boundary gap.
--    Inputs: For sql-37 Exercise 5, read the target keys from `pg_class` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
--    Expected result/shape: For sql-37 Exercise 5, expected output: the command tag and an independently counted set of affected `partition_name` values. The final columns are `partition_name`, and `partition_bound`. The final order is `c.relname`.
--    Verify: For sql-37 Exercise 5, materialize the intended `partition_name` target set first; require the command tag/`RETURNING` set to match it, then query `pg_class` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `partition_name` values in both cases.
--    Hint ladder, rung 1: For sql-37 Exercise 5, start with the first relation in `pg_class`; after each join, record total rows and distinct `partition_name` so the exact fanout or loss is visible.
-- 6. Edge case: test exactly 2025-02-01 00:00:00+00 and explain why FROM is
--    inclusive while TO is exclusive.
--    Inputs: For sql-37 Exercise 6, read from `solution_events`. Build the answer toward `physical_partition`, and `event_time`; keep `physical_partition` visible whenever the result has row-level grain.
--    Expected result/shape: For sql-37 Exercise 6, expected output: one row per `physical_partition`. The final columns are `physical_partition`, and `event_time`.
--    Verify: For sql-37 Exercise 6, run an anti-check that counts rows where NOT ((payload->>'source' = 'boundary')); require unique `physical_partition` where the expected grain is one row per key and confirm the projected `physical_partition`, and `event_time` against `solution_events`. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
--    Hint ladder, rung 1: For sql-37 Exercise 6, inspect the source keys that survive `WHERE`.

ROLLBACK;
