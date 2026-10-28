"""polars-010: complete bounded Polars investigation."""

import tempfile
from pathlib import Path

import polars as pl


def example_one():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "events.parquet"
        pl.DataFrame(
            {"id": [1, 2, 3], "amount": [5, 12, 20], "unused": ["x", "y", "z"]}
        ).write_parquet(path)
        query = (
            pl.scan_parquet(path)
            .filter(pl.col("amount") >= 10)
            .select("id", (pl.col("amount") * 2).alias("doubled"))
        )
        schema = query.collect_schema()
        assert schema.names() == ["id", "doubled"]
        result = query.collect(engine="streaming").sort("id")
        assert result.to_dict(as_series=False) == {"id": [2, 3], "doubled": [24, 40]}
        print(query.explain(optimized=True))
        return {"result": result.to_dicts(), "planned_columns": schema.names()}


def example_two():
    frame = pl.DataFrame({"group": ["A", "A", "B"], "value": [1, 9, 8]})
    after = (
        frame.lazy()
        .group_by("group")
        .agg(pl.col("value").mean().alias("mean"))
        .filter(pl.col("mean") > 6)
        .collect()
    )
    before = (
        frame.lazy()
        .filter(pl.col("value") > 6)
        .group_by("group")
        .agg(pl.col("value").mean().alias("mean"))
        .collect()
        .sort("group")
    )
    assert after["group"].to_list() == ["B"]
    assert before["group"].to_list() == ["A", "B"]
    return {"group_filter": after.to_dicts(), "changed_population": before.to_dicts()}


def main():
    print(example_one())
    print(example_two())
    print("polars-010 reference checks passed")


if __name__ == "__main__":
    main()
