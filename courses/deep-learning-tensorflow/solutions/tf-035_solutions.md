# tf-035: explanatory solutions

Open these answers for Comparing models with uncertainty after your own attempt at Example A, Align by identity, or after an explicit reveal. Each answer reuses the guide's literal inputs, so a mismatch points to one step. The companion script runs the assertions; this page explains why they test Paired difference, Bootstrap, Selection leakage. After matching exercise 6, Keep selection and final evaluation separate, invent a new input without looking here.

## Mechanism review

A model comparison should preserve pairing: both models predict the same held-out identities. Subtract each record loss before summarizing so shared difficulty remains represented. Resampling the pairs approximates variability under a stated sampling assumption; resampling each model separately discards their dependence. A fixed seed makes the teaching calculation reproducible, but it does not make a small sample representative. If related observations share a group, resample groups rather than pretending every row is independent. Model selection belongs on validation data. Opening the final test and then changing configuration consumes it as a selection source, even if the resulting number is still called test error.

**Paired difference:** Loss A minus loss B for the same observation.

**Bootstrap:** Resampling observed units with replacement.

**Selection leakage:** Using assessment outcomes to choose the evaluated configuration.

## Reading the implementation

Align dictionaries by stable IDs and verify equal key sets. Compute per-ID squared errors for each model and their difference. np.random.default_rng provides a local seeded generator. Sample integer indices with replacement and apply the same indices to the paired difference vector. A percentile interval describes this resampling calculation under its assumptions, not a universal confidence guarantee.

## Exercise 1: Align a fourth record

The question is: Use truth a=0, b=1, c=2, d=4, model A predictions d 5, a 0, b 2, c 2 and model B predictions b 1, d 4, c 3, a 1. Compute paired squared-error differences by ID.

Each model wins on two records, so the paired mean is exactly zero. Sorting the shared IDs pairs every prediction with its own truth regardless of dictionary insertion order.

```python
truth4 = {"a": 0.0, "b": 1.0, "c": 2.0, "d": 4.0}
a4 = {"d": 5.0, "a": 0.0, "b": 2.0, "c": 2.0}
b4 = {"b": 1.0, "d": 4.0, "c": 3.0, "a": 1.0}
diff4 = np.array([(a4[i] - truth4[i]) ** 2 - (b4[i] - truth4[i]) ** 2 for i in sorted(truth4)])
np.testing.assert_array_equal(diff4, [-1, 1, -1, 1])
assert diff4.mean() == 0
```

**Expected:** paired differences [-1, 1, -1, 1]; mean 0, so neither model has lower MSE on this fixture.

**Verify:** In a fresh process, the exercise checks confirm `diff4` equals `[-1, 1, -1, 1]` and `diff4.mean() == 0`.

## Exercise 2: Expose positional pairing

The question is: Pair the original truth, model A and model B dictionaries by insertion order instead of ID and compare with the identity-aligned differences.

Model B was stored in the order c, a, b, so positional pairing scores its prediction for c against the truth for a. The code runs without error and produces plausible numbers, which is why identity alignment must be checked rather than assumed.

```python
positional = np.array(
    [(pa - t) ** 2 - (pb - t) ** 2 for t, pa, pb in zip(truth.values(), a.values(), b.values())]
)
np.testing.assert_array_equal(positional, [-9, 1, 0])
assert not np.array_equal(positional, diff)
```

**Expected:** positional differences [-9, 1, 0] instead of [-1, 0, -1].

**Verify:** In a fresh process, the exercise checks confirm `positional` equals `[-9, 1, 0]` and `not np.array_equal(positional, diff)`.

## Exercise 3: Resample paired units

The question is: Draw 1000 bootstrap index rows with seed 7 and average each selected difference vector.

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

**Expected:** 1000 finite estimates within [-1, 0].

**Verify:** In a fresh process, the exercise checks confirm `estimates.shape == (1000,)`; `np.isfinite(estimates).all()`; `estimates.min() >= -1` and `estimates.max() <= 0`.

## Exercise 4: Reproduce the resampling

The question is: Repeat with a fresh seed 7 generator and compare the entire estimate vector.

The seed makes local execution repeatable. It does not address biased sampling, dependent observations or a metric chosen after seeing the results.

```python
again = np.random.default_rng(7).integers(0, 3, size=(1000, 3))
np.testing.assert_array_equal(diff[again].mean(1), estimates)
```

**Expected:** exact same estimates.

**Verify:** In a fresh process, the exercise checks confirm `diff[again].mean(1)` equals `estimates`.

## Exercise 5: Refuse mismatched IDs

The question is: Remove prediction c from one model and check alignment before computing differences.

An inner join would silently evaluate only the overlapping records. Missing predictions should be accounted for under an explicit failure policy rather than dropped.

```python
missing = {k: v for k, v in b.items() if k != "c"}
assert set(missing) != set(truth)
```

**Expected:** key-set mismatch detected.

**Verify:** In a fresh process, the exercise checks confirm `set(missing) != set(truth)`.

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

**Verify:** In a fresh process, the exercise checks confirm `all((row['partition'] == 'validation' for row in ledger if row['action'] == 'choose'))` and `bad['partition'] != 'validation'`.

## Review after comparison

Change one fixture value in exercise 4, Reproduce the resampling, and predict the new result before running it. Keep the failing version of exercise 5, Refuse mismatched IDs, next to its repair. A missing framework is an environment record, not a failed assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
