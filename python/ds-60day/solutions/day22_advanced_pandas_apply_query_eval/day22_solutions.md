# Day 22 Solutions: Advanced pandas: Vectorization, query, and Categoricals

**Offline teaching data:** the `restaurant-bills` [synthetic fixture](../../../fixtures/README.md) is invented, so its numbers prove methods, not facts.


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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Find one row-wise `apply(axis=1)` in a supplied example and replace it with column arithmetic, string methods, mapping, masks, `np.select`, or group transform as appropriate. **Expected behavior:** values and index match the original for normal and missing inputs. **Constraints:** do not optimize by changing the contract. **Verify:** use `pd.testing` to assert equal values, dtype, and index, then report repeated median execution seconds for both implementations on the same representative frame.

**Reasoning:** `apply(axis=1)` builds a Series for every row and calls a Python function on it, while `data["part"] / data["whole"]` performs the same division in one array operation. The contract is identical either way: equal values, the same `float64` dtype, the same index, and `NaN` where `part` is missing, which `assert_series_equal` checks in one call. The timings are recorded as three repeated trials on a larger frame instead of being asserted against a threshold, because run time depends on the machine and its current load; what must hold everywhere is that both versions agree.

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
rowwise_trials = repeat(lambda: rowwise_ratio(representative), repeat=3, number=5)
vectorized_trials = repeat(lambda: vectorized_ratio(representative), repeat=3, number=5)
assert len(rowwise_trials) == len(vectorized_trials) == 3
```

The vectorized expression states the same arithmetic without building a
row Series and calling Python once per row. Timings are reported as
distributions rather than a brittle pass/fail speed threshold.

### Exercise 2: worked answer

**Learner contract:** Convert a repeated string column to categorical only after profiling. **Evidence:** record row count, unique count, object memory, categorical memory, and the category levels. **Expected behavior:** keep the categorical version only if it reduces memory for this data. **Verify:** values remain equivalent and explain why a nearly unique ID may become larger.

**Reasoning:** A categorical stores each distinct label once plus a small integer code per row, so a column with two regions repeated 2,000 times shrinks substantially. A nearly unique ID gains nothing: the category table still holds almost every string, and the codes come on top, so its memory grows. Profiling rows, unique count, and both byte counts before converting turns the decision into evidence, and `category_if_smaller` keeps the original whenever the categorical is not smaller. Comparing the values as strings proves that the conversion changed only the representation.

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
assert nearly_unique_category.memory_usage(deep=True) > nearly_unique.memory_usage(deep=True)
```

The low-cardinality region column stores two levels plus integer codes
and is retained. The nearly unique ID must store almost every original
string in the category table *plus* codes, so conversion makes it
larger and should be rejected.

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict why row-wise `apply(axis=1)` is usually slower than column arithmetic for a simple ratio. **Progressive hint:** Vectorized operations avoid constructing/calling Python work per row. **Verify:** Assert row-wise and vectorized ratios agree including missing values, then report repeated timings on the same frame rather than a single anecdote.

**Reasoning:** For a simple ratio, the per-row overhead of `apply(axis=1)`, building a row Series and calling a Python function, is far larger than the division itself, so the vectorized expression, which runs in compiled array code, is usually much faster. The shared implementation for Exercises 3-4 first asserts that both versions agree, including the missing rows, and then prints three repeated timings for each, so the comparison rests on more than a single run.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace `frame.query('amount > @threshold')`: which name comes from a column and which comes from Python scope? **Progressive hint:** `@` marks an external Python variable. **Verify:** Set a known threshold and assert the selected row indexes; change only the Python variable and confirm `@threshold`, not a column, controls the result.

**Reasoning:** Inside `query`, a bare name such as `amount` refers to a column of the frame, and `@threshold` refers to a variable in the surrounding Python code. The shared implementation for Exercises 3-4 selects rows `b` and `c` with a threshold of 10 and only row `c` after changing the Python variable to 50, which proves that the variable, not a column, controls the cut-off. The `@` prefix keeps that meaning even if the frame also had a column named `threshold`.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Write a function that compares memory before/after categorical conversion and keeps the category only when it reduces memory. **Progressive hint:** Use `memory_usage(deep=True)` on the Series. **Verify:** Assert values are unchanged, record both deep-memory counts, and return categorical only in the fixture where its bytes are smaller.

**Reasoning:** `memory_usage(deep=True)` counts the bytes of the Python string objects as well as the array of references to them; without `deep=True`, an object column looks much smaller than it really is, and the comparison would be misleading. The helper measures both representations, keeps the categorical only when it is strictly smaller, and returns the byte counts as evidence. The shared implementation for Exercises 5-7 shows both outcomes: the repeated label becomes categorical, while the unique IDs, and the tiny four-row `segment` column, stay as they are, with unchanged values in every case.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Replace a row-wise conditional `apply` with `np.select` or `.where` while preserving missing-value behavior. **Progressive hint:** List conditions from most specific to fallback. **Verify:** Use rows covering every condition plus missing input; assert vectorized labels match the reference apply and missing policy exactly.

