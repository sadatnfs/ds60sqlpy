"""BRIDGE-ANALYTICS-01 reference: deterministic local dbt-style DuckDB project."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from importlib import import_module
from typing import Protocol, cast

LESSON_ID = "bridge-analytics-01"
PREREQUISITES = ("python-23", "sql-30", "bridge-05")
LEVEL = "advanced"

IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
SOURCE_NAMES = frozenset({"raw_customers", "raw_orders", "raw_order_items"})


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

    def __post_init__(self) -> None:
        _trusted_identifier(self.name)
        if not self.sql_type_prefixes:
            raise ValueError("column contract needs at least one SQL type prefix")


@dataclass(frozen=True)
class ProducerContract:
    source_name: str
    grain: str
    primary_key: tuple[str, ...]
    columns: tuple[ColumnContract, ...]

    def __post_init__(self) -> None:
        _trusted_identifier(self.source_name)
        if not self.grain.strip() or not self.primary_key or not self.columns:
            raise ValueError("producer contract needs grain, primary key, and columns")
        column_names = {column.name for column in self.columns}
        if not set(self.primary_key).issubset(column_names):
            raise ValueError("producer primary-key columns must exist in the contract")


@dataclass(frozen=True)
class ModelSpec:
    name: str
    layer: str
    grain: str
    depends_on: tuple[str, ...]
    sql: str

    def __post_init__(self) -> None:
        _trusted_identifier(self.name)
        if self.layer not in {"staging", "intermediate", "mart"}:
            raise ValueError("model layer must be staging, intermediate, or mart")
        if not self.grain.strip() or not self.depends_on or not self.sql.strip():
            raise ValueError("model needs grain, dependencies, and SQL")
        for dependency in self.depends_on:
            _trusted_identifier(dependency)


@dataclass(frozen=True)
class TableContract:
    model_name: str
    grain: str
    primary_key: tuple[str, ...]
    columns: tuple[ColumnContract, ...]

    def __post_init__(self) -> None:
        _trusted_identifier(self.model_name)
        if not self.grain.strip() or not self.primary_key or not self.columns:
            raise ValueError("table contract needs grain, primary key, and columns")
        column_names = {column.name for column in self.columns}
        if not set(self.primary_key).issubset(column_names):
            raise ValueError("primary-key columns must exist in the contract")


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

    def __post_init__(self) -> None:
        _trusted_identifier(self.name)
        _trusted_identifier(self.model_name)
        _trusted_identifier(self.time_dimension)
        if self.aggregation not in {"sum", "count", "count_distinct", "average"}:
            raise ValueError("unsupported metric aggregation")
        if not all(
            value.strip() for value in (self.label, self.expression, self.unit, self.description)
        ):
            raise ValueError("metric fields cannot be blank")


@dataclass(frozen=True)
class DataTest:
    name: str
    model_name: str
    violation_query: str

    def __post_init__(self) -> None:
        _trusted_identifier(self.name)
        _trusted_identifier(self.model_name)
        if not self.violation_query.strip():
            raise ValueError("data test query cannot be blank")


@dataclass(frozen=True)
class DataTestResult:
    name: str
    violation_count: int


@dataclass(frozen=True)
class ProjectResult:
    build_order: tuple[str, ...]
    test_results: tuple[DataTestResult, ...]
    mart_rows: tuple[tuple[object, ...], ...]


def _trusted_identifier(value: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise ValueError(f"untrusted SQL identifier: {value!r}")
    return value


RAW_CUSTOMERS = (
    (1, "Ada Lovelace", "enterprise"),
    (2, "Grace Hopper", "small_business"),
    (3, "Lin Chen", "enterprise"),
)
RAW_ORDERS = (
    (100, 1, "2026-01-01", "paid"),
    (101, 1, "2026-01-01", "shipped"),
    (102, 2, "2026-01-02", "cancelled"),
    (103, 2, "2026-01-02", "paid"),
    (104, 3, "2026-01-03", "placed"),
)
RAW_ORDER_ITEMS = (
    (100, 1, 2, "10.00"),
    (100, 2, 1, "5.50"),
    (101, 3, 1, "12.00"),
    (102, 4, 10, "1.00"),
    (103, 5, 3, "7.25"),
    (104, 6, 2, "100.00"),
)

PRODUCER_CONTRACTS = (
    ProducerContract(
        "raw_customers",
        "one row per customer_id",
        ("customer_id",),
        (
            ColumnContract("customer_id", ("BIGINT",), False, (int,)),
            ColumnContract("full_name", ("VARCHAR",), False, (str,)),
            ColumnContract("segment", ("VARCHAR",), False, (str,)),
        ),
    ),
    ProducerContract(
        "raw_orders",
        "one row per order_id",
        ("order_id",),
        (
            ColumnContract("order_id", ("BIGINT",), False, (int,)),
            ColumnContract("customer_id", ("BIGINT",), False, (int,)),
            ColumnContract("order_date", ("DATE",), False, (str,)),
            ColumnContract("status", ("VARCHAR",), False, (str,)),
        ),
    ),
    ProducerContract(
        "raw_order_items",
        "one row per order_id and line_id",
        ("order_id", "line_id"),
        (
            ColumnContract("order_id", ("BIGINT",), False, (int,)),
            ColumnContract("line_id", ("BIGINT",), False, (int,)),
            ColumnContract("quantity", ("INTEGER", "BIGINT"), False, (int,)),
            ColumnContract("unit_price", ("DECIMAL",), False, (str, Decimal)),
        ),
    ),
)

SOURCE_ROWS: dict[str, tuple[tuple[object, ...], ...]] = {
    "raw_customers": RAW_CUSTOMERS,
    "raw_orders": RAW_ORDERS,
    "raw_order_items": RAW_ORDER_ITEMS,
}

MODELS = (
    ModelSpec(
        "stg_customers",
        "staging",
        "one row per customer_id",
        ("raw_customers",),
        """
