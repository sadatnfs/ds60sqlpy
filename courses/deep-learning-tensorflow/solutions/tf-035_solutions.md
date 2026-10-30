# tf-035: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A model comparison should preserve pairing: both models predict the same held-out identities. Subtract each record loss before summarizing so shared difficulty remains represented. Resampling the pairs approximates variability under a stated sampling assumption; resampling each model separately discards their dependence. A fixed seed makes the teaching calculation reproducible, but it does not make a small sample representative. If related observations share a group, resample groups rather than pretending every row is independent. Model selection belongs on validation data. Opening the final test and then changing configuration consumes it as a selection source, even if the resulting number is still called test error.

**Paired difference:** LossA minus lossB for the same observation.

**Bootstrap:** Resampling observed units with replacement.

**Selection leakage:** Using assessment outcomes to choose the evaluated configuration.

## Reading the implementation

Align dictionaries by stable IDs and verify equal key sets. Compute per-ID squared errors for each model and their difference. np.random.default_rng provides a local seeded generator. Sample integer indices with replacement and apply the same indices to the paired difference vector. A percentile interval describes this resampling calculation under its assumptions, not a universal confidence guarantee.

## Exercise 1: Align by identity

The question is: Use trutha0,b1,c2 and two prediction dictionaries with different insertion order.

Dictionary insertion order is not an alignment contract. Joining by IDs keeps each difference attached to the same target record.

```python
truth = {"a": 0.0, "b": 1.0, "c": 2.0}
a = {"a": 0.0, "b": 2.0, "c": 2.0}
b = {"c": 3.0, "a": 1.0, "b": 2.0}
ids = sorted(truth)
diff = np.array([(a[i] - truth[i]) ** 2 - (b[i] - truth[i]) ** 2 for i in ids])
np.testing.assert_array_equal(diff, [-1, 0, -1])
```

**Expected:** paired differences[-1,0,-1].

**Verify:** Compare the computed values or written argument with paired differences[-1,0,-1].

## Exercise 2: Calculate the mean difference

The question is: Average the three paired loss differences and interpret its sign.

The sign depends on the declared subtraction order. A negative A-minus-B loss difference favors A for this metric and sample only.

```python
np.testing.assert_allclose(diff.mean(), -2 / 3, atol=1e-12, rtol=0)
```

**Expected:** mean-2/3; modelA has lower MSE on this fixture.

**Verify:** Compare the computed values or written argument with mean-2/3; modelA has lower MSE on this fixture.

## Exercise 3: Resample paired units

The question is: Draw1000 bootstrap index rows with seed7 and average each selected difference vector.

Sampling one difference vector automatically preserves pairing. The attainable bounds are known from the fixture, so they independently check the implementation.

```python
rng = np.random.default_rng(7)
indices = rng.integers(0, len(diff), size=(1000, len(diff)))
estimates = diff[indices].mean(1)
assert (
    estimates.shape == (1000,)
    and np.isfinite(estimates).all()
    and estimates.min() >= -1
    and estimates.max() <= 0
)
```

**Expected:** 1000 finite estimates within[-1,0].

**Verify:** Compare the computed values or written argument with 1000 finite estimates within[-1,0].

## Exercise 4: Reproduce the resampling

The question is: Repeat with a fresh seed7 generator and compare the entire estimate vector.

The seed makes local execution repeatable. It does not address biased sampling, dependent observations or a metric chosen after seeing the results.

```python
again = np.random.default_rng(7).integers(0, 3, size=(1000, 3))
np.testing.assert_array_equal(diff[again].mean(1), estimates)
```

**Expected:** exact same estimates.

**Verify:** Compare the computed values or written argument with exact same estimates.

## Exercise 5: Refuse mismatched IDs

The question is: Remove predictionc from one model and check alignment before computing differences.

An inner join would silently evaluate only the overlapping records. Missing predictions should be accounted for under an explicit failure policy rather than dropped.

```python
missing = {k: v for k, v in b.items() if k != "c"}
assert set(missing) != set(truth)
```

**Expected:** key-set mismatch detected.

**Verify:** Compare the computed values or written argument with key-set mismatch detected.

## Exercise 6: Keep selection and final evaluation separate

The question is: Record configuration choice on validation and a single frozen-test assessment; reject a later test-driven retune.

The audit concerns information use, not filenames. Once the final test influences a new choice, a new untouched assessment is needed for a fresh final claim.

```python
ledger = [
    {"action": "choose", "partition": "validation"},
    {"action": "assess", "partition": "test"},
]
assert all(row["partition"] == "validation" for row in ledger if row["action"] == "choose")
bad = {"action": "choose", "partition": "test"}
assert bad["partition"] != "validation"
```

**Expected:** selection partition validation; final-test tuning prohibited.

**Verify:** Compare the computed values or written argument with selection partition validation; final-test tuning prohibited.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
