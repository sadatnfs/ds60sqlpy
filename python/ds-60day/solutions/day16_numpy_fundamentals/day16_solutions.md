# Day 16 Solutions: NumPy Arrays, Vectorization, and Broadcasting

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting**. Predict each named
result before comparing your attempt with its matching assertions.

A NumPy array is a rectangular, usually homogeneous block of values.
Its `shape` states the length of each dimension, its `ndim` counts
dimensions, and its `dtype` controls representation and supported
numeric behavior. Unlike a nested Python list, an array supports
elementwise operations and axis-aware reductions.

Vectorization expresses work as array operations implemented in
optimized compiled loops. Broadcasting compares shapes from the right
and virtually expands dimensions of length one or missing leading
dimensions. It avoids manual loops, but a broadcastable expression can
still be semantically wrong; always state what each axis represents.

### Vocabulary used in the worked answers

- **array:** a multidimensional homogeneous data container.
- **shape:** the length of every array dimension.
- **dtype:** the stored scalar representation, such as `int64` or `float64`.
- **axis:** a dimension along which an operation is applied.
- **vectorization:** expressing elementwise work as array operations.
- **broadcasting:** NumPy's rule for combining compatible unequal shapes.

### How to compare an answer

For this lesson's **NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1-3: Worked answers

### Exercise 1: worked answer

**Learner contract:** Create a 3×4 array containing integers 0 through 11, then compute row sums, column means, and the maximum of each row. **Expected behavior:** shapes are `(3, 4)`, `(3,)`, `(4,)`, and `(3,)` for the original and three results. **Constraint:** use vectorized reductions with explicit axes, not Python loops. **Verify:** assert both shapes and exact values.

**Reasoning:** `np.arange(12).reshape(3, 4)` lays out 0 to 11 row by row, so row 0 is `[0, 1, 2, 3]`. The `axis` argument names the dimension that disappears: `sum(axis=1)` collapses the four columns of each row into one total, giving shape `(3,)` and the values `[6, 22, 38]`, while `mean(axis=0)` collapses the three rows of each column, giving shape `(4,)`. Comparing `.tolist()` results checks plain Python values, independent of NumPy's display format. Mixing up the axis is the usual error, and checking the result shape catches it immediately.

```python
import numpy as np

array = np.arange(12).reshape(3, 4)
row_sums = array.sum(axis=1)
column_means = array.mean(axis=0)
row_maximums = array.max(axis=1)

assert array.shape == (3, 4)
assert row_sums.tolist() == [6, 22, 38]
assert column_means.tolist() == [4.0, 5.0, 6.0, 7.0]
assert row_maximums.tolist() == [3, 7, 11]
```

### Exercise 2: worked answer

**Learner contract:** Generate two deterministic arrays with `np.random.default_rng(42)`, perform elementwise addition/multiplication, matrix multiplication where shapes permit, and boolean-mask selection. **Constraints:** write the shape equation before `@` and do not use the legacy global random state. **Verify:** rerunning from a fresh kernel produces identical arrays and results.

**Reasoning:** `np.random.default_rng(42)` creates an independent generator whose sequence depends only on the seed, so recreating it reproduces the same arrays, unlike the legacy global `np.random.seed`, which any other code can disturb. Elementwise `+` and `*` need equal or broadcastable shapes, while `@` follows the matrix rule `(2, 3) @ (3, 2) -> (2, 2)`: the inner dimensions must match. Writing that shape equation first prevents the common `ValueError` from applying `@` to two `(2, 3)` arrays. A Boolean mask such as `left >= 5` collects the matching elements into a flat 1-D array, whatever the original shape.

```python
import numpy as np

rng = np.random.default_rng(42)
left = rng.integers(0, 10, size=(2, 3))
right = rng.integers(0, 10, size=(2, 3))
matrix = rng.integers(0, 5, size=(3, 2))

assert (left + right).shape == (2, 3)
assert (left * right).shape == (2, 3)
assert (left @ matrix).shape == (2, 2)
selected = left[left >= 5]
assert selected.ndim == 1
```

