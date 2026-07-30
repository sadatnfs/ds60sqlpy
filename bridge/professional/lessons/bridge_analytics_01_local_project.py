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
    """Exercise 1: enforce producer row shape, types, and nullability."""

    raise NotImplementedError("reject contract violations before loading DuckDB")


def topological_order(
    models: Sequence[ModelSpec],
    *,
    source_names: frozenset[str],
) -> tuple[ModelSpec, ...]:
    """Exercise 2: order the DAG and reject missing dependencies or cycles."""

    raise NotImplementedError("return deterministic staging-to-mart order")


def build_models(
    connection: AnalyticsConnection,
    models: Sequence[ModelSpec],
    *,
    source_names: frozenset[str],
) -> tuple[str, ...]:
    """Exercise 3: rebuild every trusted model in DAG order."""

    raise NotImplementedError("use create-or-replace for idempotent local rebuilds")


def validate_table_contract(
    connection: AnalyticsConnection,
    contract: TableContract,
) -> None:
    """Exercise 4: compare actual names/types with the declared model contract."""

    raise NotImplementedError("inspect DuckDB metadata and fail on drift")


def run_data_tests(
    connection: AnalyticsConnection,
    tests: Sequence[DataTest],
) -> tuple[DataTestResult, ...]:
    """Exercise 5: execute zero-row violation queries deterministically."""

    raise NotImplementedError("a passing data test returns zero violating rows")


def reconcile_mart(connection: AnalyticsConnection) -> None:
    """Exercise 6: prove the mart reconciles to intermediate order grain."""

    raise NotImplementedError("compare revenue, orders, and customers by day")


def main() -> int:
    print("BRIDGE-ANALYTICS-01 starter loaded; no file or hosted account was used.")
    print("Implement contracts and the DAG before running the local DuckDB project.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
