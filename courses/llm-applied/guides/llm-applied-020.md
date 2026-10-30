# llm-applied-020: Fine-tuning embeddings and a small reranker

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-019`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Retrieval adaptation learns which evidence should be nearby or highly ranked for a question. This chapter develops domain relevance labels, positive and negative construction, contrastive objectives and index consistency, connecting the tiny gradient example to a realistic retrieval-training study.

## Purpose and mental model

Embedding and reranker fine-tuning adapts retrieval behavior rather than only answer generation. A bi-encoder maps queries and documents separately so document vectors can be indexed once. A cross-encoder or reranker jointly evaluates a query-document pair and is usually applied to a smaller candidate set. Contrastive training requires positives and negatives whose labels reflect the task. A false negative, such as another relevant passage labelled irrelevant, can teach contradictory geometry.

This chapter performs actual CPU updates on a small linear query projection and a separate pairwise reranker. Literal feature vectors stand in for encoded text so the gradient and ranking changes are inspectable. The bi-encoder objective makes each query favor its paired document over the other candidate. The reranker learns a scalar preference from two authored pair features. These are real trainable models, but they are not pretrained sentence encoders and do not establish semantic retrieval quality on natural language. Held-out domain evaluation remains necessary after any realistic fine-tuning.

## Train the relationship the analyst actually needs

The Methods Desk repeatedly retrieves a general variance passage when the question concerns uncertainty for repeated visits within accounts. This may be a representation gap rather than an answer-model gap. A retrieval-training example can pair that question with the relevant account-level method passage and distinguish it from a topically similar but unsuitable passage.

Relevance is conditional on the query. A visit-level analysis page can be useful for a different experiment and a negative candidate for this account-level question. Labeling the whole document as globally bad would lose that distinction. Store the query, positive evidence, negative candidate, source identities and the reason the pair expresses the intended task.

The task may have several valid positive passages. One can state the rule directly, while another supplies an equivalent explanation under the same assumptions. Treating every nonselected passage as negative can push away useful evidence. Annotation should preserve alternatives and uncertainty rather than force all candidates into a single-positive classification merely because the loss interface makes that convenient.

## Understand what the contrastive denominator means

For a query q, a common single-positive contrastive objective is the negative log of \(\exp\!\left(\frac{\operatorname{score}(q,d_+)}{\tau}\right)\) divided by the sum of those exponentials over the candidate documents. The denominator defines the alternatives the model must distinguish. The temperature tau changes the scale of score differences and the gradient, so it is part of the objective rather than a display parameter.

With two identical scores, the positive probability is one-half and the loss is log2. With three identical scores and one designated positive, the loss is log3. A change in negative-set size can therefore change the initial loss scale even when the representation has not improved or worsened. Compare ranking and held-out relevance beside the optimization curve.

A false negative can make the task contradictory. If the positive and negative are the same document under the same representation, their scores cannot be separated by changing a shared encoder. With only those two identical candidates and a single-positive target, the probability remains one-half. A multi-positive formulation or corrected labels may be appropriate, depending on the actual evidence relationship. More training cannot resolve a contradiction created by the dataset definition.

The tiny reference uses two fixed identity-feature pairs, so the first gradient can be derived exactly. It establishes that the optimizer changes the projection in the direction implied by the labels. It does not establish a tokenizer, a pretrained semantic representation or a domain benchmark. The later held-out feature probe tests one point relative to the learned linear boundary.

## Mine difficult cases without turning them into wrong labels

Random negatives can be easy enough that the model learns only broad topic differences. Hard negatives are candidates a retriever currently ranks highly despite their being unsuitable under the task. They can expose the fine distinctions the assistant needs, such as account versus visit units, a superseded definition or a missing exception.

Hardness does not establish incorrectness. A highly ranked candidate may be another valid answer or may contain the relevant fact in a different span. Review those cases before using them as negative supervision. Exact IDs help detect direct collisions, while content and family relationships can reveal near-duplicates or alternative positives with different filenames.

Mining also belongs to the development history. Record which retriever and corpus snapshot produced the candidates. Keep final assessment labels out of training and selection. A retrieval corpus may legitimately contain documents used during evaluation, but using their held-out relevance judgments to construct training pairs changes the independence claim.

## A reranker learns a different interface

A bi-encoder supports reusable document vectors and relatively cheap candidate search. A reranker can jointly inspect a query-candidate pair and learn a more detailed ordering inside a bounded pool. A pairwise objective such as softplus of the negative positive-minus-negative score margin rewards the chosen candidate over the rejected candidate for that query.

That relative score does not automatically calibrate across queries. A high score for one easy query and a lower score for another can reflect different score distributions rather than different probabilities of relevance. If the application needs an answerability threshold, calibrate and evaluate that decision separately under the relevant request population.

The candidate ceiling remains. A well-trained reranker cannot recover evidence absent from its input unless the system explicitly performs another admitted retrieval step. Report candidate recall, reranked ordering and final-context sufficiency separately. Otherwise an answer-stage failure may be incorrectly attributed to the component that merely received an incomplete pool.

## Rebuild the serving representation after adaptation

Updating an encoder changes the coordinate system used for retrieval. Query and document representations must remain a compatible pair. If document vectors are produced by an old encoder while the query side uses a new incompatible one, dimensions can still match and the scores can still be finite. Those arithmetic facts do not establish meaningful similarity.

A release should bind encoder identity, tokenizer/preprocessing, pooling, normalization and index build. Evaluate exact vector search before attributing a miss to an approximate index. Retain lexical and unadapted baselines so a domain adaptation that helps paraphrases but harms exact identifiers is visible.

Finally, measure the effect on the assistant's answers. A retriever can improve its own ranking metric while supplying context the generator misuses. The complete task still requires supported claims, valid calculations and appropriate abstention. Retrieval training is one targeted intervention in that evidence path, not a replacement for its other contracts.

## Design decisions and when to use this method

Fine-tune retrieval models when error analysis shows that the representation or pair scorer systematically misses domain relevance despite sound chunking and metadata. Choose negatives carefully: random negatives may be too easy, while hard negatives may contain relevant alternatives. Label quality and domain coverage often matter more than increasing the number of updates.

Do not train a retriever on the final relevance benchmark and then present its score as independent evidence. Split query/document families before mining negatives. Compare lexical, unadapted embedding, adapted embedding and reranked variants under matched candidate budgets. Track recall, ranking quality, unsupported-answer rate and resource cost. A better retriever can still feed a generator that ignores evidence, so answer evaluation remains a separate stage.

Adapt the stage that error analysis identifies. A query projection can change retrieval geometry, while a reranker changes ordering inside a candidate set. Preserve a frozen lexical and unadapted-vector baseline, and evaluate whether the improved retrieval actually supplies better evidence to the answer stage.

Treat negative selection as part of the supervised task. A visually similar passage can be an excellent hard negative or another relevant answer. Decide that from relevance labels and source-family relationships before optimizing the contrastive loss.

## Vocabulary and concepts

**Bi-encoder:** Separate query and document encoders enabling reusable document vectors.

**Contrastive objective:** A loss favoring positive pairs over selected negatives.

**False negative:** A relevant pair incorrectly labelled as a negative example.

**Pairwise reranker:** A scorer trained to rank one candidate above another for a query.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-020/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `llm-torch-cpu` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-020.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Compute query_embeddings=query_features@W andscore_matrix=query_embeddings@document_features.T. Cross entropy uses the diagonal document index as the positive label. Clear gradients and updateW under a fixed budget. For the reranker, score each pair with a linear weight and optimize softplus(-(positive_score-negative_score)). Inspect parameter changes, training loss and ranking separately. Freeze document features in this fixture so only the query projection is trained.

## Derive the first query-projection and reranker updates

Queries and documents are both the 2-by-2 identity matrix, while W begins at zero. The score matrix \(QWD^{\mathsf T}\) is therefore W itself. Each row has uniform class probabilities[0.5, 0.5], and the labels are[0, 1]. Mean cross entropy across two rows gives gradient[[-0.25, 0.25], [0.25, -0.25]]. SGD at 0.5 produces W=[[0.125, -0.125], [-0.125, 0.125]] after one update.

The positive-minus-negative score margin is 0.25 in both training rows. Symmetry preserves the form[[a, -a], [-a, a]] during this particular optimization, with positive a after the first step. For a new query[x, y], the two scores are[a(x-y), -a(x-y)], so the decision boundary is \(x=y\). The held-out[0.9, 0.1] lies well on the document 0 side; after the first step its scores are[0.1, -0.1]. That is a local feature-space check, not a test of understanding a new sentence.

The cross-entropy derivative can be written \(\frac{Q^{\mathsf T}(P-Y)D}{B}\) for this fixed-feature linear projection, where P contains row probabilities, Y the one-hot targets and B the number of query rows. Its shape matches W. In a real trainable encoder, gradients would flow through encoder and embedding parameters for fixed tokenized inputs; ordinary discrete token IDs and the tokenizer are not differentiable parts of that graph. Here document features remain fixed and only four projection entries are updated.

The reranker has weight w=[w = 0, w1], positive feature[1, 0] and negative[0, 1]. Its score margin is w0-w1 and its loss is softplus(-(w0-w1)). At zero, the gradient is[-0.5, 0.5]. A0.2 SGD step produces[0.1, -0.1], giving margin 0.2 and a smaller loss. This independent calculation shows what the pairwise objective favors without assuming the training loop's result.

A pairwise loss for one query should compare candidates under that same query's intended relevance. Mixing a positive from one question with a negative from an unrelated question can teach a shortcut unless the dataset design explicitly calls for it. In-batch negatives also assume that another row's positive is not a valid answer for the current query. Multiple correct passages or duplicated source families can violate that assumption.

The false-negative exercise detects that positive and negative IDs are identical. It does not supply a reusable admission function that automatically blocks all future training pairs. Different IDs can still refer to the same content or to two valid answers. Real admission needs identity, content/family and semantic relevance checks, with uncertainty preserved for review rather than forced into a negative label.

The trained models are small but real: parameters change under gradients and rankings are observed. Their input features are literal arrays, so they are not pretrained text encoders. Sentence representation training motivates this distinction between reusable encoders and pair scorers, but the local result does not inherit a natural-language benchmark score. [Sentence-BERT](https://arxiv.org/abs/1908.10084).

### Interview reasoning with explanatory answers

**Why can a hard negative be harmful?** If it is actually relevant, the objective pushes away evidence the system should retrieve. Hardness is a model score property; correctness of the negative label is a task property.

**Why evaluate candidate recall after reranker training?** A better ordering cannot recover evidence absent from the candidate set. Improvements at one stage must be measured under the full retrieval budget.

**What does the perturbed feature result establish?** The learned linear boundary behaves as expected at one nearby point with an authored label. It does not establish transfer to unseen document or language families.

## Worked example / walkthrough

### Example A: Construct paired retrieval features

The identity fixture isolates learning the pairing. A real encoder receives text and requires a tokenizer, pooling policy and governed relevance labels.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

queries = torch.eye(2)
documents = torch.eye(2)
labels = torch.tensor([0, 1])
projection = nn.Parameter(torch.zeros((2, 2)))
scores = (queries @ projection) @ documents.T
assert tuple(scores.shape) == (2, 2) and labels.tolist() == [0, 1]
```

