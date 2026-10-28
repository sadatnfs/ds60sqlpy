# polars-016: explained reference

Use a Python UDF only with an explicit value, type and batching contract.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Replace the UDF

The native expression keeps semantics visible to the engine. Removing Python callbacks is useful when the native operation actually expresses the same logic.

**Expected:** The values remain [1,4,9].

## 2. State a return type

Choose a dtype that can represent the permitted range, and test overflow or missing output under the intended policy.

**Expected:** It declares the intended integer dtype.

## 3. Change batch boundaries

The batch mean depends on the partition. That is why a partition-independent declaration would be false for this implementation.

**Expected:** The batchwise answer changes while the global answer does not.

## 4. Find a weak check

Use an independent row-level oracle or a property that distinguishes the intended operation. A convenient invariant may be necessary but insufficient.

**Expected:** Both incorrect and correct outputs can sum to zero.

## 5. Introduce hidden state

Keep counters outside the value transformation for diagnostics, or compute counts with explicit reductions. Do not use callback side effects as record identity.

**Expected:** Output can depend on evaluation order or batching.

## 6. Design a valid two-pass method

The first stage aggregates sufficient information. The second uses a constant derived from that declared population. Keep both stages within the correct train/time boundary.

**Expected:** First obtain the global mean, then subtract that fixed value.

## Complete reference

```python
"""polars-016: complete bounded Polars investigation."""

import polars as pl


def example_one():
    frame = pl.DataFrame({"x": [1, 2, 3]})
    native = frame.select((pl.col("x") * pl.col("x")).alias("square"))
    udf = frame.select(
        pl.col("x").map_elements(lambda value: value * value, return_dtype=pl.Int64).alias("square")
    )
    assert native.equals(udf)
    assert native["square"].to_list() == [1, 4, 9]
    return {"values": native.to_dicts(), "native_and_udf_equal_on_fixture": True}


def example_two():
    values = [1.0, 2.0, 3.0, 10.0]
    global_centered = [x - sum(values) / len(values) for x in values]
    batches = [values[:2], values[2:]]
    incorrectly_batched = [x - sum(batch) / len(batch) for batch in batches for x in batch]
    assert global_centered == [-3.0, -2.0, -1.0, 6.0]
    assert incorrectly_batched == [-0.5, 0.5, -3.5, 3.5]
    assert global_centered != incorrectly_batched
    return {
        "whole_dataset_centering": global_centered,
        "invalid_batchwise_centering": incorrectly_batched,
    }


def main():
    print(example_one())
    print(example_two())
    print("polars-016 reference checks passed")


if __name__ == "__main__":
    main()
```

## Interpretation

Use a Python UDF only with an explicit value, type and batching contract. Demonstrate equivalence to a trusted result on contrasting fixtures and identify which optimization claims are justified. Preserve a native implementation whenever it is clearer and semantically equivalent.
