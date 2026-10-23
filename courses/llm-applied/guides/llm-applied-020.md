# llm-applied-020: Fine-tuning embeddings and a small reranker

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-019`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Embedding and reranker fine-tuning adapts retrieval behavior rather than only answer generation. The central investigation is concrete: Use queries anddocuments equal to the2x2identity matrix, withpositive labels0, 1. The finish condition is score shape(2, 2); one positive perquery. actual gradient updatesTrue; pretrained_semantic_encoderFalse. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Embedding and reranker fine-tuning adapts retrieval behavior rather than only answer generation. A bi-encoder maps queries and documents separately so document vectors can be indexed once. A cross-encoder or reranker jointly evaluates a query-document pair and is usually applied to a smaller candidate set. Contrastive training requires positives and negatives whose labels reflect the task. A false negative, such as another relevant passage labelled irrelevant, can teach contradictory geometry.

This chapter performs actual CPU updates on a small linear query projection and a separate pairwise reranker. Literal feature vectors stand in for encoded text so the gradient and ranking changes are inspectable. The bi-encoder objective makes each query favor its paired document over the other candidate. The reranker learns a scalar preference from two authored pair features. These are real trainable models, but they are not pretrained sentence encoders and do not establish semantic retrieval quality on natural language. Held-out domain evaluation remains necessary after any realistic fine-tuning.

## Design decisions and when to use this method

Fine-tune retrieval models when error analysis shows that the representation or pair scorer systematically misses domain relevance despite sound chunking and metadata. Choose negatives carefully: random negatives may be too easy, while hard negatives may contain relevant alternatives. Label quality and domain coverage often matter more than increasing the number of updates.

Do not train a retriever on the final relevance benchmark and then present its score as independent evidence. Split query/document families before mining negatives. Compare lexical, unadapted embedding, adapted embedding and reranked variants under matched candidate budgets. Track recall, ranking quality, unsupported-answer rate and resource cost. A better retriever can still feed a generator that ignores evidence, so answer evaluation remains a separate stage.

## Vocabulary and concepts

**Bi-encoder:** Separate query and document encoders enabling reusable document vectors.

**Contrastive objective:** A loss favoring positive pairs over selected negatives.

**False negative:** A relevant pair incorrectly labelled as a negative example.

**Pairwise reranker:** A scorer trained to rank one candidate above another for a query.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-020/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-020.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-020.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Compute query_embeddings=query_features@W andscore_matrix=query_embeddings@document_features.T. Cross entropy uses the diagonal document index as the positive label. Clear gradients and updateW under a fixed budget. For the reranker, score each pair with a linear weight and optimize softplus(-(positive_score-negative_score)). Inspect parameter changes, training loss and ranking separately. Freeze document features in this fixture so only the query projection is trained.

## Worked example / walkthrough

### Example A: Construct paired retrieval features

The identity fixture isolates learning the pairing. A real encoder receives text and requires a tokenizer, pooling policy and governed relevance labels.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

queries=torch.eye(2); documents=torch.eye(2); labels=torch.tensor([0,1]); projection=nn.Parameter(torch.zeros((2,2)))
scores=(queries@projection)@documents.T
assert tuple(scores.shape)==(2,2) and labels.tolist()==[0,1]
```

**Expected:** score shape(2, 2); one positive perquery.

### Example B: Train the query projection

The projection actually changes through gradients. The resulting training ranking is a mechanics check, not evidence of transfer to unseen language.

```python
opt=torch.optim.SGD([projection],lr=.5); initial=F.cross_entropy(scores,labels).item()
for _ in range(30):
    opt.zero_grad(set_to_none=True); scores=(queries@projection)@documents.T; loss=F.cross_entropy(scores,labels); loss.backward(); opt.step()
final_scores=(queries@projection)@documents.T
assert F.cross_entropy(final_scores,labels).item()<initial and final_scores.argmax(1).tolist()==[0,1]
```

**Expected:** loss decreases; each query ranks its paired document first.

### Example C: Evaluate a perturbed held-out query

This tests one nearby feature perturbation under an authored relevance label. It is much narrower than evaluating new document families or real paraphrases.

```python
held=torch.tensor([[.9,.1]]); held_scores=(held@projection)@documents.T
assert held_scores.argmax(1).item()==0
```

**Expected:** document0 remains higher on this declared local perturbation.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: score shape(2, 2); one positive perquery. actual gradient updatesTrue; pretrained_semantic_encoderFalse. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Construct paired retrieval features.** Use queries anddocuments equal to the2x2identity matrix, withpositive labels0, 1.
   **Expected:** score shape(2, 2); one positive perquery.
   **Verify:** Save the assertion results for exercise 1, including score shape(2, 2); one positive perquery.

2. **Train the query projection.** Run30SGD.5 updates on cross entropy against diagonal positives.
   **Expected:** loss decreases; each query ranks its paired document first.
   **Verify:** Save the assertion results for exercise 2, including loss decreases; each query ranks its paired document first.

3. **Evaluate a perturbed held-out query.** Use held-out feature[.9, .1] and compare its two document scores.
   **Expected:** document0 remains higher on this declared local perturbation.
   **Verify:** Save the assertion results for exercise 3, including document0 remains higher on this declared local perturbation.

4. **Train a pairwise reranker.** Use positive feature[1, 0], negative[0, 1] and a zero linear weight; run20SGD.2 updates.
   **Expected:** positive score exceeds negative and pairwise loss decreases.
   **Verify:** Save the assertion results for exercise 4, including positive score exceeds negative and pairwise loss decreases.

5. **Detect a false-negative identity.** Assign the same document ID to bothpositive andnegative roles and refuse the pair.
   **Expected:** identity collision detected beforetraining.
   **Verify:** Save the assertion results for exercise 5, including identity collision detected beforetraining.

6. **Bound the model claim.** Record that fixed vectors were used and natural-language encoder quality was not measured.
   **Expected:** actual gradient updatesTrue; pretrained_semantic_encoderFalse.
   **Verify:** Save the assertion results for exercise 6, including actual gradient updatesTrue; pretrained_semantic_encoderFalse.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Bi-encoder, Contrastive objective, False negative using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-019` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Sentence-BERT](https://arxiv.org/abs/1908.10084), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-020, Fine-tuning embeddings and a small reranker.
Read courses/llm-applied/guides/llm-applied-020.md and courses/llm-applied/lessons/llm-applied-020.py. Direct prerequisites: `llm-applied-019`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
