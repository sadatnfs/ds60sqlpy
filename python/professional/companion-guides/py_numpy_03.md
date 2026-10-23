# Gather, Scatter, Masks, and Deterministic Selection

**Stable ID:** `python-numpy-03`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-numpy-02`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

## Learning objectives

By the end, explain the mechanism in your own words, implement each bounded contract, and use a counterexample to distinguish a correct result from a plausible mistake. The six exercises progress from inspection to transformation, edge handling and transfer.

## How to run this lesson

**Primary browser route:** run `./classroom` from the repository root and
choose **Python** on `/classroom`. Open this lesson in the shared workspace,
read its capability notice, and use its supported coding or reading workflow.
The [classroom guide](../../../docs/classroom-experience.md) explains saved work, runtimes and switching subjects.

**Optional native notebook/editor route:** the instructions below describe
separately prepared host tools. They are useful alternatives, not prerequisites
for opening this lesson in the Docker classroom.

Open the [learner script](../lessons/py_numpy_03.py) in the prepared repository environment. The browser reader is a preview; save an attempt in an ignored `.learning/` copy if you want it preserved separately. Run from the repository root. The provided worked examples execute immediately; task functions intentionally raise `NotImplementedError` until you implement them. A successful example is not evidence that the six tasks are finished.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython python/professional/lessons/py_numpy_03.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_numpy_03.py
```

Dependencies: NumPy. All fixtures are tiny and local. The terminal prints the worked results and stops without editing your files. Keep [explanatory solutions](../solutions/py_numpy_03_solutions.md) and [runnable reference](../solutions/py_numpy_03_solution.py) closed until an attempt or an explicit worked comparison.

## Vocabulary and mental model

- **Gather:** Reading values from positions named by an index array, usually producing a new array.

- **Scatter:** Writing or accumulating values into positions named by an index array.

- **Boolean mask:** An array of True and False values selecting positions under an explicit shape contract.

- **Permutation:** A reordering containing each position exactly once, so an inverse ordering exists.

Basic slices describe a regular walk through storage. Advanced integer and Boolean indexing describe selected positions and normally create a gathered copy. This distinction affects mutation: changing a gathered result does not change its source, while assigning directly through source[index] changes selected source positions. Always separate reading selection from assignment syntax when reasoning about aliases.

Repeated indices are the important scatter edge case. The expression a[index] += values gathers selected values, computes an update and writes them back. If index contains the same position twice, it does not reliably express two independent sequential increments. `np.add.at` performs unbuffered accumulation at repeated positions and gives the required additive semantics. Choose the operation from the intended update rule, not from visual similarity of syntax.

Multiple index arrays can select paired coordinates or a Cartesian grid. With rows=[0,2] and columns=[1,3], matrix[rows, columns] selects two pairs. `np.ix_` reshapes indices to select all four row-column combinations. Both operations are valid, but they return different grains. Write one output position's source coordinates by hand before deciding which form is intended.

Masks also carry axis meaning. A row filter needs one Boolean per row, not one Boolean per cell or a list of integer flags. Combining comparisons uses elementwise operators with parentheses, not Python's scalar and/or. A malformed mask should fail at the function boundary rather than broadcast or flatten silently.

Ordering needs a tie policy. Selecting the largest k scores without specifying what happens on ties can produce unstable output across algorithm choices. A stable sort preserves original position order for equal scores. Partial selection methods can improve complexity when k is small, but they require a separate ordering step and careful boundary-tie handling. The lesson uses a full stable sort first so correctness is transparent.

The exercises connect these mechanisms to categorical aggregation, row selection, pair tables and reversible ordering. Every contract states whether duplicates are valid, whether negative indices are accepted, what empty inputs mean and whether output shares storage. These policies are part of the data operation, not optional error handling.

## Worked examples and syntax anatomy

### Example 1

```python
values = np.array([10, 20, 30, 40])
selected = values[np.array([3, 1, 1])]
selected[0] = -1
assert values.tolist() == [10, 20, 30, 40]
assert selected.tolist() == [-1, 20, 20]
print("Gathered copy:", selected.tolist())
```

Integer indexing repeats index one and reorders the values without changing their source. Mutating the selected copy affects only that result. Repetition is meaningful here because the output represents requested positions, not a set of unique source rows.

### Example 2

