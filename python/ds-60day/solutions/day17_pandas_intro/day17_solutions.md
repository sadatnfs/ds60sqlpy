# Day 17 Solutions: pandas Series, DataFrames, and Indexing

**Offline teaching data:** the `restaurant-bills` [synthetic fixture](../../../fixtures/README.md) is invented, so its numbers prove methods, not facts.


<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **labeled tabular data, row grain, indexes, selection, and vectorized columns**. Predict each named
result before comparing your attempt with its matching assertions.

A Series is a one-dimensional labeled array; a DataFrame is a table of
labeled columns sharing an index. Before manipulating a DataFrame,
state its **row grain**, what one row represents, and what makes a row
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

## Exercises 1-3: Worked answers

### Exercise 1: worked answer

**Learner contract:** Using the lesson DataFrame, select rows where `time == 'Dinner'`, then compute the mean of the selected `tip` values. **Before code:** state the row grain and write the mask separately. **Expected behavior:** the result is one scalar equal to `dinner_rows['tip'].mean()`. **Constraints:** use `.loc` and do not loop. **Verify:** assert every selected row is Dinner and the selection is non-empty before reporting the mean.

**Reasoning:** The row grain of the fixture is one restaurant bill per row, so the mask selects whole bills and the mean of their `tip` column is a single scalar. Writing the mask as its own name, `dinner_mask`, makes it inspectable: you can count it and check its index before using it. `.loc[mask]` keeps the original labels, which lets later code line results up with the source. Checking `dinner_rows.empty` before averaging matters because the mean of an empty selection is `NaN`, which looks like data but is not; the reference uses a four-row frame so that the expected mean, 3.5, can be checked by hand.

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

### Exercise 2: worked answer

**Learner contract:** Add a Boolean `is_big_party` column that is `True` exactly when `size >= 5`. **Constraints:** use one vectorized comparison and explicit assignment; do not use row-wise `apply`. **Verify:** compare the new column with `df['size'].ge(5)`, inspect both True and False rows, and confirm row count/index are unchanged.

**Reasoning:** `df["size"].ge(5)` compares the whole column at once and returns a Boolean Series with the same index, so `assign` adds the column without loops and without changing row order. `>= 5` versus `> 5` is the boundary that matters: a party of exactly 5 counts as big under this contract, which the checks on both the True and the False rows confirm. `apply(axis=1)` would produce the same values far more slowly and hide the vectorized intent. `assign` returns a new frame, so the original object is not modified behind your back.

```python
df = df.assign(is_big_party=df["size"].ge(5))
assert df["is_big_party"].equals(df["size"].ge(5))
assert df.loc[df["is_big_party"], "size"].ge(5).all()
assert df.loc[~df["is_big_party"], "size"].lt(5).all()
assert len(df["is_big_party"]) == len(df)
assert df.index.equals(original_df.index)
```

Vectorized comparison preserves index alignment and avoids row loops.

### Exercise 3: worked answer

**Learner contract:** Create a safe `tip_rate = tip / total_bill`, treating a zero bill as missing rather than infinity, then sort descending by `tip_rate`. **Constraints:** preserve the unsorted source in a separate name and choose where missing rates appear. **Verify:** assert there are no infinite values and that non-missing rates are monotonically decreasing.

**Reasoning:** Division by zero in pandas produces `inf` rather than an error, and `inf` sorts to the top of a descending order, so a zero bill would look like the most generous tip. Masking zero denominators to `NaN` before dividing makes that rate missing instead, and `na_position="last"` states where missing rates go in the sorted output. Sorting into a new name, `ordered`, keeps the unsorted source available for comparison. The checks confirm that there are no infinite values and that the non-missing rates decrease.

```python
import numpy as np

safe_bill = df["total_bill"].mask(df["total_bill"].eq(0))
with_rate = df.assign(tip_rate=df["tip"] / safe_bill)
ordered = with_rate.sort_values("tip_rate", ascending=False, na_position="last")
assert not np.isinf(ordered["tip_rate"].dropna()).any()
assert ordered["tip_rate"].dropna().is_monotonic_decreasing
```

## Exercises 4-8: Expanded mastery answers

### Exercise 4: answer contract

**Learner contract:** **Prediction:** Predict the difference between `.loc[labels]` and `.iloc[positions]` after an integer index has been reordered. **Progressive hint:** Labels are not automatically row positions. **Verify:** After reordering integer labels, assert `.loc` returns the requested labels and `.iloc` returns the requested positions; list both resulting indexes.

**Reasoning:** `.loc` selects by index label and `.iloc` by position, and the two diverge as soon as the index is not `0, 1, 2, ...` in order. In the shared implementation for Exercises 4-5, the labels are `30, 10, 20`, so `.loc[[10, 20]]` returns the rows labelled 10 and 20, while `.iloc[[0, 1]]` returns the first two rows, labelled 30 and 10. Integer labels make the confusion likely: `frame.loc[0]` raises `KeyError` there even though a first row exists. Use `.iloc` only when position is truly the meaning.

### Exercise 5: answer contract

**Learner contract:** **Tracing:** Trace a boolean mask through creation, alignment by index, and row selection. What happens if mask/index labels differ? **Progressive hint:** Pandas aligns many labeled objects by index. **Verify:** Display mask and frame indexes side by side, then assert aligned selection for matching labels and the documented error/reindex policy for mismatches.

