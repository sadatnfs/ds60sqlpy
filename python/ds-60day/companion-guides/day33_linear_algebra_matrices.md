# Day 33 — Linear Algebra for Data Science (Companion Guide)

## Learning objectives
- Work with vectors, matrices, norms, dot products
- Understand matrix multiplication, projections, and orthogonality
- Decompositions: SVD intuition and applications

## Why this matters
Many ML algorithms are linear algebra under the hood. Geometric intuition improves modeling decisions.

## Core concepts and examples
### Dot product and norms
```python
import numpy as np
x = np.array([1,2,3]); y = np.array([4,5,6])
x.dot(y); np.linalg.norm(x)
```

### Matrix multiply and solve
```python
A = np.array([[2,1],[1,3]])
b = np.array([1,0])
x = np.linalg.solve(A,b)
```

### SVD
```python
U, S, VT = np.linalg.svd(A, full_matrices=False)
```

## Common pitfalls
- Confusing element-wise with matrix multiply (`*` vs `@`)
- Solving via explicit inverse; prefer `solve`

## Practice exercises
1) Project a vector onto another and compute residual
2) Low-rank approximation with top-k singular values
3) Solve a least squares problem and compare residuals

## Further reading
- LA review: https://numpy.org/doc/stable/reference/routines.linalg.html
- SVD intuition: https://www.uw.edu/~swang/files/teaching/SVD-intuition.pdf
