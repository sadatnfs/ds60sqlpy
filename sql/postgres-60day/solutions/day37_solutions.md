# Day 37 — Solutions: Partitioning


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\postgres-60day\solutions\day37_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/postgres-60day/solutions/day37_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Partition bound, Partition pruning, Sharding. Its worked-model focus is:
Map the January and February bounds on a timeline, then plan a January-15-to-February-15 query. Both partitions are required. Change the range to a January-only half-open interval and inspect EXPLAIN to prove February is pruned rather than assuming it.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 1, run the underlying read-only query over `solution_big_events` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-37 Exercise 1, expected output: one row per `big_events`. The final columns are `big_events`.
- **Independent verification:** For sql-37 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `big_events` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-37 Exercise 1, run the underlying query without `EXPLAIN` and preserve its `big_events` rows.
- **Clause check:** For sql-37 Exercise 1, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `solution_big_events`, preserve one row per `big_events`, and finish with `big_events`.
- **Alternative/trade-off:** For sql-37 Exercise 1, the chosen form is justified by this lesson-specific rationale: Temporary tables keep the answer isolated from the learner script's `big_events` names. Evaluate another form against the concrete expected result (one row per `big_events`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

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

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 2, run the underlying read-only query over `indexed_big_events`, `indexed_big_events_2025_01_time_idx`, `indexed_big_events_2025_02_time_idx`, `indexed_big_events_2025_03_time_idx`, and `indexed_big_events_2025_01` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-37 Exercise 2, expected output: one row per `plan_node`. The final columns are `plan_node`, `estimated_rows`, `actual_rows`, `loops`, and `buffers`.
- **Independent verification:** For sql-37 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-37 Exercise 2, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows.
- **Clause check:** For sql-37 Exercise 2, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `indexed_big_events`, `indexed_big_events_2025_01_time_idx`, `indexed_big_events_2025_02_time_idx`, `indexed_big_events_2025_03_time_idx`, and `indexed_big_events_2025_01`, preserve one row per `plan_node`, and finish with `plan_node`, `estimated_rows`, `actual_rows`, `loops`, and `buffers`.
- **Alternative/trade-off:** For sql-37 Exercise 2, the chosen form is justified by this lesson-specific rationale: Expected logical result: the before and after queries return the same March rows. Evaluate another form against the concrete expected result (one row per `plan_node`) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Pitfalls

- Partition bounds are lower-inclusive and upper-exclusive.
- An insert outside all bounds fails unless a default partition exists.
- Put the partition key in filtering predicates so pruning is possible.
- Too many tiny partitions increase planning and maintenance overhead.

## Exercise 3 — Prove pruning

The unbounded count can visit every leaf; the March range can prune unrelated
partitions. Inspect named child scans rather than inferring pruning from timing.

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 3, run the underlying read-only query over `solution_events` before collecting its plan. Keep seed rows, parameters, settings, and statistics fixed for each comparison.
- **Expected result/shape:** For sql-37 Exercise 3, expected output: exactly one aggregate summary row. The final columns are `plan_node`, `estimated_rows`, `actual_rows`, `loops`, and `buffers`.
- **Independent verification:** For sql-37 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows. Then read scan inputs, estimated versus actual rows × loops, filter losses, buffers, and the root node; a different node type is not itself a failure. Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.
- **Intermediate relation check:** For sql-37 Exercise 3, run the underlying query without `EXPLAIN` and preserve its `plan_node` rows.
- **Clause check:** For sql-37 Exercise 3, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `solution_events`, preserve exactly one summary row, and finish with `plan_node`, `estimated_rows`, `actual_rows`, `loops`, and `buffers`.
- **Alternative/trade-off:** For sql-37 Exercise 3, the chosen form is justified by this lesson-specific rationale: The unbounded count can visit every leaf; the March range can prune unrelated partitions. Evaluate another form against the concrete expected result (exactly one aggregate summary row) and the verification above.
- **Edge case:** Compare one selective and one broad parameter while seed rows, settings, and statistics remain unchanged.

## Exercise 4 — Route an uncovered row

