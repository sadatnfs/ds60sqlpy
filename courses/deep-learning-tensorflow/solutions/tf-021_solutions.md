# tf-021: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A padded sequence contains both real observations and artificial storage positions. An embedding lookup turns token IDs into vectors, but padding does not become a real token merely because it has a vector. Carry a valid-token mask alongside the sequence. When averaging token losses, divide by the number of valid targets rather than the padded length. Appending more padding should leave the score unchanged. Some layers propagate Keras masks, while custom arithmetic must apply them explicitly. This lesson treats token zero as padding under a declared vocabulary policy; another vocabulary may assign zero a real meaning.

**Padding:** Artificial positions added to equalize storage shapes.

**Embedding:** A learned or fixed vector table indexed by token ID.

**Mask:** A boolean description of which positions participate.

## Reading the implementation

The boolean comparison ids!=0 identifies valid tokens. tf.gather selects embedding rows in token order. tf.where(mask,loss,0) suppresses padding contributions, then reduce_sum(mask) supplies the denominator. Reject a completely padded sequence because it has no observed target loss. Avoid assuming that a numerical zero vector is an adequate replacement for an explicit mask.

## Exercise 1: Mark valid positions

The question is: Use token IDs[2,3,0] with zero declared padding.

The mask derives from vocabulary semantics, not from the magnitude of an embedding vector. A real token could legitimately have a zero vector.

```python
ids = tf.constant([2, 3, 0])
mask = ids != 0
assert mask.numpy().tolist() == [True, True, False]
assert int(tf.reduce_sum(tf.cast(mask, tf.int32))) == 2
```

**Expected:** mask[True,True,False], count2.

**Verify:** Compare the computed values or written argument with mask[True,True,False], count2.

## Exercise 2: Normalize masked losses

The question is: Use token losses[log2,log2,100] and exclude the padding position.

The numerator and denominator must use the same participation policy. Zeroing the padding loss but dividing by three would understate the mean valid-token loss.

```python
losses = tf.constant([np.log(2), np.log(2), 100.0], dtype=tf.float64)
mean = tf.reduce_sum(tf.where(mask, losses, 0.0)) / tf.reduce_sum(tf.cast(mask, tf.float64))
np.testing.assert_allclose(float(mean), np.log(2), atol=1e-12, rtol=0)
```

**Expected:** masked meanlog2; padding loss100 has no effect.

**Verify:** Compare the computed values or written argument with masked meanlog2; padding loss100 has no effect.

## Exercise 3: Check embedding axes

The question is: Lookup IDs[2,3,0] in a fixed4x2 table.

Lookup preserves token order and appends the feature dimension. It does not mix tokens or establish any language understanding by itself.

```python
table = tf.constant([[0.0, 0.0], [1.0, 0.0], [2.0, 2.0], [3.0, -1.0]])
emb = tf.gather(table, ids)
assert tuple(emb.shape) == (3, 2)
np.testing.assert_array_equal(emb.numpy()[0], [2, 2])
```

**Expected:** output shape(3,2); first row[2,2].

**Verify:** Compare the computed values or written argument with output shape(3,2); first row[2,2].

## Exercise 4: Append padding

The question is: Add two padding IDs and arbitrary corresponding losses, then recalculate the masked mean.

Padding length is a storage choice. This metamorphic test catches any accidental use of padded length as the loss denominator.

```python
extended = tf.constant([2, 3, 0, 0, 0])
m = extended != 0
l = tf.constant([np.log(2), np.log(2), 100.0, 200.0, 300.0], tf.float64)
v = tf.reduce_sum(tf.where(m, l, 0.0)) / tf.reduce_sum(tf.cast(m, tf.float64))
np.testing.assert_allclose(float(v), float(mean), atol=1e-12, rtol=0)
```

**Expected:** mean unchanged atlog2.

**Verify:** Compare the computed values or written argument with mean unchanged atlog2.

## Exercise 5: Select the last valid state

The question is: For token states[[2,2],[3,-1],[99,99]], select the final valid position.

Indexing the last stored row confuses a padding slot with the last observation. The explicit mask keeps that distinction visible.

```python
states = tf.constant([[2.0, 2.0], [3.0, -1.0], [99.0, 99.0]])
valid_states = tf.boolean_mask(states, mask)
np.testing.assert_array_equal(valid_states[-1].numpy(), [3, -1])
```

**Expected:** state[3,-1], not padding state[99,99].

**Verify:** Compare the computed values or written argument with state[3,-1], not padding state[99,99].

## Exercise 6: Refuse an empty denominator

The question is: Write a masked-average helper and test an all-padding mask.

Returning zero for no targets would fabricate a perfect loss without any observations. Rejecting the case makes absence of evidence distinct from a measured zero error.

```python
def masked_mean(values, valid):
    values = np.asarray(values)
    valid = np.asarray(valid, dtype=bool)
    if values.shape != valid.shape or not valid.any():
        raise ValueError("valid targets required")
    return values[valid].mean()


try:
    masked_mean([1, 2], [False, False])
except ValueError:
    pass
else:
    raise AssertionError("empty denominator accepted")
```

**Expected:** ValueError for zero valid positions.

**Verify:** Compare the computed values or written argument with ValueError for zero valid positions.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
