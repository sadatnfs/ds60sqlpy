# Geometry, derivatives and the meaning of a fit

Tutorial ID: `statistics-learning-001`. Prerequisites: `statistics-002`, `statistics-003`. Complete program: [learning_01.py](examples/learning_01.py).

## Key terms

- **Design matrix:** The table with one row per observation and one column per coefficient, here an intercept column and the predictor, whose product with the coefficients gives the predictions.
- **Gradient:** The vector of partial derivatives of the loss, one local slope per coefficient direction; it is zero at the least-squares solution.
- **Hessian:** The matrix of second derivatives; for squared loss it equals \(X^{\mathsf T}X\), which is positive semidefinite, so the loss surface is convex.
- **Finite-difference check:** A comparison of the analytic gradient with small perturbations of the scalar objective, which confirms the derivative only near the chosen point.
- **Singular value:** The scale of the design along one direction; a tiny singular value marks a direction where small data changes produce large coefficient changes.

## Build the objects before multiplying them

Three observations have predictor values 0,1,2 and outcomes 1,2,4. A scalar is one number. A vector stores an ordered collection of numbers; here the outcome vector has three entries. A matrix arranges numbers by row and column. Put an intercept and predictor in a three-by-two design matrix:

\[
X=\begin{pmatrix}1&0\\1&1\\1&2\end{pmatrix},\quad
y=\begin{pmatrix}1\\2\\4\end{pmatrix},\quad
\beta=\begin{pmatrix}\beta_0\\\beta_1\end{pmatrix}.
\]

Each row's dot product with beta is a prediction: multiply corresponding entries and add. Therefore \(X\beta\) has three entries, while \(X^{\mathsf T}r\) has two. These dimensions are a useful check before interpreting a result. A broadcast that creates a three-by-three array from two length-three quantities can silently turn one error per observation into nine unrelated differences.

## Derive the closest prediction

Let \(L(\beta)=\frac12\sum_i(x_i^{\mathsf T}\beta-y_i)^2\). The chain rule differentiates the outer square, then the inner linear expression. The resulting gradient and Hessian are

\[
\nabla L=X^{\mathsf T}(X\beta-y),\qquad H=X^{\mathsf T}X.
\]

The gradient is the local slope in each coefficient direction. The Hessian describes how those slopes change. For any vector \(v\), \(v^{\mathsf T}Hv=\lVert Xv\rVert^2\ge0\), so the squared-loss surface is convex. Full column rank makes it strictly convex and the coefficient solution unique.

Solving gives \(\widehat\beta=(5/6,3/2)\). Residuals are \((1/6,-1/3,1/6)\), orthogonal to both columns. The program checks the coefficients and orthogonality using a least-squares solver. The all-ones column explains why residuals sum to zero. Without an intercept that identity need not hold.

## Check a derivative independently

The code compares the analytic gradient at a chosen point with small finite differences of the scalar objective. Agreement checks this derivative locally. Finite differences themselves can be unreliable near discontinuities, with poorly conditioned calculations or when subtraction cancellation dominates. Use more than one perturbation size for difficult functions rather than increasing tolerance until a check passes.

For a positive-definite quadratic, gradient descent is stable with a positive step smaller than \(2/\lambda_{\max}(H)\). The example compares a step of \(1/\lambda_{\max}\) with \(2.2/\lambda_{\max}\). The larger step diverges along the steepest direction. A converged optimizer still says nothing about whether the chosen outcome or sampling model is scientifically appropriate.

## Redundant columns and numerical sensitivity

Adding twice the predictor as another column does not add an independent direction. Predictions can remain uniquely determined even when coefficients are not. A tiny singular value indicates a direction in which small data changes create large coefficient changes. Ridge changes the estimation problem by shrinking such directions; QR/SVD improves numerical solution without inventing missing information.

**Answered discussion: Does the fitted line prove a population effect?** No. Its geometry holds without normality. An uncertainty interval adds assumptions about sampling and errors; a causal interpretation adds identification assumptions. Keep these layers separate when explaining a coefficient.

## Worked example: step size against the largest eigenvalue

