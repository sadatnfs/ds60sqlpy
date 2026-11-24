# polars-012: explained reference

Move a typed table across an Arrow boundary while preserving its logical contract.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Inspect a null bitmap conceptually

Columnar validity allows an absent value to be represented independently of valid zero. This distinction must survive interoperability boundaries.

**Why it holds here:** In Arrow each column has a values buffer plus a separate validity bitmap. In the reference frame the value column holds 2.0, null and 4.0, and Arrow reports null_count 1 for it.

**Plausible wrong approach:** Encoding the missing value as 0.0 or NaN in the values buffer makes it a number, so a mean would include it and null_count would read 0.

**How to verify:** Convert with frame.to_arrow() and check arrow.column('value').null_count == 1, then compare with a frame where the value is 0.0 and null_count is 0.

**Expected:** The answer identifies validity metadata.

## 2. Avoid a zero-copy claim

Inspect buffers or profile allocations for a specific conversion before making a performance claim. to_pylist explicitly constructs Python objects.

**Why it holds here:** to_arrow followed by from_arrow returning an equal frame proves the values, nulls and dtypes survived for these three rows, which is a logical claim.

**Plausible wrong approach:** Concluding that the conversion copied no memory from a passing equality test is unsupported, and to_pylist definitely creates new Python objects.

**How to verify:** Keep the claim to restored.equals(frame) being True; if memory matters, measure allocations or inspect buffer addresses for that specific path.

**Expected:** It proves logical equality on the fixture.

## 3. Add a valid category

Update the declared Enum and tests together. Downstream consumers need the same versioned vocabulary.

**Why it holds here:** Extending pl.Enum to ['new', 'paid', 'shipped', 'returned'] makes returned a valid label, so casting it succeeds and it sorts after shipped.

**Plausible wrong approach:** Changing only the data while keeping the three label Enum makes the cast raise, and editing only the code without a version note leaves consumers on the old list.

**How to verify:** Cast pl.Series(['returned']) to the new Enum and check it succeeds, then confirm casting with the old three label Enum still raises.

**Expected:** The cast accepts the new label under the revised contract.

## 4. Reject an unknown category

Use a separate quarantine reason or deliberately evolve the vocabulary. Silently mapping it to shipped would create a false business state.

```python
import polars as pl

status = pl.Enum(["new", "paid", "shipped"])
try:
    pl.Series(["new", "cancelled"]).cast(status)
except pl.exceptions.InvalidOperationError:
    rejected = True
else:
    rejected = False
assert rejected
```

**Why it holds here:** cancelled is not among new, paid and shipped, so a strict cast to the Enum raises InvalidOperationError rather than inventing a code.

**Plausible wrong approach:** Replacing unknown labels with shipped before casting makes the cast pass and reports cancelled orders as shipped.

**How to verify:** Run the answer code and assert rejected is True; the same pattern rejects unknown in example_two.

**Expected:** Strict conversion rejects it.

## 5. Compare sort policies

The correct order depends on the question. Keep ordered state semantics explicit instead of relying on hidden physical category codes.

**Why it holds here:** For new, paid and shipped the Enum order and alphabetical order coincide, so the fixture cannot reveal a difference. Adding returned after shipped can: business order puts it last, alphabetical puts it before shipped.

**Plausible wrong approach:** Concluding from the three label fixture that the two sorts are interchangeable generalizes from a case where they happen to agree.

**How to verify:** Sort a frame with all four labels once as the Enum and once cast to String, and compare: the Enum gives new, paid, shipped, returned while text gives new, paid, returned, shipped.

**Expected:** Their orders can differ.

## 6. Design an interchange contract

Arrow carries structural types; your contract carries what identifiers and values mean. Add compatibility checks at the consumer boundary.

**Why it holds here:** An Arrow schema says value is a nullable float and status is a dictionary type, but not that value is in dollars, that rows are one per order, or that null means not yet measured.

**Plausible wrong approach:** Sending only the Arrow table and assuming its schema documents the data leaves the receiver to guess grain, units and the meaning of nulls.

**How to verify:** List grain, units, null policy, allowed categories and schema version in the contract, and have the consumer test the version and a key uniqueness check on arrival.

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

Document which properties were checked and which memory claims were not measured. Use explicit category vocabularies when business order matters, and test unknown-value handling as part of schema evolution.
