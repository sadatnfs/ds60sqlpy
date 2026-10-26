# jax-030: explained reference

Define \(L(w)=\sum_i m_i(x_i^{\mathsf T}w-y_i)^2/\sum_i m_i+\lambda\lVert w\rVert_2^2\). Setting its gradient to zero gives \((X^{\mathsf T}MX/N+\lambda I)w=X^{\mathsf T}My/N\), where M is diagonal with mask entries and \(N=\sum_i m_i\). For rows (1,0),(1,1),(1,2), targets 1,3,5 and lambda zero, the unique fixture solution is (1,2).

## Exercise 1: Check a penalty convention

The penalty applies to both coefficients in this contract, so compare against the matching objective.

**Expected:** A finite changed coefficient vector with zero penalized gradient.

```python
weight = solve(design, targets, mask, .1)
assert not np.allclose(np.asarray(weight), [1., 2.])
close(jax.grad(objective)(weight, design, targets, mask, .1), [0., 0.])
```

## Exercise 2: Preserve row identity under permutation

The sum objective is invariant to consistent row reordering.

**Expected:** Unchanged coefficients.

```python
close(solve(design[::-1], targets[::-1], mask[::-1], 0.), [1., 2.])
```

## Exercise 3: Reject an empty population

The component refuses an undefined empirical mean before entering the numerical kernel.

**Expected:** ValueError.

```python
try:
    admit(design, targets, jnp.zeros(3, dtype=bool), 0.)
except ValueError:
    pass
else:
    raise AssertionError('empty population admitted')
```

## Exercise 4: Reject an invalid penalty

A negative value would change the optimization problem and can destroy the intended convexity guarantee.

**Expected:** ValueError under the declared nonnegative-penalty contract.

```python
try:
    admit(design, targets, mask, -.1)
except ValueError:
    pass
else:
    raise AssertionError('negative penalty admitted')
```

## Exercise 5: Check transformation parity

The compiled function receives the numerical representation after host admission.

**Expected:** Matching coefficients.

```python
close(jax.jit(solve)(design, targets, mask, .1), solve(design, targets, mask, .1))
```

## Exercise 6: Transfer the target rule

Changing the known affine rule provides a new oracle that is not satisfied by hard-coding the original coefficients.

**Expected:** Weights [2,3].

```python
close(solve(design, jnp.array([2., 5., 8.]), mask, 0.), [2., 3.])
```

## Scope of this evidence

A zero gradient can belong to the wrong objective. A low residual can belong to an ill-conditioned problem. A JIT pass can preserve the wrong mask. Retain separate evidence for admission, mathematical correctness, transformation behavior and the intended interpretation.

Deliver your own implementation with a short contract, shape ledger, independent oracle and a failure case absent from the worked examples. Explain when a QR/SVD-based fit or a different regularization policy would be preferable to this tiny normal-equation teaching component.
