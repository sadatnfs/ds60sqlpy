# python-pandas-01: Explained reference solutions

These answers implement the contracts in [pandas Label Alignment, Nullable Logic, and Safe Assignment](../companion-guides/py_pandas_01.md). Compare after an attempt. The [executable reference](py_pandas_01_solution.py) contains the complete implementations and assertions. Each answer explains the mechanism, not just the final value.

## Exercises and reasoning

### Exercise 1: Subtract by validated identities

Subtract right from left after requiring unique indices and exactly the same label set. Preserve left index order. Reject missing or duplicate labels with ValueError; do not silently form a union and invent missing results.

**Expected:** left b=20, a=10 and right a=1, b=2 return b=18, a=9 in that order. A right Series missing b or with duplicate a raises ValueError.

```python
def aligned_difference(left: pd.Series, right: pd.Series) -> pd.Series:
    if (
        not left.index.is_unique
        or not right.index.is_unique
        or len(left) != len(right)
        or not left.index.isin(right.index).all()
    ):
        raise ValueError("Expected the same unique labels")
    return left - right.reindex(left.index)
```

The identity check precedes subtraction so no union-generated missing row can be mistaken for a real arithmetic result. Reindexing right to the left index makes output order explicit even though pandas also supports automatic alignment. Duplicate labels are rejected because the contract promises one value per identity. This does not require values to be nonmissing; a known identity with an unknown value can legitimately retain a missing difference.

```python
a = pd.Series([20, 10], index=["b", "a"])
b = pd.Series([1, 2], index=["a", "b"])
r = aligned_difference(a, b)
assert r.index.tolist() == ["b", "a"] and r.tolist() == [18, 9]
expect_value_error(lambda: aligned_difference(a, b.iloc[:1]))
expect_value_error(lambda: aligned_difference(a, pd.Series([1, 2], index=["a", "a"])))
```

### Exercise 2: Assign without swapping entities

Return a copied frame with a column assigned from a uniquely indexed Series covering exactly the frame index. Preserve frame order and existing source data. Reject duplicate or mismatched indices rather than assigning by position.

**Expected:** Frame index[b, a] and Series a=100, b=200 create column[200,100]. The original frame has no new column; an extra Series label c raises ValueError.

```python
def assign_by_label(frame: pd.DataFrame, name: str, values: pd.Series) -> pd.DataFrame:
    if (
        not frame.index.is_unique
        or not values.index.is_unique
        or len(frame) != len(values)
        or not frame.index.isin(values.index).all()
    ):
        raise ValueError("Assignment needs the same unique row identities")
    result = frame.copy()
    result[name] = values.reindex(frame.index)
    return result
```

The new frame owns its tabular mutation boundary, and the Series is explicitly aligned before assignment. This avoids relying on coincidental physical order. A caller can replace an existing column through the same function, but the original frame remains unchanged. The extra-label rejection is deliberate: silently dropping c could hide an upstream population mismatch even though pandas can technically perform the assignment.

```python
frame = pd.DataFrame({"old": [1, 2]}, index=["b", "a"])
values = pd.Series([100, 200], index=["a", "b"])
r = assign_by_label(frame, "new", values)
assert r["new"].tolist() == [200, 100] and "new" not in frame
expect_value_error(
    lambda: assign_by_label(frame, "new", pd.Series([1, 2, 3], index=["a", "b", "c"]))
)
```

### Exercise 3: Keep unknown comparison results

Require an Int64 nullable Series and return a nullable Boolean mask for values greater than zero. Preserve its index and unknown entries. Reject another dtype with ValueError so the missing-value representation is explicit.

**Expected:** Int64[2, NA,0,-1] gives [True, NA, False, False] with dtype boolean. A plain float Series is rejected; an empty Int64 Series returns empty boolean.

```python
def nullable_positive(values: pd.Series) -> pd.Series:
    if str(values.dtype) != "Int64":
        raise ValueError("Expected pandas nullable Int64")
    return values.gt(0)
```

A nullable integer comparison yields nullable Boolean values, retaining the distinction between unknown and known false. The strict dtype requirement is a teaching contract that prevents a different missingness convention from entering silently. Empty typed Series preserve schema even without observations. Downstream code must still decide how unknown truth values affect filtering, aggregation or validation; this function intentionally does not make that policy decision.

```python
s = pd.Series([2, pd.NA, 0, -1], dtype="Int64")
r = nullable_positive(s)
assert str(r.dtype) == "boolean" and r.iloc[0] and pd.isna(r.iloc[1]) and not r.iloc[2]
assert str(nullable_positive(pd.Series([], dtype="Int64")).dtype) == "boolean"
expect_value_error(lambda: nullable_positive(pd.Series([1.0, np.nan])))
```

### Exercise 4: Apply an explicit unknown-filter policy

Filter a uniquely indexed frame with a Boolean or nullable-Boolean Series covering the same unique labels. Align by label, retain only known True entries, preserve frame order and return a copy. Reject integer flags or mismatched labels.

**Expected:** Frame index[b, a, c] and mask a=True, b=NA, c=False retain only a. The output can be mutated without changing frame; Int64[1,0,1] is rejected.

