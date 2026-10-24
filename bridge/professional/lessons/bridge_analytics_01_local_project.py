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
#    Verify: For each producer contract, load one unique fixture successfully, duplicate its
#    primary-key tuple, and assert validation fails with the source/grain named before DuckDB
#    insertion.
# 2. [DAG] Draw dependencies and implement deterministic topological order with
#    missing-dependency and cycle detection.
#    Hint: Break ties by stable model name so valid independent branches are reproducible.
#    Verify: Assert raw sources precede dependent staging/intermediate/mart models with stable
#    name ordering; an unknown dependency and a two-model cycle each raise `ValueError` listing
#    unresolved names.
# 3. [Staging] Implement the three staging models without aggregation or `DISTINCT` and state
#    each row grain.
#    Hint: Staging should rename/cast, not hide duplicate producer rows.
#    Verify: Compare staging row counts with their raw sources, assert no
#    `DISTINCT`/aggregation, and record grains `customer_id`, `order_id`, and `(order_id,
#    line_number)` with typed/normalized columns.
# 4. [Intermediate model] Declare `int_order_revenue` grain, predict row count, then implement
#    its join and aggregate.
#    Hint: Aggregate line items to one row per order before joining other facts.
#    Verify: Predict and assert one row per order in `int_order_revenue`, with exact summed item
#    revenue and retained customer/status/date fields; row count equals raw orders, including
#    orders without matching items per policy.
# 5. [Mart] Build `mart_daily_revenue` and document exact status exclusions and UTC/date
#    semantics.
#    Hint: Every selected non-aggregate must belong to the daily grain.
#    Verify: Assert one row per UTC order date, only the documented completed/paid statuses
#    contribute, revenue/order/customer measures match fixtures, and output is ordered by date.
# 6. [Identifier safety] Validate trusted model names before using them in generated DDL.
#    Hint: Parameters cannot bind identifiers; constrain structure with a strict
#    grammar/allowlist.
#    Verify: Pass every checked-in model name and injection-shaped/uppercase/punctuated names;
#    assert only names matching the trusted identifier policy reach generated DDL.
# 7. [Schema contract] Compare `DESCRIBE` output with `MART_CONTRACT`; make separate name and
#    type drift fixtures.
#    Hint: Check position, normalized type prefix, and nullability according to declared policy.
#    Verify: Compare exact `DESCRIBE` column order/type compatibility with `MART_CONTRACT`;
#    separate fixtures must report name drift and type drift distinctly before publication.
# 8. [Data tests] Write zero-row violation queries for uniqueness, not-null, accepted status,
#    relationships, and positive money/quantity rules.
#    Hint: A test query returns violating rows; passing means count zero.
#    Verify: Execute each violation query against valid fixtures and assert zero rows; inject
#    one uniqueness, null, status, relationship, money, and quantity violation and assert its
#    named test returns evidence rows.
# 9. [Reconciliation] Write an independent reconciliation for mart revenue, orders, and
#    customers by day.
#    Hint: Do not reuse the mart's exact transformation path for its check.
#    Verify: Independently recompute daily revenue/order/customer measures from order grain and
#    full-outer compare; assert zero mismatches, then perturb each mart measure and observe a
#    dated mismatch row.
# 10. [Semantic metric] Define one extra metric with aggregation, grain, time dimension, unit,
#    exclusions, and denominator.
#    Hint: A metric definition is a contract, not merely a SQL expression.
#    Verify: Define an additional metric with model, expression, aggregation, grain, time
#    dimension, unit, exclusions, and denominator; calculate one fixture date and compare the
#    exact value.
# 11. [Idempotency] Run the project twice in one connection and prove identical ordered
#    snapshots.
#    Hint: Rebuild semantics should replace trusted models rather than append.
#    Verify: Run the project twice in one connection; assert identical ordered snapshots, row
#    counts, test results, and reconciliation, with no duplicate append state.
# 12. [Impact analysis] Add one deterministic source row, predict every downstream change, then
#    update tests without weakening contracts.
#    Hint: Write expected deltas before executing the rebuild.
#    Verify: Add one source row and write predicted staging/intermediate/mart row and measure
#    deltas first; assert the actual snapshot matches every predicted change and existing
#    contracts remain unchanged.
# 13. [Freshness] Add a producer freshness contract with an injected as-of time and distinguish
#    stale from missing data.
#    Hint: Time-based tests must not call the wall clock directly.
#    Verify: With an injected as-of instant, assert a present old source is reported stale, an
#    absent source missing, and a recent source current using the declared threshold.
# 14. [Build strategy] Compare full rebuild and incremental processing for this local project
#    and state what evidence is missing for incrementality.
#    Hint: Idempotent full rebuild is the reference correctness baseline.
#    Verify: Provide a comparison of full rebuild versus incremental state, keys, late updates,
#    delete handling, and atomic publication; mark incrementality unproved until change-capture
#    and replay tests exist.
# 15. [Money correctness] Trace exact revenue from producer Decimal through DuckDB type,
#    aggregation, Python snapshot, and reconciliation.
#    Hint: Reject silent float conversion and premature rounding.
#    Verify: Trace one exact Decimal from source tuple through DuckDB `DECIMAL`, order
#    aggregation, mart aggregation, Python snapshot, and reconciliation; assert equality at
#    every boundary without float conversion.
# 16. [NULL semantics] Choose behavior for missing dimension labels and prove it does not change
#    fact row count or measure totals.
#    Hint: An `unknown` label is a business rule; a filtering join is a data-loss bug unless
#    declared.
#    Verify: Inject a missing dimension label; assert the declared replacement/NULL policy,
#    unchanged fact row count, and unchanged revenue/order totals.
# 17. [Time semantics] Define daily boundaries for timezone-aware source instants and test an
#    order around midnight.
#    Hint: Convert the instant to the reporting zone before deriving its date.
#    Verify: Place timezone-aware orders immediately before and after the declared UTC midnight;
#    assert they land on the two expected dates and no local-machine timezone changes the
#    snapshot.
# 18. [Late data] Model a late-arriving order for a previously built day and compare full
#    rebuild with an incremental repair.
#    Hint: Watermarks based only on event time can miss late records.
#    Verify: Add a late order to an already-built date; assert full rebuild corrects that date
#    and the proposed incremental repair reprocesses the same affected partition to an identical
#    result.
# 19. [Snapshot determinism] Require explicit ordering and stable serialization for mart
#    snapshots across platforms.
#    Hint: Database row order is undefined without final `ORDER BY`.
#    Verify: Assert mart queries include a complete unique order, serialize dates/Decimals with
#    the documented stable format, and produce byte-identical snapshots across repeated runs.
# 20. [Performance] Inspect a bounded `EXPLAIN` for the intermediate/mart build and identify one
#    optimization that preserves grain.
#    Hint: Optimize after contracts and reconciliation pass.
#    Verify: Capture bounded `EXPLAIN` output for intermediate and mart builds, identify
#    scan/join/aggregate operators, and propose one optimization whose post-change grain,
#    counts, and reconciliation remain identical.
# 21. [Lineage] Produce a compact source-to-metric lineage table from `depends_on` and metric
#    definitions.
#    Hint: Lineage should be derivable from checked-in contracts rather than hand-maintained
#    prose alone.
#    Verify: Generate lineage rows from every raw source through models to each metric; assert
#    all declared dependencies appear, no orphan/cycle exists, and `gross_revenue` terminates at
#    `mart_daily_revenue`.
# 22. [Transaction] Design build publication so readers do not observe half-rebuilt models after
#    a failure.
#    Hint: Check DuckDB transaction/DDL semantics rather than assuming atomicity.
#    Verify: Inject failure before publication and assert readers retain the prior complete
#    mart; the design must stage or transact replacement so no partial model set becomes
#    visible.
# 23. [Failure policy] Make any contract, data-test, or reconciliation failure stop publication
#    while retaining inspectable results.
#    Hint: Do not continue to a green artifact after a red quality gate.
#    Verify: Force producer-contract, table-contract, data-test, and reconciliation failures
#    separately; assert each blocks publication while retaining the named failing query/result
#    for diagnosis.
# 24. [Portable artifact] Export a deterministic local result with manifest, metric definitions,
#    test evidence, and cleanup instructions.
#    Hint: Separate generated artifacts from source and never include local paths or
#    credentials.
#    Verify: Export an ordered result plus manifest containing lesson/version, schema/grain,
#    metric definitions, source fixture hashes, test/reconciliation results, creation command,
#    and cleanup; repeat and compare deterministically.


def main() -> int:
    print("BRIDGE-ANALYTICS-01 starter loaded; no file or hosted account was used.")
    print("Implement contracts and the DAG before running the local DuckDB project.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
