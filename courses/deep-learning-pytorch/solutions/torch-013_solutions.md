# torch-013: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A binary logit is an unrestricted score. Its sigmoid maps that score to a number between zero and one under the model's probability convention. BCEWithLogitsLoss combines the sigmoid and binary cross-entropy algebra in a numerically stable form, so its input should be logits rather than already-sigmoid-transformed probabilities. Applying sigmoid twice changes the objective while often producing finite values that look plausible.

A classification threshold is a separate decision policy. Changing it alters predicted labels without changing fitted logits. The threshold can reflect costs or coverage, but must be chosen on validation evidence rather than after viewing final-test results. The tiny scores-2, 0, 2 make the midpoint and boundary policy inspectable. Their probabilities are not automatically calibrated merely because sigmoid produced them.

**Logit:** A binary score before the sigmoid probability transformation.

**BCEWithLogitsLoss:** A stable combined binary logistic objective.

**Decision threshold:** A policy boundary converting probabilities into labels.

## Reading the implementation

F.binary_cross_entropy_with_logits expects floating targets and logits of matching shape. torch.sigmoid is useful for reporting probabilities after the objective convention is fixed. Use probability>=threshold to declare a tie policy. Compare loss at zero logit with log 2 and use extreme logits to check stable arithmetic. Do not infer label correctness from confidence alone.

## Separate score, probability, loss and decision

The binary logit z is unrestricted. Its sigmoid is p=1/(1+exp(-z)), and the unweighted binary cross entropy is -y log p-(1-y)log(1-p). For the declared binary targets y∈{0, 1}, the stable logit-space form is:

`loss = max(z,0) - z*y + log1p(exp(-abs(z)))`.

The exponent is never applied to a large positive magnitude in the final term. This avoids first rounding a probability to zero or one and then taking its logarithm. The derivative with respect to z is p-y before any mean-reduction factor. At z=0, y=1, the loss is log 2 and the derivative is-0.5. A mean across N equally weighted binary entries divides that derivative contribution by N. [PyTorch 2.9 BCEWithLogitsLoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.BCEWithLogitsLoss.html).

For logits[-2, 0, 2], the reported probabilities are approximately[0.1192, 0.5, 0.8808]. They preserve ranking. A threshold 0.5 with a greater-than-or-equal tie rule classifies the zero logit as positive. Threshold 0.8 corresponds to a logit boundary log(0.8/0.2)=log 4, about 1.3863. Moving that boundary changes decisions without changing any fitted parameter orscore.

The double-sigmoid error changes more than a label convention. At original z=0, the first sigmoid gives 0.5. Passing that value as a logit asks the loss to interpret probability sigmoid(0.5), about 0.6225. The positive-label loss becomes log(1+exp(-0.5)), about 0.4741, instead of log 2. If the first sigmoid remains in the graph, the derivative with respect to the original z gains another factor p(1-p): at zero it is about-0.0944 rather than-0.5. Finite outputs therefore do not prove the intended objective orgradient.

Stable arithmetic also does not imply a good prediction. A logit 1000 with label 1 has a loss near zero; the same logit with label 0 has loss near 1000. Both are valid finite outputs of the stable formulation. The extreme-score fixture checks numerical behavior, not whether the labels are correct or the model generalizes.

Decision costs require an additional probability assumption. If p is a calibrated probability for the relevant population, correct decisions have zero cost, false positives cost C_FP and false negatives cost C_FN, then choosing positive has expected cost C_FP(1-p), while choosing negative costs C_FN p. The positive decision is favored when p≥C_FP/(C_FP+C_FN). This derivation does not apply unchanged when costs vary by record, abstention is allowed, capacity is constrained or the probabilities are miscalibrated.

Positive-label weighting changes the loss itself. With positive-term multiplierα, the derivative for a positive target becomesα(p-1), while a negative target contributes p. The reduction convention still matters; do not silently replace the library's element-mean reduction with a sum-of-weights denominator. Such weighting can be useful for a declared fitting goal, but the resulting sigmoid should not be assumed to retain an unweighted population-probability interpretation without further calibration evidence.

