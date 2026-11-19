# swift-009: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-009_solution.swift](swift-009_solution.swift). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Mutate an independent array value:** The language contract concerns observable behavior even if storage was initially shared. Appending to the copy leaves the original unchanged.

**Do not confuse capacity and count:** Capacity is a performance hint, not an index range. Reserving twenty slots creates no logical elements.

## Task answers

### Task 1: Predict and explain

Predict original and changed arrays after append.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The language contract concerns observable behavior even if storage was initially shared. Appending to the copy leaves the original unchanged.

### Task 2: Guided modification

Replace an element in the copy and retain the original.

No separate reference answer has been written for this task. Start from Example B: Capacity is a performance hint, not an index range. Reserving twenty slots creates no logical elements.

### Task 3: Independent construction

Build a filtered array without changing the source.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```swift
let source = [-1, 2, -3, 4]
let positives = source.filter { $0 > 0 }
precondition(positives == [2, 4])
precondition(source == [-1, 2, -3, 4])
```

**Observe:** The filtered array is [2, 4] and the source is unchanged.

filter returns a new array; because arrays are values, the source keeps its own elements.

### Task 4: Diagnose a defect

Diagnose indexing a reserved but still empty array.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Array value semantics do not recursively clone objects. Never assume ArraySlice starts at index zero. Repeated insertions at the front can create quadratic work.

### Task 5: Boundary evidence

Test an empty slice and a slice whose startIndex is not zero.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Mutate an independent array value) and Example B (Do not confuse capacity and count).

### Task 6: Transfer and justify

Explain what changes when array elements are mutable class instances.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Value semantics**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Swift arrays are value types. Assigning an array produces a value that behaves independently when later mutated. The implementation can share backing storage until a write requires separation, a strategy called copy-on-write. The semantic promise is independent values, not a guarantee that every assignment immediately copies all bytes.

An array of class references still contains references as its element values. Copying the array separates its sequence structure but does not clone every referenced object. Keep that distinction in mind when building snapshots or undo history. Capacity is storage preparation and does not change the count of present elements.

`[Int]` is an array type. append grows logical count; an index replaces an existing element. reserveCapacity prepares storage. ArraySlice may preserve original indices, so use its indices rather than assuming zero.

Array value semantics do not recursively clone objects. Never assume ArraySlice starts at index zero. Repeated insertions at the front can create quadratic work.

## Review before continuing

Run the reference and confirm that it prints `swift-009: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
