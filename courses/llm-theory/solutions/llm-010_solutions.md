# llm-010: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Content, position and visibility answer different questions in a Transformer. Content vectors describe the token representation available to a layer. Positional information distinguishes where a token occurs or how far apart two tokens are. A causal mask specifies which key positions a query may read. Normalization controls feature scale. None of these mechanisms automatically supplies all the others, and a correct mask cannot repair future information that has already entered a token representation through an earlier operation.

Begin with content-only attention and no mask. Every query compares itself with the same collection of keys. If we reorder query, key and value rows together, the comparisons are relabelled but their numerical relationships are unchanged. The output rows follow the same reorder. This property is permutation equivariance. It does not mean every output is identical, and it does not mean the function ignores token identity. It means the function has no separate knowledge of an absolute row number beyond the information supplied in its inputs.

Now hold a lower-triangular causal mask fixed while moving token content between rows. The first row can read only its current first key, the second can read the first two, and later rows have progressively larger accessible prefixes. Reordering content changes which token participates in each prefix. The mask therefore introduces an ordered visibility structure. It still does not directly encode a distance such as three positions ago, and identical content can remain indistinguishable in a single normalized weighted average. Explicit positional representations supply additional order or distance information.

Finally, every path feeding an earlier output must respect the intended visibility boundary. LayerNorm in a sequence model normally reduces the feature axis of each token separately. If an implementation instead centers a feature using all token rows, a future value changes the statistic subtracted from an earlier token. That earlier token is already contaminated before attention begins. This chapter derives these distinctions and tests them with literal float64 arrays. The simplified LayerNorm uses gain one and bias zero; learned gain and bias, pre/post-norm placement and RMSNorm receive deeper treatment in llm-045.

**Permutation equivariance:** Reordering inputs produces the corresponding reorder of outputs, rather than necessarily leaving outputs unchanged.

**Positional representation:** Information attached to positions or position relationships, distinct from token content.

**Causal visibility:** A rule forbidding a query from reading future key positions.

**Reduction axis:** The array dimension over which a statistic combines values.

**Prefix invariance:** Earlier outputs are unchanged when future tokens are appended or changed under the stated causal computation.

**Epsilon:** A positive denominator stabilizer that also slightly changes normalized variance.

## Reading the implementation

Use the shape convention Q:[Tq,Dk], K:[Tk,Dk], V:[Tk,Dv]. Scores have shape [Tq,Tk], one comparison for each query/key pair. Row-wise softmax reduces the key axis, so every query receives a distribution over allowed keys. Multiplying weights [Tq,Tk] by V [Tk,Dv] gives output [Tq,Dv]. The key and value row counts must match because each attention weight selects a corresponding value row. Query count need not equal key count in cross-attention, although this lesson's main self-attention fixture uses both equal to three.

The score rule is \(S=\frac{QK^{\mathsf T}}{\sqrt{D_k}}\). Stable softmax subtracts each row maximum before exponentiation. Subtracting a common row constant preserves the normalized probabilities, while reducing the risk of overflow. A Boolean allowed matrix has the score shape. Forbidden scores become negative infinity, giving zero exponential mass. Each query needs at least one allowed key: an all-forbidden row has no normalized distribution and is rejected instead of silently producing NaN.

For feature normalization of X:[B,T,D], the mean and variance have shape [B,T,1]. They reduce only D, leaving batch and token dimensions distinct. keepdims=True retains the singleton axis so subtraction broadcasts over the intended features. The variance here divides by D, not D-1, because the operation normalizes the features of this token rather than estimating a population variance from independent sampled cases. The output has the same shape as X. Its mean is zero up to floating-point error; its variance is \(\frac{\sigma^2}{\sigma^2+\epsilon}\), not exactly one when epsilon is positive.

### Deriving the permutation identity

Let P be a permutation matrix reordering token rows. Replacing Q,K,V by P Q,P K,P V gives scores P S \({P}^{T}\). This reorders both the query rows and the key columns. A row-wise softmax commutes with those reorders: \(\operatorname{softmax}(PSP^{\mathsf T})=P\operatorname{softmax}(S)P^{\mathsf T}\). The output is therefore \(P\operatorname{softmax}(S)P^{\mathsf T}PV=P\operatorname{softmax}(S)V\), because \({P}^{T}\) P is the identity. Reordering only Q, or forgetting to reorder V with K, is a different experiment and does not test this identity.

