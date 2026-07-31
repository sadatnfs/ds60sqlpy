# Day 17 — Solutions: Pandas Intro (Series, DataFrame, Index)

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **labeled tabular data, row grain, indexes, selection, and vectorized columns**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **labeled tabular data, row grain, indexes, selection, and vectorized columns** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–3 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Using the lesson DataFrame, select rows where `time == 'Dinner'`, then compute the mean of the selected `tip` values. **Before code:** state the row grain and write the mask separately. **Expected behavior:** the result is one scalar equal to `dinner_rows['tip'].mean()`. **Constraints:** use `.loc` and do not loop. **Verify:** assert every selected row is Dinner and the selection is non-empty before reporting the mean.

**Reasoning:** Implement this exact contract as written: Using the lesson DataFrame, select rows where `time == 'Dinner'`, then compute the mean of the selected `tip` values. Before code: state the row grain and write the mask separately. Expected behavior: the result is one scalar equal to `dinner_rows['tip'].mean()`. Constraints: use `.loc` and do not loop. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert every selected row is Dinner and the selection is non-empty before reporting the mean. That connects the answer to labeled tabular data, row grain, indexes, selection, and vectorized columns.

```python
import pandas as pd

df = pd.DataFrame(
    {
        "time": ["Lunch", "Dinner", "Dinner", "Lunch"],
        "tip": [2.0, 4.0, 3.0, 1.5],
        "size": [2, 5, 3, 6],
        "total_bill": [10.0, 20.0, 0.0, 12.0],
    },
    index=["a", "b", "c", "d"],
)
original_df = df.copy(deep=True)

dinner_mask = df["time"].eq("Dinner")
dinner_rows = df.loc[dinner_mask]
if dinner_rows.empty:
    raise ValueError("the lesson fixture has no Dinner rows")
average_tip = dinner_rows["tip"].mean()

assert dinner_rows["time"].eq("Dinner").all()
assert average_tip == dinner_rows["tip"].mean() == 3.5
```

The fixture grain is one restaurant check per row. Keeping
`dinner_mask`, `dinner_rows`, and the scalar aggregation separate makes
each shape transition inspectable.

**Verification evidence:** assert every selected row is Dinner and the selection is non-empty before reporting the mean.

### Exercise 2 — worked answer

**Learner contract:** Add a Boolean `is_big_party` column that is `True` exactly when `size >= 5`. **Constraints:** use one vectorized comparison and explicit assignment; do not use row-wise `apply`. **Verify:** compare the new column with `df['size'].ge(5)`, inspect both True and False rows, and confirm row count/index are unchanged.

**Reasoning:** Implement this exact contract as written: Add a Boolean `is_big_party` column that is `True` exactly when `size >= 5`. Constraints: use one vectorized comparison and explicit assignment; do not use row-wise `apply`. Keep the prompt's named data and constraints visible in the code, then establish this specific result: compare the new column with `df['size'].ge(5)`, inspect both True and False rows, and confirm row count/index are unchanged. That connects the answer to labeled tabular data, row grain, indexes, selection, and vectorized columns.

```python
df = df.assign(is_big_party=df["size"].ge(5))
assert df["is_big_party"].equals(df["size"].ge(5))
assert df.loc[df["is_big_party"], "size"].ge(5).all()
assert df.loc[~df["is_big_party"], "size"].lt(5).all()
assert len(df["is_big_party"]) == len(df)
assert df.index.equals(original_df.index)
```

Vectorized comparison preserves index alignment and avoids row loops.

**Verification evidence:** compare the new column with `df['size'].ge(5)`, inspect both True and False rows, and confirm row count/index are unchanged.

### Exercise 3 — worked answer

**Learner contract:** Create a safe `tip_rate = tip / total_bill`, treating a zero bill as missing rather than infinity, then sort descending by `tip_rate`. **Constraints:** preserve the unsorted source in a separate name and choose where missing rates appear. **Verify:** assert there are no infinite values and that non-missing rates are monotonically decreasing.

**Reasoning:** Implement this exact contract as written: Create a safe `tip_rate = tip / total_bill`, treating a zero bill as missing rather than infinity, then sort descending by `tip_rate`. Constraints: preserve the unsorted source in a separate name and choose where missing rates appear. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert there are no infinite values and that non-missing rates are monotonically decreasing. That connects the answer to labeled tabular data, row grain, indexes, selection, and vectorized columns.

```python
import numpy as np

safe_bill = df["total_bill"].mask(df["total_bill"].eq(0))
with_rate = df.assign(tip_rate=df["tip"] / safe_bill)
ordered = with_rate.sort_values("tip_rate", ascending=False, na_position="last")
assert not np.isinf(ordered["tip_rate"].dropna()).any()
assert ordered["tip_rate"].dropna().is_monotonic_decreasing
```

**Verification evidence:** assert there are no infinite values and that non-missing rates are monotonically decreasing.

## Exercises 4–8 — Expanded mastery answers

### Exercise 4 — answer contract

