-- Day 37 solutions: partitioning
BEGIN;
SET search_path TO training, public;

CREATE TABLE solution_events (
  event_id bigint GENERATED ALWAYS AS IDENTITY,
  event_time timestamptz NOT NULL,
  customer_id int,
  payload jsonb
) PARTITION BY RANGE (event_time);

CREATE TABLE solution_events_2025_01 PARTITION OF solution_events
  FOR VALUES FROM ('2025-01-01 00:00:00+00') TO ('2025-02-01 00:00:00+00');
CREATE TABLE solution_events_2025_02 PARTITION OF solution_events
  FOR VALUES FROM ('2025-02-01 00:00:00+00') TO ('2025-03-01 00:00:00+00');

-- Exercise 1: add March and April partitions.
CREATE TABLE solution_events_2025_03 PARTITION OF solution_events
  FOR VALUES FROM ('2025-03-01 00:00:00+00') TO ('2025-04-01 00:00:00+00');
CREATE TABLE solution_events_2025_04 PARTITION OF solution_events
  FOR VALUES FROM ('2025-04-01 00:00:00+00') TO ('2025-05-01 00:00:00+00');

INSERT INTO solution_events(event_time, customer_id, payload)
SELECT timestamptz '2025-01-01 00:00:00+00'
         + ((n * 47) % (120 * 24 * 60)) * interval '1 minute',
       1 + ((n * 19 - 1) % 500),
       jsonb_build_object('source_row', n)
FROM generate_series(1, 5000) AS g(n);

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*)
FROM solution_events
WHERE event_time >= timestamptz '2025-03-01 00:00:00+00'
  AND event_time < timestamptz '2025-04-01 00:00:00+00';

-- Exercise 2: a partitioned index creates one child index per partition.
CREATE INDEX idx_solution_events_customer_time
  ON solution_events(customer_id, event_time);

EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM solution_events
WHERE customer_id = 42
  AND event_time >= timestamptz '2025-03-01 00:00:00+00'
  AND event_time < timestamptz '2025-04-01 00:00:00+00';

-- Exercise 3: the unbounded query can visit every partition; the bounded query
-- lets PostgreSQL prune to March.
EXPLAIN SELECT COUNT(*) FROM solution_events;
EXPLAIN
SELECT COUNT(*) FROM solution_events
WHERE event_time >= timestamptz '2025-03-01 00:00:00+00'
  AND event_time < timestamptz '2025-04-01 00:00:00+00';

-- Exercise 4: original exercises already created April, so June is the
-- deliberately uncovered value routed to DEFAULT.
CREATE TABLE solution_events_default PARTITION OF solution_events DEFAULT;
INSERT INTO solution_events(event_time, customer_id, payload)
VALUES ('2025-06-15 00:00:00+00', 1, '{"source":"default"}');
SELECT tableoid::regclass AS physical_partition, event_time
FROM solution_events
WHERE event_time = timestamptz '2025-06-15 00:00:00+00';

-- Exercise 5: this catalog query shows the covered named ranges. Without the
-- DEFAULT partition, an insert outside them raises “no partition ... found”.
SELECT relid::regclass AS partition_name,
       pg_get_expr(c.relpartbound, c.oid) AS partition_bound
FROM pg_partition_tree('solution_events') pt
JOIN pg_class c ON c.oid = pt.relid
WHERE pt.isleaf
ORDER BY c.relname;

-- Exercise 6: the exact February boundary belongs to February because lower
-- FROM bounds are inclusive and upper TO bounds are exclusive.
INSERT INTO solution_events(event_time, customer_id, payload)
VALUES ('2025-02-01 00:00:00+00', 2, '{"source":"boundary"}');
SELECT tableoid::regclass AS physical_partition, event_time
FROM solution_events
WHERE payload->>'source' = 'boundary';

ROLLBACK;
