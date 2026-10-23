# torch-012: Capstone: an auditable tiny PyTorch regressor

## Level and prerequisites

Beginner; approximately 180 minutes. Direct prerequisites: `torch-011`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

An auditable regressor combines data identity, a baseline, an explicit training loop and separate assessment. The central investigation is concrete: Use rows zero, e1, e2, e3, [1, 1, 1], [2, 1, 1] and target 2 a-b+c. The finish condition is targets 0, 2, -1, 1, 2, 4. disjoint IDs; holdout count 2; explicit limited scope. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

An auditable regressor combines data identity, a baseline, an explicit training loop and separate assessment. The three-feature fixture uses target 2 a-b+c, so every row can be checked by hand. Four rows are used for fitting and two are reserved for assessment. A training-mean baseline provides a comparison that ignores features. The learned linear model updates under a fixed 100-step budget without using the holdout to choose settings.

The capstone must report what it actually establishes. A small synthetic holdout can show that the implementation uses features in the intended way, but it cannot establish robustness or population accuracy. Keep the scalar arithmetic pilot from lesson 008 as an independent mechanism check alongside the larger experiment. Hashing split IDs records identity; it does not prove the split design was appropriate.

## Design decisions and when to use this method

Use a capstone to combine independently checked boundaries: data identity, fitted baseline, parameter construction, update sequence and held-out evaluation. Prefer a model whose hypothesis class matches the stated synthetic mechanism so implementation errors remain diagnosable. More layers would add ambiguity without making this known linear fixture a stronger population study.

Freeze the split, initial state, rate and 100-step budget before assessment. If the two holdout results trigger another design choice, treat them as selection evidence and use another independent assessment for a fresh claim. Keep an analytic mechanism oracle beside the fitted experiment so a low final error cannot conceal compensating mistakes.

## Paired TensorFlow comparison

Compare [tf-012](../../deep-learning-tensorflow/guides/tf-012.md) after deriving the shared numerical contract.

The paired TensorFlow regressor uses the same feature and target fixture. PyTorch Linear stores the kernel transposed relative to Keras Dense, but both can represent the same function. Compare split IDs, loss reduction, dtype and update budget before interpreting numeric differences.

## Vocabulary and concepts

**Experiment manifest:** The identities and settings needed to reconstruct a run.

**Training baseline:** A simple rule fitted only on training data.

**Frozen assessment:** Evaluation performed after model-selection choices are fixed.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-012/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-012.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-012.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Create X shaped(6, 3), targets shaped(6, 1), and nn.Linear(3, 1, bias=False) with zero weights. Select rows by frozen index lists. Use MSELoss and SGD.1, zeroing gradients every step. Evaluate after the fixed budget under no_grad. Record train and holdout losses with their counts, plus model state and split identities. Do not overwrite the original split after seeing errors.

## Derive a capstone oracle from the training design

The six input rows are zero, the three coordinate basis vectors, then[1, 1, 1] and[2, 1, 1]. The target is 2 a-b+c, so the targets are[0, 2, -1, 1, 2, 4]. The first four rows are training and the last two are assessment. Input shape is(6, 3), target shape(6, 1), and the bias-free Linear stores one row of three weights. This shape contract must remain unchanged throughout fitting and evaluation.

The training-only baseline is(0+2-1+1)/4=0.5. On assessment targets 2 and 4, its squared errors are 2.25 and 12.25, giving MSE 7.25. This baseline ignores features but uses the same assessment records and metric as the learned model. Fitting its constant to the assessment mean would invalidate that comparison.

The basis-vector training design makes the optimizer trajectory independently solvable. Let the stored weight row be w=[w_a, w_b, w_c] and the intended row be w*=[2, -1, 1]. The zero input contributes a zero residual because the model has no bias. The other three rows isolate one coefficient each, so the training objective is:

`L_train(w) = [(w_a-2)²+(w_b+1)²+(w_c-1)²]/4`.

Its gradient is(w-w*)/2. With SGD rate 0.1, one update changes the error to 0.95(w-w*). Starting at zero, after t updates the weight is`w_t=(1-0.95^t)w*`. This oracle does not read PyTorch's gradient buffer or reuse the training-loop implementation. It follows from the declared design matrix and denominator.

After 100 updates, the missing fraction is r=0.95^100, about 0.00592. The weights are approximately[1.98816, -0.99408, 0.99408]. The final training MSE is 1.5r² and the assessment MSE is 10 r², about 0.000351. The assessment formula follows because its predictions are(1-r) times targets 2 and 4, so the two squared residuals are 4 r² and 16 r². These exact symbolic quantities strengthen the capstone beyond merely observing that loss decreased or beat 7.25.

The curve records each loss before that iteration's update. Its first value is 1.5 and its last value corresponds to 99 completed updates, namely 1.5×0.95^198. The separately recomputed final training error follows 100 updates and is 1.5×0.95^200. Calling curve[-1] the final model's loss would create a one-step interpretation error even though every loop operation ran successfully.

The fixture is identifiable within this hypothesis class because the three nonzero training rows span all three feature directions. That mathematical fact helps explain successful recovery on linear combinations of those directions. It does not show that an arbitrary real dataset is linear, noise-free, representative orwell-conditioned. Adding a trainable bias, changing feature scaling oraltering the loss denominator changes the derivation and requires a new oracle.

The final report should retain training and assessment IDs, their counts, parameter dtype and layout, initial state, actual update count, baseline score, final fixed-state errors and the visible synthetic limitation. model.eval() and no_grad make evaluation behavior and derivative recording explicit; no optimizer step occurs during assessment. The two assessment rows demonstrate the intended procedure, but are far too few and too deliberately constructed to support a broad reliability claim.

