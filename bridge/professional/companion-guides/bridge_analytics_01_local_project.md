# BRIDGE-ANALYTICS-01 — Local analytics engineering project

## Level and prerequisites

**Level:** Advanced  
**Stable lesson ID:** `bridge-analytics-01`  
**Catalog prerequisites:** `python-data-01`, `sql-analytics-01`, and
`bridge-05`  
**Prerequisites:** the
[professional columnar-data module](../../../python/professional/companion-guides/py_data_01_arrow_duckdb.md),
[advanced analytical SQL lab](../../../sql/professional/companion-guides/sql_analytics_01_query_patterns.md),
and [Bridge Day 5](../../companion-guides/day05_db_testing_fixtures_doubles.md).
Those paths include the Python Day 23 and SQL Day 30 foundations.

This module builds a small dbt-style analytics project entirely in an in-memory
DuckDB database. “dbt-style” means models form a declared directed acyclic graph
(DAG), transformations are select statements materialized in dependency order,
grain and contracts are explicit, and data tests plus reconciliation gate the
mart. It does not require the dbt package, a hosted warehouse, an account,
credentials, a network connection, or local database files.

Install the professional and quality profiles once while connected if the
normal setup has not already installed them:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pip install -e ".[professional,quality]"
```

```bash
# macOS/Linux
.venv/bin/python -m pip install -e ".[professional,quality]"
```

Run the answer-free starter:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\professional\lessons\bridge_analytics_01_local_project.py
```

```bash
# macOS/Linux
.venv/bin/python bridge/professional/lessons/bridge_analytics_01_local_project.py
```

Run the completed local project:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\professional\solutions\bridge_analytics_01_local_project_solution.py
```

```bash
# macOS/Linux
.venv/bin/python bridge/professional/solutions/bridge_analytics_01_local_project_solution.py
```

The solution builds twice in the same in-memory connection and asserts that the
ordered snapshot is identical. Closing the process removes all tables.


<!-- BEGIN BRIDGE ENRICHMENT: HOW TO RUN -->
## How to run this lesson

Start at the repository root. The answer-free starter is deliberately safe to
run: it prints orientation text and does not call unfinished functions or
contact PostgreSQL.

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\professional\lessons\bridge_analytics_01_local_project.py
.\.venv\Scripts\python.exe -m pytest bridge\professional\tests -q
```

```bash
# macOS/Linux
.venv/bin/python bridge/professional/lessons/bridge_analytics_01_local_project.py
.venv/bin/python -m pytest bridge/professional/tests -q
```

Read this guide first, implement one boundary at a time in
`bridge/professional/lessons/bridge_analytics_01_local_project.py`, and use small fakes or recording doubles for the
default evidence path. This lesson uses only an in-memory DuckDB database created by the process. Closing the process removes it; do not create or commit a local database file.
<!-- END BRIDGE ENRICHMENT: HOW TO RUN -->

## Learning objectives

By the end, you can:

- describe source, staging, intermediate, and mart responsibilities;
- declare a table's grain before writing its query;
- represent model lineage as a dependency DAG;
- topologically order models and reject missing dependencies or cycles;
- validate deterministic producer fixtures before loading them;
- keep source contracts distinct from transformed table contracts;
- rebuild models idempotently with trusted names and `CREATE OR REPLACE`;
- define a semantic metric with model, expression, aggregation, time
  dimension, unit, and exclusions;
- express data tests as queries returning violating rows;
- test uniqueness, not-null, accepted values, relationships, and business
  rules;
- reconcile a mart to its intermediate-detail source;
- prove a second clean rebuild returns the same rows and tests.

## Vocabulary and concepts

