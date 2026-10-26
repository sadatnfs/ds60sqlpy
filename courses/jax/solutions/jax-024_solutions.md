# jax-024: explained reference

For \(f(X)=X^{\mathsf T}X\) with \(X\in\mathbb R^{N\times D}\), the output shape is \((D,D)\). N affects the reduction but not the output dimensions. For \(X=\begin{bmatrix}1&2\\3&4\\5&6\end{bmatrix}\), the Gram matrix is \(\begin{bmatrix}35&44\\44&56\end{bmatrix}\). This exact small matrix checks the same interface that abstract shape evaluation describes.

## Exercise 1: Change only the abstract row count

The feature count controls the Gram dimensions; row count is reduced.

**Expected:** Still (2,2).

```python
shape = jax.eval_shape(gram, jax.ShapeDtypeStruct((7, 2), jnp.float64))
assert shape.shape == (2, 2)
```

## Exercise 2: Change the feature count

An extra feature changes both Gram axes.

**Expected:** (4,4).

```python
shape = jax.eval_shape(gram, jax.ShapeDtypeStruct((3, 4), jnp.float64))
assert shape.shape == (4, 4)
```

## Exercise 3: Inspect staged dependencies

This robust structural check avoids asserting a version-specific pretty-print string.

**Expected:** One output variable and at least one numerical equation.

```python
closed = jax.make_jaxpr(gram)(values)
assert len(closed.jaxpr.outvars) == 1
assert closed.jaxpr.eqns
```

## Exercise 4: Execute another compatible value

The shape and dtype stay compatible, while the bilinear product scales quadratically.

**Expected:** Four times the original Gram matrix.

```python
compiled = jax.jit(gram).lower(values).compile()
close(compiled(2 * values), 4 * gram(values))
```

## Exercise 5: Compose a scalar sensitivity

The sum of \(X^{\mathsf T}X\) equals the sum of squared row sums.

**Expected:** Each row has two copies of twice its row sum: [[6,6],[14,14],[22,22]].

```python
close(jax.grad(lambda x: gram(x).sum())(values), [[6., 6.], [14., 14.], [22., 22.]])
```

## Exercise 6: Separate metadata from values

Shape inference cannot establish a data-dependent numeric answer.

**Expected:** Same (2,2) shape, all-zero matrix.

```python
zero = jnp.zeros_like(values)
result = jax.jit(gram)(zero)
assert result.shape == (2, 2)
close(result, jnp.zeros((2, 2)))
```

## Scope of this evidence

For a staging mismatch, identify whether the failure concerns source tracing, lowering, backend compilation or an executable signature. Avoid brittle checks of textual IR, and do not call a process-local compiled object a portable export.

Design a deployment artifact contract with input/output shapes, dtype, backend, version and fresh-process evidence. Explain which parts this unit checked and which would require a separately prepared export/target-runtime workflow.
