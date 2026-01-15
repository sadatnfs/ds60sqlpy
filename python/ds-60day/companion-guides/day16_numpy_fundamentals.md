# Day 16 — NumPy Fundamentals: Arrays, Vectorization, Broadcasting (Companion Guide)

## Learning objectives
- Create and manipulate ndarrays; understand shape, dtype, and strides
- Replace Python loops with vectorized array operations for speed and clarity
- Use broadcasting rules to combine arrays of different but compatible shapes
- Distinguish views vs copies; avoid subtle bugs when slicing

## Why this matters
NumPy is the foundation of scientific Python. Vectorized operations are orders of magnitude faster than Python loops and unlock idiomatic data science code. Broadcasting lets you express operations concisely without manual tiling.

## Mental models
- An ndarray = (buffer of bytes) + (dtype) + (shape) + (strides). Vectorization is fast because operations loop in C over contiguous memory, not in Python.
- Broadcasting = align shapes from right to left; a dimension of 1 can be stretched to match the other operand. Fails only when non‑singleton dimensions disagree.
- Slicing returns **views** (usually) that share the same memory. Writing into a view writes into the original.

## Core concepts and examples
### Creating arrays
```python
import numpy as np
np.array([1,2,3], dtype=np.int64)
np.arange(12).reshape(3,4)
np.linspace(0, 1, 5)      # 0. , 0.25, 0.5, 0.75, 1.
np.zeros((2,3)), np.ones((2,3)), np.full((2,3), 7)
```

### Vectorization vs Python loops
```python
x = np.arange(1_000_000)
# vectorized
x2 = x * 2
# Python loop (slow)
res = np.empty_like(x)
for i in range(len(x)):
    res[i] = x[i] * 2
```
Prefer vectorized ops; they are clearer and drastically faster.

### Broadcasting rules
Right-align shapes; compare each dimension from right to left. A dimension is compatible when equal or one of them is 1.
```python
M = np.ones((3,3))
v = np.arange(3)       # shape (3,)
M + v                  # broadcast v across rows → (3,3)

A = np.ones((2,3,4))
b = np.arange(4)       # (4,)
A * b                  # broadcast along last axis → (2,3,4)
```

### Views vs copies
```python
Z = np.arange(12).reshape(3,4)
sub = Z[:, 1:3]      # view (no copy)
sub[:] = -1          # writes into Z!
Z
```
Force a copy when needed: `Z[:, 1:3].copy()`.

### Aggregations and axis
```python
Z = np.arange(12).reshape(3,4)
Z.sum()              # 66
Z.sum(axis=0)        # shape (4,)
Z.mean(axis=1)       # shape (3,)
```

## Performance tips
- Prefer contiguous arrays for kernels (C‑order by default). Use `np.ascontiguousarray` if needed.
- Vectorize; avoid Python loops in hot paths.
- Use ufuncs (`np.add`, `np.multiply`) and in‑place updates (`out=`) when appropriate.

## Common pitfalls
- Unexpected writes via views; `.copy()` when you intend isolation.
- Broadcasting mistakes when shapes are not aligned; print `.shape` and reason right‑to‑left.
- Mixing Python lists and arrays; convert early and keep everything ndarray.

## Practice exercises
1) Create a 1000×1000 array of random numbers and compute column‑wise z‑scores using broadcasting (subtract mean, divide by std).
2) Implement a rolling 3‑point average using strides or vectorized slicing (no Python loops).
3) Show a case where a slice changes the original; then fix it with `.copy()` and explain why.

## Stretch goals
- Implement a softmax function in a numerically stable way: subtract max before `exp`.
- Explore `np.einsum` to express matrix operations succinctly.

## Check your understanding
- Explain broadcasting with an example where shapes (2,1,3) and (1,4,1) combine.
- Why are vectorized operations faster than Python loops?
- When would you convert to contiguous arrays explicitly?

## Further reading
- NumPy quickstart: https://numpy.org/doc/stable/user/quickstart.html
- Broadcasting: https://numpy.org/doc/stable/user/basics.broadcasting.html
- Strides and memory: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.strides.html