| Term | Meaning |
|---|---|
| analytics engineering | Building tested, documented, reusable data models for analysis |
| source | Producer-owned raw input boundary |
| staging model | Thin rename, cast, trim, and standardization layer |
| intermediate model | Reusable transformation at a clearly declared grain |
| mart | Consumer-facing table shaped for a business question |
| grain | What exactly one row represents |
| DAG | Directed acyclic graph of model dependencies |
| lineage | Upstream sources and models that contribute to an output |
| producer contract | Expected source columns, types, nullability, and key |
| table contract | Expected transformed columns, SQL types, and semantic key |
| data test | Query whose returned rows represent violations |
| reconciliation | Independent comparison proving aggregate outputs match detail |
| semantic metric | Shared definition of a measure, aggregation, time, unit, and exclusions |
| idempotent rebuild | Repeating the same build yields the same declared state |
| materialization | How a select statement becomes a relation; this lab uses tables |

## Worked example / walkthrough

### 1. Start from deterministic producer fixtures

Three local sources model customers, orders, and order lines. Values are fixed
tuples in source control; no clock, random generator, download, or personal
data is involved.

Each `ProducerContract` declares:

- source name;
- grain statement;
- primary-key columns;
- ordered columns;
- allowed Python types;
- nullability;
- expected SQL type family.

`validate_producer_rows()` checks width, types, nullability, and unique keys
before a value reaches DuckDB. SQL values are inserted with `?` parameters;
fixture data is never interpolated into query text.

Producer contracts do not make upstream data trustworthy forever. In a real
pipeline, record schema version, producer owner, freshness expectation, late
arrival policy, and compatibility window.

### 2. Declare model grain and lineage

The project DAG is:

```text
raw_customers ───────────────> stg_customers ───────────────┐
                                                            │
raw_orders ──────────────────> stg_orders ───────────┐       │
                                                    ├──> int_order_revenue
raw_order_items ─────────────> stg_order_items ─────┘              │
                                                                   v
                                                        mart_daily_revenue
```

`stg_customers` participates in the relationship tests even though the current
revenue intermediate model needs only customer IDs from orders.

The declared grains are:

| Model | Grain |
|---|---|
| `stg_customers` | one row per `customer_id` |
| `stg_orders` | one row per `order_id` |
| `stg_order_items` | one row per `order_id`, `line_id` |
| `int_order_revenue` | one row per paid/shipped `order_id` |
| `mart_daily_revenue` | one row per `order_date` |

Write the grain before SQL. If a join changes row count unexpectedly, compare
both sides to their declared grain before adding `DISTINCT`, which often hides
the defect.

### 3. Topologically order the DAG

`topological_order()` treats raw names as already resolved. On each pass it
selects all models whose dependencies are resolved, sorts their names for
determinism, and appends them. It rejects:

- duplicate model names;
- a dependency that is neither a source nor a model;
- a cycle with no resolvable next model.

A deterministic build order makes logs, tests, and diffs easier to compare.

### 4. Give each layer one job

Staging models:

- cast IDs and dates;
- trim names;
- normalize categorical case;
- preserve source grain;
- avoid business aggregation.

`int_order_revenue` joins completed orders to line items and computes one
`order_revenue` per order. It excludes `cancelled` and `placed` status by a
documented business rule.

`mart_daily_revenue` aggregates completed-order revenue by date and publishes
gross revenue, order count, and distinct customer count.

The project uses trusted checked-in model names. `_trusted_identifier()` guards
the small f-string boundary used for `CREATE OR REPLACE TABLE` and `DESCRIBE`.
Runtime data values use DuckDB parameters. Do not generalize this into accepting
arbitrary user-provided model names or SQL.

### 5. Define a semantic metric

The reference metric records:

```text
name: gross_revenue
model: mart_daily_revenue
expression: gross_revenue
aggregation: sum
time dimension: order_date
unit: currency units
```

Its description states the calculation and exclusions: quantity times unit
price for paid or shipped orders; cancelled and placed orders are excluded.

A useful metric definition also needs currency handling, refund policy, time
zone, late-arriving data behavior, and ownership in a real system. The course
fixture uses one abstract currency and a date without time-zone conversion, so
the definition says so rather than implying global correctness.