SELECT
    CAST(customer_id AS BIGINT) AS customer_id,
    trim(full_name) AS full_name,
    lower(trim(segment)) AS segment
FROM raw_customers
""".strip(),
    ),
    ModelSpec(
        "stg_orders",
        "staging",
        "one row per order_id",
        ("raw_orders",),
        """
SELECT
    CAST(order_id AS BIGINT) AS order_id,
    CAST(customer_id AS BIGINT) AS customer_id,
    CAST(order_date AS DATE) AS order_date,
    lower(trim(status)) AS status
FROM raw_orders
""".strip(),
    ),
    ModelSpec(
        "stg_order_items",
        "staging",
        "one row per order_id and line_id",
        ("raw_order_items",),
        """
SELECT
    CAST(order_id AS BIGINT) AS order_id,
    CAST(line_id AS BIGINT) AS line_id,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(unit_price AS DECIMAL(18, 2)) AS unit_price
FROM raw_order_items
""".strip(),
    ),
    ModelSpec(
        "int_order_revenue",
        "intermediate",
        "one row per completed order_id",
        ("stg_orders", "stg_order_items"),
        """
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    sum(i.quantity * i.unit_price) AS order_revenue
FROM stg_orders AS o
JOIN stg_order_items AS i USING (order_id)
WHERE o.status IN ('paid', 'shipped')
GROUP BY o.order_id, o.customer_id, o.order_date
""".strip(),
    ),
    ModelSpec(
        "mart_daily_revenue",
        "mart",
        "one row per order_date",
        ("int_order_revenue",),
        """
SELECT
    order_date,
    sum(order_revenue) AS gross_revenue,
    count(*) AS order_count,
    count(DISTINCT customer_id) AS customer_count
FROM int_order_revenue
GROUP BY order_date
""".strip(),
    ),
)

MART_CONTRACT = TableContract(
    "mart_daily_revenue",
    "one row per order_date",
    ("order_date",),
    (
        ColumnContract("order_date", ("DATE",), False),
        ColumnContract("gross_revenue", ("DECIMAL",), False),
        ColumnContract("order_count", ("BIGINT",), False),
        ColumnContract("customer_count", ("BIGINT",), False),
    ),
)

GROSS_REVENUE_METRIC = MetricDefinition(
    name="gross_revenue",
    label="Gross revenue",
    model_name="mart_daily_revenue",
    expression="gross_revenue",
    aggregation="sum",
    time_dimension="order_date",
    unit="currency units",
    description=(
        "Sum of quantity times unit price for paid or shipped orders, "
        "grouped by UTC-neutral course order_date; cancelled and placed orders are excluded."
    ),
)

DATA_TESTS = (
    DataTest(
        "stg_customers_key",
        "stg_customers",
        """
SELECT customer_id
FROM stg_customers
GROUP BY customer_id
HAVING customer_id IS NULL OR count(*) <> 1
""".strip(),
    ),
    DataTest(
        "stg_orders_key_status",
        "stg_orders",
        """
SELECT order_id
FROM stg_orders
GROUP BY order_id
HAVING order_id IS NULL
    OR count(*) <> 1
    OR bool_or(status NOT IN ('paid', 'shipped', 'cancelled', 'placed'))
""".strip(),
    ),
    DataTest(
        "orders_customer_relationship",
        "stg_orders",
        """
