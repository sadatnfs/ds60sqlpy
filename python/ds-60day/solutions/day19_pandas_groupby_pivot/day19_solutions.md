# Day 19 Solutions: Grouping, Pivoting, and Melting in pandas

**Offline teaching data:** the `restaurant-bills` [synthetic fixture](../../../fixtures/README.md) is invented, so its numbers prove methods, not facts.


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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Group the lesson data by two categorical columns and compute named count, sum, mean, and median outputs. **Before code:** state the output grain and whether missing group keys are included. **Constraints:** use named `.agg`, avoid ambiguous MultiIndex columns, and distinguish row count from unique-entity count. **Verify:** assert group-key uniqueness and reconcile the summed additive measure to the input total.

**Reasoning:** The output grain is one row per observed `(day, smoker)` pair, and writing that before coding tells you which uniqueness check to run afterwards. Named aggregation such as `row_count=("tip", "size")` produces flat, self-describing column names instead of a two-level column index, and `size` counts rows, which is not the same as counting distinct customers. Sums are additive, so the grouped `total_bill` values must add up to the source total; means and medians are not additive and are checked by hand instead. Passing `observed=True` and `dropna=False` states the categorical and missing-key policies explicitly, which matters because the default for `observed` changes from `False` to `True` in pandas 3.

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
summary = df.groupby(
    ["day", "smoker"],
    as_index=False,
    observed=True,
    dropna=False,
).agg(
    row_count=("tip", "size"),
    total_bill=("total_bill", "sum"),
    mean_tip=("tip", "mean"),
    median_tip=("tip", "median"),
)
assert not summary.duplicated(["day", "smoker"]).any()
assert summary["total_bill"].sum() == df["total_bill"].sum()
```

The output grain is one row per observed `(day, smoker)` pair.

### Exercise 2: worked answer

**Learner contract:** Create a pivot table and then return it to long form with `melt` or `stack`. **Contract:** choose explicit index, column, value, aggregation, and missing-cell policy. **Expected behavior:** the long form clearly identifies every dimension and measurement. **Verify:** reconcile non-missing values/totals and explain any rows introduced or removed.

**Reasoning:** `pivot_table` with `aggfunc="mean"` creates one cell for every `(day, time)` combination, including combinations that never occur: in this fixture, Thursday has no dinner rows and Friday has no lunch rows, so those cells are `NaN`. `stack(future_stack=True)` returns to one row per `(day, time)` and keeps those gaps, so the explicit `.dropna()` removes exactly the structural combinations, which is the stated missing-cell policy. Because a mean is not additive, the check compares every value with a direct grouped mean instead of summing the pivot cells.

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

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict whether rows with a missing group key are included by default and compare `dropna=True` with `dropna=False`. **Progressive hint:** Missing group keys are normally excluded unless requested. **Verify:** Group the same fixture both ways; assert totals differ exactly by the missing-key rows and state which output matches the intended policy.

**Reasoning:** By default `groupby` drops rows whose key is missing, so the value 2 for the `None` team disappears from the default result, giving totals of 4 and 6. `dropna=False` keeps a separate `NaN` group, which is the right policy when every row must be accounted for in a reconciliation. The shared implementation for Exercises 3-4 asserts that the difference between the two totals equals the value of the missing-key rows exactly, which proves nothing else changed between the two calls.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace a wide table through `melt` and back through `pivot_table`; name the identifier, variable, and value columns. **Progressive hint:** Reshaping changes layout, not the underlying measures. **Verify:** Assert the long table has identifier/variable/value columns and that pivoting back preserves the original labeled values and additive total.

**Reasoning:** `melt` turns the wide month columns into rows: `id` is the identifier, `month` the variable, and `amount` the value, so 2 rows with two month columns become 4 rows. Pivoting back with `aggfunc="sum"` is lossless here because each `(id, month)` pair occurs exactly once; if a pair repeated, the sum would merge those rows. The shared implementation for Exercises 3-4 asserts the three long-form column names, an unchanged total, and that the round trip reproduces the original frame exactly.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Implement grouped weighted means without using a simple mean of group means. **Progressive hint:** Aggregate weighted numerators and denominators at the same grain. **Verify:** For two groups, compute numerator and denominator explicitly and assert the grouped weighted means, including the chosen zero-weight behavior.

**Reasoning:** A weighted mean is the sum of score times weight divided by the sum of the weights within each group; averaging group means, or averaging the raw scores, gives a different number whenever weights differ. For team A, `(80 * 1 + 100 * 3) / (1 + 3)` is 95, while the plain mean of the two scores is 90. Keeping the numerator and denominator as separate aggregated columns makes both parts visible and checkable before the division.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair a calculation that joins a customer-level total back to line items and then sums it, multiplying totals by line count. **Progressive hint:** Do not re-aggregate a measure after broadcasting it to a finer grain. **Verify:** Show the inflated total after summing broadcast customer totals, then assert the repaired grain-aware calculation matches the original customer-level total.

**Reasoning:** Joining a customer-level total back to the line items repeats it once per line, so summing that column counts customer c1's 15 twice and reports 37 instead of 22. The repair aggregates at the grain where the measure lives: keep one row per customer, or sum the original line amounts. The shared implementation for Exercises 5-7 shows the inflated total first, then asserts that the repaired total matches both the customer-level table and the line amounts, and `validate="many_to_one"` in the merge enforces that each line matches exactly one customer total.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Handle groups whose total weight is zero and categories with no observed rows; state whether they appear in output. **Progressive hint:** Make zero-denominator and categorical `observed` behavior explicit. **Verify:** Test a zero-weight group and an unobserved categorical level; assert their value/presence follows the documented denominator and `observed` policy.

**Reasoning:** Team B's total weight is 0, so its weighted mean is undefined; replacing the zero denominator with a missing value before dividing gives `NaN` instead of `inf` or an error, and the output says so explicitly. For a categorical key, `observed=True` lists only the categories that occur in the data, while `observed=False` also lists unobserved levels such as `"C"`, with an empty sum of 0. Choose `observed=False` when a report must show every level, including those with no rows.

## Expanded mastery lab solutions

Write the input and output grain before grouping or reshaping. Reconcile row counts and totals at equivalent grains.

### Shared implementation for Exercises 3-4: Missing groups and reversible shape

```python
import pandas as pd

