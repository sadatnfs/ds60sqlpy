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
--    Inputs: Use only the declared lesson objects (big_events, big_events_2025_01, big_events_2025_02) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Return the keys/measures named by the prompt at one explicitly declared row grain, with deterministic order for ranked or limited output and an explicit policy for NULL/empty input.
--    Verify: Check uniqueness at the declared grain and compare row counts or totals with a simpler control query over the same population.
--    Hint ladder, rung 1: Build FROM/JOIN and inspect keys first; add filtering, grouping/windows, projection, and deterministic ordering one stage at a time.
-- 2. Create indexes on partitions and compare query plans.
--    Inputs: Use only the declared lesson objects (big_events, big_events_2025_01, big_events_2025_02) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 3. Prediction: remove the event_time predicate and predict how many
--    partitions appear in the plan. Restore the predicate and verify pruning.
--    Inputs: Use only the declared lesson objects (big_events, big_events_2025_01, big_events_2025_02) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 4. Construction: add a DEFAULT partition, insert an April event, and use
--    tableoid::regclass to prove which physical partition owns it.
--    Inputs: Use only the declared lesson objects (big_events, big_events_2025_01, big_events_2025_02) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Expect a successful command tag plus a catalog/behavior result that shows the named object or invariant; do not count an unverified CREATE/ALTER as completion.
--    Verify: Query pg_catalog/information_schema where appropriate, then run one valid and one boundary case inside the lesson safety boundary.
--    Hint ladder, rung 1: Write the row grain and invariant in prose first; then map each requirement to the smallest column, key, constraint, or migration step.
-- 5. Debugging: attempt to insert a March row before adding a matching/default
--    partition. Read the error and explain the range-boundary gap.
--    Inputs: Use only the declared lesson objects (big_events, big_events_2025_01, big_events_2025_02) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.
-- 6. Edge case: test exactly 2025-02-01 00:00:00+00 and explain why FROM is
--    inclusive while TO is exclusive.
--    Inputs: Use only the declared lesson objects (big_events, big_events_2025_01, big_events_2025_02) and any small disposable fixture the prompt explicitly asks you to create.
--    Expected result/shape: Record the prediction first, then capture both result/plan shapes with the prompt's named keys, measures, row counts, or SQLSTATE.
--    Verify: Use identical inputs for the comparison and explain every observed difference; revise the prediction when the transcript disagrees.
--    Hint ladder, rung 1: Hold every input constant, change one clause or case, and write down the expected row count/shape before executing either form.

ROLLBACK;
