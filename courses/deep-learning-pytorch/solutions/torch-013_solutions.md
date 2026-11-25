# torch-013: explanatory solutions

Open these answers only after attempting Binary logits, BCEWithLogitsLoss and thresholds yourself. They reuse the guide's literal inputs, starting from Example A, Convert fixed logits, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Logit, BCEWithLogitsLoss, Decision threshold. After a pass, choose a new input for exercise 6, Count threshold errors, without looking.

After comparing, follow the [review steps](../STUDY-GUIDE.md#after-the-solutions).

## Mechanism review

A binary logit is an unrestricted score. Its sigmoid maps that score to a number between zero and one under the model's probability convention. BCEWithLogitsLoss combines the sigmoid and binary cross-entropy algebra in a numerically stable form, so its input should be logits rather than already-sigmoid-transformed probabilities. Applying sigmoid twice changes the objective while often producing finite values that look plausible.

A classification threshold is a separate decision policy. Changing it alters predicted labels without changing fitted logits. The threshold can reflect costs or coverage, but must be chosen on validation evidence rather than after viewing final-test results. The tiny scores -2, 0, 2 make the midpoint and boundary policy inspectable. Their probabilities are not automatically calibrated merely because sigmoid produced them.

**Logit:** A binary score before the sigmoid probability transformation.

**BCEWithLogitsLoss:** A stable combined binary logistic objective.

**Decision threshold:** A policy boundary converting probabilities into labels.

## Reading the implementation

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

## Exercise 1: Convert new logits

The question is: Apply sigmoid to the float64 logits -1, 1 and 3.

\(\sigma(-z)=1-\sigma(z)\), so opposite logits give complementary probabilities.

```python
other = torch.tensor([-1.0, 1.0, 3.0], dtype=torch.float64)
converted = torch.sigmoid(other)
np.testing.assert_allclose(
    converted.tolist(),
    [1 / (1 + np.exp(1)), 1 / (1 + np.exp(-1)), 1 / (1 + np.exp(-3))],
    atol=1e-12,
    rtol=0,
)
np.testing.assert_allclose((converted[0] + converted[1]).item(), 1, atol=1e-12, rtol=0)
```

**Expected:** probabilities about 0.2689, 0.7311 and 0.9526; the first two sum to 1.

**Verify:** In a fresh process, the exercise checks confirm `converted.tolist()` matches `[1 / (1 + np.exp(1)), 1 / (1 + np.exp(-1)), 1 / (1 + np.exp(-3))]` within 1e-12 and `(converted[0] + converted[1]).item()` matches `1` within 1e-12.

## Exercise 2: Compute a negative-label loss

The question is: Compute BCEWithLogitsLoss for logit 2 with label 0.

For label 0 the loss is \(-\log(1-\sigma(z))=\log(1+e^{z})\); a confident wrong score is penalized heavily.

```python
negative = F.binary_cross_entropy_with_logits(
    torch.tensor([2.0], dtype=torch.float64), torch.tensor([0.0], dtype=torch.float64)
)
np.testing.assert_allclose(negative.item(), np.log1p(np.exp(2)), atol=1e-12, rtol=0)
```

**Expected:** loss \(\log(1+e^{2})\), about 2.1269, within 1e-12.

**Verify:** In a fresh process, the exercise checks confirm `negative.item()` matches `np.log1p(np.exp(2))` within 1e-12.

## Exercise 3: Threshold the new probabilities

The question is: Classify the new probabilities at thresholds 0.5 and 0.75, counting a probability equal to the threshold as positive.

0.7311 passes 0.5 but not 0.75, so the threshold is a policy choice applied after the model's probability.

```python
assert (converted >= 0.5).tolist() == [False, True, True] and (converted >= 0.75).tolist() == [
    False,
    False,
    True,
]
```

**Expected:** labels False, True, True versus False, False, True.

**Verify:** In a fresh process, the exercise checks confirm `(converted >= 0.5).tolist() == [False, True, True]` and `(converted >= 0.75).tolist() == [False, False, True]`.

## Exercise 4: Expose a double-sigmoid mistake

The question is: Feed probability 0.5 as though it were a logit and compare with log 2.

The API interprets 0.5 as a score favoring the positive class. It cannot infer that the caller already transformed the score.

```python
wrong = F.binary_cross_entropy_with_logits(
    torch.tensor([0.5], dtype=torch.float64), torch.tensor([1.0], dtype=torch.float64)
)
assert abs(wrong.item() - np.log(2)) > 0.1
```

**Expected:** incorrect loss differs by more than 0.1.

**Verify:** In a fresh process, the exercise checks confirm `abs(wrong.item() - np.log(2)) > 0.1`.

## Exercise 5: Test extreme finite scores

The question is: Use logits 1000, -1000 with labels 1, 0.

The combined objective avoids an unstable `log(sigmoid())` round trip. This protects arithmetic but does not validate labels or shapes.

```python
extreme = F.binary_cross_entropy_with_logits(
    torch.tensor([1000.0, -1000.0]), torch.tensor([1.0, 0.0]), reduction="none"
)
assert torch.isfinite(extreme).all()
torch.testing.assert_close(extreme, torch.zeros(2), atol=1e-6, rtol=0)
```

**Expected:** finite losses approximately 0.

**Verify:** In a fresh process, the exercise checks confirm `torch.isfinite(extreme).all()` and `extreme` matches `torch.zeros(2)` within 1e-06.

## Exercise 6: Count threshold errors

The question is: Use truth 0, 1, 1 and compare the two decision policies.

A decision error count is not the same as probability loss. A different cost matrix or population can favor a different threshold.

```python
truth = torch.tensor([False, True, True])
assert (
    int(((probabilities >= 0.5) != truth).sum()) == 0
    and int(((probabilities >= 0.8) != truth).sum()) == 1
)
```

**Expected:** 0 errors at 0.5 and 1 at 0.8.

**Verify:** In a fresh process, the exercise checks confirm `int(((probabilities >= 0.5) != truth).sum()) == 0` and `int(((probabilities >= 0.8) != truth).sum()) == 1`.

