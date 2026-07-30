"""Reference implementation for python-data-01.

The default path parses the tracked CSV with the standard library. pandas is an
optional convenience fallback; PyArrow and DuckDB unlock the columnar lab.
Nothing downloads data or contacts a server.
"""

from __future__ import annotations

import csv
import importlib.util
import re
import tempfile
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Literal

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "data" / "sales.csv"
PARTITION_VALUE = re.compile(r"^[a-z0-9-]+$")


@dataclass(frozen=True)
class Sale:
    """Typed interpretation of one CSV record."""

    order_id: int
    event_date: date
    region: str
    category: str
    units: int
    unit_price: Decimal
    note: str | None

    @property
    def revenue(self) -> Decimal:
        return self.units * self.unit_price


@dataclass(frozen=True)
class SalesSummary:
    """Portable aggregate result with the engine made visible."""

    engine: Literal["stdlib-csv", "pandas-csv"]
    row_count: int
    total_revenue: Decimal
    null_note_count: int
    regions: tuple[str, ...]


@dataclass(frozen=True)
class SchemaRoundTrip:
    """Evidence preserved through a PyArrow Parquet round trip."""

    path: Path
    schema_before: str
    schema_after: str
    row_count: int
    null_note_count: int


@dataclass(frozen=True)
class QueryObservation:
    """DuckDB results plus visible plan evidence."""

    rows: tuple[tuple[str, Decimal], ...]
    plan: str
    filter_visible: bool
    projections_visible: bool


