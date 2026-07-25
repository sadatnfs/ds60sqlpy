-- Day 37: Partitioning & Data Sharding (PostgreSQL native partitioning demo)
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
-- 1) Add more partitions and test pruning.
-- 2) Create indexes on partitions and compare query plans.

ROLLBACK;
