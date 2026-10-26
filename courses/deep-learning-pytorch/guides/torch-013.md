# torch-013: Binary logits, BCEWithLogitsLoss and thresholds

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-012`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A binary logit is an unrestricted score. The central investigation is concrete: Apply sigmoid to-2, 0, 2. The finish condition is middle probability 0.5 and strictly increasing values. 0 errors at.5 and 1 at.8. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A binary logit is an unrestricted score. Its sigmoid maps that score to a number between zero and one under the model's probability convention. BCEWithLogitsLoss combines the sigmoid and binary cross-entropy algebra in a numerically stable form, so its input should be logits rather than already-sigmoid-transformed probabilities. Applying sigmoid twice changes the objective while often producing finite values that look plausible.

A classification threshold is a separate decision policy. Changing it alters predicted labels without changing fitted logits. The threshold can reflect costs or coverage, but must be chosen on validation evidence rather than after viewing final-test results. The tiny scores-2, 0, 2 make the midpoint and boundary policy inspectable. Their probabilities are not automatically calibrated merely because sigmoid produced them.

## Design decisions and when to use this method

Use one logit per binary event when the target represents a yes/no outcome. Keep the training objective in logit space and apply sigmoid for a probability-oriented report or decision policy. Choose threshold, calibration and error costs using an appropriate validation protocol rather than tuning them on a final assessment.

Before using class orpositive-label weights, write the weighted objective and its denominator. Weighting changes the fitting target and can change the meaning of the raw sigmoid output. It is not equivalent to changing a decision threshold after fitting, and it does not independently establish calibrated probabilities on a new population.

## Paired TensorFlow comparison

Compare [tf-013](../../deep-learning-tensorflow/guides/tf-013.md) after deriving the shared numerical contract.

TensorFlow's sigmoid-cross-entropy-with-logits operation and PyTorch BCEWithLogitsLoss share the logit convention. Keras BinaryCrossentropy requires its from_logits setting to agree with the model output. Match dtype, shape and element reduction before comparing scalar values.

## Vocabulary and concepts

**Logit:** A binary score before the sigmoid probability transformation.

**BCEWithLogitsLoss:** A stable combined binary logistic objective.

**Decision threshold:** A policy boundary converting probabilities into labels.

## How to run this lesson

Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **Deep Learning with PyTorch: tensors to reliable model releases** subject and select `torch-013`. Use its `llm-torch-cpu` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `courses/deep-learning-pytorch/lessons/torch-013.py` under `.learning/expansion/torch-013/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

`F.binary_cross_entropy_with_logits` expects floating targets and logits of matching shape. `torch.sigmoid` is useful for reporting probabilities after the objective convention is fixed. Use `probability>=threshold` to declare a tie policy. Compare loss at zero logit with log 2 and use extreme logits to check stable arithmetic. Do not infer label correctness from confidence alone.

## Separate score, probability, loss and decision

The binary logit z is unrestricted. Its sigmoid is \(p=\frac{1}{1+\exp(-z)}\), and the unweighted binary cross entropy is \(-y\log p-(1-y)\log(1-p)\). For the declared binary targets y∈{0, 1}, the stable logit-space form is:

`loss = max(z,0) - z*y + log1p(exp(-abs(z)))`.

The exponent is never applied to a large positive magnitude in the final term. This avoids first rounding a probability to zero or one and then taking its logarithm. The derivative with respect to z is p-y before any mean-reduction factor. At \(z=0\), \(y=1\), the loss is log 2 and the derivative is-0.5. A mean across N equally weighted binary entries divides that derivative contribution by N. [PyTorch 2.9 BCEWithLogitsLoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.BCEWithLogitsLoss.html).

For logits[-2, 0, 2], the reported probabilities are approximately[0.1192, 0.5, 0.8808]. They preserve ranking. A threshold 0.5 with a greater-than-or-equal tie rule classifies the zero logit as positive. Threshold 0.8 corresponds to a logit boundary \(\log\!\left(\frac{0.8}{0.2}\right)=\log4\), about 1.3863. Moving that boundary changes decisions without changing any fitted parameter or score.

The double-sigmoid error changes more than a label convention. At original \(z=0\), the first sigmoid gives 0.5. Passing that value as a logit asks the loss to interpret probability \(\sigma(0.5)\), about 0.6225. The positive-label loss becomes \(\log(1+\exp(-0.5))\), about 0.4741, instead of log 2. If the first sigmoid remains in the graph, the derivative with respect to the original z gains another factor p(1-p): at zero it is about-0.0944 rather than-0.5. Finite outputs therefore do not prove the intended objective or gradient.

Stable arithmetic also does not imply a good prediction. A logit 1000 with label 1 has a loss near zero; the same logit with label 0 has loss near 1000. Both are valid finite outputs of the stable formulation. The extreme-score fixture checks numerical behavior, not whether the labels are correct or the model generalizes.

