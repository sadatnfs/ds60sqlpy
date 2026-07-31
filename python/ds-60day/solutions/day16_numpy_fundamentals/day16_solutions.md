# Day 16 — Solutions: NumPy Fundamentals

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

## Exercises 1–3 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Create a 3×4 array containing integers 0 through 11, then compute row sums, column means, and the maximum of each row. **Expected behavior:** shapes are `(3, 4)`, `(3,)`, `(4,)`, and `(3,)` for the original and three results. **Constraint:** use vectorized reductions with explicit axes, not Python loops. **Verify:** assert both shapes and exact values.

**Reasoning:** Implement this exact contract as written: Create a 3×4 array containing integers 0 through 11, then compute row sums, column means, and the maximum of each row. Expected behavior: shapes are `(3, 4)`, `(3,)`, `(4,)`, and `(3,)` for the original and three results. Constraint: use vectorized reductions with explicit axes, not Python loops. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert both shapes and exact values. That connects the answer to NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

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

**Verification evidence:** assert both shapes and exact values.

### Exercise 2 — worked answer

**Learner contract:** Generate two deterministic arrays with `np.random.default_rng(42)`, perform elementwise addition/multiplication, matrix multiplication where shapes permit, and boolean-mask selection. **Constraints:** write the shape equation before `@` and do not use the legacy global random state. **Verify:** rerunning from a fresh kernel produces identical arrays and results.

**Reasoning:** Implement this exact contract as written: Generate two deterministic arrays with `np.random.default_rng(42)`, perform elementwise addition/multiplication, matrix multiplication where shapes permit, and boolean-mask selection. Constraints: write the shape equation before `@` and do not use the legacy global random state. Keep the prompt's named data and constraints visible in the code, then establish this specific result: rerunning from a fresh kernel produces identical arrays and results. That connects the answer to NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

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

**Verification evidence:** rerunning from a fresh kernel produces identical arrays and results.

### Exercise 3 — worked answer

**Learner contract:** Demonstrate broadcasting by standardizing each column of a small 2-D array. **Expected behavior:** each standardized column has mean approximately 0 and standard deviation approximately 1. **Constraints:** keep means/stds as `(columns,)`, reject zero-standard-deviation columns, and assert the final shape equals the input shape. **Verify:** Assert output shape equals input shape, nonconstant columns have mean near zero and standard deviation near one, and zero-variance input raises or follows the written policy.

**Reasoning:** Implement this exact contract as written: Demonstrate broadcasting by standardizing each column of a small 2-D array. Expected behavior: each standardized column has mean approximately 0 and standard deviation approximately 1. Constraints: keep means/stds as `(columns,)`, reject zero-standard-deviation columns, and assert the final shape equals the input shape. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert output shape equals input shape, nonconstant columns have mean near zero and standard deviation near one, and zero-variance input raises or follows the written policy. That connects the answer to NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

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

**Verification evidence:** Assert output shape equals input shape, nonconstant columns have mean near zero and standard deviation near one, and zero-variance input raises or follows the written policy.

## Exercises 4–8 — Expanded mastery answers

### Exercise 4 — answer contract

**Learner contract:** **Prediction:** Predict the shape and values of a `(2, 3)` array plus a `(3,)` array, then explain broadcasting alignment. **Progressive hint:** Broadcasting compares dimensions from the right. **Verify:** Assert the `(2, 3) + (3,)` result shape and exact values; write which right-aligned dimension proves the broadcast is valid.

**Reasoning:** Predict this named state change before running it: Prediction: Predict the shape and values of a `(2, 3)` array plus a `(3,)` array, then explain broadcasting alignment. Progressive hint: Broadcasting compares dimensions from the right. Then compare the prediction with this proof target: Assert the `(2, 3) + (3,)` result shape and exact values; write which right-aligned dimension proves the broadcast is valid. This makes NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Assert the `(2, 3) + (3,)` result shape and exact values; write which right-aligned dimension proves the broadcast is valid.

### Exercise 5 — answer contract

