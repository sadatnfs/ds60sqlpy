"""Actual Polars quality classification and version-aware snapshot selection."""

import polars as pl

SCHEMA = {
    "row_id": pl.Int64,
    "delivery_id": pl.String,
    "source_version": pl.Int64,
    "packages": pl.Int64,
    "route_id": pl.Int64,
}


def fixture():
    return pl.DataFrame(
        {
            "row_id": [1, 2, 3],
            "delivery_id": ["A", "B", "A"],
            "source_version": [1, 1, 2],
            "packages": [2, 3, 4],
            "route_id": [10, 20, 10],
        },
        schema=SCHEMA,
    )


def inspect(frame):
    if dict(frame.schema) != SCHEMA:
        raise ValueError("Validate the declared typed column schema before this quality pass")
    if frame["row_id"].null_count() or frame["row_id"].n_unique() != frame.height:
        raise ValueError("Each supplied row needs its own audit identity")
    classified = frame.with_columns(
        pl.when(
            pl.col("delivery_id").is_null()
            | (pl.col("delivery_id").str.strip_chars().str.len_chars() == 0)
        )
        .then(pl.lit("missing_delivery_id"))
        .when(pl.col("source_version").is_null() | (pl.col("source_version") < 1))
        .then(pl.lit("invalid_source_version"))
        .when(pl.col("packages").is_null())
        .then(pl.lit("missing_packages"))
        .when(pl.col("packages") < 1)
        .then(pl.lit("nonpositive_packages"))
        .when(pl.col("route_id").is_null() | ~pl.col("route_id").is_in([10, 20]))
        .then(pl.lit("unknown_route"))
        .otherwise(pl.lit(None, dtype=pl.String))
        .alias("reason")
    )
    rejected = classified.filter(pl.col("reason").is_not_null())
    valid = classified.filter(pl.col("reason").is_null())
    conflicts = (
        valid.group_by("delivery_id", "source_version")
        .agg(
            pl.col("packages").n_unique().alias("different_package_values"),
            pl.col("route_id").n_unique().alias("different_routes"),
        )
        .filter((pl.col("different_package_values") > 1) | (pl.col("different_routes") > 1))
    )
    if conflicts.height:
        raise ValueError(
            "A delivery source version has conflicting payloads; do not choose an arbitrary row"
        )
    latest = (
        valid.sort(["delivery_id", "source_version", "row_id"])
        .unique(subset="delivery_id", keep="last", maintain_order=True)
        .sort("delivery_id")
    )
    not_current = valid.filter(~pl.col("row_id").is_in(latest["row_id"].to_list()))
    assert frame.height == latest.height + not_current.height + rejected.height
    return {
        "current": latest.select(
            "delivery_id", "source_version", "packages", "route_id"
        ).to_dicts(),
        "quarantine": rejected.select("row_id", "delivery_id", "reason").to_dicts(),
        "historical_or_replayed_row_ids": not_current["row_id"].to_list(),
        "input_rows": frame.height,
        "publishable": rejected.height == 0,
    }


def example_one():
    result = inspect(fixture())
    assert result["current"] == [
        {"delivery_id": "A", "source_version": 2, "packages": 4, "route_id": 10},
        {"delivery_id": "B", "source_version": 1, "packages": 3, "route_id": 20},
    ]
    assert result["historical_or_replayed_row_ids"] == [1] and result["quarantine"] == []
    assert result["publishable"] is True and sum(row["packages"] for row in result["current"]) == 7
    return result


def example_two():
    bad = pl.DataFrame(
        {
            "row_id": [4, 5],
            "delivery_id": ["C", "D"],
            "source_version": [1, 1],
            "packages": [None, -1],
            "route_id": [10, 20],
        },
        schema=SCHEMA,
    )
    result = inspect(pl.concat([fixture(), bad]))
    assert result["input_rows"] == 5 and result["publishable"] is False
    assert [(row["row_id"], row["reason"]) for row in result["quarantine"]] == [
        (4, "missing_packages"),
        (5, "nonpositive_packages"),
    ]
    conflict = pl.DataFrame(
        {
            "row_id": [6],
            "delivery_id": ["A"],
            "source_version": [2],
            "packages": [9],
            "route_id": [10],
        }
    )
    try:
        inspect(pl.concat([fixture(), conflict]))
    except ValueError:
        result["equal_version_conflict_rejected"] = True
    else:
        raise AssertionError("A later input position is not a valid conflict-resolution policy")
    return result


def main():
    from ds60sqlpy.plot_artifacts import publish_report, publish_table

    first, second = example_one(), example_two()
    columns = ["delivery_id", "source_version", "packages", "route_id"]
    publish_table(
        columns,
        [[row[name] for name in columns] for row in first["current"]],
        description=(
            "Accepted current snapshot selected by declared "
            "delivery version; the earlier A record remains "
            "accounted for."
        ),
    )
    publish_report(
        second,
        description=(
            "Quarantined input identities and a deliberately "
            "rejected equal-version conflict; no partial product is "
            "silently published."
        ),
    )
    print("Current package total:", sum(row["packages"] for row in first["current"]))
    print("Rejected rows:", second["quarantine"])


if __name__ == "__main__":
    main()
