# jax-029: explained reference

Attention is \(O=\operatorname{softmax}(QK^{\mathsf T}/\sqrt d+M)V\), with the transpose attached to K and softmax over allowed key columns. For the adapter, \(\partial L/\partial B=s(XA)^{\mathsf T}G\) and \(\partial L/\partial A=sX^{\mathsf T}GB^{\mathsf T}\). With X all ones, W=I_8, A entries 1/8, B=0, s=2 and mean squared output loss, the B gradient is 1/2 and A gradient zero. An SGD step of 0.1 yields output 0.8 and loss 0.64.

## Solution approach

Port each formula term by term. Attention scores are `q k^T / sqrt(d)`, masked entries become negative infinity, a row-wise softmax gives weights, and the weights average the value rows. With zero queries and keys every allowed score is zero, so each query takes a plain average of the value rows it may see. The adapter is `I + 2 * A @ B` with A of shape (8, 2) and B of shape (2, 8).

**Why it is correct here:** Under the causal mask, query 0 sees row 0, query 1 rows 0 and 1, and query 2 all three, so changing row 2 cannot reach the first two outputs. Summing outputs gives row 0 weight 1 + 1/2 + 1/3 = 11/6, row 1 weight 5/6 and row 2 weight 1/3. Scores [1 / sqrt(2), 0] give probability `sigmoid(1 / sqrt(2))` near 0.67. The adapter has 16 + 16 = 32 entries and rank at most two.

## Exercise 1: Perturb only the future

This checks the complete output path, not only whether the mask looks triangular.

**Expected:** Earlier outputs remain identical.

```python
changed = v.at[2].set(jnp.array([100.0, 200.0]))
close(attention(q, k, changed, mask)[:2], attention(q, k, v, mask)[:2])
```

**Plausible wrong approach:** Checking only that the mask is lower triangular does not prove the output path respects it. Changing the future value row to [100, 200] tests the complete computation directly.

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

**Plausible wrong approach:** Dropping the `sqrt(d)` scale gives `sigmoid(1)` near 0.73 instead of about 0.67. The zero-score fixture cannot catch this, because zero divided by any scale is still zero.

## Exercise 3: Refuse an empty allowed set

A fully masked query has no categorical distribution under this contract.

**Expected:** ValueError during input validation.

```python
try:
    admit_attention(q, k, v, mask.at[0].set(False))
except ValueError:
    pass
else:
    raise AssertionError("all-masked query admitted")
```

**Plausible wrong approach:** Masking with a large negative number such as -1e9 instead of rejecting a query with no allowed key hides the problem. With all entries equal, softmax spreads weight over forbidden keys; with -inf everywhere it returns NaN.

## Exercise 4: Trace value gradients

A source value accumulates contributions from every query that can use it.

**Expected:** Each feature receives source-row weights [11/6,5/6,1/3].

```python
g = jax.grad(lambda values: attention(q, k, values, mask).sum())(v)
close(g, [[11 / 6, 11 / 6], [5 / 6, 5 / 6], [1 / 3, 1 / 3]])
```

**Plausible wrong approach:** Expecting every value row to get gradient one per feature assumes each query uses every key. Row 0 is visible to all three queries and row 2 only to the last, so the weights differ.

## Exercise 5: Count and bound the adapter

A rank bound constrains a matrix family, not the number of nonzero visible entries or measured model quality.

**Expected:** 32 entries; rank at most two.

```python
assert a.size + b.size == 32
assert np.linalg.matrix_rank(np.asarray(a @ b)) <= 2
```

**Plausible wrong approach:** Reading the rank bound as a statement that A @ B has at most two nonzero entries confuses rank with sparsity. At the given values B is zero, so the product is zero; trained factors can fill all 64 entries.

## Exercise 6: Compile the validated operation

This checks JAX transformation parity for the validated CPU mechanism only.

**Expected:** Matching causal-average outputs.

```python
close(jax.jit(attention)(q, k, v, mask), attention(q, k, v, mask))
```

**Plausible wrong approach:** Calling `admit_attention` inside `jax.jit` fails, since `np.asarray(allowed)` needs a concrete array. Only the pure `attention` helper is compiled, after validation on the host.

## How to verify

Run the reference and confirm `jax-029: 8 asserted cases passed`. Print `attention(q, k, v, mask)` and check rows [2, 0], [1, 1] and [8/3, 8/3] against the causal averages. Then remove the square-root division in a scratch copy and watch only the nonuniform scale task fail.

## Scope of this evidence

For a port mismatch, inspect factor orientation, score scale, axis, mask convention and reduction first. Square matrices and uniform scores can conceal wrong operations. Do not infer full-model equivalence from these two isolated mechanisms.

Compare with llm-009, llm-032, llm-applied-016 and llm-046 using identical literal fixtures. Specify the additional tokenizer, position, normalization, parameter and optimizer contracts required before attempting a full model conversion.
