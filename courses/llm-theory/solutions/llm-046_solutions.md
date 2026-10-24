# llm-046: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Attention architecture and attention execution are separate design dimensions. Multi-head attention, MHA, uses distinct query, key and value heads. Multi-query attention, MQA, shares one key/value head across query heads. Grouped-query attention, GQA, uses an intermediate number of key/value heads, with several query heads sharing each pair. The query-head count can remain fixed while cached key/value storage shrinks. This changes the representation constraint, so replacing arbitrary MHA weights with shared heads does not guarantee identical model quality or outputs.

FlashAttention addresses a different problem: how to execute exact attention while reducing expensive memory traffic. Its GPU implementations use tiling and hardware-aware scheduling. A useful mathematical ingredient is an online softmax normalizer that updates a running maximum, denominator and weighted-value numerator across blocks. This allows the exact output to be accumulated without retaining the entire score matrix.

The reference here implements grouped head selection and blockwise stable attention in NumPy. It verifies algebraic parity with a dense oracle and reports the largest score block used by the routine. It is not a FlashAttention kernel, does not benchmark a GPU, and does not claim that the whole test process avoids dense allocations because the independent oracle deliberately constructs them.

**MHA:** Attention with one key/value head per query head.

**MQA:** Attention sharing one key/value head across all query heads.

**GQA:** Attention sharing key/value heads within groups of query heads.

**Online softmax state:** A running maximum,normalizer and weighted-value numerator.

**IO-aware kernel:** An implementation designed around memory hierarchy and traffic,not only arithmetic count.

## Reading the implementation

For the single-batch reference, Q has shape(Hq, T, d), K shape(Hkv, T, d), and V shape(Hkv, T, dv), with Hq divisible by Hkv. Query head h uses key/value head h//(Hq/Hkv). The dense helper normalizes allowed keys per query. The online helper processes legal key blocks, skips blocks with no allowed keys, and rescales old accumulated state whenever a larger score appears. It rejects an entirely masked row rather than returning an invented distribution.

The online implementation checks its weighted-value numerator and denominator after every block, then checks the divided output. It raises ValueError when these intermediates exceed finite floating-point range, even if another evaluation order could produce a representable final average. Finite inputs and scores alone do not guarantee a finite unnormalized numerator.

## Exercise 1: Count cache and projection dimensions

The question is: Use batch 1, time 5, query heads4, head width 2, float32, and compare KV heads 4, 2, 1.

The cache factor2 counts keys and values. These are raw tensor/weight counts excluding allocator, activation, quantization-metadata and communication overhead.

```python
query_heads=4; head_width=2; width=8; time=5
cache_bytes=[2*1*time*kv_heads*head_width*4 for kv_heads in [4,2,1]]
parameters=[width*(query_heads*head_width)+2*width*(kv_heads*head_width)+(query_heads*head_width)*width for kv_heads in [4,2,1]]
assert cache_bytes==[320,160,80] and parameters==[256,192,160]
```

**Expected:** raw KV bytes 320, 160, 80; projection weights 256, 192, 160 for model width 8 without biases.

**Verify:** Compare the computed values or written argument with raw KV bytes 320, 160, 80; projection weights 256, 192, 160 for model width 8 without biases.

## Exercise 2: Verify grouped heads against an equivalent repeated-head oracle

The question is: Use 4 query heads and 2 KV heads; repeat each KV head twice only in the dense oracle.

The comparison manufactures identical shared heads, so parity is expected. It does not say that an arbitrary trained four-KV-head model can be compressed to two heads without changing behavior.

