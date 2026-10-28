"""polars-010: worked starting point; complete the guide's six changes."""

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


if __name__ == "__main__":
    print(example_one())

# TODO 1: Raise the amount threshold to 15.
# TODO 2: Add a large text field that the result does not need.
# TODO 3: Compute the same filter and projection eagerly.
# TODO 4: Change group A to values 1 and 11.
# TODO 5: Identify which statement actually materializes the query.
# TODO 6: Explain why asserting the entire explain string is brittle.
