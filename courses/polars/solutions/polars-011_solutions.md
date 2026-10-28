# polars-011: explained reference

Publish a small typed artifact with independently checked readback.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change input order

Compare after sorting by id. If output order matters to a consumer, publish that order explicitly rather than relying on a directory listing.

**Expected:** Sorted logical output remains equal.

## 2. Prevent self-ingestion

Separate source and output namespaces or use an explicit input manifest. A broad *.parquet pattern can turn an idempotent transformation into repeated accumulation.

**Expected:** A rerun does not read its prior combined output.

## 3. Validate the output key

Add a duplicate id across two files to demonstrate the need for a global contract. Per-file uniqueness is insufficient.

**Expected:** n_unique equals height for the valid fixture.

## 4. Track rejected coverage

Keep raw identifiers and reasons, then reconcile counts. If a policy imputes a value instead, record that category separately.

**Expected:** Two accepted plus one rejected equals three source rows.

## 5. Test a schema change

Treat schema evolution as a reviewed contract change. A successful read that widens everything to text may break downstream arithmetic.

**Expected:** The program either rejects it or follows a documented cast policy.

## 6. Verify an artifact

Check the actual file after writing. A larger pipeline should also record its input identity, version and ownership before publication.

**Expected:** Readback matches the intended frame.

## Complete reference

```python
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
```

## Interpretation

Publish a small typed artifact with independently checked readback. Extend it to multiple input parts, a deliberate overlap and one malformed value. Describe which failures stop publication and which produce an explicit quarantine artifact; that decision becomes a testable contract in analytics engineering.