The three-point regression from `examples/learning_01.py` has Hessian eigenvalues that differ by almost a factor of nine, which is enough to make the step-size rule visible. This snippet runs plain gradient descent at three multiples of \(1/\lambda_{\max}\) and records the distance to the least-squares solution.

```python
import numpy as np

x = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
y = np.array([1.0, 2.0, 4.0])
beta = np.linalg.lstsq(x, y, rcond=None)[0]
lam = np.linalg.eigvalsh(x.T @ x)
print("eigenvalues:", np.round(lam, 3))
for factor in (1.0, 1.9, 2.2):
    b, path = np.zeros(2), []
    for step in range(1, 31):
        b -= factor / lam[-1] * (x.T @ (x @ b - y))
        if step in (1, 5, 30):
            path.append(round(float(np.linalg.norm(b - beta)), 3))
    print(f"step {factor}/lambda_max -> distance after 1, 5, 30: {path}")
```

```text
eigenvalues: [0.838 7.162]
step 1.0/lambda_max -> distance after 1, 5, 30: [0.178, 0.108, 0.005]
step 1.9/lambda_max -> distance after 1, 5, 30: [1.542, 1.008, 0.072]
step 2.2/lambda_max -> distance after 1, 5, 30: [2.05, 4.241, 404.518]
```

The eigenvalues are 0.838 and 7.162. At one over the largest, the distance shrinks from 0.178 after one step to 0.005 after thirty. At 1.9 the iterate still converges, but it overshoots on the steep direction: starting 1.716 from the solution, it is still 1.542 away after one step and 0.072 away after thirty. At 2.2 the steep direction is multiplied by a factor larger than one in magnitude each iteration, and the distance grows to 404.518. The slow direction, governed by 0.838, sets how many steps a stable rate needs; the fast direction, governed by 7.162, sets how large the rate may be. Their ratio, the condition number, is why badly scaled features make first-order optimizers crawl.

## Worked example: a redundant column and a nearly redundant one

Append twice the predictor as a third column, then nudge one entry of that column by \(10^{-4}\) so that it is only nearly redundant.

```python
import numpy as np

np.set_printoptions(suppress=True)

x = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
y = np.array([1.0, 2.0, 4.0])
redundant = np.column_stack([x, 2 * x[:, 1]])
coef = np.linalg.lstsq(redundant, y, rcond=None)[0]
print("singular values:", np.round(np.linalg.svd(redundant, compute_uv=False), 4))
print("min-norm coefficients:", np.round(coef, 3), "predictions:", np.round(redundant @ coef, 3))
near = redundant.copy()
near[:, 2] += [0.0, 1e-4, 0.0]
for shift in (0.0, 0.01):
    c = np.linalg.lstsq(near, y + [0, shift, 0], rcond=None)[0]
    print(f"y[1] shifted by {shift}: coefficients {np.round(c, 1)}")
```

```text
singular values: [5.185  1.0564 0.    ]
min-norm coefficients: [0.833 0.3   0.6  ] predictions: [0.833 2.333 3.833]
y[1] shifted by 0.0: coefficients [    1.  10001.5 -5000. ]
y[1] shifted by 0.01: coefficients [    1.   9801.5 -4900. ]
```

With an exact duplicate, the third singular value is 0, and the solver returns the minimum-norm answer: slope weights 0.3 and 0.6, whose combination \(0.3+2(0.6)=1.5\) reproduces the original slope and the same predictions 0.833, 2.333, 3.833. Any split along the null direction fits equally well, so the individual numbers carry no meaning. After the tiny nudge the matrix has full rank, and the solver obeys it: coefficients near 10001.5 and -5000. Moving one outcome by 0.01 shifts them to 9801.5 and -4900, a change of 200 from a perturbation smaller than any plausible measurement error. Predictions are still stable; coefficient stories are not.

## Diagnostics for a fit you plan to interpret

Compute the singular values of the design and their ratio before reading any coefficient. Standardize features before gradient methods so one direction does not dictate the step. Verify an analytic gradient at more than one point and more than one perturbation size. When coefficients swing under small edits to the data, report predictions or identifiable combinations instead of individual slopes, or change the estimation problem deliberately with a penalty.

Continue to [likelihood and intervals](02-likelihood-and-inference.md). API reference: [NumPy least squares](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html).
