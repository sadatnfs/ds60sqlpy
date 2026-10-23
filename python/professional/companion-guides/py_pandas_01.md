# pandas Label Alignment, Nullable Logic, and Safe Assignment

**Stable ID:** `python-pandas-01`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-20`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

## Learning objectives

By the end, explain the mechanism in your own words, implement each bounded contract, and use a counterexample to distinguish a correct result from a plausible mistake. The six exercises progress from inspection to transformation, edge handling and transfer.

## How to run this lesson

Open the [learner script](../lessons/py_pandas_01.py) in the prepared repository environment. The browser reader is a preview; save an attempt in an ignored `.learning/` copy if you want it preserved separately. Run from the repository root. The provided worked examples execute immediately; task functions intentionally raise `NotImplementedError` until you implement them. A successful example is not evidence that the six tasks are finished.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython python/professional/lessons/py_pandas_01.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_pandas_01.py
```

Dependencies: pandas and NumPy. All fixtures are tiny and local. The terminal prints the worked results and stops without editing your files. Keep [explanatory solutions](../solutions/py_pandas_01_solutions.md) and [runnable reference](../solutions/py_pandas_01_solution.py) closed until an attempt or an explicit worked comparison.

## Vocabulary and mental model

- **Index:** The labels attached to rows or Series elements, which pandas often uses to align operations rather than relying on physical position.

- **Alignment:** Matching operands by their labels before arithmetic or assignment; it can introduce missing values when label sets differ.

- **Nullable dtype:** A pandas representation that preserves missing values alongside a logical integer or Boolean type, such as Int64 or boolean.

- **Unknown Boolean:** A missing truth value represented by pd.NA, which is distinct from both True and False.

pandas combines tabular values with labels. Two Series containing the same values in different orders are not interchangeable when their indices identify different customers. Arithmetic and assignment frequently align on labels first. This is useful when identities are reliable and dangerous when an index is merely a leftover row counter. Decide whether an operation is label-based or position-based before converting to NumPy.

Duplicate labels complicate alignment because one label can refer to multiple positions. A function promising one value per customer should validate uniqueness before arithmetic or assignment. Resetting the index may be appropriate when order is the real identity, but it must be an explicit transformation, not a way to silence an alignment error. Preserve a real identifier column when it carries domain meaning.

Missingness has several distinct causes. A label may be absent from a Series, or its label may exist with an unknown value. Reindexing turns both into a missing displayed value unless presence is tracked separately. Filling every missing value with zero collapses absence, unknown measurement and known zero into one representation. That may be an intentional policy for counts, but it is wrong for many measured quantities.

Nullable Boolean logic preserves unknown comparisons. With an Int64 Series containing pd.NA, comparison to zero can produce True, False or pd.NA. A filter needs an explicit policy for unknown rows. This lesson drops them only in the function whose name and contract state that policy; other functions preserve unknown values so downstream code can decide.

Assignment is also an identity operation. Assigning a Series to a DataFrame column normally aligns by index, whereas assigning its to_numpy result uses position. Neither is universally preferable. If customer b appears first in one input and last in another, positional assignment can silently swap their values while preserving row count and dtype. A small reversed-index fixture makes the bug visible.

Finally, concatenation appends rows but does not guarantee that keys remain unique or schemas match. Require explicit columns and dtype compatibility when combining typed batches. A result that prints nicely may still have silently widened a nullable integer to object or duplicated an entity. The exercises build narrow reusable boundaries that reject ambiguity while preserving input tables.

## Worked examples and syntax anatomy

### Example 1

```python
left = pd.Series([20, 10], index=["b", "a"])
right = pd.Series([1, 2], index=["a", "b"])
result = left - right
assert result.to_dict() == {"a": 9, "b": 18}
assert (left.to_numpy() - right.to_numpy()).tolist() == [19, 8]
print("Label subtraction:", result.to_dict())
```

The two arithmetic expressions answer different questions. Series subtraction matches a with a and b with b, while array subtraction pairs the first elements regardless of identity. The resulting numbers differ even though every input has length two. Labels are part of the data contract.

### Example 2

