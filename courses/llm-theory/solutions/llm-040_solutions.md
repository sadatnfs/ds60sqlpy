# llm-040: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A reliability argument combines a decision rule with evidence and its limits. When comparing systems, preserve question-level pairing and the dependence between paraphrases in the same family. Resampling individual rows can exaggerate the effective sample size when many variants repeat one underlying task. Aggregate or resample by family under a declared policy. Prompt and retrieval tuning belong on validation data; the final holdout is opened after the policy is frozen. Abstention changes coverage, so accuracy among answered questions must be reported beside answered count and total count. A favorable mean is not enough when severe failures violate a required gate.

**Clustered resampling:** Sampling related groups as units rather than individual rows.

**Coverage:** Fraction of questions receiving an answer.

**Reliability argument:** A decision supported by specified tests and bounded assumptions.

## Reading the implementation

Align both systems by question ID, compute per-question loss or correctness differences, then average within family if families are the resampling unit. Use one index draw for the paired family differences. Preserve a decision ledger separating validation choices from final assessment. Calculate coverage=answered/total and selective accuracy=correct_answered/answered, with an explicit empty-answer policy.

## Exercise 1: Group a second fixture

The question is: Use families A, B, B, C with paired differences [2, -1, 0, 1]; compute family means, the row mean and the equal-family mean.

Family B contributes two rows to the row mean but one value to the equal-family mean, so the two targets differ even without duplication.

```python
fam2 = np.array(["A", "B", "B", "C"])
d2 = np.array([2.0, -1.0, 0.0, 1.0])
g2 = np.array([d2[fam2 == f].mean() for f in ["A", "B", "C"]])
np.testing.assert_array_equal(g2, [2, -0.5, 1])
assert d2.mean() == 0.5
np.testing.assert_allclose(g2.mean(), 5 / 6, atol=1e-12, rtol=0)
```

**Expected:** family means A 2, B -0.5, C 1; row mean 0.5; equal-family mean 5/6.

**Verify:** In a fresh process, the exercise checks confirm `g2` equals `[2, -0.5, 1]`; `d2.mean() == 0.5` and `g2.mean()` matches `5 / 6` within 1e-12.

## Exercise 2: Predict bootstrap support

The question is: Draw 2000 resamples of three family means with replacement using seed 3 and predict the range and number of distinct estimates.

Each estimate averages three of the observed family means, so it cannot leave their range, and there are only 10 multisets of three draws from three values. More draws sample this small distribution more densely without adding families.

```python
idx = np.random.default_rng(3).integers(0, 3, size=(2000, 3))
est = g2[idx].mean(1)
assert est.min() >= -0.5 and est.max() <= 2
assert len(np.unique(np.round(est, 12))) <= 10
```

**Expected:** every estimate lies in [-0.5, 2]; at most 10 distinct means occur.

**Verify:** In a fresh process, the exercise checks confirm `est.min() >= -0.5`; `est.max() <= 2` and `len(np.unique(np.round(est, 12))) <= 10`.

## Exercise 3: Expose row-weighting dependence

The question is: Repeat q1 ten times and compare row mean with unchanged family means.

Duplicating a variant can alter a row-weighted conclusion without adding new task families. The test demonstrates why the unit must be chosen before scoring.

```python
repeated = np.concatenate([diff, [-1.0] * 10])
assert repeated.mean() != diff.mean() and grouped.mean() == 0
```

**Expected:** row mean changes; family mean remains 0.

**Verify:** In a fresh process, the exercise checks confirm `repeated.mean() != diff.mean()` and `grouped.mean() == 0`.

## Exercise 4: Report selective accuracy

The question is: Of 4 questions, answer 2 correctly and abstain on 2. Compute coverage and answered accuracy.

Perfect accuracy among answered questions can coexist with limited usefulness. Coverage makes the abstention tradeoff visible.

```python
total, answered, correct = 4, 2, 2
assert answered / total == 0.5 and correct / answered == 1 and correct == 2
```

**Expected:** coverage 0.5; answered accuracy 1; total correct answers 2.

**Verify:** In a fresh process, the exercise checks confirm `answered / total == 0.5`, `correct / answered == 1` and `correct == 2`.

## Exercise 5: Audit decision chronology

The question is: Record prompt selection on validation followed by final-test assessment; flag a test-driven prompt change.

Information use determines the boundary. Renaming a file or calling a repeated assessment a confirmation does not restore an untouched holdout.

```python
ledger = [("select_prompt", "validation"), ("assess", "test")]
assert all(part == "validation" for action, part in ledger if action == "select_prompt")
forbidden = ("select_prompt", "test")
assert forbidden[1] != "validation"
```

**Expected:** test-driven selection is invalid for a fresh final claim.

**Verify:** In a fresh process, the exercise checks confirm `all((part == 'validation' for action, part in ledger if action == 'select_prompt'))` and `forbidden[1] != 'validation'`.

## Exercise 6: Combine gates with uncertainty

The question is: Require no severe failures and adequate family coverage; evaluate a report with one severe failure.

The decision reflects a predeclared constraint. A mean difference and a bootstrap summary provide evidence but do not replace a required failure-severity gate.

```python
gates = {"severe_failures": 1, "tested_families": 2, "minimum_families": 2}
go = gates["severe_failures"] == 0 and gates["tested_families"] >= gates["minimum_families"]
assert not go
```

**Expected:** decision no-go regardless of favorable average.

**Verify:** In a fresh process, the exercise checks confirm `not go`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
