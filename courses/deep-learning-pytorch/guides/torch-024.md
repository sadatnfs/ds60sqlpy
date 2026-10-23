# torch-024: Capstone: a small classifier with honest evaluation

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 210 minutes. Direct prerequisites: `torch-023`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A classifier capstone must connect the task definition to training and evaluation evidence. The central investigation is concrete: Use training x-2, -1, 1, 2 with labels0, 0, 1, 1 and test x-3, 3. The finish condition is 4 training records, 2 test records. negative0/1 errors; positive1/1. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A classifier capstone must connect the task definition to training and evaluation evidence. The literal fixture classifies the sign of a scalar coordinate. Training and test IDs are fixed before fitting. Normalization statistics use only training rows, and the decision threshold is declared before test scoring. Aone-weight logistic model is sufficient for the fixture; unnecessary depth would obscure the experiment rather than improve its meaning.

Report confusion counts and their denominator, not only accuracy. A mean baseline or constant-class baseline provides a comparison under the same held-out units. Per-group failures can be hidden by an aggregate. The tiny test contains only two rows, so the capstone proves an inspectable local pipeline without establishing population reliability. PyTorch standard-deviation defaults differ from NumPy's population default, so the preprocessing comparison must set correction explicitly.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-024](../../deep-learning-tensorflow/guides/tf-024.md) after deriving the shared numerical contract.

The paired TensorFlow classifier uses the same geometry. Match normalization variance conventions:NumPy default std uses N, while PyTorch std defaults to a correction that must be over r id den here. Both need logit loss, threshold policy, train-only fit and complete confusion counts.

## Vocabulary and concepts

**Confusion matrix:** Counts of true/false positive and negative decisions.

**Frozen threshold:** A decision policy chosen before final assessment.

**Population standard deviation:** A variance calculation dividing by N rather than N-1.

**Subgroup evidence:** Errors and counts reported for a declared subset.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-024/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-024.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-024.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

UseX shaped(4, 1), floating binary targets and nn.Linear(1, 1, bias=False). Calculate x.std(dim=0, correction=0)to match the declared population normalization fixture. Train with BCEWithLogitsLoss for40 fixed SGD updates. Evaluate with model.eval and no_grad, then classify logits>=0. Count TP, TN, FP, FN with boolean masks and verify their sum.

## Worked example / walkthrough

### Example A: Freeze the geometric task

The labels are defined from the fixture geometry before training. The holdout is not used to design a different target after seeing predictions.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

x=torch.tensor([[-2.],[-1.],[1.],[2.]]); y=torch.tensor([[0.],[0.],[1.],[1.]])
test_x=torch.tensor([[-3.],[3.]]); truth=torch.tensor([False,True]); train_ids={'a','b','c','d'}; test_ids={'e','f'}
assert not train_ids&test_ids and len(test_ids)==2
```

**Expected:** 4 training records, 2 test records.

### Example B: Fit explicit normalization

PyTorch's default sample correction would produce a different scale. Specifying correction0 aligns this fixture with the paired TensorFlow/NumPy calculation.

```python
mean=x.mean(0); scale=x.std(0,correction=0); tx=(x-mean)/scale; vx=(test_x-mean)/scale
assert mean.item()==0; np.testing.assert_allclose(scale.item(),np.sqrt(2.5),atol=1e-6,rtol=0)
```

**Expected:** mean0; scale sqrt2.5.

### Example C: Train a fixed classifier

The fixed budget is part of the experiment. It is not repeated until the test happens to look favorable.

```python
model=nn.Linear(1,1,bias=False)
with torch.no_grad(): model.weight.zero_()
optimizer=torch.optim.SGD(model.parameters(),lr=.1)
for _ in range(40):
    optimizer.zero_grad(set_to_none=True); loss=F.binary_cross_entropy_with_logits(model(tx),y); loss.backward(); optimizer.step()
assert model.weight.item()>0 and torch.isfinite(model.weight).all()
```

**Expected:** positive finite weight after40 updates.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: 4 training records, 2 test records. negative0/1 errors; positive1/1. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Freeze the geometric task.** Use training x-2, -1, 1, 2 with labels0, 0, 1, 1 and test x-3, 3.
   **Expected:** 4 training records, 2 test records.
   **Verify:** Save the assertion results for exercise 1, including 4 training records, 2 test records.

2. **Fit explicit normalization.** Calculate training mean and population standard deviation.
   **Expected:** mean0; scale sqrt2.5.
   **Verify:** Save the assertion results for exercise 2, including mean0; scale sqrt2.5.

3. **Train a fixed classifier.** Zero-initialize the weight and run40 SGD.1 steps with binary logits loss.
   **Expected:** positive finite weight after40 updates.
   **Verify:** Save the assertion results for exercise 3, including positive finite weight after40 updates.

4. **Account for every test prediction.** Threshold test logits at0 and calculate confusion counts.
   **Expected:** TP1, TN1, FP0, FN0, total2.
   **Verify:** Save the assertion results for exercise 4, including TP1, TN1, FP0, FN0, total2.

5. **Compare a constant baseline.** Predict class0 for both test rows and count mistakes.
   **Expected:** baseline1 error; model0 on this fixture.
   **Verify:** Save the assertion results for exercise 5, including baseline1 error; model0 on this fixture.

6. **Reveal a group-specific failure.** Flip only the positive group decision and report group counts.
   **Expected:** negative0/1 errors; positive1/1.
   **Verify:** Save the assertion results for exercise 6, including negative0/1 errors; positive1/1.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Confusion matrix, Frozen threshold, Population standard deviation using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-023` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why can identical models disagree after preprocessing?**

Different variance corrections, dtypes or fit partitions change the input values. Framework comparisons must include preprocessing state.

**Does100percent on two test rows establish reliability?**

No. It establishes those observations under this fixture. Representative independent data and uncertainty are separate evidence.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-024, Capstone: a small classifier with honest evaluation.
Read courses/deep-learning-pytorch/guides/torch-024.md and courses/deep-learning-pytorch/lessons/torch-024.py. Direct prerequisites: `torch-023`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