### 6. Validate the transformed table contract

`MART_CONTRACT` declares ordered column names, compatible DuckDB type prefixes,
primary key, and grain. `validate_table_contract()` compares `DESCRIBE` output
with this declaration.

DuckDB `CREATE TABLE AS SELECT` does not automatically preserve every source
constraint. Semantic nullability and uniqueness therefore remain data tests,
not assumptions inferred from physical DDL.

### 7. Treat tests as violation queries

Every `DataTest` returns bad rows:

- duplicate or null customer IDs;
- duplicate or null order IDs and unsupported statuses;
- orders without a customer;
- null/non-positive line quantities or negative prices;
- duplicate/non-positive intermediate order revenue;
- duplicate/null/negative daily mart rows.

The runner wraps each query and counts violations. Zero is pass. Returning bad
rows instead of a boolean makes a failure inspectable during development.

Do not use SQLite as a DuckDB test substitute. SQL functions, type behavior,
date casting, decimal arithmetic, and query plans differ.

### 8. Reconcile independently

The reconciliation recomputes daily revenue, order count, and distinct customer
count from `int_order_revenue`, full-outer-joins to the mart, and fails if any
value is distinct.

This catches mistakes a mart-only uniqueness test cannot, such as dropping a
date or double-counting one order. The comparison is independent of the mart
SQL while retaining the same documented metric policy.

In financial systems, use explicit currency grain and tolerance/rounding
policy. Here both paths retain exact `DECIMAL` values, so `IS DISTINCT FROM`
is appropriate.

### 9. Prove rebuild idempotency

Source and model loaders use `CREATE OR REPLACE TABLE`, then parameterized
fixture inserts and deterministic select statements. `main()` runs the full
project twice and compares:

- build order;
- named test results;
- ordered mart snapshot.

Idempotency here means a clean rebuild converges to the same local state. It
does not prove incremental processing, late-arriving updates, or concurrent
deployment safety; those need separate stateful exercises.

## Exercises

### Practice contract

- **Focus:** Build a local dbt-style DuckDB project with producer contracts, deterministic DAG order, layered grain, table/metric contracts, violation tests, and independent reconciliation.
- **Assumptions:** The project runs offline on deterministic local fixtures; source rows preserve types/order; trusted model names are validated before DDL structure is generated.
- **Primary failure mode:** A model can execute successfully while still duplicating grain, drifting schema, misdefining a metric, or failing reconciliation.
- **Evidence loop:** state the boundary and prediction, implement against
  deterministic local doubles, test success/failure/cleanup, and label any
  optional live-adapter evidence separately from offline proof.

1. **Producer contract:** Add primary-key validation and a duplicate fixture failure for every
   producer contract.
   - **Progressive hint:** Validate the complete key tuple and report only safe row position/key
     metadata.
   - **Verify:** For each producer contract, load one unique fixture successfully, duplicate its primary-key tuple, and assert validation fails with the source/grain named before DuckDB insertion.
2. **DAG:** Draw dependencies and implement deterministic topological order with
   missing-dependency and cycle detection.
   - **Progressive hint:** Break ties by stable model name so valid independent branches are
     reproducible.
   - **Verify:** Assert raw sources precede dependent staging/intermediate/mart models with stable name ordering; an unknown dependency and a two-model cycle each raise `ValueError` listing unresolved names.
3. **Staging:** Implement the three staging models without aggregation or `DISTINCT` and state
   each row grain.
   - **Progressive hint:** Staging should rename/cast, not hide duplicate producer rows.
   - **Verify:** Compare staging row counts with their raw sources, assert no `DISTINCT`/aggregation, and record grains `customer_id`, `order_id`, and `(order_id, line_number)` with typed/normalized columns.
4. **Intermediate model:** Declare `int_order_revenue` grain, predict row count, then implement
   its join and aggregate.
   - **Progressive hint:** Aggregate line items to one row per order before joining other facts.
   - **Verify:** Predict and assert one row per order in `int_order_revenue`, with exact summed item revenue and retained customer/status/date fields; row count equals raw orders, including orders without matching items per policy.
