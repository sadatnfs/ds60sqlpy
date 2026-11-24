# jax-020: explained reference

For \(dx/dt=-kx\), the continuous solution at horizon T is \(x(T)=x_0e^{-kT}\). Euler with n steps of size \(h=T/n\) gives \(x_n=x_0(1-kh)^n\). Its rate derivative is \(-nhx_0(1-kh)^{n-1}\), while the continuous derivative is \(-Tx_0e^{-kT}\). These are different finite-step formulas that approach one another under a suitable refinement regime.

## Solution approach

Write the simulated value in closed form: ten Euler steps of size 0.1 multiply the initial value by `(1 - rate / 10) ** 10`. Autodiff differentiates that product, not the exponential it approximates. The tasks compare the discrete derivative with the continuous one, refine the step, and probe the edges of the recurrence at zero rate and at a step too large for decay.

**Why it is correct here:** Differentiating `(1 - k / 10) ** 10` gives `-(1 - k / 10) ** 9`, which is `-0.9 ** 9` near -0.387 at k = 1, while the continuous slope is `-exp(-1)` near -0.368. Twenty steps give `-0.95 ** 19` near -0.377, closer to the limit. Rate zero keeps the multiplier at one. The initial-state slope is `0.9 ** 10`, and one step at rate 3 multiplies by 1 - 3 = -2.

## Exercise 1: Differentiate the implemented algorithm

The derivative belongs to the discretized recurrence, not directly to the continuous exponential.

**Expected:** -0.9^9.

```python
close(jax.grad(simulate)(1.0), -(0.9**9))
```

**Plausible wrong approach:** Expecting `jax.grad(simulate)(1.)` to return `-exp(-1)` assumes autodiff differentiates the continuous model. It differentiates the ten-step program exactly, so the answer is `-0.9 ** 9`.

## Exercise 2: Compare continuous sensitivity

A disagreement here is expected discretization error rather than an autodiff defect.

**Expected:** Continuous -exp(-1), different from the ten-step derivative.

```python
continuous = -math.exp(-1.0)
discrete = float(jax.grad(simulate)(1.0))
assert not np.isclose(continuous, discrete, atol=1e-4, rtol=0.0)
```

**Plausible wrong approach:** Loosening the tolerance until the discrete and continuous slopes agree hides discretization error instead of measuring it. The lesson asserts that they differ and then shows refinement shrinking the gap.

## Exercise 3: Refine the derivative

Derivative convergence should be examined separately from value convergence.

**Expected:** The twenty-step derivative is closer to the continuous derivative.

```python
exact = -math.exp(-1.0)
a = abs(float(jax.grad(lambda k: simulate(k, steps=10))(1.0)) - exact)
b = abs(float(jax.grad(lambda k: simulate(k, steps=20))(1.0)) - exact)
assert b < a
```

**Plausible wrong approach:** Refining only the simulated value and assuming the derivative improves at the same rate skips the check that matters here. The derivative errors, about 0.019 and 0.009, are compared directly.

## Exercise 4: Check zero rate

The transition multiplier becomes one, so no decay occurs.

**Expected:** The state remains three.

```python
close(simulate(0.0, initial=3.0), 3.0)
```

**Plausible wrong approach:** Reading `rate = 0` as an empty system and expecting zero confuses the decay rate with the state. The multiplier `1 - 0 * dt` is one, so the initial value 3 is kept.

## Exercise 5: Differentiate the initial state

This linear system scales every initial perturbation by the complete discrete decay factor.

**Expected:** 0.9^10.

```python
close(jax.grad(lambda initial: simulate(1.0, initial=initial))(2.0), 0.9**10)
```

**Plausible wrong approach:** Answering `0.9 ** 9` for the initial-value sensitivity reuses the rate formula. The state is linear in its initial value, so every one of the ten factors remains and the slope is `0.9 ** 10`.

## Exercise 6: Inspect an unstable numerical regime

The large step leaves the intended stable positive-decay regime. A finite result does not make the discretization appropriate.

**Expected:** -2, despite positive continuous decay exp(-3).

```python
close(simulate(3.0, steps=1), -2.0)
assert math.exp(-3.0) > 0.0
```

**Plausible wrong approach:** Accepting -2 because it is finite treats a successful run as a valid simulation. Euler decay stays positive only while `rate * dt < 1`; at rate 3 with one step the sign flips even though `exp(-3)` is positive.

## How to verify

Run the reference and confirm `jax-020: 8 asserted cases passed`. Then evaluate `-(1 - 1 / n) ** (n - 1)` in plain Python for n = 10, 20 and 100 and compare each with `jax.grad(lambda k: simulate(k, steps=n))(1.)`. The values should match and drift toward `-exp(-1)` as n grows.

## Scope of this evidence

Before interpreting a gradient or fitted parameter, check time horizon, step size, stability and solver error. A successful scan only proves that the chosen recurrence executed. Do not use a differentiable but unstable algorithm as unqualified evidence about a continuous system.

Design a calibration study with independent synthetic observations, at least two discretizations and a sensitivity analysis. State whether the estimated parameter describes the continuous model, its numerical approximation or a misspecified surrogate.