**Reasoning:** `np.select` checks its conditions in order and uses the first that matches, so `amount >= 100` must come before `amount >= 10`, or every high value would be labelled medium. `np.select` has no notion of missing values: `NaN >= 10` is `False`, so a missing amount would fall through to `"low"`, and the trailing `.where(amount.notna())` restores the missing label. The shared implementation for Exercises 5-7 compares the result with a row-wise reference function for every band and the missing row.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Explain why a nearly unique string ID can consume more memory as a category and why category levels must be handled during concatenation. **Progressive hint:** Categories store both codes and a level table. **Verify:** Profile a repeated label and a nearly unique ID; assert the measured memory directions and reconcile category levels before/after concatenation.

**Reasoning:** A categorical keeps a table of levels in addition to the codes, so for a nearly unique ID the table is almost as large as the original column, and the codes are added on top. Levels also matter when combining data: concatenating two categoricals with different level sets produces an `object` column, losing the categorical dtype without any error. The shared implementation for Exercises 5-7 shows that loss, then reconciles the levels by converting both parts to one shared `CategoricalDtype` before concatenating, or with `union_categoricals`.

## Expanded mastery lab solutions

Prefer vectorized operations and labeled expressions, but measure rather than assuming. Use categoricals only when repetition justifies them.

### Shared implementation for Exercises 3-4: Vectorization and query scope

Column arithmetic runs through optimized array operations; row-wise `apply`
creates a Series and calls Python code repeatedly. In `query`, `amount` is a
column and `@threshold` is a Python variable.

```python
from timeit import repeat

import pandas as pd

ratios = pd.DataFrame({"part": [1.0, None, 3.0] * 1_000, "whole": [2.0, 4.0, 6.0] * 1_000})


def ratio_by_row(data: pd.DataFrame) -> pd.Series:
    return data.apply(lambda row: row["part"] / row["whole"], axis=1)


def ratio_by_column(data: pd.DataFrame) -> pd.Series:
    return data["part"] / data["whole"]


pd.testing.assert_series_equal(ratio_by_row(ratios), ratio_by_column(ratios))
for name, function in [("apply", ratio_by_row), ("vectorized", ratio_by_column)]:
    trials = repeat(lambda: function(ratios), repeat=3, number=3)
    print(name, [round(seconds, 4) for seconds in trials])

amounts = pd.DataFrame({"amount": [5.0, 20.0, 100.0]}, index=["a", "b", "c"])
threshold = 10
assert amounts.query("amount > @threshold").index.tolist() == ["b", "c"]
threshold = 50  # change only the Python variable
assert amounts.query("amount > @threshold").index.tolist() == ["c"]
```

### Shared implementation for Exercises 5-7: Measure categorical memory and vectorize conditions

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


frame = pd.DataFrame({"amount": [5.0, 20.0, 100.0, np.nan], "segment": ["A", "A", "B", "A"]})
threshold = 10
assert frame.query("amount > @threshold")["amount"].tolist() == [20.0, 100.0]

conditions = [frame["amount"].ge(100), frame["amount"].ge(10)]
labels = np.select(conditions, ["high", "medium"], default="low")
frame["band"] = pd.Series(labels, index=frame.index).where(frame["amount"].notna())
assert frame["band"].tolist()[:3] == ["low", "medium", "high"]
assert pd.isna(frame.loc[3, "band"])


def band_for(row: pd.Series) -> str | None:
    """Row-wise reference used only to check the vectorized labels."""
    if pd.isna(row["amount"]):
        return None
    if row["amount"] >= 100:
        return "high"
    if row["amount"] >= 10:
        return "medium"
    return "low"


reference = frame.apply(band_for, axis=1)
assert frame["band"].fillna("missing").tolist() == reference.fillna("missing").tolist()

optimized, memory = category_if_smaller(frame["segment"])
assert memory["before"] > 0 and memory["after"] > 0
# Four rows: the level table costs more than the codes save, so keep the original.
assert not isinstance(optimized.dtype, pd.CategoricalDtype)

repeated = pd.Series(["east", "west"] * 1_000)
ids = pd.Series([f"id-{number}" for number in range(1_000)])
chosen_repeated, repeated_memory = category_if_smaller(repeated)
chosen_ids, id_memory = category_if_smaller(ids)
print({"repeated": repeated_memory, "ids": id_memory})
assert isinstance(chosen_repeated.dtype, pd.CategoricalDtype)
assert id_memory["after"] > id_memory["before"]
assert not isinstance(chosen_ids.dtype, pd.CategoricalDtype)
assert chosen_repeated.astype(str).tolist() == repeated.tolist()

# Concatenating categoricals with different levels silently falls back to object.
from pandas.api.types import union_categoricals

north = pd.Series(["north"], dtype="category")
south = pd.Series(["south"], dtype="category")
assert not isinstance(pd.concat([north, south]).dtype, pd.CategoricalDtype)
shared = pd.CategoricalDtype(["north", "south"])
aligned = pd.concat([north.astype(shared), south.astype(shared)], ignore_index=True)
assert aligned.dtype == shared
assert union_categoricals([north, south]).categories.tolist() == ["north", "south"]
```

For an almost-unique ID, the level table repeats nearly all original strings
in addition to codes. Concatenating categoricals also requires reconciling their
level sets; measure the final workflow, not a toy column alone.