SELECT o.order_id
FROM stg_orders AS o
LEFT JOIN stg_customers AS c USING (customer_id)
WHERE c.customer_id IS NULL
""".strip(),
    ),
    DataTest(
        "order_item_business_rules",
        "stg_order_items",
        """
SELECT order_id, line_id
FROM stg_order_items
WHERE order_id IS NULL
   OR line_id IS NULL
   OR quantity <= 0
   OR unit_price < 0
""".strip(),
    ),
    DataTest(
        "intermediate_order_grain",
        "int_order_revenue",
        """
SELECT order_id
FROM int_order_revenue
GROUP BY order_id
HAVING order_id IS NULL OR count(*) <> 1 OR min(order_revenue) < 0
""".strip(),
    ),
    DataTest(
        "mart_daily_grain",
        "mart_daily_revenue",
        """
SELECT order_date
FROM mart_daily_revenue
GROUP BY order_date
HAVING order_date IS NULL
    OR count(*) <> 1
    OR min(gross_revenue) < 0
    OR min(order_count) < 1
    OR min(customer_count) < 1
""".strip(),
    ),
)


def validate_producer_rows(
    contract: ProducerContract,
    rows: Sequence[Sequence[object]],
) -> None:
    """Enforce source shape, nullability, types, and declared grain keys."""

    expected_width = len(contract.columns)
    for row_number, row in enumerate(rows, start=1):
        if len(row) != expected_width:
            raise ValueError(
                f"{contract.source_name} row {row_number} has {len(row)} values; "
                f"expected {expected_width}"
            )
        for column, value in zip(contract.columns, row, strict=True):
            if value is None and not column.nullable:
                raise ValueError(f"{contract.source_name}.{column.name} cannot be null")
            if (
                value is not None
                and column.python_types
                and not isinstance(value, column.python_types)
            ):
                raise TypeError(f"{contract.source_name}.{column.name} has invalid Python type")

    column_indexes = {column.name: index for index, column in enumerate(contract.columns)}
    keys = [
        tuple(row[column_indexes[column_name]] for column_name in contract.primary_key)
        for row in rows
    ]
    if len(keys) != len(set(keys)):
        raise ValueError(f"{contract.source_name} violates declared grain: {contract.grain}")


def topological_order(
    models: Sequence[ModelSpec],
    *,
    source_names: frozenset[str],
) -> tuple[ModelSpec, ...]:
    """Return a deterministic DAG order and reject missing or cyclic dependencies."""

    by_name = {model.name: model for model in models}
    if len(by_name) != len(models):
        raise ValueError("model names must be unique")
    for model in models:
        missing = set(model.depends_on) - set(by_name) - set(source_names)
        if missing:
            raise ValueError(f"{model.name} has missing dependencies: {sorted(missing)}")

    remaining = set(by_name)
    resolved = set(source_names)
    ordered: list[ModelSpec] = []
    while remaining:
        ready = sorted(
            name for name in remaining if set(by_name[name].depends_on).issubset(resolved)
        )
        if not ready:
            raise ValueError(f"model dependency cycle detected: {sorted(remaining)}")
        for name in ready:
            ordered.append(by_name[name])
            remaining.remove(name)
            resolved.add(name)
    return tuple(ordered)


def load_deterministic_sources(connection: AnalyticsConnection) -> None:
    """Validate producer fixtures, then rebuild three local raw tables."""

    for contract in PRODUCER_CONTRACTS:
        validate_producer_rows(contract, SOURCE_ROWS[contract.source_name])

    connection.execute(
        """
CREATE OR REPLACE TABLE raw_customers (
    customer_id BIGINT,
    full_name VARCHAR,
    segment VARCHAR
)
"""
    )
    connection.executemany(
        "INSERT INTO raw_customers VALUES (?, ?, ?)",
        RAW_CUSTOMERS,
    )
    connection.execute(
        """
CREATE OR REPLACE TABLE raw_orders (
    order_id BIGINT,
    customer_id BIGINT,
    order_date VARCHAR,
    status VARCHAR
)
"""
    )
    connection.executemany(
        "INSERT INTO raw_orders VALUES (?, ?, ?, ?)",
        RAW_ORDERS,
    )
    connection.execute(
        """