Recreating the generator with seed 42 reproduces the fixture.

### Exercise 3: worked answer

**Learner contract:** Demonstrate broadcasting by standardizing each column of a small 2-D array. **Expected behavior:** each standardized column has mean approximately 0 and standard deviation approximately 1. **Constraints:** keep means/stds as `(columns,)`, reject zero-standard-deviation columns, and assert the final shape equals the input shape. **Verify:** Assert output shape equals input shape, nonconstant columns have mean near zero and standard deviation near one, and zero-variance input raises or follows the written policy.

**Reasoning:** `values.mean(axis=0)` has shape `(2,)`, one mean per column, and broadcasting lines it up with the `(3, 2)` array from the right, so each column is centered with its own mean and then scaled by its own standard deviation. A constant column has standard deviation 0, and dividing by it would produce `NaN` values, so the function rejects that case explicitly. `np.allclose` is used for the mean and standard-deviation checks because floating-point results are close to, but not exactly, 0 and 1.

```python
import numpy as np


def standardize_columns(values: np.ndarray) -> np.ndarray:
    means = values.mean(axis=0)
    standard_deviations = values.std(axis=0)
    if np.any(standard_deviations == 0):
        raise ValueError("every column must vary")
    return (values - means) / standard_deviations


values = np.array([[1.0, 10.0], [2.0, 20.0], [3.0, 30.0]])
standardized = standardize_columns(values)
assert standardized.shape == values.shape
assert np.allclose(standardized.mean(axis=0), 0)
assert np.allclose(standardized.std(axis=0), 1)
```

## Exercises 4-8: Expanded mastery answers

### Exercise 4: answer contract

**Learner contract:** **Prediction:** Predict the shape and values of a `(2, 3)` array plus a `(3,)` array, then explain broadcasting alignment. **Progressive hint:** Broadcasting compares dimensions from the right. **Verify:** Assert the `(2, 3) + (3,)` result shape and exact values; write which right-aligned dimension proves the broadcast is valid.

**Reasoning:** Broadcasting compares shapes from the right: `(2, 3)` and `(3,)` agree on the last dimension, 3, and the missing leading dimension of the 1-D array is treated as 1 and stretched to 2. The offset row is therefore added to every row of the matrix, giving `[[101, 202, 303], [110, 220, 330]]` in the shared implementation for Exercises 4-5. An offset of shape `(2,)` would fail, because 2 does not match the trailing 3; reshaping it to `(2, 1)` would apply one offset per row instead. Writing both shapes right-aligned before running is a reliable way to predict the result.

### Exercise 5: answer contract

**Learner contract:** **Tracing:** Trace `array.sum(axis=0)` and `array.sum(axis=1)` by naming which dimension is removed and what each output element represents. **Progressive hint:** The named axis is the dimension reduced. **Verify:** Calculate both reductions by hand and assert `axis=0` removes rows into one value per column while `axis=1` removes columns into one per row.

**Reasoning:** The axis you name is the one that is removed. For the `(2, 3)` matrix, `sum(axis=0)` adds down each column and returns three values, one per column (`[11, 22, 33]`), while `sum(axis=1)` adds across each row and returns two values, one per row (`[6, 60]`). Thinking "axis 0 means rows" leads people to expect row totals from `axis=0`; thinking "axis 0 is the dimension that disappears" gives the right answer. The shared implementation for Exercises 4-5 asserts both reductions computed by hand.

### Exercise 6: answer contract

**Learner contract:** **Implementation:** Implement column standardization that leaves zero-variance columns as zeros instead of dividing by zero. **Progressive hint:** Replace a zero standard deviation with a safe denominator. **Verify:** Assert nonconstant columns standardize near mean 0/std 1, zero-variance columns become exactly zeros, and shape/dtype policy is preserved.

