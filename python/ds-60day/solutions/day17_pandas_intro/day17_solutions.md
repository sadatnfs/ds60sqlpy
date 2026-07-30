# Day 17 — Solutions: Pandas Intro (Series, DataFrame, Index)

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Select Dinner rows and compute the average tip. **Hint:** create one boolean mask, select the `tip` Series, then aggregate.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Add `is_big_party` for rows where `size >= 5`. **Hint:** assign one vectorized comparison to a new column; do not loop through rows.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** Sort descending by tip percentage (`tip / total_bill`). **Hint:** derive a named column first so you can inspect divide-by-zero or missing results.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Prediction

**Prompt:** Predict the difference between `.loc[labels]` and `.iloc[positions]` after an integer index has been reordered.

**Reasoning checkpoint:** Labels are not automatically row positions. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Tracing

**Prompt:** Trace a boolean mask through creation, alignment by index, and row selection. What happens if mask/index labels differ?

**Reasoning checkpoint:** Pandas aligns many labeled objects by index. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Implementation

**Prompt:** Create a safe `tip_rate` column that yields missing values rather than infinity when `total_bill` is zero.

**Reasoning checkpoint:** Mask or replace the zero denominator before division. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Debugging

**Prompt:** Repair chained assignment on a filtered DataFrame and explain when to use `.loc` or an explicit `.copy()`.

**Reasoning checkpoint:** Make ownership and target rows explicit. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Edge case and explanation

**Prompt:** Compute a statistic for a possibly empty selection and return `None` instead of silently presenting `NaN` as a real result.

**Reasoning checkpoint:** Check `.empty` before aggregating when absence has business meaning. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
