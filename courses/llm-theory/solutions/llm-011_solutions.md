# llm-011: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Multiple attention heads give a token several separately normalized views of its permitted context. Each head forms its own query/key comparisons and weighted value mixture. The outputs are concatenated along the feature dimension and then commonly mixed by a learned output projection. A head is not a separate sentence segment, and two heads do not imply that each sees half the tokens. Both can see the complete allowed prefix while using different projected features.

This chapter first treats head splitting as a layout operation, then performs an actual small NumPy multi-head attention calculation. The attention fixture uses identity query/key/value projections so the feature slices are directly inspectable. A real Transformer learns those projections before splitting; its heads can use different linear combinations of the original representation rather than being restricted to raw feature groups. The fixed identity fixture teaches the mechanism without pretending its feature groups are learned semantic concepts.

Residual connections and feed-forward networks complete different parts of the block. A residual adds a branch result back to its input and therefore requires matching shapes and meanings. It does not concatenate the two vectors. A tokenwise feed-forward network applies shared affine maps and a nonlinearity to each token independently. It can transform contextual features already mixed by attention without introducing another direct reduction across token positions.

The next decoder chapter combines these operations with learned embeddings, positional information and normalization. Here the goals are narrower and inspectable: preserve feature membership while splitting and joining, compute distinct head distributions, prove a causal-prefix property through the actual attention operation, and distinguish a valid residual sum from a shape-compatible but semantically wrong layout.

**Attention head:** A separately normalized query/key/value computation over permitted token positions.

**Head width:** The feature dimension assigned to one head under a declared layout.

**Concatenation:** Joining head features while preserving each token row.

**Residual addition:** Adding a shape-compatible branch output back to its input.

**Tokenwise feed-forward network:** Shared nonlinear feature processing applied independently at each token.

## Reading the implementation

### Trace the split and inverse

For X:[T,D] with T=2,D=4,H=2, the head width is \(d=\frac{D}{H}=2\). Reshape [2,4] to [2,2,2] interpreted as [token,head,head_feature], then transpose to [head,token,head_feature]. These dimensions happen to have the same sizes, making axis names more informative than the printed shape alone.

With rows [0,1,2,3] and [4,5,6,7], head zero contains [[0,1],[4,5]], while head one contains [[2,3],[6,7]]. The inverse must first transpose [head,token,feature] back to [token,head,feature], then merge the last two axes. Flattening the head-major tensor directly instead creates rows [0,1,4,5] and [2,3,6,7]. Both arrays have shape [2,4], but the wrong version mixes features from different tokens.

### Compute attention within each head

The batched multiplication Q_h \({K_{h}}^{T}\) produces [H,T,T], one query-by-key matrix for each head. The normalization axis is the final key axis. For a width-two head the scale is \(\sqrt{2}\), and a causal Boolean triangle [T,T] broadcasts across the head axis. Multiplying weights [H,T,T] by V [H,T,2] returns [H,T,2]. Rejoining produces [T,4], preserving the width needed by a residual path.

For the three-token identity-projection fixture, head zero contains [1,0],[0,1],[1,1], while head one contains [1,1],[1,0],[0,1]. At query row one, the causal mask permits keys zero and one. Head zero has scores \([0,\frac{1}{\sqrt{2}}]\) and weights \([\frac{1}{1+a},\frac{a}{1+a}]\) with \(a=\exp(\frac{1}{\sqrt{2}})\). Head one has equal allowed scores \([\frac{1}{\sqrt{2}},\frac{1}{\sqrt{2}}]\) and weights \([\frac{1}{2},\frac{1}{2}]\). Their mixtures are therefore approximately [0.33023845,0.66976155] and exactly [1,0.5]. Concatenation gives [0.33023845,0.66976155,1,0.5] before any learned output projection.

### Residual and feed-forward equations

A residual computes R(x)=x+F(x). If F(x)=2x, R(x)=3x and its Jacobian is 3I. If F(x)=0, the residual is the identity. If F(x)=-x, the sum is zero and the Jacobian is zero. Thus the identity contribution can improve the available path, but a residual connection is not a universal proof against vanishing, exploding or cancelled gradients.

A usual feed-forward branch has F(x_t)=activation(x_t W1+b1) W2+b2, using the same weights at every token t. W1 can expand the hidden feature width and W2 return it to D for residual addition. The teaching fixture chooses identity weights and \(b_{1}=-2\) so the first row [0,1,2,3] becomes [0,0,0,1]. This isolates nonlinearity and tokenwise independence. A pair of affine maps without a nonlinearity collapses to one affine map; adding width alone would not create that nonlinear behavior.

## Exercise 1: Split and rejoin

The question is: Split \(X=[[0,1,2,3],[4,5,6,7]]\) into two heads, inspect membership, then invert the layout.

Axis membership is the actual contract. Here every dimension has size two, so shape checks alone cannot distinguish a correct transpose from an incorrect one. Exact element placement supplies the missing evidence.

```python
values = np.arange(8).reshape(2, 4)
heads = split_heads(values, 2)
np.testing.assert_array_equal(heads[0], [[0, 1], [4, 5]])
np.testing.assert_array_equal(heads[1], [[2, 3], [6, 7]])
np.testing.assert_array_equal(join_heads(heads), values)
assert heads.shape == (2, 2, 2)
```