**Reasoning:** Replacing a zero standard deviation with 1 before dividing leaves the centered values unchanged, and a constant column's centered values are all 0, so it becomes exactly zeros instead of `NaN`. Converting to `float64` first avoids integer surprises and keeps the z-scores precise. The shared implementation for Exercises 6-8 asserts zeros for the constant column and mean 0 with standard deviation 1 for the varying one. Returning zeros is a policy decision; when a constant feature signals bad data, raising, as the third worked answer does, is the stricter alternative.

### Exercise 7: answer contract

**Learner contract:** **Debugging:** Repair code that mutates an original array through a slice when an independent working array was intended. **Progressive hint:** Use `.copy()` at the ownership boundary. **Verify:** Record `np.shares_memory` before repair, mutate the working slice, and assert `.copy()` keeps the original array unchanged.

**Reasoning:** Basic slicing such as `sample[:, :1]` returns a view that shares memory with the original array, so writing through the slice changes the original; `np.shares_memory` reports `True`. Calling `.copy()` where the working array is created gives it its own memory, so later writes leave the original untouched. The shared implementation for Exercises 6-8 checks both `np.shares_memory` results and that `sample[0, 0]` is still 1 after the copy is overwritten. Boolean and integer-array indexing always return copies, which is a second rule worth remembering.

### Exercise 8: answer contract

**Learner contract:** **Edge case and explanation:** Demonstrate integer overflow with a small integer dtype and prevent it by selecting a wider dtype before arithmetic. **Progressive hint:** The array dtype, not Python's unbounded integer behavior, controls storage. **Verify:** Show the small-dtype wrapped result, repeat after casting to a sufficiently wide dtype, and assert the widened arithmetic matches Python's expected integer.

**Reasoning:** A NumPy array stores numbers in a fixed-size dtype, unlike Python's unbounded integers: `int8` holds -128 to 127, so 120 + 20 wraps around to -116 without any error. Converting to a wider dtype such as `int64` before the arithmetic keeps the true value, 140, and the shared implementation for Exercises 6-8 asserts both results. NumPy 2 also raises `OverflowError` when a Python integer that cannot fit, such as 200, is combined with an `int8` array. Choose the dtype from the range of values you expect, not from memory savings alone.

## Expanded mastery lab solutions

Reason about shape, axis, dtype, and view/copy semantics before applying vectorized operations. Verify results with small arrays.

### Shared implementation for Exercises 4-5: Shape and axes

```python
import numpy as np

matrix = np.array([[1, 2, 3], [10, 20, 30]])
offset = np.array([100, 200, 300])
assert (matrix + offset).tolist() == [[101, 202, 303], [110, 220, 330]]
assert matrix.sum(axis=0).tolist() == [11, 22, 33]  # Reduce rows.
assert matrix.sum(axis=1).tolist() == [6, 60]  # Reduce columns.
```

### Shared implementation for Exercises 6-8: Stable standardization, copies, and dtype choice

```python
def standardize_columns(values: np.ndarray) -> np.ndarray:
    """Return float z-scores; constant columns become all zeros."""

    numeric = np.asarray(values, dtype=np.float64)
    means = numeric.mean(axis=0)
    standard_deviations = numeric.std(axis=0)
    safe_scale = np.where(standard_deviations == 0, 1.0, standard_deviations)
    return (numeric - means) / safe_scale


sample = np.array([[1, 5], [3, 5], [5, 5]])
standardized = standardize_columns(sample)
assert np.allclose(standardized[:, 1], 0)
assert np.isclose(standardized[:, 0].mean(), 0) and np.isclose(standardized[:, 0].std(), 1)

view = sample[:, :1]
assert np.shares_memory(view, sample)  # a basic slice is a view
working = sample[:, :1].copy()
assert not np.shares_memory(working, sample)
working[:] = -1
assert sample[0, 0] == 1  # Copy protects the original.

small = np.array([120], dtype=np.int8)
overflowed = small + np.array([20], dtype=np.int8)
wide = small.astype(np.int64) + 20
assert overflowed.tolist() == [-116]  # int8 wraps around silently
assert int(wide[0]) == 140
```
