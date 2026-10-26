# jax-012: explained reference

Let \(\widehat y=w^{\mathsf T}x\) and \(\ell(w,x,y)=(w^{\mathsf T}x-y)^2\). Then \(\nabla_w\ell=2(w^{\mathsf T}x-y)x\). For rows \([1,2]\), \([3,4]\), targets \([1,2]\), and \(w=0\), the individual gradients are \([-2,-4]\) and \([-12,-16]\). Their mean is \([-7,-10]\). This is the gradient of the mean because differentiation and a finite weighted sum commute for this stated separable objective.

## Exercise 1: Compare with a literal loop

The loop supplies a transparent oracle for this tiny batch; it is not a performance benchmark.

**Expected:** The same [0,2] values.

```python
w = jnp.array([2., -1.])
loop = jnp.stack([predict_one(w, row) for row in features])
close(jax.vmap(predict_one, in_axes=(None, 0))(w, features), loop)
```

## Exercise 2: Reduce gradients deliberately

The equality depends on the stated separable loss and equal observation weights.

**Expected:** Both [-7,-10].

```python
batch_loss = lambda w: jnp.mean(jax.vmap(loss_one, in_axes=(None, 0, 0))(w, features, targets))
close(jax.grad(batch_loss)(jnp.zeros(2)), [-7., -10.])
```

## Exercise 3: Change to a sum

The batch contains two equally weighted observations, so sum and mean differ by two.

**Expected:** [-14,-20], twice the mean gradient.

```python
summed = lambda w: jnp.sum(jax.vmap(loss_one, in_axes=(None, 0, 0))(w, features, targets))
close(jax.grad(summed)(jnp.zeros(2)), [-14., -20.])
```

## Exercise 4: Map several models

Now the model axis is mapped and the input observation is shared. This answers a different question from a single-model prediction batch.

**Expected:** [2,3,5].

```python
weights = jnp.array([[1., 0.], [0., 1.], [1., 1.]])
close(jax.vmap(predict_one, in_axes=(0, None))(weights, jnp.array([2., 3.])), [2., 3., 5.])
```

## Exercise 5: Compose with JIT

Vectorization and compilation can compose without changing the requested mathematical mapping.

**Expected:** Same predictions [0,2].

```python
compiled = jax.jit(jax.vmap(predict_one, in_axes=(None, 0)))
close(compiled(jnp.array([2., -1.]), features), [0., 2.])
```

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

## Scope of this evidence

When a vectorized result is wrong, write the unmapped function signature, every in_axes entry and the expected output axes. When a gradient comparison differs, check whether the objective couples examples or uses a different reduction before blaming vmap.

Design a two-axis comparison of candidate parameter vectors and observations. Explain why vmap alone does not establish multi-device parallelism, and estimate the memory cost of retaining a gradient for every example in a larger model.
