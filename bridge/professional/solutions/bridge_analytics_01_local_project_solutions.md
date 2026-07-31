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


<!-- BEGIN BRIDGE ENRICHMENT: SOLUTION EXAMPLE -->
## Small executable check

The checked-in model graph has a deterministic dependency order:

```python
from bridge.professional.solutions.bridge_analytics_01_local_project_solution import (
    MODELS,
    SOURCE_NAMES,
    topological_order,
)

ordered_names = tuple(model.name for model in topological_order(MODELS, source_names=SOURCE_NAMES))
assert ordered_names[-1] == "mart_daily_revenue"
assert ordered_names.index("int_order_revenue") < ordered_names.index("mart_daily_revenue")
```
<!-- END BRIDGE ENRICHMENT: SOLUTION EXAMPLE -->

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

**Verification evidence:** For each producer contract, load one unique fixture successfully, duplicate its primary-key tuple, and assert validation fails with the source/grain named before DuckDB insertion.

### Exercise 2 — DAG

**Prompt:** Draw dependencies and implement deterministic topological order with
missing-dependency and cycle detection.

**Approach:** Validate unique names/dependencies, use Kahn's algorithm or DFS with explicit
states, choose lexicographic ready nodes, and raise with the bounded cycle/missing names.

**Why:** Break ties by stable model name so valid independent branches are reproducible.

**Verification evidence:** Assert raw sources precede dependent staging/intermediate/mart models with stable name ordering; an unknown dependency and a two-model cycle each raise `ValueError` listing unresolved names.

### Exercise 3 — Staging

**Prompt:** Implement the three staging models without aggregation or `DISTINCT` and state each
row grain.

**Approach:** Select source columns explicitly with trusted casts/aliases and one output row per
source row. Let producer tests expose duplicates rather than masking them.

**Why:** Staging should rename/cast, not hide duplicate producer rows.

**Verification evidence:** Compare staging row counts with their raw sources, assert no `DISTINCT`/aggregation, and record grains `customer_id`, `order_id`, and `(order_id, line_number)` with typed/normalized columns.

### Exercise 4 — Intermediate model

**Prompt:** Declare `int_order_revenue` grain, predict row count, then implement its join and
aggregate.

**Approach:** Use order ID as primary grain, sum exact net line amounts from item rows, join
only dimensions/many-to-one sources, and reconcile predicted order count with source orders.

**Why:** Aggregate line items to one row per order before joining other facts.

**Verification evidence:** Predict and assert one row per order in `int_order_revenue`, with exact summed item revenue and retained customer/status/date fields; row count equals raw orders, including orders without matching items per policy.

### Exercise 5 — Mart

**Prompt:** Build `mart_daily_revenue` and document exact status exclusions and UTC/date
semantics.

**Approach:** Group eligible order-grain rows by declared day, compute exact
revenue/order/customer measures, and encode excluded statuses in both SQL and metric
documentation.

**Why:** Every selected non-aggregate must belong to the daily grain.

**Verification evidence:** Assert one row per UTC order date, only the documented completed/paid statuses contribute, revenue/order/customer measures match fixtures, and output is ordered by date.

### Exercise 6 — Identifier safety

**Prompt:** Validate trusted model names before using them in generated DDL.

**Approach:** Require known `ModelSpec` names matching a conservative identifier regex, reject
schema separators/quotes, and generate DDL only from validated internal specs.

**Why:** Parameters cannot bind identifiers; constrain structure with a strict
grammar/allowlist.

**Verification evidence:** Pass every checked-in model name and injection-shaped/uppercase/punctuated names; assert only names matching the trusted identifier policy reach generated DDL.

### Exercise 7 — Schema contract

**Prompt:** Compare `DESCRIBE` output with `MART_CONTRACT`; make separate name and type drift
fixtures.

**Approach:** Build an actual-column map/order, compare exact names and accepted type prefixes,
and raise targeted errors for missing/extra/type/nullability drift.

**Why:** Check position, normalized type prefix, and nullability according to declared policy.

**Verification evidence:** Compare exact `DESCRIBE` column order/type compatibility with `MART_CONTRACT`; separate fixtures must report name drift and type drift distinctly before publication.

### Exercise 8 — Data tests

**Prompt:** Write zero-row violation queries for uniqueness, not-null, accepted status,
relationships, and positive money/quantity rules.