CREATE OR REPLACE TABLE raw_order_items (
    order_id BIGINT,
    line_id BIGINT,
    quantity INTEGER,
    unit_price VARCHAR
)
"""
    )
    connection.executemany(
        "INSERT INTO raw_order_items VALUES (?, ?, ?, ?)",
        RAW_ORDER_ITEMS,
    )


def build_models(
    connection: AnalyticsConnection,
    models: Sequence[ModelSpec],
    *,
    source_names: frozenset[str],
) -> tuple[str, ...]:
    """Rebuild trusted model specifications in deterministic DAG order."""

    ordered = topological_order(models, source_names=source_names)
    for model in ordered:
        model_name = _trusted_identifier(model.name)
        connection.execute(f"CREATE OR REPLACE TABLE {model_name} AS\n{model.sql}")
    return tuple(model.name for model in ordered)


def validate_table_contract(
    connection: AnalyticsConnection,
    contract: TableContract,
) -> None:
    """Compare actual column order and SQL types with the declared contract."""

    model_name = _trusted_identifier(contract.model_name)
    rows = connection.execute(f"DESCRIBE {model_name}").fetchall()
    actual = [(str(row[0]), str(row[1]).upper()) for row in rows]
    expected_names = [column.name for column in contract.columns]
    if [name for name, _ in actual] != expected_names:
        raise ValueError(
            f"{contract.model_name} column drift: "
            f"actual={[name for name, _ in actual]} expected={expected_names}"
        )
    for column, (_, actual_type) in zip(contract.columns, actual, strict=True):
        if not actual_type.startswith(column.sql_type_prefixes):
            raise ValueError(
                f"{contract.model_name}.{column.name} type {actual_type!r} "
                f"does not match {column.sql_type_prefixes}"
            )


def run_data_tests(
    connection: AnalyticsConnection,
    tests: Sequence[DataTest],
) -> tuple[DataTestResult, ...]:
    """Count rows returned by each violation query; zero means pass."""

    results: list[DataTestResult] = []
    for test in tests:
        violations = connection.execute(
            f"SELECT count(*) FROM ({test.violation_query}) AS violations"
        ).fetchone()
        if violations is None:
            raise ValueError(f"data test {test.name} returned no count")
        results.append(DataTestResult(test.name, int(cast(int, violations[0]))))
    return tuple(results)


def reconcile_mart(connection: AnalyticsConnection) -> None:
    """Prove mart totals and counts reconcile to intermediate order grain."""

    row = connection.execute(
        """
WITH detail AS (
    SELECT
        order_date,
        sum(order_revenue) AS gross_revenue,
        count(*) AS order_count,
        count(DISTINCT customer_id) AS customer_count
    FROM int_order_revenue
    GROUP BY order_date
),
comparison AS (
    SELECT
        coalesce(d.order_date, m.order_date) AS order_date,
        d.gross_revenue AS detail_revenue,
        m.gross_revenue AS mart_revenue,
        d.order_count AS detail_orders,
        m.order_count AS mart_orders,
        d.customer_count AS detail_customers,
        m.customer_count AS mart_customers
    FROM detail AS d
    FULL OUTER JOIN mart_daily_revenue AS m USING (order_date)
)
SELECT count(*)
FROM comparison
WHERE detail_revenue IS DISTINCT FROM mart_revenue
   OR detail_orders IS DISTINCT FROM mart_orders
   OR detail_customers IS DISTINCT FROM mart_customers
"""
    ).fetchone()
    if row is None or int(cast(int, row[0])) != 0:
        raise AssertionError("mart reconciliation failed")


def mart_snapshot(
    connection: AnalyticsConnection,
) -> tuple[tuple[object, ...], ...]:
    rows = connection.execute(
        """
SELECT order_date, gross_revenue, order_count, customer_count
FROM mart_daily_revenue
ORDER BY order_date
"""
    ).fetchall()
    return tuple(tuple(row) for row in rows)


def run_project(connection: AnalyticsConnection) -> ProjectResult:
    """Load, rebuild, contract-check, test, reconcile, and snapshot the project."""

    load_deterministic_sources(connection)
    order = build_models(connection, MODELS, source_names=SOURCE_NAMES)
    validate_table_contract(connection, MART_CONTRACT)
    test_results = run_data_tests(connection, DATA_TESTS)
    failed = [result for result in test_results if result.violation_count]
    if failed:
        names = ", ".join(result.name for result in failed)
        raise AssertionError(f"data tests failed: {names}")
    reconcile_mart(connection)
    return ProjectResult(order, test_results, mart_snapshot(connection))


def open_memory_duckdb() -> AnalyticsConnection:
    """Import the optional local engine only at the executable boundary."""

    duckdb = import_module("duckdb")
    return cast(AnalyticsConnection, duckdb.connect(database=":memory:"))


def main() -> int:
    connection = open_memory_duckdb()
    try:
        first = run_project(connection)
        second = run_project(connection)
    finally:
        connection.close()
    if first != second:
        raise AssertionError("a clean rebuild changed the deterministic project result")
    print(
        "Local analytics project: "
        f"models={len(first.build_order)} "
        f"tests={len(first.test_results)} "
        f"mart_rows={len(first.mart_rows)} "
        "idempotent=True"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
