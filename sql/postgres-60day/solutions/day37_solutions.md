# Day 37: Solutions: Partitioning


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```bash
# Linux, macOS, or Windows through WSL 2, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day37_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Partition bound, Partition pruning, Sharding. Its worked-model focus is:
Map the January and February bounds on a timeline, then plan a January-15-to-February-15 query. Both partitions are required. Change the range to a January-only half-open interval and inspect `EXPLAIN` to prove February is pruned rather than assuming it.

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

PostgreSQL partitioning divides one logical table into physical child tables.
The optimizer can prune children whose bounds cannot satisfy a query predicate.
“Sharding” across servers is a separate architectural concern and is not
implemented by this single-database exercise.

## Exercise 1: Add a partition and test pruning

The executable solution uses its own `solution_events` table so the answer
never collides with the learner script's `big_events` names. All six exercises
run in one transaction that ends with `ROLLBACK`.

```sql
BEGIN;
SET search_path TO training, public;

CREATE TABLE solution_events (
  event_id bigint GENERATED ALWAYS AS IDENTITY,
  event_time timestamptz NOT NULL,
  customer_id int,
  payload jsonb
)
PARTITION BY RANGE (event_time);

CREATE TABLE solution_events_2025_01 PARTITION OF solution_events
FOR VALUES FROM ('2025-01-01 00:00:00+00') TO ('2025-02-01 00:00:00+00');

CREATE TABLE solution_events_2025_02 PARTITION OF solution_events
FOR VALUES FROM ('2025-02-01 00:00:00+00') TO ('2025-03-01 00:00:00+00');

-- Exercise 1: add March and April partitions.
CREATE TABLE solution_events_2025_03 PARTITION OF solution_events
FOR VALUES FROM ('2025-03-01 00:00:00+00') TO ('2025-04-01 00:00:00+00');

CREATE TABLE solution_events_2025_04 PARTITION OF solution_events
FOR VALUES FROM ('2025-04-01 00:00:00+00') TO ('2025-05-01 00:00:00+00');

INSERT INTO solution_events (event_time, customer_id, payload)
SELECT
  timestamptz '2025-01-01 00:00:00+00' + ((n * 47) % (120 * 24 * 60)) * interval '1 minute',
  1 + ((n * 19 - 1) % 500),
  jsonb_build_object('source_row', n)
FROM
  generate_series(1, 5000) AS g (n);

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  COUNT(*)
FROM
  solution_events
WHERE
  event_time >= timestamptz '2025-03-01 00:00:00+00'
  AND event_time < timestamptz '2025-04-01 00:00:00+00';
```

The 5,000 rows land 1,899 in January, 1,232 in February, 950 in March and 919
in April. Because both bounds are constants, the planner prunes at planning
time: the plan shows a single `Seq Scan on solution_events_2025_03` with
`actual ... rows=950` and no `Append` node.

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 1, extend `solution_events` (January and February partitions) with March and April partitions, load the 5,000 deterministic rows spread from 2025-01-01 to 2025-04-30, then run `EXPLAIN (ANALYZE, BUFFERS)` on a March-only `COUNT(*)` with constant `timestamptz` bounds.
- **Expected result/shape:** For sql-37 Exercise 1, expected output: a plan whose only scan node reads `solution_events_2025_03`, with `actual ... rows=950`; January, February, and April are pruned at planning time. `EXPLAIN` prints one text column named `QUERY PLAN`, not business rows.
- **Independent verification:** For sql-37 Exercise 1, run the same `SELECT COUNT(*)` without `EXPLAIN` and confirm it returns `950`, the scan node's actual rows; then plan a count with no `WHERE` clause and confirm that all four monthly partitions appear under one `Append` node.
- **Intermediate relation check:** For sql-37 Exercise 1, list the leaf partitions with `pg_partition_tree('solution_events')` before planning, so you know which partition names can appear in the plan.
- **Clause check:** For sql-37 Exercise 1, the solution uses `CREATE TABLE ... PARTITION OF ... FOR VALUES FROM ... TO`, one `INSERT ... SELECT` over `generate_series`, and `EXPLAIN (ANALYZE, BUFFERS)` on a `SELECT COUNT(*) ... WHERE` with two `event_time` bounds.
- **Alternative/trade-off:** For sql-37 Exercise 1, a parameter or `now()`-based bound is unknown at planning time; PostgreSQL can still prune during execution, and the plan then reports `Subplans Removed` instead of omitting the partitions.
- **Edge case:** Plan a range that starts on 2025-02-28 and ends on 2025-03-02: it touches February and March, so two partitions remain.

## Exercise 2: Index partitions and compare plans

```sql
-- Exercise 2: a partitioned index creates one child index per partition.
CREATE INDEX idx_solution_events_customer_time ON solution_events (customer_id, event_time);