```python
indices = np.array([0, 0, 2])
updates = np.array([1.0, 2.0, 5.0])
buffered = np.zeros(3)
buffered[indices] += updates
accumulated = np.zeros(3)
np.add.at(accumulated, indices, updates)
assert accumulated.tolist() == [3.0, 0.0, 5.0]
assert buffered[0] != accumulated[0]
print("Accumulated repeated indices:", accumulated.tolist())
```

Two contributions belong to category zero, so the correct sum is three. add.at preserves both additions. The buffered advanced-index update is deliberately shown as a counterexample; do not use its observed last value as a portable specification for a duplicate-assignment policy.

## Exercises

1. **Gather with explicit index rules.** Gather a one-dimensional source using a one-dimensional integer index array. Allow negative positions in the normal NumPy range and preserve duplicates/order. Reject Boolean, floating or out-of-range indices with ValueError. Return an independent result.

**Expected:** [10,20,30] with [2,-1,0] yields [30,30,10]. Empty integer positions return shape(0,). Position 3, float1.0 or a Boolean index array raises ValueError.

2. **Accumulate repeated category codes.** Sum finite one-dimensional values into bins using one nonnegative integer code per value. Reject unequal lengths, invalid codes or negative/noninteger bin counts. Zero bins are allowed only with empty inputs. Preserve every repeated-code contribution.

**Expected:** Values[1,2,5] and codes[0,0,2] with 3 bins produce[3,0,5]. Empty inputs and zero bins produce shape(0,); code 3 for 3 bins raises ValueError.

3. **Validate a row mask.** Filter a matrix using an exactly matching one-dimensional Boolean row mask. Preserve selected order and return independent storage. Reject integer flags, a cell-shaped mask or wrong row count with ValueError.

**Expected:** [[1,2],[3,4],[5,6]] with [True, False, True] gives [[1,2],[5,6]]. All false gives shape(0,2); an integer[1,0,1] mask is rejected.

4. **Select every row-column combination.** Return a Cartesian submatrix from nonnegative integer row and column arrays. Preserve duplicates and index-array order in both axes. Reject out-of-range, Boolean or noninteger indices. An empty selection on either axis must preserve the other output dimension.

**Expected:** np.arange(12).reshape(3,4), rows[2,0], columns[3,1] gives [[11,9],[3,1]]. Empty rows with two columns returns shape(0,2), not a flat vector.

5. **Make top-k ties deterministic.** Return indices of the k largest finite one-dimensional scores in descending score order, breaking ties by original position. Require an integer k between zero and the number of scores, rejecting Boolean k. Do not mutate scores.

**Expected:** [5,9,9,1] with k=3 returns [1,2,0]. k=0 returns an empty integer array; k=5 or a NaN score raises ValueError.

6. **Restore original observation order.** Return the inverse of a one-dimensional integer permutation of 0 through n-1. Reject duplicates, missing positions, negative values and noninteger dtype. Support the empty permutation. Demonstrate recovery of records after reordering.

**Expected:** Order[2,0,1] has inverse[1,2,0], and original[order][inverse] equals original. Order[0,0] is invalid; an empty integer array returns empty.

## Common mistakes and diagnosis

If category totals are too small only when codes repeat, inspect a[index] += updates and compare it with add.at. If a submatrix unexpectedly becomes one-dimensional, distinguish paired indexing from a Cartesian grid. If a mask selects strange repeated rows, print its dtype; integer zero/one arrays are indices, not Boolean filters. If top-k output changes on equal scores, define a stable tie rule before changing the sorting algorithm. If restoring order fails, verify that the original operation was a permutation rather than a lossy selection.

## Self-check and retrieval

Without copying code, explain which input property each function assumes, which observable result proves the normal case, and which counterexample would expose an incorrect implementation. Trace one boundary input by hand before running it. Keep the input and expected output beside your saved result so a reviewer can reproduce the evidence.

## Next steps

Use these mechanisms in the next deepening lesson or return to the original prerequisite examples and explain precisely which new failure cases you can now diagnose. Review the [professional track](../README.md) for related modules.

## Primary sources and official APIs

- [NumPy indexing semantics](https://numpy.org/doc/stable/user/basics.indexing.html).

- [NumPy ufunc.at repeated-index accumulation](https://numpy.org/doc/stable/reference/generated/numpy.ufunc.at.html).

## Ask Codex about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-numpy-03: Gather, Scatter, Masks, and Deterministic Selection.
Read python/professional/companion-guides/py_numpy_03.md and python/professional/lessons/py_numpy_03.py. Direct prerequisites: python-numpy-02.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
