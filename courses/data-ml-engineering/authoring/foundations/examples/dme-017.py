"""Compare real local engines under one explicit known-value aggregation policy."""

import sqlite3

import duckdb
import polars as pl


def sql_result(factory, records):
    connection = factory()
    try:
        connection.execute(
            "create table daily(route_id integer, day varchar, "
            "packages integer, primary "
            "key(route_id,day))"
        )
        connection.executemany("insert into daily values (?,?,?)", records)
        return connection.execute(
            "select route_id,sum(packages),count(*),count(packages) "
            "from daily group by route_id order by "
            "route_id"
        ).fetchall()
    finally:
        connection.close()


def polars_result(records, explicit_empty_policy=False):
    frame = pl.DataFrame(
        records,
        schema={"route_id": pl.Int64, "day": pl.String, "packages": pl.Int64},
        orient=("row"),
    )
    if frame.select(pl.struct("route_id", "day").n_unique()).item() != frame.height:
        raise ValueError("The declared daily observation grain must be unique")
    total = pl.col("packages").sum()
    if explicit_empty_policy:
        total = (
            pl.when(pl.col("packages").count() > 0)
            .then(total)
            .otherwise(pl.lit(None, dtype=pl.Int64))
        )
    return (
        frame.group_by("route_id")
        .agg(
            total.alias("known_total"),
            pl.len().alias("all_days"),
            pl.col("packages").count().alias("known_days"),
        )
        .sort("route_id")
        .rows()
    )


def example_one():
    records = [
        (10, "2024-01-01", 2),
        (10, "2024-01-02", None),
        (20, "2024-01-01", 3),
        (20, "2024-01-02", 0),
    ]
    sqlite = sql_result(lambda: sqlite3.connect(":memory:"), records)
    duck = sql_result(lambda: duckdb.connect(":memory:"), records)
    polars = polars_result(records)
    expected = [(10, 2, 2, 1), (20, 3, 2, 2)]
    assert sqlite == duck == polars == expected
    return {
        "columns": ["route_id", "known_total", "all_days", "known_days"],
        "actual_sqlite": sqlite,
        ("actual_duckdb"): duck,
        ("actual_polars"): polars,
    }


def example_two():
    records = [(30, "2024-01-01", None), (40, "2024-01-01", 0)]
    sqlite = sql_result(lambda: sqlite3.connect(":memory:"), records)
    duck = sql_result(lambda: duckdb.connect(":memory:"), records)
    raw_polars = polars_result(records)
    normalized = polars_result(records, explicit_empty_policy=True)
    assert sqlite == duck == [(30, None, 1, 0), (40, 0, 1, 1)]
    assert raw_polars == [(30, 0, 1, 0), (40, 0, 1, 1)]
    assert normalized == sqlite
    return {
        "sql_policy": sqlite,
        "default_polars": raw_polars,
        "explicit_policy_alignment": normalized,
        ("unknown_total_differs_from_known_zero"): True,
    }


def main():
    print("Actual engine comparison on declared daily grain:", example_one())
    print("Empty known populations need an explicit policy:", example_two())


if __name__ == "__main__":
    main()