```python
values = pd.Series([1, pd.NA, -2], dtype="Int64", index=["a", "b", "c"])
mask = values.gt(0)
assert str(mask.dtype) == "boolean" and pd.isna(mask.loc["b"])
selected = values.loc[mask.fillna(False)]
assert selected.index.tolist() == ["a"]
print("Known positive rows:", selected.to_dict())
```

The comparison preserves uncertainty for b rather than inventing a negative measurement. The filter then explicitly chooses to retain only known True rows. Filling the mask is a decision policy at the selection boundary, not an instruction to replace missing source values with zero.

## Exercises

1. **Subtract by validated identities.** Subtract right from left after requiring unique indices and exactly the same label set. Preserve left index order. Reject missing or duplicate labels with ValueError; do not silently form a union and invent missing results.

**Expected:** left b=20, a=10 and right a=1, b=2 return b=18, a=9 in that order. A right Series missing b or with duplicate a raises ValueError.

2. **Assign without swapping entities.** Return a copied frame with a column assigned from a uniquely indexed Series covering exactly the frame index. Preserve frame order and existing source data. Reject duplicate or mismatched indices rather than assigning by position.

**Expected:** Frame index[b, a] and Series a=100, b=200 create column[200,100]. The original frame has no new column; an extra Series label c raises ValueError.

3. **Keep unknown comparison results.** Require an Int64 nullable Series and return a nullable Boolean mask for values greater than zero. Preserve its index and unknown entries. Reject another dtype with ValueError so the missing-value representation is explicit.

**Expected:** Int64[2, NA,0,-1] gives [True, NA, False, False] with dtype boolean. A plain float Series is rejected; an empty Int64 Series returns empty boolean.

4. **Apply an explicit unknown-filter policy.** Filter a uniquely indexed frame with a Boolean or nullable-Boolean Series covering the same unique labels. Align by label, retain only known True entries, preserve frame order and return a copy. Reject integer flags or mismatched labels.

**Expected:** Frame index[b, a, c] and mask a=True, b=NA, c=False retain only a. The output can be mutated without changing frame; Int64[1,0,1] is rejected.

5. **Distinguish absent labels from unknown values.** For unique source labels and unique target labels, return a DataFrame indexed in target order with value and present columns. Reindex values without filling them; present indicates whether the label existed in the source even if its value was missing.

**Expected:** Source a=NA, b=5 and targets[b, a, c] yield present[True, True, False] with b value 5 and missing a, c. Duplicate target labels raise ValueError.

6. **Append typed batches without hiding identity conflicts.** Concatenate a nonempty list of frames with exactly matching column order and dtypes, and globally unique row indices. Reject schema differences or duplicate identities with ValueError. Permit an empty typed frame within the list.

**Expected:** Two Int64 frames indexed a and b concatenate to index[a, b] preserving Int64. Repeated a, reversed columns, changed dtype or an empty list is rejected.

## Common mistakes and diagnosis

If arithmetic yields unexpected NaNs, compare the index sets before filling values. If a new column appears to swap customers, inspect whether the code assigned a Series or its NumPy values. If a condition raises an ambiguous truth-value error, distinguish elementwise Boolean operations from scalar Python logic. If unknown values disappear, locate the exact fillna or filter boundary and check whether that policy was intended. If concatenation changes dtype, compare each input schema rather than coercing the combined result after information has already been lost.

## Self-check and retrieval

Without copying code, explain which input property each function assumes, which observable result proves the normal case, and which counterexample would expose an incorrect implementation. Trace one boundary input by hand before running it. Keep the input and expected output beside your saved result so a reviewer can reproduce the evidence.

## Next steps

Use these mechanisms in the next deepening lesson or return to the original prerequisite examples and explain precisely which new failure cases you can now diagnose. Review the [professional track](../README.md) for related modules.

## Primary sources and official APIs

- [pandas data alignment](https://pandas.pydata.org/docs/user_guide/dsintro.html#data-alignment-and-arithmetic).

- [pandas nullable Boolean data type](https://pandas.pydata.org/docs/user_guide/boolean.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-pandas-01: pandas Label Alignment, Nullable Logic, and Safe Assignment.
Read python/professional/companion-guides/py_pandas_01.md and python/professional/lessons/py_pandas_01.py. Direct prerequisites: python-20.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
