# tf-010: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A split defines what is unseen. If two rows belong to one account, putting one in training and one in validation exposes part of the validation entity during fitting. Grouped splitting assigns the entity once, then carries all of its rows together. Preprocessing is also fitting: a mean inferred from validation values has already consumed validation information even if no label was used. Store the training statistic and apply it unchanged to validation. This lesson uses literal account records so every crossing can be enumerated. The tiny fixture teaches isolation and does not establish that an account model will generalize to a future deployment.

**Split unit:** Entity assigned wholly to one partition.

**Leakage:** Assessment information influencing fitting or selection.

**Fit statistic:** A quantity estimated from training inputs and then frozen.

## Reading the implementation

Use a mapping from account to split before selecting values. Set intersection tests group isolation. NumPy mean reduces only the selected training values, and subtraction then broadcasts the scalar to both partitions. A validation perturbation should change transformed validation values while leaving the saved fit statistic unchanged. Hash canonical record IDs only after freezing the selection, and never refit merely because a held-out point looks extreme.

## Exercise 1: Partition a second account fixture

The question is: Use groups E, E, F, F, G, G, H, H with values 2, 4, 6, 8, 10, 12, 40, 44; train on E, F and G, then center the held-out rows with the training mean.

Three training accounts now contribute six rows, and the held-out account is centered with a statistic it did not influence. Its centered values are far from zero, which is information about the new account rather than an error.

```python
groups2 = np.array(list("EEFFGGHH"))
x2 = np.array([2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 40.0, 44.0])
train2 = np.isin(groups2, ["E", "F", "G"])
mean2 = x2[train2].mean()
assert mean2 == 7 and set(groups2[~train2]) == {"H"}
np.testing.assert_array_equal(x2[~train2] - mean2, [33.0, 37.0])
```

**Expected:** train mean 7; validation group H; centered values 33 and 37.

**Verify:** In a fresh process, the exercise checks confirm `mean2 == 7`; `set(groups2[~train2]) == {'H'}` and `x2[~train2] - mean2` equals `[33.0, 37.0]`.

## Exercise 2: Predict the effect of a training outlier

The question is: Change the first training value from 2 to 200. Predict the new training mean and the centered validation values before running the check.

Changing a validation value left the training mean alone in Example B; changing a training value moves the frozen statistic and every transformed validation row with it. A single training outlier can therefore alter all downstream evaluation inputs.

```python
outlier = x2.copy()
outlier[0] = 200
shifted = outlier[train2].mean()
assert shifted == 40
np.testing.assert_array_equal(outlier[~train2] - shifted, [0.0, 4.0])
```

**Expected:** training mean 40; centered H values 0 and 4.

**Verify:** In a fresh process, the exercise checks confirm `shifted == 40` and `outlier[~train2] - shifted` equals `[0.0, 4.0]`.

## Exercise 3: Find crossing groups

The question is: Assign alternating rows to train and validation and inspect intersections.

A row split can look balanced while violating the intended unit. Set intersection exposes the repeated accounts; disjoint row indices alone do not prove disjoint entities.

```python
wrong = np.arange(8) % 2 == 0
assert set(groups[wrong]) & set(groups[~wrong]) == set("ABCD")
```

**Expected:** A, B, C, D all cross the split.

**Verify:** In a fresh process, the exercise checks confirm `set(groups[wrong]) & set(groups[~wrong]) == set('ABCD')`.

## Exercise 4: Apply frozen centering

The question is: Center both partitions with training mean 4 and compare validation centered values.

Only the training values are guaranteed to have centered mean zero. Forcing validation to mean zero would estimate a new statistic and erase a potentially meaningful distribution shift.

```python
np.testing.assert_array_equal(x[valid] - mean, [16, 18, 26, 28])
assert (x[train] - mean).mean() == 0
```

**Expected:** validation values 16, 18, 26, 28.

**Verify:** In a fresh process, the exercise checks confirm `x[valid] - mean` equals `[16, 18, 26, 28]` and `(x[train] - mean).mean() == 0`.

## Exercise 5: Freeze selection identity

The question is: Hash sorted training IDs before and after calculating validation errors.

The hash is a compact identity receipt, not proof of good split design. It can reveal accidental mutation after evaluation. The original IDs must still be available for review.

```python
import hashlib, json

ids = ["a1", "a2", "b1", "b2"]
frozen = json.dumps(ids).encode()
digest = hashlib.sha256(frozen).hexdigest()
validation_error = float(np.mean((x[valid] - mean) ** 2))
assert validation_error > 0 and hashlib.sha256(json.dumps(ids).encode()).hexdigest() == digest
```

**Expected:** The selection hash is unchanged.

**Verify:** In a fresh process, the exercise checks confirm `validation_error > 0` and `hashlib.sha256(json.dumps(ids).encode()).hexdigest() == digest`.

## Exercise 6: Transfer to unseen accounts

The question is: Add account E with value 1000 only to evaluation; specify whether its normalization can update the training mean.

A deployment input is transformed using the fitted state. Updating the mean online is a separate algorithm requiring an explicit policy and new evaluation; it is not a harmless formatting adjustment.

```python
new_value = 1000 - mean
assert new_value == 996 and mean == 4
```

**Expected:** transformed value 996; fitted mean remains 4.

**Verify:** In a fresh process, the exercise checks confirm `new_value == 996` and `mean == 4`.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