5. **Mart:** Build `mart_daily_revenue` and document exact status exclusions and UTC/date
   semantics.
   - **Progressive hint:** Every selected non-aggregate must belong to the daily grain.
   - **Verify:** Assert one row per UTC order date, only the documented completed/paid statuses contribute, revenue/order/customer measures match fixtures, and output is ordered by date.
6. **Identifier safety:** Validate trusted model names before using them in generated DDL.
   - **Progressive hint:** Parameters cannot bind identifiers; constrain structure with a strict
     grammar/allowlist.
   - **Verify:** Pass every checked-in model name and injection-shaped/uppercase/punctuated names; assert only names matching the trusted identifier policy reach generated DDL.
7. **Schema contract:** Compare `DESCRIBE` output with `MART_CONTRACT`; make separate name and
   type drift fixtures.
   - **Progressive hint:** Check position, normalized type prefix, and nullability according to
     declared policy.
   - **Verify:** Compare exact `DESCRIBE` column order/type compatibility with `MART_CONTRACT`; separate fixtures must report name drift and type drift distinctly before publication.
8. **Data tests:** Write zero-row violation queries for uniqueness, not-null, accepted status,
   relationships, and positive money/quantity rules.
   - **Progressive hint:** A test query returns violating rows; passing means count zero.
   - **Verify:** Execute each violation query against valid fixtures and assert zero rows; inject one uniqueness, null, status, relationship, money, and quantity violation and assert its named test returns evidence rows.
9. **Reconciliation:** Write an independent reconciliation for mart revenue, orders, and
   customers by day.
   - **Progressive hint:** Do not reuse the mart's exact transformation path for its check.
   - **Verify:** Independently recompute daily revenue/order/customer measures from order grain and full-outer compare; assert zero mismatches, then perturb each mart measure and observe a dated mismatch row.
10. **Semantic metric:** Define one extra metric with aggregation, grain, time dimension, unit,
   exclusions, and denominator.
   - **Progressive hint:** A metric definition is a contract, not merely a SQL expression.
   - **Verify:** Define an additional metric with model, expression, aggregation, grain, time dimension, unit, exclusions, and denominator; calculate one fixture date and compare the exact value.
11. **Idempotency:** Run the project twice in one connection and prove identical ordered
   snapshots.
   - **Progressive hint:** Rebuild semantics should replace trusted models rather than append.
   - **Verify:** Run the project twice in one connection; assert identical ordered snapshots, row counts, test results, and reconciliation, with no duplicate append state.
12. **Impact analysis:** Add one deterministic source row, predict every downstream change, then
   update tests without weakening contracts.
   - **Progressive hint:** Write expected deltas before executing the rebuild.
   - **Verify:** Add one source row and write predicted staging/intermediate/mart row and measure deltas first; assert the actual snapshot matches every predicted change and existing contracts remain unchanged.
13. **Freshness:** Add a producer freshness contract with an injected as-of time and distinguish
   stale from missing data.
   - **Progressive hint:** Time-based tests must not call the wall clock directly.
   - **Verify:** With an injected as-of instant, assert a present old source is reported stale, an absent source missing, and a recent source current using the declared threshold.
14. **Build strategy:** Compare full rebuild and incremental processing for this local project
   and state what evidence is missing for incrementality.
   - **Progressive hint:** Idempotent full rebuild is the reference correctness baseline.
   - **Verify:** Provide a comparison of full rebuild versus incremental state, keys, late updates, delete handling, and atomic publication; mark incrementality unproved until change-capture and replay tests exist.
15. **Money correctness:** Trace exact revenue from producer Decimal through DuckDB type,
   aggregation, Python snapshot, and reconciliation.
   - **Progressive hint:** Reject silent float conversion and premature rounding.
   - **Verify:** Trace one exact Decimal from source tuple through DuckDB `DECIMAL`, order aggregation, mart aggregation, Python snapshot, and reconciliation; assert equality at every boundary without float conversion.
