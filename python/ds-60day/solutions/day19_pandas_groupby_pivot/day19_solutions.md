# Day 19 — Solutions: GroupBy, Aggregation, Pivoting

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **split-apply-combine, grouped summaries, and reshaping**. Predict each named
result before comparing your attempt with its matching assertions.

Grouped analysis starts with grain. `groupby` splits rows by key values,
applies reductions or transformations, and combines results. An
aggregation reduces each group and changes row grain; `transform`
returns one aligned value per original row and preserves row count.

A pivot makes combinations of keys into rows and columns while applying
an aggregation for duplicates. `melt` turns wide measurement columns
into a long variable/value pair. Reshaping changes representation, so
state which columns identify an observation and reconcile totals before
and after.

### Vocabulary used in the worked answers

- **group key:** the column values defining membership in a group.
- **aggregation:** a reduction from many rows to a summary.
- **transform:** a group calculation aligned back to every original row.
- **pivot:** a reshape that places one key's values across columns.
- **melt:** a reshape from wide measurement columns to long rows.
- **grain:** what one output row represents after an operation.

### How to compare an answer

For this lesson's **split-apply-combine, grouped summaries, and reshaping** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Group the lesson data by two categorical columns and compute named count, sum, mean, and median outputs. **Before code:** state the output grain and whether missing group keys are included. **Constraints:** use named `.agg`, avoid ambiguous MultiIndex columns, and distinguish row count from unique-entity count. **Verify:** assert group-key uniqueness and reconcile the summed additive measure to the input total.

**Reasoning:** Implement this exact contract as written: Group the lesson data by two categorical columns and compute named count, sum, mean, and median outputs. Before code: state the output grain and whether missing group keys are included. Constraints: use named `.agg`, avoid ambiguous MultiIndex columns, and distinguish row count from unique-entity count. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert group-key uniqueness and reconcile the summed additive measure to the input total. That connects the answer to split-apply-combine, grouped summaries, and reshaping.

```python
import pandas as pd

df = pd.DataFrame(
    {
        "day": ["Thu", "Thu", "Fri", "Fri"],
        "smoker": ["No", "Yes", "No", "No"],
        "time": ["Lunch", "Lunch", "Dinner", "Dinner"],
        "tip": [2.0, 3.0, 4.0, 2.0],
        "total_bill": [10.0, 20.0, 30.0, 15.0],
    }
)

# Grain: one row per observed (day, smoker) pair. This fixture has no
# missing group keys; dropna=False would retain them if introduced.
summary = (
    df.groupby(
        ["day", "smoker"],
        as_index=False,
        observed=True,
        dropna=False,
    )
    .agg(
        row_count=("tip", "size"),
        total_bill=("total_bill", "sum"),
        mean_tip=("tip", "mean"),
        median_tip=("tip", "median"),
    )
)
assert not summary.duplicated(["day", "smoker"]).any()
assert summary["total_bill"].sum() == df["total_bill"].sum()
```

The output grain is one row per observed `(day, smoker)` pair.

**Verification evidence:** assert group-key uniqueness and reconcile the summed additive measure to the input total.

### Exercise 2 — worked answer

**Learner contract:** Create a pivot table and then return it to long form with `melt` or `stack`. **Contract:** choose explicit index, column, value, aggregation, and missing-cell policy. **Expected behavior:** the long form clearly identifies every dimension and measurement. **Verify:** reconcile non-missing values/totals and explain any rows introduced or removed.

**Reasoning:** Implement this exact contract as written: Create a pivot table and then return it to long form with `melt` or `stack`. Contract: choose explicit index, column, value, aggregation, and missing-cell policy. Expected behavior: the long form clearly identifies every dimension and measurement. Keep the prompt's named data and constraints visible in the code, then establish this specific result: reconcile non-missing values/totals and explain any rows introduced or removed. That connects the answer to split-apply-combine, grouped summaries, and reshaping.

```python
pivot = df.pivot_table(
    index="day",
    columns="time",
    values="tip",
    aggfunc="mean",
    observed=True,
)
long = (
    pivot.rename_axis(columns="time")
    .stack(future_stack=True)
    .dropna()
    .rename("mean_tip")
    .reset_index()
)
assert set(long.columns) == {"day", "time", "mean_tip"}
direct = (
    df.groupby(["day", "time"], as_index=False, observed=True)
    .agg(mean_tip=("tip", "mean"))
    .sort_values(["day", "time"])
    .reset_index(drop=True)
)
pd.testing.assert_frame_equal(
    long.sort_values(["day", "time"]).reset_index(drop=True),
    direct,
)
```