EXPLAIN (
  ANALYZE,
  BUFFERS
)
SELECT
  *
FROM
  solution_events
WHERE
  customer_id = 42
  AND event_time >= timestamptz '2025-03-01 00:00:00+00'
  AND event_time < timestamptz '2025-04-01 00:00:00+00';

SELECT
  tablename,
  indexname
FROM
  pg_indexes
WHERE
  schemaname = 'training'
  AND tablename LIKE 'solution_events%'
ORDER BY
  tablename;
```

One `CREATE INDEX` on the parent produces the parent's partitioned index and
four child indexes, such as `solution_events_2025_03_customer_id_event_time_idx`.
The plan reads only the March partition and, on this seed, uses that child
index to return the two matching rows. A small child can still make a
sequential scan rational after statistics change; compare the partition names
and row counts, not only the node type.

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 2, create one index on the partitioned parent, `solution_events (customer_id, event_time)`, then run `EXPLAIN (ANALYZE, BUFFERS)` on `SELECT *` for `customer_id = 42` in March.
- **Expected result/shape:** For sql-37 Exercise 2, expected output: `pg_indexes` lists the parent index plus one `(customer_id, event_time)` index for each of the four monthly partitions, and the plan reads only `solution_events_2025_03`, returning `rows=2`. On this seed the scan uses `solution_events_2025_03_customer_id_event_time_idx`; another access path is acceptable when statistics differ.
- **Independent verification:** For sql-37 Exercise 2, query `SELECT tablename, indexname FROM pg_indexes WHERE tablename LIKE 'solution_events%' ORDER BY tablename` and confirm five rows; then run the query without `EXPLAIN` and confirm it returns the same two rows that the plan reports.
- **Intermediate relation check:** For sql-37 Exercise 2, count the March rows for `customer_id = 42` with a plain `SELECT COUNT(*)` before reading the plan; the answer, `2`, is what the plan's actual rows must match.
- **Clause check:** For sql-37 Exercise 2, the solution uses one `CREATE INDEX ... ON solution_events (customer_id, event_time)` and `EXPLAIN (ANALYZE, BUFFERS)` on a `SELECT * ... WHERE customer_id = 42` with two `event_time` bounds.
- **Alternative/trade-off:** For sql-37 Exercise 2, `CREATE INDEX CONCURRENTLY` cannot target a partitioned parent; online builds use `CREATE INDEX ... ON ONLY` on the parent, a concurrent build per partition, and `ALTER INDEX ... ATTACH PARTITION`.
- **Edge case:** Create the DEFAULT partition after the index exists (Exercise 4): `pg_indexes` then shows a sixth row for `solution_events_default`, created automatically.

## Pitfalls

- Partition bounds are lower-inclusive and upper-exclusive.
- An insert outside all bounds fails unless a default partition exists.
- Put the partition key in filtering predicates so pruning is possible.
- Too many tiny partitions increase planning and maintenance overhead.

## Exercise 3: Prove pruning

The unbounded count can visit every leaf; the March range can prune unrelated
partitions. Inspect named child scans rather than inferring pruning from timing.

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 3, run plain `EXPLAIN` (without `ANALYZE`) on `SELECT COUNT(*) FROM solution_events` with no predicate, then on the same count restricted to the March half-open range.
- **Expected result/shape:** For sql-37 Exercise 3, expected output: the unfiltered plan lists four scans, one per monthly partition, under one `Append`; the March plan lists only `solution_events_2025_03` and has no `Append` node.
- **Independent verification:** For sql-37 Exercise 3, write the predicted number of scanned partitions (4 and 1) before running both plans, then count the `Seq Scan on solution_events_...` lines in each plan and compare them with the prediction.
- **Intermediate relation check:** For sql-37 Exercise 3, compare the planner's estimated rows per partition in the unfiltered plan (1899, 1232, 950, and 919 on this seed) with `SELECT tableoid::regclass, COUNT(*) FROM solution_events GROUP BY 1`.
- **Clause check:** For sql-37 Exercise 3, the solution uses two plain `EXPLAIN` statements over `SELECT COUNT(*) FROM solution_events`, the second with a `WHERE` on `event_time`.
- **Alternative/trade-off:** For sql-37 Exercise 3, `SET enable_partition_pruning = off` in a scratch transaction shows the March query scanning all four partitions, which proves that the setting, not luck, removed them.
- **Edge case:** A predicate written as `date_trunc('month', event_time) = '2025-03-01'` hides the partition key inside a function, so the planner cannot prune and all four partitions are scanned.

## Exercise 4: Route an uncovered row

Because the original tasks already add April, the solution inserts a June row
into the DEFAULT partition and verifies ownership with `tableoid::regclass`.

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 4, add `solution_events_default` as the DEFAULT partition and insert one event dated `2025-06-15 00:00:00+00`, which no monthly partition covers.
- **Expected result/shape:** For sql-37 Exercise 4, expected output: one row, `physical_partition` = `solution_events_default` and `event_time` = `2025-06-15 00:00:00+00`.
- **Independent verification:** For sql-37 Exercise 4, before the DEFAULT partition exists, the same insert fails with SQLSTATE `23514` (`no partition of relation "solution_events" found for row`); after it exists, `SELECT COUNT(*) FROM solution_events_default` returns `1`.
- **Intermediate relation check:** For sql-37 Exercise 4, list the leaf partitions with `pg_partition_tree('solution_events')` before and after `CREATE TABLE ... DEFAULT`; the second list has one more row.
- **Clause check:** For sql-37 Exercise 4, the solution uses `CREATE TABLE ... PARTITION OF solution_events DEFAULT`, one `INSERT ... VALUES`, and a `SELECT tableoid::regclass, event_time ... WHERE event_time = ...`.
- **Alternative/trade-off:** For sql-37 Exercise 4, creating a June partition instead keeps every row in a named range, but later dates fail again until another partition exists; a DEFAULT partition accepts them and needs monitoring.
- **Edge case:** After a row sits in the DEFAULT partition, creating a June partition that covers it fails until that row is moved, because PostgreSQL checks that the default partition holds no rows for the new range.

## Exercise 5: Diagnose a range gap

The catalog query prints every physical bound. Without DEFAULT, a date outside
those bounds raises “no partition ... found”; that failure is preferable to
silent misrouting.

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 5, list the leaf partitions of `solution_events` and their bounds from `pg_partition_tree('solution_events')` joined to `pg_class`, after Exercises 1 to 4 created four monthly partitions and the DEFAULT partition.
- **Expected result/shape:** For sql-37 Exercise 5, expected output: five rows ordered by `c.relname`, with columns `partition_name` and `partition_bound`: four `FOR VALUES FROM (...) TO (...)` rows for January to April and one `DEFAULT` row for `solution_events_default`.
- **Independent verification:** For sql-37 Exercise 5, compare the bound text with the dates you wrote in Exercise 1; then, in a scratch transaction before any DEFAULT partition exists, insert a `2025-07-01 00:00:00+00` row and confirm SQLSTATE `23514`, which this catalog query explains because no listed bound covers July.
- **Intermediate relation check:** For sql-37 Exercise 5, run the catalog query once without `WHERE pt.isleaf`: the parent `solution_events` appears as a non-leaf row with a NULL bound.
- **Clause check:** For sql-37 Exercise 5, the solution joins `pg_partition_tree('solution_events')` to `pg_class` on `oid`, keeps `pt.isleaf`, projects `relid::regclass` and `pg_get_expr(c.relpartbound, c.oid)`, and orders by `c.relname`.
- **Alternative/trade-off:** For sql-37 Exercise 5, psql's `\d+ solution_events` shows the same partitions and bounds interactively, but a catalog query is repeatable inside a script and can be compared row by row.
- **Edge case:** The bound text is printed in the session time zone; after `SET TIME ZONE 'America/New_York'` the same bounds display as `2024-12-31 19:00:00-05` and so on, while the stored instants do not change.

## Exercise 6: Test the exact boundary

February 1 lands in February because range partitions include `FROM` and
exclude `TO`. The query proves placement rather than relying only on prose.

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 6, insert one row at exactly `2025-02-01 00:00:00+00` with `payload` `{"source":"boundary"}`, then read it back by that payload value.
- **Expected result/shape:** For sql-37 Exercise 6, expected output: one row, `physical_partition` = `solution_events_2025_02` and `event_time` = `2025-02-01 00:00:00+00`, because `FROM` bounds are inclusive and `TO` bounds are exclusive.
- **Independent verification:** For sql-37 Exercise 6, insert a second row at `2025-01-31 23:59:59.999999+00` and confirm that `tableoid::regclass` reports `solution_events_2025_01` for it, so the two instants one microsecond apart land in different partitions.
- **Intermediate relation check:** For sql-37 Exercise 6, select `tableoid::regclass` and `event_time` for both boundary rows in one query ordered by `event_time` to see the change of partition.
- **Clause check:** For sql-37 Exercise 6, the solution uses one `INSERT ... VALUES` and a `SELECT tableoid::regclass, event_time ... WHERE payload ->> 'source' = 'boundary'`.
- **Alternative/trade-off:** For sql-37 Exercise 6, a `timestamp` (without time zone) partition key would compare local wall-clock values instead of instants; `timestamptz` keeps the boundary independent of the session time zone.
- **Edge case:** Insert `2025-02-01 00:00:00-01` (01:00 UTC): it also lands in February, because the bound is compared as an instant, not as text.
