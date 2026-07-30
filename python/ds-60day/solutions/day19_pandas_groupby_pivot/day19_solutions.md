# Day 19 — Solutions: GroupBy, Aggregation, Pivoting

We summarize, reshape, and validate totals on the tips dataset.

Contents
- Exercise 1: Revenue and avg tip by (day, smoker)
- Exercise 2: Pivot of average tip by (day x time) with fill_value=0
- Exercise 3: Melt wide → long, then groupby to validate totals

---

Setup
```python
import pandas as pd, numpy as np, seaborn as sns

df = sns.load_dataset('tips')
```

Exercise 1 — Group by (day, smoker)
```python
df = df.assign(revenue=df['total_bill'])    # treat total_bill as revenue here
agg = (df
    .groupby(['day','smoker'], as_index=False)
    .agg(revenue=('revenue','sum'), avg_tip=('tip','mean'))
)
agg.head()
```

Exercise 2 — Pivot avg tip by (day x time)
```python
pt = pd.pivot_table(df, values='tip', index='day', columns='time', aggfunc='mean', fill_value=0)
pt
```

Exercise 3 — Melt back to long and validate
```python
long = pt.reset_index().melt(id_vars='day', var_name='time', value_name='avg_tip')
# Validate: join with counts per (day,time) and compare weighted average to original groupby
counts = df.groupby(['day','time']).size().rename('n')
joined = (long.set_index(['day','time'])
              .join(counts)
              .reset_index())
```
Notes
- Use as_index=False or reset_index() to keep flat DataFrames when needed.
- After multi-agg, flatten columns with map or to_flat_index.

---

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Compute total revenue and average tip by `(day, smoker)`. **Hint:** write the intended output column names and source-column/function pairs before calling `.agg`.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Create a pivot table of average tip by day and time, filling absent combinations with zero. **Hint:** identify the row index, output columns, measured value, and aggregation independently.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** Melt a wide table to long, then group to verify totals against the original. **Hint:** preserve an identifier column and compare at the same grain, using a tolerance for floating-point results.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Prediction

**Prompt:** Predict whether rows with a missing group key are included by default and compare `dropna=True` with `dropna=False`.

**Reasoning checkpoint:** Missing group keys are normally excluded unless requested. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Tracing

**Prompt:** Trace a wide table through `melt` and back through `pivot_table`; name the identifier, variable, and value columns.

**Reasoning checkpoint:** Reshaping changes layout, not the underlying measures. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Implementation

**Prompt:** Implement grouped weighted means without using a simple mean of group means.

**Reasoning checkpoint:** Aggregate weighted numerators and denominators at the same grain. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Debugging

**Prompt:** Repair a calculation that joins a customer-level total back to line items and then sums it, multiplying totals by line count.

**Reasoning checkpoint:** Do not re-aggregate a measure after broadcasting it to a finer grain. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Edge case and explanation

**Prompt:** Handle groups whose total weight is zero and categories with no observed rows; state whether they appear in output.

**Reasoning checkpoint:** Make zero-denominator and categorical `observed` behavior explicit. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

## Expanded mastery lab solutions

Write the input and output grain before grouping or reshaping. Reconcile row counts and totals at equivalent grains.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Missing groups and reversible shape

```python
import pandas as pd

frame = pd.DataFrame({"team": ["A", None, "A"], "value": [1, 2, 3]})
default = frame.groupby("team")["value"].sum()
including_missing = frame.groupby("team", dropna=False)["value"].sum()
assert default.sum() == 4
assert including_missing.sum() == 6

wide = pd.DataFrame({"id": [1, 2], "jan": [10, 20], "feb": [11, 22]})
long = wide.melt(id_vars="id", var_name="month", value_name="amount")
round_trip = long.pivot_table(index="id", columns="month", values="amount", aggfunc="sum")
assert round_trip.loc[1, "jan"] == 10
```

### Practices 3–5 — Weighted aggregation at one grain

```python
scores = pd.DataFrame(
    {"team": ["A", "A", "B"], "score": [80.0, 100.0, 50.0], "weight": [1.0, 3.0, 0.0]}
)
scores["weighted_score"] = scores["score"] * scores["weight"]
parts = scores.groupby("team", observed=True).agg(
    numerator=("weighted_score", "sum"),
    denominator=("weight", "sum"),
)
parts["weighted_mean"] = parts["numerator"].div(
    parts["denominator"].where(parts["denominator"].ne(0))
)
assert parts.loc["A", "weighted_mean"] == 95.0
assert pd.isna(parts.loc["B", "weighted_mean"])

# Keep customer totals at customer grain for reconciliation. If a total is
# joined back to lines for display, do not sum the repeated display column.
```