16. **NULL semantics:** Choose behavior for missing dimension labels and prove it does not
   change fact row count or measure totals.
   - **Progressive hint:** An `unknown` label is a business rule; a filtering join is a
     data-loss bug unless declared.
   - **Verify:** Inject a missing dimension label; assert the declared replacement/NULL policy, unchanged fact row count, and unchanged revenue/order totals.
17. **Time semantics:** Define daily boundaries for timezone-aware source instants and test an
   order around midnight.
   - **Progressive hint:** Convert the instant to the reporting zone before deriving its date.
   - **Verify:** Place timezone-aware orders immediately before and after the declared UTC midnight; assert they land on the two expected dates and no local-machine timezone changes the snapshot.
18. **Late data:** Model a late-arriving order for a previously built day and compare full
   rebuild with an incremental repair.
   - **Progressive hint:** Watermarks based only on event time can miss late records.
   - **Verify:** Add a late order to an already-built date; assert full rebuild corrects that date and the proposed incremental repair reprocesses the same affected partition to an identical result.
19. **Snapshot determinism:** Require explicit ordering and stable serialization for mart
   snapshots across platforms.
   - **Progressive hint:** Database row order is undefined without final `ORDER BY`.
   - **Verify:** Assert mart queries include a complete unique order, serialize dates/Decimals with the documented stable format, and produce byte-identical snapshots across repeated runs.
20. **Performance:** Inspect a bounded `EXPLAIN` for the intermediate/mart build and identify
   one optimization that preserves grain.
   - **Progressive hint:** Optimize after contracts and reconciliation pass.
   - **Verify:** Capture bounded `EXPLAIN` output for intermediate and mart builds, identify scan/join/aggregate operators, and propose one optimization whose post-change grain, counts, and reconciliation remain identical.
21. **Lineage:** Produce a compact source-to-metric lineage table from `depends_on` and metric
   definitions.
   - **Progressive hint:** Lineage should be derivable from checked-in contracts rather than
     hand-maintained prose alone.
   - **Verify:** Generate lineage rows from every raw source through models to each metric; assert all declared dependencies appear, no orphan/cycle exists, and `gross_revenue` terminates at `mart_daily_revenue`.
22. **Transaction:** Design build publication so readers do not observe half-rebuilt models
   after a failure.
   - **Progressive hint:** Check DuckDB transaction/DDL semantics rather than assuming
     atomicity.
   - **Verify:** Inject failure before publication and assert readers retain the prior complete mart; the design must stage or transact replacement so no partial model set becomes visible.
23. **Failure policy:** Make any contract, data-test, or reconciliation failure stop publication
   while retaining inspectable results.
   - **Progressive hint:** Do not continue to a green artifact after a red quality gate.
   - **Verify:** Force producer-contract, table-contract, data-test, and reconciliation failures separately; assert each blocks publication while retaining the named failing query/result for diagnosis.
24. **Portable artifact:** Export a deterministic local result with manifest, metric
   definitions, test evidence, and cleanup instructions.
   - **Progressive hint:** Separate generated artifacts from source and never include local
     paths or credentials.
   - **Verify:** Export an ordered result plus manifest containing lesson/version, schema/grain, metric definitions, source fixture hashes, test/reconciliation results, creation command, and cleanup; repeat and compare deterministically.

### Before opening the solution

- Record what the offline doubles prove and what they cannot prove.
- Inspect exact call order, parameters, schema, and failure behavior.
- Keep credentials, payloads, and high-cardinality identifiers out of output.
- Require deterministic reruns before considering an exercise complete.


## Self-check

