# torch-014: CrossEntropyLoss, multiclass and multilabel contracts

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-013`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Multiclass classification chooses exactly one outcome among mutually exclusive classes. The central investigation is concrete: Use one row of three zero logits and target class 1. The finish condition is cross entropy log 3. IndexError or RuntimeError identifying an invalid target. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Multiclass classification chooses exactly one outcome among mutually exclusive classes. Multilabel classification makes several independent binary decisions, so multiple labels can be present. A final layer with three outputs can serve either task; the target meaning determines the loss. PyTorch CrossEntropyLoss expects raw class logits and class-index targets by default. It includes log-softmax internally, so applying softmax first changes the intended calculation.

The class axis convention matters. For ordinary batches, logits have shape(N, C) and targets(N). For spatial tasks, the class axis remains dimension 1, unlike many channels-last examples in other frameworks. Multilabel BCEWithLogitsLoss instead expects a target matrix matching the logits. Report which axes are averaged before comparing losses with different output widths.

## Design decisions and when to use this method

Choose the loss from the event being predicted. Use a categorical objective when exactly one ofC outcomes is the target for each unit. Use separate binary objectives when several labels can hold simultaneously. The final layer width alone cannot make that decision, and casting orreshaping labels cannot repair a wrong event definition.

Keep class vocabulary, axis location, target representation and ignored-label policy explicit. For framework comparison, translate the class axis before comparing reductions. Treat probability targets, label smoothing and class weights as separate objective variants whose validity and denominator must be checked, rather than assuming they behave identically to integer class-index targets.

## Paired TensorFlow comparison

Compare [tf-014](../../deep-learning-tensorflow/guides/tf-014.md) after deriving the shared numerical contract.

Keras sparse categorical loss commonly treats the last axis as classes, while PyTorch CrossEntropyLoss uses dimension 1 for batched/spatial logits. Both need raw logits when configured as logits losses. Independent multilabel targets use binary objectives rather than one class-index objective.

## Vocabulary and concepts

**Multiclass target:** One class identity among mutually exclusive alternatives.

**Multilabel target:** A binary presence value for each independently meaningful label.

**Class axis:** The dimension indexing alternative categories in a logit tensor.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-014/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-014.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-014.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use F.cross_entropy with long integer class indices and floating logits. Sparse target indices must satisfy \(0\le \mathrm{target}<C\). For independent labels, use floating 0/1 targets with F.binary_cross_entropy_with_logits. `softmax(dim=1)` creates a class distribution for reporting. A uniform three-class logit vector gives loss log 3, while three independent binary logits at zero each give probability 0.5.

## Derive the class competition and its tensor contract

For a single multiclass record with logits z_0..z_(C-1), softmax assigns \(p_c=\frac{e^{z_c}}{\sum_j e^{z_j}}\). The indexed-target loss is`logsumexp(z)-z_y`. It compares the observed class with all alternatives through one shared normalization. Adding the same constant to every logit leaves the probabilities and loss unchanged, which is why a numerically stable implementation can subtract a row maximum.

At three zero logits and target class 1, p=[\(\frac{1}{3}\), \(\frac{1}{3}\), \(\frac{1}{3}\)] and loss=log 3. The gradient with respect to the three logits is[\(\frac{1}{3}\), \(\frac{-2}{3}\), \(\frac{1}{3}\)] before a batch reduction. The components sum to zero because raising every score equally cannot change class competition. This provides a derivative interpretation beyond the forward scalar.

PyTorch's indexed-target shapes are:

| Task | Logits | Integer target | Class axis |
| --- | --- | --- | --- |
| One record | (C, ) | scalar | The only logit axis |
| Ordinary batch | (N, C) | (N, ) | Dimension 1 |
| Spatial labels | (N, C, H, W) | (N, H, W) | Dimension 1 |
| Independent multilabel batch | (N, C) | Floating(N, C) | Each label is a binary event |

A sparse target index is a category identity, not a numeric value to regress. It must be a valid class index under the declared vocabulary. Probability-target forms instead match the logit shape and require a meaningful distribution across the class axis. The application should validate nonnegativity and normalization rather than assuming a floating tensor automatically supplies valid soft labels. The official API distinguishes these forms and their reductions. [PyTorch 2.9 CrossEntropyLoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.CrossEntropyLoss.html).

Applying softmax before CrossEntropyLoss feeds probabilities into an API that interprets them as logits and normalizes again. Uniform scores are a poor detector of this bug because any equal-valued score vector still produces a uniform distribution and losslog 3. A nonuniform fixture such as[2, 0, -2] exposes the changed confidence and objective. This is another reason to retain asymmetric, nonuniform examples alongside exact symmetric reference points.

Multilabel prediction has a different denominator and probability meaning. For two records and three binary labels, there are six binary events. Zero logits give each marginal probability 0.5, so the three probabilities in a row sum to 1.5 rather than one. That sum can represent an expected count of positive labels; it is not itself a probability of one mutually exclusive outcome. Shared features can still relate the labels, and independent binary losses do not automatically describe their full joint distribution.

Each zero-logit binary entry contributeslog 2. Summing all six gives 6 log2; the element mean giveslog 2; the mean across records of a sum across three labels gives 3 log2. All three are possible reductions, but they imply different objective and gradient scales. State whether the denominator counts records, labels, valid pixels or another participation unit.

Weights and ignored entries require another check. For class-index targets with class weights, PyTorch's weighted mean uses the participating target-class weights in its denominator, and ignore_index excludes designated targets from that participation. Do not transfer that exact formula automatically to soft-target cross entropy orpositive-weighted binary loss. A padded spatial orsequence target can otherwise change training scale while the displayed output tensor shape remains plausible.

For Keras comparisons, the default class-axis convention is often the last axis, whereas the PyTorch spatial categorical interface expects classes at dimension 1. Reorder axes and align target indexing explicitly; merely matching total element count can normalize across the wrong population orcouple unrelated observations.

## Worked example / walkthrough

### Example A: Calculate uniform multiclass loss

Every class has probability one-third. The target index identifies a category, not a numeric magnitude to regress.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

logits=torch.zeros((1,3),dtype=torch.float64); target=torch.tensor([1],dtype=torch.long)
np.testing.assert_allclose(F.cross_entropy(logits,target).item(),np.log(3),atol=1e-12,rtol=0)
```

