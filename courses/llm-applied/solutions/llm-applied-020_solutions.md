# llm-applied-020: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Embedding and reranker fine-tuning adapts retrieval behavior rather than only answer generation. A bi-encoder maps queries and documents separately so document vectors can be indexed once. A cross-encoder or reranker jointly evaluates a query-document pair and is usually applied to a smaller candidate set. Contrastive training requires positives and negatives whose labels reflect the task. A false negative, such as another relevant passage labelled irrelevant, can teach contradictory geometry.

This chapter performs actual CPU updates on a small linear query projection and a separate pairwise reranker. Literal feature vectors stand in for encoded text so the gradient and ranking changes are inspectable. The bi-encoder objective makes each query favor its paired document over the other candidate. The reranker learns a scalar preference from two authored pair features. These are real trainable models, but they are not pretrained sentence encoders and do not establish semantic retrieval quality on natural language. Held-out domain evaluation remains necessary after any realistic fine-tuning.

**Bi-encoder:** Separate query and document encoders enabling reusable document vectors.

**Contrastive objective:** A loss favoring positive pairs over selected negatives.

**False negative:** A relevant pair incorrectly labelled as a negative example.

**Pairwise reranker:** A scorer trained to rank one candidate above another for a query.

## Reading the implementation

Compute query_embeddings=query_features@W andscore_matrix=query_embeddings@document_features.T. Cross entropy uses the diagonal document index as the positive label. Clear gradients and updateW under a fixed budget. For the reranker, score each pair with a linear weight and optimize softplus(-(positive_score-negative_score)). Inspect parameter changes, training loss and ranking separately. Freeze document features in this fixture so only the query projection is trained.

## Derive the first query-projection and reranker updates

Queries and documents are both the2-by-2 identity matrix, while W begins at zero. The score matrix \(QWD^{\mathsf T}\) is therefore W itself. Each row has uniform class probabilities[0.5, 0.5], and the labels are[0, 1]. Mean cross entropy across two rows gives gradient[[-0.25, 0.25], [0.25, -0.25]]. SGD at0.5 produces W=[[0.125, -0.125], [-0.125, 0.125]] after one update.

The positive-minus-negative score margin is 0.25 in both training rows. Symmetry preserves the form[[a, -a], [-a, a]] during this particular optimization, with positive a after the first step. For a new query[x, y], the two scores are[a(x-y), -a(x-y)], so the decision boundary is \(x=y\). The held-out[0.9, 0.1] lies well on the document0 side; after the first step its scores are[0.1, -0.1]. That is a local feature-space check, not a test of understanding a new sentence.

The cross-entropy derivative can be written \(\frac{Q^{\mathsf T}(P-Y)D}{B}\) for this fixed-feature linear projection, where P contains row probabilities, Y the one-hot targets and B the number of query rows. Its shape matches W. In a real trainable encoder, gradients would flow through encoder and embedding parameters for fixed tokenized inputs; ordinary discrete token IDs and the tokenizer are not differentiable parts of that graph. Here document features remain fixed and only four projection entries are updated.

The reranker has weight w=[w = 0, w1], positive feature[1, 0] and negative[0, 1]. Its score margin is w0-w1 and its loss is softplus(-(w0-w1)). At zero, the gradient is[-0.5, 0.5]. A0.2 SGD step produces[0.1, -0.1], giving margin0.2 and a smaller loss. This independent calculation shows what the pairwise objective favors without assuming the training loop's result.

A pairwise loss for one query should compare candidates under that same query's intended relevance. Mixing a positive from one question with a negative from an unrelated question can teach a shortcut unless the dataset design explicitly calls for it. In-batch negatives also assume that another row's positive is not a valid answer for the current query. Multiple correct passages or duplicated source families can violate that assumption.

The false-negative exercise detects that positive and negative IDs are identical. It does not supply a reusable admission function that automatically blocks all future training pairs. Different IDs can still refer to the same content or to two valid answers. Real admission needs identity, content/family and semantic relevance checks, with uncertainty preserved for review rather than forced into a negative label.

