# tf-010: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A split defines what is unseen. If two rows belong to one account, putting one in training and one in validation exposes part of the validation entity during fitting. Grouped splitting assigns the entity once, then carries all of its rows together. Preprocessing is also fitting: a mean inferred from validation values has already consumed validation information even if no label was used. Store the training statistic and apply it unchanged to validation. This lesson uses literal account records so every crossing can be enumerated. The tiny fixture teaches isolation and does not establish that an account model will generalize to a future deployment.

**Split unit:** Entity assigned wholly to one partition.

**Leakage:** Assessment information influencing fitting or selection.

**Fit statistic:** A quantity estimated from training inputs and then frozen.

## Reading the implementation

Use a mapping from account to split before selecting values. Set intersection tests group isolation. NumPy mean reduces only the selected training values, and subtraction then broadcasts the scalar to both partitions. A validation perturbation should change transformed validation values while leaving the saved fit statistic unchanged. Hash canonical record IDs only after freezing the selection, and never refit merely because a held-out point looks extreme.

## Exercise 1: Partition accounts

The question is: Use account IDs A,A,B,B,C,C,D,D with values1,3,5,7,20,22,30,32; train on A,B.

The boolean mask has one position per record. Its values come from group identity, not a target-dependent ranking. Training has four values and validation has four, but equal counts are incidental to the group-isolation contract.

```python
groups = np.array(list("AABBCCDD"))
x = np.array([1.0, 3.0, 5.0, 7.0, 20.0, 22.0, 30.0, 32.0])
train = np.isin(groups, ["A", "B"])
valid = ~train
mean = x[train].mean()
assert mean == 4 and set(groups[valid]) == {"C", "D"}
```

**Expected:** train mean4 and validation IDs C,D.

**Verify:** Compare the computed values or written argument with train mean4 and validation IDs C,D.

## Exercise 2: Expose global fitting

The question is: Change the last validation value to3200 and compare train-only and global means.

A perturbation restricted to validation cannot influence a training-only mean. This controlled counterexample detects leakage more directly than inspecting the name of a preprocessing object.

```python
changed = x.copy()
changed[-1] = 3200
assert changed[train].mean() == mean
assert changed.mean() != x.mean()
```

**Expected:** training mean stays4; global mean changes.

**Verify:** Compare the computed values or written argument with training mean stays4; global mean changes.

## Exercise 3: Find crossing groups

The question is: Assign alternating rows to train and validation and inspect intersections.

A row split can look balanced while violating the intended unit. Set intersection exposes the repeated accounts; disjoint row indices alone do not prove disjoint entities.

```python
wrong = np.arange(8) % 2 == 0
assert set(groups[wrong]) & set(groups[~wrong]) == set("ABCD")
```

**Expected:** A,B,C,D all cross the split.

**Verify:** Compare the computed values or written argument with A,B,C,D all cross the split.

## Exercise 4: Apply frozen centering

The question is: Center both partitions with training mean4 and compare validation centered values.

Only the training values are guaranteed to have centered mean zero. Forcing validation to mean zero would estimate a new statistic and erase a potentially meaningful distribution shift.

```python
np.testing.assert_array_equal(x[valid] - mean, [16, 18, 26, 28])
assert (x[train] - mean).mean() == 0
```

**Expected:** validation values16,18,26,28.

**Verify:** Compare the computed values or written argument with validation values16,18,26,28.

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

**Verify:** Compare the computed values or written argument with The selection hash is unchanged.

## Exercise 6: Transfer to unseen accounts

The question is: Add account E with value1000 only to evaluation; specify whether its normalization can update the training mean.

A deployment input is transformed using the fitted state. Updating the mean online is a separate algorithm requiring an explicit policy and new evaluation; it is not a harmless formatting adjustment.

```python
new_value = 1000 - mean
assert new_value == 996 and mean == 4
```

**Expected:** transformed value996; fitted mean remains4.

**Verify:** Compare the computed values or written argument with transformed value996; fitted mean remains4.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
