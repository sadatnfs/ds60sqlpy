# torch-024: Capstone: a small classifier with honest evaluation

## Level and prerequisites

Intermediate; approximately 210 minutes. Direct prerequisites: `torch-023`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A classifier capstone must connect the task definition to training and evaluation evidence. The central investigation is concrete: Use training x-2, -1, 1, 2 with labels 0, 0, 1, 1 and test x-3, 3. The finish condition is 4training records, 2test records. negative 0/1errors; positive \(\frac{1}{1}\). A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A classifier capstone must connect the task definition to training and evaluation evidence. The literal fixture classifies the sign of a scalar coordinate. Training and test IDs are fixed before fitting. Normalization statistics use only training rows, and the decision threshold is declared before test scoring. Aone-weight logistic model is sufficient for the fixture; unnecessary depth would obscure the experiment rather than improve its meaning.

Report confusion counts and their denominator, not only accuracy. A mean baseline or constant-class baseline provides a comparison under the same held-out units. Per-group failures can be hidden by an aggregate. The tiny test contains only two rows, so the capstone proves an inspectable local pipeline without establishing population reliability. PyTorch standard-deviation defaults differ from NumPy's population default, so the preprocessing comparison must set correction explicitly.

## Design decisions and when to use this method

Use the one-weight logistic model because the declared target is the sign of one scalar coordinate. Additional hidden layers would add parameters without resolving uncertainty in this visible task. Freeze preprocessing, step budget and decision threshold before examining the two test decisions. If those choices are tuned from later results, record that population as selection data rather than claiming it stayed an untouched test.

Treat the capstone as an inspectable training-and-evaluation procedure. The labels and geometric rule are public, and the test points extend beyond the training coordinate range. A successful fixture proves the declared local behavior; it does not establish a blind scientific discovery, calibration or reliability for a real application.

## Paired TensorFlow comparison

Compare [tf-024](../../deep-learning-tensorflow/guides/tf-024.md) after deriving the shared numerical contract.

The paired TensorFlow classifier uses the same geometry. Match normalization variance conventions: NumPy default std uses N, while PyTorch std defaults to a correction that must be overridden here. Both need logit loss, threshold policy, train-only fit and complete confusion counts.

## Vocabulary and concepts

**Confusion matrix:** Counts of true/false positive and negative decisions.

**Frozen threshold:** A decision policy chosen before final assessment.

**Population standard deviation:** A variance calculation dividing by N rather than N-1.

