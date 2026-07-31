# Day 22 — Solutions: Advanced Pandas (apply vs vectorize, query/eval, categoricals)

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**pandas vectorization, expression APIs, and memory-aware categoricals**.

Pandas is fastest and clearest when an operation can be expressed over
entire columns: arithmetic, comparisons, string/datetime accessors,
mapping, masks, or group transforms. A row-wise `apply(axis=1)` builds a
Series and calls Python for each row, so it should be a last resort for
genuinely row-dependent logic, not a default.

`query` and `eval` provide readable expression syntax but introduce
another name-resolution layer. Categoricals store repeated labels as
integer codes plus a level table; they can reduce memory and encode a
closed vocabulary, but nearly unique values may use more memory. Measure
before and after and define behavior for unseen categories.

### Vocabulary used in the worked answers

- **vectorization:** column/array operations executed without a Python call per row.
- **row-wise apply:** calling a Python function with each row Series.
- **expression:** a calculation/filter written for `query` or `eval`.
- **categorical:** codes plus a finite table of allowed label values.
- **cardinality:** the count of distinct values in a column.
- **memory profiling:** measuring retained memory under a stated representation.

### Reference pattern 1 — Replace row-wise conditional logic with masks

Column expressions state each rule and preserve index alignment.

```python
import numpy as np
import pandas as pd

frame = pd.DataFrame({"amount": [5, 20, 60]})
frame["band"] = np.select(
    [frame["amount"].ge(50), frame["amount"].ge(10)],
    ["high", "medium"],
    default="low",
)
frame.to_dict("records")
```

**Expected observation:** `[{'amount': 5, 'band': 'low'}, {'amount': 20, 'band': 'medium'}, {'amount': 60, 'band': 'high'}]`.

### Reference pattern 2 — Measure categorical conversion

Keep the conversion only when data characteristics justify it.

```python
labels = pd.Series(["east", "west"] * 1_000, name="region")
categorical = labels.astype("category")
{
    "unique": labels.nunique(),
    "rows": len(labels),
    "object_bytes": int(labels.memory_usage(deep=True)),
    "category_bytes": int(categorical.memory_usage(deep=True)),
}
```

**Expected observation:** Two unique labels across 2,000 rows are reported, and the categorical representation is normally smaller. Exact byte counts vary by pandas version.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Find one row-wise `apply(axis=1)` in a supplied example and replace it with column arithmetic, string methods, mapping, masks, `np.select`, or group transform as appropriate. **Expected behavior:** values and index match the original for normal and missing inputs. **Constraints:** do not optimize by changing the contract. **Verify:** use `pd.testing` for equality and measure repeated execution on representative data.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies pandas vectorization, expression APIs, and memory-aware categoricals.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A named Python function plus `apply` is acceptable for truly irregular per-row objects; benchmark and keep the contract explicit.

**Edge case:** Missing values in conditions, divide-by-zero, nearly unique strings, unseen category levels, and unsafe dynamic expressions require care.

**Solution evidence to inspect:** use `pd.testing` for equality and measure repeated execution on representative data.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Convert a repeated string column to categorical only after profiling. **Evidence:** record row count, unique count, object memory, categorical memory, and the category levels. **Expected behavior:** keep the categorical version only if it reduces memory for this data. **Verify:** values remain equivalent and explain why a nearly unique ID may become larger.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies pandas vectorization, expression APIs, and memory-aware categoricals.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A named Python function plus `apply` is acceptable for truly irregular per-row objects; benchmark and keep the contract explicit.

**Edge case:** Missing values in conditions, divide-by-zero, nearly unique strings, unseen category levels, and unsafe dynamic expressions require care.

**Solution evidence to inspect:** values remain equivalent and explain why a nearly unique ID may become larger.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict why row-wise `apply(axis=1)` is usually slower than column arithmetic for a simple ratio. **Progressive hint:** Vectorized operations avoid constructing/calling Python work per row. **Verify:** Assert row-wise and vectorized ratios agree including missing values, then report repeated timings on the same frame rather than a single anecdote.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying pandas vectorization, expression APIs, and memory-aware categoricals.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A named Python function plus `apply` is acceptable for truly irregular per-row objects; benchmark and keep the contract explicit.

**Edge case:** Missing values in conditions, divide-by-zero, nearly unique strings, unseen category levels, and unsafe dynamic expressions require care.

**Solution evidence to inspect:** Assert row-wise and vectorized ratios agree including missing values, then report repeated timings on the same frame rather than a single anecdote.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace `frame.query('amount > @threshold')`: which name comes from a column and which comes from Python scope? **Progressive hint:** `@` marks an external Python variable. **Verify:** Set a known threshold and assert the selected row indexes; change only the Python variable and confirm `@threshold`—not a column—controls the result.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the pandas vectorization, expression APIs, and memory-aware categoricals model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A named Python function plus `apply` is acceptable for truly irregular per-row objects; benchmark and keep the contract explicit.

**Edge case:** Missing values in conditions, divide-by-zero, nearly unique strings, unseen category levels, and unsafe dynamic expressions require care.

**Solution evidence to inspect:** Set a known threshold and assert the selected row indexes; change only the Python variable and confirm `@threshold`—not a column—controls the result.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Write a function that compares memory before/after categorical conversion and keeps the category only when it reduces memory. **Progressive hint:** Use `memory_usage(deep=True)` on the Series. **Verify:** Assert values are unchanged, record both deep-memory counts, and return categorical only in the fixture where its bytes are smaller.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies pandas vectorization, expression APIs, and memory-aware categoricals.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A named Python function plus `apply` is acceptable for truly irregular per-row objects; benchmark and keep the contract explicit.