The paired TensorFlow implementation uses the same mathematical fixture in float32, whereas this PyTorch reference uses float64. Compare the function, transposed kernel layout, denominator and update count before tolerances. A small rounding difference is different from a missing update, an unintended bias or a changed split.

## Worked example / walkthrough

### Example A: Create the three-feature fixture

The target formula is part of the fixture definition. The learner can inspect it without relying on an opaque downloaded dataset.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

x=torch.tensor([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[1.,1.,1.],[2.,1.,1.]],dtype=torch.float64)
y=x@torch.tensor([[2.],[-1.],[1.]],dtype=torch.float64); train=[0,1,2,3]; test=[4,5]
torch.testing.assert_close(y[:,0],torch.tensor([0.,2.,-1.,1.,2.,4.],dtype=torch.float64),atol=0,rtol=0)
```

**Expected:** targets 0, 2, -1, 1, 2, 4.

### Example B: Measure the training-mean baseline

The baseline receives the same assessment rows as the model, but its constant is fitted only on training targets.

```python
mean=y[train].mean(); baseline=((y[test]-mean)**2).mean()
assert mean.item()==.5 and baseline.item()==7.25
```

**Expected:** mean.5; holdout MSE 7.25.

### Example C: Train a bounded linear model

The fixed budget is decided before assessment. A successful decrease demonstrates fitting on exposed data, not generalization by itself.

```python
model=nn.Linear(3,1,bias=False,dtype=torch.float64)
with torch.no_grad(): model.weight.zero_()
optimizer=torch.optim.SGD(model.parameters(),lr=.1); initial=((model(x[train])-y[train])**2).mean().item(); curve=[]
for _ in range(100):
    optimizer.zero_grad(set_to_none=True); loss=((model(x[train])-y[train])**2).mean(); curve.append(loss.item()); loss.backward(); optimizer.step()
assert len(curve)==100 and np.isfinite(curve).all() and curve[-1]<initial
expected_weight=torch.tensor([[2.,-1.,1.]],dtype=torch.float64)*(1-.95**100)
torch.testing.assert_close(model.weight,expected_weight,atol=1e-12,rtol=0)
np.testing.assert_allclose([curve[0],curve[-1]],[1.5,1.5*.95**198],atol=1e-12,rtol=0)
```

**Expected:** 100 finite updates; training loss decreases.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: targets 0, 2, -1, 1, 2, 4. disjoint IDs; holdout count 2; explicit limited scope. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Create the three-feature fixture.** Use rows zero, e1, e2, e3, [1, 1, 1], [2, 1, 1] and target 2 a-b+c.
   **Expected:** targets 0, 2, -1, 1, 2, 4.
   **Verify:** Save the assertion results for exercise 1, including targets 0, 2, -1, 1, 2, 4.

2. **Measure the training-mean baseline.** Fit the constant from training targets and score the two holdout rows.
   **Expected:** mean.5; holdout MSE 7.25.
   **Verify:** Save the assertion results for exercise 2, including mean.5; holdout MSE 7.25.

3. **Train a bounded linear model.** Initialize a bias-free 3-to-1Linear layer at zero and run 100 SGD.1 updates.
   **Expected:** 100 finite updates; training loss decreases.
   **Verify:** Save the assertion results for exercise 3, including 100 finite updates; training loss decreases.

4. **Open the holdout after fitting.** Calculate final training and holdout MSE without updates.
   **Expected:** finite errors; holdout error below 7.25on this fixture.
   **Verify:** Save the assertion results for exercise 4, including finite errors; holdout error below 7.25on this fixture.

5. **Retain an independent pilot oracle.** Calculate the scalar first update directly from NumPy without using the module.
   **Expected:** w28/15and loss 56/675.
   **Verify:** Save the assertion results for exercise 5, including w28/15and loss 56/675.

6. **Write the bounded evidence report.** Record split IDs, 100 steps, errors and the two-row limitation.
   **Expected:** disjoint IDs; holdout count 2; explicit limited scope.
   **Verify:** Save the assertion results for exercise 6, including disjoint IDs; holdout count 2; explicit limited scope.

## Common pitfalls and diagnosis

If fitting fails to approach the coefficient row[2, -1, 1], inspect feature order, stored weight orientation, zero initialization and the no-bias setting. If the learned weight differs from(1-0.95^100) times that row, inspect the denominator and actual number of steps before changing a learning rate. A decrease alone cannot distinguish 99 from 100 updates or an accidental extra intercept.

If a reported final loss matches the last training-curve value rather than the recomputed final model, check the before/after update timing. If the baseline is not 7.25, verify that its mean came only from training targets. If holdout error informed another decision, record that change of role. Preserve the independent scalar pilot and the closed-form capstone trace so a large collection of passing prints cannot replace mechanism-level evidence.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Experiment manifest, Training baseline, Frozen assessment using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-011` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why retain a simple baseline?**

It shows whether the learned feature model adds value over a rule using only training target information. The comparison must use identical assessment units.

**Why keep a scalar pilot beside a capstone?**

The pilot has an independent arithmetic oracle and can localize gradient/update errors that a larger fit may hide.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-012, Capstone: an auditable tiny PyTorch regressor.
Read courses/deep-learning-pytorch/guides/torch-012.md and courses/deep-learning-pytorch/lessons/torch-012.py. Direct prerequisites: `torch-011`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
