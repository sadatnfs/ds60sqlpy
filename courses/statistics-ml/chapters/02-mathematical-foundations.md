# 2. Mathematical Foundations

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-002`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

A dataset with n observations and p numerical features becomes a matrix X with n rows and p columns. A linear prediction is X beta: a weighted combination of feature columns. Least squares chooses the prediction vector closest to y in squared Euclidean distance. Geometry explains what software computes and why redundant columns create unstable coefficients.

Mathematical foundations are useful when they diagnose a real failure: a nearly singular covariance, exploding gradients, invalid probability integrals or a convergence assumption that does not hold. Distinguish the mathematical problem from the numerical algorithm. A unique theoretical answer can still be impossible to calculate accurately from rounded inputs.

## Methods, mechanisms, and limits

### stat-02-01

**Linear algebra**

Represent a linear transformation as matrix multiplication and track dimensions explicitly. If X is n by p, beta must have length p. Dimension checks catch many silent broadcasting errors before model interpretation begins.

### stat-02-02

**Vector spaces and projections**

Least-squares fitted values project y onto the column space of X. The residual is orthogonal to every fitted direction. This geometric property holds even when several coefficient vectors generate the same projection.

### stat-02-03

**Matrix rank**

Rank counts linearly independent columns or rows. Full column rank gives unique ordinary least-squares coefficients; duplicate categories plus an intercept violate it. Inspect singular values rather than trusting an optimizer's success flag.

### stat-02-04

**Eigenvalues and eigenvectors**

For Av=lambda v, the direction v is preserved by A. Covariance eigenvectors define principal directions and eigenvalues their variances. Repeated eigenvalues make individual eigenvector orientations nonunique even when the subspace is meaningful.

### stat-02-05

**Singular value decomposition**

Write X=U S V-transpose, with nonnegative singular values. Small singular values reveal weakly identified directions; truncating them creates a lower-rank approximation. SVD-based least squares avoids explicitly inverting X-transpose X.

### stat-02-06

**Positive definite matrices**

A symmetric matrix is positive definite when v-transpose A v is positive for every nonzero v. Covariances are at least semidefinite; duplicate variables can make them singular. Cholesky factorization requires stricter positivity.

### stat-02-07

**Matrix calculus**

For squared loss, the gradient is 2 X-transpose(X beta-y). The transpose maps observation errors back into coefficient coordinates. Confirm shapes and finite-difference checks before implementing more elaborate gradient code.

### stat-02-08

**Differential calculus**

A derivative is a local slope, while a second derivative describes curvature. A zero derivative can indicate a minimum, maximum or saddle. Optimization requires checking the local geometry or stronger global assumptions.

### stat-02-09

**Integral calculus**

A continuous probability is an integral of density over a region, not the density at a point. Expectations integrate value times density. A density may exceed one while its total integral remains one.

### stat-02-10

**Multivariable calculus**

Partial derivatives change one coordinate while holding others fixed; gradients collect them. Cross-partials express interactions. Scaling coordinates changes gradient magnitudes and can strongly affect an iterative optimizer's path.

### stat-02-11

**Taylor expansions**

A first-order expansion f(x+h) approximately equals f(x)+grad(f)-transpose h for small h. The delta method uses this local approximation for uncertainty. It can fail near boundaries or with large skewed uncertainty.

### stat-02-12

**Convex analysis**

A convex objective over a convex feasible set has no inferior local minima. Strict convexity can ensure uniqueness. Convexity simplifies optimization but does not certify that the model or loss reflects the scientific objective.

### stat-02-13

**Numerical conditioning**

Condition numbers describe sensitivity of the exact solution to perturbed inputs. Near-collinear predictors can produce enormous coefficient changes from tiny data changes while predictions remain similar within the training region.

### stat-02-14

**Numerical stability**

A stable algorithm controls additional errors introduced by arithmetic. Subtracting nearly equal large numbers loses precision; solving by QR/SVD is usually safer than forming an explicit matrix inverse.

### stat-02-15

**Real analysis fundamentals**

Convergence of functions, sums and integrals requires conditions. Pointwise convergence alone does not permit exchanging a limit and an integral. Dominated convergence supplies one sufficient condition used in asymptotic derivations.

### stat-02-16

**Measure-theoretic probability**

A probability space specifies outcomes, measurable events and a probability measure. Conditional expectation is an information-dependent random variable, generalizing familiar conditional averages even when conditioning on a probability-zero continuous value.

### stat-02-17

**Differential equations**

A differential equation specifies a rate of change, such as dN/dt=rN. Its solution requires an initial condition. Discrete numerical steps approximate the trajectory, and large steps can introduce artificial instability.

### stat-02-18

**Information theory**

Entropy averages negative log probabilities; KL divergence averages a log density ratio and is directional. Coding or predictive log loss provides an operational interpretation. Zero model probability for a possible event can make KL infinite.

## Worked Python demonstrations

Complete offline program: [chapter_02.py](../examples/chapter_02.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_02.py
```

### Least squares is a projection

The three observations do not lie exactly on a line. `lstsq` produces coefficients and a residual whose dot product with each feature column is numerically zero. Adding twice the slope column increases the number of columns but leaves rank at two. Thus extra stored features need not add identifiable information.

### Verify a derivative before trusting optimization

Central finite differences perturb one coordinate at a time. Agreement with the analytic gradient validates the derivative at the chosen point, not global optimizer correctness. The KL calculation then shows why assigning probability 0.1 to a half-probability event incurs a predictive penalty.

### Complete executable example

```python
import numpy as np

def projection_and_rank():
    x = np.array([[1., 0.], [1., 1.], [1., 2.]])
    y = np.array([1., 2., 4.])
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    assert np.allclose(x.T @ residual, 0, atol=1e-12)
    redundant = np.column_stack([x, 2*x[:, 1]])
    assert np.linalg.matrix_rank(redundant) == 2
    print("Coefficients:", beta, "rank with duplicate direction:", 2)

def gradients_and_information():
    x = np.array([[1., 0.], [1., 1.], [1., 2.]])
    y, beta = np.array([1., 2., 4.]), np.array([0.2, 0.5])
    loss = lambda b: np.sum((x @ b-y)**2)
    h = 1e-6
    finite = np.array([(loss(beta+h*e)-loss(beta-h*e))/(2*h) for e in np.eye(2)])
    analytic = 2*x.T @ (x @ beta-y)
    assert np.allclose(finite, analytic, atol=1e-7)
    p, q = np.array([.5, .5]), np.array([.9, .1])
    kl = np.sum(p*np.log(p/q))
    assert kl > 0
    print("Gradient:", analytic, "KL in nats:", round(float(kl), 4))

def main():
    projection_and_rank()
    gradients_and_information()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: Why avoid the inverse formula for regression?** Forming X-transpose X squares the condition number, and explicit inversion adds unnecessary computation. QR or SVD solves the least-squares problem more reliably. Poor conditioning remains an information problem even with a stable algorithm.

**Interview: Does a small singular value mean a feature should always be deleted?** No. It identifies a poorly determined direction, which may combine several scientifically essential variables. Scaling, redesign, regularization or reporting uncertainty may be more appropriate than mechanically dropping one column.

## Primary sources and official APIs

- [NumPy least-squares API](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html).

- [NumPy singular-value decomposition API](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html).

## Reading connections

[Previous chapter](01-problem-formulation-and-statistical-reasoning.md) | [Book contents](../README.md) | [Next chapter](03-probability-fundamentals-and-stochastic-processes.md)