**Approach:** Keep each invariant in a named query, count its rows through `run_data_tests`, and
preserve individual results rather than one combined opaque flag.

**Why:** A test query returns violating rows; passing means count zero.

**Verification evidence:** Execute each violation query against valid fixtures and assert zero rows; inject one uniqueness, null, status, relationship, money, and quantity violation and assert its named test returns evidence rows.

### Exercise 9 — Reconciliation

**Prompt:** Write an independent reconciliation for mart revenue, orders, and customers by day.

**Approach:** Aggregate from the trusted intermediate/source path independently, full-join by
day, and fail on missing sides or exact measure differences.

**Why:** Do not reuse the mart's exact transformation path for its check.

**Verification evidence:** Independently recompute daily revenue/order/customer measures from order grain and full-outer compare; assert zero mismatches, then perturb each mart measure and observe a dated mismatch row.

### Exercise 10 — Semantic metric

**Prompt:** Define one extra metric with aggregation, grain, time dimension, unit, exclusions,
and denominator.

**Approach:** Create a `MetricDefinition` such as revenue per purchasing customer with explicit
numerator/denominator, daily grain, currency unit, eligible statuses, and zero-denominator
behavior.

**Why:** A metric definition is a contract, not merely a SQL expression.

**Verification evidence:** Define an additional metric with model, expression, aggregation, grain, time dimension, unit, exclusions, and denominator; calculate one fixture date and compare the exact value.

### Exercise 11 — Idempotency

**Prompt:** Run the project twice in one connection and prove identical ordered snapshots.

**Approach:** Use create-or-replace in topological order, run contracts/tests/reconciliation
both times, and compare deterministic `ORDER BY` snapshots plus unchanged row counts/sums.

**Why:** Rebuild semantics should replace trusted models rather than append.

**Verification evidence:** Run the project twice in one connection; assert identical ordered snapshots, row counts, test results, and reconciliation, with no duplicate append state.

### Exercise 12 — Impact analysis

**Prompt:** Add one deterministic source row, predict every downstream change, then update tests
without weakening contracts.

**Approach:** Choose a valid linked row, calculate affected staging/intermediate/day measures,
rebuild, and assert only those rows/measures change while all contracts remain identical.

**Why:** Write expected deltas before executing the rebuild.

**Verification evidence:** Add one source row and write predicted staging/intermediate/mart row and measure deltas first; assert the actual snapshot matches every predicted change and existing contracts remain unchanged.

### Exercise 13 — Freshness

**Prompt:** Add a producer freshness contract with an injected as-of time and distinguish stale
from missing data.

**Approach:** Declare source timestamp, maximum age, and timezone; compare maximum observed
timestamp with injected UTC as-of; report empty and stale sources as separate failures.

**Why:** Time-based tests must not call the wall clock directly.

**Verification evidence:** With an injected as-of instant, assert a present old source is reported stale, an absent source missing, and a recent source current using the declared threshold.

### Exercise 14 — Build strategy

**Prompt:** Compare full rebuild and incremental processing for this local project and state
what evidence is missing for incrementality.

**Approach:** Keep full create-or-replace for bounded fixtures; an incremental design needs
stable unique keys, watermark/late-data policy, merge semantics, and reconciliation against
periodic full rebuilds.

**Why:** Idempotent full rebuild is the reference correctness baseline.

**Verification evidence:** Provide a comparison of full rebuild versus incremental state, keys, late updates, delete handling, and atomic publication; mark incrementality unproved until change-capture and replay tests exist.

### Exercise 15 — Money correctness

**Prompt:** Trace exact revenue from producer Decimal through DuckDB type, aggregation, Python
snapshot, and reconciliation.

**Approach:** Declare DECIMAL types/scales, keep exact arithmetic through models/tests, convert
to Decimal at the boundary, and round only labeled presentation values.

**Why:** Reject silent float conversion and premature rounding.

**Verification evidence:** Trace one exact Decimal from source tuple through DuckDB `DECIMAL`, order aggregation, mart aggregation, Python snapshot, and reconciliation; assert equality at every boundary without float conversion.

### Exercise 16 — NULL semantics

**Prompt:** Choose behavior for missing dimension labels and prove it does not change fact row
count or measure totals.

**Approach:** Use a left join and explicit `COALESCE` to a documented unknown member, then
reconcile fact counts/revenue before and after enrichment.

**Why:** An `unknown` label is a business rule; a filtering join is a data-loss bug unless
declared.

