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
