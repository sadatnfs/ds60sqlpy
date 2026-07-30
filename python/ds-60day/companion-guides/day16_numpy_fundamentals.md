# Day 16 — NumPy Arrays, Vectorization, and Broadcasting

**Level:** Intermediate

NumPy stores homogeneous values in an `ndarray` and applies compiled operations
across whole arrays. Shape and dtype are part of every array's contract.

## Learning objectives

By the end of this lesson, you can:

- create arrays and inspect `shape`, `ndim`, and `dtype`;
- interpret an aggregation's `axis`;
- replace element-by-element Python loops with array expressions;
- predict valid broadcasting from trailing dimensions;
- demonstrate when slicing returns a view versus an independent copy.

## Prerequisites

Complete the Python foundations through Day 15 (`python-15`). The standard setup
installs the `data` dependency group containing NumPy.

## Vocabulary and mental model

- **Array:** homogeneous n-dimensional container.
- **Shape:** tuple of lengths along each dimension.
- **Dtype:** fixed representation used for every element.
- **Vectorization:** express work as array operations rather than Python-level
  element loops.
- **Axis:** dimension removed or transformed by an operation.
- **Broadcasting:** align compatible shapes without explicitly copying values.
- **View:** another array sharing underlying memory; **copy:** independent data.

For shape `(rows, columns)`, `axis=0` combines rows and returns one result per
column; `axis=1` combines columns and returns one result per row.

## Worked example

```python
import numpy as np

scores = np.array([[10.0, 20.0, 30.0], [15.0, 25.0, 35.0]])
column_means = scores.mean(axis=0)
centered = scores - column_means

assert centered.shape == scores.shape
assert np.allclose(centered.mean(axis=0), 0.0)
```

`column_means` has shape `(3,)`, compatible with the matrix's trailing
dimension, so it broadcasts across both rows.

## Exercises and progressive hints

1. Create a `1000 x 1000` matrix and compute row means without Python loops.
   **Hint:** verify the result has 1,000 values and choose the axis that removes
   columns.
2. Normalize each column to `[0, 1]` with broadcasting. **Hint:** compute
   column-wise minima and ranges separately; decide what a zero-range column
   should become.
3. Show how changing a slice can change its source, then prevent that behavior.
   **Hint:** check `np.shares_memory` and compare a basic slice with `.copy()`.

Use a seeded generator (`np.random.default_rng(42)`) if you generate data so
results remain deterministic.

### Additional mastery practice

Reason about shape, axis, dtype, and view/copy semantics before applying vectorized operations. Verify results with small arrays.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** Predict the shape and values of a `(2, 3)` array plus a `(3,)` array, then explain broadcasting alignment.
   **Progressive hint:** Broadcasting compares dimensions from the right.
5. **Tracing:** Trace `array.sum(axis=0)` and `array.sum(axis=1)` by naming which dimension is removed and what each output element represents.
   **Progressive hint:** The named axis is the dimension reduced.
6. **Implementation:** Implement column standardization that leaves zero-variance columns as zeros instead of dividing by zero.
   **Progressive hint:** Replace a zero standard deviation with a safe denominator.
7. **Debugging:** Repair code that mutates an original array through a slice when an independent working array was intended.
   **Progressive hint:** Use `.copy()` at the ownership boundary.
8. **Edge case and explanation:** Demonstrate integer overflow with a small integer dtype and prevent it by selecting a wider dtype before arithmetic.
   **Progressive hint:** The array dtype, not Python's unbounded integer behavior, controls storage.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- What shapes can broadcast with an array shaped `(1000, 4)`?
- What does `mean(axis=1)` return for a two-dimensional array?
- Why can adding a float to an integer array produce a float result?
- When is a view useful, and when is it dangerous?

Expected behavior: row means have shape `(1000,)`, normalized non-constant
columns have minimum 0 and maximum 1, and copy mutation leaves the source alone.

## Common pitfalls and diagnosis

- **Broadcasting error:** write both shapes right-aligned and compare dimensions
  from the end; each pair must match or contain `1`.
- **Wrong-shaped aggregation:** print the input/result shapes and re-evaluate
  the axis.
- **Integer values truncate on assignment:** inspect `dtype` before assigning a
  float into an integer array.
- **Division by zero during scaling:** detect constant columns before dividing.
- **Source data changes through a slice:** use `.copy()` at the boundary where
  independence is required.

## Continue

- [Open the learner notebook](../notebooks/day16_numpy_fundamentals.ipynb)
- [Check the separate solution](../solutions/day16_numpy_fundamentals/day16_solutions.md)
- [Next: Day 17 — pandas fundamentals](day17_pandas_intro.md)
