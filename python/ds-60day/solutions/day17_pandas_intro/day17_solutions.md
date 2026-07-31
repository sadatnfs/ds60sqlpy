# Day 17 — Solutions: Pandas Intro (Series, DataFrame, Index)

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**labeled tabular data, row grain, indexes, selection, and vectorized columns**.

A Series is a one-dimensional labeled array; a DataFrame is a table of
labeled columns sharing an index. Before manipulating a DataFrame,
state its **row grain**—what one row represents—and what makes a row
unique. Column names carry variable meaning; the index carries row
labels, which may or may not be a business key.

`loc` selects by labels and boolean masks; `iloc` selects by integer
positions. Pandas aligns many operations by index labels rather than
blindly by current row position. Prefer vectorized column operations
and explicit `.loc` assignment. Inspect shape, dtypes, missingness, and
a small sample before trusting a calculation.

### Vocabulary used in the worked answers

- **Series:** a one-dimensional array with an index and optional name.
- **DataFrame:** a two-dimensional collection of aligned labeled columns.
- **index:** the labels identifying rows for selection and alignment.
- **row grain:** the real-world meaning of one row.
- **boolean mask:** a True/False Series used to select matching rows.
- **vectorized operation:** a column/array operation applied without an explicit Python row loop.

### Reference pattern 1 — Build and inspect a tiny labeled table

Use constructed data so the example is fully offline.

```python
import pandas as pd

sales = pd.DataFrame({
    "order_id": [101, 102, 103],
    "region": ["west", "east", "west"],
    "amount": [20.0, 35.0, 15.0],
})
(sales.shape, sales.dtypes.astype(str).to_dict(), sales["order_id"].is_unique)
```

**Expected observation:** `((3, 3), {...}, True)`. The dtype spellings may vary slightly; each row represents one order and `order_id` is unique here.

### Reference pattern 2 — Filter rows and derive a column without a loop

A mask selects west orders; a vectorized expression creates tax.

```python
west = sales.loc[sales["region"].eq("west"), ["order_id", "amount"]]
sales = sales.assign(amount_with_tax=sales["amount"] * 1.08)
(west["order_id"].tolist(), sales["amount_with_tax"].round(2).tolist())
```

**Expected observation:** `([101, 103], [21.6, 37.8, 16.2])`. The original row index is retained in `west`.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Using the lesson DataFrame, select rows where `time == 'Dinner'`, then compute the mean of the selected `tip` values. **Before code:** state the row grain and write the mask separately. **Expected behavior:** the result is one scalar equal to `dinner_rows['tip'].mean()`. **Constraints:** use `.loc` and do not loop. **Verify:** assert every selected row is Dinner and the selection is non-empty before reporting the mean.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies labeled tabular data, row grain, indexes, selection, and vectorized columns.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Method chaining can express a readable pipeline; named intermediate frames are better while learning or debugging each contract.

**Edge case:** Empty selections, duplicate indexes, zero denominators, missing values, and chained assignment need explicit behavior.

**Solution evidence to inspect:** assert every selected row is Dinner and the selection is non-empty before reporting the mean.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Add a Boolean `is_big_party` column that is `True` exactly when `size >= 5`. **Constraints:** use one vectorized comparison and explicit assignment; do not use row-wise `apply`. **Verify:** compare the new column with `df['size'].ge(5)`, inspect both True and False rows, and confirm row count/index are unchanged.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies labeled tabular data, row grain, indexes, selection, and vectorized columns.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Method chaining can express a readable pipeline; named intermediate frames are better while learning or debugging each contract.

**Edge case:** Empty selections, duplicate indexes, zero denominators, missing values, and chained assignment need explicit behavior.

**Solution evidence to inspect:** compare the new column with `df['size'].ge(5)`, inspect both True and False rows, and confirm row count/index are unchanged.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** Create a safe `tip_rate = tip / total_bill`, treating a zero bill as missing rather than infinity, then sort descending by `tip_rate`. **Constraints:** preserve the unsorted source in a separate name and choose where missing rates appear. **Verify:** assert there are no infinite values and that non-missing rates are monotonically decreasing.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies labeled tabular data, row grain, indexes, selection, and vectorized columns.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Method chaining can express a readable pipeline; named intermediate frames are better while learning or debugging each contract.

**Edge case:** Empty selections, duplicate indexes, zero denominators, missing values, and chained assignment need explicit behavior.

**Solution evidence to inspect:** assert there are no infinite values and that non-missing rates are monotonically decreasing.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict the difference between `.loc[labels]` and `.iloc[positions]` after an integer index has been reordered. **Progressive hint:** Labels are not automatically row positions. **Verify:** After reordering integer labels, assert `.loc` returns the requested labels and `.iloc` returns the requested positions; list both resulting indexes.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying labeled tabular data, row grain, indexes, selection, and vectorized columns.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Method chaining can express a readable pipeline; named intermediate frames are better while learning or debugging each contract.

**Edge case:** Empty selections, duplicate indexes, zero denominators, missing values, and chained assignment need explicit behavior.

**Solution evidence to inspect:** After reordering integer labels, assert `.loc` returns the requested labels and `.iloc` returns the requested positions; list both resulting indexes.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace a boolean mask through creation, alignment by index, and row selection. What happens if mask/index labels differ? **Progressive hint:** Pandas aligns many labeled objects by index. **Verify:** Display mask and frame indexes side by side, then assert aligned selection for matching labels and the documented error/reindex policy for mismatches.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the labeled tabular data, row grain, indexes, selection, and vectorized columns model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Method chaining can express a readable pipeline; named intermediate frames are better while learning or debugging each contract.

