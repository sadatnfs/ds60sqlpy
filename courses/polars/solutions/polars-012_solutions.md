# polars-012: explained reference

Move a typed table across an Arrow boundary while preserving its logical contract.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Inspect a null bitmap conceptually

Columnar validity allows an absent value to be represented independently of valid zero. This distinction must survive interoperability boundaries.

**Expected:** The answer identifies validity metadata.

## 2. Avoid a zero-copy claim

Inspect buffers or profile allocations for a specific conversion before making a performance claim. to_pylist explicitly constructs Python objects.

**Expected:** It proves logical equality on the fixture.

## 3. Add a valid category

Update the declared Enum and tests together. Downstream consumers need the same versioned vocabulary.

**Expected:** The cast accepts the new label under the revised contract.

## 4. Reject an unknown category

Use a separate quarantine reason or deliberately evolve the vocabulary. Silently mapping it to shipped would create a false business state.

**Expected:** Strict conversion rejects it.

## 5. Compare sort policies

The correct order depends on the question. Keep ordered state semantics explicit instead of relying on hidden physical category codes.

**Expected:** Their orders can differ.

## 6. Design an interchange contract

Arrow carries structural types; your contract carries what identifiers and values mean. Add compatibility checks at the consumer boundary.

**Expected:** It includes grain, units, null policy and schema version.

## Complete reference

```python
"""polars-012: complete bounded Polars investigation."""

import polars as pl
import pyarrow as pa


def example_one():
    frame = pl.DataFrame({"id": [1, 2, 3], "value": [2.0, None, 4.0]})
    arrow = frame.to_arrow()
    assert arrow.column("id").to_pylist() == [1, 2, 3]
    assert arrow.column("value").null_count == 1
    restored = pl.from_arrow(arrow)
    assert restored.equals(frame)
    assert isinstance(arrow, pa.Table)
    return {"arrow_schema": str(arrow.schema), "round_trip": True, "nulls": 1}


def example_two():
    status = pl.Enum(["new", "paid", "shipped"])
    frame = pl.DataFrame({"status": ["shipped", "new", "paid"]}).with_columns(
        pl.col("status").cast(status)
    )
    assert frame.sort("status")["status"].cast(pl.String).to_list() == ["new", "paid", "shipped"]
    try:
        pl.Series(["unknown"]).cast(status)
    except pl.exceptions.InvalidOperationError:
        rejected = True
    else:
        rejected = False
    assert rejected
    return {"business_order": ["new", "paid", "shipped"], "unknown_rejected": rejected}


def main():
    print(example_one())
    print(example_two())
    print("polars-012 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Move a typed table across an Arrow boundary while preserving its logical contract. Document which properties were checked and which memory claims were not measured. Use explicit category vocabularies when business order matters, and test unknown-value handling as part of schema evolution.
