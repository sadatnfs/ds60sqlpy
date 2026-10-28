"""polars-011: worked starting point; complete the guide's six changes."""

import tempfile
from pathlib import Path

import polars as pl


def example_one():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        pl.DataFrame({"id": [1, 2], "value": [2.5, 3.5]}).write_parquet(root / "part-a.parquet")
        pl.DataFrame({"id": [3], "value": [4.5]}).write_parquet(root / "part-b.parquet")
        query = pl.scan_parquet(str(root / "part-*.parquet")).select("id", "value")
        query.sink_parquet(root / "combined.parquet")
        result = pl.read_parquet(root / "combined.parquet").sort("id")
        assert result["id"].to_list() == [1, 2, 3]
        assert result["value"].sum() == 10.5
        return {"rows": result.to_dicts(), "schema": str(result.schema)}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Rename the input parts so their lexical order changes.
# TODO 2: Explain why combined.parquet is outside part-*.parquet.
# TODO 3: Check output id uniqueness after combining parts.
# TODO 4: Report accepted and rejected CSV counts.
# TODO 5: Change one part from numeric values to incompatible text.
# TODO 6: Read the written Parquet file and compare its schema and values.
