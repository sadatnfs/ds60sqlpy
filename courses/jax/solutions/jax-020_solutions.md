# jax-020: explained reference

For \(dx/dt=-kx\), the continuous solution at horizon T is \(x(T)=x_0e^{-kT}\). Euler with n steps of size \(h=T/n\) gives \(x_n=x_0(1-kh)^n\). Its rate derivative is \(-nhx_0(1-kh)^{n-1}\), while the continuous derivative is \(-Tx_0e^{-kT}\). These are different finite-step formulas that approach one another under a suitable refinement regime.

## Exercise 1: Differentiate the implemented algorithm

The derivative belongs to the discretized recurrence, not directly to the continuous exponential.

**Expected:** -0.9^9.

```python
close(jax.grad(simulate)(1.), -(.9 ** 9))
```

## Exercise 2: Compare continuous sensitivity

A disagreement here is expected discretization error rather than an autodiff defect.

**Expected:** Continuous -exp(-1), different from the ten-step derivative.

```python
continuous = -math.exp(-1.)
discrete = float(jax.grad(simulate)(1.))
assert not np.isclose(continuous, discrete, atol=1e-4, rtol=0.)
```

## Exercise 3: Refine the derivative

Derivative convergence should be examined separately from value convergence.

**Expected:** The twenty-step derivative is closer to the continuous derivative.

```python
exact = -math.exp(-1.)
a = abs(float(jax.grad(lambda k: simulate(k, steps=10))(1.)) - exact)
b = abs(float(jax.grad(lambda k: simulate(k, steps=20))(1.)) - exact)
assert b < a
```

## Exercise 4: Check zero rate

The transition multiplier becomes one, so no decay occurs.

**Expected:** The state remains three.

```python
close(simulate(0., initial=3.), 3.)
```

## Exercise 5: Differentiate the initial state

This linear system scales every initial perturbation by the complete discrete decay factor.

**Expected:** 0.9^10.

```python
close(jax.grad(lambda initial: simulate(1., initial=initial))(2.), .9 ** 10)
```

## Exercise 6: Inspect an unstable numerical regime

The large step leaves the intended stable positive-decay regime. A finite result does not make the discretization appropriate.

**Expected:** -2, despite positive continuous decay exp(-3).

```python
close(simulate(3., steps=1), -2.)
assert math.exp(-3.) > 0.
```

## Scope of this evidence

Before interpreting a gradient or fitted parameter, check time horizon, step size, stability and solver error. A successful scan only proves that the chosen recurrence executed. Do not use a differentiable but unstable algorithm as unqualified evidence about a continuous system.

Design a calibration study with independent synthetic observations, at least two discretizations and a sensitivity analysis. State whether the estimated parameter describes the continuous model, its numerical approximation or a misspecified surrogate.
