# Day 16 — Solutions: NumPy Fundamentals

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting**.

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

### Reference pattern 1 — Inspect shape before calculating

Give each dimension a meaning and compare axis reductions.

```python
import numpy as np

scores = np.array([[8, 6, 10], [4, 9, 8]])
{
    "shape": scores.shape,
    "per_column": scores.mean(axis=0).tolist(),
    "per_row": scores.mean(axis=1).tolist(),
}
```

**Expected observation:** `{'shape': (2, 3), 'per_column': [6.0, 7.5, 9.0], 'per_row': [8.0, 7.0]}`.

### Reference pattern 2 — Center every column through broadcasting

A length-three vector applies to the three columns of every row.

```python
column_means = scores.mean(axis=0)
centered = scores - column_means
(centered.tolist(), centered.mean(axis=0).round(10).tolist())
```

**Expected observation:** The centered rows are displayed and every column mean is `[0.0, 0.0, 0.0]` up to floating-point precision.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Create a 3×4 array containing integers 0 through 11, then compute row sums, column means, and the maximum of each row. **Expected behavior:** shapes are `(3, 4)`, `(3,)`, `(4,)`, and `(3,)` for the original and three results. **Constraint:** use vectorized reductions with explicit axes, not Python loops. **Verify:** assert both shapes and exact values.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Python lists for small heterogeneous general-purpose data; use arrays for rectangular numeric computation.

**Edge case:** Empty axes, integer overflow, NaN propagation, boolean-mask shape mismatch, and accidental view mutation need deliberate handling.

**Solution evidence to inspect:** assert both shapes and exact values.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Generate two deterministic arrays with `np.random.default_rng(42)`, perform elementwise addition/multiplication, matrix multiplication where shapes permit, and boolean-mask selection. **Constraints:** write the shape equation before `@` and do not use the legacy global random state. **Verify:** rerunning from a fresh kernel produces identical arrays and results.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Python lists for small heterogeneous general-purpose data; use arrays for rectangular numeric computation.

**Edge case:** Empty axes, integer overflow, NaN propagation, boolean-mask shape mismatch, and accidental view mutation need deliberate handling.

**Solution evidence to inspect:** rerunning from a fresh kernel produces identical arrays and results.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** Demonstrate broadcasting by standardizing each column of a small 2-D array. **Expected behavior:** each standardized column has mean approximately 0 and standard deviation approximately 1. **Constraints:** keep means/stds as `(columns,)`, reject zero-standard-deviation columns, and assert the final shape equals the input shape. **Verify:** Assert output shape equals input shape, nonconstant columns have mean near zero and standard deviation near one, and zero-variance input raises or follows the written policy.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Python lists for small heterogeneous general-purpose data; use arrays for rectangular numeric computation.

**Edge case:** Empty axes, integer overflow, NaN propagation, boolean-mask shape mismatch, and accidental view mutation need deliberate handling.

**Solution evidence to inspect:** Assert output shape equals input shape, nonconstant columns have mean near zero and standard deviation near one, and zero-variance input raises or follows the written policy.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict the shape and values of a `(2, 3)` array plus a `(3,)` array, then explain broadcasting alignment. **Progressive hint:** Broadcasting compares dimensions from the right. **Verify:** Assert the `(2, 3) + (3,)` result shape and exact values; write which right-aligned dimension proves the broadcast is valid.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Python lists for small heterogeneous general-purpose data; use arrays for rectangular numeric computation.

**Edge case:** Empty axes, integer overflow, NaN propagation, boolean-mask shape mismatch, and accidental view mutation need deliberate handling.

**Solution evidence to inspect:** Assert the `(2, 3) + (3,)` result shape and exact values; write which right-aligned dimension proves the broadcast is valid.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace `array.sum(axis=0)` and `array.sum(axis=1)` by naming which dimension is removed and what each output element represents. **Progressive hint:** The named axis is the dimension reduced. **Verify:** Calculate both reductions by hand and assert `axis=0` removes rows into one value per column while `axis=1` removes columns into one per row.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Python lists for small heterogeneous general-purpose data; use arrays for rectangular numeric computation.

**Edge case:** Empty axes, integer overflow, NaN propagation, boolean-mask shape mismatch, and accidental view mutation need deliberate handling.