**Expected:** score shape(2, 2); one positive per query.

### Example B: Train the query projection

The projection actually changes through gradients. The resulting training ranking is a mechanics check, not evidence of transfer to unseen language.

```python
opt = torch.optim.SGD([projection], lr=0.5)
initial = F.cross_entropy(scores, labels).item()
for _ in range(30):
    opt.zero_grad(set_to_none=True)
    scores = (queries @ projection) @ documents.T
    loss = F.cross_entropy(scores, labels)
    loss.backward()
    opt.step()
final_scores = (queries @ projection) @ documents.T
assert F.cross_entropy(final_scores, labels).item() < initial and final_scores.argmax(
    1
).tolist() == [0, 1]
```

**Expected:** loss decreases; each query ranks its paired document first.

### Example C: Evaluate a perturbed held-out query

This tests one nearby feature perturbation under an authored relevance label. It is much narrower than evaluating new document families or real paraphrases.

```python
held = torch.tensor([[0.9, 0.1]])
held_scores = (held @ projection) @ documents.T
assert held_scores.argmax(1).item() == 0
```

**Expected:** document 0 remains higher on this declared local perturbation.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: score shape(2, 2); one positive per query. actual gradient updates True; pretrained_semantic_encoder False. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Construct paired retrieval features.** Use queries and documents equal to the 2x2identity matrix, with positive labels 0, 1.
   **Expected:** score shape(2, 2); one positive per query.
   **Verify:** Save the assertion results for exercise 1, including score shape(2, 2); one positive per query.

