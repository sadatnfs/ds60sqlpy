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

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** An alternative physical/object design is valid only if catalog inspection and valid/invalid behavior prove the same invariant.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Pitfalls

- Partition bounds are lower-inclusive and upper-exclusive.
- An insert outside all bounds fails unless a default partition exists.
- Put the partition key in filtering predicates so pruning is possible.
- Too many tiny partitions increase planning and maintenance overhead.

## Exercise 3 — Prove pruning

The unbounded count can visit every leaf; the March range can prune unrelated
partitions. Inspect named child scans rather than inferring pruning from timing.

### Reasoning and verification

- **Expected result/shape:** A written prediction plus the actual query/plan output, including the compared row counts, keys, measures, or SQLSTATE named by the prompt.
- **Independent verification:** Run both cases with the same inputs, record the observed difference, and revise the explanation if evidence contradicts the prediction.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 4 — Route an uncovered row

Because the original tasks already add April, the solution inserts a June row
into the DEFAULT partition and verifies ownership with `tableoid::regclass`.

### Reasoning and verification

- **Expected result/shape:** The statement completes with the expected command tag, and a catalog or behavior query exposes the named object/rule; no unrelated schema object persists.
- **Independent verification:** Inspect the applicable pgcatalog/informationschema entry and run one valid plus one boundary case inside the lesson's safety boundary.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 5 — Diagnose a range gap

The catalog query prints every physical bound. Without DEFAULT, a date outside
those bounds raises “no partition ... found”; that failure is preferable to
silent misrouting.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 6 — Test the exact boundary

February 1 lands in February because range partitions include `FROM` and
exclude `TO`. The query proves placement rather than relying only on prose.

### Reasoning and verification

- **Expected result/shape:** A table-shaped result containing every key/measure named in the prompt; the result must preserve the row grain described in the walkthrough and expose every named key or measure.
- **Independent verification:** Check uniqueness at the declared grain, deterministic ordering when rows are ranked/limited, and reconcile counts or totals to a simpler control query over the same population.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.
