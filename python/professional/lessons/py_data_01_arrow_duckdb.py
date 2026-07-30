"""python-data-01 learner lab: CSV, Arrow, Parquet, and DuckDB.

The worked example uses only ``csv`` from the standard library. Optional
PyArrow, DuckDB, and pandas exercises remain local and are explained in the
companion guide.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "data" / "sales.csv"


def read_raw_rows(path: Path = FIXTURE) -> list[dict[str, str]]:
    """Worked example: read CSV's string-oriented representation."""

    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_nullable_text(value: str) -> str | None:
    """Convert CSV's empty-field convention into an explicit nullable value.

    TODO: trim surrounding whitespace and return ``None`` for an empty value.
    """

    raise NotImplementedError("complete parse_nullable_text")


def total_revenue(rows: Iterable[dict[str, str]]) -> float:
    """Calculate ``units * unit_price`` across raw CSV rows.

    TODO: parse each field explicitly. Round only the final display value;
    discuss in the guide why Decimal or integer minor units are safer for real
    money.
    """

    raise NotImplementedError("complete total_revenue")


def partition_directory(region: str) -> str:
    """Return a Hive-style partition directory such as ``region=north``.

    TODO: accept only lower-case letters, digits, and hyphens. Reject empty or
    unsafe values rather than inserting arbitrary text into a path.
    """

    raise NotImplementedError("complete partition_directory")


def self_check() -> None:
    rows = read_raw_rows()
    print(f"Worked example: {len(rows)} raw rows")
    print(
        "Raw Python types:",
        {key: type(value).__name__ for key, value in rows[0].items()},
    )
    print(f"Blank note from CSV is represented as {rows[1]['note']!r}")

    for label, call in (
        ("nullable text", lambda: parse_nullable_text("  ")),
        ("revenue", lambda: total_revenue(rows)),
        ("partition path", lambda: partition_directory("north")),
    ):
        try:
            value = call()
        except NotImplementedError:
            print(f"TODO: {label}")
        else:
            print(f"Completed: {label} -> {value!r}")


if __name__ == "__main__":
    self_check()