**Learner contract:** **Tracing:** Trace `array.sum(axis=0)` and `array.sum(axis=1)` by naming which dimension is removed and what each output element represents. **Progressive hint:** The named axis is the dimension reduced. **Verify:** Calculate both reductions by hand and assert `axis=0` removes rows into one value per column while `axis=1` removes columns into one per row.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace `array.sum(axis=0)` and `array.sum(axis=1)` by naming which dimension is removed and what each output element represents. Progressive hint: The named axis is the dimension reduced. Record the named value, shape, label, or iterator position needed to establish: Calculate both reductions by hand and assert `axis=0` removes rows into one value per column while `axis=1` removes columns into one per row. The trace exposes NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting directly.

**Evidence to locate in the grouped implementation:** Calculate both reductions by hand and assert `axis=0` removes rows into one value per column while `axis=1` removes columns into one per row.

### Exercise 6 — answer contract

**Learner contract:** **Implementation:** Implement column standardization that leaves zero-variance columns as zeros instead of dividing by zero. **Progressive hint:** Replace a zero standard deviation with a safe denominator. **Verify:** Assert nonconstant columns standardize near mean 0/std 1, zero-variance columns become exactly zeros, and shape/dtype policy is preserved.

**Reasoning:** Implement this exact contract as written: Implementation: Implement column standardization that leaves zero-variance columns as zeros instead of dividing by zero. Progressive hint: Replace a zero standard deviation with a safe denominator. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert nonconstant columns standardize near mean 0/std 1, zero-variance columns become exactly zeros, and shape/dtype policy is preserved. That connects the answer to NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

**Evidence to locate in the grouped implementation:** Assert nonconstant columns standardize near mean 0/std 1, zero-variance columns become exactly zeros, and shape/dtype policy is preserved.

### Exercise 7 — answer contract

**Learner contract:** **Debugging:** Repair code that mutates an original array through a slice when an independent working array was intended. **Progressive hint:** Use `.copy()` at the ownership boundary. **Verify:** Record `np.shares_memory` before repair, mutate the working slice, and assert `.copy()` keeps the original array unchanged.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair code that mutates an original array through a slice when an independent working array was intended. Progressive hint: Use `.copy()` at the ownership boundary. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Record `np.shares_memory` before repair, mutate the working slice, and assert `.copy()` keeps the original array unchanged. The diagnosis depends on NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

**Evidence to locate in the grouped implementation:** Record `np.shares_memory` before repair, mutate the working slice, and assert `.copy()` keeps the original array unchanged.

### Exercise 8 — answer contract

**Learner contract:** **Edge case and explanation:** Demonstrate integer overflow with a small integer dtype and prevent it by selecting a wider dtype before arithmetic. **Progressive hint:** The array dtype, not Python's unbounded integer behavior, controls storage. **Verify:** Show the small-dtype wrapped result, repeat after casting to a sufficiently wide dtype, and assert the widened arithmetic matches Python's expected integer.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Demonstrate integer overflow with a small integer dtype and prevent it by selecting a wider dtype before arithmetic. Progressive hint: The array dtype, not Python's unbounded integer behavior, controls storage. Values below, at, and above the named boundary must produce the evidence Show the small-dtype wrapped result, repeat after casting to a sufficiently wide dtype, and assert the widened arithmetic matches Python's expected integer. Those cases show how NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting behaves at its edge.

**Evidence to locate in the grouped implementation:** Show the small-dtype wrapped result, repeat after casting to a sufficiently wide dtype, and assert the widened arithmetic matches Python's expected integer.

## Expanded mastery lab solutions

Reason about shape, axis, dtype, and view/copy semantics before applying vectorized operations. Verify results with small arrays.

### Shared implementation for Exercises 4–5 — Shape and axes

```python
import numpy as np

matrix = np.array([[1, 2, 3], [10, 20, 30]])
offset = np.array([100, 200, 300])
assert (matrix + offset).tolist() == [[101, 202, 303], [110, 220, 330]]
assert matrix.sum(axis=0).tolist() == [11, 22, 33]  # Reduce rows.
assert matrix.sum(axis=1).tolist() == [6, 60]       # Reduce columns.
```

### Shared implementation for Exercises 6–8 — Stable standardization, copies, and dtype choice

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

working = sample[:, :1].copy()
working[:] = -1
assert sample[0, 0] == 1       # Copy protects the original.

small = np.array([120], dtype=np.int8)
overflowed = small + np.array([20], dtype=np.int8)
wide = small.astype(np.int64) + 20
assert int(overflowed[0]) != 140
assert int(wide[0]) == 140
```
