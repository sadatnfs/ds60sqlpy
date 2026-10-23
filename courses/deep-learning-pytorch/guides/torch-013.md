# torch-013: Binary logits, BCEWithLogitsLoss and thresholds

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-012`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A binary logit is an unrestricted score. The central investigation is concrete: Apply sigmoid to-2, 0, 2. The finish condition is middle probability.5 and strictly increasing values. 0 errors at.5 and1 at.8. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A binary logit is an unrestricted score. Its sigmoid maps that score to a number between zero and one under the model's probability convention. BCEWithLogitsLoss combines the sigmoid and binary cross-entropy algebra in a numerically stable form, so its input should be logits rather than already-sigmoid e d probabilities. Applying sigmoid twice changes the objective while often producing finite values that look plausible.

A classification threshold is a separate decision policy. Changing it alters predicted labels without changing fitted logits. The threshold can reflect costs or coverage, but must be chosen on validation evidence rather than after viewing final-test results. The tiny scores-2, 0, 2 make the midpoint and boundary policy inspectable. Their probabilities are not automatically calibrated merely because sigmoid produced them.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-013](../../deep-learning-tensorflow/guides/tf-013.md) after deriving the shared numerical contract.

TensorFlow's sigmoid-cross-entropy-with-logits operation and PyTorch BCEWithLogitsLoss share the logit convention. Keras Binary Cross entropy requires its from_logits setting to agree with the model output. Match dtype, shape and element reduction before comparing scalar values.

## Vocabulary and concepts

**Logit:** A binary score before the sigmoid probability transformation.

**BCEWithLogitsLoss:** A stable combined binary logistic objective.

**Decision threshold:** A policy boundary converting probabilities into labels.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-013/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-013.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-013.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

F.binary_cross_entropy_with_logits expects floating targets and logits of matching shape. torch.sigmoid is useful for reporting probabilities after the objective convention is fixed. Use probability>=threshold to declare a tie policy. Compare loss at zero logit with log2 and use extreme logits to check stable arithmetic. Do not infer label correctness from confidence alone.

## Worked example / walkthrough

### Example A: Convert fixed logits

The monotonic transformation preserves ranking. A score of zero is the exact midpoint, which makes threshold ties explicit.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

logits=torch.tensor([-2.,0.,2.],dtype=torch.float64); probabilities=torch.sigmoid(logits)
assert probabilities[1].item()==.5 and bool(torch.all(torch.diff(probabilities)>0))
```

**Expected:** middle probability.5 and strictly increasing values.

### Example B: Check the midpoint objective

A fifty-fifty prediction assigns probability one-half to the observed label. Its negative logarithm is an independent reference.

```python
loss=F.binary_cross_entropy_with_logits(torch.tensor([0.],dtype=torch.float64),torch.tensor([1.],dtype=torch.float64))
np.testing.assert_allclose(loss.item(),np.log(2),atol=1e-12,rtol=0)
```

**Expected:** loss log2 within1e-12.

### Example C: Move the decision threshold

The middle decision changes while the model scores remain fixed. This is a policy change, not an optimizer update.

```python
assert (probabilities>=.5).tolist()==[False,True,True]
assert (probabilities>=.8).tolist()==[False,False,True]
```

**Expected:** labels False, True, True versus False, False, True.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: middle probability.5 and strictly increasing values. 0 errors at.5 and1 at.8. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Convert fixed logits.** Apply sigmoid to-2, 0, 2.
   **Expected:** middle probability.5 and strictly increasing values.
   **Verify:** Save the assertion results for exercise 1, including middle probability.5 and strictly increasing values.

2. **Check the midpoint objective.** Compute positive-label BCE at zero logit.
   **Expected:** loss log2 within1e-12.
   **Verify:** Save the assertion results for exercise 2, including loss log2 within1e-12.

3. **Move the decision threshold.** Compare thresholds.5 and.8 with>=ties.
   **Expected:** labels False, True, True versus False, False, True.
   **Verify:** Save the assertion results for exercise 3, including labels False, True, True versus False, False, True.

4. **Expose a double-sigmoid mistake.** Feed probability.5 as though it were a logit and compare with log2.
   **Expected:** incorrect loss differs by more than.1.
   **Verify:** Save the assertion results for exercise 4, including incorrect loss differs by more than.1.

5. **Test extreme finite scores.** Use logits1000, -1000 with labels1, 0.
   **Expected:** finite losses approximately0.
   **Verify:** Save the assertion results for exercise 5, including finite losses approximately0.

6. **Count threshold errors.** Use truth0, 1, 1 and compare the two decision policies.
   **Expected:** 0 errors at.5 and1 at.8.
   **Verify:** Save the assertion results for exercise 6, including 0 errors at.5 and1 at.8.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Logit, BCEWithLogitsLoss, Decision threshold using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-012` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why prefer BCEWithLogitsLoss over manually applying sigmoid and log?**

The combined implementation can rearrange the algebra to avoid overflow and loss of precision at extreme scores. Manual probability conversion can round to zero or one first.

**Does a probability.9 mean90percent of such predictions are correct?**

Only if calibration evidence supports that interpretation for the relevant population. Sigmoid alone defines a model output, not an empirical reliability guarantee.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-013, Binary logits, BCEWithLogitsLoss and thresholds.
Read courses/deep-learning-pytorch/guides/torch-013.md and courses/deep-learning-pytorch/lessons/torch-013.py. Direct prerequisites: `torch-012`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