**Edge case:** Empty selections, duplicate indexes, zero denominators, missing values, and chained assignment need explicit behavior.

**Solution evidence to inspect:** Display mask and frame indexes side by side, then assert aligned selection for matching labels and the documented error/reindex policy for mismatches.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Create a safe `tip_rate` column that yields missing values rather than infinity when `total_bill` is zero. **Progressive hint:** Mask or replace the zero denominator before division. **Verify:** Assert zero bills yield missing rates, positive bills yield the calculated ratio, and the entire column contains no positive/negative infinity.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies labeled tabular data, row grain, indexes, selection, and vectorized columns.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Method chaining can express a readable pipeline; named intermediate frames are better while learning or debugging each contract.

**Edge case:** Empty selections, duplicate indexes, zero denominators, missing values, and chained assignment need explicit behavior.

**Solution evidence to inspect:** Assert zero bills yield missing rates, positive bills yield the calculated ratio, and the entire column contains no positive/negative infinity.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair chained assignment on a filtered DataFrame and explain when to use `.loc` or an explicit `.copy()`. **Progressive hint:** Make ownership and target rows explicit. **Verify:** Turn chained-assignment warnings into explicit `.loc` or `.copy()` ownership; assert the intended frame changes and the unintended frame does not.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in labeled tabular data, row grain, indexes, selection, and vectorized columns.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Method chaining can express a readable pipeline; named intermediate frames are better while learning or debugging each contract.

**Edge case:** Empty selections, duplicate indexes, zero denominators, missing values, and chained assignment need explicit behavior.

**Solution evidence to inspect:** Turn chained-assignment warnings into explicit `.loc` or `.copy()` ownership; assert the intended frame changes and the unintended frame does not.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Compute a statistic for a possibly empty selection and return `None` instead of silently presenting `NaN` as a real result. **Progressive hint:** Check `.empty` before aggregating when absence has business meaning. **Verify:** Test nonempty and empty selections; assert the former returns the statistic and the latter returns `None`, not a value presented as meaningful.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from labeled tabular data, row grain, indexes, selection, and vectorized columns.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Method chaining can express a readable pipeline; named intermediate frames are better while learning or debugging each contract.

**Edge case:** Empty selections, duplicate indexes, zero denominators, missing values, and chained assignment need explicit behavior.

**Solution evidence to inspect:** Test nonempty and empty selections; assert the former returns the statistic and the latter returns `None`, not a value presented as meaningful.
<!-- END BEGINNER SOLUTION REVIEW -->

We solve selection and transformation tasks on the `tips` dataset.

Contents
- Exercise 1: Dinner rows average tip
- Exercise 2: Boolean column is_big_party
- Exercise 3: Sort by tip percentage descending

---

Setup
```python
import pandas as pd, seaborn as sns

df = sns.load_dataset('tips')
```

Exercise 1 — Average tip for Dinner
```python
avg_tip_dinner = df.loc[df['time'] == 'Dinner', 'tip'].mean()
print(round(avg_tip_dinner, 2))
```
Line-by-line
- Boolean mask selects Dinner rows; then select the tip column; compute mean.

Exercise 2 — is_big_party (size >= 5)
```python
df = df.assign(is_big_party=df['size'] >= 5)
# or: df.loc[:, 'is_big_party'] = df['size'] >= 5
```

Exercise 3 — Sort by tip percentage
```python
df = df.assign(tip_pct=df['tip'] / df['total_bill'])
sorted_df = df.sort_values('tip_pct', ascending=False)
sorted_df[['total_bill','tip','tip_pct']].head()
```
Notes
- Use assign for chain-friendly column creation.
- Avoid chained indexing for assignment; prefer .loc or assign.

---

## Expanded mastery lab solutions

State a DataFrame's row grain, column meanings, and index role before selecting or deriving data. Prefer vectorized, explicit assignments.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Labels, positions, and alignment

`.loc` selects index labels; `.iloc` selects zero-based positions. A boolean
Series is aligned by labels, so a mismatched index can raise or select
unexpected rows. Build masks from the frame being filtered.

### Practices 3–5 — Safe derivation and explicit ownership

```python
import numpy as np
import pandas as pd

frame = pd.DataFrame(
    {"total_bill": [20.0, 0.0, 15.0], "tip": [4.0, 1.0, 3.0], "meal": ["D", "D", "L"]},
    index=[20, 10, 30],
)

denominator = frame["total_bill"].replace(0, np.nan)
frame["tip_rate"] = frame["tip"] / denominator
assert pd.isna(frame.loc[10, "tip_rate"])

# Mutate the original frame deliberately.
frame.loc[frame["meal"].eq("D"), "is_dinner"] = True

# Or create an explicitly independent subset.
dinners = frame.loc[frame["meal"].eq("D")].copy()
dinners["label"] = "dinner"


def mean_tip_for(frame: pd.DataFrame, meal: str) -> float | None:
    selected = frame.loc[frame["meal"].eq(meal), "tip"]
    return None if selected.empty else float(selected.mean())


assert mean_tip_for(frame, "D") == 2.5
assert mean_tip_for(frame, "B") is None
assert frame.loc[20, "total_bill"] == 20.0
assert frame.iloc[0]["total_bill"] == 20.0
```
