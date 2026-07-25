# Day 37 — Solutions: Partitioning

PostgreSQL partitioning divides one logical table into physical child tables.
The optimizer can prune children whose bounds cannot satisfy a query predicate.
“Sharding” across servers is a separate architectural concern and is not
implemented by this single-database exercise.

## Exercise 1 — Add a partition and test pruning

Temporary tables keep the answer isolated from the learner script's
`big_events` names.

```sql
BEGIN;
SET LOCAL search_path TO training, public;

CREATE TEMP TABLE solution_big_events (
  id bigint GENERATED ALWAYS AS IDENTITY,
  event_time timestamptz NOT NULL,
  customer_id int,
  payload jsonb
) PARTITION BY RANGE (event_time);

CREATE TEMP TABLE solution_big_events_2025_01
  PARTITION OF solution_big_events
  FOR VALUES FROM ('2025-01-01 00:00:00+00')
             TO ('2025-02-01 00:00:00+00');

CREATE TEMP TABLE solution_big_events_2025_02
  PARTITION OF solution_big_events
  FOR VALUES FROM ('2025-02-01 00:00:00+00')
             TO ('2025-03-01 00:00:00+00');

CREATE TEMP TABLE solution_big_events_2025_03
  PARTITION OF solution_big_events
  FOR VALUES FROM ('2025-03-01 00:00:00+00')
             TO ('2025-04-01 00:00:00+00');

INSERT INTO solution_big_events(event_time, customer_id, payload)
SELECT timestamptz '2025-01-01 00:00:00+00'
         + (event_no - 1) * interval '30 minutes',
       1 + ((event_no * 29 - 1) % 500),
       jsonb_build_object('source_row', event_no)
FROM generate_series(1, 3000) AS g(event_no);

EXPLAIN (ANALYZE, VERBOSE)
SELECT COUNT(*)
FROM solution_big_events
WHERE event_time >= timestamptz '2025-03-01 00:00:00+00'
  AND event_time < timestamptz '2025-04-01 00:00:00+00';

ROLLBACK;
```

Inspect the plan for only the March child (or for other evidence that January
and February were pruned). Exact wording varies by PostgreSQL version.

## Exercise 2 — Index partitions and compare plans

```sql
BEGIN;
SET LOCAL search_path TO training, public;

CREATE TEMP TABLE indexed_big_events (
  id bigint GENERATED ALWAYS AS IDENTITY,
  event_time timestamptz NOT NULL,
  customer_id int,
  payload jsonb
) PARTITION BY RANGE (event_time);

CREATE TEMP TABLE indexed_big_events_2025_01
  PARTITION OF indexed_big_events
  FOR VALUES FROM ('2025-01-01 00:00:00+00')
             TO ('2025-02-01 00:00:00+00');

CREATE TEMP TABLE indexed_big_events_2025_02
  PARTITION OF indexed_big_events
  FOR VALUES FROM ('2025-02-01 00:00:00+00')
             TO ('2025-03-01 00:00:00+00');

CREATE TEMP TABLE indexed_big_events_2025_03
  PARTITION OF indexed_big_events
  FOR VALUES FROM ('2025-03-01 00:00:00+00')
             TO ('2025-04-01 00:00:00+00');

INSERT INTO indexed_big_events(event_time, customer_id, payload)
SELECT timestamptz '2025-01-01 00:00:00+00'
         + (event_no - 1) * interval '30 minutes',
       1 + ((event_no * 29 - 1) % 500),
       jsonb_build_object('source_row', event_no)
FROM generate_series(1, 3000) AS g(event_no);

EXPLAIN (ANALYZE, BUFFERS)
SELECT event_time, customer_id
FROM indexed_big_events
WHERE event_time >= timestamptz '2025-03-02 00:00:00+00'
  AND event_time < timestamptz '2025-03-03 00:00:00+00';

CREATE INDEX indexed_big_events_2025_01_time_idx
  ON indexed_big_events_2025_01(event_time);
CREATE INDEX indexed_big_events_2025_02_time_idx
  ON indexed_big_events_2025_02(event_time);
CREATE INDEX indexed_big_events_2025_03_time_idx
  ON indexed_big_events_2025_03(event_time);

EXPLAIN (ANALYZE, BUFFERS)
SELECT event_time, customer_id
FROM indexed_big_events
WHERE event_time >= timestamptz '2025-03-02 00:00:00+00'
  AND event_time < timestamptz '2025-03-03 00:00:00+00';

ROLLBACK;
```

Expected logical result: the before and after queries return the same March
rows. The indexed plan may use only the March index; the small child can still
make a sequential scan rational.

## Pitfalls

- Partition bounds are lower-inclusive and upper-exclusive.
- An insert outside all bounds fails unless a default partition exists.
- Put the partition key in filtering predicates so pruning is possible.
- Too many tiny partitions increase planning and maintenance overhead.
