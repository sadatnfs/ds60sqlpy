# jax-031: explained reference

The authored rule is \(y=1+2x-\frac12x^2\). A feature row \(\phi(x)=(1,x,x^2)\) has exact coefficients \((1,2,-1/2)\). For mean squared loss, \(\nabla_w L=2\Phi^{\mathsf T}(\Phi w-y)/N\). The fixed full-batch update is \(w'=w-0.02\nabla_wL\). An affine candidate uses only (1,x), so it cannot represent the quadratic term over arbitrary inputs.

## Solution approach

Build the comparison in layers that can each be checked alone. `features` maps an input to [1, x, x squared], `targets` is the known rule 1 + 2x - 0.5x squared, and `loss` is the mean squared residual. `advance` runs plain gradient descent with step 0.02 inside `jax.lax.scan`, so a fixed number of steps is one compiled loop whose only carried state is the coefficient vector.

**Why it is correct here:** The gradient of the mean squared residual is `2 X'(Xw - y) / n`, which the first task writes out by hand. Targets are exactly quadratic in x, so least squares on the five training rows recovers [1, 2, -0.5]. Each update reads only `state` and fixed data, which makes 200 plus 200 steps equal 400. At x = 3 the rule gives 1 + 6 - 4.5 = 2.5.

## Exercise 1: Audit the initial gradient

This isolates objective and feature construction before interpreting a long trajectory.

**Expected:** Matching three-coordinate gradients.

```python
zero = jnp.zeros(3)
explicit = 2 * train_design.T @ (train_design @ zero - train_y) / train_y.size
close(jax.grad(loss)(zero, train_design, train_y), explicit)
```

**Plausible wrong approach:** Comparing the trained weights with [1, 2, -0.5] and calling a mismatch a bug overlooks the budget. Four hundred steps at rate 0.02 need not converge, so the exact optimum comes from `lstsq` instead.

## Exercise 2: Check an independent optimum

The linear-in-features optimum is a separate algorithmic reference for the gradient-descent endpoint.

**Expected:** [1,2,-0.5] within numerical tolerance.

```python
optimum = jnp.linalg.lstsq(train_design, train_y, rcond=None)[0]
close(optimum, [1.0, 2.0, -0.5])
```

**Plausible wrong approach:** Dividing the explicit gradient by nothing, or forgetting its factor of two, gives a vector proportional to the autodiff result but not equal. The first task fails for either slip.

## Exercise 3: Replay the fixed budget

This study is deterministic under its stated numeric environment and contains no random data order.

**Expected:** Matching trained coefficients.

```python
again = jax.jit(lambda w: advance(w, 400))(jnp.zeros(3))[0]
close(again, trained)
```

**Plausible wrong approach:** Carrying a step counter or learning-rate schedule in the loop and dropping it on resume would break the 200 plus 200 replay. Here the transition is fixed, so coefficients alone suffice.

## Exercise 4: Resume a partial trajectory

For this fixed-batch plain SGD transition, the coefficient vector is sufficient numeric continuation state; the step count remains reporting metadata.

**Expected:** Matching final coefficients.

```python
first = advance(jnp.zeros(3), 200)[0]
continued = advance(first, 200)[0]
close(continued, trained)
```

**Plausible wrong approach:** Shuffling the training rows each step with a fresh random key would make a replay disagree unless the key is saved. This study has no random order, which is why the second run matches.

## Exercise 5: Verify the held-out split

This is a literal split check, not proof that a real dataset has no semantic or source-family leakage.

**Expected:** No exact overlapping input values.

```python
assert not set(np.asarray(train_x).tolist()) & set(np.asarray(heldout_x).tolist())
```

**Plausible wrong approach:** Treating the held-out points at -1.5, -0.5, 0.5 and 1.5 as extrapolation misreads the split. They sit between training inputs; x = 3 lies outside the training range of -2 to 2.

## Exercise 6: Transfer the coefficient rule

The algebraic target is known here. A real model's extrapolation outside observed support would require additional evidence.

**Expected:** Prediction 2.5 under the known synthetic rule.

```python
oracle = jnp.array([1.0, 2.0, -0.5])
close(features(jnp.array([3.0])) @ oracle, [2.5])
```

**Plausible wrong approach:** Claiming that a learned model will extrapolate to 2.5 at x = 3 borrows a guarantee from the synthetic oracle. Only the known rule gives that value; a real fit would need evidence beyond its support.

## How to verify

Run the reference and confirm `jax-031: 8 asserted cases passed`. Print the second output of `advance(jnp.zeros(3), 400)` to see the loss trajectory fall, and print `trained` next to `optimum` to see how close the budget came. Evaluating `loss(trained, heldout_design, heldout_y)` gives the held-out error for the report.

## Scope of this evidence

A favorable score can come from leakage, a changed target reduction, unequal comparison rows or a stale reported loss. Preserve the split and configuration before fitting. Report a failed or disappointing comparison rather than repeatedly tuning on the final held-out points.

Design a fresh nonlinear target or noisy dataset, choose development and final evaluation units, and defend a baseline before running. Produce a report with source identity, configuration, numerical checks, observed results and explicit limitations. A completed reference is not an expertise certificate.