**Subgroup evidence:** Errors and counts reported for a declared subset.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-024`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-024.py` under `.learning/expansion/torch-024/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use X shaped (4, 1), floating binary targets and nn.Linear(1, 1, bias=False). Calculate `x.std(dim=0, correction=0)` to match the declared population normalization fixture. Train with BCEWithLogitsLoss for 40 fixed SGD updates. Evaluate with model.eval and no_grad, then classify \(\mathrm{logits}\ge 0\). Count TP, TN, FP, FN with boolean masks and verify their sum.

## Derive the classifier and audit every assessment row

The training values `[-2, -1, 1, 2]` have mean zero and squared deviations summing to ten. Population variance divides by four, giving 2.5 and scale \(\sqrt{2.5}\). PyTorch's `correction=0` matches NumPy's default used in the paired TensorFlow guide. Using the default sample correction would divide by three and produce \(\sqrt{\frac{10}{3}}\). Both scales are mathematically meaningful statistics, but they define different model inputs and update trajectories. Equal final class labels would not prove framework parity.

The stored model weight has shape(1, 1), inputs and targets have shape(4, 1), and logits have shape(4, 1). The bias is deliberately absent. Binary cross-entropy with logits is applied directly to those logits. Applying sigmoid first and then passing its output to the logits loss would change the objective. A target shaped(4, ) is also a different interface from(4, 1), even when it contains the same four numbers; preserve the declared axes rather than relying on broadcasting or reshaping after a failure.

For one normalized feature t and label y, the logit is \(z=\mathrm{wt}\) and the loss derivative with respect to w is \((\operatorname{sigmoid}(z)-y)t\). At \(w=0\), all probabilities are one-half. Writing \(s=\sqrt{2.5}\), the four derivative contributions are \(\frac{-1}{s}\), -1/(2s), -1/(2s), \(\frac{-1}{s}\). Their mean is -3/(4s), approximately-0.474342. The first SGD step at 0.1 therefore makes w approximately 0.0474342. This analytic sign and scale explain why the later fixed 40-step run should have a positive finite weight.

The data are separable under this one-feature rule. In an unregularized logistic model, continued loss reduction can push the weight larger without a finite optimum that must be reached. Forty steps are a declared computational budget, not evidence of convergence or a reason to repeat training until a preferred test score appears. If early stopping or hyperparameters are to be selected, they need a separate selection procedure and data boundary.

The decision rule is \(\mathrm{logit}\ge 0\), which corresponds to probability>=0.5. At the zero initial weight, both test logits are exactly zero and this tie convention predicts the positive class for both rows. After a positive weight, the transformed-3 point has a negative logit and the+3 point a positive one. The final confusion table is:

| Test input | Truth | Decision | Count category |
| --- | --- | --- | --- |
| -3 | negative | negative | \(\mathrm{TN}=1\) |
| +3 | positive | positive | \(\mathrm{TP}=1\) |

FP and FN are zero, and the four counts sum to two. The fixed class-zero baseline instead has \(\mathrm{TN}=1\), \(\mathrm{FN}=1\). Its one error and the model's zero errors are evaluated on the same two units. This is a useful paired comparison, but one changed decision would move accuracy by 50 percentage points, so the apparent difference is not a stable population estimate.

The subgroup counterexample changes only the positive row's decision. The negative group then has 0 errors out of 1 and the positive group 1 out of 1. Reporting only an aggregate error rate of \(\frac{1}{2}\) hides which group failed. At the same time, one observation per group is not sufficient for a reliable subgroup performance claim. These sign-based teaching groups are not a demonstrated fairness analysis of a real population.

Distinct train/test IDs are necessary but not sufficient for independence. Real data can contain copied examples, shared source families, temporal leakage or features only available after the decision. The literal fixture has none of those hidden sources by construction, but its rule is already visible to the learner. Preserve this difference between a procedure test and an undisclosed final assessment.

Finally, normalization parameters belong to the fitted artifact. The test coordinates must reuse the training mean and scale. Recomputing statistics on each inference batch changes predictions according to which other rows arrived together. A release should save feature order, units, mean, scale, dtype and threshold with the model state, and compare a known input through the complete preprocessing-and-model path. Model weights alone are not the whole predictor.

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

**Expected:** 4training records, 2test records.

### Example B: Fit explicit normalization

PyTorch's default sample correction would produce a different scale. Specifying correction 0 aligns this fixture with the paired TensorFlow/NumPy calculation.

```python
mean=x.mean(0); scale=x.std(0,correction=0); tx=(x-mean)/scale; vx=(test_x-mean)/scale
assert mean.item()==0; np.testing.assert_allclose(scale.item(),np.sqrt(2.5),atol=1e-6,rtol=0)
```

**Expected:** mean 0; scale sqrt 2.5.

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

**Expected:** positive finite weight after 40 updates.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: 4training records, 2test records. negative 0/1errors; positive \(\frac{1}{1}\). Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Freeze the geometric task.** Use training x-2, -1, 1, 2 with labels 0, 0, 1, 1 and test x-3, 3.
   **Expected:** 4training records, 2test records.
   **Verify:** Save the assertion results for exercise 1, including 4training records, 2test records.

2. **Fit explicit normalization.** Calculate training mean and population standard deviation.
   **Expected:** mean 0; scale sqrt 2.5.
   **Verify:** Save the assertion results for exercise 2, including mean 0; scale sqrt 2.5.

3. **Train a fixed classifier.** Zero-initialize the weight and run 40 SGD with rate 0.1 steps with binary logits loss.
   **Expected:** positive finite weight after 40 updates.
   **Verify:** Save the assertion results for exercise 3, including positive finite weight after 40 updates.

4. **Account for every test prediction.** Threshold test logits at 0 and calculate confusion counts.
   **Expected:** TP 1, TN 1, FP 0, FN 0, total 2.
   **Verify:** Save the assertion results for exercise 4, including TP 1, TN 1, FP 0, FN 0, total 2.

5. **Compare a constant baseline.** Predict class 0 for both test rows and count mistakes.
   **Expected:** baseline 1 error; model 0 on this fixture.
   **Verify:** Save the assertion results for exercise 5, including baseline 1 error; model 0 on this fixture.

6. **Reveal a group-specific failure.** Flip only the positive group decision and report group counts.
   **Expected:** negative 0/1errors; positive \(\frac{1}{1}\).
   **Verify:** Save the assertion results for exercise 6, including negative 0/1errors; positive \(\frac{1}{1}\).

## Common pitfalls and diagnosis

If a paired-framework weight differs, check `correction=0`, initialization, loss reduction, target shape and update count before assuming a backend defect. Compute the first derivative -3/(4sqrt(2.5)) and inspect its sign. If the model predicts both classes incorrectly, verify that thresholding uses logits rather than a second sigmoid interpretation and that truth rows retain their identity order.

If confusion counts do not sum to two, inspect Boolean complements, shape broadcasting and missing rows. If a subgroup report lacks its denominator, it is incomplete. If a result looks exceptionally strong, revisit the public geometric rule, tiny visible holdout and extrapolation range before calling it population evidence. A failed data or evaluation boundary is a no-go result even when the arithmetic accuracy is perfect.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Confusion matrix, Frozen threshold, Population standard deviation using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-023` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Why can identical models disagree after preprocessing?**

Different variance corrections, dtypes or fit partitions change the input values. Framework comparisons must include preprocessing state.

**Does 100 percent on two test rows establish reliability?**

No. It establishes those observations under this fixture. Representative independent data and uncertainty are separate evidence.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-024, Capstone: a small classifier with honest evaluation.
Read courses/deep-learning-pytorch/guides/torch-024.md and courses/deep-learning-pytorch/lessons/torch-024.py. Direct prerequisites: `torch-023`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
