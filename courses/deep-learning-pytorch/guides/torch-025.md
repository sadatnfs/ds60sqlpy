# torch-025: Contrastive embeddings and negative sampling

## Level and prerequisites

Advanced; approximately 120 minutes. Direct prerequisites: `torch-024`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Embedding objectives teach a representation to preserve selected relationships. The central investigation is concrete: Use anchor[1, 0], positive[1, 1], negative[0, 1]. The finish condition is dots 1, 0; cosines 1/sqrt 2, 0. positive probability increases; argmax remains 0. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Embedding objectives teach a representation to preserve selected relationships. A positive pair is declared related under a task definition, while a negative pair is declared unrelated. Those labels are assumptions supplied by the dataset, not facts inferred from a similarity score. Dot products depend on vector magnitude and direction. Cosine similarity divides by both norms and compares direction. A high score can still belong to an irrelevant or duplicated example.

Contrastive cross entropy compares a positive candidate with selected negatives. Its temperature changes score concentration and gradient scale. False negatives can create contradictory supervision, especially when two document versions contain the same answer. This lesson uses literal vectors and an actual differentiable projection so the objective and gradient are inspectable. It does not claim that the tiny representation has learned natural-language semantics.

## Design decisions and when to use this method

Choose a representation objective from the relationship the application needs to preserve. Define positives, negatives and source-family exclusions before optimizing similarity. Decide whether vector magnitude carries useful signal or whether a directional comparison is intended; normalization changes the model contract rather than merely cleaning up a score.

Use the fixed two-candidate example to inspect relative scores and one query-projection derivative. Broader retrieval evaluation needs representative queries, relevance judgments, candidate identities and a fixed index/model version. A finite contrastive loss or nonzero gradient cannot establish that the labels are sensible or the representation captures natural-language meaning.

## Paired TensorFlow comparison

Compare [tf-025](../../deep-learning-tensorflow/guides/tf-025.md) after deriving the shared numerical contract.

The paired TensorFlow lesson uses the same vector arithmetic and candidate objective. PyTorch exposes the projection gradient through Parameter.grad after backward. Match normalization, temperature and candidate identities before comparing objective values.

## Vocabulary and concepts

**Contrastive objective:** A loss encouraging a positive candidate to outrank chosen negatives.

**Cosine similarity:** A directional comparison normalized by vector lengths.

**False negative:** A related candidate incorrectly labeled unrelated.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-025/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-025.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-025.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use torch.dot for one-dimensional vectors and F.cosine_similarity with an explicit feature dimension. Check nonzero finite norms before interpreting cosine. Build a two-candidate logit row and use class index 0 for the positive. A trainable projection can receive gradients through these scores. Keep candidate identities beside vectors and reject a positive/negative identity collision before training.

## Derive the contrastive competition and its gradient

For nonzero vectors a and b, the dot product is \(\sum_i a_i b_i\) and cosine is their dot divided by \(\lVert a\rVert_2\lVert b\rVert_2\). With a=[1, 0], positive=[1, 1] and negative=[0, 1], the scores are 1 and 0, while cosines are \(\frac{1}{\sqrt{2}}\) and 0. Scaling the positive by ten increases its dot to ten without changing direction. That particular example keeps the ranking, but in general a large poorly aligned vector can outrank a small well-aligned vector under dot product and lose under cosine.

