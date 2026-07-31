# Day 19 — Solutions: GroupBy, Aggregation, Pivoting

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**split-apply-combine, grouped summaries, and reshaping**.

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

### Reference pattern 1 — Aggregate to one row per group

Write the output grain before reading the result.

```python
import pandas as pd

orders = pd.DataFrame({
    "order_id": [1, 2, 3, 4],
    "region": ["east", "east", "west", "west"],
    "amount": [10, 15, 7, 8],
})
summary = (
    orders.groupby("region", as_index=False)
    .agg(order_count=("order_id", "nunique"), total=("amount", "sum"))
)
summary.to_dict("records")
```

**Expected observation:** `[{'region': 'east', 'order_count': 2, 'total': 25}, {'region': 'west', 'order_count': 2, 'total': 15}]`.

### Reference pattern 2 — Align a group total back to every source row

Transform preserves the original index and row count.

```python
orders = orders.assign(
    region_total=orders.groupby("region")["amount"].transform("sum")
)
orders[["order_id", "region", "amount", "region_total"]].to_dict("records")
```

**Expected observation:** Every east row receives `25` and every west row receives `15`; there are still four rows.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Group the lesson data by two categorical columns and compute named count, sum, mean, and median outputs. **Before code:** state the output grain and whether missing group keys are included. **Constraints:** use named `.agg`, avoid ambiguous MultiIndex columns, and distinguish row count from unique-entity count. **Verify:** assert group-key uniqueness and reconcile the summed additive measure to the input total.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies split-apply-combine, grouped summaries, and reshaping.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `crosstab` for frequency tables, `pivot` only when combinations are unique, and `pivot_table` when duplicates need aggregation.

**Edge case:** Missing group keys, unobserved categories, duplicate pivot cells, all-missing groups, and non-additive measures need explicit handling.

**Solution evidence to inspect:** assert group-key uniqueness and reconcile the summed additive measure to the input total.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Create a pivot table and then return it to long form with `melt` or `stack`. **Contract:** choose explicit index, column, value, aggregation, and missing-cell policy. **Expected behavior:** the long form clearly identifies every dimension and measurement. **Verify:** reconcile non-missing values/totals and explain any rows introduced or removed.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies split-apply-combine, grouped summaries, and reshaping.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `crosstab` for frequency tables, `pivot` only when combinations are unique, and `pivot_table` when duplicates need aggregation.

**Edge case:** Missing group keys, unobserved categories, duplicate pivot cells, all-missing groups, and non-additive measures need explicit handling.

**Solution evidence to inspect:** reconcile non-missing values/totals and explain any rows introduced or removed.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict whether rows with a missing group key are included by default and compare `dropna=True` with `dropna=False`. **Progressive hint:** Missing group keys are normally excluded unless requested. **Verify:** Group the same fixture both ways; assert totals differ exactly by the missing-key rows and state which output matches the intended policy.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying split-apply-combine, grouped summaries, and reshaping.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `crosstab` for frequency tables, `pivot` only when combinations are unique, and `pivot_table` when duplicates need aggregation.

**Edge case:** Missing group keys, unobserved categories, duplicate pivot cells, all-missing groups, and non-additive measures need explicit handling.

**Solution evidence to inspect:** Group the same fixture both ways; assert totals differ exactly by the missing-key rows and state which output matches the intended policy.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace a wide table through `melt` and back through `pivot_table`; name the identifier, variable, and value columns. **Progressive hint:** Reshaping changes layout, not the underlying measures. **Verify:** Assert the long table has identifier/variable/value columns and that pivoting back preserves the original labeled values and additive total.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the split-apply-combine, grouped summaries, and reshaping model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `crosstab` for frequency tables, `pivot` only when combinations are unique, and `pivot_table` when duplicates need aggregation.

**Edge case:** Missing group keys, unobserved categories, duplicate pivot cells, all-missing groups, and non-additive measures need explicit handling.

**Solution evidence to inspect:** Assert the long table has identifier/variable/value columns and that pivoting back preserves the original labeled values and additive total.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement grouped weighted means without using a simple mean of group means. **Progressive hint:** Aggregate weighted numerators and denominators at the same grain. **Verify:** For two groups, compute numerator and denominator explicitly and assert the grouped weighted means, including the chosen zero-weight behavior.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies split-apply-combine, grouped summaries, and reshaping.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `crosstab` for frequency tables, `pivot` only when combinations are unique, and `pivot_table` when duplicates need aggregation.

**Edge case:** Missing group keys, unobserved categories, duplicate pivot cells, all-missing groups, and non-additive measures need explicit handling.

**Solution evidence to inspect:** For two groups, compute numerator and denominator explicitly and assert the grouped weighted means, including the chosen zero-weight behavior.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a calculation that joins a customer-level total back to line items and then sums it, multiplying totals by line count. **Progressive hint:** Do not re-aggregate a measure after broadcasting it to a finer grain. **Verify:** Show the inflated total after summing broadcast customer totals, then assert the repaired grain-aware calculation matches the original customer-level total.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in split-apply-combine, grouped summaries, and reshaping.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `crosstab` for frequency tables, `pivot` only when combinations are unique, and `pivot_table` when duplicates need aggregation.

**Edge case:** Missing group keys, unobserved categories, duplicate pivot cells, all-missing groups, and non-additive measures need explicit handling.

**Solution evidence to inspect:** Show the inflated total after summing broadcast customer totals, then assert the repaired grain-aware calculation matches the original customer-level total.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Handle groups whose total weight is zero and categories with no observed rows; state whether they appear in output. **Progressive hint:** Make zero-denominator and categorical `observed` behavior explicit. **Verify:** Test a zero-weight group and an unobserved categorical level; assert their value/presence follows the documented denominator and `observed` policy.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from split-apply-combine, grouped summaries, and reshaping.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use `crosstab` for frequency tables, `pivot` only when combinations are unique, and `pivot_table` when duplicates need aggregation.

**Edge case:** Missing group keys, unobserved categories, duplicate pivot cells, all-missing groups, and non-additive measures need explicit handling.

**Solution evidence to inspect:** Test a zero-weight group and an unobserved categorical level; assert their value/presence follows the documented denominator and `observed` policy.
<!-- END BEGINNER SOLUTION REVIEW -->

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
