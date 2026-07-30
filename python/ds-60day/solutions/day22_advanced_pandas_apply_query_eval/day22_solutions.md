# Day 22 — Solutions: Advanced Pandas (apply vs vectorize, query/eval, categoricals)

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Find a slow row-wise `apply` and replace it with vectorized logic. **Hint:** classify the operation as arithmetic, conditional selection, string method, mapping, or group transform; pandas has primitives for each.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Convert a repeated string column to categorical and profile memory. **Hint:** compare `memory_usage(deep=True)` before and after, record unique/row counts, and do not assume a high-cardinality column will improve.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict why row-wise `apply(axis=1)` is usually slower than column arithmetic for a simple ratio.

**Reasoning checkpoint:** Vectorized operations avoid constructing/calling Python work per row. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace `frame.query('amount > @threshold')`: which name comes from a column and which comes from Python scope?

**Reasoning checkpoint:** `@` marks an external Python variable. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Write a function that compares memory before/after categorical conversion and keeps the category only when it reduces memory.

**Reasoning checkpoint:** Use `memory_usage(deep=True)` on the Series. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Replace a row-wise conditional `apply` with `np.select` or `.where` while preserving missing-value behavior.

**Reasoning checkpoint:** List conditions from most specific to fallback. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Explain why a nearly unique string ID can consume more memory as a category and why category levels must be handled during concatenation.

**Reasoning checkpoint:** Categories store both codes and a level table. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
