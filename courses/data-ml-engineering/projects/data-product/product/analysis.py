"""Actual Polars quality checks, DuckDB aggregation and an independent oracle."""

from __future__ import annotations

from typing import Any

import duckdb
import polars as pl
import pyarrow as pa

from .contracts import ROUTES, StateError, validate_snapshot

SCHEMA = pa.schema([("route_id", pa.int64()), ("deliveries", pa.int64()), ("packages", pa.int64())])


def transform(
    snapshot: dict[str, Any],
) -> tuple[pa.Table | None, list[dict[str, Any]], dict[str, int]]:
    validate_snapshot(snapshot)
    frame = pl.DataFrame(
        snapshot["records"],
        schema={"delivery_id": pl.String, "route_id": pl.Int64, "packages": pl.Int64},
        strict=True,
    )
    reasons: list[dict[str, Any]] = []
    duplicate = frame.filter(pl.col("delivery_id").is_duplicated())
    if duplicate.height:
        reasons.append(
            {
                "code": "duplicate_delivery",
                "identities": sorted(set(duplicate["delivery_id"].to_list()))[:8],
            }
        )
    unknown = frame.filter(~pl.col("route_id").is_in(list(ROUTES)))
    if unknown.height:
        reasons.append(
            {"code": "unknown_route", "identities": sorted(set(unknown["route_id"].to_list()))[:8]}
        )
    nonpositive = frame.filter(pl.col("packages") <= 0)
    if nonpositive.height:
        reasons.append(
            {"code": "nonpositive_packages", "identities": nonpositive["delivery_id"].to_list()[:8]}
        )
    statistics = {"source_rows": frame.height, "source_packages": int(frame["packages"].sum())}
    if reasons:
        return None, reasons, statistics
    connection = duckdb.connect(":memory:")
    try:
        connection.execute("SET threads=2")
        connection.register("deliveries", frame.to_arrow())
        values = connection.execute(
            "SELECT route_id, count(*) AS deliveries, sum(packages) AS packages "
            "FROM deliveries GROUP BY route_id ORDER BY route_id"
        ).fetchall()
    finally:
        connection.close()
    rows = [
        {"route_id": int(route), "deliveries": int(count), "packages": int(packages)}
        for route, count, packages in values
    ]
    expected: dict[int, dict[str, int]] = {}
    for record in snapshot["records"]:
        route = record["route_id"]
        entry = expected.setdefault(route, {"route_id": route, "deliveries": 0, "packages": 0})
        entry["deliveries"] += 1
        entry["packages"] += record["packages"]
    oracle = [expected[key] for key in sorted(expected)]
    if rows != oracle:
        raise StateError("Actual analytical result disagrees with the independent source oracle")
    table = pa.Table.from_pylist(rows, schema=SCHEMA)
    return table, reasons, statistics