Because the original tasks already add April, the solution inserts a June row
into the DEFAULT partition and verifies ownership with `tableoid::regclass`.

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 4, read from `solution_events`, and `solution_events_default`. Build the answer toward `physical_partition`, and `event_time`; keep `physical_partition` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-37 Exercise 4, expected output: one row per `physical_partition`. The final columns are `physical_partition`, and `event_time`.
- **Independent verification:** For sql-37 Exercise 4, run an anti-check that counts rows where NOT ((event_time = timestamptz '2025-06-15 00:00:00+00')); require unique `physical_partition` where the expected grain is one row per key and confirm the projected `physical_partition`, and `event_time` against `solution_events`, and `solution_events_default`. Add one row for which `(event_time = timestamptz '2025-06-15 00:00:00+00')` is true and one for which it is false; verify only the matching `physical_partition` value is returned.
- **Intermediate relation check:** For sql-37 Exercise 4, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-37 Exercise 4, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `solution_events`, and `solution_events_default`, preserve one row per `physical_partition`, and finish with `physical_partition`, and `event_time`.
- **Alternative/trade-off:** For sql-37 Exercise 4, the chosen form is justified by this lesson-specific rationale: Because the original tasks already add April, the solution inserts a June row into the DEFAULT partition and verifies ownership with `tableoid::regclass`. Evaluate another form against the concrete expected result (one row per `physical_partition`) and the verification above.
- **Edge case:** Add one row for which `(event_time = timestamptz '2025-06-15 00:00:00+00')` is true and one for which it is false; verify only the matching `physical_partition` value is returned.

## Exercise 5 — Diagnose a range gap

The catalog query prints every physical bound. Without DEFAULT, a date outside
those bounds raises “no partition ... found”; that failure is preferable to
silent misrouting.

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 5, read the target keys from `pg_class` before writing. Keep the change inside the lesson transaction and capture the command tag or `RETURNING` values.
- **Expected result/shape:** For sql-37 Exercise 5, expected output: the command tag and an independently counted set of affected `partition_name` values. The final columns are `partition_name`, and `partition_bound`. The final order is `c.relname`.
- **Independent verification:** For sql-37 Exercise 5, materialize the intended `partition_name` target set first; require the command tag/`RETURNING` set to match it, then query `pg_class` again and prove rollback or idempotent retry. Use an empty target set and a multi-row target set; reconcile the affected `partition_name` values in both cases.
- **Intermediate relation check:** For sql-37 Exercise 5, start with the first relation in `pg_class`; after each join, record total rows and distinct `partition_name` so the exact fanout or loss is visible.
- **Clause check:** For sql-37 Exercise 5, the solution actually uses `FROM`, `JOIN ... ON`, `WHERE`, `SELECT`, and `ORDER BY`. Read only those operations: begin at `pg_class`, preserve one row per `partition_name`, and finish with `partition_name`, and `partition_bound` ordered by `c.relname`.
- **Alternative/trade-off:** For sql-37 Exercise 5, the chosen form is justified by this lesson-specific rationale: The catalog query prints every physical bound. Evaluate another form against the concrete expected result (the command tag and an independently counted set of affected `partition_name` values) and the verification above.
- **Edge case:** Use an empty target set and a multi-row target set; reconcile the affected `partition_name` values in both cases.

## Exercise 6 — Test the exact boundary

February 1 lands in February because range partitions include `FROM` and
exclude `TO`. The query proves placement rather than relying only on prose.

### Reasoning and verification

- **Inputs/evidence:** For sql-37 Exercise 6, read from `solution_events`. Build the answer toward `physical_partition`, and `event_time`; keep `physical_partition` visible whenever the result has row-level grain.
- **Expected result/shape:** For sql-37 Exercise 6, expected output: one row per `physical_partition`. The final columns are `physical_partition`, and `event_time`.
- **Independent verification:** For sql-37 Exercise 6, run an anti-check that counts rows where NOT ((payload->>'source' = 'boundary')); require unique `physical_partition` where the expected grain is one row per key and confirm the projected `physical_partition`, and `event_time` against `solution_events`. Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
- **Intermediate relation check:** For sql-37 Exercise 6, inspect the source keys that survive `WHERE`.
- **Clause check:** For sql-37 Exercise 6, the solution actually uses `FROM`, `WHERE`, and `SELECT`. Read only those operations: begin at `solution_events`, preserve one row per `physical_partition`, and finish with `physical_partition`, and `event_time`.
- **Alternative/trade-off:** For sql-37 Exercise 6, the chosen form is justified by this lesson-specific rationale: February 1 lands in February because range partitions include `FROM` and exclude `TO`. Evaluate another form against the concrete expected result (one row per `physical_partition`) and the verification above.
- **Edge case:** Insert rows immediately before, exactly at, and immediately after the literal lower and upper comparisons in the final `WHERE` clause; identify which rows pass each inclusive or exclusive comparison.
