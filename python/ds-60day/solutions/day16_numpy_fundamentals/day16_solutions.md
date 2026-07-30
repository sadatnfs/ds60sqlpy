# Day 16 — Solutions: NumPy Fundamentals

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Create a `1000 x 1000` matrix and compute row means without Python loops. **Hint:** verify the result has 1,000 values and choose the axis that removes columns.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Normalize each column to `[0, 1]` with broadcasting. **Hint:** compute column-wise minima and ranges separately; decide what a zero-range column should become.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** Show how changing a slice can change its source, then prevent that behavior. **Hint:** check `np.shares_memory` and compare a basic slice with `.copy()`. Use a seeded generator (`np.random.default_rng(42)`) if you generate data so results remain deterministic.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Prediction

**Prompt:** Predict the shape and values of a `(2, 3)` array plus a `(3,)` array, then explain broadcasting alignment.

**Reasoning checkpoint:** Broadcasting compares dimensions from the right. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Tracing

**Prompt:** Trace `array.sum(axis=0)` and `array.sum(axis=1)` by naming which dimension is removed and what each output element represents.

**Reasoning checkpoint:** The named axis is the dimension reduced. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Implementation

**Prompt:** Implement column standardization that leaves zero-variance columns as zeros instead of dividing by zero.

**Reasoning checkpoint:** Replace a zero standard deviation with a safe denominator. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Debugging

**Prompt:** Repair code that mutates an original array through a slice when an independent working array was intended.

**Reasoning checkpoint:** Use `.copy()` at the ownership boundary. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Edge case and explanation

**Prompt:** Demonstrate integer overflow with a small integer dtype and prevent it by selecting a wider dtype before arithmetic.

**Reasoning checkpoint:** The array dtype, not Python's unbounded integer behavior, controls storage. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
