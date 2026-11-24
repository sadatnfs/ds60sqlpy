# jax-024: explained reference

For \(f(X)=X^{\mathsf T}X\) with \(X\in\mathbb R^{N\times D}\), the output shape is \((D,D)\). N affects the reduction but not the output dimensions. For \(X=\begin{bmatrix}1&2\\3&4\\5&6\end{bmatrix}\), the Gram matrix is \(\begin{bmatrix}35&44\\44&56\end{bmatrix}\). This exact small matrix checks the same interface that abstract shape evaluation describes.

## Solution approach

Separate what is known from shapes alone from what needs values. For `X.T @ X` with X of shape (n, d), the output is (d, d) whatever n is, so `jax.eval_shape` can answer shape questions without arithmetic. Values need execution, and the staged jaxpr and compiled executable sit between the two.

**Why it is correct here:** A (7, 2) input gives (2, 2) and a (3, 4) input gives (4, 4). The compiled executable accepts any (3, 2) float64 input, and doubling X multiplies the Gram matrix by four. The sum of all Gram entries equals the sum of squared row sums, here 3, 7 and 11, so each entry's derivative is twice its row sum: 6, 14 and 22. Zero input gives the zero (2, 2) matrix.

## Exercise 1: Change only the abstract row count

The feature count controls the Gram dimensions; row count is reduced.

**Expected:** Still (2,2).

```python
shape = jax.eval_shape(gram, jax.ShapeDtypeStruct((7, 2), jnp.float64))
assert shape.shape == (2, 2)
```

**Plausible wrong approach:** Confusing `X.T @ X` with `X @ X.T` predicts a (7, 7) result for seven rows. The Gram matrix here compares features, so the row count is summed away.

## Exercise 2: Change the feature count

An extra feature changes both Gram axes.

**Expected:** (4,4).

```python
shape = jax.eval_shape(gram, jax.ShapeDtypeStruct((3, 4), jnp.float64))
assert shape.shape == (4, 4)
```

**Plausible wrong approach:** Expecting `jax.eval_shape` to return numbers misreads it. It returns a `ShapeDtypeStruct` with shape and dtype, which is why the zero-input task needs a real call to learn values.

## Exercise 3: Inspect staged dependencies

This robust structural check avoids asserting a version-specific pretty-print string.

**Expected:** One output variable and at least one numerical equation.

```python
closed = jax.make_jaxpr(gram)(values)
assert len(closed.jaxpr.outvars) == 1
assert closed.jaxpr.eqns
```

**Plausible wrong approach:** Asserting the exact printed jaxpr, such as a particular `dot_general` line, ties the test to one JAX version. The reference checks one output variable and a nonempty equation list.

## Exercise 4: Execute another compatible value

The shape and dtype stay compatible, while the bilinear product scales quadratically.

**Expected:** Four times the original Gram matrix.

```python
compiled = jax.jit(gram).lower(values).compile()
close(compiled(2 * values), 4 * gram(values))
```

**Plausible wrong approach:** Predicting that doubling the input doubles the output treats the Gram matrix as linear. Both factors double, so the result is four times the original.

## Exercise 5: Compose a scalar sensitivity

The sum of \(X^{\mathsf T}X\) equals the sum of squared row sums.

**Expected:** Each row has two copies of twice its row sum: [[6,6],[14,14],[22,22]].

```python
close(jax.grad(lambda x: gram(x).sum())(values), [[6.0, 6.0], [14.0, 14.0], [22.0, 22.0]])
```

**Plausible wrong approach:** Answering `2 * X` gives the derivative of the trace of the Gram matrix, the sum of squares. The task sums every entry, including off-diagonal ones, which couples the features and gives row-sum copies.

## Exercise 6: Separate metadata from values

Shape inference cannot establish a data-dependent numeric answer.

**Expected:** Same (2,2) shape, all-zero matrix.

```python
zero = jnp.zeros_like(values)
result = jax.jit(gram)(zero)
assert result.shape == (2, 2)
close(result, jnp.zeros((2, 2)))
```

**Plausible wrong approach:** Calling the executable compiled for (3, 2) on a (7, 2) array fails, because `lower(...).compile()` fixes the signature. Shape inference across sizes belongs to `eval_shape` or a fresh `jax.jit` call.

## How to verify

Run the reference and confirm `jax-024: 8 asserted cases passed`. Compute `gram(values)` and compare it with [[35, 44], [44, 56]] worked out by hand from the three rows. Then print `jax.make_jaxpr(gram)(values)` to see the transpose and product, and pass a (7, 2) array to `compiled` to see the signature error.

## Scope of this evidence

For a staging mismatch, identify whether the failure concerns source tracing, lowering, backend compilation or an executable signature. Avoid brittle checks of textual IR, and do not call a process-local compiled object a portable export.

Design a deployment artifact contract with input/output shapes, dtype, backend, version and fresh-process evidence. Explain which parts this unit checked and which would require a separately prepared export/target-runtime workflow.
