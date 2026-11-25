# torch-013: Binary logits, BCEWithLogitsLoss and thresholds

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-012`.

## Learning objectives

Train binary classifiers on logits with BCEWithLogitsLoss and choose a decision threshold as a separate, explicit policy.

Central investigation: Convert the logits -2, 0 and 2 to probabilities, evaluate the zero-logit loss, compare thresholds 0.5 and 0.8 and feed a probability into a logits loss by mistake.

Finish condition: The middle probability is 0.5, the zero-logit loss is log 2, threshold 0.5 gives 0 errors and 0.8 gives 1 on truth 0, 1, 1, the double-sigmoid loss differs by more than 0.1, and logits of magnitude 1000 stay finite.

## Purpose and mental model

A binary logit is an unrestricted score. Its sigmoid maps that score to a number between zero and one under the model's probability convention. BCEWithLogitsLoss combines the sigmoid and binary cross-entropy algebra in a numerically stable form, so its input should be logits rather than already-sigmoid-transformed probabilities. Applying sigmoid twice changes the objective while often producing finite values that look plausible.

A classification threshold is a separate decision policy. Changing it alters predicted labels without changing fitted logits. The threshold can reflect costs or coverage, but must be chosen on validation evidence rather than after viewing final-test results. The tiny scores -2, 0, 2 make the midpoint and boundary policy inspectable. Their probabilities are not automatically calibrated merely because sigmoid produced them.

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

Run `torch-013` on the `llm-torch-cpu` worker ([launch, save and tolerance rules](../STUDY-GUIDE.md#launch-a-lesson)).

Examples B and C reuse `probabilities` from earlier blocks; run all three in order.

## Syntax anatomy and reasoning sequence

`F.binary_cross_entropy_with_logits` expects floating targets and logits of matching shape. `torch.sigmoid` is useful for reporting probabilities after the objective convention is fixed. Use `probability>=threshold` to declare a tie policy. Compare loss at zero logit with log 2 and use extreme logits to check stable arithmetic. Do not infer label correctness from confidence alone.

## Separate score, probability, loss and decision

The binary logit z is unrestricted. Its sigmoid is \(p=\frac{1}{1+\exp(-z)}\), and the unweighted binary cross entropy is \(-y\log p-(1-y)\log(1-p)\). For the declared binary targets y∈{0, 1}, the stable logit-space form is:

`loss = max(z,0) - z*y + log1p(exp(-abs(z)))`.

The exponent is never applied to a large positive magnitude in the final term. This avoids first rounding a probability to zero or one and then taking its logarithm. The derivative with respect to z is p-y before any mean-reduction factor. At \(z=0\), \(y=1\), the loss is log 2 and the derivative is -0.5. A mean across N equally weighted binary entries divides that derivative contribution by N. [PyTorch 2.9 BCEWithLogitsLoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.BCEWithLogitsLoss.html).

For logits [-2, 0, 2], the reported probabilities are approximately [0.1192, 0.5, 0.8808]. They preserve ranking. A threshold 0.5 with a greater-than-or-equal tie rule classifies the zero logit as positive. Threshold 0.8 corresponds to a logit boundary \(\log\!\left(\frac{0.8}{0.2}\right)=\log4\), about 1.3863. Moving that boundary changes decisions without changing any fitted parameter or score.

The double-sigmoid error changes more than a label convention. At original \(z=0\), the first sigmoid gives 0.5. Passing that value as a logit asks the loss to interpret probability \(\sigma(0.5)\), about 0.6225. The positive-label loss becomes \(\log(1+\exp(-0.5))\), about 0.4741, instead of log 2. If the first sigmoid remains in the graph, the derivative with respect to the original z gains another factor p(1-p): at zero it is about -0.0944 rather than -0.5. Finite outputs therefore do not prove the intended objective or gradient.

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

logits = torch.tensor([-2.0, 0.0, 2.0], dtype=torch.float64)
probabilities = torch.sigmoid(logits)
assert probabilities[1].item() == 0.5 and bool(torch.all(torch.diff(probabilities) > 0))
```

**Expected:** middle probability 0.5 and strictly increasing values.

### Example B: Check the midpoint objective

A fifty-fifty prediction assigns probability one-half to the observed label. Its negative logarithm is an independent reference.

```python
loss = F.binary_cross_entropy_with_logits(
    torch.tensor([0.0], dtype=torch.float64), torch.tensor([1.0], dtype=torch.float64)
)
np.testing.assert_allclose(loss.item(), np.log(2), atol=1e-12, rtol=0)
```

**Expected:** loss log 2 within 1e-12.

### Example C: Move the decision threshold

The middle decision changes while the model scores remain fixed. This is a policy change, not an optimizer update.

```python
assert (probabilities >= 0.5).tolist() == [False, True, True]
assert (probabilities >= 0.8).tolist() == [False, False, True]
```

