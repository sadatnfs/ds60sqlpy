# polars-016: explained reference

Use a Python UDF only with an explicit value, type and batching contract.

The executable reference contains the two complete worked cases with assertions. The changes below explain the independent practice and its limits.


## 1. Replace the UDF

The native expression keeps semantics visible to the engine. Removing Python callbacks is useful when the native operation actually expresses the same logic.

```python
import polars as pl

frame = pl.DataFrame({"x": [1, 2, 3]})
native = frame.select(pl.col("x").pow(2).alias("square"))
assert native["square"].to_list() == [1, 4, 9]
```

**Why it holds here:** pl.col('x').pow(2) is a native expression the engine can see and vectorize, and on [1, 2, 3] it gives [1, 4, 9], matching the map_elements version from example_one.

**Plausible wrong approach:** Keeping the lambda and only setting return_dtype still runs Python once per row and blocks optimizations that need to inspect the expression.

**How to verify:** Run the answer code and assert [1, 4, 9], then compare with the UDF output via native.equals(udf).

**Expected:** The values remain [1, 4, 9].

## 2. State a return type

Choose a dtype that can represent the permitted range, and test overflow or missing output under the intended policy.

**Why it holds here:** map_elements cannot infer a dtype reliably before running, so declaring return_dtype=pl.Int64 states what the column should hold and lets the schema be known in advance.

**Plausible wrong approach:** Omitting return_dtype lets Polars guess from the first values, so a column of small values today may get a different dtype than one with large values tomorrow.

**How to verify:** Declare pl.Int64 in the UDF, then check frame.select(...).schema shows Int64 and that a value above the Int64 range is rejected or handled by a test.

**Expected:** It declares the intended integer dtype.

## 3. Change batch boundaries

The batch mean depends on the partition. That is why a partition-independent declaration would be false for this implementation.

**Why it holds here:** With batches [1] and [2, 3, 10], each batch subtracts its own mean, giving [0, -3, -2, 5], while the global result stays [-3, -2, -1, 6].

**Plausible wrong approach:** Assuming batch size does not matter because each batch looks centered ignores that the means 1 and 5 differ from the global 4.

**How to verify:** Compute both partitions in plain Python as example_two does and assert the batch outputs differ from each other and from the global one.

**Expected:** The batchwise answer changes while the global answer does not.

## 4. Find a weak check

Use an independent row-level oracle or a property that distinguishes the intended operation. A convenient invariant may be necessary but insufficient.

**Why it holds here:** Both the batched output [-0.5, 0.5, -3.5, 3.5] and the global output [-3, -2, -1, 6] sum to zero, so a sum check cannot tell them apart.

**Plausible wrong approach:** Treating zero sum as proof of correct centering passes the defect, because any per batch centering also sums to zero.

**How to verify:** Compare against an independently computed list such as x minus 4.0 for each value, which fails for the batched output.

**Expected:** Both incorrect and correct outputs can sum to zero.

## 5. Introduce hidden state

Keep counters outside the value transformation for diagnostics, or compute counts with explicit reductions. Do not use callback side effects as record identity.

**Why it holds here:** A counter incremented inside the UDF depends on how many times and in what order Polars calls it, which can change with threads, batching or optimization.

**Plausible wrong approach:** Using that counter as a row id works on a small single threaded run and then produces gaps or repeats under a different engine.

**How to verify:** Use with_row_index for identity and pl.len() for counts, and test by running the query with two engines and comparing ids.

**Expected:** Output can depend on evaluation order or batching.

## 6. Design a valid two-pass method

The first stage aggregates sufficient information. The second uses a constant derived from that declared population. Keep both stages within the correct train/time boundary.

**Why it holds here:** Stage one computes the mean of [1, 2, 3, 10], which is 4.0. Stage two subtracts that constant from every row, so batches can run freely because the constant does not depend on them.

**Plausible wrong approach:** Computing the mean on all data including validation rows makes the two pass method correct numerically but leaks held out information.

**How to verify:** Store the stage one mean, apply stage two over any partition, and assert [-3, -2, -1, 6] regardless of how rows are split.

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

Demonstrate equivalence to a trusted result on contrasting fixtures and identify which optimization claims are justified. Preserve a native implementation whenever it is clearer and semantically equivalent.
