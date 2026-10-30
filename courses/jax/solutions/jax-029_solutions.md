# jax-029: explained reference

Attention is \(O=\operatorname{softmax}(QK^{\mathsf T}/\sqrt d+M)V\), with the transpose attached to K and softmax over allowed key columns. For the adapter, \(\partial L/\partial B=s(XA)^{\mathsf T}G\) and \(\partial L/\partial A=sX^{\mathsf T}GB^{\mathsf T}\). With X all ones, W=I_8, A entries 1/8, B=0, s=2 and mean squared output loss, the B gradient is 1/2 and A gradient zero. An SGD step of 0.1 yields output 0.8 and loss 0.64.

## Exercise 1: Perturb only the future

This checks the complete output path, not only whether the mask looks triangular.

**Expected:** Earlier outputs remain identical.

```python
changed = v.at[2].set(jnp.array([100.0, 200.0]))
close(attention(q, k, changed, mask)[:2], attention(q, k, v, mask)[:2])
```

## Exercise 2: Test the scale with nonuniform scores

A scalar logistic calculation detects omission of the square-root scale.

**Expected:** Weights determined by softmax([1/sqrt(2),0]).

```python
query = jnp.array([[1.0, 0.0]])
keys = jnp.eye(2)
values = 2 * jnp.eye(2)
probability = 1 / (1 + math.exp(-1 / math.sqrt(2)))
close(
    attention(query, keys, values, jnp.ones((1, 2), dtype=bool)),
    [[2 * probability, 2 * (1 - probability)]],
)
```

## Exercise 3: Refuse an empty allowed set

A fully masked query has no categorical distribution under this contract.

**Expected:** ValueError during admission.

```python
try:
    admit_attention(q, k, v, mask.at[0].set(False))
except ValueError:
    pass
else:
    raise AssertionError("all-masked query admitted")
```

## Exercise 4: Trace value gradients

A source value accumulates contributions from every query that can use it.

**Expected:** Each feature receives source-row weights [11/6,5/6,1/3].

```python
g = jax.grad(lambda values: attention(q, k, values, mask).sum())(v)
close(g, [[11 / 6, 11 / 6], [5 / 6, 5 / 6], [1 / 3, 1 / 3]])
```

## Exercise 5: Count and bound the adapter

A rank bound constrains a matrix family, not the number of nonzero visible entries or measured model quality.

**Expected:** 32 entries; rank at most two.

```python
assert a.size + b.size == 32
assert np.linalg.matrix_rank(np.asarray(a @ b)) <= 2
```

## Exercise 6: Compile the admitted operation

This checks JAX transformation parity for the admitted CPU mechanism only.

**Expected:** Matching causal-average outputs.

```python
close(jax.jit(attention)(q, k, v, mask), attention(q, k, v, mask))
```

## Scope of this evidence

For a port mismatch, inspect factor orientation, score scale, axis, mask convention and reduction first. Square matrices and uniform scores can conceal wrong operations. Do not infer full-model equivalence from these two isolated mechanisms.

Compare with llm-009, llm-032, llm-applied-016 and llm-046 using identical literal fixtures. Specify the additional tokenizer, position, normalization, parameter and optimizer contracts required before attempting a full model conversion.
