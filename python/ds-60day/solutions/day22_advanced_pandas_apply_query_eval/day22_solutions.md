# Day 22 — Solutions: Advanced Pandas (apply vs vectorize, query/eval, categoricals)

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **pandas vectorization, expression APIs, and memory-aware categoricals**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **pandas vectorization, expression APIs, and memory-aware categoricals** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Find one row-wise `apply(axis=1)` in a supplied example and replace it with column arithmetic, string methods, mapping, masks, `np.select`, or group transform as appropriate. **Expected behavior:** values and index match the original for normal and missing inputs. **Constraints:** do not optimize by changing the contract. **Verify:** use `pd.testing` to assert equal values, dtype, and index, then report repeated median execution seconds for both implementations on the same representative frame.

**Reasoning:** Implement this exact contract as written: Find one row-wise `apply(axis=1)` in a supplied example and replace it with column arithmetic, string methods, mapping, masks, `np.select`, or group transform as appropriate. Expected behavior: values and index match the original for normal and missing inputs. Constraints: do not optimize by changing the contract. Keep the prompt's named data and constraints visible in the code, then establish this specific result: use `pd.testing` to assert equal values, dtype, and index, then report repeated median execution seconds for both implementations on the same representative frame. That connects the answer to pandas vectorization, expression APIs, and memory-aware categoricals.

```python
import pandas as pd
from timeit import repeat

frame = pd.DataFrame(
    {"part": [2.0, 6.0, None], "whole": [4.0, 8.0, 2.0]},
    index=["a", "b", "missing"],
)


def rowwise_ratio(data: pd.DataFrame) -> pd.Series:
    return data.apply(lambda row: row["part"] / row["whole"], axis=1)


def vectorized_ratio(data: pd.DataFrame) -> pd.Series:
    return data["part"] / data["whole"]


reference = rowwise_ratio(frame)
vectorized = vectorized_ratio(frame)
pd.testing.assert_series_equal(vectorized, reference)
assert vectorized.index.equals(frame.index)

representative = pd.concat([frame] * 500, ignore_index=True)
rowwise_trials = repeat(
    lambda: rowwise_ratio(representative), repeat=3, number=5
)
vectorized_trials = repeat(
    lambda: vectorized_ratio(representative), repeat=3, number=5
)
assert len(rowwise_trials) == len(vectorized_trials) == 3
```

The vectorized expression states the same arithmetic without building a
row Series and calling Python once per row. Timings are reported as
distributions rather than a brittle pass/fail speed threshold.

**Verification evidence:** use `pd.testing` to assert equal values, dtype, and index, then report repeated median execution seconds for both implementations on the same representative frame.

### Exercise 2 — worked answer

**Learner contract:** Convert a repeated string column to categorical only after profiling. **Evidence:** record row count, unique count, object memory, categorical memory, and the category levels. **Expected behavior:** keep the categorical version only if it reduces memory for this data. **Verify:** values remain equivalent and explain why a nearly unique ID may become larger.

**Reasoning:** Implement this exact contract as written: Convert a repeated string column to categorical only after profiling. Evidence: record row count, unique count, object memory, categorical memory, and the category levels. Expected behavior: keep the categorical version only if it reduces memory for this data. Keep the prompt's named data and constraints visible in the code, then establish this specific result: values remain equivalent and explain why a nearly unique ID may become larger. That connects the answer to pandas vectorization, expression APIs, and memory-aware categoricals.

```python
import pandas as pd


def category_if_smaller(series: pd.Series) -> pd.Series:
    candidate = series.astype("category")
    if candidate.memory_usage(deep=True) < series.memory_usage(deep=True):
        return candidate
    return series.copy()


labels = pd.Series(["east", "west"] * 1_000, name="region")
candidate = labels.astype("category")
profile = {
    "rows": len(labels),
    "unique": labels.nunique(dropna=False),
    "object_bytes": int(labels.memory_usage(deep=True)),
    "category_bytes": int(candidate.memory_usage(deep=True)),
    "levels": candidate.cat.categories.tolist(),
}
optimized = category_if_smaller(labels)
assert optimized.astype("string").tolist() == labels.astype("string").tolist()
assert optimized.memory_usage(deep=True) <= labels.memory_usage(deep=True)

nearly_unique = pd.Series(
    [f"id-{number}" for number in range(1_000)],
    name="customer_id",
)
nearly_unique_category = nearly_unique.astype("category")
assert (
    nearly_unique_category.memory_usage(deep=True)
    > nearly_unique.memory_usage(deep=True)
)
```

The low-cardinality region column stores two levels plus integer codes
and is retained. The nearly unique ID must store almost every original
string in the category table *plus* codes, so conversion makes it
larger and should be rejected.