Decision costs require an additional probability assumption. If p is a calibrated probability for the relevant population, correct decisions have zero cost, false positives cost C_FP and false negatives cost C_FN, then choosing positive has expected cost C_FP(1-p), while choosing negative costs C_FN p. The positive decision is favored when p≥\(\frac{C_{\mathrm{FP}}}{C_{\mathrm{FP}}+C_{\mathrm{FN}}}\). This derivation does not apply unchanged when costs vary by record, abstention is allowed, capacity is constrained or the probabilities are miscalibrated.

Positive-label weighting changes the loss itself. With positive-term multiplierα, the derivative for a positive target becomesα(p-1), while a negative target contributes p. The reduction convention still matters; do not silently replace the library's element-mean reduction with a sum-of-weights denominator. Such weighting can be useful for a declared fitting goal, but the resulting sigmoid should not be assumed to retain an unweighted population-probability interpretation without further calibration evidence.

The data boundary should validate target range, shape, dtype and finiteness. A floating target tensor is required by this binary objective, but floating representation alone does not prove that its values lie in the intended range. Likewise, a sigmoid output lies between zero and one by construction; that mathematical range does not establish empirical reliability. Report ranking, probability loss, decision errors and calibration as related but distinct observations.

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

**Expected:** middle probability 0.5 and strictly increasing values.

### Example B: Check the midpoint objective

A fifty-fifty prediction assigns probability one-half to the observed label. Its negative logarithm is an independent reference.

```python
loss=F.binary_cross_entropy_with_logits(torch.tensor([0.],dtype=torch.float64),torch.tensor([1.],dtype=torch.float64))
np.testing.assert_allclose(loss.item(),np.log(2),atol=1e-12,rtol=0)
```

**Expected:** loss log 2 within 1e-12.

### Example C: Move the decision threshold

The middle decision changes while the model scores remain fixed. This is a policy change, not an optimizer update.

```python
assert (probabilities>=.5).tolist()==[False,True,True]
assert (probabilities>=.8).tolist()==[False,False,True]
```

**Expected:** labels False, True, True versus False, False, True.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: middle probability 0.5 and strictly increasing values. 0 errors at.5 and 1 at.8. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Convert fixed logits.** Apply sigmoid to-2, 0, 2.
   **Expected:** middle probability 0.5 and strictly increasing values.
   **Verify:** Save the assertion results for exercise 1, including middle probability 0.5 and strictly increasing values.

2. **Check the midpoint objective.** Compute positive-label BCE at zero logit.
   **Expected:** loss log 2 within 1e-12.
   **Verify:** Save the assertion results for exercise 2, including loss log 2 within 1e-12.

3. **Move the decision threshold.** Compare thresholds.5 and.8 with>=ties.
   **Expected:** labels False, True, True versus False, False, True.
   **Verify:** Save the assertion results for exercise 3, including labels False, True, True versus False, False, True.

4. **Expose a double-sigmoid mistake.** Feed probability 0.5 as though it were a logit and compare with log 2.
   **Expected:** incorrect loss differs by more than.1.
   **Verify:** Save the assertion results for exercise 4, including incorrect loss differs by more than.1.

5. **Test extreme finite scores.** Use logits 1000, -1000 with labels 1, 0.
   **Expected:** finite losses approximately 0.
   **Verify:** Save the assertion results for exercise 5, including finite losses approximately 0.

6. **Count threshold errors.** Use truth 0, 1, 1 and compare the two decision policies.
   **Expected:** 0 errors at.5 and 1 at.8.
   **Verify:** Save the assertion results for exercise 6, including 0 errors at.5 and 1 at.8.

## Common pitfalls and diagnosis

If loss is finite but training is unexpectedly weak, inspect whether sigmoid was applied before a logits-aware objective. Compare both the midpoint loss and the derivative, not only the predicted labels. If extreme scores produce NaN in a hand-written `log(sigmoid())` path, use the combined objective rather than clipping until an assertion passes.

If error counts change while logits stay fixed, inspect threshold and tie policy before blaming optimization. If a confidence score is presented as an empirical success frequency, look for calibration evidence on the relevant population. If positive-label weights were introduced, record the changed objective and denominator. Validate target range and matching shape explicitly instead of treating a successful API call as a complete data contract.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Logit, BCEWithLogitsLoss, Decision threshold using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-012` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

**Why prefer BCEWithLogitsLoss over manually applying sigmoid and log?**

The combined implementation can rearrange the algebra to avoid overflow and loss of precision at extreme scores. Manual probability conversion can round to zero or one first.

**Does a probability.9 mean 90 percent of such predictions are correct?**

Only if calibration evidence supports that interpretation for the relevant population. Sigmoid alone defines a model output, not an empirical reliability guarantee.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-013, Binary logits, BCEWithLogitsLoss and thresholds.
Read courses/deep-learning-pytorch/guides/torch-013.md and courses/deep-learning-pytorch/lessons/torch-013.py. Direct prerequisites: `torch-012`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
