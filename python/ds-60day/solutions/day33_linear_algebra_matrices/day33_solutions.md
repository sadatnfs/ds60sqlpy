# Day 33 — Solutions: Linear Algebra & Matrices for ML Intuition

We implement the normal equation (closed-form least squares), add an intercept, and compare to scikit-learn. We also discuss numerical stability and when to prefer iterative methods.

Contents
- Exercise 1: Add an intercept column and recompute w
- Exercise 2: Compare closed-form solution vs sklearn LinearRegression
- Exercise 3: When normal equation is unstable; why gradient/iterative methods are preferred

---

Setup and synthetic data
```python
import numpy as np
rng = np.random.default_rng(0)

n, d = 200, 3
X = rng.normal(size=(n, d))
true_w = np.array([2.0, -1.0, 0.5])
y = X @ true_w + rng.normal(scale=0.5, size=n)
```

Exercise 1 — Add intercept and recompute w
```python
# Add a column of ones for intercept
X1 = np.c_[np.ones((n, 1)), X]   # shape (n, d+1)

# Normal equation with pseudo-inverse for stability
w_hat = np.linalg.pinv(X1.T @ X1) @ X1.T @ y
w_hat
```
Line-by-line
- np.c_ concatenates a column of 1s to X to model an intercept term
- pinv (Moore–Penrose) is numerically safer than explicit inverse

---

Exercise 2 — Compare to sklearn LinearRegression
```python
from sklearn.linear_model import LinearRegression

lr = LinearRegression(fit_intercept=True)
lr.fit(X, y)

w0 = lr.intercept_
w  = lr.coef_

w0, w
```
Notes
- LinearRegression with fit_intercept=True estimates intercept internally
- Expect close agreement between (w0, w) and the closed-form solution above

---

Exercise 3 — Stability and iterative methods
- Normal equation inverts X^T X (or solves a system); if X has multicollinearity or large condition number, numerical errors grow
- Use np.linalg.lstsq or pinv to mitigate; better yet, rely on QR/SVD inside libraries
- For large n,d or online learning, gradient-based solvers (SGD, coordinate descent) scale better (avoid O(d^3) inversion)

Takeaways
- Prefer library solvers (sklearn) that use robust decompositions
- Add regularization (Ridge/Lasso) when features are collinear or high-dimensional
