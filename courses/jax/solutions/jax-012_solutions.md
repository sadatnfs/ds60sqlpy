# jax-012: explained reference

Let \(\widehat y=w^{\mathsf T}x\) and \(\ell(w,x,y)=(w^{\mathsf T}x-y)^2\). Then \(\nabla_w\ell=2(w^{\mathsf T}x-y)x\). For rows \([1,2]\), \([3,4]\), targets \([1,2]\), and \(w=0\), the individual gradients are \([-2,-4]\) and \([-12,-16]\). Their mean is \([-7,-10]\). This is the gradient of the mean because differentiation and a finite weighted sum commute for this stated separable objective.

## Solution approach

Name the mapped axis before writing `in_axes`. Prediction batches map the feature rows and share one weight, so `in_axes=(None, 0)`. The model comparison maps the weight rows and shares one feature vector, so `in_axes=(0, None)`. For gradients, the per-example derivative of the squared error is `2 * (w . x - t) * x`, which at zero weight is `-2 * t * x`.

**Why it is correct here:** With w = [2, -1], the rows [1, 2] and [3, 4] give 2 - 2 = 0 and 6 - 4 = 2. At zero weight the per-example gradients are -2 * 1 * [1, 2] = [-2, -4] and -2 * 2 * [3, 4] = [-12, -16], whose mean is [-7, -10] and sum [-14, -20]. The three models applied to [2, 3] give 2, 3 and 2 + 3 = 5.

## Exercise 1: Compare with a literal loop

The loop supplies a transparent oracle for this tiny batch; it is not a performance benchmark.

**Expected:** The same [0,2] values.

```python
w = jnp.array([2.0, -1.0])
loop = jnp.stack([predict_one(w, row) for row in features])
close(jax.vmap(predict_one, in_axes=(None, 0))(w, features), loop)
```

**Plausible wrong approach:** Mapping both arguments with `in_axes=0` pairs weight entry 2 with row [1, 2] and entry -1 with row [3, 4]. Each call then sees a scalar weight against a length-2 row, which `vdot` rejects.

## Exercise 2: Reduce gradients deliberately

The equality depends on the stated separable loss and equal observation weights.

**Expected:** Both [-7,-10].

```python
batch_loss = lambda w: jnp.mean(jax.vmap(loss_one, in_axes=(None, 0, 0))(w, features, targets))
close(jax.grad(batch_loss)(jnp.zeros(2)), [-7.0, -10.0])
```

**Plausible wrong approach:** Assuming the mean of per-example gradients always equals the gradient of the batch objective ignores weighting. With unequal observation weights the plain mean of the per-example rows no longer matches.

## Exercise 3: Change to a sum

The batch contains two equally weighted observations, so sum and mean differ by two.

**Expected:** [-14,-20], twice the mean gradient.

```python
summed = lambda w: jnp.sum(jax.vmap(loss_one, in_axes=(None, 0, 0))(w, features, targets))
close(jax.grad(summed)(jnp.zeros(2)), [-14.0, -20.0])
```

**Plausible wrong approach:** Reusing [-7, -10] for the summed objective halves the step an optimizer would take. Summing two equally weighted examples doubles the gradient to [-14, -20].

## Exercise 4: Map several models

Now the model axis is mapped and the input observation is shared. This answers a different question from a single-model prediction batch.

**Expected:** [2,3,5].

```python
weights = jnp.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
close(jax.vmap(predict_one, in_axes=(0, None))(weights, jnp.array([2.0, 3.0])), [2.0, 3.0, 5.0])
```

**Plausible wrong approach:** Keeping `in_axes=(None, 0)` for the model comparison hands the whole (3, 2) weight matrix to every call and maps over the scalars of [2, 3]. That is a shape error, not a set of three predictions.

## Exercise 5: Compose with JIT

Vectorization and compilation can compose without changing the requested mathematical mapping.

**Expected:** Same predictions [0,2].

```python
compiled = jax.jit(jax.vmap(predict_one, in_axes=(None, 0)))
close(compiled(jnp.array([2.0, -1.0]), features), [0.0, 2.0])
```

**Plausible wrong approach:** Wrapping only `predict_one` in `jax.jit` and keeping a Python loop gives the same [0, 2] but never tests whether `jit` composes with `vmap`. The task compiles the mapped function itself.

## Exercise 6: Allocate random streams per row

The mapped argument is a batch of keys rather than one key implicitly reused for every example.

**Expected:** Array shape (3,2); replay with the same key batch agrees.

```python
keys = jax.random.split(jax.random.key(23), 3)
draw = jax.vmap(lambda key: jax.random.normal(key, (2,)))
a, b = draw(keys), draw(keys)
assert a.shape == (3, 2)
close(a, b)
```

**Plausible wrong approach:** Closing over one key, as in `jax.vmap(lambda _: jax.random.normal(key, (2,)))`, produces three identical rows. Splitting into three keys and mapping over them gives each row its own stream.

## How to verify

Run the reference and confirm `jax-012: 8 asserted cases passed`. Print `jax.vmap(jax.grad(loss_one), in_axes=(None, 0, 0))(jnp.zeros(2), features, targets)` and expect the rows [-2, -4] and [-12, -16]. Averaging and summing that (2, 2) array by hand reproduces both batch gradients without calling the batch losses.

## Scope of this evidence

When a vectorized result is wrong, write the unmapped function signature, every in_axes entry and the expected output axes. When a gradient comparison differs, check whether the objective couples examples or uses a different reduction before blaming vmap.

Design a two-axis comparison of candidate parameter vectors and observations. Explain why vmap alone does not establish multi-device parallelism, and estimate the memory cost of retaining a gradient for every example in a larger model.
