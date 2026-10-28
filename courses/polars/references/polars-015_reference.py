"""polars-015: complete bounded Polars investigation."""

import tempfile
from pathlib import Path

import polars as pl


def example_one():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "source.parquet"
        pl.DataFrame(
            {
                "id": range(1000),
                "group": [i % 5 for i in range(1000)],
                "value": [i % 7 for i in range(1000)],
            }
        ).write_parquet(path)
        query = (
            pl.scan_parquet(path)
            .filter(pl.col("id") >= 100)
            .group_by("group")
            .agg(pl.col("value").sum())
            .sort("group")
        )
        memory = query.collect(engine="in-memory")
        streaming = query.collect(engine="streaming")
        assert memory.equals(streaming)
        assert streaming["value"].sum() == sum(i % 7 for i in range(100, 1000))
        query.sink_parquet(Path(d) / "result.parquet", engine="streaming")
        assert pl.read_parquet(Path(d) / "result.parquet").sort("group").equals(streaming)
        return {"same_result": True, "rows": streaming.to_dicts()}


def example_two():
    frame = pl.DataFrame({"x": range(20)})
    per_row = (
        frame.lazy().with_columns((pl.col("x") * 2).alias("twice")).collect(engine="streaming")
    )
    whole = frame.lazy().select(pl.col("x").sum().alias("total")).collect(engine="streaming")
    assert per_row.height == 20 and whole.height == 1
    assert whole.item() == 190 and per_row["twice"].sum() == 380
    return {"row_map_rows": 20, "reduction_rows": 1, "sum": 190}


def main():
    print(example_one())
    print(example_two())
    print("polars-015 reference checks passed")


if __name__ == "__main__":
    main()
