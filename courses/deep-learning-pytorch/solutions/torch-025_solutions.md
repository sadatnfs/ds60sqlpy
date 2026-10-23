# torch-025: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Embedding objectives teach a representation to preserve selected relationships. A positive pair is declared related under a task definition, while a negative pair is declared unrelated. Those labels are assumptions supplied by the dataset, not facts inferred from a similarity score. Dot products depend on vector magnitude and direction. Cosine similarity divides by both norms and compares direction. A high score can still belong to an irrelevant or duplicated example.

Contrastive cross entropy compares a positive candidate with selected negatives. Its temperature changes score concentration and gradient scale. False negatives can create contradictory supervision, especially when two document versions contain the same answer. This lesson uses literal vectors and an actual differentiable projection so the objective and gradient are inspectable. It does not claim that the tiny representation has learned natural-language semantics.

**Contrastive objective:** A loss encouraging a positive candidate to outrank chosen negatives.

**Cosine similarity:** A directional comparison normalized by vector lengths.

**False negative:** A related candidate incorrectly labeled unrelated.

## Reading the implementation

Use torch.dot for one-dimensional vectors and F.cosine_similarity with an explicit feature dimension. Check nonzero finite norms before interpreting cosine. Build a two-candidate logit row and use class index 0 for the positive. A trainable projection can receive gradients through these scores. Keep candidate identities beside vectors and reject a positive/negative identity collision before training.

## Derive the contrastive competition and its gradient

For nonzero vectors a and b, the dot product is sum_i a_i b_i and cosine is their dot divided by||a||||b||. With a=[1, 0], positive=[1, 1] and negative=[0, 1], the scores are 1 and 0, while cosines are 1/sqrt(2) and 0. Scaling the positive by ten increases its dot to ten without changing direction. That particular example keeps the ranking, but in general a large poorly aligned vector can outrank a small well-aligned vector under dot product and lose under cosine.