**Verification evidence:** values remain equivalent and explain why a nearly unique ID may become larger.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict why row-wise `apply(axis=1)` is usually slower than column arithmetic for a simple ratio. **Progressive hint:** Vectorized operations avoid constructing/calling Python work per row. **Verify:** Assert row-wise and vectorized ratios agree including missing values, then report repeated timings on the same frame rather than a single anecdote.

**Reasoning:** Predict this named state change before running it: Prediction: Predict why row-wise `apply(axis=1)` is usually slower than column arithmetic for a simple ratio. Progressive hint: Vectorized operations avoid constructing/calling Python work per row. Then compare the prediction with this proof target: Assert row-wise and vectorized ratios agree including missing values, then report repeated timings on the same frame rather than a single anecdote. This makes pandas vectorization, expression APIs, and memory-aware categoricals observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Assert row-wise and vectorized ratios agree including missing values, then report repeated timings on the same frame rather than a single anecdote.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace `frame.query('amount > @threshold')`: which name comes from a column and which comes from Python scope? **Progressive hint:** `@` marks an external Python variable. **Verify:** Set a known threshold and assert the selected row indexes; change only the Python variable and confirm `@threshold`—not a column—controls the result.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace `frame.query('amount > @threshold')`: which name comes from a column and which comes from Python scope? Progressive hint: `@` marks an external Python variable. Record the named value, shape, label, or iterator position needed to establish: Set a known threshold and assert the selected row indexes; change only the Python variable and confirm `@threshold`—not a column—controls the result. The trace exposes pandas vectorization, expression APIs, and memory-aware categoricals directly.

**Evidence to locate in the grouped implementation:** Set a known threshold and assert the selected row indexes; change only the Python variable and confirm `@threshold`—not a column—controls the result.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Write a function that compares memory before/after categorical conversion and keeps the category only when it reduces memory. **Progressive hint:** Use `memory_usage(deep=True)` on the Series. **Verify:** Assert values are unchanged, record both deep-memory counts, and return categorical only in the fixture where its bytes are smaller.

**Reasoning:** Implement this exact contract as written: Implementation: Write a function that compares memory before/after categorical conversion and keeps the category only when it reduces memory. Progressive hint: Use `memory_usage(deep=True)` on the Series. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert values are unchanged, record both deep-memory counts, and return categorical only in the fixture where its bytes are smaller. That connects the answer to pandas vectorization, expression APIs, and memory-aware categoricals.

**Evidence to locate in the grouped implementation:** Assert values are unchanged, record both deep-memory counts, and return categorical only in the fixture where its bytes are smaller.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Replace a row-wise conditional `apply` with `np.select` or `.where` while preserving missing-value behavior. **Progressive hint:** List conditions from most specific to fallback. **Verify:** Use rows covering every condition plus missing input; assert vectorized labels match the reference apply and missing policy exactly.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Replace a row-wise conditional `apply` with `np.select` or `.where` while preserving missing-value behavior. Progressive hint: List conditions from most specific to fallback. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Use rows covering every condition plus missing input; assert vectorized labels match the reference apply and missing policy exactly. The diagnosis depends on pandas vectorization, expression APIs, and memory-aware categoricals.

**Evidence to locate in the grouped implementation:** Use rows covering every condition plus missing input; assert vectorized labels match the reference apply and missing policy exactly.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Explain why a nearly unique string ID can consume more memory as a category and why category levels must be handled during concatenation. **Progressive hint:** Categories store both codes and a level table. **Verify:** Profile a repeated label and a nearly unique ID; assert the measured memory directions and reconcile category levels before/after concatenation.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Explain why a nearly unique string ID can consume more memory as a category and why category levels must be handled during concatenation. Progressive hint: Categories store both codes and a level table. Values below, at, and above the named boundary must produce the evidence Profile a repeated label and a nearly unique ID; assert the measured memory directions and reconcile category levels before/after concatenation. Those cases show how pandas vectorization, expression APIs, and memory-aware categoricals behaves at its edge.

**Evidence to locate in the grouped implementation:** Profile a repeated label and a nearly unique ID; assert the measured memory directions and reconcile category levels before/after concatenation.

## Expanded mastery lab solutions

Prefer vectorized operations and labeled expressions, but measure rather than assuming. Use categoricals only when repetition justifies them.

### Shared implementation for Exercises 3–4 — Vectorization and query scope

Column arithmetic runs through optimized array operations; row-wise `apply`
creates a Series and calls Python code repeatedly. In `query`, `amount` is a
column and `@threshold` is a Python variable.

### Shared implementation for Exercises 5–7 — Measure categorical memory and vectorize conditions

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