2. **Train the query projection.** Run 30SGD at 0.5 updates on cross entropy against diagonal positives.
   **Expected:** loss decreases; each query ranks its paired document first.
   **Verify:** Save the assertion results for exercise 2, including loss decreases; each query ranks its paired document first.

3. **Evaluate a perturbed held-out query.** Use held-out feature[.9, .1] and compare its two document scores.
   **Expected:** document 0 remains higher on this declared local perturbation.
   **Verify:** Save the assertion results for exercise 3, including document 0 remains higher on this declared local perturbation.

4. **Train a pairwise reranker.** Use positive feature[1, 0], negative[0, 1] and a zero linear weight; run 20SGD at 0.2 updates.
   **Expected:** positive score exceeds negative and pairwise loss decreases.
   **Verify:** Save the assertion results for exercise 4, including positive score exceeds negative and pairwise loss decreases.

5. **Detect a false-negative identity.** Assign the same document ID to positive and negative roles and identify the collision as a prospective admission failure.
   **Expected:** identity collision detected; this check is separate from the earlier training loops.
   **Verify:** Save the assertion results for exercise 5, including identity collision detected; this check is separate from the earlier training loops.

6. **Bound the model claim.** Record that fixed vectors were used and natural-language encoder quality was not measured.
   **Expected:** actual gradient updates True; pretrained_semantic_encoder False.
   **Verify:** Save the assertion results for exercise 6, including actual gradient updates True; pretrained_semantic_encoder False.

## Common pitfalls and diagnosis

If the first projection update has the wrong sign, derive P-Y for the paired labels and check the mean denominator. If the held-out feature changes class unexpectedly, inspect its side of the analytic \(x=y\) boundary. If a reranker prefers the negative, verify feature and response identity pairing before changing the loss.

If training improves but retrieval quality falls, inspect false negatives, family leakage and whether the served index uses the new encoder space. If a duplicate-ID assertion is described as a complete admission system, identify the absent enforcement function and broader semantic checks. Keep training ranking, held-out relevance and downstream answer support as distinct results.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Bi-encoder, Contrastive objective, False negative using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-019` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Sentence-BERT](https://arxiv.org/abs/1908.10084), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-020, Fine-tuning embeddings and a small reranker.
Read courses/llm-applied/guides/llm-applied-020.md and courses/llm-applied/lessons/llm-applied-020.py. Direct prerequisites: `llm-applied-019`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
