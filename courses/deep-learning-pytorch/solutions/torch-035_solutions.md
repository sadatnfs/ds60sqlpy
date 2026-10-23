# torch-035: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Model comparisons should preserve the pairing between predictions on the same held-out identities. Subtract per-record losses before averaging, so shared case difficulty remains represented. A bootstrap resamples observed units with replacement and estimates variability under a stated sampling model. It cannot repair biased data or create independent units from many duplicates. Related records may need group-level resampling rather than row-level draws.

PyTorch generators provide a local reproducible random stream for this calculation. A seed makes an implementation repeatable in the tested runtime, but does not make the inference assumptions valid. Keep model selection on validation data and freeze the final test before choosing a winner. A confidence interval or mean loss difference is one piece of evidence, not a complete release policy.

**Paired difference:** The loss contrast for the same identified observation.

**Resampling unit:** The independent entity selected during a bootstrap draw.

**Selection bias:** Optimism introduced when evaluation results guide configuration choices.

**Local generator:** An explicit random-state object separate from unrelated global draws.

## Reading the implementation

Align prediction dictionaries by stable IDs and check equal keysets. Calculate squared-error A minus squared-errorB for each ID. Sample indices with torch.rand int and an explicit Generator, then index the paired difference vector. Use the same resampling unit for both systems by resampling the already-paired values. Report independent count and selection history beside the estimate.

## Derive the paired contrast and the finite bootstrap law

Align by stable ID before calculating losses. The fixture's dictionary insertion orders differ, so zipping values would compare unrelated targets and predictions. The correct table is:

| ID | Truth | A prediction | B prediction | A squared loss | B squared loss | A minus B |
| --- | --- | --- | --- | --- | --- | --- |
| a | 0 | 0 | 1 | 0 | 1 | -1 |
| b | 1 | 2 | 2 | 1 | 1 | 0 |
| c | 2 | 2 | 3 | 0 | 1 | -1 |

The mean contrast is-2/3 in squared-target units. Its sign favors A for this loss and these three cases. It does not mean A wins on every possible metric, group or deployment condition. Equal key sets are required before indexing; silently dropping missing predictions can select an easier assessment subset.

Pairing preserves shared case difficulty. In general, Var(lossA-lossB)=Var(lossA)+Var(lossB)-2Cov(lossA, lossB). Independently resampling the two models discards that covariance and answers a different question. The particular fixture has B losses all equal to one, so its covariance term is zero; it is not by itself a strong counterexample for every unpaired bootstrap mistake.

A separate analytic example makes the dependence visible. Suppose two cases have losses A=[1, 11] and B=[0, 10]. Every paired difference is one, so every paired resampled mean is one. Independent resampling can pair the easy A loss with the hard B loss or vice versa and create variation that was absent from the paired contrast. This explains the method without claiming that the original three-case code exercised that different fixture.

For the actual differences[-1, 0, -1], an empirical draw has probability 2/3 of-1 and 1/3 of zero. Each bootstrap estimate averages three independent draws from that empirical distribution. Let K count the selected-1 values; then K has a Binomial(3, 2/3) law and the estimate is-K/3:

| Resampled mean | Exact empirical probability |
| --- | --- |
| -1 | 8/27 |
| -2/3 | 12/27 |
| -1/3 | 6/27 |
| 0 | 1/27 |

The expected bootstrap mean is-2/3 and its variance is 2/27 under this empirical resampling model. These are properties of resampling the three observed values, not a proof that the unknown population has this four-point distribution. The thousand generated estimates approximate these probabilities with random frequency variation. The reference checks shape, finiteness and the exact allowed range, not a guaranteed count for each value.

More draws refine the numerical approximation to that empirical distribution. They do not turn three cases into a thousand independent assessment observations. Even the ideal empirical percentile interval can be uninformative here: the lower tail includes-1 and the upper tail reaches zero. The code does not calculate or certify a particular confidence interval, and any interval method would still need its sampling assumptions and quantile convention stated.

If several rows come from one source family, resample families together when the intended independence is at that level. Define the estimand as well: equal family means and row-weighted population means differ when families have different sizes. Time dependence may require blocks or another design rather than an ordinary independent-row bootstrap. Stable row IDs alone do not resolve those dependencies.