A mean is non-additive, so validate each day/time value against a direct
grouped mean rather than summing all pivot cells. This contract drops
unobserved day/time cells when returning to long form; removing
`.dropna()` would instead retain those structural missing combinations.

**Verification evidence:** reconcile non-missing values/totals and explain any rows introduced or removed.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict whether rows with a missing group key are included by default and compare `dropna=True` with `dropna=False`. **Progressive hint:** Missing group keys are normally excluded unless requested. **Verify:** Group the same fixture both ways; assert totals differ exactly by the missing-key rows and state which output matches the intended policy.

**Reasoning:** Predict this named state change before running it: Prediction: Predict whether rows with a missing group key are included by default and compare `dropna=True` with `dropna=False`. Progressive hint: Missing group keys are normally excluded unless requested. Then compare the prediction with this proof target: Group the same fixture both ways; assert totals differ exactly by the missing-key rows and state which output matches the intended policy. This makes split-apply-combine, grouped summaries, and reshaping observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Group the same fixture both ways; assert totals differ exactly by the missing-key rows and state which output matches the intended policy.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace a wide table through `melt` and back through `pivot_table`; name the identifier, variable, and value columns. **Progressive hint:** Reshaping changes layout, not the underlying measures. **Verify:** Assert the long table has identifier/variable/value columns and that pivoting back preserves the original labeled values and additive total.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace a wide table through `melt` and back through `pivot_table`; name the identifier, variable, and value columns. Progressive hint: Reshaping changes layout, not the underlying measures. Record the named value, shape, label, or iterator position needed to establish: Assert the long table has identifier/variable/value columns and that pivoting back preserves the original labeled values and additive total. The trace exposes split-apply-combine, grouped summaries, and reshaping directly.

**Evidence to locate in the grouped implementation:** Assert the long table has identifier/variable/value columns and that pivoting back preserves the original labeled values and additive total.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Implement grouped weighted means without using a simple mean of group means. **Progressive hint:** Aggregate weighted numerators and denominators at the same grain. **Verify:** For two groups, compute numerator and denominator explicitly and assert the grouped weighted means, including the chosen zero-weight behavior.

**Reasoning:** Implement this exact contract as written: Implementation: Implement grouped weighted means without using a simple mean of group means. Progressive hint: Aggregate weighted numerators and denominators at the same grain. Keep the prompt's named data and constraints visible in the code, then establish this specific result: For two groups, compute numerator and denominator explicitly and assert the grouped weighted means, including the chosen zero-weight behavior. That connects the answer to split-apply-combine, grouped summaries, and reshaping.

**Evidence to locate in the grouped implementation:** For two groups, compute numerator and denominator explicitly and assert the grouped weighted means, including the chosen zero-weight behavior.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair a calculation that joins a customer-level total back to line items and then sums it, multiplying totals by line count. **Progressive hint:** Do not re-aggregate a measure after broadcasting it to a finer grain. **Verify:** Show the inflated total after summing broadcast customer totals, then assert the repaired grain-aware calculation matches the original customer-level total.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a calculation that joins a customer-level total back to line items and then sums it, multiplying totals by line count. Progressive hint: Do not re-aggregate a measure after broadcasting it to a finer grain. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Show the inflated total after summing broadcast customer totals, then assert the repaired grain-aware calculation matches the original customer-level total. The diagnosis depends on split-apply-combine, grouped summaries, and reshaping.

**Evidence to locate in the grouped implementation:** Show the inflated total after summing broadcast customer totals, then assert the repaired grain-aware calculation matches the original customer-level total.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Handle groups whose total weight is zero and categories with no observed rows; state whether they appear in output. **Progressive hint:** Make zero-denominator and categorical `observed` behavior explicit. **Verify:** Test a zero-weight group and an unobserved categorical level; assert their value/presence follows the documented denominator and `observed` policy.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Handle groups whose total weight is zero and categories with no observed rows; state whether they appear in output. Progressive hint: Make zero-denominator and categorical `observed` behavior explicit. Values below, at, and above the named boundary must produce the evidence Test a zero-weight group and an unobserved categorical level; assert their value/presence follows the documented denominator and `observed` policy. Those cases show how split-apply-combine, grouped summaries, and reshaping behaves at its edge.

**Evidence to locate in the grouped implementation:** Test a zero-weight group and an unobserved categorical level; assert their value/presence follows the documented denominator and `observed` policy.

## Expanded mastery lab solutions

Write the input and output grain before grouping or reshaping. Reconcile row counts and totals at equivalent grains.

### Shared implementation for Exercises 3–4 — Missing groups and reversible shape

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

### Shared implementation for Exercises 5–7 — Weighted aggregation at one grain

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