The trained models are small but real: parameters change under gradients and rankings are observed. Their input features are literal arrays, so they are not pretrained text encoders. Sentence representation training motivates this distinction between reusable encoders and pair scorers, but the local result does not inherit a natural-language benchmark score. [Sentence-BERT](https://arxiv.org/abs/1908.10084).

### Interview reasoning with explanatory answers

**Why can a hard negative be harmful?** If it is actually relevant, the objective pushes away evidence the system should retrieve. Hardness is a model score property; correctness of the negative label is a task property.

**Why evaluate candidate recall after reranker training?** A better ordering cannot recover evidence absent from the candidate set. Improvements at one stage must be measured under the full retrieval budget.

**What does the perturbed feature result establish?** The learned linear boundary behaves as expected at one nearby point with an authored label. It does not establish transfer to unseen document or language families.

## Exercise 1: Construct paired retrieval features

The question is: Use queries and documents equal to the 2-by-2 identity matrix, with positive labels 0, 1.

The identity fixture isolates learning the pairing. A real encoder receives text and requires a tokenizer, pooling policy and governed relevance labels.

```python
queries=torch.eye(2); documents=torch.eye(2); labels=torch.tensor([0,1]); projection=nn.Parameter(torch.zeros((2,2)))
scores=(queries@projection)@documents.T
assert tuple(scores.shape)==(2,2) and labels.tolist()==[0,1]
```

**Expected:** score shape(2, 2); one positive per query.

**Verify:** Compare the computed values or written argument with score shape(2, 2); one positive per query.

## Exercise 2: Train the query projection

The question is: Run30SGD.5 updates on cross entropy against diagonal positives.

The projection actually changes through gradients. The resulting training ranking is a mechanics check, not evidence of transfer to unseen language.

```python
opt=torch.optim.SGD([projection],lr=.5); initial=F.cross_entropy(scores,labels).item()
for _ in range(30):
    opt.zero_grad(set_to_none=True); scores=(queries@projection)@documents.T; loss=F.cross_entropy(scores,labels); loss.backward(); opt.step()
final_scores=(queries@projection)@documents.T
assert F.cross_entropy(final_scores,labels).item()<initial and final_scores.argmax(1).tolist()==[0,1]
```

**Expected:** loss decreases; each query ranks its paired document first.

**Verify:** Compare the computed values or written argument with loss decreases; each query ranks its paired document first.

## Exercise 3: Evaluate a perturbed held-out query

The question is: Use held-out feature[.9, .1] and compare its two document scores.

This tests one nearby feature perturbation under an authored relevance label. It is much narrower than evaluating new document families or real paraphrases.

```python
held=torch.tensor([[.9,.1]]); held_scores=(held@projection)@documents.T
assert held_scores.argmax(1).item()==0
```

**Expected:** document0 remains higher on this declared local perturbation.

**Verify:** Compare the computed values or written argument with document0 remains higher on this declared local perturbation.

## Exercise 4: Train a pairwise reranker

The question is: Use positive feature[1, 0], negative[0, 1] and a zero linear weight; run20SGD.2 updates.

The reranker objective compares candidates for one query. Its training data must distinguish relevance from superficial length or lexical artifacts.

```python
weight=nn.Parameter(torch.zeros(2)); positive=torch.tensor([1.,0.]); negative=torch.tensor([0.,1.]); optimizer=torch.optim.SGD([weight],lr=.2); first=F.softplus(-(positive@weight-negative@weight)).item()
for _ in range(20):
    optimizer.zero_grad(set_to_none=True); objective=F.softplus(-(positive@weight-negative@weight)); objective.backward(); optimizer.step()
assert positive@weight>negative@weight and F.softplus(-(positive@weight-negative@weight)).item()<first
```

**Expected:** positive score exceeds negative and pairwise loss decreases.

**Verify:** Compare the computed values or written argument with positive score exceeds negative and pairwise loss decreases.

## Exercise 5: Detect a false-negative identity

The question is: Assign the same document ID to positive and negative roles and identify the collision as a prospective admission failure.

A duplicated relevant passage can be a false negative even when filenames differ. Exact and family-level checks help prevent contradictory supervision.

```python
pair={'positive':'doc-a','negative':'doc-a'}
assert pair['positive']==pair['negative']
```

**Expected:** identity collision detected; this check is separate from the earlier training loops.

**Verify:** Compare the computed values or written argument with identity collision detected; this check is separate from the earlier training loops.

## Exercise 6: Bound the model claim

The question is: Record that fixed vectors were used and natural-language encoder quality was not measured.

A realistic next experiment should use pinned encoder weights, domain labels and held-out families while retaining these arithmetic and ranking checks.

```python
receipt={'query_projection_updates':30,'reranker_updates':20,'literal_feature_fixture':True,'pretrained_semantic_encoder':False,'natural_language_quality_measured':False}
assert receipt['query_projection_updates']==30 and not receipt['natural_language_quality_measured']
```

**Expected:** actual gradient updates True; pretrained_semantic_encoder False.

**Verify:** Compare the computed values or written argument with actual gradient updates True; pretrained_semantic_encoder False.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
