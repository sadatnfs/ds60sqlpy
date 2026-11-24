# torch-010: explanatory solutions

Open these answers only after attempting Datasets, held-out families and leakage controls yourself. They reuse the guide's literal inputs, starting from Example A, Inspect a literal Dataset, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Map-style Dataset, Subset, Split unit. After a pass, choose a new input for exercise 6, Apply the frozen transform, without looking.

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

The eight literal records form four account groups. Training selects original indices 0, 1, 2, 3 from A and B; assessment selects 4, 5, 6, 7 from C and D. The two Subset objects do not copy or redefine those records. They map their local index into the original dataset. Thus `assessment[0]` returns original identity 4, account C, value 20. A local batch position zero is not a replacement for the source identity.

| Population | Original identities | Values | Mean |
| --- | --- | --- | --- |
| Training accounts A, B | 0, 1, 2, 3 | 1, 3, 5, 7 | 4 |
| Assessment accounts C, D | 4, 5, 6, 7 | 20, 22, 30, 32 | 26 |
| All records | 0..7 | All eight values | 15 |

Each item returns a scalar tensor plus identity and group metadata. Stacking the four selected training scalars creates a tensor shaped (4, ), whose mean is the fitted normalization state. Applying that scalar to four assessment values yields [16, 18, 26, 28]. Those transformed assessment values do not have mean zero, and they should not be forced to. Their nonzero mean is information about the assessment population relative to the training baseline.

The held-out perturbation is a direct test of the information boundary. Replacing only the final assessment value 32 with 3200 leaves the training values and mean four unchanged. The global mean changes from 15 to 411 because the total becomes 3288 over eight records. A preprocessing path whose fitted training mean changes under this perturbation has consumed assessment information, even if no target label was read.

Alternating row indices produces superficially balanced four-row sets but puts one row from every account on each side. Row-ID intersections are empty while the account-group intersection is A, B, C, D. If the claim concerns new accounts, this is a failure before any neural layer is built. A stronger optimizer or more epochs cannot undo that information crossing.

Dataset is an access interface, not an isolation or immutability guarantee. Subset delegates to the underlying dataset, so later mutation of that object's values can change what a subset returns. A retrieved scalar tensor may also share storage with its source. Use out-of-place transformations or an explicit ownership boundary when mutation is intended, and freeze the fitted preprocessing state independently of mutable dataset access. [PyTorch 2.9 Dataset, Subset and data loading](https://docs.pytorch.org/docs/2.9/data.html).

Keeping identity and group fields does not require feeding them into the model as features. They support split checks, duplicate detection, pairing and error analysis. An account identifier used as an embedding feature would require a separate justification about availability and the meaning of unseen account IDs; it should not enter the model accidentally merely because it travels through the loader.

Finally, four assessment rows here represent only two held-out account families. The fixture is too small and too structured to establish reliable population performance. Its useful evidence is that the access interface, group isolation and preprocessing boundary behave as declared. Later evaluation should preserve the relevant independent units when estimating uncertainty rather than treating correlated rows as additional independent accounts.

## Exercise 1: Inspect a different record

The question is: Read item 5 of the literal Accounts dataset.

The dataset returns the original index with the group label, so downstream code can audit identities.

```python
record = Accounts()[5]
assert record[0] == 5 and record[1] == "C" and record[2].item() == 22
```

**Expected:** ID 5, group C, value 22.

**Verify:** In a fresh process, the exercise checks confirm `record[0] == 5`, `record[1] == 'C'` and `record[2].item() == 22`.

## Exercise 2: Hold out a different pair of groups

The question is: Train on groups A and C and hold out B and D with Subset; check the group sets and the training mean.

The training values are 1, 3, 20 and 22. A different group choice changes the fitted statistic, which is why it must be fitted after the split.

```python
pool = Accounts()
keep = [i for i in range(len(pool)) if pool[i][1] in {"A", "C"}]
rest = [i for i in range(len(pool)) if i not in keep]
fit = torch.utils.data.Subset(pool, keep)
held = torch.utils.data.Subset(pool, rest)
assert {row[1] for row in fit} == {"A", "C"} and not {row[1] for row in fit} & {
    row[1] for row in held
}
assert torch.stack([row[2] for row in fit]).mean().item() == 11.5
```

**Expected:** disjoint group sets; training mean 11.5.

**Verify:** In a fresh process, the exercise checks confirm `{row[1] for row in fit} == {'A', 'C'}`; `not {row[1] for row in fit} & {row[1] for row in held}` and `torch.stack([row[2] for row in fit]).mean().item() == 11.5`.

## Exercise 3: Apply the new frozen transform

The question is: Center the held-out values with the training mean 11.5.

The held-out values 5, 7, 30 and 32 are transformed with the frozen training statistic, never with their own mean.

```python
shifted_values = torch.stack([row[2] for row in held]) - 11.5
torch.testing.assert_close(
    shifted_values, torch.tensor([-6.5, -4.5, 18.5, 20.5], dtype=torch.float64), atol=0, rtol=0
)
```

**Expected:** -6.5, -4.5, 18.5, 20.5.

**Verify:** In a fresh process, the exercise checks confirm `shifted_values` matches `torch.tensor([-6.5, -4.5, 18.5, 20.5], dtype=torch.float64)` exactly.

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

**Verify:** In a fresh process, the exercise checks confirm `new_mean.item() == 4` and `changed.values.mean() != dataset.values.mean()`.

## Exercise 5: Expose row-level leakage

The question is: Assign alternating indices to train/test and inspect group intersection.

Balanced row counts can hide complete group leakage. The independent entity identities determine whether assessment is genuinely unseen.

```python
left = {dataset[i][1] for i in range(0, 8, 2)}
right = {dataset[i][1] for i in range(1, 8, 2)}
assert left & right == set("ABCD")
```

**Expected:** all four account groups A, B, C and D cross the split.

**Verify:** In a fresh process, the exercise checks confirm `left & right == set('ABCD')`.

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

**Verify:** In a fresh process, the exercise checks confirm `centered` matches `torch.tensor([16.0, 18.0, 26.0, 28.0], dtype=torch.float64)` exactly.

## Review after comparison

Repeat exercise 4, Perturb only assessment values, with one changed fixture value and predict the difference before running it. Keep your failing attempt at exercise 5, Expose row-level leakage, beside the repaired result. A missing framework is not a failing assertion. These solutions use only local fixtures.