**Learner contract:** **Prediction:** Predict the difference between `.loc[labels]` and `.iloc[positions]` after an integer index has been reordered. **Progressive hint:** Labels are not automatically row positions. **Verify:** After reordering integer labels, assert `.loc` returns the requested labels and `.iloc` returns the requested positions; list both resulting indexes.

**Reasoning:** Predict this named state change before running it: Prediction: Predict the difference between `.loc[labels]` and `.iloc[positions]` after an integer index has been reordered. Progressive hint: Labels are not automatically row positions. Then compare the prediction with this proof target: After reordering integer labels, assert `.loc` returns the requested labels and `.iloc` returns the requested positions; list both resulting indexes. This makes labeled tabular data, row grain, indexes, selection, and vectorized columns observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** After reordering integer labels, assert `.loc` returns the requested labels and `.iloc` returns the requested positions; list both resulting indexes.

### Exercise 5 — answer contract

**Learner contract:** **Tracing:** Trace a boolean mask through creation, alignment by index, and row selection. What happens if mask/index labels differ? **Progressive hint:** Pandas aligns many labeled objects by index. **Verify:** Display mask and frame indexes side by side, then assert aligned selection for matching labels and the documented error/reindex policy for mismatches.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace a boolean mask through creation, alignment by index, and row selection. What happens if mask/index labels differ? Progressive hint: Pandas aligns many labeled objects by index. Record the named value, shape, label, or iterator position needed to establish: Display mask and frame indexes side by side, then assert aligned selection for matching labels and the documented error/reindex policy for mismatches. The trace exposes labeled tabular data, row grain, indexes, selection, and vectorized columns directly.

**Evidence to locate in the grouped implementation:** Display mask and frame indexes side by side, then assert aligned selection for matching labels and the documented error/reindex policy for mismatches.

### Exercise 6 — answer contract

**Learner contract:** **Implementation:** Create a safe `tip_rate` column that yields missing values rather than infinity when `total_bill` is zero. **Progressive hint:** Mask or replace the zero denominator before division. **Verify:** Assert zero bills yield missing rates, positive bills yield the calculated ratio, and the entire column contains no positive/negative infinity.

**Reasoning:** Implement this exact contract as written: Implementation: Create a safe `tip_rate` column that yields missing values rather than infinity when `total_bill` is zero. Progressive hint: Mask or replace the zero denominator before division. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert zero bills yield missing rates, positive bills yield the calculated ratio, and the entire column contains no positive/negative infinity. That connects the answer to labeled tabular data, row grain, indexes, selection, and vectorized columns.

**Evidence to locate in the grouped implementation:** Assert zero bills yield missing rates, positive bills yield the calculated ratio, and the entire column contains no positive/negative infinity.

### Exercise 7 — answer contract

**Learner contract:** **Debugging:** Repair chained assignment on a filtered DataFrame and explain when to use `.loc` or an explicit `.copy()`. **Progressive hint:** Make ownership and target rows explicit. **Verify:** Turn chained-assignment warnings into explicit `.loc` or `.copy()` ownership; assert the intended frame changes and the unintended frame does not.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair chained assignment on a filtered DataFrame and explain when to use `.loc` or an explicit `.copy()`. Progressive hint: Make ownership and target rows explicit. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Turn chained-assignment warnings into explicit `.loc` or `.copy()` ownership; assert the intended frame changes and the unintended frame does not. The diagnosis depends on labeled tabular data, row grain, indexes, selection, and vectorized columns.

**Evidence to locate in the grouped implementation:** Turn chained-assignment warnings into explicit `.loc` or `.copy()` ownership; assert the intended frame changes and the unintended frame does not.

### Exercise 8 — answer contract

**Learner contract:** **Edge case and explanation:** Compute a statistic for a possibly empty selection and return `None` instead of silently presenting `NaN` as a real result. **Progressive hint:** Check `.empty` before aggregating when absence has business meaning. **Verify:** Test nonempty and empty selections; assert the former returns the statistic and the latter returns `None`, not a value presented as meaningful.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Compute a statistic for a possibly empty selection and return `None` instead of silently presenting `NaN` as a real result. Progressive hint: Check `.empty` before aggregating when absence has business meaning. Values below, at, and above the named boundary must produce the evidence Test nonempty and empty selections; assert the former returns the statistic and the latter returns `None`, not a value presented as meaningful. Those cases show how labeled tabular data, row grain, indexes, selection, and vectorized columns behaves at its edge.

**Evidence to locate in the grouped implementation:** Test nonempty and empty selections; assert the former returns the statistic and the latter returns `None`, not a value presented as meaningful.

## Expanded mastery lab solutions

State a DataFrame's row grain, column meanings, and index role before selecting or deriving data. Prefer vectorized, explicit assignments.

### Shared implementation for Exercises 4–5 — Labels, positions, and alignment

`.loc` selects index labels; `.iloc` selects zero-based positions. A boolean
Series is aligned by labels, so a mismatched index can raise or select
unexpected rows. Build masks from the frame being filtered.

### Shared implementation for Exercises 6–8 — Safe derivation and explicit ownership

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