**Expected:** cross entropy log 3.

### Example B: Contrast independent binary outputs

Independent probabilities need not sum to one. A softmax would force labels to compete and change the task.

```python
independent=torch.sigmoid(logits)
assert independent.tolist()==[[.5,.5,.5]] and independent.sum().item()==1.5
```

**Expected:** probabilities.5, .5, .5 with sum 1.5.

### Example C: Inspect target shapes and types

The target contracts differ because the prediction events differ. Reshaping or casting without understanding those events can make a wrong task appear accepted.

```python
classes=torch.tensor([2,0],dtype=torch.long); labels=torch.tensor([[1.,0.,1.],[0.,1.,0.]])
assert tuple(classes.shape)==(2,) and tuple(labels.shape)==(2,3) and classes.dtype==torch.long and labels.is_floating_point()
```

**Expected:** shapes(2, ) and(2, 3); long versus floating.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: cross entropy log 3. IndexError or RuntimeError identifying an invalid target. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Calculate uniform multiclass loss.** Use one row of three zero logits and target class 1.
   **Expected:** cross entropy log 3.
   **Verify:** Save the assertion results for exercise 1, including cross entropy log 3.

2. **Contrast independent binary outputs.** Apply sigmoid to the same three zero logits for a multilabel task.
   **Expected:** probabilities.5, .5, .5 with sum 1.5.
   **Verify:** Save the assertion results for exercise 2, including probabilities.5, .5, .5 with sum 1.5.

3. **Inspect target shapes and types.** Create class indices 2, 0 and binary rows[1, 0, 1], [0, 1, 0].
   **Expected:** shapes(2, ) and(2, 3); long versus floating.
   **Verify:** Save the assertion results for exercise 3, including shapes(2, ) and(2, 3); long versus floating.

4. **Check class-axis normalization.** Apply `softmax(dim=1)` to a 2-by-3 matrix.
   **Expected:** each row sums 1.
   **Verify:** Save the assertion results for exercise 4, including each row sums 1.

5. **Name the multilabel denominator.** Compute BCE over two rows and three labels of zero logits.
   **Expected:** sum 6 log2; mean log 2.
   **Verify:** Save the assertion results for exercise 5, including sum 6 log2; mean log 2.

6. **Reject an out-of-vocabulary class.** Use class index 3 for a three-class row.
   **Expected:** IndexError or RuntimeError identifying an invalid target.
   **Verify:** Save the assertion results for exercise 6, including IndexError or RuntimeError identifying an invalid target.

## Common pitfalls and diagnosis

If probabilities sum along the batch axis instead of the class axis, inspect the softmax dimension and give each axis a semantic name. If a class-index target was converted to a floating matrix just to avoid an error, verify whether the task actually changed to a soft-target ormultilabel objective. A class index 3 isinvalid for three classes 0..2, regardless of how confidently a model predicts.

If a double-softmax mistake passes the uniform-logit case, test a nonuniform row and compare the target probability and gradient. If padding orclass weighting changes the scalar unexpectedly, reconstruct the library's exact participation denominator for that target form. Never compare a per-label mean with a per-record summed objective as though their matching function names implied the same training problem.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Multiclass target, Multilabel target, Class axis using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-013` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why should softmax usually stay out of the training forward for CrossEntropyLoss?**

CrossEntropyLoss already combines log-softmax with negative log likelihood. Supplying probabilities as logits applies the wrong transformation and can weaken numerical stability.

**Can one-hot labels always replace class indices?**

PyTorch supports probability targets in particular forms, but that is a different explicit contract. Keep class-index and soft-target cases distinct and verify shape, reduction and label meaning.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-014, CrossEntropyLoss, multiclass and multilabel contracts.
Read courses/deep-learning-pytorch/guides/torch-014.md and courses/deep-learning-pytorch/lessons/torch-014.py. Direct prerequisites: `torch-013`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