**Verification evidence:** Inject a missing dimension label; assert the declared replacement/NULL policy, unchanged fact row count, and unchanged revenue/order totals.

### Exercise 17 — Time semantics

**Prompt:** Define daily boundaries for timezone-aware source instants and test an order around
midnight.

**Approach:** Declare UTC or a named reporting zone, apply conversion once in
staging/intermediate logic, and fixture instants on both sides of midnight to verify bucket
assignment.

**Why:** Convert the instant to the reporting zone before deriving its date.

**Verification evidence:** Place timezone-aware orders immediately before and after the declared UTC midnight; assert they land on the two expected dates and no local-machine timezone changes the snapshot.

### Exercise 18 — Late data

**Prompt:** Model a late-arriving order for a previously built day and compare full rebuild with
an incremental repair.

**Approach:** The full rebuild updates the old day automatically; incrementality needs
ingestion-time lookback or affected-partition reprocessing plus reconciliation.

**Why:** Watermarks based only on event time can miss late records.

**Verification evidence:** Add a late order to an already-built date; assert full rebuild corrects that date and the proposed incremental repair reprocesses the same affected partition to an identical result.

### Exercise 19 — Snapshot determinism

**Prompt:** Require explicit ordering and stable serialization for mart snapshots across
platforms.

**Approach:** Select declared columns in contract order, order by the primary/time key,
normalize exact scalar serialization, and compare tuples rather than display-formatted text.

**Why:** Database row order is undefined without final `ORDER BY`.

**Verification evidence:** Assert mart queries include a complete unique order, serialize dates/Decimals with the documented stable format, and produce byte-identical snapshots across repeated runs.

### Exercise 20 — Performance

**Prompt:** Inspect a bounded `EXPLAIN` for the intermediate/mart build and identify one
optimization that preserves grain.

**Approach:** Look for repeated scans, large joins, and unnecessary sorts; reduce projected
columns or pre-aggregate at declared grain, then re-run all tests/reconciliation.

**Why:** Optimize after contracts and reconciliation pass.

**Verification evidence:** Capture bounded `EXPLAIN` output for intermediate and mart builds, identify scan/join/aggregate operators, and propose one optimization whose post-change grain, counts, and reconciliation remain identical.

### Exercise 21 — Lineage

**Prompt:** Produce a compact source-to-metric lineage table from `depends_on` and metric
definitions.

**Approach:** Traverse the DAG from metric model to producers, emit ordered model/layer/grain
edges and metric exclusions, and test the expected path.

**Why:** Lineage should be derivable from checked-in contracts rather than hand-maintained prose
alone.

**Verification evidence:** Generate lineage rows from every raw source through models to each metric; assert all declared dependencies appear, no orphan/cycle exists, and `gross_revenue` terminates at `mart_daily_revenue`.

### Exercise 22 — Transaction

**Prompt:** Design build publication so readers do not observe half-rebuilt models after a
failure.

**Approach:** Run the model sequence in an explicit transaction when supported, validate
contracts/tests before commit, roll back on failure, or build versioned temporary models then
swap after validation.

**Why:** Check DuckDB transaction/DDL semantics rather than assuming atomicity.

**Verification evidence:** Inject failure before publication and assert readers retain the prior complete mart; the design must stage or transact replacement so no partial model set becomes visible.

### Exercise 23 — Failure policy

**Prompt:** Make any contract, data-test, or reconciliation failure stop publication while
retaining inspectable results.

**Approach:** Collect named results, raise before commit/export when one fails, and return
bounded failure evidence without mutating the last known-good artifact.

**Why:** Do not continue to a green artifact after a red quality gate.

**Verification evidence:** Force producer-contract, table-contract, data-test, and reconciliation failures separately; assert each blocks publication while retaining the named failing query/result for diagnosis.

### Exercise 24 — Portable artifact

**Prompt:** Export a deterministic local result with manifest, metric definitions, test
evidence, and cleanup instructions.

**Approach:** Write under ignored `artifacts/`, include build timestamp from an injected clock,
source fixture/version, ordered schema/data, quality results and definitions, then document safe
regeneration/removal.

**Why:** Separate generated artifacts from source and never include local paths or credentials.

**Verification evidence:** Export an ordered result plus manifest containing lesson/version, schema/grain, metric definitions, source fixture hashes, test/reconciliation results, creation command, and cleanup; repeat and compare deterministically.