The data boundary should validate target range, shape, dtype and finiteness. A floating target tensor is required by this binary objective, but floating representationalone does not prove that its values lie in the intended range. Likewise, a sigmoid output lies between zero and one byconstruction; that mathematical range does not establish empirical reliability. Report ranking, probability loss, decision errors and calibration as related but distinct observations.

## Exercise 1: Convert fixed logits

The question is: Apply sigmoid to-2, 0, 2.

The monotonic transformation preserves ranking. A score of zero is the exact midpoint, which makes threshold ties explicit.

```python
logits=torch.tensor([-2.,0.,2.],dtype=torch.float64); probabilities=torch.sigmoid(logits)
assert probabilities[1].item()==.5 and bool(torch.all(torch.diff(probabilities)>0))
```

**Expected:** middle probability.5 and strictly increasing values.

**Verify:** Compare the computed values or written argument with middle probability.5 and strictly increasing values.

## Exercise 2: Check the midpoint objective

The question is: Compute positive-label BCE at zero logit.

A fifty-fifty prediction assigns probability one-half to the observed label. Its negative logarithm is an independent reference.

```python
loss=F.binary_cross_entropy_with_logits(torch.tensor([0.],dtype=torch.float64),torch.tensor([1.],dtype=torch.float64))
np.testing.assert_allclose(loss.item(),np.log(2),atol=1e-12,rtol=0)
```

**Expected:** loss log 2 within 1e-12.

**Verify:** Compare the computed values or written argument with loss log 2 within 1e-12.

## Exercise 3: Move the decision threshold

The question is: Compare thresholds.5 and.8 with>=ties.

The middle decision changes while the model scores remain fixed. This is a policy change, not an optimizer update.

```python
assert (probabilities>=.5).tolist()==[False,True,True]
assert (probabilities>=.8).tolist()==[False,False,True]
```

**Expected:** labels False, True, True versus False, False, True.

**Verify:** Compare the computed values or written argument with labels False, True, True versus False, False, True.

## Exercise 4: Expose a double-sigmoid mistake

The question is: Feed probability.5 as though it were a logit and compare with log 2.

The API interprets.5 as a score favoring the positive class. It cannot infer that the caller already transformed the score.

```python
wrong=F.binary_cross_entropy_with_logits(torch.tensor([.5],dtype=torch.float64),torch.tensor([1.],dtype=torch.float64))
assert abs(wrong.item()-np.log(2))>.1
```

**Expected:** incorrect loss differs by more than.1.

**Verify:** Compare the computed values or written argument with incorrect loss differs by more than.1.

## Exercise 5: Test extreme finite scores

The question is: Use logits 1000, -1000 with labels 1, 0.

The combined objective avoids an unstable log(sigmoid()) round trip. This protects arithmetic but does not validate labels or shapes.

```python
extreme=F.binary_cross_entropy_with_logits(torch.tensor([1000.,-1000.]),torch.tensor([1.,0.]),reduction='none')
assert torch.isfinite(extreme).all(); torch.testing.assert_close(extreme,torch.zeros(2),atol=1e-6,rtol=0)
```

**Expected:** finite losses approximately 0.

**Verify:** Compare the computed values or written argument with finite losses approximately 0.

## Exercise 6: Count threshold errors

The question is: Use truth 0, 1, 1 and compare the two decision policies.

A decision error count is not the same as probability loss. A different cost matrix or population can favor a different threshold.

```python
truth=torch.tensor([False,True,True])
assert int(((probabilities>=.5)!=truth).sum())==0 and int(((probabilities>=.8)!=truth).sum())==1
```

**Expected:** 0 errors at.5 and 1 at.8.

**Verify:** Compare the computed values or written argument with 0 errors at.5 and 1 at.8.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
