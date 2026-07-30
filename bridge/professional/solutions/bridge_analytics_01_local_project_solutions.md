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
