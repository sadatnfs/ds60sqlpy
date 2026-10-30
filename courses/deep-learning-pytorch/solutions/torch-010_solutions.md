# torch-010: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A Dataset is an interface for retrieving observations, not a guarantee that the experiment is leakage-free. Related records need a shared split unit, such as account or source document. Subset selects indices from a dataset, but choosing those indices is a statistical-design responsibility. Fit preprocessing only on the training subset and freeze it before transforming validation or holdout records. A validation-only extreme should not change a training mean.

This lesson implements a tiny map-style Dataset over eight literal account records. Each item includes identity, group and numeric value so split and pairing checks remain possible. The dataset is deterministic and contains no file or network reads. Grouped splitting, training-only normalization and an explicit held-out perturbation distinguish data-interface correctness from evaluation validity.

**Map-style Dataset:** A dataset providing indexed item retrieval and a length.

**Subset:** An index selection over an existing dataset.

**Split unit:** The entity assigned wholly to one partition.

**Training-only fit:** Estimating preprocessing state without assessment inputs.

## Reading the implementation

Subclass Dataset and implement __len__ and__getitem__. A Subset stores a sequence of indices and delegates item retrieval to the original dataset. Build training indices from whole account groups before calculating any statistic. Stack only selected training values to estimate the mean. Use sets of group IDs to check isolation; disjoint row indices alone are insufficient.

## Trace selection, fitted state and delegated access

The eight literal records form four account groups. Training selects original indices 0, 1, 2, 3 fromA and B; assessment selects 4, 5, 6, 7 fromC and D. The two Subset objects do not copy or redefine those records. They map their local index into the original dataset. Thus assessment[0] returns original identity 4, accountC, value 20. A local batch position zero is not a replacement for the source identity.

| Population | Original identities | Values | Mean |
| --- | --- | --- | --- |
| Training accountsA, B | 0, 1, 2, 3 | 1, 3, 5, 7 | 4 |
| Assessment accountsC, D | 4, 5, 6, 7 | 20, 22, 30, 32 | 26 |
| All records | 0..7 | All eight values | 15 |

Each item returns a scalar tensor plus identity and group metadata. Stacking the four selected training scalars creates a tensor shaped(4, ), whose mean is the fitted normalization state. Applying that scalar to four assessment values yields[16, 18, 26, 28]. Those transformed assessment values do not have mean zero, and they should not be forced to. Their nonzero mean is information about the assessment population relative to the training baseline.

The held-out perturbation is a direct test of the information boundary. Replacing only the final assessment value 32 with 3200 leaves the training values and mean four unchanged. The global mean changes from 15 to 411 because the total becomes 3288 over eight records. A preprocessing path whose fitted training mean changes under this perturbation has consumed assessment information, even if no target label was read.

Alternating row indices produces superficially balanced four-row sets but puts one row from every account on each side. Row-ID intersections are empty while the account-group intersection isA, B, C, D. If the claim concerns new accounts, this is a failure before any neural layer is built. A stronger optimizer or more epochs cannot undo that information crossing.

Dataset is an access interface, not an isolation or immutability guarantee. Subset delegates to the underlying dataset, so later mutation of that object's values can change what a subset returns. A retrieved scalar tensor may also share storage with its source. Use out-of-place transformations or an explicit ownership boundary when mutation is intended, and freeze the fitted preprocessing state independently of mutable dataset access. [PyTorch 2.9 Dataset, Subset and data loading](https://docs.pytorch.org/docs/2.9/data.html).

Keeping identity and group fields does not require feeding them into the model as features. They support split checks, duplicate detection, pairing and error analysis. An account identifier used as an embedding feature would require a separate justification about availability and the meaning of unseen account IDs; it should not enter the model accidentally merely because it travels through the loader.

Finally, four assessment rows here represent only two held-out account families. The fixture is too small and too structured to establish reliable population performance. Its useful evidence is that the access interface, group isolation and preprocessing boundary behave as declared. Later evaluation should preserve the relevant independent units when estimating uncertainty rather than treating correlated rows as additional independent accounts.

## Exercise 1: Inspect a literal Dataset

The question is: Create eight records with groups A, A, B, B, C, C, D, D and values 1, 3, 5, 7, 20, 22, 30, 32.

The dataset returns metadata beside the tensor. A value-only interface would make it harder to audit group membership and record conservation.

```python
dataset = Accounts()
assert len(dataset) == 8
identity, group, value = dataset[0]
assert identity == 0 and group == "A" and value.item() == 1
```

**Expected:** length 8; item 0 has ID 0, group A, value 1.

**Verify:** Compare the computed values or written argument with length 8; item 0 has ID 0, group A, value 1.

## Exercise 2: Select whole groups

The question is: Train on accounts A, B and holdout C, D using Subset.

The grouping policy precedes the subset construction. Subset itself would happily accept a leaking row-level split.

```python
train_ids = [i for i in range(len(dataset)) if dataset[i][1] in {"A", "B"}]
test_ids = [i for i in range(len(dataset)) if i not in train_ids]
train = torch.utils.data.Subset(dataset, train_ids)
test = torch.utils.data.Subset(dataset, test_ids)
assert len(train) == len(test) == 4 and not {row[1] for row in train} & {row[1] for row in test}
```

**Expected:** four records each; group intersection empty.

**Verify:** Compare the computed values or written argument with four records each; group intersection empty.

## Exercise 3: Fit only training values

The question is: Calculate the mean from the four training tensors.

The statistic is fitted state. Even without labels, it would leak assessment information if computed over the entire dataset.

```python
mean = torch.stack([row[2] for row in train]).mean()
assert mean.item() == 4
```

**Expected:** mean 4.

**Verify:** Compare the computed values or written argument with mean 4.

## Exercise 4: Perturb only assessment values

The question is: Replace the final held-out value with 3200 in a copied dataset and recompute the training mean.

This controlled perturbation directly tests the information boundary. A correct implementation is invariant to held-out-only changes during fitting.

```python
changed = Accounts()
changed.values = changed.values.clone()
changed.values[-1] = 3200
new_mean = torch.stack([changed[i][2] for i in train_ids]).mean()
assert new_mean.item() == 4 and changed.values.mean() != dataset.values.mean()
```

**Expected:** training mean unchanged 4; global mean changes.

**Verify:** Compare the computed values or written argument with training mean unchanged 4; global mean changes.

## Exercise 5: Expose row-level leakage

The question is: Assign alternating indices to train/test and inspect group intersection.

Balanced row counts can hide complete group leakage. The independent entity identities determine whether assessment is genuinely unseen.

```python
left = {dataset[i][1] for i in range(0, 8, 2)}
right = {dataset[i][1] for i in range(1, 8, 2)}
assert left & right == set("ABCD")
```

**Expected:** allA, B, C, D cross.

**Verify:** Compare the computed values or written argument with allA, B, C, D cross.

## Exercise 6: Apply the frozen transform

The question is: Center held-out values with the training mean.

Validation values need not have zero mean after a training-fitted transform. Re-centering them independently would use new fitted state and conceal distribution shift.

```python
centered = torch.stack([row[2] for row in test]) - mean
torch.testing.assert_close(
    centered, torch.tensor([16.0, 18.0, 26.0, 28.0], dtype=torch.float64), atol=0, rtol=0
)
```

**Expected:** 16, 18, 26, 28.

**Verify:** Compare the computed values or written argument with 16, 18, 26, 28.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
