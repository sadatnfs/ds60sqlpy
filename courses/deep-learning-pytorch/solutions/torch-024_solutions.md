# torch-024: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A classifier capstone must connect the task definition to training and evaluation evidence. The literal fixture classifies the sign of a scalar coordinate. Training and test IDs are fixed before fitting. Normalization statistics use only training rows, and the decision threshold is declared before test scoring. Aone-weight logistic model is sufficient for the fixture; unnecessary depth would obscure the experiment rather than improve its meaning.

Report confusion counts and their denominator, not only accuracy. A mean baseline or constant-class baseline provides a comparison under the same held-out units. Per-group failures can be hidden by an aggregate. The tiny test contains only two rows, so the capstone proves an inspectable local pipeline without establishing population reliability. PyTorch standard-deviation defaults differ from NumPy's population default, so the preprocessing comparison must set correction explicitly.

**Confusion matrix:** Counts of true/false positive and negative decisions.

**Frozen threshold:** A decision policy chosen before final assessment.

**Population standard deviation:** A variance calculation dividing by N rather than N-1.

**Subgroup evidence:** Errors and counts reported for a declared subset.

## Reading the implementation

Use X shaped (4, 1), floating binary targets and nn.Linear(1, 1, bias=False). Calculate `x.std(dim=0, correction=0)` to match the declared population normalization fixture. Train with BCEWithLogitsLoss for 40 fixed SGD updates. Evaluate with model.eval and no_grad, then classify \(\mathrm{logits}\ge 0\). Count TP, TN, FP, FN with boolean masks and verify their sum.

## Derive the classifier and audit every assessment row

The training values `[-2, -1, 1, 2]` have mean zero and squared deviations summing to ten. Population variance divides by four, giving 2.5 and scale \(\sqrt{2.5}\). PyTorch's `correction=0` matches NumPy's default used in the paired TensorFlow guide. Using the default sample correction would divide by three and produce \(\sqrt{\frac{10}{3}}\). Both scales are mathematically meaningful statistics, but they define different model inputs and update trajectories. Equal final class labels would not prove framework parity.

The stored model weight has shape (1, 1), inputs and targets have shape (4, 1), and logits have shape (4, 1). The bias is deliberately absent. Binary cross-entropy with logits is applied directly to those logits. Applying sigmoid first and then passing its output to the logits loss would change the objective. A target shaped (4, ) is also a different interface from (4, 1), even when it contains the same four numbers; preserve the declared axes rather than relying on broadcasting or reshaping after a failure.

For one normalized feature t and label y, the logit is \(z=\mathrm{wt}\) and the loss derivative with respect to w is \((\operatorname{sigmoid}(z)-y)t\). At \(w=0\), all probabilities are one-half. Writing \(s=\sqrt{2.5}\), the four derivative contributions are \(\frac{-1}{s}\), -1/(2s), -1/(2s), \(\frac{-1}{s}\). Their mean is -3/(4s), approximately -0.474342. The first SGD step at 0.1 therefore makes w approximately 0.0474342. This analytic sign and scale explain why the later fixed 40-step run should have a positive finite weight.

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

## Exercise 1: Fit normalization on new training values

The question is: Use training inputs 0, 2, 4, 6, compute the mean and population standard deviation, and transform the test input 8.

The squared deviations 9, 1, 1, 9 average to 5; the test value uses the frozen training statistics.

```python
fresh_x = torch.tensor([[0.0], [2.0], [4.0], [6.0]])
centre = fresh_x.mean(0)
spread = fresh_x.std(0, correction=0)
assert centre.item() == 3
np.testing.assert_allclose(spread.item(), np.sqrt(5), atol=1e-6, rtol=0)
np.testing.assert_allclose(
    ((torch.tensor([[8.0]]) - centre) / spread).item(), np.sqrt(5), atol=1e-6, rtol=0
)
```

**Expected:** mean 3; scale \(\sqrt{5}\); transformed test value \(\sqrt{5}\), about 2.2361.

