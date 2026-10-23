# torch-025: Contrastive embeddings and negative sampling

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-024`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Embedding objectives teach a representation to preserve selected relationships. The central investigation is concrete: Use anchor[1, 0], positive[1, 1], negative[0, 1]. The finish condition is dots1, 0; cosines1/sqrt2, 0. positive probability increases; argmax remains0. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Embedding objectives teach a representation to preserve selected relationships. A positive pair is declared related under a task definition, while a negative pair is declared unrelated. Those labels are assumptions supplied by the dataset, not facts inferred from a similarity score. Dot products depend on vector magnitude and direction. Cosine similarity divides by both norms and compares direction. A high score can still belong to an irrelevant or duplicated example.

Contrastive cross entropy compares a positive candidate with selected negatives. Its temperature changes score concentration and gradient scale. False negatives can create contradictory supervision, especially when two document versions contain the same answer. This lesson uses literal vectors and an actual differentiable projection so the objective and gradient are inspectable. It does not claim that the tiny representation has learned natural-language semantics.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-025](../../deep-learning-tensorflow/guides/tf-025.md) after deriving the shared numerical contract.

The paired TensorFlow lesson uses the same vector arithmetic and candidate objective. PyTorch exposes the projection gradient through Parameter.grad after backward. Match normalization, temperature and candidate identities before comparing objective values.

## Vocabulary and concepts

**Contrastive objective:** A loss encouraging a positive candidate to out rank chosen negatives.

**Cosine similarity:** A directional comparison normalized by vector lengths.

**False negative:** A related candidate incorrectly label led unrelated.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-025/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-025.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-025.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use torch.dot for one-dimensional vectors and F.cosine_similarity with an explicit feature dimension. Check nonzero finite norms before interpreting cosine. Build a two-candidate logit row and use class index0 for the positive. A trainable projection can receive gradients through these scores. Keep candidate identities beside vectors and reject a positive/negative identity collision before training.

## Worked example / walkthrough

### Example A: Compare dot and cosine scores

The positive vector is not parallel to the anchor, so its cosine is below one. Equal-looking scalar scores from different similarity definitions need not mean the same relationship.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

anchor=torch.tensor([1.,0.],dtype=torch.float64); positive=torch.tensor([1.,1.],dtype=torch.float64); negative=torch.tensor([0.,1.],dtype=torch.float64)
assert torch.dot(anchor,positive).item()==1 and torch.dot(anchor,negative).item()==0
np.testing.assert_allclose(F.cosine_similarity(anchor,positive,dim=0).item(),1/np.sqrt(2),atol=1e-12,rtol=0)
```

**Expected:** dots1, 0; cosines1/sqrt2, 0.

### Example B: Scale without changing direction

Normalization removes positive scale from this comparison. A model trained with unnormalized dot products may intentionally use magnitude, so normalization is a modeling choice.

```python
scaled=10*positive
assert torch.dot(anchor,scaled).item()==10
torch.testing.assert_close(F.cosine_similarity(anchor,scaled,dim=0),F.cosine_similarity(anchor,positive,dim=0),atol=1e-12,rtol=0)
```

**Expected:** dot becomes10; cosine unchanged.

### Example C: Calculate a two-candidate loss

The loss depends on the relative score advantage. It does not verify whether the supplied positive and negative labels are semantically correct.

```python
logits=torch.tensor([[1.,0.]],dtype=torch.float64)
np.testing.assert_allclose(F.cross_entropy(logits,torch.tensor([0])).item(),np.log1p(np.exp(-1)),atol=1e-12,rtol=0)
```

**Expected:** cross entropy log(1+exp(-1)).

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: dots1, 0; cosines1/sqrt2, 0. positive probability increases; argmax remains0. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Compare dot and cosine scores.** Use anchor[1, 0], positive[1, 1], negative[0, 1].
   **Expected:** dots1, 0; cosines1/sqrt2, 0.
   **Verify:** Save the assertion results for exercise 1, including dots1, 0; cosines1/sqrt2, 0.

2. **Scale without changing direction.** Multiply the positive vector by 10 and compare scores.
   **Expected:** dot becomes10; cosine unchanged.
   **Verify:** Save the assertion results for exercise 2, including dot becomes10; cosine unchanged.

3. **Calculate a two-candidate loss.** Use logits[1, 0] with target0.
   **Expected:** cross entropy log(1+exp(-1)).
   **Verify:** Save the assertion results for exercise 3, including cross entropy log(1+exp(-1)).

4. **Inspect a projection gradient.** Create a trainable2 x2 identity projection and back propagate the positive-versus-negative objective.
   **Expected:** finite nonzero projection gradient.
   **Verify:** Save the assertion results for exercise 4, including finite nonzero projection gradient.

5. **Detect contradictory candidate identity.** Assign the same document ID to positive and negative roles.
   **Expected:** identity collision detected.
   **Verify:** Save the assertion results for exercise 5, including identity collision detected.

6. **Separate temperature from ranking.** Compare softmax[1, 0] at temperatures1 and.5.
   **Expected:** positive probability increases; argmax remains0.
   **Verify:** Save the assertion results for exercise 6, including positive probability increases; argmax remains0.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Contrastive objective, Cosine similarity, False negative using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-024` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why can a negative-sampling bug survive a finite-loss check?**

A mathematically valid loss can optimize contradictory labels. Identity and relevance audits are separate from numerical finiteness.

**Does cosine similarity make all embedding models interchangeable?**

No. It standardizes a score calculation within a representation space. Different encoders and preprocessing policies can define incompatible spaces.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-025, Contrastive embeddings and negative sampling.
Read courses/deep-learning-pytorch/guides/torch-025.md and courses/deep-learning-pytorch/lessons/torch-025.py. Direct prerequisites: `torch-024`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