```python
q=np.arange(24,dtype=float).reshape(4,3,2)/10
k=np.arange(12,dtype=float).reshape(2,3,2)/7
v=np.array([[[1.,0.],[0.,2.],[3.,1.]],[[2.,1.],[1.,4.],[5.,2.]]])
grouped=gqa(q,k,v)
expanded_k=np.repeat(k,2,axis=0); expanded_v=np.repeat(v,2,axis=0)
oracle=np.stack([dense(q[h],expanded_k[h],expanded_v[h],np.tri(3,dtype=bool)) for h in range(4)])
assert grouped.shape==(4,3,2); np.testing.assert_allclose(grouped,oracle,atol=1e-12,rtol=0)
```

**Expected:** outputs agree within 1e-12; shape(4, 3, 2).

**Verify:** Compare the computed values or written argument with outputs agree within 1e-12; shape(4, 3, 2).

## Exercise 3: Trace online softmax at extreme scores

The question is: Combine scores 1000, 999, 998 and values 1, 3, 5 in blocks of 2.

When the running maximum changes, the old numerator and denominator must both be rescaled. Updating only one produces a plausible but incorrect weighted average.

```python
scores=np.array([1000.,999.,998.]); values=np.array([[1.],[3.],[5.]])
online,peak=online_row(scores,values,2)
mass=np.exp(np.array([0.,-1.,-2.])); expected=(mass@values)/mass.sum()
np.testing.assert_allclose(online,expected,atol=1e-12,rtol=0); assert peak==2 and np.isfinite(online).all()
```

**Expected:** finite output equals a maximum-shifted dense calculation.

**Verify:** Compare the computed values or written argument with finite output equals a maximum-shifted dense calculation.

## Exercise 4: Compare several block sizes under causal masking

The question is: Use five nonuniform query/key rows and compare block sizes 1, 2, 3, 5 with dense attention.

The odd length exercises a partial final block. The mask makes some early-row blocks empty, which the implementation must skip without generating negative-infinity subtractionNaNs.

```python
queries=np.array([[1.,0.],[0.,1.],[1.,1.],[-1.,2.],[2.,-1.]])
keys=np.array([[2.,0.],[1.,1.],[0.,2.],[-1.,1.],[1.,-2.]])
values=np.arange(10,dtype=float).reshape(5,2); allowed=np.tri(5,dtype=bool); expected=dense(queries,keys,values,allowed)
for block in [1,2,3,5]:
    output,peak=online_attention(queries,keys,values,allowed,block)
    np.testing.assert_allclose(output,expected,atol=1e-12,rtol=0); assert peak<=block
```

**Expected:** all outputs agree within 1e-12; largest temporary score block does not exceed the chosen size.

**Verify:** Compare the computed values or written argument with all outputs agree within 1e-12; largest temporary score block does not exceed the chosen size.

## Exercise 5: Preserve a causal prefix under future changes

The question is: Change only value rows 3 and 4 and compare the first three online outputs.

Block processing must preserve the same information boundary as dense attention. Tiling is not permission to normalize with future values or include masked keys in the denominator.

```python
changed=values.copy(); changed[3:]+=100
altered,_=online_attention(queries,keys,changed,allowed,2)
np.testing.assert_allclose(altered[:3],expected[:3],atol=1e-12,rtol=0)
```

**Expected:** first three rows unchanged.

**Verify:** Compare the computed values or written argument with first three rows unchanged.

## Exercise 6: Reject invalid grouping and empty support

The question is: Try 4 query heads with 3 KV heads, and an all-false attention row.

Head mapping needs an integer group size, and each query needs at least one legal key. Clear validation separates architecture misuse from numerical-kernel failure.

```python
try: gqa(np.zeros((4,2,2)),np.zeros((3,2,2)),np.zeros((3,2,2)))
except ValueError: pass
else: raise AssertionError('indivisible head grouping accepted')
bad=allowed.copy(); bad[0]=False
try: online_attention(queries,keys,values,bad,2)
except ValueError: pass
else: raise AssertionError('empty attention support accepted')
```

**Expected:** both raise ValueError; no output NaNs are accepted.

**Verify:** Compare the computed values or written argument with both raise ValueError; no output NaNs are accepted.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