- Is every source and model grain written in plain language?
- Can you trace every mart column to its upstream models?
- Does the DAG reject missing dependencies and cycles?
- Are producer rows checked before loading?
- Are SQL values parameterized?
- Are dynamic DDL names limited to trusted checked-in identifiers?
- Does staging avoid business aggregation?
- Is intermediate order revenue exactly one row per completed order?
- Does the semantic metric define calculation, aggregation, time, unit, and
  exclusions?
- Do data tests return violating rows and pass only at zero?
- Does reconciliation compare all published measures to detail?
- Does the second full rebuild produce an identical ordered snapshot?
- Does the project use in-memory DuckDB with no hosted account or local data
  file?

## Common pitfalls

- **Writing SQL before grain:** join and aggregate defects become hard to name.
- **Using `DISTINCT` to fix duplicates:** it can hide an incorrect many-to-many
  join.
- **Mixing business rules into staging:** downstream reuse and debugging suffer.
- **Treating a DAG diagram as executable lineage:** dependencies must drive
  actual build order.
- **Validating only column presence:** order, type, key, nullability, and
  semantics can still drift.
- **Testing only the mart:** source, relationship, and intermediate-grain
  failures remain hidden.
- **Reusing mart SQL for reconciliation:** both paths can share the same defect.
- **Interpolating fixture values:** use DuckDB parameter sequences.
- **Accepting runtime identifiers:** checked-in model names are a code boundary,
  not user data.
- **Using floats for money:** the project casts to exact decimal arithmetic.
- **Claiming incremental idempotency from a full rebuild:** stateful incremental
  behavior needs its own fixtures and watermarks.
- **Writing a local `.duckdb` file by default:** in-memory execution keeps tests
  isolated and USB-safe.


<!-- BEGIN BRIDGE ENRICHMENT: ASK CODEX -->
## Ask Codex about this lesson

Use the checked-in `guide-ds60sqlpy-learning` skill as a tutor, not as an
answer generator. The direct catalog prerequisites are `bridge-05`, `python-data-01`, `sql-analytics-01`. The
prompt below deliberately names exact paths so a new Codex task can orient
itself without guessing.

```text
Tutor me through stable lesson ID bridge-analytics-01: Analytics Engineering, Lineage, and Data Contracts.
Direct catalog prerequisites: bridge-05, python-data-01, sql-analytics-01. Assume I completed exactly those
prerequisites, then begin with one short Retrieval question that connects each
prerequisite to this lesson.

Use repository skill guide-ds60sqlpy-learning.
Companion guide: bridge/professional/companion-guides/bridge_analytics_01_local_project.md
Learner artifact: bridge/professional/lessons/bridge_analytics_01_local_project.py

Do not open, quote, summarize, or copy anything under solutions/ until I
explicitly say I have finished my attempt and ask to compare.

Use these coaching phases in order:
1. Predict — ask what I expect before I run or change code.
2. Attempt — let me implement or explain one numbered exercise at a time.
3. Hint — give the smallest useful conceptual hint, never a finished answer.
4. Evidence — ask for the exact return value, exception type, recorded calls,
   query plus bound parameters, or written decision required by that exercise.
5. Retrieval — close with two no-notes questions and one transfer problem.

Keep the default path offline and fake-first. If the lesson has an optional
PostgreSQL step, require my explicit opt-in, DS60_DATABASE_URL, and the
disposable advanced_sql_training database; never ask me to paste the URL.

Done when every numbered exercise has its own evidence, normal/edge/failure
behavior is explained in my words, the relevant offline tests pass, and I can
solve the final transfer problem without opening solutions/.
```
<!-- END BRIDGE ENRICHMENT: ASK CODEX -->

## Next step

Complete the
[learner file](../lessons/bridge_analytics_01_local_project.py) and add a
deliberately failing contract case before reviewing the
[reference implementation](../solutions/bridge_analytics_01_local_project_solution.py)
and [solution reasoning](../solutions/bridge_analytics_01_local_project_solutions.md).
Then adapt the same source → staging → intermediate → mart pattern to a small
local dataset whose grain and ownership you can state precisely.