The local torch.Generator makes this calculation reproducible without depending on unrelated global draws. A fresh generator seeded identically reproduces the index matrix in the tested environment. NumPy's generator in the paired TensorFlow route is a different random implementation; identical seed numbers do not require identical index matrices across the two libraries. Compare the statistical contract, allowed values and within-implementation replay rather than treating cross-library random bits as a shared oracle.

This resampling holds the fitted prediction vectors fixed. It does not include variation from retraining with a different initialization, batch order or training sample. If the decision concerns the whole fitting procedure, that uncertainty needs a broader experimental design. If test results are used to select another architecture, threshold or stopping rule, the test has become selection information. An unchanged filename cannot restore an untouched assessment boundary.

Finally, a negative point estimate is not a complete release decision. Record effect size, uncertainty, assessment coverage, severe failures and operating costs under their own evidence. The tiny fixture teaches pairing and resampling mechanics while making its limited independent sample size explicit.

## Exercise 1: Align predictions by ID

The question is: Use truth a0, b1, c2 with A0, 2, 2 and B 1, 2, 3 in different dictionary order.

Dictionary insertion order is not an identity join. The contrast must keep each prediction attached to its own target.

```python
truth={'a':0.,'b':1.,'c':2.}; a={'a':0.,'b':2.,'c':2.}; b={'c':3.,'a':1.,'b':2.}; ids=sorted(truth)
difference=torch.tensor([(a[i]-truth[i])**2-(b[i]-truth[i])**2 for i in ids],dtype=torch.float64)
assert difference.tolist()==[-1.,0.,-1.]
```

**Expected:** paired squared-loss differences-1, 0, -1.

**Verify:** Compare the computed values or written argument with paired squared-loss differences-1, 0, -1.

## Exercise 2: Interpret the average contrast

The question is: Average the three paired differences.

The sign follows the declared A-minus-Blossorder. A negative value favors A only for this metric and assessment set.

```python
np.testing.assert_allclose(difference.mean().item(),-2/3,atol=1e-12,rtol=0)
```

**Expected:** mean-2/3, favoring A on this loss fixture.

**Verify:** Compare the computed values or written argument with mean-2/3, favoring A on this loss fixture.

## Exercise 3: Resample pairs reproducibly

The question is: Draw 1000 three-index bootstrap samples with local Generator seed 7.

The known range of per-record differences bounds every resampled mean. That independent bound can expose an indexing or reduction error.

```python
generator=torch.Generator().manual_seed(7); indices=torch.randint(0,3,(1000,3),generator=generator); estimates=difference[indices].mean(1)
assert tuple(estimates.shape)==(1000,) and torch.isfinite(estimates).all() and estimates.min()>=-1 and estimates.max()<=0
```

**Expected:** 1000finite estimates within-1..0.

**Verify:** Compare the computed values or written argument with 1000finite estimates within-1..0.

## Exercise 4: Replay the local random stream

The question is: Create a new Generator with seed 7 and compare the index matrix.

Reusing an advanced generator would not replay the beginning. The generator state is part of the reproducibility record.

```python
again=torch.randint(0,3,(1000,3),generator=torch.Generator().manual_seed(7))
assert torch.equal(indices,again)
```

**Expected:** exact match.

**Verify:** Compare the computed values or written argument with exact match.

## Exercise 5: Reject missing assessment identities

The question is: Remove c from one prediction dictionary and check the keyset.

Silently inner-joining would drop a missing prediction and change the evaluation population. Define a failure policy instead of removing hard cases.

```python
missing={key:value for key,value in b.items() if key!='c'}
assert set(missing)!=set(truth)
```

**Expected:** mismatch detected before comparison.

**Verify:** Compare the computed values or written argument with mismatch detected before comparison.

## Exercise 6: Preserve a final-test boundary

The question is: Record configuration choice on validation and assessment on test; flag a test-driven new choice.

The boundary depends on the actual decision sequence, not on the dataset filename. After test-driven changes, new untouched evidence is needed.

```python
ledger=[('choose','validation'),('assess','test')]
assert all(partition=='validation' for action,partition in ledger if action=='choose')
assert ('choose','test')[1]!='validation'
```

**Expected:** test selection violates the declared boundary.

**Verify:** Compare the computed values or written argument with test selection violates the declared boundary.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