frame = pd.DataFrame({"team": ["A", None, "A"], "value": [1, 2, 3]})
default = frame.groupby("team")["value"].sum()
including_missing = frame.groupby("team", dropna=False)["value"].sum()
assert default.sum() == 4
assert including_missing.sum() == 6
missing_key_total = frame.loc[frame["team"].isna(), "value"].sum()
assert including_missing.sum() - default.sum() == missing_key_total

wide = pd.DataFrame({"id": [1, 2], "jan": [10, 20], "feb": [11, 22]})
long = wide.melt(id_vars="id", var_name="month", value_name="amount")
round_trip = long.pivot_table(index="id", columns="month", values="amount", aggfunc="sum")
assert round_trip.loc[1, "jan"] == 10
assert long.columns.tolist() == ["id", "month", "amount"]
assert long["amount"].sum() == wide[["jan", "feb"]].to_numpy().sum()
restored = round_trip.reindex(columns=["jan", "feb"]).rename_axis(columns=None).reset_index()
pd.testing.assert_frame_equal(restored, wide)
```

### Shared implementation for Exercises 5-7: Weighted aggregation at one grain

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

# Broadcasting a customer total to line grain and summing it inflates the total.
lines = pd.DataFrame({"customer": ["c1", "c1", "c2"], "amount": [10.0, 5.0, 7.0]})
customer_totals = lines.groupby("customer", as_index=False).agg(customer_total=("amount", "sum"))
joined = lines.merge(customer_totals, on="customer", validate="many_to_one")
assert joined["customer_total"].sum() == 37.0  # c1's 15 is counted twice
repaired = joined.drop_duplicates("customer")["customer_total"].sum()
assert repaired == customer_totals["customer_total"].sum() == lines["amount"].sum() == 22.0

# An unobserved categorical level appears only when observed=False.
categorical = scores.assign(team=pd.Categorical(scores["team"], categories=["A", "B", "C"]))
observed_only = categorical.groupby("team", observed=True)["weight"].sum()
all_levels = categorical.groupby("team", observed=False)["weight"].sum()
assert observed_only.index.tolist() == ["A", "B"]
assert all_levels.loc["C"] == 0.0
```
