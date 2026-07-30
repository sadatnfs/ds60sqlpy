"""python-data-01 learner lab: CSV, Arrow, Parquet, and DuckDB.

The worked example uses only ``csv`` from the standard library. Optional
PyArrow, DuckDB, and pandas exercises remain local and are explained in the
companion guide.
"""

from __future__ import annotations

import csv
from collections.abc import Callable, Iterable
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

    checks: tuple[tuple[str, Callable[[], object]], ...] = (
        ("nullable text", lambda: parse_nullable_text("  ")),
        ("revenue", lambda: total_revenue(rows)),
        ("partition path", lambda: partition_directory("north")),
    )
    for label, call in checks:
        try:
            value = call()
        except NotImplementedError:
            print(f"TODO: {label}")
        else:
            print(f"Completed: {label} -> {value!r}")


# === Numbered professional practice ===
#
# Attempt every exercise before opening solutions. Keep evidence in a copy
# under .learning/ or in tests; do not overwrite the reference solution.
# Full acceptance checks and progressive hints:
# companion-guides/py_data_01_arrow_duckdb.md
#
# Exercise 1 — define the CSV contract
# Prompt: Implement `parse_nullable_text` and `total_revenue`. Parse dates, integers, and
# prices in one place rather than scattering conversion across analysis code. Test blank
# notes and a malformed number. For real money, prefer `Decimal` or integer minor units. A
# binary `float` is used in the learner exercise only to keep its first step small.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 2 — compare storage contracts
# Prompt: Make a table in your notes: | Question | CSV | Parquet | | --- | --- | --- | |
# Can a text editor inspect it? | | | | Are types/nullability stored? | | | | Can a scan
# select columns efficiently? | | | | Does Python need an extra engine? | | | | Is
# append/stream exchange simple? | | | Choose a format for a five-row configuration export
# and for a repeated 50-million-row analytical scan. Explain each answer.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 3 — build an Arrow schema
# Prompt: With PyArrow installed, define non-null integer, date, region, category, units,
# and decimal fields plus a nullable note. Create the table with this schema, write
# Parquet, read it, and assert: - schema equality, - six rows, and - three null notes. Do
# not infer the schema first and then claim it was guaranteed.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 4 — make partitions deliberate
# Prompt: Implement `partition_directory`. Reject `../north`, slashes, empty strings, and
# unexpected case. Write one stable file per region at
# `region=<validated-value>/part-000.csv`. Partitioning every high-cardinality value can
# create millions of tiny files, so choose commonly filtered dimensions and plan sizes.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 5 — query Parquet with DuckDB
# Prompt: Use an in-memory connection and `read_parquet(?)`. Group revenue by region for
# rows with at least two units. Bind path and threshold values as parameters. Then run
# `EXPLAIN` on the same SQL. Find: - a Parquet scan, - a units filter, and - projected
# columns that exclude `note`. Record the plan from your installed DuckDB version. Plan
# formatting changes, so look for semantics rather than copying one exact rendering.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 6 — explain pushdown honestly
# Prompt: Pushdown does not mean every query reads zero irrelevant bytes. Row-group
# statistics, file organization, filter selectivity, expression support, and engine
# version matter. Write: 1. what the plan proves, 2. what it suggests may be skipped, and
# 3. what would require profiling or scan metrics to prove.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 7 — exercise the fallback
# Prompt: Run `summarize_with_csv_fallback` in an environment without PyArrow/DuckDB. If
# pandas exists, it uses typed `read_csv`; otherwise it uses the standard library. Confirm
# the same row count, null count, region set, and revenue across engines. Verify optional
# package detection neither installs dependencies nor contacts the network.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 8 — plan schema evolution
# Prompt: Create version 2 of the sales schema with one nullable additive column and one
# proposed type change. Define which readers remain compatible and write a
# migration/rejection policy.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 9 — control file and row-group size
# Prompt: Generate a larger local deterministic dataset and compare many tiny Parquet
# files with fewer bounded files/row groups. Record metadata count, scan planning, file
# sizes, and filtered query behavior.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 10 — validate a dataset before querying
# Prompt: Build a local validation report for schema equality, required/null counts,
# unique row IDs, accepted regions, positive units, decimal range, date range, partition-
# to-column agreement, and total row count.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 11 — reconcile a local analytical join
# Prompt: Create a small region lookup fixture, join it to sales in DuckDB, and reproduce
# the result with standard-library or pandas logic. Include an unknown region and
# duplicate lookup key.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 12 — find a non-pushdown filter
# Prompt: Compare `units >= ?` with a transformed predicate such as a function of units.
# Inspect plans and scan evidence, then rewrite only when semantics remain identical.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 13 — publish a dataset atomically
# Prompt: Write partitioned output to a temporary version directory, validate it, create a
# manifest of relative paths, sizes, hashes, rows, and schema, then atomically update a
# local current-version pointer.
# Evidence: add a boundary check and explain the failure policy.
#
# Exercise 14 — reconcile decimals and timestamps across engines
# Prompt: Add boundary decimal values and timezone-aware timestamps to a local round trip.
# Compare CSV parsing, Arrow/Parquet, pandas, and DuckDB types and results with explicit
# normalization.
# Evidence: add a boundary check and explain the failure policy.
#
# === End numbered professional practice ===

if __name__ == "__main__":
    self_check()