```python
def select_known_true(frame: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    if (
        not frame.index.is_unique
        or not mask.index.is_unique
        or len(frame) != len(mask)
        or not frame.index.isin(mask.index).all()
        or str(mask.dtype) not in {"bool", "boolean"}
    ):
        raise ValueError("Expected one Boolean mask value per unique frame label")
    keep = mask.reindex(frame.index).fillna(False)
    return frame.loc[keep].copy()
```

Unknown mask entries are converted to false only after index validation and alignment, so the choice is attached to the correct entity. The explicit copy establishes a safe modification boundary independent of pandas chained-assignment behavior or copy-on-write settings. Rejecting numeric flags prevents a common ambiguity between a mask and positional indexer. A different policy, such as returning unknown rows separately for review, should be a separately named contract.

```python
frame = pd.DataFrame({"x": [2, 1, 3]}, index=["b", "a", "c"])
mask = pd.Series([True, pd.NA, False], index=["a", "b", "c"], dtype="boolean")
r = select_known_true(frame, mask)
assert r.index.tolist() == ["a"]
r.loc["a", "x"] = 99
assert frame.loc["a", "x"] == 1
expect_value_error(
    lambda: select_known_true(frame, pd.Series([1, 0, 1], index=frame.index, dtype="Int64"))
)
```

### Exercise 5: Distinguish absent labels from unknown values

For unique source labels and unique target labels, return a DataFrame indexed in target order with value and present columns. Reindex values without filling them; present indicates whether the label existed in the source even if its value was missing.

**Expected:** Source a=NA, b=5 and targets[b, a, c] yield present[True, True, False] with b value 5 and missing a, c. Duplicate target labels raise ValueError.

```python
def reindex_with_presence(values: pd.Series, labels: list[str]) -> pd.DataFrame:
    target = pd.Index(labels)
    if not values.index.is_unique or not target.is_unique:
        raise ValueError("Expected unique source and target labels")
    return pd.DataFrame(
        {"value": values.reindex(target), "present": target.isin(values.index)}, index=target
    )
```

The value column alone cannot distinguish an absent source label from an existing label with a missing measurement. The presence indicator records membership before reindexing, preserving that provenance. Target order is explicit and need not be sorted. This pattern is useful for reconciliation and feature availability because filling both cases with zero would erase the reason information is unavailable.

```python
s = pd.Series([pd.NA, 5], index=["a", "b"], dtype="Int64")
r = reindex_with_presence(s, ["b", "a", "c"])
assert r.index.tolist() == ["b", "a", "c"] and r["present"].tolist() == [True, True, False]
assert r.loc["b", "value"] == 5 and pd.isna(r.loc["a", "value"]) and pd.isna(r.loc["c", "value"])
expect_value_error(lambda: reindex_with_presence(s, ["a", "a"]))
```

### Exercise 6: Append typed batches without hiding identity conflicts

Concatenate a nonempty list of frames with exactly matching column order and dtypes, and globally unique row indices. Reject schema differences or duplicate identities with ValueError. Permit an empty typed frame within the list.

**Expected:** Two Int64 frames indexed a and b concatenate to index[a, b] preserving Int64. Repeated a, reversed columns, changed dtype or an empty list is rejected.

```python
def strict_concat(frames: list[pd.DataFrame]) -> pd.DataFrame:
    if not frames:
        raise ValueError("At least one typed frame is required")
    first = frames[0]
    if any(
        not frame.columns.equals(first.columns) or not frame.dtypes.equals(first.dtypes)
        for frame in frames
    ):
        raise ValueError("Batch columns and dtypes must match exactly")
    try:
        return pd.concat(frames, axis=0, verify_integrity=True)
    except ValueError as error:
        raise ValueError("Batch row identities must be globally unique") from error
```

Concatenation is not a schema validator by default, so the function checks both ordered columns and logical dtypes first. verify_integrity then rejects duplicate row identities across the combined batches. This avoids silently resetting identities merely to make concatenation succeed. An empty list has no schema from which to construct a meaningful typed result, while an empty frame with the agreed schema can safely contribute no rows.

```python
a = pd.DataFrame({"x": pd.Series([1], index=["a"], dtype="Int64")})
b = pd.DataFrame({"x": pd.Series([2], index=["b"], dtype="Int64")})
r = strict_concat([a, b])
assert r.index.tolist() == ["a", "b"] and str(r["x"].dtype) == "Int64"
expect_value_error(lambda: strict_concat([a, a]))
expect_value_error(lambda: strict_concat([a, b.astype(float)]))
expect_value_error(lambda: strict_concat([]))
```

## Verification and interpretation

Run `python python/professional/solutions/py_pandas_01_solution.py` from the repository root with the prepared interpreter. The code checks normal inputs and explicit edge cases before printing its success line. Assertions are the evidence; the printed sentence alone is not. The helper `expect_value_error` requires an actual `ValueError` and fails if a function silently accepts an invalid input. Inspect each function's mutation and ordering behavior as part of its contract.
