# jax-030: explained reference

Define \(L(w)=\sum_i m_i(x_i^{\mathsf T}w-y_i)^2/\sum_i m_i+\lambda\lVert w\rVert_2^2\). Setting its gradient to zero gives \((X^{\mathsf T}MX/N+\lambda I)w=X^{\mathsf T}My/N\), where M is diagonal with mask entries and \(N=\sum_i m_i\). For rows (1,0),(1,1),(1,2), targets 1,3,5 and lambda zero, the unique fixture solution is (1,2).

## Solution approach

Assemble the component from pieces with distinct jobs. `admit` checks contracts on the host: matching row counts, a nonempty Boolean mask, a finite nonnegative penalty and finite data. `objective` states the penalized masked mean squared error. `solve` builds the normal equations of that same objective, so its answer must make the objective's gradient zero.

**Why it is correct here:** Setting the gradient of `mean((Xw - y) ** 2) + lambda * w . w` to zero gives `(X'X / n + lambda I) w = X'y / n`, which is what `solve` builds. Targets [1, 3, 5] follow 1 + 2x, so penalty zero returns [1, 2] in any row order; penalty 0.1 shrinks it. Targets [2, 5, 8] follow 2 + 3x and give [2, 3].

## Exercise 1: Check a penalty convention

The penalty applies to both coefficients in this contract, so compare against the matching objective.

**Expected:** A finite changed coefficient vector with zero penalized gradient.

```python
weight = solve(design, targets, mask, 0.1)
assert not np.allclose(np.asarray(weight), [1.0, 2.0])
close(jax.grad(objective)(weight, design, targets, mask, 0.1), [0.0, 0.0])
```

**Plausible wrong approach:** Penalizing only the slope, as many regression libraries do, gives a different weight. Its objective gradient would not be zero here, because this contract penalizes both coefficients.

## Exercise 2: Preserve row identity under permutation

The sum objective is invariant to consistent row reordering.

**Expected:** Unchanged coefficients.

```python
close(solve(design[::-1], targets[::-1], mask[::-1], 0.0), [1.0, 2.0])
```

**Plausible wrong approach:** Reversing the design rows but not the targets pairs each row with another target and changes the fitted line. Permutation invariance holds only when rows, targets and mask move together.

## Exercise 3: Reject an empty population

The component refuses an undefined empirical mean before entering the numerical kernel.

**Expected:** ValueError.

```python
try:
    admit(design, targets, jnp.zeros(3, dtype=bool), 0.0)
except ValueError:
    pass
else:
    raise AssertionError("empty population admitted")
```

**Plausible wrong approach:** Letting an all-false mask reach `solve` divides by a zero count and returns non-finite values rather than an error. `admit` rejects the empty population first.

## Exercise 4: Reject an invalid penalty

A negative value would change the optimization problem and can destroy the intended convexity guarantee.

**Expected:** ValueError under the declared nonnegative-penalty contract.

```python
try:
    admit(design, targets, mask, -0.1)
except ValueError:
    pass
else:
    raise AssertionError("negative penalty admitted")
```

**Plausible wrong approach:** Relying on the solve to fail for a negative penalty does not work here: with -0.1 the matrix stays invertible because the smallest eigenvalue of `X'X / 3` is about 0.28. The contract rule must reject it.

## Exercise 5: Check transformation parity

The compiled function receives the numerical representation after host-side validation.

**Expected:** Matching coefficients.

```python
close(jax.jit(solve)(design, targets, mask, 0.1), solve(design, targets, mask, 0.1))
```

**Plausible wrong approach:** Moving `admit` inside the compiled function breaks it, because `np.asarray` cannot read a tracer. Validation stays on the host and only `solve` is passed to `jax.jit`.

## Exercise 6: Transfer the target rule

Changing the known affine rule provides a new oracle that is not satisfied by hard-coding the original coefficients.

**Expected:** Weights [2,3].

```python
close(solve(design, jnp.array([2.0, 5.0, 8.0]), mask, 0.0), [2.0, 3.0])
```

**Plausible wrong approach:** Returning [1, 2] from a helper that memorized the first fixture would pass the first few checks. The new targets [2, 5, 8] demand [2, 3] and expose a hard-coded answer.

## How to verify

Run the reference and confirm `jax-030: 8 asserted cases passed`. Print `solve(design, targets, mask, .1)` and confirm both coefficients move from [1, 2]. Then evaluate `objective` at that weight and at small perturbations of it to see the minimum, and confirm `jax.grad(objective)` is zero there.

## Scope of this evidence

A zero gradient can belong to the wrong objective. A low residual can belong to an ill-conditioned problem. A JIT pass can preserve the wrong mask. Retain separate evidence for input validation, mathematical correctness, transformation behavior and the intended interpretation.

Deliver your own implementation with a short contract, shape ledger, independent oracle and a failure case absent from the worked examples. Explain when a QR/SVD-based fit or a different regularization policy would be preferable to this tiny normal-equation teaching component.