**Edge case:** Missing values in conditions, divide-by-zero, nearly unique strings, unseen category levels, and unsafe dynamic expressions require care.

**Solution evidence to inspect:** Assert values are unchanged, record both deep-memory counts, and return categorical only in the fixture where its bytes are smaller.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Replace a row-wise conditional `apply` with `np.select` or `.where` while preserving missing-value behavior. **Progressive hint:** List conditions from most specific to fallback. **Verify:** Use rows covering every condition plus missing input; assert vectorized labels match the reference apply and missing policy exactly.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in pandas vectorization, expression APIs, and memory-aware categoricals.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A named Python function plus `apply` is acceptable for truly irregular per-row objects; benchmark and keep the contract explicit.

**Edge case:** Missing values in conditions, divide-by-zero, nearly unique strings, unseen category levels, and unsafe dynamic expressions require care.

**Solution evidence to inspect:** Use rows covering every condition plus missing input; assert vectorized labels match the reference apply and missing policy exactly.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Explain why a nearly unique string ID can consume more memory as a category and why category levels must be handled during concatenation. **Progressive hint:** Categories store both codes and a level table. **Verify:** Profile a repeated label and a nearly unique ID; assert the measured memory directions and reconcile category levels before/after concatenation.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from pandas vectorization, expression APIs, and memory-aware categoricals.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A named Python function plus `apply` is acceptable for truly irregular per-row objects; benchmark and keep the contract explicit.

**Edge case:** Missing values in conditions, divide-by-zero, nearly unique strings, unseen category levels, and unsafe dynamic expressions require care.

**Solution evidence to inspect:** Profile a repeated label and a nearly unique ID; assert the measured memory directions and reconcile category levels before/after concatenation.
<!-- END BEGINNER SOLUTION REVIEW -->

We identify a slow apply, rewrite with vectorized ops, and demonstrate memory savings from categoricals.

Contents
- Exercise 1: Replace slow apply with vectorized logic or transform
- Exercise 2: Convert high-cardinality string column to category and profile memory

---

Exercise 1 — Replace slow apply
```python
import pandas as pd
import numpy as np

# Example: compute within-group percentage without row-wise apply
np.random.seed(0)
df = pd.DataFrame({
    'region': np.random.choice(list('ABCD'), size=1000),
    'sales': np.random.randint(1, 100, size=1000)
})

# SLOW (avoid):
# df['pct'] = df.apply(lambda r: r['sales'] / df[df['region']==r['region']]['sales'].sum(), axis=1)

# FAST (vectorized with transform):
group_totals = df.groupby('region')['sales'].transform('sum')
df['pct'] = df['sales'] / group_totals

print(df.head())
```
Why it’s better
- transform broadcasts group totals back to rows; no Python loop
- Readable and scales to large data

Alternative: boolean logic with vectorization
```python
# Tip percentage without apply
df2 = pd.DataFrame({'total_bill':[10,20], 'tip':[2,5]})
df2 = df2.assign(tip_pct=df2['tip']/df2['total_bill'])
```

---

Exercise 2 — Categoricals for memory
```python
import pandas as pd
import numpy as np

n = 1_000_00  # 100k rows
cities = [f"city_{i}" for i in range(2000)]
raw = pd.DataFrame({'city': np.random.choice(cities, size=n)})

mem_before = raw['city'].memory_usage(deep=True)
raw['city'] = raw['city'].astype('category')
mem_after = raw['city'].memory_usage(deep=True)

print({"bytes_before": int(mem_before), "bytes_after": int(mem_after)})
print(raw['city'].dtype)
```
Notes
- Category compresses repeated strings; huge savings for large, repetitive columns
- Beware: category imposes a fixed vocabulary; handle unknowns when joining new data

query/eval tip
```python
th = 0.2
subset = df.query('pct > @th')      # pass local variable with @
```

---

## Expanded mastery lab solutions

Prefer vectorized operations and labeled expressions, but measure rather than assuming. Use categoricals only when repetition justifies them.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Vectorization and query scope

Column arithmetic runs through optimized array operations; row-wise `apply`
creates a Series and calls Python code repeatedly. In `query`, `amount` is a
column and `@threshold` is a Python variable.

### Practices 3–5 — Measure categorical memory and vectorize conditions

```python
import numpy as np
import pandas as pd


def category_if_smaller(series: pd.Series) -> tuple[pd.Series, dict[str, int]]:
    """Return the lower-memory representation plus measured byte counts."""

    before = int(series.memory_usage(deep=True))
    candidate = series.astype("category")
    after = int(candidate.memory_usage(deep=True))
    chosen = candidate if after < before else series.copy()
    return chosen, {"before": before, "after": after}


frame = pd.DataFrame(
    {"amount": [5.0, 20.0, 100.0, np.nan], "segment": ["A", "A", "B", "A"]}
)
threshold = 10
assert frame.query("amount > @threshold")["amount"].tolist() == [20.0, 100.0]

conditions = [frame["amount"].ge(100), frame["amount"].ge(10)]
labels = np.select(conditions, ["high", "medium"], default="low")
frame["band"] = pd.Series(labels, index=frame.index).where(frame["amount"].notna())
assert frame["band"].tolist()[:3] == ["low", "medium", "high"]
assert pd.isna(frame.loc[3, "band"])

optimized, memory = category_if_smaller(frame["segment"])
assert memory["before"] > 0 and memory["after"] > 0
```

For an almost-unique ID, the level table repeats nearly all original strings
in addition to codes. Concatenating categoricals also requires reconciling their
level sets; measure the final workflow, not a toy column alone.
