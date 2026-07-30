# BRIDGE-ANALYTICS-01 — Solution reasoning

Start with the
[learner file](../lessons/bridge_analytics_01_local_project.py). The executable
reference is
[bridge_analytics_01_local_project_solution.py](bridge_analytics_01_local_project_solution.py).

## Source and contract boundaries

The solution keeps source fixtures as immutable tuples and validates them
against producer contracts before insertion. Contracts include ordered columns,
Python types, nullability, declared grain, and primary-key fields. DuckDB values
are bound with `?` parameters.

This proves the producer boundary using deterministic synthetic data. It does
not imply that a real producer will honor freshness, schema evolution, or late
arrival expectations; those belong in a versioned external contract.

## DAG and layer reasoning

`topological_order()` resolves raw sources first, then selects dependency-ready
models in name order. Duplicate names, unknown dependencies, and cycles fail
before any model build.

Staging models only cast and normalize. `int_order_revenue` establishes
completed-order grain before the daily mart aggregates it. Keeping the
intermediate model makes order-level tests and reconciliation possible without
reverse-engineering a daily aggregate.

Model names and SQL are checked-in code. `_trusted_identifier()` validates the
small identifier interpolation boundary. This is distinct from parameterized
fixture values.

## Metric and table contracts

`GROSS_REVENUE_METRIC` names the consumer model, expression, sum aggregation,
date dimension, unit, calculation, and status exclusions. The definition is
deliberately honest about the simplified course domain.

`MART_CONTRACT` validates exact column order and compatible type prefixes from
DuckDB `DESCRIBE`. Semantic uniqueness and nullability remain queries because
`CREATE TABLE AS SELECT` does not carry every physical constraint.

## Test and reconciliation reasoning

Data tests are zero-row violation queries. Wrapping them in `SELECT count(*)`
creates stable pass/fail results while retaining a query that can be run
directly to inspect offending rows.

The reconciliation independently recomputes all three daily measures from
order grain and full-outer-joins them to the mart. `IS DISTINCT FROM` handles
missing rows and NULL differences without float tolerance because the fixture
uses exact decimals.

## Rebuild reasoning

Every raw table and model is replaced from deterministic inputs. The project
then validates the mart contract, runs all data tests, reconciles measures, and
returns an ordered snapshot. Running this sequence twice proves convergence and
that no hidden append or session-order state affects the result.

The in-memory connection ensures cleanup on close and avoids generated database
files, caches, credentials, and hosted services.

## Tradeoffs

- `CREATE OR REPLACE TABLE` is simple and deterministic but not a zero-downtime
  production deployment strategy.
- Python tuple fixtures make source behavior transparent but do not exercise
  large-file parsing or evolving producer schemas.
- Type-prefix matching tolerates DuckDB decimal precision widening but is less
  exact than a fully versioned physical schema contract.
- Full-table tests are appropriate for a tiny local project. Large warehouses
  need partition-aware tests, sampling policy, and freshness controls.
- One semantic metric dataclass documents intent but is not a complete semantic
  query engine.
- A full rebuild proves one kind of idempotency, not incremental correctness,
  late-arriving updates, snapshots, or slowly changing dimensions.
- In-memory DuckDB is portable and fast but does not prove PostgreSQL or cloud
  warehouse behavior.

Extend this project only when a new model has a declared grain, dependencies,
contract, violation queries, independent reconciliation where applicable, and
a deterministic expected change to the final snapshot.

## Exercise solutions

These walkthroughs map one-for-one to the answer-free learner artifact and
companion guide. The executable reference is `bridge/professional/solutions/bridge_analytics_01_local_project_solution.py`.

**Shared failure rule:** A model can execute successfully while still duplicating grain, drifting schema, misdefining a metric, or failing reconciliation.

### Exercise 1 — Producer contract

**Prompt:** Add primary-key validation and a duplicate fixture failure for every producer
contract.

**Approach:** Track seen key tuples after shape/type/null checks, reject null or repeated keys,
and add deterministic fixtures that differ only by the duplicate row.

**Why:** Validate the complete key tuple and report only safe row position/key metadata.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 2 — DAG

