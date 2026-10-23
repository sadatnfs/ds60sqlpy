# NumPy Memory Ownership, Strides, and Safe Mutation

**Stable ID:** `python-numpy-01`

**Estimated time:** 150 minutes; split the reading and implementation across sessions when useful.

## Level and prerequisites

Intermediate. Direct catalog prerequisites: `python-16`. This lesson deepens the named mechanism after the introductory track; it does not require a cloud account or download data.

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

Open the [learner script](../lessons/py_numpy_01.py) in the prepared repository environment. The browser reader is a preview; save an attempt in an ignored `.learning/` copy if you want it preserved separately. Run from the repository root. The provided worked examples execute immediately; task functions intentionally raise `NotImplementedError` until you implement them. A successful example is not evidence that the six tasks are finished.

Windows PowerShell:

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython python/professional/lessons/py_numpy_01.py
```

macOS/Linux:

```bash
.venv/bin/python python/professional/lessons/py_numpy_01.py
```

Dependencies: NumPy. All fixtures are tiny and local. The terminal prints the worked results and stops without editing your files. Keep [explanatory solutions](../solutions/py_numpy_01_solutions.md) and [runnable reference](../solutions/py_numpy_01_solution.py) closed until an attempt or an explicit worked comparison.

## Vocabulary and mental model

- **Buffer:** The contiguous region of bytes storing array values; several array objects can refer to the same buffer.

- **View:** An array that interprets existing storage with its own shape and strides, so changes may be visible through another array.

- **Stride:** The byte distance used to move one position along an axis; it is not a count of elements.

- **Ownership:** Responsibility for a memory allocation, which differs from whether another array can share or mutate its storage.

An array is a description of how to interpret bytes: data type, shape, starting location and strides. Indexing does not always allocate new values. A slice can move the starting location and change a stride while continuing to point at the same buffer. That is why assigning through a slice can change the source. A deliberate copy creates independent storage for ordinary numeric arrays.

Consider a three-by-four int64 array. Each value takes eight bytes, advancing one column takes eight bytes, and advancing one row takes 32 bytes. Transposing exchanges which axis uses which stride; it need not reorder the buffer. A contiguous array follows a regular layout compatible with a chosen row-major or column-major convention. A noncontiguous view can still be mathematically correct, but some downstream operations need to allocate a contiguous temporary.

Do not decide independence from `base is None` alone. Arrays can have a chain of views or share storage through a common ancestor. Use `np.shares_memory` when the actual overlap question matters. Empty arrays deserve special treatment: they contain no shared element even when produced by slicing. The meaningful contract is whether mutating one populated array can affect the other.

Ownership is a boundary design choice. A function that promises not to mutate its input can work on an owned output while reading input views safely. A read-only view prevents writes through that particular view; it does not freeze the underlying buffer if another writable alias still exists. A snapshot requires copying, and object-dtype arrays contain references whose nested Python objects may remain shared after an ordinary array copy.

The exercises distinguish inspection, independent extraction, transformation, access restriction and snapshotting. Predict the source and result after each mutation before executing. Treat dtype and empty-shape behavior as part of the contract. The goal is to make mutation visible and deliberate, not to copy every intermediate indiscriminately. Extra copies cost memory and time; accidental aliases cost correctness.

## Worked examples and syntax anatomy

### Example 1

```python
a = np.arange(6, dtype=np.int64)
view = a[::2]
view[1] = 99
assert a.tolist() == [0, 1, 99, 3, 4, 5]
assert np.shares_memory(a, view)
print("Shared slice:", a.tolist(), view.strides)
```

The slice selects indices zero, two, four. Its one-dimensional stride is 16 bytes because each int64 occupies eight bytes and the slice advances two elements. Assigning the second slice element changes source index two. This is a storage relationship, not a new collection of values.

### Example 2

```python
a = np.arange(6, dtype=np.int64).reshape(2, 3)
copy = a[:, 1:].copy()
copy[0, 0] = -1
assert a[0, 1] == 1 and not np.shares_memory(a, copy)
assert a.T.strides == (8, 24)
print("Original preserved:", a.tolist(), "transpose strides:", a.T.strides)
```

A copy detaches the selected values before mutation. The transpose changes strides from row/column movement to column/row movement without requiring a new mathematical value at each position. The assertions distinguish independence from a merely different shape.

## Exercises

1. **Inspect a concrete layout.** Implement layout for any NumPy array, returning shape, strides, itemsize and nbytes as a dictionary. Inspect np.arange(12, dtype=np.int64).reshape(3,4), its transpose and an empty float32 array. Do not mutate values.

**Expected:** The original has shape(3,4), strides(32,8), itemsize 8 and nbytes 96; the transpose has strides(8,32); the empty array has nbytes 0.

2. **Return an independent window.** Implement a one-dimensional half-open window [start, stop) that returns an independent copy. Require 0<=start<=stop<=len(values); reject a matrix or invalid bounds with ValueError. An empty valid window is allowed.

**Expected:** For [10,20,30,40] and bounds 1,3 return [20,30]. Changing output[0] leaves source[1]=20. Bounds 2,2 return shape(0,); bounds 3,2 raise ValueError.

3. **Transform without mutating callers.** Return a new floating-point matrix with each row mean subtracted. Require a finite two-dimensional numeric input with at least one column. Permit zero rows. Integer inputs must not fail because of in-place float subtraction. Reject an unrepresentable centered result with ValueError.

**Expected:** [[1,3],[10,14]] becomes[[-1,1],[-2,2]]; source stays unchanged and result shares no memory. Shape(0,2) remains(0,2); a zero-column or NaN input raises ValueError.

4. **Distinguish access restriction from a snapshot.** Return a view that shares numeric storage but rejects assignment through that view. Do not change the source writeable flag. Demonstrate that changing the source remains visible in the view.

**Expected:** Assigning view[0]=9 raises ValueError; source[0]=7 succeeds and then view[0] equals 7. Source flags.writeable remainsTrue.

5. **Select a strided view deliberately.** Return every step-th value from a one-dimensional array as a view. Require a positive integer step and reject bool, zero, negative or noninteger steps. Preserve empty inputs.

**Expected:** For np.arange(7) with step 3 return [0,3,6]; a mutation of result[1] changes source[3]. Step 0 and True raise ValueError; an empty source returns shape(0,).

6. **Transfer ownership across a cache boundary.** Copy each array in a mapping so future numeric mutations of source arrays do not affect the snapshot. Preserve keys and allow an empty mapping. Reject object-dtype arrays with ValueError because copying their buffer would not deep-copy nested Python objects.

**Expected:** Two keys pointing to one source array produce two independent snapshot arrays. Mutating one snapshot leaves the other and source unchanged. Empty input returns{}; dtype=object is rejected.

## Common mistakes and diagnosis

If changing a returned array unexpectedly changes the source, inspect np.shares_memory and the exact slicing expression before adding copies at random. If subtraction raises an output-casting error, check the input dtype and whether an in-place operation tried to store fractions in integers. If a supposedly frozen view changes, inspect other writable aliases; flags on one view do not freeze the buffer. If a transpose seems slow, inspect its strides and whether a downstream operation requires contiguous storage. Never infer correctness solely from a fast timing or a successful shape check.

## Self-check and retrieval

Without copying code, explain which input property each function assumes, which observable result proves the normal case, and which counterexample would expose an incorrect implementation. Trace one boundary input by hand before running it. Keep the input and expected output beside your saved result so a reviewer can reproduce the evidence.

## Next steps

Use these mechanisms in the next deepening lesson or return to the original prerequisite examples and explain precisely which new failure cases you can now diagnose. Review the [professional track](../README.md) for related modules.

## Primary sources and official APIs

- [NumPy copies and views](https://numpy.org/doc/stable/user/basics.copies.html).

- [NumPy ndarray.strides](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.strides.html).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through python-numpy-01: NumPy Memory Ownership, Strides, and Safe Mutation.
Read python/professional/companion-guides/py_numpy_01.md and python/professional/lessons/py_numpy_01.py. Direct prerequisites: python-16.
Explain the vocabulary and mechanism at a beginner-friendly pace, then ask me to predict a concrete result before my attempt. Give one hint at a time, review my numerical or exception evidence, and ask retrieval questions in my own words. Do not read solutions/ until I request it or have made an honest attempt. Use only the prepared local Python environment and tiny offline inputs; preserve my saved work.
Done when all six contracts and their boundary cases have inspected evidence and I can explain why a tempting incorrect implementation fails.
```
