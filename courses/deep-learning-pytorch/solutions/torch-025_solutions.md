# torch-025: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Embedding objectives teach a representation to preserve selected relationships. A positive pair is declared related under a task definition, while a negative pair is declared unrelated. Those labels are assumptions supplied by the dataset, not facts inferred from a similarity score. Dot products depend on vector magnitude and direction. Cosine similarity divides by both norms and compares direction. A high score can still belong to an irrelevant or duplicated example.

Contrastive cross entropy compares a positive candidate with selected negatives. Its temperature changes score concentration and gradient scale. False negatives can create contradictory supervision, especially when two document versions contain the same answer. This lesson uses literal vectors and an actual differentiable projection so the objective and gradient are inspectable. It does not claim that the tiny representation has learned natural-language semantics.

**Contrastive objective:** A loss encouraging a positive candidate to out rank chosen negatives.

**Cosine similarity:** A directional comparison normalized by vector lengths.

**False negative:** A related candidate incorrectly label led unrelated.

## Reading the implementation

Use torch.dot for one-dimensional vectors and F.cosine_similarity with an explicit feature dimension. Check nonzero finite norms before interpreting cosine. Build a two-candidate logit row and use class index0 for the positive. A trainable projection can receive gradients through these scores. Keep candidate identities beside vectors and reject a positive/negative identity collision before training.

## Exercise 1: Compare dot and cosine scores

The question is: Use anchor[1, 0], positive[1, 1], negative[0, 1].

The positive vector is not parallel to the anchor, so its cosine is below one. Equal-looking scalar scores from different similarity definitions need not mean the same relationship.

```python
anchor=torch.tensor([1.,0.],dtype=torch.float64); positive=torch.tensor([1.,1.],dtype=torch.float64); negative=torch.tensor([0.,1.],dtype=torch.float64)
assert torch.dot(anchor,positive).item()==1 and torch.dot(anchor,negative).item()==0
np.testing.assert_allclose(F.cosine_similarity(anchor,positive,dim=0).item(),1/np.sqrt(2),atol=1e-12,rtol=0)
```

**Expected:** dots1, 0; cosines1/sqrt2, 0.

**Verify:** Compare the computed values or written argument with dots1, 0; cosines1/sqrt2, 0.

## Exercise 2: Scale without changing direction

The question is: Multiply the positive vector by 10 and compare scores.

Normalization removes positive scale from this comparison. A model trained with unnormalized dot products may intentionally use magnitude, so normalization is a modeling choice.

```python
scaled=10*positive
assert torch.dot(anchor,scaled).item()==10
torch.testing.assert_close(F.cosine_similarity(anchor,scaled,dim=0),F.cosine_similarity(anchor,positive,dim=0),atol=1e-12,rtol=0)
```

**Expected:** dot becomes10; cosine unchanged.

**Verify:** Compare the computed values or written argument with dot becomes10; cosine unchanged.

## Exercise 3: Calculate a two-candidate loss

The question is: Use logits[1, 0] with target0.

The loss depends on the relative score advantage. It does not verify whether the supplied positive and negative labels are semantically correct.

```python
logits=torch.tensor([[1.,0.]],dtype=torch.float64)
np.testing.assert_allclose(F.cross_entropy(logits,torch.tensor([0])).item(),np.log1p(np.exp(-1)),atol=1e-12,rtol=0)
```

**Expected:** cross entropy log(1+exp(-1)).

**Verify:** Compare the computed values or written argument with cross entropy log(1+exp(-1)).

## Exercise 4: Inspect a projection gradient

The question is: Create a trainable2 x2 identity projection and back propagate the positive-versus-negative objective.

This is an actual gradient path through the representation. It establishes the optimization mechanism, not held-out retrieval quality.

```python
projection=nn.Parameter(torch.eye(2,dtype=torch.float64)); query=anchor@projection
scores=torch.stack([query@positive,query@negative])[None,:]
F.cross_entropy(scores,torch.tensor([0])).backward()
assert projection.grad is not None and torch.isfinite(projection.grad).all() and torch.count_nonzero(projection.grad)>0
```

**Expected:** finite nonzero projection gradient.

**Verify:** Compare the computed values or written argument with finite nonzero projection gradient.

## Exercise 5: Detect contradictory candidate identity

The question is: Assign the same document ID to positive and negative roles.

A duplicate can remain contradictory even when its text or vector representation differs. Check source families as well as exact IDs in a realistic corpus.

```python
pair={'positive':'doc-a','negative':'doc-a'}
assert pair['positive']==pair['negative']
```

**Expected:** identity collision detected.

**Verify:** Compare the computed values or written argument with identity collision detected.

## Exercise 6: Separate temperature from ranking

The question is: Compare softmax[1, 0] at temperatures1 and.5.

Temperature changes confidence concentration and gradients. It does not supply additional relevance evidence or guarantee calibration.

```python
warm=torch.softmax(logits,dim=1); cool=torch.softmax(logits/.5,dim=1)
assert cool[0,0]>warm[0,0] and warm.argmax(1).item()==cool.argmax(1).item()==0
```

**Expected:** positive probability increases; argmax remains0.

**Verify:** Compare the computed values or written argument with positive probability increases; argmax remains0.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
