# torch-035: explanatory solutions

Open these answers only after attempting Paired model comparisons and uncertainty yourself. They reuse the guide's literal inputs, starting from Example A, Align predictions by ID, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Paired difference, Resampling unit, Selection bias. After a pass, choose a new input for exercise 6, Preserve a final-test boundary, without looking.

After comparing, follow the [review steps](../STUDY-GUIDE.md#after-the-solutions).

## Mechanism review

Model comparisons should preserve the pairing between predictions on the same held-out identities. Subtract per-record losses before averaging, so shared case difficulty remains represented. A bootstrap resamples observed units with replacement and estimates variability under a stated sampling model. It cannot repair biased data or create independent units from many duplicates. Related records may need group-level resampling rather than row-level draws.

PyTorch generators provide a local reproducible random stream for this calculation. A seed makes an implementation repeatable in the tested runtime, but does not make the inference assumptions valid. Keep model selection on validation data and freeze the final test before choosing a winner. A confidence interval or mean loss difference is one piece of evidence, not a complete release policy.

**Paired difference:** The loss contrast for the same identified observation.

**Resampling unit:** The independent entity selected during a bootstrap draw.

**Selection bias:** Optimism introduced when evaluation results guide configuration choices.

**Local generator:** An explicit random-state object separate from unrelated global draws.

## Reading the implementation

Align prediction dictionaries by stable IDs and check equal keysets. Calculate squared error A minus squared error B for each ID. Sample indices with torch.randint and an explicit Generator, then index the paired difference vector. Use the same resampling unit for both systems by resampling the already-paired values. Report independent count and selection history beside the estimate.

## Derive the paired contrast and the finite bootstrap law

Align by stable ID before calculating losses. The fixture's dictionary insertion orders differ, so zipping values would compare unrelated targets and predictions. The correct table is:

| ID | Truth | A prediction | B prediction | A squared loss | B squared loss | A minus B |
| --- | --- | --- | --- | --- | --- | --- |
| a | 0 | 0 | 1 | 0 | 1 | -1 |
| b | 1 | 2 | 2 | 1 | 1 | 0 |
| c | 2 | 2 | 3 | 0 | 1 | -1 |

The mean contrast is \(\frac{-2}{3}\) in squared-target units. Its sign favors A for this loss and these three cases. It does not mean A wins on every possible metric, group or deployment condition. Equal key sets are required before indexing; silently dropping missing predictions can select an easier assessment subset.

Pairing preserves shared case difficulty. In general, \(\operatorname{Var}(\ell_A-\ell_B)=\operatorname{Var}(\ell_A)+\operatorname{Var}(\ell_B)-2\operatorname{Cov}(\ell_A,\ell_B)\). Independently resampling the two models discards that covariance and answers a different question. The particular fixture has B losses all equal to one, so its covariance term is zero; it is not by itself a strong counterexample for every unpaired bootstrap mistake.

A separate analytic example makes the dependence visible. Suppose two cases have losses A=[1, 11] and B=[0, 10]. Every paired difference is one, so every paired resampled mean is one. Independent resampling can pair the easy A loss with the hard B loss or vice versa and create variation that was absent from the paired contrast. This explains the method without claiming that the original three-case code exercised that different fixture.

For the actual differences [-1, 0, -1], an empirical draw has probability \(\frac{2}{3}\) of -1 and \(\frac{1}{3}\) of zero. Each bootstrap estimate averages three independent draws from that empirical distribution. Let K count the selected-1 values; then K has a Binomial(3, \(\frac{2}{3}\)) law and the estimate is -K/3:

| Resampled mean | Exact empirical probability |
| --- | --- |
| -1 | \(\frac{8}{27}\) |
| \(\frac{-2}{3}\) | \(\frac{12}{27}\) |
| \(\frac{-1}{3}\) | \(\frac{6}{27}\) |
| 0 | \(\frac{1}{27}\) |

The expected bootstrap mean is \(\frac{-2}{3}\) and its variance is \(\frac{2}{27}\) under this empirical resampling model. These are properties of resampling the three observed values, not a proof that the unknown population has this four-point distribution. The thousand generated estimates approximate these probabilities with random frequency variation. The reference checks shape, finiteness and the exact allowed range, not a guaranteed count for each value.

More draws refine the numerical approximation to that empirical distribution. They do not turn three cases into a thousand independent assessment observations. Even the ideal empirical percentile interval can be uninformative here: the lower tail includes-1 and the upper tail reaches zero. The code does not calculate or certify a particular confidence interval, and any interval method would still need its sampling assumptions and quantile convention stated.

If several rows come from one source family, resample families together when the intended independence is at that level. Define the estimand as well: equal family means and row-weighted population means differ when families have different sizes. Time dependence may require blocks or another design rather than an ordinary independent-row bootstrap. Stable row IDs alone do not resolve those dependencies.

The local torch.Generator makes this calculation reproducible without depending on unrelated global draws. A fresh generator seeded identically reproduces the index matrix in the tested environment. NumPy's generator in the paired TensorFlow route is a different random implementation; identical seed numbers do not require identical index matrices across the two libraries. Compare the statistical contract, allowed values and within-implementation replay rather than treating cross-library random bits as a shared oracle.

This resampling holds the fitted prediction vectors fixed. It does not include variation from retraining with a different initialization, batch order or training sample. If the decision concerns the whole fitting procedure, that uncertainty needs a broader experimental design. If test results are used to select another architecture, threshold or stopping rule, the test has become selection information. An unchanged filename cannot restore an untouched assessment boundary.

Finally, a negative point estimate is not a complete release decision. Record effect size, uncertainty, assessment coverage, severe failures and operating costs under their own evidence. The tiny fixture teaches pairing and resampling mechanics while making its limited independent sample size explicit.

## Exercise 1: Align a new pair of models

The question is: Use truth x=1, y=2 with model A predictions x=1, y=4 and model B predictions y=2, x=0 in different dictionary order.

Sorting identities before pairing keeps each difference on one record.

```python
truth2 = {"x": 1.0, "y": 2.0}
model_a = {"x": 1.0, "y": 4.0}
model_b = {"y": 2.0, "x": 0.0}
keys = sorted(truth2)
paired = torch.tensor(
    [(model_a[k] - truth2[k]) ** 2 - (model_b[k] - truth2[k]) ** 2 for k in keys],
    dtype=torch.float64,
)
assert paired.tolist() == [-1.0, 4.0]
```

**Expected:** paired squared-loss differences A minus B: [-1, 4].

**Verify:** In a fresh process, the exercise checks confirm `paired.tolist() == [-1.0, 4.0]`.

## Exercise 2: Interpret the new mean contrast

The question is: Average the two paired differences and state which model the fixture favors.

A positive mean of A minus B losses means A has the larger loss.

```python
assert paired.mean().item() == 1.5
```

**Expected:** mean 1.5, favoring model B on this loss.

**Verify:** In a fresh process, the exercise checks confirm `paired.mean().item() == 1.5`.

## Exercise 3: Bound the new bootstrap means

The question is: Draw 500 two-index bootstrap samples with Generator seed 11 and inspect the possible means.

With two differences, a resample of size two can only average two copies of one value or one of each.

```python
gen = torch.Generator().manual_seed(11)
draws = torch.randint(0, 2, (500, 2), generator=gen)
boot = paired[draws].mean(1)
assert set(boot.tolist()) <= {-1.0, 1.5, 4.0} and boot.min() >= -1 and boot.max() <= 4
```

**Expected:** every mean is -1, 1.5 or 4.

**Verify:** In a fresh process, the exercise checks confirm `set(boot.tolist()) <= {-1.0, 1.5, 4.0}`; `boot.min() >= -1` and `boot.max() <= 4`.

## Exercise 4: Replay the local random stream

The question is: Create a new Generator with seed 7 and compare the index matrix.

Reusing an advanced generator would not replay the beginning. The generator state is part of the reproducibility record.

```python
again = torch.randint(0, 3, (1000, 3), generator=torch.Generator().manual_seed(7))
assert torch.equal(indices, again)
```

**Expected:** exact match.

**Verify:** In a fresh process, the exercise checks confirm `torch.equal(indices, again)`.

## Exercise 5: Reject missing assessment identities

The question is: Remove c from one prediction dictionary and check the keyset.

Silently inner-joining would drop a missing prediction and change the evaluation population. Define a failure policy instead of removing hard cases.

```python
missing = {key: value for key, value in b.items() if key != "c"}
assert set(missing) != set(truth)
```

**Expected:** mismatch detected before comparison.

**Verify:** In a fresh process, the exercise checks confirm `set(missing) != set(truth)`.

## Exercise 6: Preserve a final-test boundary

The question is: Record configuration choice on validation and assessment on test; flag a test-driven new choice.

The boundary depends on the actual decision sequence, not on the dataset filename. After test-driven changes, new untouched evidence is needed.

```python
ledger = [("choose", "validation"), ("assess", "test")]
assert all(partition == "validation" for action, partition in ledger if action == "choose")
assert ("choose", "test")[1] != "validation"
```

**Expected:** test selection violates the declared boundary.

**Verify:** In a fresh process, the exercise checks confirm `all((partition == 'validation' for action, partition in ledger if action == 'choose'))` and `('choose', 'test')[1] != 'validation'`.

