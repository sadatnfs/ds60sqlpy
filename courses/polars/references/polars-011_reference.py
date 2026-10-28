"""polars-011: complete bounded Polars investigation."""

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


def example_two():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "raw.csv"
        path.write_text("id,amount\n1,2\n2,broken\n3,4\n")
        raw = pl.read_csv(path, schema_overrides={"amount": pl.String})
        parsed = raw.with_columns(pl.col("amount").cast(pl.Int64, strict=False).alias("parsed"))
        invalid = parsed.filter(pl.col("parsed").is_null())
        assert invalid["id"].to_list() == [2]
        assert parsed.filter(pl.col("parsed").is_not_null())["parsed"].sum() == 6
        return {"quarantine": invalid.to_dicts(), "accepted_total": 6}


def main():
    print(example_one())
    print(example_two())
    print("polars-011 reference checks passed")


if __name__ == "__main__":
    main()