**Reasoning:** A Boolean Series used as a row selector is aligned to the frame by index label, not by position. A mask built from the frame itself, such as `reordered["value"].str.endswith("y")`, shares its index, so the selection is exact. A mask with different labels cannot be aligned, and `.loc` raises `IndexingError` instead of guessing, as the shared implementation for Exercises 4-5 shows. The safe habit is to build masks from the frame being filtered; when a mask must come from elsewhere, reindex it explicitly and decide what missing labels mean.

### Exercise 6: answer contract

**Learner contract:** **Implementation:** The fixture has no zero bills, so construct the edge case: append one row with `total_bill = 0.0` and `tip = 1.0` to a copy of `df`, then compute `tip_rate` so that the zero bill yields a missing value instead of infinity. **Progressive hint:** Replace a zero denominator with a missing value, for example with `.where(total_bill != 0)`, before dividing. **Verify:** Assert the new row's rate is missing, the 240 original rows equal `tip / total_bill` exactly, `df` itself still has 240 rows, and the column contains no positive or negative infinity.

**Reasoning:** The fixture has no zero bills, so the edge case has to be constructed: one appended row with `total_bill = 0.0` and `tip = 1.0`. Replacing the zero denominator with a missing value, `.where(total_bill != 0)`, before dividing makes that row's rate `NaN` instead of `inf`, while every original row keeps exactly `tip / total_bill`. Building the extended frame with `pd.concat` leaves the 240-row fixture untouched. The shared implementation for Exercises 6-8 checks the new row, the unchanged original rates, and the absence of infinity.

### Exercise 7: answer contract

**Learner contract:** **Debugging:** Repair chained assignment on a filtered DataFrame and explain when to use `.loc` or an explicit `.copy()`. **Progressive hint:** Make ownership and target rows explicit. **Verify:** Turn chained-assignment warnings into explicit `.loc` or `.copy()` ownership; assert the intended frame changes and the unintended frame does not.

**Reasoning:** `frame[mask]["tip"] = 0.0` performs two operations: the first returns a new temporary frame, and the assignment then changes that temporary, so the original stays unchanged. pandas 2 warns with `SettingWithCopyWarning`; pandas 3, which always uses Copy-on-Write, never updates the original through chained assignment. A single `frame.loc[mask, "tip"] = value` names the target frame, rows, and column in one step, and `.copy()` makes an independent subset explicit, as `dinners` does in the shared implementation for Exercises 6-8, which also shows the original left unchanged after a chained assignment.

### Exercise 8: answer contract

**Learner contract:** **Edge case and explanation:** Compute a statistic for a possibly empty selection and return `None` instead of silently presenting `NaN` as a real result. **Progressive hint:** Check `.empty` before aggregating when absence has business meaning. **Verify:** Test nonempty and empty selections; assert the former returns the statistic and the latter returns `None`, not a value presented as meaningful.

**Reasoning:** The mean of an empty selection is `NaN`, which flows into reports and averages as if it were a measurement. Checking `selected.empty` and returning `None` makes absence a distinct, testable outcome, and returning `float(...)` in the nonempty case keeps the result a plain Python number. In the shared implementation for Exercises 6-8, the dinner rows give 2.5 and the nonexistent meal code `"B"` gives `None`. Callers must then handle `None` explicitly, which moves the decision about missing data to the code that knows what it means.

## Expanded mastery lab solutions

State a DataFrame's row grain, column meanings, and index role before selecting or deriving data. Prefer vectorized, explicit assignments.

### Shared implementation for Exercises 4-5: Labels, positions, and alignment

`.loc` selects index labels; `.iloc` selects zero-based positions. A boolean
Series is aligned by labels, so a mismatched index can raise or select
unexpected rows. Build masks from the frame being filtered.

```python
import pandas as pd

reordered = pd.DataFrame({"value": ["thirty", "ten", "twenty"]}, index=[30, 10, 20])
assert reordered.loc[[10, 20]].index.tolist() == [10, 20]  # labels
assert reordered.iloc[[0, 1]].index.tolist() == [30, 10]  # positions

mask = reordered["value"].str.endswith("y")  # built from the frame: same index
assert reordered.loc[mask].index.tolist() == [30, 20]

foreign = pd.Series([True, False, True], index=[0, 1, 2])  # different labels
try:
    reordered.loc[foreign]
except pd.errors.IndexingError as error:
    print("misaligned mask:", error)
else:
    raise AssertionError("a mask with foreign labels should not be accepted")
```

### Shared implementation for Exercises 6-8: Safe derivation and explicit ownership

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

# Chained assignment changes a temporary copy, so the original stays unchanged.
import warnings

chained = frame.copy()
with warnings.catch_warnings(record=True):
    warnings.simplefilter("always")
    chained[chained["meal"].eq("D")]["tip"] = 0.0
assert chained["tip"].tolist() == frame["tip"].tolist()

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

# The lesson fixture has no zero bills, so build the edge case on a copy.
from ds60sqlpy.teaching_data import load_teaching_frame

bills = load_teaching_frame("restaurant-bills")
zero_bill = pd.DataFrame({"total_bill": [0.0], "tip": [1.0]})
extended = pd.concat([bills, zero_bill], ignore_index=True)
rate = extended["tip"] / extended["total_bill"].where(extended["total_bill"] != 0)
assert pd.isna(rate.iloc[-1])
assert rate.iloc[:-1].equals(bills["tip"] / bills["total_bill"])
assert len(bills) == 240 and not np.isinf(rate).any()
```