**Expected:** head zero is [[0,1],[4,5]], head one is [[2,3],[6,7]], and rejoining restores X exactly.

**Verify:** Compare the computed values or written argument with head zero is [[0,1],[4,5]], head one is [[2,3],[6,7]], and rejoining restores X exactly.

## Exercise 2: Calculate a residual

The question is: Add branch 2X to X, then compare with zero and cancelling branches.

Residual addition does not concatenate or double feature width. The cancelling branch is a counterexample to the idea that an identity skip always guarantees a nonzero final derivative or representation.

```python
values = np.arange(8).reshape(2, 4)
branch = 2 * values
residual = values + branch
np.testing.assert_array_equal(residual, 3 * values)
np.testing.assert_array_equal(values + np.zeros_like(values), values)
np.testing.assert_array_equal(values + (-values), np.zeros_like(values))
assert residual.shape == values.shape
```

**Expected:** 2X gives 3X, zero branch gives X, and branch -X gives zero; all retain the same shape.

**Verify:** Compare the computed values or written argument with 2X gives 3X, zero branch gives X, and branch -X gives zero; all retain the same shape.

## Exercise 3: Use a tokenwise nonlinear block

The question is: Apply the explicit identity-weight, bias-minus-two feed-forward branch to two token rows.

The nonlinearity changes feature behavior, while shared tokenwise application preserves independence across token rows. Context mixing is supplied by the attention branch, not by secretly reducing the time axis here.

```python
values = np.arange(8, dtype=np.float64).reshape(2, 4)
output = tokenwise_feed_forward(values)
np.testing.assert_array_equal(output[0], [0, 0, 0, 1])
changed = values.copy()
changed[1] = [100, 200, 300, 400]
np.testing.assert_array_equal(tokenwise_feed_forward(changed)[0], output[0])
```

**Expected:** first output [0,0,0,1]; changing the second token does not change the first output.

**Verify:** Compare the computed values or written argument with first output [0,0,0,1]; changing the second token does not change the first output.

## Exercise 4: Test actual head mixtures and causal prefixes

The question is: Run the three-token four-feature fixture through two causal heads and compare independently recomputed prefixes.

This check exercises real score normalization and value mixing, extending the earlier tokenwise-only prefix check. The analytic row-one expectation is an independent oracle for head identity and the softmax axis. Prefix equality then checks the visibility boundary.

```python
values = np.array([[1., 0., 1., 1.], [0., 1., 1., 0.], [1., 1., 0., 1.]])
output, weights = multihead(values, heads=2, causal=True)
a = np.exp(1 / np.sqrt(2))
np.testing.assert_allclose(weights[0, 1, :2], [1 / (1 + a), a / (1 + a)], atol=1e-12, rtol=0)
np.testing.assert_allclose(weights[1, 1, :2], [0.5, 0.5], atol=1e-12, rtol=0)
np.testing.assert_array_equal(weights[:, 1, 2], [0, 0])
np.testing.assert_allclose(output[1], [1 / (1 + a), a / (1 + a), 1, 0.5], atol=1e-12, rtol=0)
for length in [1, 2, 3]:
    prefix, _ = multihead(values[:length], heads=2, causal=True)
    np.testing.assert_allclose(prefix, output[:length], atol=1e-12, rtol=0)
```

**Expected:** head distributions differ as derived, row-one output is \([\frac{1}{1+a},\frac{a}{1+a},1,0.5]\), and every prefix matches.

**Verify:** Compare the computed values or written argument with head distributions differ as derived, row-one output is \([\frac{1}{1+a},\frac{a}{1+a},1,0.5]\), and every prefix matches.

## Exercise 5: Reject an indivisible width

The question is: Call the split helper with width 5 and two heads, then with zero heads and an empty token axis.

A head dimension must be a positive integer under the fixed-width partition. Silently dropping or padding features would define a different representation and needs an explicit design, not an accidental reshape workaround.

```python
for values, count in [(np.zeros((2, 5)), 2), (np.zeros((2, 4)), 0), (np.zeros((0, 4)), 2)]:
    try:
        split_heads(values, count)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid head layout accepted')
```

**Expected:** each invalid layout raises ValueError before reshape.

**Verify:** Compare the computed values or written argument with each invalid layout raises ValueError before reshape.

## Exercise 6: Detect a wrong rejoin

The question is: Flatten the head-major tensor directly and compare values with the correctly inverted transpose.

Element count and final shape are necessary but insufficient. A semantic axis mistake can preserve both while routing one token's features into another token's representation.

```python
values = np.arange(8).reshape(2, 4)
heads = split_heads(values, 2)
wrong = heads.reshape(2, 4)
np.testing.assert_array_equal(wrong, [[0, 1, 4, 5], [2, 3, 6, 7]])
assert wrong.shape == values.shape
assert not np.array_equal(wrong, values)
np.testing.assert_array_equal(join_heads(heads), values)
```

**Expected:** the wrong [2,4] result differs despite matching shape; the inverse operation restores X.

**Verify:** Compare the computed values or written argument with the wrong [2,4] result differs despite matching shape; the inverse operation restores X.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
