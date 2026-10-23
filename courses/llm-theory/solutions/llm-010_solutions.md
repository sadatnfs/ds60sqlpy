# llm-010: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Attention without positions or a causal boundary is equivariant to a joint permutation of tokens: changing input order simply changes output order. A decoder needs information about order, supplied by positional representations and by the causal mask. Those mechanisms have different roles. Position embeddings attach vectors to locations, while a causal mask restricts accessible locations. Normalization can accidentally defeat causality if it computes statistics across the whole sequence. Tokenwise LayerNorm reduces feature values within each position, so future tokens cannot alter an earlier token through that reduction. The fixture separates these effects instead of attributing every order dependency to position embeddings.

**Equivariance:** A transformation of inputs produces the corresponding transformation of outputs.

**Position embedding:** A vector associated with a token location.

**Tokenwise normalization:** Statistics calculated across features of one position.

## Reading the implementation

A joint permutation must be applied to Q,K,V together. Compare the permuted output with the same permutation of the original result. Tokenwise normalization uses axis=-1 with keepdims=True; sequence-wide normalization uses axis=0 and couples token rows. Add a fixed position table to content vectors before attention to break pure content permutation equivariance.

## Exercise 1: Permute content-only attention

The question is: Use Q=K[[1,0],[0,1],[1,1]],V[[1,2],[3,4],[5,6]]; jointly permute rows2,0,1.

The scores and value mixtures move with the token identities. This comparison uses unmasked attention; a causal mask itself introduces an order boundary.

```python
q=np.array([[1.,0.],[0.,1.],[1.,1.]]); v=np.array([[1.,2.],[3.,4.],[5.,6.]]); order=[2,0,1]
out=attention(q,q,v); changed=attention(q[order],q[order],v[order])
np.testing.assert_allclose(changed,out[order],atol=1e-12,rtol=0)
```

**Expected:** permuted output equals original output rows2,0,1.

**Verify:** Compare the computed values or written argument with permuted output equals original output rows2,0,1.

## Exercise 2: Normalize each token

The question is: Normalize rows[1,3] and[10,20] independently, then alter only the second row.

The first row uses only its own feature mean and variance. A future token has no opportunity to influence those quantities.

```python
x=np.array([[1.,3.],[10.,20.]]); changed=x.copy(); changed[1]=[1000,2000]
np.testing.assert_allclose(layer_norm(x)[0],layer_norm(changed)[0],atol=1e-12,rtol=0)
```

**Expected:** first normalized row unchanged.

**Verify:** Compare the computed values or written argument with first normalized row unchanged.

## Exercise 3: Expose sequence-wide leakage

The question is: Center each feature across both token rows, then repeat after changing the future row.

Reducing across time mixes future values into the statistics used by an earlier position. A correct attention mask cannot repair information already leaked by another component.

```python
assert not np.allclose((x-x.mean(0))[0],(changed-changed.mean(0))[0])
```

**Expected:** first centered row changes.

**Verify:** Compare the computed values or written argument with first centered row changes.

## Exercise 4: Attach fixed positions

The question is: Add position vectors[[0,0],[1,0],[0,2]]; permute content but keep positions fixed.

Moving content to a new location changes its positional representation. Permuting both content and position vectors together would instead move the whole annotated token and test a different condition.

```python
pos=np.array([[0.,0.],[1.,0.],[0.,2.]])
a=attention(q+pos,q+pos,v); b=attention(q[order]+pos,q[order]+pos,v[order])
assert not np.allclose(b,a[order])
```

**Expected:** outputs no longer follow a pure token permutation.

**Verify:** Compare the computed values or written argument with outputs no longer follow a pure token permutation.

## Exercise 5: Check feature centering

The question is: Inspect tokenwise normalized row means for the original fixture.

The per-row mean is the relevant invariant. A global mean of zero could also be produced by a leaking sequence-wide operation, so it is too weak by itself.

```python
np.testing.assert_allclose(layer_norm(x).mean(-1),[0,0],atol=1e-12,rtol=0)
```

**Expected:** each row mean approximately0.

**Verify:** Compare the computed values or written argument with each row mean approximately0.

## Exercise 6: Handle constant tokens

The question is: Normalize[5,5] with epsilon1e-5.

Epsilon handles a zero variance without introducing future-token information. The constant row becomes zero before any learned scale or offset is applied.

```python
np.testing.assert_array_equal(layer_norm(np.array([[5.,5.]])),[[0,0]])
```

**Expected:** finite vector[0,0].

**Verify:** Compare the computed values or written argument with finite vector[0,0].

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
