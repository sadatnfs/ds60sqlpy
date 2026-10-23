# tf-025: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

An embedding objective encourages relationships between representations. Dot products depend on both direction and magnitude, whereas cosine divides by both vector norms and measures direction. A positive pair is declared related; a negative pair is declared unrelated under a sampling policy. That policy is part of the task. If a duplicate of the positive is labelled negative, the objective asks the model to satisfy contradictory evidence. A numerical loss can still be finite in this situation, so inspect identities before optimizing. The three fixed vectors let you calculate every score and show why a higher dot product is not always stronger directional similarity.

**Positive pair:** Two examples declared related by the training task.

**Negative pair:** An example pair declared unrelated under a sampling policy.

**Cosine similarity:** Dot product divided by the product of vector lengths.

## Reading the implementation

reduce_sum(a*b) is a dot product for equal-length vectors. Divide by norm(a)*norm(b) for cosine and reject a zero norm. A two-candidate contrastive loss can be written as sparse softmax cross entropy with target index0. Temperature divides scores before normalization. It changes the sharpness of probabilities and the scale of gradients, not which candidate initially ranks first.

## Exercise 1: Compare similarity measures

The question is: Use anchor[1,0],positive[1,1],negative[0,1]; compute dots and cosines.

The positive is not parallel to the anchor, so its cosine is below one despite a dot product of one. Magnitudes and directions should not be conflated.

```python
a=np.array([1.,0.]); pos=np.array([1.,1.]); neg=np.array([0.,1.])
assert (a@pos,a@neg)==(1,0)
np.testing.assert_allclose([(a@pos)/(np.linalg.norm(a)*np.linalg.norm(pos)),a@neg],[1/np.sqrt(2),0],atol=1e-12,rtol=0)
```

**Expected:** dots1,0; cosines1/sqrt2,0.

**Verify:** Compare the computed values or written argument with dots1,0; cosines1/sqrt2,0.

## Exercise 2: Scale a candidate

The question is: Multiply the positive vector by10 and compare dot product and cosine.

Scaling changes the unnormalized score but leaves direction unchanged. This demonstrates why normalization is a modeling choice with consequences for retrieval rankings.

```python
scaled=10*pos
assert a@scaled==10
np.testing.assert_allclose((a@scaled)/(np.linalg.norm(a)*np.linalg.norm(scaled)),1/np.sqrt(2),atol=1e-12,rtol=0)
```

**Expected:** dot10; cosine unchanged.

**Verify:** Compare the computed values or written argument with dot10; cosine unchanged.

## Exercise 3: Calculate a contrastive loss

The question is: Use logits[1,0] with the positive at index0.

The loss encourages the positive score to exceed the negative score. It does not independently establish that the selected negative is semantically unrelated.

```python
loss=tf.nn.sparse_softmax_cross_entropy_with_logits(labels=[0],logits=[[1.,0.]])
np.testing.assert_allclose(loss.numpy(),[np.log1p(np.exp(-1))],atol=1e-6,rtol=0)
```

**Expected:** losslog(1+exp(-1)).

**Verify:** Compare the computed values or written argument with losslog(1+exp(-1)).

## Exercise 4: Detect a false negative

The question is: Replace the negative vector and identity with the positive identity.

Identity checks belong before interpreting training loss. Two equal vectors may arise legitimately, but the same document explicitly labelled both positive and negative is a direct contradiction.

```python
positive_id='doc-a'; negative_id='doc-a'; duplicate=np.array_equal(pos,pos.copy())
assert duplicate and positive_id==negative_id
```

**Expected:** duplicate positive/negative identity is flagged.

**Verify:** Compare the computed values or written argument with duplicate positive/negative identity is flagged.

## Exercise 5: Observe temperature

The question is: Compare softmax[1,0] at temperatures1 and.5.

A lower positive temperature sharpens this distribution. It is not a source of additional evidence and must not be confused with a calibrated probability of semantic truth.

```python
p1=tf.nn.softmax([1.,0.]).numpy(); p2=tf.nn.softmax(np.array([1.,0.],dtype='float32')/.5).numpy()
assert p2[0]>p1[0] and int(p1.argmax())==int(p2.argmax())==0
```

**Expected:** positive probability increases at.5; ranking stays0 first.

**Verify:** Compare the computed values or written argument with positive probability increases at.5; ranking stays0 first.

## Exercise 6: Reject undefined cosine

The question is: Implement cosine with finite and nonzero-norm checks; pass a zero anchor.

Inventing zero similarity for a zero vector hides an undefined directional comparison. Rejecting it forces the caller to decide whether to skip, repair or represent missing information.

```python
def cosine(x,y):
    x,y=np.asarray(x),np.asarray(y); den=np.linalg.norm(x)*np.linalg.norm(y)
    if x.shape!=y.shape or not np.isfinite(den) or den==0: raise ValueError('finite nonzero vectors')
    return float(x@y/den)
try: cosine([0,0],[1,1])
except ValueError: pass
else: raise AssertionError('undefined cosine accepted')
```

**Expected:** ValueError for zero norm.

**Verify:** Compare the computed values or written argument with ValueError for zero norm.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