If a mask M is present, the corresponding relabelling identity requires reordering the mask too, as P M \({P}^{T}\). Keeping a causal triangle fixed is intentionally different: it keeps the visibility graph attached to row positions while moving content. Similarly, adding a fixed position table E gives input P X + E after a content reorder, while a pure reorder of the original positioned input would be \(P(X+E)=PX+PE\). Unless E happens to remain unchanged under P, those expressions differ.

## Exercise 1: Permute content-only attention

The question is: Use \(Q=K=[[1,0],[0,1],[1,1]]\) and \(V=[[1,2],[3,4],[5,6]]\). Reorder all three by [2,0,1] and compare outputs.

The first query has scores \([\frac{1}{\sqrt{2}},0,\frac{1}{\sqrt{2}}]\), so keys one and three receive equal weight. Their values are symmetric around [3,4], and the middle value is [3,4] itself, making the first weighted result exactly [3,4] in real arithmetic. The row permutation preserves these relationships. This is an unmasked calculation; a fixed causal triangle would change the experiment.

```python
query = np.array([[1., 0.], [0., 1.], [1., 1.]])
value = np.array([[1., 2.], [3., 4.], [5., 6.]])
order = np.array([2, 0, 1])
scores, weights, original = attention_parts(query, query, value)
changed = attention(query[order], query[order], value[order])
np.testing.assert_allclose(changed, original[order], atol=1e-12, rtol=0)
scale = np.exp(1 / np.sqrt(2))
expected_first_weights = np.array([scale, 1, scale]) / (2 * scale + 1)
np.testing.assert_allclose(weights[0], expected_first_weights, atol=1e-12, rtol=0)
np.testing.assert_allclose(original[0], [3, 4], atol=1e-12, rtol=0)
assert scores.shape == weights.shape == (3, 3)
assert original.shape == (3, 2)
```

**Expected:** attention weights move with key identities; output follows the same row reorder; the first original output is [3,4].

**Verify:** Compare the computed values or written argument with attention weights move with key identities; output follows the same row reorder; the first original output is [3,4].

## Exercise 2: Normalize each token

The question is: Normalize [[1,3],[10,20]] across each row, then replace only the second row with [1000,2000].

For [1,3], the mean is 2, centered features are [-1,1], and the mean squared centered value is 1. The second token uses a different mean and variance, but neither statistic appears in the first token calculation. Altering the future row cannot change the first normalized row. Positive epsilon makes the magnitude slightly below one.

```python
values = np.array([[1., 3.], [10., 20.]])
changed = values.copy()
changed[1] = [1000., 2000.]
normalized = layer_norm(values)
expected_first = np.array([-1., 1.]) / np.sqrt(1 + 1e-5)
np.testing.assert_allclose(normalized[0], expected_first, atol=1e-12, rtol=0)
np.testing.assert_allclose(layer_norm(changed)[0], normalized[0], atol=1e-12, rtol=0)
assert normalized.shape == values.shape
```

**Expected:** the first normalized row remains \(\frac{[-1,1]}{\sqrt{1+1\times10^{-5}}}\), approximately [-0.999995,0.999995].

**Verify:** Compare the computed values or written argument with the first normalized row remains \(\frac{[-1,1]}{\sqrt{1+1\times10^{-5}}}\), approximately [-0.999995,0.999995].

## Exercise 3: Expose sequence-wide leakage

The question is: Center each feature across the two token rows, then change the future row from [10,20] to [1000,2000].

The original feature means are [5.5,11.5]. Replacing the future row changes them to [500.5,1001.5], so subtracting those means changes the earlier row. There is no attention operation in this counterexample: the leakage is already present in preprocessing. This is why a mask test must be complemented by a full computation-path prefix test.

```python
values = np.array([[1., 3.], [10., 20.]])
changed = values.copy()
changed[1] = [1000., 2000.]
original_first = (values - values.mean(axis=0, keepdims=True))[0]
changed_first = (changed - changed.mean(axis=0, keepdims=True))[0]
np.testing.assert_array_equal(original_first, [-4.5, -8.5])
np.testing.assert_array_equal(changed_first, [-499.5, -998.5])
assert not np.allclose(original_first, changed_first)
```