**Verify:** In a fresh process, the exercise checks confirm `centre.item() == 3`, `spread.item()` matches `np.sqrt(5)` within 1e-06 and `((torch.tensor([[8.0]]) - centre) / spread).item()` matches `np.sqrt(5)` within 1e-06.

## Exercise 2: Count a new confusion table

The question is: Compare predictions True, False, True, True with truth True, False, False, True.

Every prediction lands in exactly one cell, so the four counts sum to the record count 4.

```python
predicted = torch.tensor([True, False, True, True])
actual = torch.tensor([True, False, False, True])
counts = {
    "TP": int((predicted & actual).sum()),
    "TN": int((~predicted & ~actual).sum()),
    "FP": int((predicted & ~actual).sum()),
    "FN": int((~predicted & actual).sum()),
}
assert counts == {"TP": 2, "TN": 1, "FP": 1, "FN": 0}
```

**Expected:** TP 2, TN 1, FP 1, FN 0.

**Verify:** In a fresh process, the exercise checks confirm `counts == {'TP': 2, 'TN': 1, 'FP': 1, 'FN': 0}`.

## Exercise 3: Classify with a fixed weight

The question is: With weight 2 and no bias, classify the normalized inputs -1.5, -0.2, 0 and 0.4 at logit 0, counting 0 as positive.

The decision depends on the sign of the logit; the tie rule assigns the zero logit to the positive class.

```python
logits_t = 2 * torch.tensor([-1.5, -0.2, 0.0, 0.4])
assert (logits_t >= 0).tolist() == [False, False, True, True]
```

**Expected:** False, False, True, True.

**Verify:** In a fresh process, the exercise checks confirm `(logits_t >= 0).tolist() == [False, False, True, True]`.

## Exercise 4: Account for every test prediction

The question is: Threshold test logits at 0 and calculate confusion counts.

The conservation check prevents dropped or duplicated test rows from silently changing the metric.

```python
model.eval()
with torch.no_grad():
    prediction = model(vx).ravel() >= 0
counts = {
    "tp": int((prediction & truth).sum()),
    "tn": int((~prediction & ~truth).sum()),
    "fp": int((prediction & ~truth).sum()),
    "fn": int((~prediction & truth).sum()),
}
assert counts == {"tp": 1, "tn": 1, "fp": 0, "fn": 0} and sum(counts.values()) == 2
```

**Expected:** TP 1, TN 1, FP 0, FN 0, total 2.

**Verify:** In a fresh process, the exercise checks confirm `counts == {'tp': 1, 'tn': 1, 'fp': 0, 'fn': 0}` and `sum(counts.values()) == 2`.

## Exercise 5: Compare a constant baseline

The question is: Predict class 0 for both test rows and count mistakes.

The comparison uses identical test units. It does not justify a population claim from two cases.

```python
baseline = torch.zeros(2, dtype=torch.bool)
assert int((baseline != truth).sum()) == 1 and int((prediction != truth).sum()) == 0
```

**Expected:** baseline 1 error; model 0 on this fixture.

**Verify:** In a fresh process, the exercise checks confirm `int((baseline != truth).sum()) == 1` and `int((prediction != truth).sum()) == 0`.

## Exercise 6: Reveal a group-specific failure

The question is: Flip only the positive group decision and report group counts.

A global error rate of one-half would hide the entire failure in the positive group. Counts and group meaning belong beside the aggregate.

```python
broken = prediction.clone()
broken[1] = False
report = {
    group: (int(broken[i] != truth[i]), 1) for i, group in enumerate(["negative", "positive"])
}
assert report == {"negative": (0, 1), "positive": (1, 1)}
```

**Expected:** negative class: 0 of 1 wrong; positive class: 1 of 1 wrong.

**Verify:** In a fresh process, the exercise checks confirm `report == {'negative': (0, 1), 'positive': (1, 1)}`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