**Expected:** labels False, True, True versus False, False, True.

## Prediction before your attempt

Derive Example A again with its **Expected** line covered: Convert fixed logits. Predict exercise 6, Count threshold errors, from its prompt alone: Use truth 0, 1, 1 and compare the two decision policies. Then explain why this finish condition holds: The middle probability is 0.5, the zero-logit loss is log 2, threshold 0.5 gives 0 errors and 0.8 gives 1 on truth 0, 1, 1, the double-sigmoid loss differs by more than 0.1, and logits of magnitude 1000 stay finite. Keep each prediction beside the observed value.

## Exercises

1. **Convert new logits.** Apply sigmoid to the float64 logits -1, 1 and 3.
   **Expected:** probabilities about 0.2689, 0.7311 and 0.9526; the first two sum to 1.
   **Verify:** In a fresh process, the exercise checks confirm `converted.tolist()` matches `[1 / (1 + np.exp(1)), 1 / (1 + np.exp(-1)), 1 / (1 + np.exp(-3))]` within 1e-12 and `(converted[0] + converted[1]).item()` matches `1` within 1e-12.

2. **Compute a negative-label loss.** Compute BCEWithLogitsLoss for logit 2 with label 0.
   **Expected:** loss \(\log(1+e^{2})\), about 2.1269, within 1e-12.
   **Verify:** In a fresh process, the exercise checks confirm `negative.item()` matches `np.log1p(np.exp(2))` within 1e-12.

3. **Threshold the new probabilities.** Classify the new probabilities at thresholds 0.5 and 0.75, counting a probability equal to the threshold as positive.
   **Expected:** labels False, True, True versus False, False, True.
   **Verify:** In a fresh process, the exercise checks confirm `(converted >= 0.5).tolist() == [False, True, True]` and `(converted >= 0.75).tolist() == [False, False, True]`.

4. **Expose a double-sigmoid mistake.** Feed probability 0.5 as though it were a logit and compare with log 2.
   **Expected:** incorrect loss differs by more than 0.1.
   **Verify:** In a fresh process, the exercise checks confirm `abs(wrong.item() - np.log(2)) > 0.1`.

5. **Test extreme finite scores.** Use logits 1000, -1000 with labels 1, 0.
   **Expected:** finite losses approximately 0.
   **Verify:** In a fresh process, the exercise checks confirm `torch.isfinite(extreme).all()` and `extreme` matches `torch.zeros(2)` within 1e-06.

6. **Count threshold errors.** Use truth 0, 1, 1 and compare the two decision policies.
   **Expected:** 0 errors at 0.5 and 1 at 0.8.
   **Verify:** In a fresh process, the exercise checks confirm `int(((probabilities >= 0.5) != truth).sum()) == 0` and `int(((probabilities >= 0.8) != truth).sum()) == 1`.

## Common pitfalls and diagnosis

If loss is finite but training is unexpectedly weak, inspect whether sigmoid was applied before a logits-aware objective. Compare both the midpoint loss and the derivative, not only the predicted labels. If extreme scores produce NaN in a hand-written `log(sigmoid())` path, use the combined objective rather than clipping until an assertion passes.

If error counts change while logits stay fixed, inspect threshold and tie policy before blaming optimization. If a confidence score is presented as an empirical success frequency, look for calibration evidence on the relevant population. If positive-label weights were introduced, record the changed objective and denominator. Validate target range and matching shape explicitly instead of treating a successful API call as a complete data contract.

## Progressive hints

Hint 1: Example B (Check the midpoint objective) alters one assumption of Example A (Convert fixed logits). Hint 2: exercise 4, Expose a double-sigmoid mistake, should end at incorrect loss differs by more than 0.1. Work backward from it. Hint 3: exercise 5, Test extreme finite scores, changes one input; predict which value moves first.

## Self-check and retrieval

Close the worked examples and rebuild Example C, Move the decision threshold, from its inputs alone. Predict whether exercise 3, Threshold the new probabilities, survives one changed input. Then explain Logit, BCEWithLogitsLoss, Decision threshold in terms of that fixture; say which claims the code guarantees and which need new observations.

## Next step

If Example A (Convert fixed logits) cannot be rebuilt without help, revisit `torch-012` first. `torch-014` (CrossEntropyLoss, multiclass and multilabel contracts) builds directly on this lesson.

## Sources and verification status

API and mechanism reference: [PyTorch 2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22 for the Logit, BCEWithLogitsLoss, Decision threshold behavior these fixtures check ([verification status](../STUDY-GUIDE.md#sources-and-verification-status)).

## Interview reasoning with worked answers

**Why prefer BCEWithLogitsLoss over manually applying sigmoid and log?**

The combined implementation can rearrange the algebra to avoid overflow and loss of precision at extreme scores. Manual probability conversion can round to zero or one first.

**Does a probability 0.9 mean 90 percent of such predictions are correct?**

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
