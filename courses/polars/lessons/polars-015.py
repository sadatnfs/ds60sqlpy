"""polars-015: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Increase input size within a declared resource budget.
# TODO 2: Use a nearly unique grouping key.
# TODO 3: Write the same query directly to Parquet.
# TODO 4: Add an ordered output requirement.
# TODO 5: Explain why subtracting a full-dataset mean is not independently streamable by
#    arbitrary batches.
# TODO 6: Write a capacity conclusion supported by this fixture.
