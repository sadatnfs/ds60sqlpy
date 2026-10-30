# tf-022: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Attention mixes value vectors using weights derived from query-key scores. A causal mask restricts each query to its current and earlier positions. The mask must act before the key-axis softmax, otherwise forbidden positions can consume probability mass or influence normalization. Equal scores make the allowed distribution easy to calculate: each legal key receives equal weight. Prefix invariance is a direct information-boundary test: recomputing a shorter prefix should reproduce the full computation early outputs. This property must hold across every decoder component, not just attention. A passing mask test cannot detect a contaminated training corpus or incorrect target shifting.

**Query:** A vector used to request information from keys.

**Key:** A vector scored against a query.

**Causal mask:** A rule excluding future positions from a query.

## Reading the implementation

Q@transpose(K) forms query-by-key scores, scaled by square root of key width. tf.linalg.band_part constructs the lower triangle. tf.where replaces forbidden scores with negative infinity before `tf.nn.softmax(axis=-1)`. Multiplying weights by V returns one output vector per query. The supplied helper accepts only square, nonempty self-attention with matching row counts and finite data.

## Exercise 1: Calculate uniform mixtures

The question is: Use zero3x2 queries and keys with V[[2,0],[0,2],[6,6]].

Each row averages exactly its legal values. The first row copies one vector, the second averages two, and the third averages three. No learned weights are needed to inspect the boundary.

```python
q = np.zeros((3, 2))
v = np.array([[2.0, 0.0], [0.0, 2.0], [6.0, 6.0]])
out = attention(q, q, v).numpy()
np.testing.assert_allclose(out, [[2, 0], [1, 1], [8 / 3, 8 / 3]], atol=1e-6, rtol=0)
```

**Expected:** outputs[[2,0],[1,1],[8/3,8/3]].

**Verify:** Compare the computed values or written argument with outputs[[2,0],[1,1],[8/3,8/3]].

## Exercise 2: Perturb the future

The question is: Replace only the third value with[100,200].

A change to a future value must not influence earlier queries. This causal assertion is more informative than a visually triangular attention plot.

```python
future = v.copy()
future[2] = [100, 200]
changed = attention(q, q, future).numpy()
np.testing.assert_allclose(changed[:2], out[:2], atol=1e-6, rtol=0)
np.testing.assert_allclose(changed[2], [34, 202 / 3], atol=1e-6, rtol=0)
```

**Expected:** first two rows unchanged; final row[34,202/3].

**Verify:** Compare the computed values or written argument with first two rows unchanged; final row[34,202/3].

## Exercise 3: Recompute every prefix

The question is: For prefix lengths1,2,3 run the function anew on sliced Q,K,V.

The prefix computation reconstructs its mask and softmax. Slicing already-computed full weights would not independently test whether future information influenced them.

```python
for cut in range(1, 4):
    prefix = attention(q[:cut], q[:cut], v[:cut]).numpy()
    np.testing.assert_allclose(prefix, out[:cut], atol=1e-6, rtol=0)
```

**Expected:** all prefix outputs match the full early rows.

**Verify:** Compare the computed values or written argument with all prefix outputs match the full early rows.

## Exercise 4: Expose post-softmax masking

The question is: Multiply uniform1/3 weights by a triangle without renormalizing.

Zeros in forbidden positions do not prove a valid probability distribution. Masking after normalization leaves insufficient mass on early rows and changes their output scale.

```python
broken = np.ones((3, 3)) / 3 * np.tri(3)
np.testing.assert_allclose(broken.sum(1), [1 / 3, 2 / 3, 1], atol=1e-12, rtol=0)
```

**Expected:** row sums[1/3,2/3,1].

**Verify:** Compare the computed values or written argument with row sums[1/3,2/3,1].

## Exercise 5: Use nonuniform scores

The question is: Set Q=K[[1,0],[0,1],[1,1]] and repeat the prefix test.

Uniform scores can hide a missing scale factor or swapped query/key operation. A nonuniform fixture adds a second independent family of behavior.

```python
non = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
full = attention(non, non, v).numpy()
for cut in range(1, 4):
    np.testing.assert_allclose(
        attention(non[:cut], non[:cut], v[:cut]).numpy(), full[:cut], atol=1e-6, rtol=0
    )
```

**Expected:** prefix comparisons pass within 1e-6.

**Verify:** Compare the computed values or written argument with prefix comparisons pass within 1e-6.

## Exercise 6: Refuse malformed input

The question is: Pass an empty sequence and a value matrix with the wrong row count.

A probability distribution needs at least one legal key. Clear input failures prevent shape bugs from emerging later as unexplained NaNs or matrix multiplication errors.

```python
for args in [(np.empty((0, 2)), np.empty((0, 2)), np.empty((0, 2))), (q, q, v[:2])]:
    try:
        attention(*args)
    except ValueError:
        pass
    else:
        raise AssertionError("bad shape accepted")
```

**Expected:** both raise ValueError.

**Verify:** Compare the computed values or written argument with both raise ValueError.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