**Solution evidence to inspect:** Calculate both reductions by hand and assert `axis=0` removes rows into one value per column while `axis=1` removes columns into one per row.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement column standardization that leaves zero-variance columns as zeros instead of dividing by zero. **Progressive hint:** Replace a zero standard deviation with a safe denominator. **Verify:** Assert nonconstant columns standardize near mean 0/std 1, zero-variance columns become exactly zeros, and shape/dtype policy is preserved.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Python lists for small heterogeneous general-purpose data; use arrays for rectangular numeric computation.

**Edge case:** Empty axes, integer overflow, NaN propagation, boolean-mask shape mismatch, and accidental view mutation need deliberate handling.

**Solution evidence to inspect:** Assert nonconstant columns standardize near mean 0/std 1, zero-variance columns become exactly zeros, and shape/dtype policy is preserved.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair code that mutates an original array through a slice when an independent working array was intended. **Progressive hint:** Use `.copy()` at the ownership boundary. **Verify:** Record `np.shares_memory` before repair, mutate the working slice, and assert `.copy()` keeps the original array unchanged.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Python lists for small heterogeneous general-purpose data; use arrays for rectangular numeric computation.

**Edge case:** Empty axes, integer overflow, NaN propagation, boolean-mask shape mismatch, and accidental view mutation need deliberate handling.

**Solution evidence to inspect:** Record `np.shares_memory` before repair, mutate the working slice, and assert `.copy()` keeps the original array unchanged.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Demonstrate integer overflow with a small integer dtype and prevent it by selecting a wider dtype before arithmetic. **Progressive hint:** The array dtype, not Python's unbounded integer behavior, controls storage. **Verify:** Show the small-dtype wrapped result, repeat after casting to a sufficiently wide dtype, and assert the widened arithmetic matches Python's expected integer.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use Python lists for small heterogeneous general-purpose data; use arrays for rectangular numeric computation.

**Edge case:** Empty axes, integer overflow, NaN propagation, boolean-mask shape mismatch, and accidental view mutation need deliberate handling.

**Solution evidence to inspect:** Show the small-dtype wrapped result, repeat after casting to a sufficiently wide dtype, and assert the widened arithmetic matches Python's expected integer.
<!-- END BEGINNER SOLUTION REVIEW -->

We compute row-wise means without Python loops, normalize columns with broadcasting, and demonstrate view vs copy.

Contents
- Exercise 1: Row-wise means (no Python loops)
- Exercise 2: Column-wise 0–1 normalization with broadcasting
- Exercise 3: View vs copy demo

---

Exercise 1 — Row-wise means
```python
import numpy as np

A = np.arange(12).reshape(3, 4)
row_means = A.mean(axis=1)           # shape (3,)
assert np.allclose(row_means, np.array([1.5, 5.5, 9.5]))
```
Why: mean with axis=1 reduces columns, giving one mean per row.

---

Exercise 2 — Normalize each column to [0, 1]
```python
X = np.array([[1.0, 10.0], [3.0, 5.0], [5.0, 0.0]])
mins = X.min(axis=0)                 # shape (2,)
ranges = X.max(axis=0) - mins        # shape (2,)
X_norm = (X - mins) / ranges         # broadcasting subtracts mins row-wise
```
Notes
- Broadcasting aligns shapes right-to-left; (3,2) minus (2,) works.
- Beware division by zero when a column is constant; guard with `np.where(ranges==0, 1, ranges)`.

---

Exercise 3 — View vs copy
```python
Z = np.arange(12).reshape(3,4)
sub = Z[:, 1:3]      # view (shares memory)
sub[:] = -1          # writes into original
assert (Z[:, 1:3] == -1).all()

# Safe copy when isolating
Z2 = Z[:, 1:3].copy()
Z2[:] = 99
assert not (Z[:, 1:3] == 99).any()
```
Takeaway
- Slices are usually views; use .copy() when you intend independence.

---

## Expanded mastery lab solutions

Reason about shape, axis, dtype, and view/copy semantics before applying vectorized operations. Verify results with small arrays.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Shape and axes

```python
import numpy as np

matrix = np.array([[1, 2, 3], [10, 20, 30]])
offset = np.array([100, 200, 300])
assert (matrix + offset).tolist() == [[101, 202, 303], [110, 220, 330]]
assert matrix.sum(axis=0).tolist() == [11, 22, 33]  # Reduce rows.
assert matrix.sum(axis=1).tolist() == [6, 60]       # Reduce columns.
```

### Practices 3–5 — Stable standardization, copies, and dtype choice

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
