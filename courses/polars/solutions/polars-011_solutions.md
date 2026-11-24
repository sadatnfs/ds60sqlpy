# polars-011: explained reference

Publish a small typed artifact with independently checked readback.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Change input order

Compare after sorting by id. If output order matters to a consumer, publish that order explicitly rather than relying on a directory listing.

**Why it holds here:** The glob reads part-a and part-b in whatever order the directory lists them, but sorting by id gives [1, 2, 3] with values summing to 10.5 either way.

**Plausible wrong approach:** Comparing the unsorted frames after renaming fails spuriously, and asserting on head() rows ties the test to filesystem listing order.

**How to verify:** Rename the parts so b sorts first, rerun, and assert sort('id') output equals the original sorted output.

**Expected:** Sorted logical output remains equal.

## 2. Prevent self-ingestion

Separate source and output namespaces or use an explicit input manifest. A broad *.parquet pattern can turn an idempotent transformation into repeated accumulation.

**Why it holds here:** part-*.parquet cannot match combined.parquet, so a rerun reads only the three source rows and rewrites the same output.

**Plausible wrong approach:** A glob of *.parquet would pick up the previous combined.parquet on each rerun, so the row count would grow from 3 to 6 and then 9 without any error.

**How to verify:** Run the pipeline twice in the same directory and assert the combined height stays 3 and the value total stays 10.5.

**Expected:** A rerun does not read its prior combined output.

## 3. Validate the output key

Add a duplicate id across two files to demonstrate the need for a global contract. Per-file uniqueness is insufficient.

```python
import tempfile
from pathlib import Path

import polars as pl

with tempfile.TemporaryDirectory() as d:
    root = Path(d)
    pl.DataFrame({"id": [1, 2], "value": [2.5, 3.5]}).write_parquet(root / "part-a.parquet")
    pl.DataFrame({"id": [3], "value": [4.5]}).write_parquet(root / "part-b.parquet")
    combined = pl.scan_parquet(str(root / "part-*.parquet")).collect()
    assert combined["id"].n_unique() == combined.height == 3
```

**Why it holds here:** Uniqueness must hold across all parts together. In the fixture ids 1, 2 and 3 are distinct overall, so n_unique and height both equal 3.

**Plausible wrong approach:** Checking each file separately passes even if part-b also contained id 2, because each file alone would still be unique.

**How to verify:** Run the answer code, then rewrite part-b with id 2 and confirm the global assertion fails while per file checks still pass.

**Expected:** n_unique equals height for the valid fixture.

## 4. Track rejected coverage

Keep raw identifiers and reasons, then reconcile counts. If a policy imputes a value instead, record that category separately.

```python
import tempfile
from pathlib import Path

import polars as pl

with tempfile.TemporaryDirectory() as d:
    path = Path(d) / "raw.csv"
    path.write_text("id,amount\n1,2\n2,broken\n3,4\n")
    raw = pl.read_csv(path, schema_overrides={"amount": pl.String})
    parsed = raw.with_columns(pl.col("amount").cast(pl.Int64, strict=False).alias("parsed"))
    accepted = parsed.filter(pl.col("parsed").is_not_null()).height
    rejected = parsed.filter(pl.col("parsed").is_null()).height
    assert (accepted, rejected, raw.height) == (2, 1, 3)
```

**Why it holds here:** Reading amount as String keeps broken as text, and the non strict cast turns it into null, so ids 1 and 3 are accepted and id 2 is rejected.

**Plausible wrong approach:** Filtering out the null parsed rows and reporting only the accepted frame gives a clean total of 6 but no record that id 2 existed, so the counts cannot be reconciled.

**How to verify:** Run the answer code: (accepted, rejected, raw.height) equals (2, 1, 3), and the accepted parsed total is 6.

**Expected:** Two accepted plus one rejected equals three source rows.

## 5. Test a schema change

Treat schema evolution as a reviewed contract change. A successful read that widens everything to text may break downstream arithmetic.

**Why it holds here:** If part-b's value column becomes text while part-a stays float, the parts no longer share one schema and the combined read must either fail or apply a stated cast.

**Plausible wrong approach:** Reading every part as String to make the scan succeed hides the change and breaks the later value sum of 10.5.

**How to verify:** Write part-b with a String value column, rerun, and record whether the read raises; if a cast policy is chosen, assert its rejected count.

**Expected:** The program either rejects it or follows a documented cast policy.

## 6. Verify an artifact

Check the actual file after writing. A larger pipeline should also record its input identity, version and ownership before publication.

**Why it holds here:** Reading back combined.parquet checks what was actually written; sorted ids [1, 2, 3], values summing to 10.5 and the Int64 and Float64 schema should all match.

**Plausible wrong approach:** Asserting only on the in memory frame before writing would miss a sink failure, a wrong path or a dtype change during write.

**How to verify:** Run pl.read_parquet on the output, sort by id, and assert equality with the intended frame and equality of the schemas.

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

Extend it to multiple input parts, a deliberate overlap and one malformed value. Describe which failures stop publication and which produce an explicit quarantine artifact; that decision becomes a testable contract in analytics engineering.