**Expected:** the first centered row changes from [-4.5,-8.5] to [-499.5,-998.5].

**Verify:** Compare the computed values or written argument with the first centered row changes from [-4.5,-8.5] to [-499.5,-998.5].

## Exercise 4: Attach fixed positions

The question is: Add \(E=[[0,0],[1,0],[0,2]]\) to query/key content, then reorder content while keeping E attached to the original row positions.

The position vector is part of the input to the score computation. Moving content to a new location while preserving the location table is different from relabelling all rows of an already positioned representation. The fixture adds positions only to query/key construction to isolate score effects; a full Transformer commonly adds token and position representations before all projections, including values.

```python
query = np.array([[1., 0.], [0., 1.], [1., 1.]])
value = np.array([[1., 2.], [3., 4.], [5., 6.]])
positions = np.array([[0., 0.], [1., 0.], [0., 2.]])
order = np.array([2, 0, 1])
original = attention(query + positions, query + positions, value)
fixed_positions = attention(query[order] + positions, query[order] + positions, value[order])
assert not np.allclose(fixed_positions, original[order])
relabelled = attention((query + positions)[order], (query + positions)[order], value[order])
np.testing.assert_allclose(relabelled, original[order], atol=1e-12, rtol=0)
```

**Expected:** fixed-position outputs do not follow a pure content permutation; jointly reordering E restores the relabelling identity.

**Verify:** Compare the computed values or written argument with fixed-position outputs do not follow a pure content permutation; jointly reordering E restores the relabelling identity.

## Exercise 5: Check feature centering and causal prefixes

The question is: Check tokenwise means, then compare causal attention over normalized full input with recomputed prefixes.

Feature normalization does not mix token rows, and the triangle prevents attention from reading future keys, so the combined operation preserves every prefix. The fixed-mask permutation comparison changes which content occupies each causal prefix. This separates the visibility graph from the content-only equivariance theorem.

```python
values = np.array([[1., 2., 5.], [10., 20., 15.], [7., 0., -2.]])
normalized = layer_norm(values)
np.testing.assert_allclose(normalized.mean(axis=-1), 0, atol=1e-12, rtol=0)
allowed = np.tri(len(values), dtype=bool)
full = attention(normalized, normalized, normalized, allowed)
for length in [1, 2, 3]:
    prefix = layer_norm(values[:length])
    result = attention(prefix, prefix, prefix, np.tri(length, dtype=bool))
    np.testing.assert_allclose(result, full[:length], atol=1e-12, rtol=0)
order = np.array([2, 0, 1])
permuted = normalized[order]
fixed_mask = attention(permuted, permuted, permuted, allowed)
assert not np.allclose(fixed_mask, full[order])
```

**Expected:** row means are approximately zero and every causal prefix matches; fixed-mask content permutation need not match.

**Verify:** Compare the computed values or written argument with row means are approximately zero and every causal prefix matches; fixed-mask content permutation need not match.

## Exercise 6: Handle constant tokens and invalid normalization

The question is: Normalize [5,5], then reject an empty feature axis, zero epsilon and an all-forbidden attention row.

A constant token has zero centered values and zero variance. Positive epsilon produces a finite zero output. This stabilizer does not justify accepting an empty feature dimension, nonfinite data or a query with no allowed key. Rejecting these cases makes the cause observable instead of producing NaN and diagnosing it several layers later.

```python
constant = layer_norm(np.array([[5., 5.]]))
np.testing.assert_array_equal(constant, [[0., 0.]])
assert np.isfinite(constant).all()
for operation in [
    lambda: layer_norm(np.empty((2, 0))),
    lambda: layer_norm(np.array([[5., 5.]]), epsilon=0),
    lambda: attention(np.ones((1, 2)), np.ones((1, 2)), np.ones((1, 2)), np.zeros((1, 1), dtype=bool)),
]:
    try:
        operation()
    except ValueError:
        pass
    else:
        raise AssertionError('invalid contract was accepted')
```

**Expected:** constant token becomes finite [0,0]; each invalid contract raises ValueError.

**Verify:** Compare the computed values or written argument with constant token becomes finite [0,0]; each invalid contract raises ValueError.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