**Prompt:** Draw dependencies and implement deterministic topological order with
missing-dependency and cycle detection.

**Approach:** Validate unique names/dependencies, use Kahn's algorithm or DFS with explicit
states, choose lexicographic ready nodes, and raise with the bounded cycle/missing names.

**Why:** Break ties by stable model name so valid independent branches are reproducible.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 3 — Staging

**Prompt:** Implement the three staging models without aggregation or `DISTINCT` and state each
row grain.

**Approach:** Select source columns explicitly with trusted casts/aliases and one output row per
source row. Let producer tests expose duplicates rather than masking them.

**Why:** Staging should rename/cast, not hide duplicate producer rows.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 4 — Intermediate model

**Prompt:** Declare `int_order_revenue` grain, predict row count, then implement its join and
aggregate.

**Approach:** Use order ID as primary grain, sum exact net line amounts from item rows, join
only dimensions/many-to-one sources, and reconcile predicted order count with source orders.

**Why:** Aggregate line items to one row per order before joining other facts.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 5 — Mart

**Prompt:** Build `mart_daily_revenue` and document exact status exclusions and UTC/date
semantics.

**Approach:** Group eligible order-grain rows by declared day, compute exact
revenue/order/customer measures, and encode excluded statuses in both SQL and metric
documentation.

**Why:** Every selected non-aggregate must belong to the daily grain.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 6 — Identifier safety

**Prompt:** Validate trusted model names before using them in generated DDL.

**Approach:** Require known `ModelSpec` names matching a conservative identifier regex, reject
schema separators/quotes, and generate DDL only from validated internal specs.

**Why:** Parameters cannot bind identifiers; constrain structure with a strict
grammar/allowlist.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 7 — Schema contract

**Prompt:** Compare `DESCRIBE` output with `MART_CONTRACT`; make separate name and type drift
fixtures.

**Approach:** Build an actual-column map/order, compare exact names and accepted type prefixes,
and raise targeted errors for missing/extra/type/nullability drift.

**Why:** Check position, normalized type prefix, and nullability according to declared policy.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 8 — Data tests

**Prompt:** Write zero-row violation queries for uniqueness, not-null, accepted status,
relationships, and positive money/quantity rules.

**Approach:** Keep each invariant in a named query, count its rows through `run_data_tests`, and
preserve individual results rather than one combined opaque flag.

**Why:** A test query returns violating rows; passing means count zero.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 9 — Reconciliation

**Prompt:** Write an independent reconciliation for mart revenue, orders, and customers by day.

**Approach:** Aggregate from the trusted intermediate/source path independently, full-join by
day, and fail on missing sides or exact measure differences.

**Why:** Do not reuse the mart's exact transformation path for its check.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 10 — Semantic metric

**Prompt:** Define one extra metric with aggregation, grain, time dimension, unit, exclusions,
and denominator.

**Approach:** Create a `MetricDefinition` such as revenue per purchasing customer with explicit
numerator/denominator, daily grain, currency unit, eligible statuses, and zero-denominator
behavior.

**Why:** A metric definition is a contract, not merely a SQL expression.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 11 — Idempotency

**Prompt:** Run the project twice in one connection and prove identical ordered snapshots.

**Approach:** Use create-or-replace in topological order, run contracts/tests/reconciliation
both times, and compare deterministic `ORDER BY` snapshots plus unchanged row counts/sums.

**Why:** Rebuild semantics should replace trusted models rather than append.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 12 — Impact analysis

**Prompt:** Add one deterministic source row, predict every downstream change, then update tests
without weakening contracts.

**Approach:** Choose a valid linked row, calculate affected staging/intermediate/day measures,
rebuild, and assert only those rows/measures change while all contracts remain identical.

**Why:** Write expected deltas before executing the rebuild.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 13 — Freshness

**Prompt:** Add a producer freshness contract with an injected as-of time and distinguish stale
from missing data.

**Approach:** Declare source timestamp, maximum age, and timezone; compare maximum observed
timestamp with injected UTC as-of; report empty and stale sources as separate failures.