def read_csv_rows(path: Path = FIXTURE) -> list[dict[str, str]]:
    """Read raw CSV values; all fields remain text at this boundary."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_nullable_text(value: str) -> str | None:
    """Interpret an empty or whitespace-only CSV field as NULL."""

    stripped = value.strip()
    return stripped if stripped else None


def parse_sale(row: dict[str, str]) -> Sale:
    """Apply one explicit schema to a raw CSV record."""

    required = {
        "order_id",
        "event_date",
        "region",
        "category",
        "units",
        "unit_price",
        "note",
    }
    missing = required.difference(row)
    if missing:
        raise ValueError(f"CSV row is missing columns: {sorted(missing)}")
    units = int(row["units"])
    price = Decimal(row["unit_price"])
    if units < 0:
        raise ValueError("units must be non-negative")
    if price < 0:
        raise ValueError("unit_price must be non-negative")
    return Sale(
        order_id=int(row["order_id"]),
        event_date=date.fromisoformat(row["event_date"]),
        region=row["region"].strip(),
        category=row["category"].strip(),
        units=units,
        unit_price=price,
        note=parse_nullable_text(row["note"]),
    )


def load_sales(path: Path = FIXTURE) -> list[Sale]:
    """Load typed records through the portable CSV path."""

    return [parse_sale(row) for row in read_csv_rows(path)]


def summarize_stdlib(path: Path = FIXTURE) -> SalesSummary:
    """Summarize CSV without a third-party dependency."""

    sales = load_sales(path)
    return SalesSummary(
        engine="stdlib-csv",
        row_count=len(sales),
        total_revenue=sum((sale.revenue for sale in sales), start=Decimal("0")),
        null_note_count=sum(sale.note is None for sale in sales),
        regions=tuple(sorted({sale.region for sale in sales})),
    )


def summarize_with_csv_fallback(path: Path = FIXTURE) -> SalesSummary:
    """Use pandas when present, otherwise retain a stdlib CSV path."""

    if importlib.util.find_spec("pandas") is None:
        return summarize_stdlib(path)

    import pandas as pd  # type: ignore[import-untyped]

    frame = pd.read_csv(
        path,
        dtype={
            "order_id": "int64",
            "region": "string",
            "category": "string",
            "units": "int64",
            "unit_price": "string",
            "note": "string",
        },
        parse_dates=["event_date"],
    )
    prices = [Decimal(value) for value in frame["unit_price"].tolist()]
    units = [int(value) for value in frame["units"].tolist()]
    total = sum(
        (price * unit for price, unit in zip(prices, units, strict=True)),
        start=Decimal("0"),
    )
    return SalesSummary(
        engine="pandas-csv",
        row_count=len(frame),
        total_revenue=total,
        null_note_count=int(frame["note"].isna().sum()),
        regions=tuple(sorted(str(value) for value in frame["region"].unique())),
    )


def partition_directory(region: str) -> str:
    """Return a validated Hive-style partition segment."""

    if not PARTITION_VALUE.fullmatch(region):
        raise ValueError("region must use lower-case letters, digits, or hyphens")
    return f"region={region}"


def write_partitioned_csv(
    sales: Iterable[Sale],
    root: Path,
) -> tuple[Path, ...]:
    """Write deterministic region partitions using portable CSV files."""

    by_region: dict[str, list[Sale]] = defaultdict(list)
    for sale in sales:
        by_region[sale.region].append(sale)

    paths: list[Path] = []
    fieldnames = [
        "order_id",
        "event_date",
        "category",
        "units",
        "unit_price",
        "note",
    ]
    for region in sorted(by_region):
        directory = root / partition_directory(region)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "part-000.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for sale in by_region[region]:
                writer.writerow(
                    {
                        "order_id": sale.order_id,
                        "event_date": sale.event_date.isoformat(),
                        "category": sale.category,
                        "units": sale.units,
                        "unit_price": str(sale.unit_price),
                        "note": sale.note or "",
                    }
                )
        paths.append(path)
    return tuple(paths)


def _require_modules(names: Sequence[str]) -> None:
    missing = [name for name in names if importlib.util.find_spec(name) is None]
    if missing:
        raise ModuleNotFoundError(f"optional local packages not installed: {', '.join(missing)}")


def write_parquet_round_trip(
    sales: Sequence[Sale],
    path: Path,
) -> SchemaRoundTrip:
    """Write typed Arrow data to Parquet and validate the read schema."""

    _require_modules(("pyarrow",))
    import pyarrow as pa
    import pyarrow.parquet as pq

    schema = pa.schema(
        [
            pa.field("order_id", pa.int64(), nullable=False),
            pa.field("event_date", pa.date32(), nullable=False),
            pa.field("region", pa.string(), nullable=False),
            pa.field("category", pa.string(), nullable=False),
            pa.field("units", pa.int64(), nullable=False),
            pa.field("unit_price", pa.decimal128(10, 2), nullable=False),
            pa.field("note", pa.string(), nullable=True),
        ]
    )
    table = pa.Table.from_pylist(
        [
            {
                "order_id": sale.order_id,
                "event_date": sale.event_date,
                "region": sale.region,
                "category": sale.category,
                "units": sale.units,
                "unit_price": sale.unit_price,
                "note": sale.note,
            }
            for sale in sales
        ],
        schema=schema,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path, compression="snappy")  # type: ignore[no-untyped-call]
    restored = pq.read_table(path)  # type: ignore[no-untyped-call]
    if restored.schema != schema:
        raise AssertionError(
            f"schema changed across Parquet round trip:\n{schema}\n{restored.schema}"
        )
    return SchemaRoundTrip(
        path=path,
        schema_before=str(schema),
        schema_after=str(restored.schema),
        row_count=restored.num_rows,
        null_note_count=restored.column("note").null_count,
    )


def query_parquet_with_duckdb(
    path: Path,
    *,
    minimum_units: int,
) -> QueryObservation:
    """Query Parquet locally and return the physical-plan evidence."""

    _require_modules(("duckdb",))
    import duckdb

    sql = """
        SELECT region, sum(units * unit_price) AS revenue
        FROM read_parquet(?)
        WHERE units >= ?
        GROUP BY region
        ORDER BY region
    """
    with duckdb.connect(database=":memory:") as connection:
        raw_rows = connection.execute(
            sql,
            [str(path), minimum_units],
        ).fetchall()
        plan_rows = connection.execute(
            f"EXPLAIN {sql}",
            [str(path), minimum_units],
        ).fetchall()
    plan = "\n".join(" | ".join(str(value) for value in row) for row in plan_rows)
    normalized = plan.lower()
    rows = tuple((str(region), Decimal(str(revenue))) for region, revenue in raw_rows)
    return QueryObservation(
        rows=rows,
        plan=plan,
        filter_visible="filter" in normalized and "units" in normalized,
        projections_visible="projection" in normalized and "region" in normalized,
    )


def optional_columnar_demo(sales: Sequence[Sale], workspace: Path) -> None:
    """Run or clearly skip the optional columnar path."""

    missing = [name for name in ("pyarrow", "duckdb") if importlib.util.find_spec(name) is None]
    if missing:
        print(
            "Columnar demo not run; optional local packages missing:",
            ", ".join(missing),
        )
        return
    proof = write_parquet_round_trip(sales, workspace / "sales.parquet")
    observation = query_parquet_with_duckdb(proof.path, minimum_units=2)
    print(
        f"Parquet rows={proof.row_count}, null notes={proof.null_note_count}, "
        f"schema preserved={proof.schema_before == proof.schema_after}"
    )
    print("DuckDB rows:", observation.rows)
    print(
        "Plan evidence:",
        f"filter={observation.filter_visible}",
        f"projections={observation.projections_visible}",
    )


def main() -> int:
    """Run portable and optional paths in a disposable directory."""

    sales = load_sales()
    summary = summarize_with_csv_fallback()
    print(
        f"{summary.engine}: rows={summary.row_count}, "
        f"revenue={summary.total_revenue}, null notes={summary.null_note_count}"
    )
    with tempfile.TemporaryDirectory(prefix="ds60-columnar-") as directory:
        workspace = Path(directory)
        partitions = write_partitioned_csv(sales, workspace / "partitions")
        print("partition files:", *(path.parent.name for path in partitions))
        optional_columnar_demo(sales, workspace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
