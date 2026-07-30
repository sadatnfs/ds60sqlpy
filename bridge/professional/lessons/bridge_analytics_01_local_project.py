"""BRIDGE-ANALYTICS-01: a local dbt-style analytics project.

Prerequisites: Python Day 23, SQL Day 30, and Bridge Day 5.
This learner file defines contracts and TODOs without importing its solution.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

LESSON_ID = "bridge-analytics-01"
PREREQUISITES = ("python-23", "sql-30", "bridge-05")
LEVEL = "advanced"


class QueryResult(Protocol):
    def fetchone(self) -> Sequence[object] | None: ...

    def fetchall(self) -> Sequence[Sequence[object]]: ...


class AnalyticsConnection(Protocol):
    def execute(
        self,
        query: str,
        parameters: Sequence[object] | None = None,
    ) -> QueryResult: ...

    def executemany(
        self,
        query: str,
        parameters: Sequence[Sequence[object]],
    ) -> QueryResult: ...

    def close(self) -> None: ...


@dataclass(frozen=True)
class ColumnContract:
    name: str
    sql_type_prefixes: tuple[str, ...]
    nullable: bool
    python_types: tuple[type[object], ...] = ()


@dataclass(frozen=True)
class ProducerContract:
    source_name: str
    grain: str
    primary_key: tuple[str, ...]
    columns: tuple[ColumnContract, ...]


@dataclass(frozen=True)
class ModelSpec:
    name: str
    layer: str
    grain: str
    depends_on: tuple[str, ...]
    sql: str


@dataclass(frozen=True)
class TableContract:
    model_name: str
    grain: str
    primary_key: tuple[str, ...]
    columns: tuple[ColumnContract, ...]


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    label: str
    model_name: str
    expression: str
    aggregation: str
    time_dimension: str
    unit: str
    description: str


@dataclass(frozen=True)
class DataTest:
    name: str
    model_name: str
    violation_query: str


@dataclass(frozen=True)
class DataTestResult:
    name: str
    violation_count: int


@dataclass(frozen=True)
class ProjectResult:
    build_order: tuple[str, ...]
    test_results: tuple[DataTestResult, ...]
    mart_rows: tuple[tuple[object, ...], ...]


def validate_producer_rows(
    contract: ProducerContract,
    rows: Sequence[Sequence[object]],
) -> None:
    """Core implementation: enforce producer row shape, types, and nullability."""

    raise NotImplementedError("reject contract violations before loading DuckDB")


def topological_order(
    models: Sequence[ModelSpec],
    *,
    source_names: frozenset[str],
) -> tuple[ModelSpec, ...]:
    """Core implementation: order the DAG and reject missing dependencies or cycles."""

    raise NotImplementedError("return deterministic staging-to-mart order")


def build_models(
    connection: AnalyticsConnection,
    models: Sequence[ModelSpec],
    *,
    source_names: frozenset[str],
) -> tuple[str, ...]:
    """Core implementation: rebuild every trusted model in DAG order."""

    raise NotImplementedError("use create-or-replace for idempotent local rebuilds")


def validate_table_contract(
    connection: AnalyticsConnection,
    contract: TableContract,
) -> None:
    """Core implementation: compare actual names/types with the declared model contract."""

    raise NotImplementedError("inspect DuckDB metadata and fail on drift")


def run_data_tests(
    connection: AnalyticsConnection,
    tests: Sequence[DataTest],
) -> tuple[DataTestResult, ...]:
    """Core implementation: execute zero-row violation queries deterministically."""

    raise NotImplementedError("a passing data test returns zero violating rows")


def reconcile_mart(connection: AnalyticsConnection) -> None:
    """Core implementation: prove the mart reconciles to intermediate order grain."""

    raise NotImplementedError("compare revenue, orders, and customers by day")


# Exercises (answer-free)
# Focus: Build a local dbt-style DuckDB project with producer contracts, deterministic DAG
#    order, layered grain, table/metric contracts, violation tests, and independent
#    reconciliation.
# Assumptions: The project runs offline on deterministic local fixtures; source rows preserve
#    types/order; trusted model names are validated before DDL structure is generated.
# Failure to watch for: A model can execute successfully while still duplicating grain, drifting
#    schema, misdefining a metric, or failing reconciliation.
# Work in order: predict -> implement -> test -> debug -> extend. Keep official
# answers out of this starter and collect deterministic fake-backed evidence.
# 1. [Producer contract] Add primary-key validation and a duplicate fixture failure for every
#    producer contract.
#    Hint: Validate the complete key tuple and report only safe row position/key metadata.
# 2. [DAG] Draw dependencies and implement deterministic topological order with
#    missing-dependency and cycle detection.
#    Hint: Break ties by stable model name so valid independent branches are reproducible.
# 3. [Staging] Implement the three staging models without aggregation or `DISTINCT` and state
#    each row grain.
#    Hint: Staging should rename/cast, not hide duplicate producer rows.
# 4. [Intermediate model] Declare `int_order_revenue` grain, predict row count, then implement
#    its join and aggregate.
#    Hint: Aggregate line items to one row per order before joining other facts.
# 5. [Mart] Build `mart_daily_revenue` and document exact status exclusions and UTC/date
#    semantics.
#    Hint: Every selected non-aggregate must belong to the daily grain.
# 6. [Identifier safety] Validate trusted model names before using them in generated DDL.
#    Hint: Parameters cannot bind identifiers; constrain structure with a strict
#    grammar/allowlist.
# 7. [Schema contract] Compare `DESCRIBE` output with `MART_CONTRACT`; make separate name and
#    type drift fixtures.
#    Hint: Check position, normalized type prefix, and nullability according to declared policy.
# 8. [Data tests] Write zero-row violation queries for uniqueness, not-null, accepted status,
#    relationships, and positive money/quantity rules.
#    Hint: A test query returns violating rows; passing means count zero.
# 9. [Reconciliation] Write an independent reconciliation for mart revenue, orders, and
#    customers by day.
#    Hint: Do not reuse the mart's exact transformation path for its check.
# 10. [Semantic metric] Define one extra metric with aggregation, grain, time dimension, unit,
#    exclusions, and denominator.
#    Hint: A metric definition is a contract, not merely a SQL expression.
# 11. [Idempotency] Run the project twice in one connection and prove identical ordered
#    snapshots.
#    Hint: Rebuild semantics should replace trusted models rather than append.
# 12. [Impact analysis] Add one deterministic source row, predict every downstream change, then
#    update tests without weakening contracts.
#    Hint: Write expected deltas before executing the rebuild.
# 13. [Freshness] Add a producer freshness contract with an injected as-of time and distinguish
#    stale from missing data.
#    Hint: Time-based tests must not call the wall clock directly.
# 14. [Build strategy] Compare full rebuild and incremental processing for this local project
#    and state what evidence is missing for incrementality.
#    Hint: Idempotent full rebuild is the reference correctness baseline.
# 15. [Money correctness] Trace exact revenue from producer Decimal through DuckDB type,
#    aggregation, Python snapshot, and reconciliation.
#    Hint: Reject silent float conversion and premature rounding.
# 16. [NULL semantics] Choose behavior for missing dimension labels and prove it does not change
#    fact row count or measure totals.
#    Hint: An `unknown` label is a business rule; a filtering join is a data-loss bug unless
#    declared.
# 17. [Time semantics] Define daily boundaries for timezone-aware source instants and test an
#    order around midnight.
#    Hint: Convert the instant to the reporting zone before deriving its date.
# 18. [Late data] Model a late-arriving order for a previously built day and compare full
#    rebuild with an incremental repair.
#    Hint: Watermarks based only on event time can miss late records.
# 19. [Snapshot determinism] Require explicit ordering and stable serialization for mart
#    snapshots across platforms.
#    Hint: Database row order is undefined without final `ORDER BY`.
# 20. [Performance] Inspect a bounded `EXPLAIN` for the intermediate/mart build and identify one
#    optimization that preserves grain.
#    Hint: Optimize after contracts and reconciliation pass.
# 21. [Lineage] Produce a compact source-to-metric lineage table from `depends_on` and metric
#    definitions.
#    Hint: Lineage should be derivable from checked-in contracts rather than hand-maintained
#    prose alone.
# 22. [Transaction] Design build publication so readers do not observe half-rebuilt models after
#    a failure.
#    Hint: Check DuckDB transaction/DDL semantics rather than assuming atomicity.
# 23. [Failure policy] Make any contract, data-test, or reconciliation failure stop publication
#    while retaining inspectable results.
#    Hint: Do not continue to a green artifact after a red quality gate.
# 24. [Portable artifact] Export a deterministic local result with manifest, metric definitions,
#    test evidence, and cleanup instructions.
#    Hint: Separate generated artifacts from source and never include local paths or
#    credentials.


def main() -> int:
    print("BRIDGE-ANALYTICS-01 starter loaded; no file or hosted account was used.")
    print("Implement contracts and the DAG before running the local DuckDB project.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
