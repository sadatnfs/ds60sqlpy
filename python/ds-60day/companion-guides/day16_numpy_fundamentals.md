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

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day16_numpy_fundamentals.md`, then open `python/ds-60day/notebooks/day16_numpy_fundamentals.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 16 — numpy arrays, vectorization, and broadcasting to practice NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **array:** a multidimensional homogeneous data container.
- **shape:** the length of every array dimension.
- **dtype:** the stored scalar representation, such as `int64` or `float64`.
- **axis:** a dimension along which an operation is applied.
- **vectorization:** expressing elementwise work as array operations.
- **broadcasting:** NumPy's rule for combining compatible unequal shapes.

### Syntax anatomy

For a shape `(rows, columns)` array, `values.mean(axis=0)` collapses the
row axis and returns one mean per column; `axis=1` collapses columns and
returns one mean per row. In `matrix - column_means`, shapes `(r, c)`
and `(c,)` align from the right, so the one-dimensional vector is used
across every row.

### Worked example 1 — Inspect shape before calculating

Give each dimension a meaning and compare axis reductions. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
import numpy as np

scores = np.array([[8, 6, 10], [4, 9, 8]])
{
    "shape": scores.shape,
    "per_column": scores.mean(axis=0).tolist(),
    "per_row": scores.mean(axis=1).tolist(),
}
```

**Expected observation**

```text
`{'shape': (2, 3), 'per_column': [6.0, 7.5, 9.0], 'per_row': [8.0, 7.0]}`.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Center every column through broadcasting

A length-three vector applies to the three columns of every row. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
column_means = scores.mean(axis=0)
centered = scores - column_means
(centered.tolist(), centered.mean(axis=0).round(10).tolist())
```

**Expected observation**

```text
The centered rows are displayed and every column mean is `[0.0, 0.0, 0.0]` up to floating-point precision.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Print `.shape`, `.dtype`, and a small slice before diagnosing an array calculation.
2. Name axis meanings in prose before choosing `axis=0` or `axis=1`.
3. When broadcasting fails, align shapes from the right and insert an explicit singleton dimension if needed.
4. Distinguish a view from a copy before mutating a slice.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** Use Python lists for small heterogeneous general-purpose data; use arrays for rectangular numeric computation.

**Boundary to remember:** Empty axes, integer overflow, NaN propagation, boolean-mask shape mismatch, and accidental view mutation need deliberate handling.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Create a 3×4 array containing integers 0 through 11, then compute row sums, column means, and the maximum of each row.
   **Expected behavior:** shapes are `(3, 4)`, `(3,)`, `(4,)`, and `(3,)` for the original and three results. **Constraint:** use vectorized reductions with explicit axes, not Python loops.
   **Verify:** assert both shapes and exact values.

2. Generate two deterministic arrays with `np.random.default_rng(42)`, perform elementwise addition/multiplication, matrix multiplication where shapes permit, and boolean-mask selection. **Constraints:** write the shape equation before `@` and do not use the legacy global random state.
   **Verify:** rerunning from a fresh kernel produces identical arrays and results.

3. Demonstrate broadcasting by standardizing each column of a small 2-D array.
   **Expected behavior:** each standardized column has mean approximately 0 and standard deviation approximately 1. **Constraints:** keep means/stds as `(columns,)`, reject zero-standard-deviation columns, and assert the final shape equals the input shape.
   **Verify:** Assert output shape equals input shape, nonconstant columns have mean near zero and standard deviation near one, and zero-variance input raises or follows the written policy.

### Additional mastery practice

Reason about shape, axis, dtype, and view/copy semantics before applying vectorized operations. Verify results with small arrays.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** Predict the shape and values of a `(2, 3)` array plus a `(3,)` array, then explain broadcasting alignment.
   **Progressive hint:** Broadcasting compares dimensions from the right.
   **Verify:** Assert the `(2, 3) + (3,)` result shape and exact values; write which right-aligned dimension proves the broadcast is valid.
5. **Tracing:** Trace `array.sum(axis=0)` and `array.sum(axis=1)` by naming which dimension is removed and what each output element represents.
   **Progressive hint:** The named axis is the dimension reduced.
   **Verify:** Calculate both reductions by hand and assert `axis=0` removes rows into one value per column while `axis=1` removes columns into one per row.
6. **Implementation:** Implement column standardization that leaves zero-variance columns as zeros instead of dividing by zero.
   **Progressive hint:** Replace a zero standard deviation with a safe denominator.
   **Verify:** Assert nonconstant columns standardize near mean 0/std 1, zero-variance columns become exactly zeros, and shape/dtype policy is preserved.
7. **Debugging:** Repair code that mutates an original array through a slice when an independent working array was intended.
   **Progressive hint:** Use `.copy()` at the ownership boundary.
   **Verify:** Record `np.shares_memory` before repair, mutate the working slice, and assert `.copy()` keeps the original array unchanged.
8. **Edge case and explanation:** Demonstrate integer overflow with a small integer dtype and prevent it by selecting a wider dtype before arithmetic.
   **Progressive hint:** The array dtype, not Python's unbounded integer behavior, controls storage.
   **Verify:** Show the small-dtype wrapped result, repeat after casting to a sufficiently wide dtype, and assert the widened arithmetic matches Python's expected integer.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-16`
(Day 16 — NumPy Arrays, Vectorization, and Broadcasting). Direct catalog prerequisites: `python-15`.
I have completed the direct prerequisites: `python-15`. Emphasize NumPy arrays, shapes, dtypes, vectorization, axes, and broadcasting.
Read `python/ds-60day/companion-guides/day16_numpy_fundamentals.md` and use the learner notebook
`python/ds-60day/notebooks/day16_numpy_fundamentals.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
