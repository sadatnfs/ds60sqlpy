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
2. **DAG:** Draw dependencies and implement deterministic topological order with
   missing-dependency and cycle detection.
   - **Progressive hint:** Break ties by stable model name so valid independent branches are
     reproducible.
3. **Staging:** Implement the three staging models without aggregation or `DISTINCT` and state
   each row grain.
   - **Progressive hint:** Staging should rename/cast, not hide duplicate producer rows.
4. **Intermediate model:** Declare `int_order_revenue` grain, predict row count, then implement
   its join and aggregate.
   - **Progressive hint:** Aggregate line items to one row per order before joining other facts.
5. **Mart:** Build `mart_daily_revenue` and document exact status exclusions and UTC/date
   semantics.
   - **Progressive hint:** Every selected non-aggregate must belong to the daily grain.
6. **Identifier safety:** Validate trusted model names before using them in generated DDL.
   - **Progressive hint:** Parameters cannot bind identifiers; constrain structure with a strict
     grammar/allowlist.
7. **Schema contract:** Compare `DESCRIBE` output with `MART_CONTRACT`; make separate name and
   type drift fixtures.
   - **Progressive hint:** Check position, normalized type prefix, and nullability according to
     declared policy.
8. **Data tests:** Write zero-row violation queries for uniqueness, not-null, accepted status,
   relationships, and positive money/quantity rules.
   - **Progressive hint:** A test query returns violating rows; passing means count zero.
9. **Reconciliation:** Write an independent reconciliation for mart revenue, orders, and
   customers by day.
   - **Progressive hint:** Do not reuse the mart's exact transformation path for its check.
10. **Semantic metric:** Define one extra metric with aggregation, grain, time dimension, unit,
   exclusions, and denominator.
   - **Progressive hint:** A metric definition is a contract, not merely a SQL expression.
11. **Idempotency:** Run the project twice in one connection and prove identical ordered
   snapshots.
   - **Progressive hint:** Rebuild semantics should replace trusted models rather than append.
12. **Impact analysis:** Add one deterministic source row, predict every downstream change, then
   update tests without weakening contracts.
   - **Progressive hint:** Write expected deltas before executing the rebuild.
13. **Freshness:** Add a producer freshness contract with an injected as-of time and distinguish
   stale from missing data.
   - **Progressive hint:** Time-based tests must not call the wall clock directly.
14. **Build strategy:** Compare full rebuild and incremental processing for this local project
   and state what evidence is missing for incrementality.
   - **Progressive hint:** Idempotent full rebuild is the reference correctness baseline.
15. **Money correctness:** Trace exact revenue from producer Decimal through DuckDB type,
   aggregation, Python snapshot, and reconciliation.
   - **Progressive hint:** Reject silent float conversion and premature rounding.
16. **NULL semantics:** Choose behavior for missing dimension labels and prove it does not
   change fact row count or measure totals.
   - **Progressive hint:** An `unknown` label is a business rule; a filtering join is a
     data-loss bug unless declared.
17. **Time semantics:** Define daily boundaries for timezone-aware source instants and test an
   order around midnight.
   - **Progressive hint:** Convert the instant to the reporting zone before deriving its date.
18. **Late data:** Model a late-arriving order for a previously built day and compare full
   rebuild with an incremental repair.
   - **Progressive hint:** Watermarks based only on event time can miss late records.
19. **Snapshot determinism:** Require explicit ordering and stable serialization for mart
   snapshots across platforms.
   - **Progressive hint:** Database row order is undefined without final `ORDER BY`.
20. **Performance:** Inspect a bounded `EXPLAIN` for the intermediate/mart build and identify
   one optimization that preserves grain.
   - **Progressive hint:** Optimize after contracts and reconciliation pass.
21. **Lineage:** Produce a compact source-to-metric lineage table from `depends_on` and metric
   definitions.
   - **Progressive hint:** Lineage should be derivable from checked-in contracts rather than
     hand-maintained prose alone.
22. **Transaction:** Design build publication so readers do not observe half-rebuilt models
   after a failure.
   - **Progressive hint:** Check DuckDB transaction/DDL semantics rather than assuming
     atomicity.
23. **Failure policy:** Make any contract, data-test, or reconciliation failure stop publication
   while retaining inspectable results.
   - **Progressive hint:** Do not continue to a green artifact after a red quality gate.
24. **Portable artifact:** Export a deterministic local result with manifest, metric
   definitions, test evidence, and cleanup instructions.
   - **Progressive hint:** Separate generated artifacts from source and never include local
     paths or credentials.

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

## Next step

Complete the
[learner file](../lessons/bridge_analytics_01_local_project.py) and add a
deliberately failing contract case before reviewing the
[reference implementation](../solutions/bridge_analytics_01_local_project_solution.py)
and [solution reasoning](../solutions/bridge_analytics_01_local_project_solutions.md).
Then adapt the same source → staging → intermediate → mart pattern to a small
local dataset whose grain and ownership you can state precisely.