**Why:** Time-based tests must not call the wall clock directly.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 14 — Build strategy

**Prompt:** Compare full rebuild and incremental processing for this local project and state
what evidence is missing for incrementality.

**Approach:** Keep full create-or-replace for bounded fixtures; an incremental design needs
stable unique keys, watermark/late-data policy, merge semantics, and reconciliation against
periodic full rebuilds.

**Why:** Idempotent full rebuild is the reference correctness baseline.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 15 — Money correctness

**Prompt:** Trace exact revenue from producer Decimal through DuckDB type, aggregation, Python
snapshot, and reconciliation.

**Approach:** Declare DECIMAL types/scales, keep exact arithmetic through models/tests, convert
to Decimal at the boundary, and round only labeled presentation values.

**Why:** Reject silent float conversion and premature rounding.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 16 — NULL semantics

**Prompt:** Choose behavior for missing dimension labels and prove it does not change fact row
count or measure totals.

**Approach:** Use a left join and explicit `COALESCE` to a documented unknown member, then
reconcile fact counts/revenue before and after enrichment.

**Why:** An `unknown` label is a business rule; a filtering join is a data-loss bug unless
declared.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 17 — Time semantics

**Prompt:** Define daily boundaries for timezone-aware source instants and test an order around
midnight.

**Approach:** Declare UTC or a named reporting zone, apply conversion once in
staging/intermediate logic, and fixture instants on both sides of midnight to verify bucket
assignment.

**Why:** Convert the instant to the reporting zone before deriving its date.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 18 — Late data

**Prompt:** Model a late-arriving order for a previously built day and compare full rebuild with
an incremental repair.

**Approach:** The full rebuild updates the old day automatically; incrementality needs
ingestion-time lookback or affected-partition reprocessing plus reconciliation.

**Why:** Watermarks based only on event time can miss late records.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 19 — Snapshot determinism

**Prompt:** Require explicit ordering and stable serialization for mart snapshots across
platforms.

**Approach:** Select declared columns in contract order, order by the primary/time key,
normalize exact scalar serialization, and compare tuples rather than display-formatted text.

**Why:** Database row order is undefined without final `ORDER BY`.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 20 — Performance

**Prompt:** Inspect a bounded `EXPLAIN` for the intermediate/mart build and identify one
optimization that preserves grain.

**Approach:** Look for repeated scans, large joins, and unnecessary sorts; reduce projected
columns or pre-aggregate at declared grain, then re-run all tests/reconciliation.

**Why:** Optimize after contracts and reconciliation pass.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 21 — Lineage

**Prompt:** Produce a compact source-to-metric lineage table from `depends_on` and metric
definitions.

**Approach:** Traverse the DAG from metric model to producers, emit ordered model/layer/grain
edges and metric exclusions, and test the expected path.

**Why:** Lineage should be derivable from checked-in contracts rather than hand-maintained prose
alone.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 22 — Transaction

**Prompt:** Design build publication so readers do not observe half-rebuilt models after a
failure.

**Approach:** Run the model sequence in an explicit transaction when supported, validate
contracts/tests before commit, roll back on failure, or build versioned temporary models then
swap after validation.

**Why:** Check DuckDB transaction/DDL semantics rather than assuming atomicity.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 23 — Failure policy

**Prompt:** Make any contract, data-test, or reconciliation failure stop publication while
retaining inspectable results.

**Approach:** Collect named results, raise before commit/export when one fails, and return
bounded failure evidence without mutating the last known-good artifact.

**Why:** Do not continue to a green artifact after a red quality gate.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.

### Exercise 24 — Portable artifact

**Prompt:** Export a deterministic local result with manifest, metric definitions, test
evidence, and cleanup instructions.

**Approach:** Write under ignored `artifacts/`, include build timestamp from an injected clock,
source fixture/version, ordered schema/data, quality results and definitions, then document safe
regeneration/removal.

**Why:** Separate generated artifacts from source and never include local paths or credentials.

**Evidence:** Assert deterministic outputs plus the exact calls that did
and did not cross the boundary. Keep live/network evidence opt-in,
credential-free, bounded, and separately labeled.