A zero vector has no direction. PyTorch's normalization/similarity APIs use an epsilon convention for numerical stability; receiving a finite number from that convention does not make a zero vector semantically informative. If the application requires directional similarity, validate finite nonzero norms and define a refusal or fallback policy. The paired TensorFlow chapter's explicit zero-norm rejection is a data contract, not a claim that every framework cosine API raises automatically. [PyTorch 2.9 normalize](https://docs.pytorch.org/docs/2.9/generated/torch.nn.functional.normalize.html).

Let candidates have scores s_j and let candidate 0 be the positive. For temperature tau>0, define p_j=exp(s_j/tau)/sum_k exp(s_k/tau). The loss is -log(p_0)=logsumexp(s/tau)-s_0/tau. Stable cross entropy computes this without manually exponentiating large logits. With scores[1, 0] and tau 1, p_0≈0.731059 and loss≈0.313262, which equals log(1+exp(-1)). With tau 0.5, the effective logits are[2, 0], p_0≈0.880797 and loss≈0.126928.

Positive temperature scaling preserves the ranking of fixed scores. It changes probabilities and the derivative dL/ds_j=(p_j-y_j)/tau. Lower temperature does not guarantee a larger gradient on every example, because the probabilities also change. For this already-correct pair, the positive-score derivative is approximately-0.268941 at tau 1 and-0.238406 at tau 0.5. Hard or incorrectly ranked examples can behave differently. Treat temperature as an objective and calibration choice, not a universal gradient amplifier.

The reference trains neither candidate vector in its projection check. It defines q=aP with an identity 2×2 trainable P, then uses the fixed positive and negative vectors as candidates. At tau 1, let c=1/(1+exp(1))≈0.268941. The query derivative is -c[1, 1]+c[0, 1]=[-c, 0]. Since a=[1, 0], the projection derivative is the outer product a^T[-c, 0], or[[-c, 0], [0, 0]]. Only the first projection row receives this contribution. This exact analytic matrix is stronger explanatory evidence than the reference's broad finite/nonzero assertion.

A shared encoder applied to the anchor and both candidates would have additional gradient paths. A symmetric contrastive objective would also evaluate reverse-direction comparisons. Those are different experiments from this one-branch projection check. The unchanged reference calls backward but does not take a projection optimizer step, so its evidence is differentiability and a local gradient, not a completed representation-learning run.

Negative sampling defines the competition. With M equal candidate scores, the loss is log(M), so changing the number of negatives changes the numerical baseline even when the representation is unchanged. Losses from two candidate-pool designs are not automatically comparable. In-batch negatives also couple examples: changing batch membership can change an anchor's objective even if its positive pair stays fixed. This is one reason microbatch gradient accumulation need not reproduce a larger in-batch contrastive batch.

If a positive and negative are literally the same vector under the same scoring path, their scores must agree. For a two-candidate loss, the positive probability is one-half and the opposing query-gradient terms cancel. The model cannot satisfy contradictory role labels through that shared representation. If the vectors are different views of the same relevant document, the model may instead learn a nuisance distinction. Identity checks catch exact collisions; family/version and relevance audits are needed for less obvious false negatives.

Several relevant candidates may require a multi-positive objective or a relevance-aware sampling policy rather than marking all but one as negative. Evaluation should keep the intended corpus, candidate count and exclusions visible. A high score is not an external truth label, and embeddings from different model/tokenizer/normalization versions should not be mixed merely because their dimensions match. Record the representation-space identity with any saved retrieval index.

## Exercise 1: Compare dot and cosine scores

The question is: Use anchor[1, 0], positive[1, 1], negative[0, 1].

The positive vector is not parallel to the anchor, so its cosine is below one. Equal-looking scalar scores from different similarity definitions need not mean the same relationship.

```python
anchor=torch.tensor([1.,0.],dtype=torch.float64); positive=torch.tensor([1.,1.],dtype=torch.float64); negative=torch.tensor([0.,1.],dtype=torch.float64)
assert torch.dot(anchor,positive).item()==1 and torch.dot(anchor,negative).item()==0
np.testing.assert_allclose(F.cosine_similarity(anchor,positive,dim=0).item(),1/np.sqrt(2),atol=1e-12,rtol=0)
```

**Expected:** dots 1, 0; cosines 1/sqrt 2, 0.

**Verify:** Compare the computed values or written argument with dots 1, 0; cosines 1/sqrt 2, 0.

## Exercise 2: Scale without changing direction

The question is: Multiply the positive vector by 10 and compare scores.

Normalization removes positive scale from this comparison. A model trained with unnormalized dot products may intentionally use magnitude, so normalization is a modeling choice.

```python
scaled=10*positive
assert torch.dot(anchor,scaled).item()==10
torch.testing.assert_close(F.cosine_similarity(anchor,scaled,dim=0),F.cosine_similarity(anchor,positive,dim=0),atol=1e-12,rtol=0)
```

**Expected:** dot becomes 10; cosine unchanged.

**Verify:** Compare the computed values or written argument with dot becomes 10; cosine unchanged.

## Exercise 3: Calculate a two-candidate loss

The question is: Use logits[1, 0] with target 0.

The loss depends on the relative score advantage. It does not verify whether the supplied positive and negative labels are semantically correct.

```python
logits=torch.tensor([[1.,0.]],dtype=torch.float64)
np.testing.assert_allclose(F.cross_entropy(logits,torch.tensor([0])).item(),np.log1p(np.exp(-1)),atol=1e-12,rtol=0)
```

**Expected:** cross entropy log(1+exp(-1)).

**Verify:** Compare the computed values or written argument with cross entropy log(1+exp(-1)).

## Exercise 4: Inspect a projection gradient

The question is: Create a trainable 2 x2identity projection and back propagate the positive-versus-negative objective.

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

The question is: Compare softmax[1, 0] at temperatures 1 and.5.

Temperature changes confidence concentration and gradients. It does not supply additional relevance evidence or guarantee calibration.

```python
warm=torch.softmax(logits,dim=1); cool=torch.softmax(logits/.5,dim=1)
assert cool[0,0]>warm[0,0] and warm.argmax(1).item()==cool.argmax(1).item()==0
```

**Expected:** positive probability increases; argmax remains 0.

**Verify:** Compare the computed values or written argument with positive probability increases; argmax remains 0.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
