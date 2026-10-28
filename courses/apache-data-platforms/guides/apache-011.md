# apache-011: Compute kernels and chunked tables

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-010`.

## The mechanism

A record batch contains equal-length columns for one batch of rows. A table can
contain columns composed of multiple chunks. Chunks are pieces of storage and
processing history. They are not automatically customer groups, file partitions,
network partitions or transaction boundaries. A calculation must therefore define
its grouping independently of how batches happened to arrive.

Arrow compute kernels operate on typed arrays and, where supported, chunked
arrays. A kernel has an input contract and a null policy. Arithmetic, comparison,
filtering and aggregation can treat missing values differently. A comparison with
a missing value commonly produces a missing Boolean; filtering must then decide
whether a missing selection bit drops the row or produces a null output slot.
The choice affects the result's meaning and should be visible in the code.

The program uses native kernels instead of a Python loop over individual values.
This gives the engine a typed operation it can implement efficiently. It does not
eliminate all overhead or guarantee a speedup for a five-row fixture. Tiny data
are chosen here to make correctness independently checkable, not to establish a
performance ranking against Python or another engine.

## Worked case A: the chunk boundary must not change an aggregate

The first case stores `[4, None, 8]` and `[2, 6]` as two chunks of one column.
There are five logical slots and four observed numbers. The total is 20 and the
observed mean is 5. Combining the chunks and repeating the calculation gives the
same result. This is a semantic invariant: merely repacking storage must not
change the answer.

A common error is to average the two chunk means. They are 6 and 4, so this
particular fixture happens to give 5 again. The program therefore includes a
second split that has unequal observed counts and different means: `[4]` and
`[None, 8, 2, 6]`. The unweighted mean of the chunk means becomes
\((4+16/3)/2=14/3\), which is not 5. A test that uses only convenient balanced
chunks would miss the bug.

The correct recombination weights each chunk by its valid count:
\[\bar{x}=\frac{\sum_c n_c\bar{x}_c}{\sum_c n_c}.\]
This identity is also the foundation for mergeable partial aggregate states in
query engines. The state must retain enough information, here sum and count,
to combine results without changing the estimand. A mean alone is insufficient.

## Worked case B: selecting rows and replacing missing measurements

The second case compares values with 5. The resulting mask contains a missing
entry for the unknown measurement. Default filtering keeps the values 8 and 6.
Using the explicit emit-null behavior preserves an additional null slot for the
unknown comparison. Neither result says that the original value was zero.
They encode different policies about uncertain membership in the selected set.

The program also computes a mean after `fill_null(..., 0)`. That mean is 4,
because the denominator becomes five slots. The observed-only mean was 5. The
calculation has changed from the average among measured values to an average that
assigns zero to an unmeasured case. In a revenue system that could be an accepted
rule for no purchase; in a sensor system it could be a severe measurement error.
The library cannot decide the intended meaning from the numeric type alone.

A Boolean mask deserves the same attention as the data column. Filling a missing
mask with false is a selection rule; filling the measured value with zero is a
measurement rule. They can produce different downstream counts even when a final
sum happens to agree.

## Mistakes and diagnosis

Do not use batch number as a grouping key unless the problem actually defines
batches as groups. Do not compute a mean of means without the correct counts.
Do not rely on an accidental equal-size fixture to validate partial aggregation.
When output row counts differ, inspect mask validity and null-selection behavior
before blaming the kernel. The supplied assertions deliberately compare two
storage layouts and two missing-data policies.

## Interview discussion

**Which aggregate states can you safely merge across workers?** Sum and count are
straightforward associative states under their numeric semantics. Mean requires
both. Variance needs a suitable combined state and numerical care. Exact median
cannot generally be recovered from one median per partition. Chunked arrays
provide a small local setting in which to prove the same algebraic distinction
before reasoning about a distributed aggregation plan.

## Complete worked source

This is a complete editable worked program for the declared prepared runtime. It uses bounded local fixtures and does not install packages or start distributed services.

```python
import math

import pyarrow as pa
import pyarrow.compute as pc

values = pa.chunked_array([[4, None, 8], [2, 6]], type=pa.int64())
assert len(values) == 5 and values.num_chunks == 2
assert pc.sum(values).as_py() == 20 and pc.mean(values).as_py() == 5
assert pc.mean(values.combine_chunks()).as_py() == 5
unequal = pa.chunked_array([[4], [None, 8, 2, 6]], type=pa.int64())
wrong_mean = sum(pc.mean(chunk).as_py() for chunk in unequal.chunks) / 2
assert math.isclose(wrong_mean, 14 / 3) and not math.isclose(wrong_mean, 5)
sums = [pc.sum(chunk).as_py() for chunk in unequal.chunks]
counts = [len(chunk) - chunk.null_count for chunk in unequal.chunks]
assert sum(sums) / sum(counts) == 5
mask = pc.greater(values, 5)
selected = pc.filter(values, mask)
uncertain = pc.filter(values, mask, null_selection_behavior="emit_null")
assert selected.to_pylist() == [8, 6]
assert uncertain.to_pylist() == [None, 8, 6]
assert pc.mean(pc.fill_null(values, 0)).as_py() == 4
print("Observed mean:", 5, "incorrect chunk mean:", wrong_mean)
print("Selected:", selected.to_pylist(), "retaining unknown membership:", uncertain.to_pylist())
print("Zero-filled mean changes the denominator:", 4)
```

## Primary references

- [Arrow compute functions](https://arrow.apache.org/docs/python/compute.html)
- [Arrow filter null policy](https://arrow.apache.org/docs/python/generated/pyarrow.compute.filter.html)