A zero vector has no direction. PyTorch's normalization/similarity APIs use an epsilon convention for numerical stability; receiving a finite number from that convention does not make a zero vector semantically informative. If the application requires directional similarity, validate finite nonzero norms and define a refusal or fallback policy. The paired TensorFlow chapter's explicit zero-norm rejection is a data contract, not a claim that every framework cosine API raises automatically. [PyTorch 2.9 normalize](https://docs.pytorch.org/docs/2.9/generated/torch.nn.functional.normalize.html).

Let candidates have scores s_j and let candidate 0 be the positive. For temperature \(\tau>0\), define \(p_j=\frac{\exp(s_j/\tau)}{\sum_k\exp(s_k/\tau)}\). The loss is \(-\log p_0=\operatorname{logsumexp}(s/\tau)-\frac{s_0}{\tau}\). Stable cross entropy computes this without manually exponentiating large logits. With scores[1, 0] and tau 1, p_0≈0.731059 and loss≈0.313262, which equals \(\log(1+\exp(-1))\). With tau 0.5, the effective logits are[2, 0], p_0≈0.880797 and loss≈0.126928.

Positive temperature scaling preserves the ranking of fixed scores. It changes probabilities and the derivative \(\frac{\partial L}{\partial s_{j}}=\frac{p_{j}-y_{j}}{\tau}\). Lower temperature does not guarantee a larger gradient on every example, because the probabilities also change. For this already-correct pair, the positive-score derivative is approximately-0.268941 at tau 1 and-0.238406 at tau 0.5. Hard or incorrectly ranked examples can behave differently. Treat temperature as an objective and calibration choice, not a universal gradient amplifier.

The reference trains neither candidate vector in its projection check. It defines q=aP with an identity 2×2 trainable P, then uses the fixed positive and negative vectors as candidates. At tau 1, let \(c=\frac{1}{1+\exp(1)}\)≈0.268941. The query derivative is -c[1, 1]+c[0, 1]=[-c, 0]. Since a=[1, 0], the projection derivative is the outer product \(a^{\mathsf T}[-c,0]\), or[[-c, 0], [0, 0]]. Only the first projection row receives this contribution. This exact analytic matrix is stronger explanatory evidence than the reference's broad finite/nonzero assertion.

A shared encoder applied to the anchor and both candidates would have additional gradient paths. A symmetric contrastive objective would also evaluate reverse-direction comparisons. Those are different experiments from this one-branch projection check. The unchanged reference calls backward but does not take a projection optimizer step, so its evidence is differentiability and a local gradient, not a completed representation-learning run.

Negative sampling defines the competition. With M equal candidate scores, the loss is \(\log(M)\), so changing the number of negatives changes the numerical baseline even when the representation is unchanged. Losses from two candidate-pool designs are not automatically comparable. In-batch negatives also couple examples: changing batch membership can change an anchor's objective even if its positive pair stays fixed. This is one reason microbatch gradient accumulation need not reproduce a larger in-batch contrastive batch.

If a positive and negative are literally the same vector under the same scoring path, their scores must agree. For a two-candidate loss, the positive probability is one-half and the opposing query-gradient terms cancel. The model cannot satisfy contradictory role labels through that shared representation. If the vectors are different views of the same relevant document, the model may instead learn a nuisance distinction. Identity checks catch exact collisions; family/version and relevance audits are needed for less obvious false negatives.

Several relevant candidates may require a multi-positive objective or a relevance-aware sampling policy rather than marking all but one as negative. Evaluation should keep the intended corpus, candidate count and exclusions visible. A high score is not an external truth label, and embeddings from different model/tokenizer/normalization versions should not be mixed merely because their dimensions match. Record the representation-space identity with any saved retrieval index.

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

**Expected:** dots 1, 0; cosines 1/sqrt 2, 0.

### Example B: Scale without changing direction

Normalization removes positive scale from this comparison. A model trained with unnormalized dot products may intentionally use magnitude, so normalization is a modeling choice.

```python
scaled=10*positive
assert torch.dot(anchor,scaled).item()==10
torch.testing.assert_close(F.cosine_similarity(anchor,scaled,dim=0),F.cosine_similarity(anchor,positive,dim=0),atol=1e-12,rtol=0)
```

**Expected:** dot becomes 10; cosine unchanged.

### Example C: Calculate a two-candidate loss

The loss depends on the relative score advantage. It does not verify whether the supplied positive and negative labels are semantically correct.

```python
logits=torch.tensor([[1.,0.]],dtype=torch.float64)
np.testing.assert_allclose(F.cross_entropy(logits,torch.tensor([0])).item(),np.log1p(np.exp(-1)),atol=1e-12,rtol=0)
```

**Expected:** cross entropy \(\log(1+\exp(-1))\).

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: dots 1, 0; cosines 1/sqrt 2, 0. positive probability increases; argmax remains 0. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Compare dot and cosine scores.** Use anchor[1, 0], positive[1, 1], negative[0, 1].
   **Expected:** dots 1, 0; cosines 1/sqrt 2, 0.
   **Verify:** Save the assertion results for exercise 1, including dots 1, 0; cosines 1/sqrt 2, 0.

2. **Scale without changing direction.** Multiply the positive vector by 10 and compare scores.
   **Expected:** dot becomes 10; cosine unchanged.
   **Verify:** Save the assertion results for exercise 2, including dot becomes 10; cosine unchanged.

3. **Calculate a two-candidate loss.** Use logits[1, 0] with target 0.
   **Expected:** cross entropy \(\log(1+\exp(-1))\).
   **Verify:** Save the assertion results for exercise 3, including cross entropy \(\log(1+\exp(-1))\).

4. **Inspect a projection gradient.** Create a trainable 2 x2identity projection and back propagate the positive-versus-negative objective.
   **Expected:** finite nonzero projection gradient.
   **Verify:** Save the assertion results for exercise 4, including finite nonzero projection gradient.

5. **Detect contradictory candidate identity.** Assign the same document ID to positive and negative roles.
   **Expected:** identity collision detected.
   **Verify:** Save the assertion results for exercise 5, including identity collision detected.

6. **Separate temperature from ranking.** Compare softmax[1, 0] at temperatures 1 and.5.
   **Expected:** positive probability increases; argmax remains 0.
   **Verify:** Save the assertion results for exercise 6, including positive probability increases; argmax remains 0.

## Common pitfalls and diagnosis

If dot scores grow while directional quality does not, inspect norms and the intended normalization policy. If cosine returns a finite value for a zero vector, apply the application's semantic boundary instead of interpreting epsilon behavior as a meaningful direction. If the projection gradient differs, derive the two score derivatives and check which branches are trainable.

If loss changes after increasing batch size or candidate count, reconstruct the denominator and negative set before attributing improvement to the encoder. If positives are pulled apart, check exact IDs, source families and alternate relevant answers among negatives. If temperature changes ranking for fixed finite scores and positive tau, inspect a separate sorting or preprocessing change. A finite loss with contradictory supervision remains an invalid experiment.

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



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-025, Contrastive embeddings and negative sampling.
Read courses/deep-learning-pytorch/guides/torch-025.md and courses/deep-learning-pytorch/lessons/torch-025.py. Direct prerequisites: `torch-024`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
