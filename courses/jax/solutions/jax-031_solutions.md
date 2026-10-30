# jax-031: explained reference

The authored rule is \(y=1+2x-\frac12x^2\). A feature row \(\phi(x)=(1,x,x^2)\) has exact coefficients \((1,2,-1/2)\). For mean squared loss, \(\nabla_w L=2\Phi^{\mathsf T}(\Phi w-y)/N\). The fixed full-batch update is \(w'=w-0.02\nabla_wL\). An affine candidate uses only (1,x), so it cannot represent the quadratic term over arbitrary inputs.

## Exercise 1: Audit the initial gradient

This isolates objective and feature construction before interpreting a long trajectory.

**Expected:** Matching three-coordinate gradients.

```python
zero = jnp.zeros(3)
explicit = 2 * train_design.T @ (train_design @ zero - train_y) / train_y.size
close(jax.grad(loss)(zero, train_design, train_y), explicit)
```

## Exercise 2: Check an independent optimum

The linear-in-features optimum is a separate algorithmic reference for the gradient-descent endpoint.

**Expected:** [1,2,-0.5] within numerical tolerance.

```python
optimum = jnp.linalg.lstsq(train_design, train_y, rcond=None)[0]
close(optimum, [1.0, 2.0, -0.5])
```

## Exercise 3: Replay the fixed budget

This study is deterministic under its stated numeric environment and contains no random data order.

**Expected:** Matching trained coefficients.

```python
again = jax.jit(lambda w: advance(w, 400))(jnp.zeros(3))[0]
close(again, trained)
```

## Exercise 4: Resume a partial trajectory

For this fixed-batch plain SGD transition, the coefficient vector is sufficient numeric continuation state; the step count remains reporting metadata.

**Expected:** Matching final coefficients.

```python
first = advance(jnp.zeros(3), 200)[0]
continued = advance(first, 200)[0]
close(continued, trained)
```

## Exercise 5: Verify the held-out split

This is a literal split check, not proof that a real dataset has no semantic or source-family leakage.

**Expected:** No exact overlapping input values.

```python
assert not set(np.asarray(train_x).tolist()) & set(np.asarray(heldout_x).tolist())
```

## Exercise 6: Transfer the coefficient rule

The algebraic target is known here. A real model's extrapolation outside observed support would require additional evidence.

**Expected:** Prediction 2.5 under the known synthetic rule.

```python
oracle = jnp.array([1.0, 2.0, -0.5])
close(features(jnp.array([3.0])) @ oracle, [2.5])
```

## Scope of this evidence

A favorable score can come from leakage, a changed target reduction, unequal comparison rows or a stale reported loss. Preserve the split and configuration before fitting. Report a failed or disappointing comparison rather than repeatedly tuning on the final held-out points.

Design a fresh nonlinear target or noisy dataset, choose development and final evaluation units, and defend a baseline before running. Produce a report with source identity, configuration, numerical checks, observed results and explicit limitations. A completed reference is not an expertise certificate.
